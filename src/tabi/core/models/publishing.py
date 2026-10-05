"""Release preparation and public allowlists; no platform approval is inferred."""

from typing import Literal, Self

from pydantic import AwareDatetime, Field, HttpUrl, model_validator

from .assets import CommercialUse
from .base import (
    SHA256,
    AssetRef,
    Canvas,
    Document,
    DraftDocument,
    Frame,
    FrameRate,
    HashedFile,
    Identifier,
    Model,
    PositiveInt,
    RelativePath,
    Text,
    unique,
)
from .production import Credit, ReviewRecord


class Chapter(Model):
    start_frame: Frame
    title: Text


class FlowCommercialReview(Model):
    provider_models: list[Text] = Field(min_length=1)
    commercial_use: CommercialUse = "pending"
    reviewed_at: AwareDatetime
    reviewer: Text
    source_links: list[HttpUrl] = Field(min_length=1)
    note: Text

    @model_validator(mode="after")
    def official_sources(self):
        if any(
            link.host not in {"support.google.com", "policies.google.com"}
            for link in self.source_links
        ):
            raise ValueError("Flow terms evidence must link to official Google sources")
        unique(self.provider_models, "reviewed provider models")
        return self


class ReleasePreparation(DraftDocument):
    document_type: Literal["release_preparation"] = "release_preparation"
    job_id: Identifier
    source_kind: Literal["layered", "flow"] = Field(
        default="layered", exclude_if=lambda value: value == "layered"
    )
    flow_terms: FlowCommercialReview | None = Field(
        default=None, exclude_if=lambda value: value is None
    )
    concept_notes: str = Field(default="", exclude_if=lambda value: not value)
    title: Text
    description: str = ""
    disclosure_notes: str = ""
    chapters: list[Chapter] = Field(default_factory=list)
    thumbnail: AssetRef | None = None
    creative_review: ReviewRecord | None = None
    metadata_review: ReviewRecord | None = None
    manual_links: list[HttpUrl] = Field(default_factory=list, exclude_if=lambda value: not value)
    claim_notes: str = Field(default="", exclude_if=lambda value: not value)


class PublicTrack(Model):
    placement_id: Identifier
    asset: AssetRef
    source_sha256: SHA256
    start_sample: Frame
    end_sample: PositiveInt
    title: Text | None = None
    artist: Text | None = None
    credits: list[Credit] = Field(default_factory=list)
    explicit_content: bool | None = None
    isrc: Text | None = None
    upc: Text | None = None
    release_url: HttpUrl | None = None

    @model_validator(mode="after")
    def interval(self) -> Self:
        if self.end_sample <= self.start_sample:
            raise ValueError("public track interval must be nonempty")
        return self


class PublicAssetRights(Model):
    asset: AssetRef
    commercial_use: CommercialUse
    approved: bool
    synthetic: bool


class PublicRelease(Document):
    document_type: Literal["public_release"] = "public_release"
    title: Text
    description: str
    disclosure_notes: str
    purpose: Literal["preview", "production", "synthetic_test"]
    video_sha256: SHA256
    snapshot_sha256: SHA256
    first_frame: Frame
    frame_count: PositiveInt
    fps: FrameRate
    canvas: Canvas
    tracks: list[PublicTrack]
    chapters: list[Chapter]
    chapter_status: Literal["not_requested", "valid", "invalid"]
    thumbnail_sha256: SHA256 | None
    rights: list[PublicAssetRights]


class ReleaseInspection(Document):
    document_type: Literal["release_inspection"] = "release_inspection"
    preparation_id: Identifier
    job_id: Identifier
    status: Literal[
        "technically_verified", "creatively_reviewed", "rights_reviewed", "ready_for_manual_upload"
    ]
    metadata_sha256: SHA256
    render_report_sha256: SHA256
    public: PublicRelease
    blockers: list[Identifier]
    warnings: list[Text]

    @model_validator(mode="after")
    def readiness(self) -> Self:
        if (self.status == "ready_for_manual_upload") != (not self.blockers):
            raise ValueError("release readiness must agree with its unresolved checks")
        return self


class ReleaseBundleReport(Document):
    document_type: Literal["release_bundle_report"] = "release_bundle_report"
    bundle_path: RelativePath
    inspection: ReleaseInspection
    files: list[HashedFile]

    @model_validator(mode="after")
    def contained(self) -> Self:
        unique([item.location.path for item in self.files], "bundle files")
        if any(
            item.location.root_id != "project"
            or not item.location.path.startswith(self.bundle_path + "/")
            for item in self.files
        ):
            raise ValueError("bundle manifest files must be inside the bundle")
        return self
