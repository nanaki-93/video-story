/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "web_releases";
export type CancelRequested = boolean;
export type Diagnostic = string | null;
export type DocumentType1 = "flow_export";
export type EpisodeId = string;
export type Id = string;
export type Id1 = string;
export type Sha256 = string;
export type Version = string;
export type AudioLocks = ResolvedAssetLock[];
export type DurationFrames = number;
export type EpisodeId1 = string;
export type EpisodeRevision = number;
export type PipelineSha256 = string;
export type AudioBitrate = number;
export type AudioCodec = string | null;
export type AudioGainDb = number;
export type Height = number;
export type Width = number;
export type ColorSpace = "bt709";
export type Container = "mp4" | "mkv";
export type Den = number;
export type Num = number;
export type Id2 = string;
export type PixelFormat = string;
export type SampleRate = 48000;
export type VideoBitrate = number | null;
export type VideoCodec = string;
export type RecipeSha256 = string;
export type Key = string | null;
export type Path = string;
export type RootId = string;
export type Sha2561 = string;
export type SizeBytes = number;
export type ReviewNote = string | null;
export type Rights = "pending" | "confirmed" | "not-permitted";
export type CupKind = "unknown" | "none" | "takeaway" | "ceramic";
export type CupPosition = "unknown" | "table" | "held";
export type District = string;
export type Hands = "unknown" | "resting" | "holding_cup";
export type HasHandle = boolean | null;
export type HasSaucer = boolean | null;
export type Inventory = string[];
export type Pose = "unknown" | "resting" | "watching" | "sipping";
export type Synthetic = boolean;
export type Title = string;
export type References = FlowReference[];
/**
 * @minItems 1
 */
export type Segments = [FlowSegment, ...FlowSegment[]];
export type CandidateId = string;
export type EndFrame = number;
export type StartFrame = number;
export type ToolchainSha256 = string;
export type Id3 = string;
export type Version1 = string;
export type FadeInSamples = number;
export type FadeOutSamples = number;
export type GainDb = number;
export type Id4 = string;
export type LoopCrossfadeSamples = number;
export type LoopDurationSamples = number | null;
export type ReleaseId = string | null;
export type Role = "music" | "ambience";
export type SampleRate1 = 48000;
export type StartSample = number;
export type TrimEndSample = number;
export type TrimStartSample = number;
export type Tracks = TrackPlacement[];
export type InputsSha256 = string;
export type Owner = string | null;
export type ReportPath = string | null;
export type Revision = number;
export type SchemaVersion = "1.0";
export type State = "queued" | "running" | "interrupted" | "cancelled" | "failed" | "verified";
export type FlowExports = FlowExport[];
export type StartFrame1 = number;
export type Title1 = string;
export type Chapters = Chapter[];
export type ClaimNotes = string;
export type ConceptNotes = string;
export type ContentSha256 = string;
export type Note = string | null;
export type ReviewedAt = string;
export type Reviewer = string;
export type Description = string;
export type DisclosureNotes = string;
export type DocumentType2 = "release_preparation";
export type CommercialUse = "pending" | "confirmed" | "not-permitted";
export type Note1 = string;
/**
 * @minItems 1
 */
export type ProviderModels = [string, ...string[]];
export type ReviewedAt1 = string;
export type Reviewer1 = string;
/**
 * @minItems 1
 */
export type SourceLinks = [string, ...string[]];
export type Id5 = string;
export type JobId = string;
export type ManualLinks = string[];
export type Revision1 = number;
export type SchemaVersion1 = "1.0";
export type SourceKind = "layered" | "flow";
export type Title2 = string;
export type Preparations = ReleasePreparation[];
export type SchemaVersion2 = "1.0";

