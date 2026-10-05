"""Small, strict contracts for a reviewed sequence of complete Flow clips."""

import hashlib
from typing import Literal, Self

from pydantic import Field, HttpUrl, model_validator

from .base import (
    SHA256,
    Canvas,
    DraftDocument,
    Frame,
    FrameInterval,
    FrameRate,
    HashedFile,
    Identifier,
    Model,
    PositiveInt,
    RelativePath,
    ResolvedAssetLock,
    Text,
    content_hash,
    unique,
)
from .episode import TrackPlacement
from .production import OutputProfile

BeatKind = Literal["rest", "look", "pickup", "sip", "return_cup", "sway", "deep_breath", "district"]


class FlowReference(Model):
    title: Text
    media: HashedFile
    rights: Literal["pending", "confirmed", "not-permitted"] = "pending"
    synthetic: bool = False


class FlowState(Model):
    """User-confirmed facts, independent of the recipe's intended appearance."""

    cup_kind: Literal["unknown", "none", "takeaway", "ceramic"] = "unknown"
    cup_position: Literal["unknown", "table", "held"] = "unknown"
    has_handle: bool | None = None
    has_saucer: bool | None = None
    hands: Literal["unknown", "resting", "holding_cup"] = "unknown"
    pose: Literal["unknown", "resting", "watching", "sipping"] = "unknown"
    district: Text = "Tokyo"
    inventory: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def coherent(self) -> Self:
        unique(self.inventory, "inventory items")
        if self.cup_kind == "none" and self.cup_position != "unknown":
            raise ValueError("an absent cup cannot be on the table or held")
        if self.cup_position == "held" and self.hands != "holding_cup":
            raise ValueError("a held cup requires holding hands")
        if self.hands == "holding_cup" and self.cup_position != "held":
            raise ValueError("holding hands require a held cup")
        return self


class FlowBeat(Model):
    id: Identifier
    kind: BeatKind
    target_frame: Frame
    district: Text | None = None

    @model_validator(mode="after")
    def transition(self) -> Self:
        if (self.kind == "district") != (self.district is not None):
            raise ValueError("only a district beat requires a new district")
        return self


class FlowRecipe(Model):
    identity: Text = (
        "TABI, the pink-lavender axolotl in the supplied approved reference, "
        "with dark-brown eyes, attached pink gills and purple headphones."
    )
    outfit: Text = "The reference's green coat with leopard-patterned trim."
    setting: Text = "A warm wooden sightseeing train carriage travelling through Tokyo at sunset."
    camera: Text = "A fixed wide view across the aisle, at seated eye level."
    exterior: Text = "Tokyo scenery moves continuously from right to left with natural parallax."
    opening_inventory: list[Text] = Field(
        default_factory=lambda: ["one takeaway cup on the table", "one open book", "one pen"]
    )
    opening_mode: Literal["text_reference", "image_motion"] = "image_motion"
    project_url: HttpUrl | None = None
    fps: FrameRate = Field(default_factory=lambda: FrameRate(num=24, den=1))
    target_frames: PositiveInt = 2160
    beats: list[FlowBeat] = Field(default_factory=list)

    @model_validator(mode="after")
    def settings(self) -> Self:
        unique([beat.id for beat in self.beats], "beat IDs")
        if any(beat.target_frame >= self.target_frames for beat in self.beats):
            raise ValueError("beat must start inside the target video")
        if self.beats != sorted(self.beats, key=lambda beat: beat.target_frame):
            raise ValueError("beats must be ordered by target frame")
        if self.project_url and (
            self.project_url.scheme != "https"
            or self.project_url.host not in {"flow.google.com", "labs.google"}
            or self.project_url.username
            or self.project_url.password
        ):
            raise ValueError("project link must be an HTTPS Google Flow URL")
        return self


class FlowLimits(Model):
    credit_ceiling: Frame
    remaining_allowance: Frame
    estimated_credit_per_attempt: Frame
    max_retries_per_beat: Frame = Field(default=1, le=3)
    max_attempts: PositiveInt = Field(default=30, le=100)
    allowance_checked_at: Text

    @model_validator(mode="after")
    def allowance(self) -> Self:
        if self.credit_ceiling > self.remaining_allowance:
            raise ValueError("credit ceiling exceeds checked remaining allowance")
        return self


