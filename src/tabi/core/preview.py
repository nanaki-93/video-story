"""Renderer-backed review workflow shared by transports; global integer frame addresses."""

from uuid import uuid4

from .authoring import AuthoringService
from .episodes import EpisodeService
from .jobs.planner import pipeline_fingerprint
from .models.base import Canvas, canonical_bytes, content_hash
from .models.preview import PreviewMarker, PreviewSelection
from .models.rendering import RenderReport
from .persistence import RevisionConflict
from .render.profiles import preset_profile
from .timeline.compiler import ActionCompiler


class PreviewService:
    def __init__(self, assets, settings, jobs):
        self.assets, self.store, self.settings, self.jobs = assets, assets.store, settings, jobs
        self.author = AuthoringService(assets)

    def selection(self, identity):
        self.author.episode(identity)  # Validate both identity and document ownership.
        try:
            return self.store.read(f"previews/{identity}.json")
        except FileNotFoundError:
            return None

    def inspect(self, identity):
        episode = self.author.episode(identity)
        selected = self.selection(identity)
        current_hash, issue = None, None
        try:
            current_hash = content_hash(
                ActionCompiler(self.assets, purpose="preview").compile(episode)
            )
        except (ValueError, OSError) as error:
            issue = str(error)
        stale = selected is not None and (
            current_hash != selected.snapshot_sha256 or selected.pipeline != pipeline_fingerprint()
        )
        return {
            "schema_version": "1.0",
            "document_type": "web_preview",
            "episode": episode,
            "snapshot_episode": self.store.read_snapshot(selected.snapshot_sha256).episode
            if selected
            else None,
            "selection": selected,
            "stale": stale,
            "issue": issue,
            "job": self.jobs.ledger.get(selected.job_id) if selected else None,
            "previous_job": self.jobs.ledger.get(selected.previous_job_id)
            if selected and selected.previous_job_id
            else None,
        }

    def submit(self, identity, expected_revision, first, end):
        with self.store.exclusive_lock(f".preview-{identity}.lock"):
            episode = self.author.episode(identity)
            if episode.revision != expected_revision:
                raise RevisionConflict("Episode changed; reload before generating its preview")
            if not 0 <= first < end <= episode.duration_frames:
                raise ValueError("Preview range must be inside the episode")
            result = EpisodeService(self.assets, self.settings).compile(episode)
            if self.author.episode(identity).revision != expected_revision:
                raise RevisionConflict("Episode changed during compilation; reload and retry")
            previous = self.selection(identity)
            previous_job = None
            if previous:
                previous_job = (
                    previous.job_id
                    if self.jobs.ledger.get(previous.job_id).state == "verified"
                    else previous.previous_job_id
                )
            job = self.jobs.submit(
                result.snapshot_sha256,
                preset_profile("proxy", fps=episode.fps),
                f"exports/previews/{uuid4().hex}.mp4",
                first_frame=first,
                end_frame=end,
            )
            selected = PreviewSelection(
                schema_version="1.0",
                id=identity,
                revision=previous.revision if previous else 0,
                snapshot_sha256=result.snapshot_sha256,
                pipeline=pipeline_fingerprint(),
                job_id=job.id,
                previous_job_id=previous_job,
                markers=previous.markers if previous else [],
            )
            return self.store.save_draft(
                selected, expected_revision=previous.revision if previous else None
            )

    def marker(self, identity, snapshot_hash, frame, note):
        with self.store.exclusive_lock(f".preview-{identity}.lock"):
            selected = self.selection(identity)
            if selected is None or selected.snapshot_sha256 != snapshot_hash:
                raise RevisionConflict("Preview changed; reload before marking this frame")
            snapshot = self.store.read_snapshot(snapshot_hash)
            if not 0 <= frame < snapshot.episode.duration_frames:
                raise ValueError("Review frame is outside the snapshot")
            marker = PreviewMarker(
                id=uuid4().hex, snapshot_sha256=snapshot_hash, frame=frame, note=note
            )
            updated = PreviewSelection.model_validate(
                {**selected.model_dump(), "markers": [*selected.markers, marker]}
            )
            return self.store.save_draft(updated, expected_revision=selected.revision)

    def frame(self, digest, frame):
        # A bounded, cancellable still lane is owned separately from export jobs.
        with self.store.exclusive_lock(".preview-frame.lock"):
            identity = uuid4().hex
            relative = f"previews/frames/{identity}.png"
            with self.store._directory(("previews", "frames"), create=True):
                pass
            report = EpisodeService(self.assets, self.settings).frame(
                digest, frame, self.store.root / relative, canvas=Canvas(width=960, height=540)
            )
            self.store._atomic_write(
                f"previews/frames/{identity}.json", canonical_bytes(report), overwrite=False
            )
            return identity, report

    def frame_report(self, identity):
        # Only a report emitted by frame() addresses a downloadable still.
        from pydantic import TypeAdapter

        from .models.base import Identifier

        TypeAdapter(Identifier).validate_python(identity)
        report = self.store.read(f"previews/frames/{identity}.json")
        if not isinstance(report, RenderReport) or report.frame_count != 1:
            raise ValueError("Not a verified frame report")
        return f"previews/frames/{identity}.png", report
