"""Asset identities, provenance and prepared actions; approval is hash-bound."""

from typing import Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from .base import (
    SHA256,
    AssetRef,
    Canvas,
    Crop,
    DraftDocument,
    Frame,
    FrameInterval,
    FrameRate,
    HashedFile,
    Identifier,
    MediaPath,
    Model,
    Point,
    PositiveInt,
    Text,
    Version,
    content_hash,
    unique,
)

CommercialUse = Literal["pending", "confirmed", "not-permitted"]
Channel = Literal["body", "face"]


class Approval(Model):
    status: Literal["draft", "review", "approved", "rejected"] = "draft"
    content_sha256: SHA256 | None = None
    reviewer: Text | None = None
    reviewed_at: AwareDatetime | None = None
    note: Text | None = None

    @model_validator(mode="after")
    def evidence(self) -> Self:
        if self.status == "approved" and not all(
            (self.content_sha256, self.reviewer, self.reviewed_at)
        ):
            raise ValueError("approved content requires its hash, reviewer and review timestamp")
        return self


class ApprovableDocument(DraftDocument):
    approval: Approval = Field(default_factory=Approval)

    @property
    def approval_hash(self) -> str:
        # Bind review to all content/metadata, but not to its review or save revision.
        return content_hash(self.model_dump(mode="json", exclude={"approval", "revision"}))

    @model_validator(mode="after")
    def matching_approval(self) -> Self:
        if (
            self.approval.status == "approved"
            and self.approval.content_sha256 != self.approval_hash
        ):
            raise ValueError("approval hash does not match the current content; review again")
        return self


class GenerationRecord(Model):
    model_name: Text | None = None
    model_sha256: SHA256 | None = None
    workflow: MediaPath | None = None
    workflow_sha256: SHA256 | None = None
    seed: Frame | None = None
    notes: Text | None = None


class Provenance(Model):
    origin: Literal["unknown", "user_supplied", "synthetic", "generated"] = "unknown"
    creator: Text | None = None
    reference_ids: list[Identifier] = Field(default_factory=list)
    licence_evidence: list[MediaPath] = Field(default_factory=list)
    commercial_use: CommercialUse = "pending"
    generation: GenerationRecord | None = None
    notes: Text | None = None


class ProbeData(Model):
    canvas: Canvas | None = None
    fps: FrameRate | None = None
    frame_count: PositiveInt | None = None
    sample_rate: PositiveInt | None = None
    duration_samples: PositiveInt | None = None
    channels: PositiveInt | None = None
    codec: Text | None = None
    pixel_format: Text | None = None
    color_space: Literal["srgb", "bt709", "grayscale", "unknown"] = "unknown"
    alpha_mode: Literal["none", "straight", "premultiplied", "unknown"] = "unknown"
    pixel_aspect: FrameRate = Field(default_factory=lambda: FrameRate(num=1, den=1))


class Compatibility(Model):
    cameras: list[Identifier] = Field(default_factory=list)
    outfits: list[Identifier] = Field(default_factory=list, exclude_if=lambda value: not value)
    templates: list[AssetRef] = Field(default_factory=list)
    channels: list[Channel] = Field(default_factory=list)
    anchor: Point | None = None
    pivot: Point | None = None
    crop: Crop | None = None


class Asset(ApprovableDocument):
    document_type: Literal["asset"]
    version: Version
    kind: Literal["still", "mask", "sequence", "video", "audio", "font"]
    source: MediaPath
    files: list[HashedFile] = Field(min_length=1)
    proxies: list[HashedFile] = Field(default_factory=list)
    probe: ProbeData
    compatibility: Compatibility = Field(default_factory=Compatibility)
    provenance: Provenance = Field(default_factory=Provenance)

    @model_validator(mode="after")
    def media_shape(self) -> Self:
        unique([(f.location.root_id, f.location.path) for f in self.files], "asset file paths")
        probe = self.probe
        if self.kind in {"still", "mask", "sequence", "video"} and probe.canvas is None:
            raise ValueError("visual assets require a canvas")
        if self.kind in {"sequence", "video"} and (probe.fps is None or probe.frame_count is None):
            raise ValueError("animated assets require explicit source fps and frame count")
        if self.kind == "sequence" and len(self.files) != probe.frame_count:
            raise ValueError("sequence file count must match probed frame count")
        if self.kind == "audio" and not all(
            (probe.sample_rate, probe.duration_samples, probe.channels)
        ):
            raise ValueError("audio requires sample rate, channels and sample duration")
        if self.kind == "mask" and probe.color_space != "grayscale":
            raise ValueError("masks must use grayscale values")
        if self.compatibility.crop and probe.canvas:
            crop, canvas = self.compatibility.crop, probe.canvas
            if crop.x + crop.width > canvas.width or crop.y + crop.height > canvas.height:
                raise ValueError("crop exceeds the source canvas")
        if self.provenance.origin == "synthetic" and self.approval.status == "approved":
            raise ValueError("synthetic fixtures cannot receive production approval")
        return self


class Action(Model):
    id: Identifier
    version: Version
    channel: Channel
    start_pose: Identifier
    end_pose: Identifier
    kind: Literal["loop", "one_shot"]
    frame_count: PositiveInt
    clip: AssetRef
    loop: FrameInterval | None = None
    requires_props: dict[Identifier, Identifier] = Field(default_factory=dict)
    resulting_props: dict[Identifier, Identifier] = Field(default_factory=dict)
    compatible_body_poses: list[Identifier] = Field(default_factory=list)
    occupies_channels: list[Channel] = Field(default_factory=list)

    @model_validator(mode="after")
    def loop_shape(self) -> Self:
        if self.kind == "loop":
            if self.loop is None or self.loop.end_frame > self.frame_count:
                raise ValueError("loop actions require an interval within their source frames")
            if self.start_pose != self.end_pose:
                raise ValueError("a loop must return to its starting pose")
        elif self.loop is not None:
            raise ValueError("one-shot actions cannot declare a loop")
        unique(self.occupies_channels, "occupied channels")
        return self


class ActionPack(ApprovableDocument):
    document_type: Literal["action_pack"]
    version: Version
    camera_id: Identifier
    outfit_id: Identifier | None = Field(default=None, exclude_if=lambda value: value is None)
    template: AssetRef
    canvas: Canvas
    anchor: Point
    fps: FrameRate
    alpha_mode: Literal["straight", "premultiplied"]
    actions: list[Action] = Field(min_length=1)

    @model_validator(mode="after")
    def action_ids(self) -> Self:
        unique([a.id for a in self.actions], "action IDs")
        if not (
            0 <= self.anchor.x <= self.canvas.width and 0 <= self.anchor.y <= self.canvas.height
        ):
            raise ValueError("anchor is outside the pack canvas")
        return self
