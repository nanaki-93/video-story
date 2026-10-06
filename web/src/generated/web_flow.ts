/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type ContentSha256 = string | null;
export type Note = string | null;
export type ReviewedAt = string | null;
export type Reviewer = string | null;
export type Status = "draft" | "review" | "approved" | "rejected";
export type X = number;
export type Y = number;
export type Cameras = string[];
export type Channels = ("body" | "face")[];
export type Height = number;
export type Width = number;
export type X1 = number;
export type Y1 = number;
export type Outfits = string[];
export type Id = string;
export type Version = string;
export type Templates = AssetRef[];
export type DocumentType = "asset";
/**
 * @minItems 1
 */
export type Files = [HashedFile, ...HashedFile[]];
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
export type Id1 = string;
export type Kind = "still" | "mask" | "sequence" | "video" | "audio" | "font";
export type AlphaMode = "none" | "straight" | "premultiplied" | "unknown";
export type Height1 = number;
export type Width1 = number;
export type Channels1 = number | null;
export type Codec = string | null;
export type ColorSpace = "srgb" | "bt709" | "grayscale" | "unknown";
export type DurationSamples = number | null;
export type Den = number;
export type Num = number;
export type FrameCount = number | null;
export type PixelFormat = string | null;
export type SampleRate = number | null;
export type CommercialUse = "pending" | "confirmed" | "not-permitted";
export type Creator = string | null;
export type ManifestSha256 = string | null;
export type ModelName = string | null;
export type ModelSha256 = string | null;
export type Notes = string | null;
export type PromptId = string | null;
export type Seed = number | null;
export type WorkflowSha256 = string | null;
export type LicenceEvidence = MediaPath[];
export type Notes1 = string | null;
export type Origin = "unknown" | "user_supplied" | "synthetic" | "generated";
export type ReferenceIds = string[];
export type Proxies = HashedFile[];
export type Revision = number;
export type SchemaVersion = "1.0";
export type Version1 = string;
export type PreparedSamples = number;
export type AudioSources = AudioSource[];
export type CandidateUrl = string | null;
export type DocumentType1 = "web_flow";
export type AcceptedIds = string[];
export type District = string | null;
export type Id2 = string;
export type Kind1 = "rest" | "look" | "pickup" | "sip" | "return_cup" | "sway" | "deep_breath" | "district";
export type TargetFrame = number;
export type Diagnostic = string | null;
export type DocumentType2 = "flow_attempt";
export type EpisodeId = string;
export type Id3 = string;
export type Mode = "text_reference" | "image_motion" | "extend" | "shot_start";
export type ObservedCredits = number | null;
export type ParentId = string | null;
export type ParentSha256 = string | null;
export type Prompt = string;
export type PromptSha256 = string;
export type ProviderClipId = string | null;
export type ProviderModel = string | null;
export type RecipeSha256 = string;
export type ReferencesSha256 = string;
export type ReservedCredits = number;
export type RetryIndex = number;
export type RetryReason = string | null;
export type Revision1 = number;
export type SchemaVersion1 = "1.0";
export type ShotId = string | null;
export type State = "prepared" | "awaiting_external" | "submitted" | "unknown" | "received" | "failed";
export type TemplateVersion = "1" | "2";
export type Attempts = FlowAttempt[];
export type AttemptId = string;
export type FrameCount1 = number;
export type Id4 = string;
export type CupKind = "unknown" | "none" | "takeaway" | "ceramic";
export type CupPosition = "unknown" | "table" | "held";
export type District1 = string;
export type Hands = "unknown" | "resting" | "holding_cup";
export type HasHandle = boolean | null;
export type HasSaucer = boolean | null;
export type Inventory = string[];
export type Pose = "unknown" | "resting" | "watching" | "sipping";
export type ParentId1 = string | null;
export type ParentSha2561 = string | null;
export type Preparation = string | null;
export type RetryFocus = ("particles" | "mouth" | "identity" | "props" | "motion" | "action") | null;
export type Review = "pending" | "accepted" | "rejected";
export type ReviewNote = string | null;
export type ReviewPacket = string | null;
export type ReviewedSha256 = string | null;
export type SafeEndFrame = number | null;
export type TechnicalNotes = string[];
export type TechnicalOk = boolean;
export type EndFrame = number;
export type StartFrame = number;
export type Candidates = FlowCandidate[];
export type DocumentType3 = "flow_episode";
export type Id5 = string;
export type AllowanceCheckedAt = string;
export type CreditCeiling = number;
export type EstimatedCreditPerAttempt = number;
export type EstimatedStartCredit = number | null;
export type MaxAttempts = number;
export type MaxRetriesPerBeat = number;
export type RemainingAllowance = number;
export type Paused = boolean;
export type Beats = FlowBeat[];
export type Camera = string;
export type Exterior = string;
export type Identity = string;
export type OpeningInventory = string[];
export type OpeningMode = "text_reference" | "image_motion";
export type Outfit = string;
export type ProjectUrl = string | null;
export type Setting = string;
/**
 * @minItems 1
 */
