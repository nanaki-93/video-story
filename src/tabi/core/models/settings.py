"""Local preferences and measured job progress; no secrets in settings documents."""

from typing import Literal

from pydantic import Field

from .base import Document, DraftDocument, Frame, Number
from .generation import GenerationPolicy
from .production import RenderJob


class AppPreferences(DraftDocument):
    document_type: Literal["app_preferences"] = "app_preferences"
    id: Literal["local"] = "local"
    cache_budget_bytes: Frame = 20 * 1024**3
    export_preset: Literal["proxy", "1080p", "4k"] = "1080p"
    encoder: Literal["libx264", "h264_videotoolbox"] = "libx264"
    theme: Literal["dusk", "contrast"] = "dusk"
    generation: GenerationPolicy = Field(default_factory=GenerationPolicy)


class JobProgress(Document):
    document_type: Literal["job_progress"] = "job_progress"
    job: RenderJob
    elapsed_running_seconds: Number = Field(ge=0)
    measured_fps: Number | None = Field(ge=0)
    eta_seconds: Number | None = Field(ge=0)