class FlowAttempt(DraftDocument):
    document_type: Literal["flow_attempt"] = "flow_attempt"
    episode_id: Identifier
    parent_id: Identifier | None = None
    parent_sha256: SHA256 | None = None
    recipe_sha256: SHA256
    references_sha256: SHA256
    beat: FlowBeat
    mode: Literal["text_reference", "image_motion", "extend"]
    prompt: Text
    prompt_sha256: SHA256
    template_version: Literal["1"] = "1"
    state: Literal["prepared", "awaiting_external", "submitted", "unknown", "received", "failed"]
    reserved_credits: Frame
    observed_credits: Frame | None = None
    retry_index: Frame = 0
    retry_reason: Text | None = None
    provider_clip_id: Text | None = None
    provider_model: Text | None = None
    diagnostic: Text | None = None

    @model_validator(mode="after")
    def binding(self) -> Self:
        if (self.parent_id is None) != (self.parent_sha256 is None):
            raise ValueError("parent identity and hash must be provided together")
        if (self.mode == "extend") != (self.parent_id is not None):
            raise ValueError("native continuation requires a parent; opening must have none")
        if hashlib.sha256(self.prompt.encode()).hexdigest() != self.prompt_sha256:
            raise ValueError("prompt hash does not match the submitted text")
        if self.retry_index and self.retry_reason is None:
            raise ValueError("a retry requires a focused correction reason")
        if self.state in {"unknown", "failed"} and self.diagnostic is None:
            raise ValueError("unknown or failed attempt requires a diagnostic")
        return self


class FlowCandidate(Model):
    id: Identifier
    attempt_id: Identifier
    parent_id: Identifier | None
    parent_sha256: SHA256 | None
    media: HashedFile
    original: HashedFile | None = None
    preparation: Text | None = None
    fps: FrameRate
    canvas: Canvas
    frame_count: PositiveInt
    trim: FrameInterval
    technical_ok: bool
    technical_notes: list[Text] = Field(default_factory=list)
    review: Literal["pending", "accepted", "rejected"] = "pending"
    reviewed_sha256: SHA256 | None = None
    review_note: Text | None = None
    observed_state: FlowState | None = None
    safe_end_frame: Frame | None = None
    review_packet: RelativePath | None = None

    @property
    def usable_frames(self) -> int:
        return self.trim.end_frame - self.trim.start_frame

    @model_validator(mode="after")
    def review_binding(self) -> Self:
        if self.trim.end_frame > self.frame_count:
            raise ValueError("trim exceeds actual decoded frames")
        if (self.parent_id is None) != (self.parent_sha256 is None):
            raise ValueError("candidate parent requires its hash")
        if (self.original is None) != (self.preparation is None):
            raise ValueError("preparation must identify its immutable original")
        if self.review != "pending" and self.reviewed_sha256 != self.media.sha256:
            raise ValueError("review must bind the exact candidate content hash")
        if self.review != "pending" and self.review_note is None:
            raise ValueError("review requires a note")
        if self.review == "accepted" and (not self.technical_ok or self.observed_state is None):
            raise ValueError("acceptance requires technical verification and observed ending state")
        if self.safe_end_frame is not None and not (
            self.trim.start_frame < self.safe_end_frame <= self.trim.end_frame
        ):
            raise ValueError("safe ending must be inside the reviewed trim")
        return self


