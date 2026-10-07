"""Verified local release bundles with explicit public/private boundaries."""

import csv
import io
import json
import os
import shutil
import stat
import tempfile
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

from PIL import Image
from pydantic import TypeAdapter

from .assets.service import digest_file
from .jobs import JobService
from .models import Asset, ReleaseRecord
from .models.base import (
    AssetRef,
    HashedFile,
    Identifier,
    MediaPath,
    canonical_bytes,
    content_hash,
)
from .models.production import ReviewRecord
from .models.publishing import (
    PublicAssetRights,
    PublicRelease,
    PublicTrack,
    ReleaseBundleReport,
    ReleaseInspection,
    ReleasePreparation,
)
from .models.rendering import RenderReport
from .persistence import StorageError
from .process import checkpoint
from .render.backend import FrozenRegistry


def chapter_lines(chapters, fps, duration_frames):
    """Whole-second authored chapters, without rounding or inventing markers."""
    if not chapters:
        return [], None
    seconds = [Fraction(chapter.start_frame * fps.den, fps.num) for chapter in chapters]
    duration = Fraction(duration_frames * fps.den, fps.num)
    if (
        len(seconds) < 3
        or seconds[0] != 0
        or any(value.denominator != 1 for value in seconds)
        or any(b - a < 10 for a, b in zip(seconds, [*seconds[1:], duration], strict=True))
        or any("\n" in item.title or "\r" in item.title for item in chapters)
    ):
        return [], (
            "Chapters omitted: supply at least three ascending whole-second markers from 00:00, "
            "with every chapter (including the last) at least ten seconds. Track list retained."
        )
    result = []
    for second, chapter in zip(seconds, chapters, strict=True):
        hour, remainder = divmod(int(second), 3600)
        minute, second = divmod(remainder, 60)
        stamp = f"{hour}:{minute:02}:{second:02}" if hour else f"{minute:02}:{second:02}"
        result.append(f"{stamp} {chapter.title}")
    return result, None


def csv_cell(value):
    # Text cells must not become spreadsheet formulas when a CSV is opened.
    text = "" if value is None else str(value)
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) else text


def tracklist_csv(tracks):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "start_sample",
            "end_sample",
            "sample_rate",
            "title",
            "artist",
            "asset_id",
            "version",
            "isrc",
            "release_url",
        ]
    )
    for track in tracks:
        writer.writerow(
            [
                track.start_sample,
                track.end_sample,
                48000,
                csv_cell(track.title),
                csv_cell(track.artist),
                csv_cell(track.asset.id),
                track.asset.version,
                csv_cell(track.isrc),
                csv_cell(track.release_url),
            ]
        )
    return buffer.getvalue()


