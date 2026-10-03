"""Observed renderer output; technical verification is not creative approval."""

from typing import Literal

from pydantic import Field

from .audio import AudioMixReport, AudioVerification
from .base import SHA256, AbsolutePath, Canvas, Document, Frame, FrameRate, Model, PositiveInt
from .production import Fingerprint


class AssemblyInfo(Model):
    mode: Literal["stream_copy", "reencode"]
    chunk_sha256: list[SHA256] = Field(min_length=1)
    fallback_reason: str | None = None


class RenderReport(Document):
    document_type: Literal["render_report"] = "render_report"
    purpose: Literal["preview", "production", "synthetic_test"]
    snapshot_sha256: SHA256
    first_frame: Frame
    frame_count: PositiveInt
    canvas: Canvas
    fps: FrameRate
    output: AbsolutePath
    output_sha256: SHA256
    output_bytes: PositiveInt
    graph_sha256: SHA256
    backend: Fingerprint
    toolchain_fingerprint: SHA256
    render_seconds: float = Field(gt=0)
    full_decode_passed: bool
    timestamps_verified: bool
    normalized_images: Frame
    warnings: list[str] = Field(default_factory=list)
    audio_mix: AudioMixReport | None = None
    audio_verification: AudioVerification | None = None
    assembly: AssemblyInfo | None = Field(default=None, exclude_if=lambda v: v is None)


class CompilationResult(Document):
    document_type: Literal["compilation_result"] = "compilation_result"
    snapshot_sha256: SHA256
    snapshot_path: AbsolutePath
    review_content_sha256: SHA256
    purpose: Literal["preview", "production", "synthetic_test"]
    duration_frames: PositiveInt
    scheduled_events: Frame
    locked_inputs: Frame
