"""Shared episode validation, immutable compilation and preview application service."""

import os
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from .assets import AssetService
from .config import Settings
from .documents import DocumentError
from .models import CompiledSnapshot, Episode, ValidationReport
from .models.assets import Approval
from .models.base import Canvas, canonical_bytes
from .models.production import OutputProfile, ValidationIssue
from .models.rendering import CompilationResult
from .persistence import StorageError
from .process import ToolError
from .render.backend import FrozenRegistry
from .render.ffmpeg import FFmpegRenderer
from .timeline.compiler import ActionCompiler


class EpisodeService:
    def __init__(self, assets: AssetService, settings: Settings):
        self.assets, self.store, self.settings = assets, assets.store, settings

    def validate(self, episode: Episode, *, purpose: str = "preview") -> ValidationReport:
        try:
            ActionCompiler(self.assets, purpose=purpose).compile(episode)
        except DocumentError as error:
            return error.report()
        except (ValueError, OSError, ToolError) as error:
            return ValidationReport(
                schema_version="1.0",
                document_type="validation_report",
                scope="compile",
                valid=False,
                issues=[
                    ValidationIssue(
                        severity="error",
                        code="compile_failed",
                        location=["episode", episode.id],
                        message=str(error),
                        suggested_fix=(
                            "Resolve the stated asset, timing, pose or state requirement, "
                            "then validate again."
                        ),
                    )
                ],
            )
        return ValidationReport(
            schema_version="1.0",
            document_type="validation_report",
            scope="compile",
            valid=True,
            issues=[],
        )

    def _result(self, snapshot: CompiledSnapshot, digest: str) -> CompilationResult:
        return CompilationResult(
            schema_version="1.0",
            snapshot_sha256=digest,
            snapshot_path=str(self.store.root / "snapshots" / f"{digest}.json"),
            review_content_sha256=snapshot.approval_hash,
            purpose=snapshot.purpose,
            duration_frames=snapshot.episode.duration_frames,
            scheduled_events=len(snapshot.schedule),
            locked_inputs=len(snapshot.locked_assets),
        )

    def compile(
        self, episode: Episode, *, purpose: str = "preview", output: Path | None = None
    ) -> CompilationResult:
        snapshot = ActionCompiler(self.assets, purpose=purpose).compile(episode)
        digest = self.store.save_snapshot(snapshot)
        result = self._result(snapshot, digest)
        if output is not None:
            output = output.expanduser().absolute()
            if output.exists() or output.is_symlink():
                raise StorageError("snapshot export exists; select a new path")
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = None
            try:
                with NamedTemporaryFile(
                    prefix=".tabi-snapshot-", dir=output.parent, delete=False
                ) as stream:
                    temporary = Path(stream.name)
                    stream.write(canonical_bytes(snapshot))
                    stream.flush()
                    os.fsync(stream.fileno())
                if CompiledSnapshot.model_validate_json(temporary.read_bytes()) != snapshot:
                    raise StorageError("snapshot export failed byte/model verification")
                os.link(temporary, output)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        return result

    def inspect_snapshot(self, digest: str) -> dict:
        snapshot = self.store.read_snapshot(digest)
        return {
            "result": self._result(snapshot, digest).model_dump(mode="json"),
            "snapshot": snapshot.model_dump(mode="json"),
        }

    def review_snapshot(
        self, digest: str, *, expected_hash: str, reviewer: str, note: str
    ) -> CompilationResult:
        snapshot = self.store.read_snapshot(digest)
        if snapshot.purpose != "production":
            raise StorageError(
                "only production-purpose snapshots can receive production review; "
                "fixtures remain synthetic"
            )
        if snapshot.approval.status == "approved":
            raise StorageError("snapshot is already approved; preserve its immutable review")
        if snapshot.approval_hash != expected_hash:
            raise StorageError("reviewed snapshot hash is stale")
        FrozenRegistry(self.assets, snapshot, require_approval=False)
        approval = Approval(
            status="approved",
            content_sha256=expected_hash,
            reviewer=reviewer,
            reviewed_at=datetime.now(UTC),
            note=note,
        )
        reviewed = CompiledSnapshot.model_validate({**snapshot.model_dump(), "approval": approval})
        return self._result(reviewed, self.store.save_snapshot(reviewed))

    def frame(self, digest: str, frame: int, output: Path, *, canvas: Canvas | None = None):
        return FFmpegRenderer(self.assets, self.settings).frame(
            self.store.read_snapshot(digest), frame, output, canvas=canvas
        )

    def preview(
        self,
        digest: str,
        start: int,
        end: int,
        output: Path,
        *,
        canvas: Canvas | None = None,
        encoder: str = "libx264",
    ):
        snapshot = self.store.read_snapshot(digest)
        profile = OutputProfile(
            id="preview",
            canvas=canvas or Canvas(width=960, height=540),
            fps=snapshot.episode.fps,
            container="mp4",
            video_codec=encoder,
            pixel_format="yuv420p",
            color_space="bt709",
        )
        return FFmpegRenderer(self.assets, self.settings).clip(
            snapshot, start, end, output, profile
        )
