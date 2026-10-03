"""Frozen compiler output, job ledger and factual release metadata contracts."""

from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, Field, HttpUrl, model_validator

from .assets import ApprovableDocument, Channel, CommercialUse
from .base import (
    SHA256,
    AssetRef,
    Canvas,
    Document,
    DraftDocument,
    Frame,
    FrameInterval,
    FrameRate,
    HashedFile,
    Identifier,
    MediaPath,
    Model,
    Number,
    PositiveInt,
    RelativePath,
    ResolvedAssetLock,
    Text,
    unique,
)
from .episode import Episode, TrackPlacement
from .scenes import LandmarkEvent, PropEvent


class Fingerprint(Model):
    name: Text
    version: Text
    sha256: SHA256


class ScheduledAction(FrameInterval):
    type: Literal["action"]
    id: Identifier
    scene_id: Identifier
    pack: AssetRef
    action_id: Identifier
    clip: AssetRef
    channel: Channel
    source_start_frame: Frame
    phase_origin_frame: Frame
    loop: FrameInterval | None = None
    start_pose: Identifier
    end_pose: Identifier
    resulting_props: dict[Identifier, Identifier] = Field(default_factory=dict)


ScheduleEvent = Annotated[ScheduledAction | LandmarkEvent | PropEvent, Field(discriminator="type")]


class CompiledSnapshot(ApprovableDocument):
    document_type: Literal["compiled_snapshot"]
    purpose: Literal["preview", "production", "synthetic_test"]
    episode: Episode
    locked_assets: list[ResolvedAssetLock]
    schedule: list[ScheduleEvent]
    audio_placements: list[TrackPlacement]
    compiler: Fingerprint
    prng: Fingerprint

    @model_validator(mode="after")
    def locked_inputs(self) -> Self:
        if self.revision != 0:
            raise ValueError("snapshots do not have mutable revisions")
        if self.purpose == "synthetic_test" and self.approval.status == "approved":
            raise ValueError("synthetic snapshots cannot receive production approval")
        unique([lock.id for lock in self.locked_assets], "snapshot lock IDs")
        locks = {(lock.id, lock.version): lock.sha256 for lock in self.locked_assets}
        references = self.episode.references()
        for event in self.schedule:
            if isinstance(event, ScheduledAction):
                references.add((event.pack.id, event.pack.version))
                references.add((event.clip.id, event.clip.version))
            if isinstance(event, LandmarkEvent):
                references.add((event.asset.id, event.asset.version))
        references.update((track.asset.id, track.asset.version) for track in self.audio_placements)
        if not references.issubset(locks):
            raise ValueError("snapshot is missing resolved asset hashes")
        for lock in self.episode.asset_locks:
            if lock.sha256 is not None and locks[(lock.id, lock.version)] != lock.sha256:
                raise ValueError("snapshot lock differs from the authored locked hash")
        unique([event.id for event in self.schedule], "schedule IDs")
        scenes = {scene.id: scene for scene in self.episode.scenes}
        for event in self.schedule:
            if event.scene_id not in scenes:
                raise ValueError("schedule references an unknown scene")
            scene = scenes[event.scene_id]
            start = event.frame if isinstance(event, PropEvent) else event.start_frame
            end = start + 1 if isinstance(event, PropEvent) else event.end_frame
            if not scene.start_frame <= start < end <= scene.end_frame:
                raise ValueError("scheduled event is outside its scene")
        if any(
            t.start_sample + t.duration_samples
            > self.episode.fps.sample_at(self.episode.duration_frames)
            for t in self.audio_placements
        ):
            raise ValueError("compiled audio extends past the episode")
        return self


class OutputProfile(Model):
    id: Identifier
    canvas: Canvas
    fps: FrameRate
    container: Literal["mp4", "mkv"]
    video_codec: Text
    pixel_format: Text
    color_space: Literal["bt709"]
    audio_codec: Text | None = None
    audio_gain_db: Number = Field(default=0.0, ge=-120, le=24, exclude_if=lambda v: v == 0)
    sample_rate: Literal[48000] = 48000
    video_bitrate: PositiveInt | None = None


class ChunkRecord(Model):
    index: Frame
    first_frame: Frame
    frame_count: PositiveInt
    state: Literal["pending", "rendering", "verified", "failed"]
    output: HashedFile | None = None

    @model_validator(mode="after")
    def verified_output(self) -> Self:
        if self.state == "verified" and self.output is None:
            raise ValueError("verified chunks require an output hash and path")
        return self


class JobError(Model):
    code: Identifier
    message: Text
    log_path: RelativePath | None = None


