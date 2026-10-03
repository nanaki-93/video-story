"""Machine capability observations, distinct from verified render results."""

from datetime import datetime
from typing import Literal

from pydantic import Field

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
    observed_at: datetime
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