export type Beats1 = [FlowBeat, ...FlowBeat[]];
export type DurationFrames = number;
export type Framing = "wide" | "medium" | "close";
export type Id6 = string;
export type MaxExtensions = number;
export type ReferenceKey = string;
export type Title = string;
export type Shots = FlowShot[];
export type TargetFrames = number;
export type Key = string | null;
export type ReviewNote1 = string | null;
export type Rights = "pending" | "confirmed" | "not-permitted";
export type Synthetic = boolean;
export type Title1 = string;
export type References = FlowReference[];
export type Revision2 = number;
export type SchemaVersion2 = "1.0";
export type Title2 = string;
export type Episodes = FlowEpisode[];
export type CancelRequested = boolean;
export type Diagnostic1 = string | null;
export type DocumentType4 = "flow_export";
export type EpisodeId1 = string;
export type Id7 = string;
export type Id8 = string;
export type Sha2561 = string;
export type Version2 = string;
export type AudioLocks = ResolvedAssetLock[];
export type DurationFrames1 = number;
export type EpisodeId2 = string;
export type EpisodeRevision = number;
export type PipelineSha256 = string;
export type AudioBitrate = number;
export type AudioCodec = string | null;
export type AudioGainDb = number;
export type ColorSpace1 = "bt709";
export type Container = "mp4" | "mkv";
export type Id9 = string;
export type PixelFormat1 = string;
export type SampleRate1 = 48000;
export type VideoBitrate = number | null;
export type VideoCodec = string;
export type RecipeSha2561 = string;
export type References1 = FlowReference[];
/**
 * @minItems 1
 */
export type Segments = [FlowSegment, ...FlowSegment[]];
export type CandidateId = string;
export type ToolchainSha256 = string;
export type FadeInSamples = number;
export type FadeOutSamples = number;
export type GainDb = number;
export type Id10 = string;
export type LoopCrossfadeSamples = number;
export type LoopDurationSamples = number | null;
export type ReleaseId = string | null;
export type Role = "music" | "ambience";
export type SampleRate2 = 48000;
export type StartSample = number;
export type TrimEndSample = number;
export type TrimStartSample = number;
export type Tracks = TrackPlacement[];
export type InputsSha256 = string;
export type Owner = string | null;
export type ReportPath = string | null;
export type Revision3 = number;
export type SchemaVersion3 = "1.0";
export type State1 = "queued" | "running" | "interrupted" | "cancelled" | "failed" | "verified";
export type Exports = FlowExport[];
export type NextReferenceKey = string | null;
export type AcceptedFrames = number;
export type Action =
  "paused" | "waiting_flow" | "review" | "finish" | "choose_reference" | "needs_attention" | "prepare";