class RenderJob(DraftDocument):
    document_type: Literal["render_job"]
    snapshot_sha256: SHA256
    profile: OutputProfile
    backend: Fingerprint
    state: Literal["queued", "running", "paused", "interrupted", "cancelled", "failed", "verified"]
    duration_frames: PositiveInt
    chunks: list[ChunkRecord]
    completed_frames: Frame = 0
    output: HashedFile | None = None
    report_path: RelativePath | None = None
    error: JobError | None = None

    @model_validator(mode="after")
    def ledger(self) -> Self:
        cursor = 0
        for index, chunk in enumerate(self.chunks):
            if chunk.index != index or chunk.first_frame != cursor:
                raise ValueError("chunk ledger must be ordered and contiguous")
            cursor += chunk.frame_count
        if self.chunks and cursor != self.duration_frames:
            raise ValueError("chunk ledger does not cover the full render interval")
        completed = sum(chunk.frame_count for chunk in self.chunks if chunk.state == "verified")
        if self.completed_frames != completed:
            raise ValueError("progress must equal the verified chunk frame count")
        if self.state == "verified" and (
            self.output is None or self.report_path is None or completed != self.duration_frames
        ):
            raise ValueError("verified jobs require all chunks, output and verification report")
        if self.state == "failed" and self.error is None:
            raise ValueError("failed job requires a diagnostic")
        return self


class Credit(Model):
    name: Text
    role: Text


class ReleaseTrack(Model):
    asset: AssetRef
    title: Text
    master: MediaPath
    sha256: SHA256 | None = None
    sample_rate: PositiveInt
    channels: PositiveInt
    duration_samples: PositiveInt
    credits: list[Credit] = Field(default_factory=list)
    explicit_content: bool | None = None
    isrc: Text | None = None
    commercial_use_status: CommercialUse = "pending"
    ai_use_notes: Text | None = None
    source_project: MediaPath | None = None
    release_url: HttpUrl | None = None


class ReviewRecord(Model):
    reviewer: Text
    reviewed_at: AwareDatetime
    content_sha256: SHA256
    note: Text | None = None


class ReleaseRecord(DraftDocument):
    document_type: Literal["release_record"]
    artist: Text
    release_title: Text
    tracks: list[ReleaseTrack] = Field(min_length=1)
    upc: Text | None = None
    rights_status: CommercialUse = "pending"
    status: Literal[
        "draft",
        "technically_verified",
        "creatively_reviewed",
        "rights_reviewed",
        "ready_for_manual_upload",
        "uploaded",
        "published",
    ] = "draft"
    technical_report: MediaPath | None = None
    creative_review: ReviewRecord | None = None
    disclosure_reviewed: bool = False
    disclosure_notes: Text | None = None
    claim_notes: Text | None = None
    release_links: dict[Identifier, HttpUrl] = Field(default_factory=dict)
    published_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def factual_readiness(self) -> Self:
        unique([(t.asset.id, t.asset.version) for t in self.tracks], "release track assets")
        if self.status != "draft" and self.technical_report is None:
            raise ValueError("technical verification report is required for this release status")
        if self.status in {
            "creatively_reviewed",
            "rights_reviewed",
            "ready_for_manual_upload",
            "uploaded",
            "published",
        }:
            if self.creative_review is None:
                raise ValueError("creative review evidence is missing")
        if self.status in {"rights_reviewed", "ready_for_manual_upload", "uploaded", "published"}:
            if self.rights_status != "confirmed" or any(
                t.commercial_use_status != "confirmed" for t in self.tracks
            ):
                raise ValueError("pending rights cannot gain a reviewed/ready release status")
        if self.status in {"ready_for_manual_upload", "uploaded", "published"}:
            if not self.disclosure_reviewed or any(t.sha256 is None for t in self.tracks):
                raise ValueError("upload readiness needs reviewed disclosure and hashed masters")
        if self.status in {"uploaded", "published"} and not self.release_links:
            raise ValueError("uploaded status requires an actual recorded platform link")
        if self.status == "published" and self.published_at is None:
            raise ValueError("published status requires its actual timestamp")
        return self


class ValidationIssue(Model):
    severity: Literal["error", "warning", "info"]
    code: Identifier
    location: list[str | int]
    message: Text
    suggested_fix: Text


class ValidationReport(Document):
    document_type: Literal["validation_report"]
    scope: Literal["structure", "compile"] = "structure"
    valid: bool
    issues: list[ValidationIssue]

    @model_validator(mode="after")
    def consistent_status(self) -> Self:
        if self.valid == any(issue.severity == "error" for issue in self.issues):
            raise ValueError("valid flag does not match report errors")
        return self
