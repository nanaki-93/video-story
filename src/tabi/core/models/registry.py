"""Requests and observed asset health, separate from immutable approval records."""

from typing import Literal

from pydantic import Field

from .assets import Compatibility, Provenance
from .base import SHA256, AssetRef, Document, FrameRate, MediaPath, Model


class ImportRequest(AssetRef):
    kind: Literal["still", "mask", "sequence", "video", "audio", "font"]
    paths: list[MediaPath] = Field(min_length=1)
    mode: Literal["copy", "link"] = "copy"
    fps: FrameRate | None = None
    compatibility: Compatibility = Field(default_factory=Compatibility)
    provenance: Provenance = Field(default_factory=Provenance)


class FileHealth(Model):
    location: MediaPath
    expected_sha256: SHA256
    observed_sha256: SHA256 | None = None
    status: Literal["ok", "missing", "changed", "inaccessible"]
    message: str | None = None


class AssetHealth(Document):
    document_type: Literal["asset_health"] = "asset_health"
    asset: AssetRef
    content_sha256: SHA256
    files: list[FileHealth]
    proxies: list[FileHealth]
    source_available: bool
    media_valid: bool
    approval_valid: bool
    rights: Literal["pending", "confirmed", "not-permitted"]
    publication_ready: bool
