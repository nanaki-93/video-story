/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type AcceptedIds = string[];
export type District = string | null;
export type Id = string;
export type Kind = "rest" | "look" | "pickup" | "sip" | "return_cup" | "sway" | "deep_breath" | "district";
export type TargetFrame = number;
export type Diagnostic = string | null;
export type DocumentType = "flow_attempt";
export type EpisodeId = string;
export type Id1 = string;
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
export type Revision = number;
export type SchemaVersion = "1.0";
export type ShotId = string | null;
export type State = "prepared" | "awaiting_external" | "submitted" | "unknown" | "received" | "failed";
export type TemplateVersion = "1" | "2";
export type Attempts = FlowAttempt[];
export type AttemptId = string;
export type Height = number;
export type Width = number;
export type Den = number;
export type Num = number;
export type FrameCount = number;
export type Id2 = string;
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
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
export type DocumentType1 = "flow_episode";
export type Id3 = string;
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
export type Exterior1 = string | null;
export type Framing = "wide" | "medium" | "close";
export type Id4 = string;
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
export type Revision1 = number;
export type SchemaVersion1 = "1.0";
export type Title2 = string;

export interface FlowEpisode {
  accepted_ids?: AcceptedIds;
  attempts?: Attempts;
  candidates?: Candidates;
  document_type?: DocumentType1;
  id: Id3;
  limits: FlowLimits;
  paused?: Paused;
  recipe: FlowRecipe;
  references?: References;
  revision?: Revision1;
  schema_version: SchemaVersion1;
  title: Title2;
}
/**
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "FlowAttempt".
 */
export interface FlowAttempt {
  beat: FlowBeat;
  diagnostic?: Diagnostic;
  document_type?: DocumentType;
  episode_id: EpisodeId;
  id: Id1;
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
  revision?: Revision;
  schema_version: SchemaVersion;
  shot_id?: ShotId;
  state: State;
  template_version?: TemplateVersion;
}
/**
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "FlowBeat".
 */
export interface FlowBeat {
  district?: District;
  id: Id;
  kind: Kind;
  target_frame: TargetFrame;
}
/**
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "FlowCandidate".
 */
export interface FlowCandidate {
  attempt_id: AttemptId;
  canvas: Canvas;
  fps: FrameRate;
  frame_count: FrameCount;
  id: Id2;
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
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * User-confirmed facts, independent of the recipe's intended appearance.
 *
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
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
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "FrameInterval".
 */
export interface FrameInterval {
  end_frame: EndFrame;
  start_frame: StartFrame;
}
/**
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
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
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
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
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
 * via the `definition` "FlowShot".
 */
export interface FlowShot {
  beats: Beats1;
  duration_frames: DurationFrames;
  exterior?: Exterior1;
  framing: Framing;
  id: Id4;
  max_extensions?: MaxExtensions;
  reference_key: ReferenceKey;
  title: Title;
}
/**
 * This interface was referenced by `FlowEpisode`'s JSON-Schema
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
