"""Saved preview selection and frame-addressed review notes; never production approval."""

from typing import Literal

from pydantic import Field

from .base import SHA256, DraftDocument, Frame, Identifier, Model, Text
from .production import Fingerprint


class PreviewMarker(Model):
    id: Identifier
    snapshot_sha256: SHA256
    frame: Frame
    note: Text = Field(max_length=4000)


class PreviewSelection(DraftDocument):
    document_type: Literal["preview_selection"] = "preview_selection"
    snapshot_sha256: SHA256
    pipeline: Fingerprint
    job_id: Identifier
    previous_job_id: Identifier | None = None
    markers: list[PreviewMarker] = Field(default_factory=list, max_length=10000)
