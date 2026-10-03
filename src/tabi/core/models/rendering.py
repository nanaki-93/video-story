"""Observed renderer output; technical verification is not creative approval."""

from typing import Literal

from pydantic import Field

from .audio import AudioMixReport, AudioVerification
from .base import (
    SHA256,
    AbsolutePath,
    Canvas,
    Document,
    Frame,
    FrameRate,
    HashedFile,
    Identifier,
    Model,
    Number,
    PositiveInt,
)
from .production import Fingerprint, OutputProfile


class AssemblyInfo(Model):
    mode: Literal["stream_copy", "reencode"]
    chunk_sha256: list[SHA256] = Field(min_length=1)
    fallback_reason: str | None = None


class CacheReuse(Model):
    key: SHA256
    origin_snapshot_sha256: SHA256


class MP4Layout(Model):
    moov_offset: Frame
    first_mdat_offset: Frame
    fast_start: Literal[True] = True


class VideoVerification(Model):
    codec: Literal["h264"] = "h264"
    profile: Literal["High"] = "High"
    level: PositiveInt
    pixel_format: Literal["yuv420p"] = "yuv420p"
    canvas: Canvas
    fps: FrameRate
    frame_count: PositiveInt
    duration_seconds: Number = Field(gt=0)
    container_duration_seconds: Number = Field(gt=0)
    bit_rate: PositiveInt | None = None
    color_space: Literal["bt709"] = "bt709"
    color_range: Literal["tv"] = "tv"
    progressive: Literal[True] = True
    timestamps_verified: Literal[True] = True
    full_decode_passed: Literal[True] = True
    mp4: MP4Layout


class ExportVerification(Document):
    document_type: Literal["export_verification"] = "export_verification"
    job_id: Identifier
    snapshot_sha256: SHA256
    output: HashedFile
    profile: OutputProfile
    video: VideoVerification
    audio: AudioVerification | None = None


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
    cache_reuse: CacheReuse | None = Field(default=None, exclude_if=lambda v: v is None)
    normalized_cache_hits: Frame = Field(default=0, exclude_if=lambda v: v == 0)
    video_verification: VideoVerification | None = Field(
        default=None, exclude_if=lambda v: v is None
    )


class CompilationResult(Document):
    document_type: Literal["compilation_result"] = "compilation_result"
    snapshot_sha256: SHA256
    snapshot_path: AbsolutePath
    review_content_sha256: SHA256
    purpose: Literal["preview", "production", "synthetic_test"]
    duration_frames: PositiveInt
    scheduled_events: Frame
    locked_inputs: Frame
