"""Disposable, content-addressed cache inventory and conservative storage planning."""

from typing import Literal, Self

from pydantic import AwareDatetime, Field, JsonValue, model_validator

from .base import SHA256, AbsolutePath, Document, Frame, HashedFile, Model, Text, content_hash
from .production import OutputProfile
from .rendering import RenderReport

CACHE_PREFIX = ".cache/tabi-v1"
CacheKind = Literal["normalized_image", "video_chunk"]


class CacheEntry(Document):
    document_type: Literal["cache_entry"] = "cache_entry"
    kind: CacheKind
    key: SHA256
    descriptor: dict[str, JsonValue]
    created_at: AwareDatetime
    output: HashedFile
    report: RenderReport | None = None
    warnings: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def owned_identity(self) -> Self:
        suffix = "png" if self.kind == "normalized_image" else "mp4"
        expected = f"{CACHE_PREFIX}/{self.kind}/{self.key}/payload.{suffix}"
        if self.key != content_hash(self.descriptor):
            raise ValueError("cache key differs from its canonical descriptor")
        if self.output.location.root_id != "project" or self.output.location.path != expected:
            raise ValueError("cache payload must have its exact owned content-addressed path")
        if (self.kind == "video_chunk") != (self.report is not None):
            raise ValueError("video cache entries require their original verification report")
        if self.report and (self.report.output_sha256, self.report.output_bytes) != (
            self.output.sha256,
            self.output.size_bytes,
        ):
            raise ValueError("cache verification report differs from its payload")
        return self


class CacheSummary(Model):
    kind: CacheKind
    key: SHA256
    size_bytes: Frame
    sha256: SHA256
    created_at: AwareDatetime
    valid: bool
    protected: bool = False
    message: Text | None = None


class CacheInventory(Document):
    document_type: Literal["cache_inventory"] = "cache_inventory"
    root: AbsolutePath
    inventory_sha256: SHA256
    entries: list[CacheSummary]
    entry_bytes: Frame
    warnings: list[Text] = Field(default_factory=list)


class CachePruneReport(Document):
    document_type: Literal["cache_prune_report"] = "cache_prune_report"
    removed: list[SHA256]
    removed_entry_bytes: Frame
    remaining_entry_bytes: Frame


class StorageEstimate(Document):
    document_type: Literal["storage_estimate"] = "storage_estimate"
    snapshot_sha256: SHA256
    first_frame: Frame
    frame_count: Frame = Field(gt=0)
    profile: OutputProfile
    available_bytes: Frame
    normalization_bytes: Frame
    video_bytes: Frame
    audio_bytes: Frame
    reserve_bytes: Frame
    required_additional_bytes: Frame
    sufficient: bool
    assumptions: list[Text]

    @model_validator(mode="after")
    def totals(self) -> Self:
        if self.required_additional_bytes != (
            self.normalization_bytes + self.video_bytes + self.audio_bytes + self.reserve_bytes
        ) or self.sufficient != (self.available_bytes >= self.required_additional_bytes):
            raise ValueError("storage totals and availability must agree")
        return self