export interface WebReleases {
  document_type?: DocumentType;
  flow_exports?: FlowExports;
  preparations: Preparations;
  schema_version: SchemaVersion2;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "FlowExport".
 */
export interface FlowExport {
  cancel_requested?: CancelRequested;
  diagnostic?: Diagnostic;
  document_type?: DocumentType1;
  episode_id: EpisodeId;
  id: Id;
  inputs: FlowExportInputs;
  inputs_sha256: InputsSha256;
  output?: HashedFile | null;
  owner?: Owner;
  report_path?: ReportPath;
  revision?: Revision;
  schema_version: SchemaVersion;
  state: State;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "FlowExportInputs".
 */
export interface FlowExportInputs {
  audio_locks?: AudioLocks;
  duration_frames: DurationFrames;
  episode_id: EpisodeId1;
  episode_revision: EpisodeRevision;
  pipeline_sha256: PipelineSha256;
  profile: OutputProfile;
  recipe_sha256: RecipeSha256;
  references: References;
  segments: Segments;
  toolchain_sha256: ToolchainSha256;
  tracks?: Tracks;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "ResolvedAssetLock".
 */
export interface ResolvedAssetLock {
  id: Id1;
  sha256: Sha256;
  version: Version;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "OutputProfile".
 */
export interface OutputProfile {
  audio_bitrate?: AudioBitrate;
  audio_codec?: AudioCodec;
  audio_gain_db?: AudioGainDb;
  canvas: Canvas;
  color_space: ColorSpace;
  container: Container;
  fps: FrameRate;
  id: Id2;
  pixel_format: PixelFormat;
  sample_rate?: SampleRate;
  video_bitrate?: VideoBitrate;
  video_codec: VideoCodec;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "FlowReference".
 */
export interface FlowReference {
  key?: Key;
  media: HashedFile;
  review_note?: ReviewNote;
  rights?: Rights;
  starting_state?: FlowState | null;
  synthetic?: Synthetic;
  title: Title;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha2561;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * User-confirmed facts, independent of the recipe's intended appearance.
 *
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "FlowState".
 */
export interface FlowState {
  cup_kind?: CupKind;
  cup_position?: CupPosition;
  district?: District;
  hands?: Hands;
  has_handle?: HasHandle;
  has_saucer?: HasSaucer;
  inventory?: Inventory;
  pose?: Pose;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "FlowSegment".
 */
export interface FlowSegment {
  candidate_id: CandidateId;
  media: HashedFile;
  observed_state: FlowState;
  trim: FrameInterval;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "FrameInterval".
 */
export interface FrameInterval {
  end_frame: EndFrame;
  start_frame: StartFrame;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "TrackPlacement".
 */
export interface TrackPlacement {
  asset: AssetRef;
  fade_in_samples?: FadeInSamples;
  fade_out_samples?: FadeOutSamples;
  gain_db?: GainDb;
  id: Id4;
  loop_crossfade_samples?: LoopCrossfadeSamples;
  loop_duration_samples?: LoopDurationSamples;
  release_id?: ReleaseId;
  role?: Role;
  sample_rate?: SampleRate1;
  start_sample: StartSample;
  trim_end_sample: TrimEndSample;
  trim_start_sample: TrimStartSample;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id3;
  version: Version1;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "ReleasePreparation".
 */
export interface ReleasePreparation {
  chapters?: Chapters;
  claim_notes?: ClaimNotes;
  concept_notes?: ConceptNotes;
  creative_review?: ReviewRecord | null;
  description?: Description;
  disclosure_notes?: DisclosureNotes;
  document_type?: DocumentType2;
  flow_terms?: FlowCommercialReview | null;
  id: Id5;
  job_id: JobId;
  manual_links?: ManualLinks;
  metadata_review?: ReviewRecord | null;
  revision?: Revision1;
  schema_version: SchemaVersion1;
  source_kind?: SourceKind;
  thumbnail?: AssetRef | null;
  title: Title2;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "Chapter".
 */
export interface Chapter {
  start_frame: StartFrame1;
  title: Title1;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "ReviewRecord".
 */
export interface ReviewRecord {
  content_sha256: ContentSha256;
  note?: Note;
  reviewed_at: ReviewedAt;
  reviewer: Reviewer;
}
/**
 * This interface was referenced by `WebReleases`'s JSON-Schema
 * via the `definition` "FlowCommercialReview".
 */
export interface FlowCommercialReview {
  commercial_use?: CommercialUse;
  note: Note1;
  provider_models: ProviderModels;
  reviewed_at: ReviewedAt1;
  reviewer: Reviewer1;
  source_links: SourceLinks;
}
