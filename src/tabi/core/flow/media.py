"""Strict native-clip imports, with explicit source-preserving preparation."""

import json
import os
import shutil
import tempfile
from fractions import Fraction
from pathlib import Path
from uuid import uuid4

from ..assets import AssetService
from ..assets.service import digest_file
from ..models.assets import Provenance
from ..models.base import AssetRef, FrameInterval, HashedFile, MediaPath
from ..models.flow import FlowCandidate, FlowReference
from ..models.registry import ImportRequest
from ..process import run_tool
from .service import FlowError, FlowService, updated


class FlowMedia:
    def __init__(self, service: FlowService, settings):
        self.service, self.settings = service, settings
        self.assets = AssetService(
            service.store,
            roots=service.media_roots,
            ffmpeg=settings.ffmpeg,
            ffprobe=settings.ffprobe,
        )

    def reference(self, source: MediaPath, *, title: str, synthetic: bool = False) -> FlowReference:
        asset = self.assets.import_asset(
            ImportRequest(
                id=f"flow-reference-{uuid4().hex}",
                version="1.0",
                kind="still",
                paths=[source],
                provenance=Provenance(origin="synthetic" if synthetic else "user_supplied"),
            )
        )
        return FlowReference(title=title, media=asset.files[0], synthetic=synthetic)

    def import_result(
        self,
        episode_id: str,
        attempt_id: str,
        source: MediaPath,
        *,
        revision: int,
        source_kind: str = "segment",
        source_range: FrameInterval | None = None,
        prepare_timestamp_gap: bool = False,
        provider_clip_id: str | None = None,
        provider_model: str | None = None,
        observed_credits: int | None = None,
        synthetic: bool = False,
    ):
        episode = self.service.get(episode_id)
        if revision != episode.revision:
            raise FlowError("Video changed; reload before importing this result.")
        attempt = next((item for item in episode.attempts if item.id == attempt_id), None)
        if attempt is None:
            raise FlowError("Choose the pending attempt for this result.")
        path = self.assets.resolve(source)
        source_hash, source_size = digest_file(path)
        existing = next(
            (item for item in episode.candidates if item.attempt_id == attempt_id), None
        )
        if existing:
            original = existing.original or existing.media
            if original.sha256 == source_hash:
                return episode  # A repeated receipt never adds progress or spends again.
            raise FlowError("This attempt already has a different result; prepare a new attempt.")
        if attempt.state not in {"prepared", "awaiting_external", "submitted", "unknown"}:
            raise FlowError("This attempt is closed; reconcile its outcome first.")
        if source_kind not in {"segment", "scene"} or (
            source_kind == "scene" and source_range is None
        ):
            raise FlowError("A cumulative scene needs the explicit new-segment frame range.")
        if any((item.original or item.media).sha256 == source_hash for item in episode.candidates):
            raise FlowError("This file belongs to another attempt; use the new native result.")
        original, preparation = None, None
        cache = f".cache/flow-import-{uuid4().hex}"
        with self.service.store._directory(tuple(cache.split("/")), create=True):
            pass
        scratch = self.service.store.root / cache
        try:
            prepared_source = source
            if prepare_timestamp_gap:
                if source_kind != "scene":
                    raise FlowError("Gap preparation is only for a diagnosed scene download.")
                fps, frames, gaps = self._diagnose_gap(path)
                if source_range.end_frame > frames:
                    raise FlowError("Selected frame range exceeds the decoded scene.")
                original = self._preserve_raw(path, source_hash, source_size)
                target = scratch / "continuous.mp4"
                run_tool(
                    [
                        self.settings.ffmpeg,
                        "-v",
                        "error",
                        "-xerror",
                        "-nostdin",
                        "-protocol_whitelist",
                        "file,pipe",
                        "-i",
                        str(path),
                        "-map",
                        "0:v:0",
                        "-an",
                        "-vf",
                        f"setpts=N*{fps.denominator}/({fps.numerator}*TB)",
                        "-fps_mode",
                        "passthrough",
                        "-c:v",
                        "libx264",
                        "-crf",
                        "18",
                        "-pix_fmt",
                        "yuv420p",
                        "-movflags",
                        "+faststart",
                        str(target),
                    ],
                    timeout=300,
                )
                preparation = (
                    f"Explicit scene-gap correction at decoded frame indexes {gaps}; "
                    "no interpolation or repeated frames; video-only derived version."
                )
                prepared_source = MediaPath(path=f"{cache}/continuous.mp4")
            asset_id = f"flow-{attempt.id}"
            try:
                asset = self.assets.require_valid(AssetRef(id=asset_id, version="1.0"))
                if asset.provenance.notes != f"Flow source SHA256: {source_hash}":
                    raise FlowError("A different source is already associated with this attempt.")
            except FileNotFoundError:
                asset = self.assets.import_asset(
                    ImportRequest(
                        id=asset_id,
                        version="1.0",
                        kind="video",
                        paths=[prepared_source],
                        provenance=Provenance(
                            origin="synthetic" if synthetic else "generated",
                            notes=f"Flow source SHA256: {source_hash}",
                        ),
                    )
                )
            if digest_file(path) != (source_hash, source_size):
                raise FlowError("Source changed during import; retry after its download completes.")
            probe = asset.probe
            if probe.fps != episode.recipe.fps:
                raise FlowError("Source frame rate differs; start with matching video settings.")
            trim = source_range or FrameInterval(start_frame=0, end_frame=probe.frame_count)
            if trim.end_frame > probe.frame_count:
                raise FlowError("Selected range exceeds the actual native frames.")
            candidate = FlowCandidate(
                id=uuid4().hex,
                attempt_id=attempt.id,
                parent_id=attempt.parent_id,
                parent_sha256=attempt.parent_sha256,
                media=asset.files[0],
                original=original,
                preparation=preparation,
                fps=probe.fps,
                canvas=probe.canvas,
                frame_count=probe.frame_count,
                trim=trim,
                technical_ok=True,
                technical_notes=["Full strict decode and every presentation timestamp verified."],
            )
            attempt = updated(
                attempt,
                state="received",
                observed_credits=observed_credits,
                provider_clip_id=provider_clip_id,
                provider_model=provider_model,
            )
            return self.service.save(
                updated(
                    episode,
                    attempts=[
                        attempt if item.id == attempt.id else item for item in episode.attempts
                    ],
                    candidates=[*episode.candidates, candidate],
                ),
                expected_revision=revision,
            )
        finally:
            shutil.rmtree(scratch)  # Only this invocation's owned temporary directory.

    def _preserve_raw(self, path: Path, digest: str, size: int) -> HashedFile:
        folder = f"sources/flow-originals/{uuid4().hex}"
        with self.service.store._directory(tuple(folder.split("/")), create=True):
            pass
        destination = self.service.store.root / folder / "original.mp4"
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as output:
            temporary = Path(output.name)
            try:
                with path.open("rb") as source:
                    shutil.copyfileobj(source, output)
                output.flush()
                os.fsync(output.fileno())
                if digest_file(temporary) != (digest, size):
                    raise FlowError("Original copy changed during preparation.")
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)
        return HashedFile(
            location=MediaPath(path=f"{folder}/original.mp4"), sha256=digest, size_bytes=size
        )

    def _diagnose_gap(self, path: Path):
        payload = json.loads(
            run_tool(
                [
                    self.settings.ffprobe,
                    "-v",
                    "error",
                    "-protocol_whitelist",
                    "file,pipe",
                    "-select_streams",
                    "v:0",
                    "-show_streams",
                    "-show_frames",
                    "-show_entries",
                    "stream=r_frame_rate,time_base:frame=best_effort_timestamp",
                    "-of",
                    "json",
                    str(path),
                ],
                timeout=300,
                max_bytes=32 * 1024 * 1024,
            )
        )
        stream = payload["streams"][0]
        fps = Fraction(stream["r_frame_rate"])
        step = 1 / fps / Fraction(stream["time_base"])
        ticks = [int(item["best_effort_timestamp"]) for item in payload["frames"]]
        gaps = []
        for index in range(1, len(ticks)):
            delta = ticks[index] - ticks[index - 1]
            if abs(delta - step) <= 1:
                continue
            if delta < step or abs(delta / step - round(delta / step)) > Fraction(1, 100):
                raise FlowError("This is not a simple timestamp gap; request native segments.")
            gaps.append(index)
        if not gaps:
            raise FlowError("No scene timestamp gap was diagnosed; use the unmodified native file.")
        return fps, len(ticks), gaps
