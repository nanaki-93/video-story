"""Machine capability observations, distinct from verified render results."""

from typing import Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from .base import SHA256, Document, Model
from .production import ValidationIssue


class MachineInfo(Model):
    os: str
    os_version: str
    architecture: str
    cpu: str
    memory_bytes: int | None = Field(default=None, ge=0)
    python_version: str
    python_executable: str
    is_target_m5_pro: bool


class ToolInfo(Model):
    requested: str
    path: str | None = None
    version: str | None = None
    version_output: str | None = None
    sha256: SHA256 | None = None


class StorageInfo(Model):
    path: str
    writable: bool
    free_bytes: int | None = Field(default=None, ge=0)
    required_free_bytes: int = Field(ge=0)


class CapabilityReport(Document):
    document_type: Literal["capability_report"] = "capability_report"
    observed_at: AwareDatetime
    machine: MachineInfo
    ffmpeg: ToolInfo
    ffprobe: ToolInfo
    filters: list[str]
    encoders: list[str]
    hardware_accelerators: list[str]
    required_filters: list[str]
    required_encoders: list[str]
    encoder_verification: Literal["listed_only"] = "listed_only"
    storage: StorageInfo
    fingerprint: SHA256
    ready: bool
    issues: list[ValidationIssue]

    @model_validator(mode="after")
    def consistent_status(self) -> Self:
        if self.ready == any(p.severity == "error" for p in self.issues):
            raise ValueError("ready must agree with capability errors")
        return self


class SpikeVerification(Model):
    decoded_frames: int = Field(gt=0)
    sampled_frames: list[int]
    pixel_checks: int = Field(gt=0)
    max_rgb_error: int = Field(ge=0)
    motion_boundary_checks: int = Field(gt=0)
    max_boundary_error_pixels: int = Field(ge=0)
    rgb_tolerance: int = Field(ge=0)
    decoded_audio_samples: int = Field(gt=0)
    audio_rms: list[float]
    tone_energy_ratio: list[float]
    continuous_timestamps: bool
    full_decode_passed: bool


class RenderSpikeReport(Document):
    document_type: Literal["render_spike_report"] = "render_spike_report"
    fixture_version: Literal["t02-v1"] = "t02-v1"
    synthetic: bool = True
    production_approved: bool = False
    observed_at: AwareDatetime
    machine: MachineInfo
    toolchain_fingerprint: SHA256
    ffmpeg_version: str
    encoder: Literal["libx264", "h264_videotoolbox"]
    hardware_required: bool
    render_seconds: float = Field(gt=0)
    render_fps: float = Field(gt=0)
    output: str
    output_sha256: SHA256
    output_bytes: int = Field(gt=0)
    input_hashes: dict[str, SHA256]
    graph_sha256: SHA256
    verification: SpikeVerification

    @model_validator(mode="after")
    def synthetic_only(self) -> Self:
        if not self.synthetic or self.production_approved:
            raise ValueError("spike reports are synthetic and never approved for production")
        if self.hardware_required != (self.encoder == "h264_videotoolbox"):
            raise ValueError("hardware requirement does not match spike encoder")
        return self