export type AttemptId1 = string | null;
export type CandidateId1 = string | null;
export type CreditUnits = number;
export type Message = string;
export type ParentId2 = string | null;
export type TargetFrames1 = number;
export type ParentUrl = string | null;
export type Framing1 = "wide" | "medium" | "close";
export type Instruction = string;
export type Key1 = string;
export type Url = string | null;
export type ReferenceSlots = FlowReferenceSlot[];
export type ReferenceUrls = string[];
export type RemainingBeats = FlowBeat[];
export type Checklist = string[];
export type Diagnostics = string[];
export type Frame = number;
export type Role1 = string;
export type Url1 = string;
export type Images = FlowImage[];
export type JoinUrl = string | null;
export type SafeCutFrame = number | null;
export type SchemaVersion4 = "1.0";
export type AcceptedFrames1 = number;
export type DurationFrames2 = number;
export type Framing2 = "wide" | "medium" | "close";
export type Id11 = string;
export type Index = number;
export type ReferenceKey1 = string;
export type StartFrame1 = number;
export type State2 = "complete" | "current" | "pending";
export type Title3 = string;
export type Shots1 = FlowShotView[];
export type StartingReferenceKey = string | null;
export type TargetSamples = number;

export interface WebFlow {
  audio_sources?: AudioSources;
  candidate_url?: CandidateUrl;
  document_type?: DocumentType1;
  episode?: FlowEpisode | null;
  episodes: Episodes;
  exports?: Exports;
  next_reference_key?: NextReferenceKey;
  next_step?: FlowNext | null;
  parent_url?: ParentUrl;
  preset: FlowRecipe;
  reference_slots?: ReferenceSlots;
  reference_urls?: ReferenceUrls;
  remaining_beats?: RemainingBeats;
  review?: FlowReviewView | null;
  safe_cut_frame?: SafeCutFrame;
  schema_version: SchemaVersion4;
  shots?: Shots1;
  starting_reference_key?: StartingReferenceKey;
  target_samples?: TargetSamples;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "AudioSource".
 */
export interface AudioSource {
  asset: Asset;
  prepared_samples: PreparedSamples;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "Asset".
 */
export interface Asset {
  approval?: Approval;
  compatibility?: Compatibility;
  document_type: DocumentType;
  files: Files;
  id: Id1;
  kind: Kind;
  probe: ProbeData;
  provenance?: Provenance;
  proxies?: Proxies;
  revision?: Revision;
  schema_version: SchemaVersion;
  source: MediaPath;
  version: Version1;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "Approval".
 */
export interface Approval {
  content_sha256?: ContentSha256;
  note?: Note;
  reviewed_at?: ReviewedAt;
  reviewer?: Reviewer;
  status?: Status;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "Compatibility".
 */
export interface Compatibility {
  anchor?: Point | null;
  cameras?: Cameras;
  channels?: Channels;
  crop?: Crop | null;
  outfits?: Outfits;
  pivot?: Point | null;
  templates?: Templates;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "Point".
 */
export interface Point {
  x: X;
  y: Y;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "Crop".
 */
export interface Crop {
  height: Height;
  width: Width;
  x: X1;
  y: Y1;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "ProbeData".
 */
export interface ProbeData {
  alpha_mode?: AlphaMode;
  canvas?: Canvas | null;
  channels?: Channels1;
  codec?: Codec;
  color_space?: ColorSpace;
  duration_samples?: DurationSamples;
  fps?: FrameRate | null;
  frame_count?: FrameCount;
  pixel_aspect?: FrameRate;
  pixel_format?: PixelFormat;
  sample_rate?: SampleRate;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height1;
  width: Width1;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "Provenance".
 */
export interface Provenance {
  commercial_use?: CommercialUse;
  creator?: Creator;
  generation?: GenerationRecord | null;
  licence_evidence?: LicenceEvidence;
  notes?: Notes1;
  origin?: Origin;
  reference_ids?: ReferenceIds;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "GenerationRecord".
 */
export interface GenerationRecord {
  manifest_sha256?: ManifestSha256;
  model_hashes?: ModelHashes;
  model_name?: ModelName;
  model_sha256?: ModelSha256;
  notes?: Notes;
  prompt_id?: PromptId;
  seed?: Seed;
  workflow?: MediaPath | null;
  workflow_sha256?: WorkflowSha256;
}
export interface ModelHashes {
  [k: string]: string;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowEpisode".
 */
export interface FlowEpisode {
  accepted_ids?: AcceptedIds;
  attempts?: Attempts;
  candidates?: Candidates;
  document_type?: DocumentType3;
  id: Id5;
  limits: FlowLimits;
  paused?: Paused;
  recipe: FlowRecipe;
  references?: References;
  revision?: Revision2;
  schema_version: SchemaVersion2;
  title: Title2;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowAttempt".
 */
export interface FlowAttempt {
  beat: FlowBeat;
  diagnostic?: Diagnostic;
  document_type?: DocumentType2;
  episode_id: EpisodeId;
  id: Id3;
  mode: Mode;
  observed_credits?: ObservedCredits;
  parent_id?: ParentId;
  parent_sha256?: ParentSha256;
  prompt: Prompt;
  prompt_sha256: PromptSha256;
  provider_clip_id?: ProviderClipId;
  provider_model?: ProviderModel;
  recipe_sha256: RecipeSha256;
  references_sha256: ReferencesSha256;
  reserved_credits: ReservedCredits;
  retry_index?: RetryIndex;
  retry_reason?: RetryReason;
  revision?: Revision1;
  schema_version: SchemaVersion1;
  shot_id?: ShotId;
  state: State;
  template_version?: TemplateVersion;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowBeat".
 */
export interface FlowBeat {
  district?: District;
  id: Id2;
  kind: Kind1;
  target_frame: TargetFrame;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowCandidate".
 */
export interface FlowCandidate {
  attempt_id: AttemptId;
  canvas: Canvas;
  fps: FrameRate;
  frame_count: FrameCount1;
  id: Id4;
  media: HashedFile;
  observed_state?: FlowState | null;
  original?: HashedFile | null;
  parent_id: ParentId1;
  parent_sha256: ParentSha2561;
  preparation?: Preparation;
  retry_focus?: RetryFocus;
  review?: Review;
  review_note?: ReviewNote;
  review_packet?: ReviewPacket;
  reviewed_sha256?: ReviewedSha256;
  safe_end_frame?: SafeEndFrame;
  technical_notes?: TechnicalNotes;
  technical_ok: TechnicalOk;
  trim: FrameInterval;
}
/**
 * User-confirmed facts, independent of the recipe's intended appearance.
 *
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowState".
 */
export interface FlowState {
  cup_kind?: CupKind;
  cup_position?: CupPosition;
  district?: District1;
  hands?: Hands;
  has_handle?: HasHandle;
  has_saucer?: HasSaucer;
  inventory?: Inventory;
  pose?: Pose;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FrameInterval".
 */
export interface FrameInterval {
  end_frame: EndFrame;
  start_frame: StartFrame;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowLimits".
 */
export interface FlowLimits {
  allowance_checked_at: AllowanceCheckedAt;
  credit_ceiling: CreditCeiling;
  estimated_credit_per_attempt: EstimatedCreditPerAttempt;
  estimated_start_credit?: EstimatedStartCredit;
  max_attempts?: MaxAttempts;
  max_retries_per_beat?: MaxRetriesPerBeat;
  remaining_allowance: RemainingAllowance;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowRecipe".
 */
export interface FlowRecipe {
  beats?: Beats;
  camera?: Camera;
  exterior?: Exterior;
  fps?: FrameRate;
  identity?: Identity;
  opening_inventory?: OpeningInventory;
  opening_mode?: OpeningMode;
  outfit?: Outfit;
  project_url?: ProjectUrl;
  setting?: Setting;
  shots?: Shots;
  target_frames?: TargetFrames;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowShot".
 */
export interface FlowShot {
  beats: Beats1;
  duration_frames: DurationFrames;
  framing: Framing;
  id: Id6;
  max_extensions?: MaxExtensions;
  reference_key: ReferenceKey;
  title: Title;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowReference".
 */
export interface FlowReference {
  key?: Key;
  media: HashedFile;
  review_note?: ReviewNote1;
  rights?: Rights;
  starting_state?: FlowState | null;
  synthetic?: Synthetic;
  title: Title1;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowExport".
 */
export interface FlowExport {
  cancel_requested?: CancelRequested;
  diagnostic?: Diagnostic1;
  document_type?: DocumentType4;
  episode_id: EpisodeId1;
  id: Id7;
  inputs: FlowExportInputs;
  inputs_sha256: InputsSha256;
  output?: HashedFile | null;
  owner?: Owner;
  report_path?: ReportPath;
  revision?: Revision3;
  schema_version: SchemaVersion3;
  state: State1;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowExportInputs".
 */
export interface FlowExportInputs {
  audio_locks?: AudioLocks;
  duration_frames: DurationFrames1;
  episode_id: EpisodeId2;
  episode_revision: EpisodeRevision;
  pipeline_sha256: PipelineSha256;
  profile: OutputProfile;
  recipe_sha256: RecipeSha2561;
  references: References1;
  segments: Segments;
  toolchain_sha256: ToolchainSha256;
  tracks?: Tracks;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "ResolvedAssetLock".
 */
export interface ResolvedAssetLock {
  id: Id8;
  sha256: Sha2561;
  version: Version2;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "OutputProfile".
 */
export interface OutputProfile {
  audio_bitrate?: AudioBitrate;
  audio_codec?: AudioCodec;
  audio_gain_db?: AudioGainDb;
  canvas: Canvas;
  color_space: ColorSpace1;
  container: Container;
  fps: FrameRate;
  id: Id9;
  pixel_format: PixelFormat1;
  sample_rate?: SampleRate1;
  video_bitrate?: VideoBitrate;
  video_codec: VideoCodec;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowSegment".
 */
export interface FlowSegment {
  candidate_id: CandidateId;
  media: HashedFile;
  observed_state: FlowState;
  trim: FrameInterval;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "TrackPlacement".
 */
export interface TrackPlacement {
  asset: AssetRef;
  fade_in_samples?: FadeInSamples;
  fade_out_samples?: FadeOutSamples;
  gain_db?: GainDb;
  id: Id10;
  loop_crossfade_samples?: LoopCrossfadeSamples;
  loop_duration_samples?: LoopDurationSamples;
  release_id?: ReleaseId;
  role?: Role;
  sample_rate?: SampleRate2;
  start_sample: StartSample;
  trim_end_sample: TrimEndSample;
  trim_start_sample: TrimStartSample;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowNext".
 */
export interface FlowNext {
  accepted_frames: AcceptedFrames;
  action: Action;
  attempt_id: AttemptId1;
  beat: FlowBeat | null;
  candidate_id: CandidateId1;
  credit_units: CreditUnits;
  message: Message;
  parent_id: ParentId2;
  target_frames: TargetFrames1;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowReferenceSlot".
 */
export interface FlowReferenceSlot {
  framing: Framing1;
  instruction: Instruction;
  key: Key1;
  starting_state: FlowState | null;
  url: Url;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowReviewView".
 */
export interface FlowReviewView {
  checklist: Checklist;
  diagnostics: Diagnostics;
  images: Images;
  join_url: JoinUrl;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowImage".
 */
export interface FlowImage {
  frame: Frame;
  role: Role1;
  url: Url1;
}
/**
 * This interface was referenced by `WebFlow`'s JSON-Schema
 * via the `definition` "FlowShotView".
 */
export interface FlowShotView {
  accepted_frames: AcceptedFrames1;
  duration_frames: DurationFrames2;
  framing: Framing2;
  id: Id11;
  index: Index;
  reference_key: ReferenceKey1;
  start_frame: StartFrame1;
  state: State2;
  title: Title3;
}