def copy_verified(source, destination, expected):
    """Stream an independent copy; never hard-link a publication to a mutable source."""
    descriptor = os.open(source, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as incoming, destination.open("xb") as outgoing:
        if not stat.S_ISREG(os.fstat(incoming.fileno()).st_mode):
            raise StorageError("release source must be a regular file")
        while block := incoming.read(1024 * 1024):
            checkpoint()
            outgoing.write(block)
        outgoing.flush()
        os.fsync(outgoing.fileno())
    if digest_file(destination) != expected or digest_file(source) != expected:
        raise StorageError("release source changed or copy verification failed")


def review_status(public, blockers, creative_review, metadata_review, *, metadata_digest=None):
    """Reviews bind the exact video and public metadata, never a mutable title."""
    blockers = list(blockers)
    digest = metadata_digest or content_hash(public)
    status = "technically_verified"
    if creative_review and creative_review.content_sha256 == public.video_sha256:
        status = "creatively_reviewed"
    else:
        blockers.append("creative_review_pending_or_stale")
    if status == "creatively_reviewed" and not blockers:
        status = "rights_reviewed"
    if not metadata_review or metadata_review.content_sha256 != digest:
        blockers.append("metadata_and_disclosure_review_pending_or_stale")
    if not blockers:
        status = "ready_for_manual_upload"
    return status, sorted(set(blockers))


class ReleaseService:
    def __init__(self, assets, settings):
        self.assets, self.store, self.settings = assets, assets.store, settings
        self.jobs = JobService(assets, settings)

    def load(self, identity):
        identity = TypeAdapter(Identifier).validate_python(identity)
        document = self.store.read(f"publishing/{identity}.json")
        if not isinstance(document, ReleasePreparation) or document.id != identity:
            raise StorageError("release preparation identity mismatch")
        return document

    def preparations(self):
        result = []
        for path in sorted((self.store.root / "publishing").glob("*.json")):
            data = json.loads(self.store._read_bytes(f"publishing/{path.name}"))
            # Retired Flow records remain archival evidence, never resumed or rewritten.
            if data.get("source_kind") == "flow":
                continue
            result.append(self.load(path.stem))
        return result

    def save(self, preparation, *, expected_revision):
        preparation = ReleasePreparation.model_validate(preparation)
        # Prevent a saved reference to an unrelated/missing job. Preparing before
        # completion is allowed; inspect/export still require verified media.
        self.jobs.ledger.get(preparation.job_id)
        return self.store.save_draft(preparation, expected_revision=expected_revision)

    def _inspect(self, preparation):
        preparation = ReleasePreparation.model_validate(preparation)
        verification = self.jobs.verify_export(preparation.job_id)
        job = self.jobs.ledger.get(preparation.job_id)
        render_report = self.store.read(job.report_path)
        if not isinstance(render_report, RenderReport) or (
            render_report.snapshot_sha256,
            render_report.first_frame,
            render_report.frame_count,
            render_report.output_sha256,
            render_report.output_bytes,
        ) != (
            job.snapshot_sha256,
            job.first_frame,
            job.duration_frames,
            job.output.sha256,
            job.output.size_bytes,
        ):
            raise StorageError("render report differs from the verified job")
        snapshot = self.store.read_snapshot(job.snapshot_sha256)
        registry = FrozenRegistry(self.assets, snapshot)
        blockers, warnings = [], []
        if snapshot.purpose != "production":
            blockers.append("non_production_snapshot")
        if job.first_frame != 0 or job.duration_frames != snapshot.episode.duration_frames:
            blockers.append("partial_export")
        if snapshot.audio_placements and verification.audio is None:
            blockers.append("missing_audio")
        rights = []
        for document in registry.documents.values():
            if isinstance(document, Asset):
                rights.append(
                    PublicAssetRights(
                        asset=AssetRef(id=document.id, version=document.version),
                        commercial_use=document.provenance.commercial_use,
                        approved=document.approval.status == "approved",
                        synthetic=document.provenance.origin == "synthetic",
                    )
                )
        if any(item.synthetic for item in rights):
            blockers.append("synthetic_assets")
        if any(not item.approved or item.commercial_use != "confirmed" for item in rights):
            blockers.append("asset_rights_or_approval_pending")
        begin = snapshot.episode.fps.sample_at(job.first_frame)
        end = snapshot.episode.fps.sample_at(job.first_frame + job.duration_frames)
        tracks, releases, music_blockers = self._music_tracks(
            snapshot.audio_placements, registry, begin, end
        )
        blockers.extend(music_blockers)
        inspection, thumbnail, lines = self._public_inspection(
            preparation,
            purpose=snapshot.purpose,
            output=job.output,
            inputs_sha256=job.snapshot_sha256,
            first_frame=job.first_frame,
            duration_frames=job.duration_frames,
            profile=job.profile,
            tracks=tracks,
            rights=rights,
            blockers=blockers,
            warnings=warnings,
            render_report=render_report,
        )
        return inspection, verification, registry, releases, thumbnail, lines

    def _music_tracks(self, placements, registry, begin, end):
        blockers = []
        tracks, releases = [], {}
        for placement in placements:
            first = max(begin, placement.start_sample)
            last = min(end, placement.start_sample + placement.duration_samples)
            if placement.role != "music" or first >= last:
                continue
            asset = registry.get(placement.asset, "asset")
            release, track = None, None
            if placement.release_id is not None:
                release = self.store.read(f"releases/{placement.release_id}.json")
                if not isinstance(release, ReleaseRecord) or release.id != placement.release_id:
                    raise StorageError("music release identity mismatch")
                releases[release.id] = release
                track = next((t for t in release.tracks if t.asset == placement.asset), None)
                if track is None:
                    raise StorageError("music release does not contain the locked track")
                if track.sha256 != asset.files[0].sha256 or (
                    track.sample_rate,
                    track.channels,
                    track.duration_samples,
                ) != (asset.probe.sample_rate, asset.probe.channels, asset.probe.duration_samples):
                    raise StorageError("music release master differs from the frozen asset")
                if (
                    release.rights_status != "confirmed"
                    or track.commercial_use_status != "confirmed"
                ):
                    blockers.append("music_rights_pending")
                if not track.credits or track.explicit_content is None:
                    blockers.append("music_credits_or_explicit_review_pending")
            else:
                blockers.append("music_metadata_pending")
            tracks.append(
                PublicTrack(
                    placement_id=placement.id,
                    asset=placement.asset,
                    source_sha256=asset.files[0].sha256,
                    start_sample=first - begin,
                    end_sample=last - begin,
                    title=track.title if track else None,
                    artist=release.artist if release else None,
                    credits=track.credits if track else [],
                    explicit_content=track.explicit_content if track else None,
                    isrc=track.isrc if track else None,
                    upc=release.upc if release else None,
                    release_url=track.release_url if track else None,
                )
            )
        tracks.sort(key=lambda item: (item.start_sample, item.placement_id))
        return tracks, releases, blockers

    def _public_inspection(
        self,
        preparation,
        *,
        purpose,
        output,
        inputs_sha256,
        first_frame,
        duration_frames,
        profile,
        tracks,
        rights,
        blockers,
        warnings,
        render_report,
    ):
        thumbnail = None
        if preparation.thumbnail:
            thumbnail = self.assets.require_valid(preparation.thumbnail, production=True)
            if thumbnail.kind != "still" or len(thumbnail.files) != 1:
                raise StorageError("thumbnail must be a single approved PNG still")
            with Image.open(self.assets.resolve(thumbnail.files[0].location)) as image:
                image.load()
                if image.format != "PNG":
                    raise StorageError("thumbnail must be PNG; import an approved PNG version")
        lines, chapter_warning = chapter_lines(preparation.chapters, profile.fps, duration_frames)
        if chapter_warning:
            warnings.append(chapter_warning)
        public = PublicRelease(
            schema_version="1.0",
            title=preparation.title,
            description=preparation.description,
            disclosure_notes=preparation.disclosure_notes,
            purpose=purpose,
            video_sha256=output.sha256,
            snapshot_sha256=inputs_sha256,
            first_frame=first_frame,
            frame_count=duration_frames,
            fps=profile.fps,
            canvas=profile.canvas,
            tracks=tracks,
            chapters=preparation.chapters if lines else [],
            chapter_status="valid" if lines else "invalid" if chapter_warning else "not_requested",
            thumbnail_sha256=thumbnail.files[0].sha256 if thumbnail else None,
            rights=sorted(rights, key=lambda item: (item.asset.id, item.asset.version)),
        )
        digest = content_hash(public)
        status, blockers = review_status(
            public,
            blockers,
            preparation.creative_review,
            preparation.metadata_review,
            metadata_digest=digest,
        )
        inspection = ReleaseInspection(
            schema_version="1.0",
            preparation_id=preparation.id,
            job_id=preparation.job_id,
            status=status,
            metadata_sha256=digest,
            render_report_sha256=content_hash(render_report),
            public=public,
            blockers=sorted(set(blockers)),
            warnings=warnings,
        )
        return inspection, thumbnail, lines

    def inspect(self, preparation):
        return self._inspect(preparation)[0]

    def review(self, identity, *, kind, expected_hash, expected_revision, reviewer, note):
        preparation = self.load(identity)
        inspection = self.inspect(preparation)
        if kind not in {"creative", "metadata"}:
            raise ValueError("review kind must be creative or metadata")
        digest = (
            inspection.public.video_sha256 if kind == "creative" else inspection.metadata_sha256
        )
        if expected_hash != digest:
            raise StorageError("reviewed content hash is stale")
        if kind == "creative" and inspection.public.purpose != "production":
            raise StorageError(
                "synthetic/preview exports cannot receive production creative review"
            )
        record = ReviewRecord(
            reviewer=reviewer, note=note, reviewed_at=datetime.now(UTC), content_sha256=digest
        )
        changed = ReleasePreparation.model_validate(
            {**preparation.model_dump(), f"{kind}_review": record}
        )
        return self.save(changed, expected_revision=expected_revision)

    def export(self, identity, bundle_id, *, require_ready=False):
        bundle_id = TypeAdapter(Identifier).validate_python(bundle_id)
        preparation = self.load(identity)
        inspection, verification, registry, releases, thumbnail, lines = self._inspect(preparation)
        if require_ready and inspection.status != "ready_for_manual_upload":
            raise StorageError("release is not ready: " + ", ".join(inspection.blockers))
        source = self.jobs.ledger.get(preparation.job_id)
        relative = f"bundles/{bundle_id}"
        with self.store._directory(("bundles",), create=True) as parent:
            try:
                os.stat(bundle_id, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise StorageError("bundle destination exists; select a new identity")
            scratch = Path(
                tempfile.mkdtemp(prefix=".tabi-release-", dir=self.store.root / "bundles")
            )
            reserved = False
            try:
                public, private = scratch / "public", scratch / "private"
                public.mkdir(mode=0o700)
                private.mkdir(mode=0o700)

                def write(path, value):
                    payload = (
                        value.encode("utf-8") if isinstance(value, str) else canonical_bytes(value)
                    )
                    with path.open("xb") as stream:
                        stream.write(payload)
                        stream.flush()
                        os.fsync(stream.fileno())

                copy_verified(
                    self.assets.resolve(source.output.location),
                    public / "video.mp4",
                    (source.output.sha256, source.output.size_bytes),
                )
                if thumbnail:
                    record = thumbnail.files[0]
                    copy_verified(
                        self.assets.resolve(record.location),
                        public / "thumbnail.png",
                        (record.sha256, record.size_bytes),
                    )
                write(public / "title.txt", inspection.public.title + "\n")
                write(public / "description.txt", inspection.public.description + "\n")
                write(public / "disclosure-notes.txt", inspection.public.disclosure_notes + "\n")
                write(public / "tracklist.csv", tracklist_csv(inspection.public.tracks))
                if lines:
                    write(public / "chapters.txt", "\n".join(lines) + "\n")
                write(public / "release-metadata.json", inspection.public)
                write(
                    public / "README.txt",
                    f"Status: {inspection.status}\nPurpose: {inspection.public.purpose}\n"
                    "Manual publication only; no platform approval is implied.\n"
                    "Unresolved checks:\n"
                    + "\n".join(inspection.blockers or ["None recorded."])
                    + "\n",
                )
                write(
                    public / "rights-summary.json",
                    {"assets": [item.model_dump(mode="json") for item in inspection.public.rights]},
                )
                write(private / "episode-snapshot.json", registry.snapshot)
                write(
                    private / "render-report.json",
                    self.store.read(source.report_path),
                )
                write(private / "export-verification.json", verification)
                write(private / "release-preparation.json", preparation)
                write(private / "inspection.json", inspection)
                (private / "registry").mkdir(mode=0o700)
                for (asset_id, version), document in registry.documents.items():
                    write(private / "registry" / f"{asset_id}@{version}.json", document)
                (private / "music").mkdir(mode=0o700)
                for release_id, document in releases.items():
                    write(private / "music" / f"{release_id}.json", document)
                write(
                    scratch / "README.txt",
                    (
                        f"Status: {inspection.status}\nPurpose: {inspection.public.purpose}\n"
                        "Only public/ is prepared for manual sharing. Review its text first.\n"
                        "private/ contains source paths and review evidence; keep it private.\n"
                        "Original masters and licence documents remain in project storage.\n"
                        "No upload, platform approval, rights or release IDs are inferred.\n"
                        "Unresolved checks:\n"
                        + "\n".join(inspection.blockers or ["None recorded."])
                        + "\n"
                        + "\n".join(inspection.warnings)
                        + "\n"
                    ),
                )
                files = []
                for path in sorted(scratch.rglob("*")):
                    if path.is_file():
                        digest, size = digest_file(path)
                        files.append(
                            HashedFile(
                                location=MediaPath(
                                    path=f"{relative}/{path.relative_to(scratch).as_posix()}"
                                ),
                                sha256=digest,
                                size_bytes=size,
                            )
                        )
                report = ReleaseBundleReport(
                    schema_version="1.0", bundle_path=relative, inspection=inspection, files=files
                )
                write(scratch / "manifest.json", report)
                # Re-evaluate locks, metadata and reviews after copying. The original
                # source files are never cleanup targets, even on cancellation.
                if self.inspect(preparation) != inspection or self.load(identity) != preparation:
                    raise StorageError("release inputs changed while preparing the bundle")
                for directory in [
                    *sorted(
                        (path for path in scratch.rglob("*") if path.is_dir()),
                        key=lambda path: len(path.parts),
                        reverse=True,
                    ),
                    scratch,
                ]:
                    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                    try:
                        os.fsync(descriptor)
                    finally:
                        os.close(descriptor)
                with self.store.writer_lock():
                    if self.load(identity) != preparation or any(
                        self.store.read(f"releases/{key}.json") != value
                        for key, value in releases.items()
                    ):
                        raise StorageError("release metadata changed before bundle publication")
                    registry.verify()
                    if (
                        thumbnail
                        and self.assets.require_valid(preparation.thumbnail, production=True)
                        != thumbnail
                    ):
                        raise StorageError("thumbnail changed before bundle publication")
                    os.mkdir(bundle_id, mode=0o700, dir_fd=parent)
                    reserved = True
                    os.replace(scratch.name, bundle_id, src_dir_fd=parent, dst_dir_fd=parent)
                    reserved = False
                    os.fsync(parent)
                return report
            finally:
                if reserved:
                    os.rmdir(bundle_id, dir_fd=parent)
                if scratch.exists():
                    shutil.rmtree(scratch)
