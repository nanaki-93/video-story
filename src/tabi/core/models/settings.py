"""Local preferences and measured job progress; no secrets in settings documents."""

import ipaddress
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import AfterValidator, Field

from .base import SHA256, Document, DraftDocument, Frame, Model, Number
from .production import RenderJob


# Read compatibility for saved preferences only; no generator is executed.
def loopback_endpoint(value):
    url = urlsplit(value)
    try:
        local = ipaddress.ip_address(url.hostname or "").is_loopback
    except ValueError:
        local = False
    if (
        url.scheme != "http"
        or not local
        or url.port is None
        or url.username
        or url.password
        or url.path not in {"", "/"}
        or url.query
        or url.fragment
    ):
        raise ValueError("use an explicit HTTP loopback IP and port, without credentials or a path")
    return value.rstrip("/")


Endpoint = Annotated[str, AfterValidator(loopback_endpoint)]


class GenerationPolicy(Model):
    enabled: bool = False
    endpoint: Endpoint = "http://127.0.0.1:8188"
    allowed_workflow_hashes: list[SHA256] = Field(default_factory=list, max_length=100)
    max_output_bytes: int = Field(default=64 * 1024**2, ge=1024, le=256 * 1024**2)


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