class FlowEpisode(DraftDocument):
    document_type: Literal["flow_episode"] = "flow_episode"
    title: Text
    recipe: FlowRecipe
    references: list[FlowReference] = Field(default_factory=list)
    limits: FlowLimits
    attempts: list[FlowAttempt] = Field(default_factory=list)
    candidates: list[FlowCandidate] = Field(default_factory=list)
    accepted_ids: list[Identifier] = Field(default_factory=list)
    paused: bool = False

    @property
    def accepted_frames(self) -> int:
        by_id = {candidate.id: candidate for candidate in self.candidates}
        return sum(by_id[key].usable_frames for key in self.accepted_ids)

    @model_validator(mode="after")
    def lineage(self) -> Self:
        unique([item.id for item in self.attempts], "attempt IDs")
        unique([item.id for item in self.candidates], "candidate IDs")
        unique([item.attempt_id for item in self.candidates], "candidate attempt associations")
        unique(self.accepted_ids, "accepted IDs")
        attempts = {item.id: item for item in self.attempts}
        candidates = {item.id: item for item in self.candidates}
        for attempt in self.attempts:
            if attempt.episode_id != self.id:
                raise ValueError("attempt belongs to a different episode")
            if attempt.parent_id is not None:
                parent = candidates.get(attempt.parent_id)
                if parent is None or parent.media.sha256 != attempt.parent_sha256:
                    raise ValueError("attempt parent is missing or changed")
        for candidate in self.candidates:
            attempt = attempts.get(candidate.attempt_id)
            if attempt is None or attempt.state != "received":
                raise ValueError("candidate requires its received attempt")
            if (candidate.parent_id, candidate.parent_sha256) != (
                attempt.parent_id,
                attempt.parent_sha256,
            ):
                raise ValueError("candidate and attempt parent disagree")
            path = {candidate.id}
            parent_id = candidate.parent_id
            while parent_id is not None:
                if parent_id in path or parent_id not in candidates:
                    raise ValueError("candidate lineage contains a cycle or missing parent")
                path.add(parent_id)
                parent_id = candidates[parent_id].parent_id
        previous = None
        for key in self.accepted_ids:
            candidate = candidates.get(key)
            if candidate is None or candidate.review != "accepted":
                raise ValueError("active branch requires accepted candidates")
            if candidate.parent_id != previous or candidate.fps != self.recipe.fps:
                raise ValueError("active branch must be contiguous and use the recipe frame rate")
            previous = key
        return self


class FlowSegment(Model):
    candidate_id: Identifier
    media: HashedFile
    trim: FrameInterval
    observed_state: FlowState


class FlowExportInputs(Model):
    episode_id: Identifier
    episode_revision: Frame
    recipe_sha256: SHA256
    references: list[FlowReference]
    segments: list[FlowSegment] = Field(min_length=1)
    profile: OutputProfile
    duration_frames: PositiveInt
    tracks: list[TrackPlacement] = Field(default_factory=list)
    audio_locks: list[ResolvedAssetLock] = Field(default_factory=list)
    pipeline_sha256: SHA256
    toolchain_sha256: SHA256

    @model_validator(mode="after")
    def coverage(self) -> Self:
        unique([item.candidate_id for item in self.segments], "export segment IDs")
        if sum(item.trim.end_frame - item.trim.start_frame for item in self.segments) != (
            self.duration_frames
        ):
            raise ValueError("export trims must cover the exact target frames")
        if self.profile.container != "mp4" or self.profile.pixel_format != "yuv420p":
            raise ValueError("Flow delivery requires MP4 and yuv420p")
        locks = {(item.id, item.version) for item in self.audio_locks}
        if any((item.asset.id, item.asset.version) not in locks for item in self.tracks):
            raise ValueError("audio placements require immutable asset locks")
        samples = self.profile.fps.sample_at(self.duration_frames)
        if any(item.start_sample + item.duration_samples > samples for item in self.tracks):
            raise ValueError("audio placement extends past the export")
        return self


class FlowExport(DraftDocument):
    document_type: Literal["flow_export"] = "flow_export"
    episode_id: Identifier
    inputs: FlowExportInputs
    inputs_sha256: SHA256
    state: Literal["queued", "running", "interrupted", "cancelled", "failed", "verified"]
    output: HashedFile | None = None
    report_path: RelativePath | None = None
    diagnostic: Text | None = None
    owner: Identifier | None = None
    cancel_requested: bool = False

    @model_validator(mode="after")
    def frozen_inputs(self) -> Self:
        if self.episode_id != self.inputs.episode_id or self.inputs_sha256 != content_hash(
            self.inputs
        ):
            raise ValueError("export inputs and content hash disagree")
        if self.state == "verified" and (self.output is None or self.report_path is None):
            raise ValueError("verified export requires output and verification report")
        if self.state == "failed" and self.diagnostic is None:
            raise ValueError("failed export requires a diagnostic")
        return self
