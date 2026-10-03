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
export type Assets = Asset[];
export type DocumentType1 = "web_catalog";
export type ActionId = string;
export type Channel = "body" | "face";
export type ConflictBehavior = "error";
export type EndFrame = number;
export type Id2 = string;
export type Repeat = "once" | "loop_to_fill";
export type ReturnPose = string | null;
export type SceneId = string;
export type StartFrame = number;
export type Version2 = string;
export type Actions = ActionRequest[];
export type Id3 = string;
export type Sha2561 = string | null;
export type Version3 = string;
export type AssetLocks = AssetLock[];
export type EndFrame1 = number;
export type Id4 = string;
export type MusicPlacements = string[];
export type Purpose = string;
export type SceneId1 = string;
export type StartFrame1 = number;
export type Summary = string;
export type Beats = StoryBeat[];
export type Notes2 = string[];
export type Objects = string[];
export type PreviousEpisodeId = string | null;
export type Summary1 = string | null;
export type Interpolation = "constant" | "linear";
/**
 * @minItems 1
 */
export type Keys = [CurveKey, ...CurveKey[]];
export type Frame = number;
export type Value = number;
export type Maximum = number;
export type Minimum = number;
export type Outside = "clamp" | "zero";
export type Scope = string;
export type Target = string;
export type Unit = "design_px_per_second" | "fraction" | "degrees" | "design_px" | "db";
export type Curves = Curve[];
export type DocumentType2 = "episode";
export type DurationFrames = number;
export type EndFrame2 = number;
export type Id5 = string;
export type Repeat1 = false;
export type SceneId2 = string;
export type SlotId = string | null;
export type StartFrame2 = number;
export type Type = "landmark";
export type WorldX = number;
export type Frame1 = number;
export type Id6 = string;
export type Location = string;
export type ObjectId = string;
export type SceneId3 = string;
export type Type1 = "prop";
export type Events = (LandmarkEvent | PropEvent)[];
export type Format = "story" | "session" | "track";
export type Id7 = string;
export type Notes3 = string | null;
export type ActionId1 = string;
export type Channel1 = "body" | "face";
export type DurationFrames1 = number;
export type EndFrame3 = number;
export type Id8 = string;
export type MaximumGapFrames = number;
export type MinimumGapFrames = number;
export type Repeat2 = "once" | "loop_to_fill";
export type SceneId4 = string;
export type StartFrame3 = number;
export type Version4 = string;
export type RandomActions = RandomActionTiming[];
export type Revision1 = number;
/**
 * @minItems 1
 */
export type Scenes = [SceneInstance, ...SceneInstance[]];
export type Anchor = string | null;
export type CharacterOutfitId = string | null;
export type Continuity1 = "preserve" | "deliberate_reset";
export type Curves1 = Curve[];
export type EndFrame4 = number;
export type Events1 = (LandmarkEvent | PropEvent)[];
export type BodyPose = string;
export type CabinLight = string | null;
export type FacialOverlay = string | null;
export type TravelDistancePx = number;
export type WeatherPhaseFrame = number;
export type Id9 = string;
export type Purpose1 = string | null;
export type StartFrame4 = number;
export type CharacterPolicy = "cut" | "single_visible" | "matched";
export type Kind1 = "cut" | "overlap";
export type Note1 = string | null;
export type OverlapFrames = number;
export type SchemaVersion1 = "1.0";
export type Seed1 = number;
export type Title = string;
export type FadeInSamples = number;
export type FadeOutSamples = number;
export type GainDb = number;
export type Id10 = string;
export type LoopCrossfadeSamples = number;
export type LoopDurationSamples = number | null;
export type ReleaseId = string | null;
export type Role = "music" | "ambience";
export type SampleRate1 = 48000;
export type StartSample = number;
export type TrimEndSample = number;
export type TrimStartSample = number;
export type Tracks = TrackPlacement[];
export type Episodes = Episode[];
/**
 * @minItems 1
 */
export type Actions1 = [Action, ...Action[]];
export type Channel2 = "body" | "face";
export type CompatibleBodyPoses = string[];
export type EndPose = string;
export type FrameCount1 = number;
export type Id11 = string;
export type Kind2 = "loop" | "one_shot";
export type EndFrame5 = number;
export type StartFrame5 = number;
export type OccupiesChannels = ("body" | "face")[];
export type StartPose = string;
export type Version5 = string;
export type AlphaMode1 = "straight" | "premultiplied";
export type CameraId = string;
export type DocumentType3 = "action_pack";
export type Id12 = string;
export type OutfitId = string | null;
export type Revision2 = number;
export type SchemaVersion2 = "1.0";
export type Version6 = string;
export type Packs = ActionPack[];
export type Artist = string;
export type ClaimNotes = string | null;
export type ContentSha2561 = string;
export type Note2 = string | null;
export type ReviewedAt1 = string;
export type Reviewer1 = string;
export type DisclosureNotes = string | null;
export type DisclosureReviewed = boolean;
export type DocumentType4 = "release_record";
export type Id13 = string;
export type PublishedAt = string | null;
export type ReleaseTitle = string;
export type Revision3 = number;
export type RightsStatus = "pending" | "confirmed" | "not-permitted";
export type SchemaVersion3 = "1.0";
export type Status1 =
  | "draft"
  | "technically_verified"
  | "creatively_reviewed"
  | "rights_reviewed"
  | "ready_for_manual_upload"
  | "uploaded"
  | "published";
/**
 * @minItems 1
 */
export type Tracks1 = [ReleaseTrack, ...ReleaseTrack[]];
export type AiUseNotes = string | null;
export type Channels2 = number;
export type CommercialUseStatus = "pending" | "confirmed" | "not-permitted";
export type Name = string;
export type Role1 = string;
export type Credits = Credit[];
export type DurationSamples1 = number;
export type ExplicitContent = boolean | null;
export type Isrc = string | null;
export type ReleaseUrl = string | null;
export type SampleRate2 = number;
export type Sha2562 = string | null;
export type Title1 = string;
export type Upc = string | null;
export type Releases = ReleaseRecord[];
export type SchemaVersion4 = "1.0";
export type CameraId1 = string;
export type Capabilities = string[];
export type Channels3 = ("body" | "face")[];
export type DocumentType5 = "scene_template";
export type Fit = "crop" | "letterbox";
export type Id14 = string;
export type MaskSemantics = "white_visible_black_hidden";
export type Revision4 = number;
export type SchemaVersion5 = "1.0";
/**
 * @minItems 1
 */
export type Slots = [LayerSlot, ...LayerSlot[]];
export type Anchor1 = string | null;
export type DepthFactor = number;
export type Color = [number, number, number] | null;
export type DefaultStrength = number;
export type Kind3 = "tint" | "rain" | "reflection";
export type StrengthTarget = string;
export type Id15 = string;
export type Kind4 = "still" | "tile_strip" | "scheduled_sprite" | "character" | "effect";
export type Opacity = number;
export type TilePeriod = number | null;
export type Z = number;
export type Version7 = string;
export type Templates1 = SceneTemplate[];

export interface WebCatalog {
  assets: Assets;
  document_type?: DocumentType1;
  episodes: Episodes;
  packs: Packs;
  releases: Releases;
  schema_version: SchemaVersion4;
  templates: Templates1;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
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
 * This interface was referenced by `WebCatalog`'s JSON-Schema
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
 * This interface was referenced by `WebCatalog`'s JSON-Schema
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
 * This interface was referenced by `Anchors`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Point".
 */
export interface Point {
  x: X;
  y: Y;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Crop".
 */
export interface Crop {
  height: Height;
  width: Width;
  x: X1;
  y: Y1;
}
/**
 * This interface was referenced by `SlotAssignments`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
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
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height1;
  width: Width1;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
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
 * This interface was referenced by `WebCatalog`'s JSON-Schema
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
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Episode".
 */
export interface Episode {
  actions?: Actions;
  asset_locks?: AssetLocks;
  beats?: Beats;
  canvas: Canvas;
  continuity?: Continuity;
  curves?: Curves;
  document_type: DocumentType2;
  duration_frames: DurationFrames;
  events?: Events;
  format: Format;
  fps: FrameRate;
  id: Id7;
  notes?: Notes3;
  random_actions?: RandomActions;
  revision?: Revision1;
  scenes: Scenes;
  schema_version: SchemaVersion1;
  seed: Seed1;
  title: Title;
  tracks?: Tracks;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "ActionRequest".
 */
export interface ActionRequest {
  action_id: ActionId;
  channel: Channel;
  conflict_behavior?: ConflictBehavior;
  end_frame: EndFrame;
  id: Id2;
  pack: AssetRef;
  repeat: Repeat;
  return_pose?: ReturnPose;
  scene_id: SceneId;
  start_frame: StartFrame;
  version: Version2;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "AssetLock".
 */
export interface AssetLock {
  id: Id3;
  sha256?: Sha2561;
  version: Version3;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "StoryBeat".
 */
export interface StoryBeat {
  end_frame: EndFrame1;
  id: Id4;
  music_placements?: MusicPlacements;
  purpose: Purpose;
  scene_id: SceneId1;
  start_frame: StartFrame1;
  summary: Summary;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Continuity".
 */
export interface Continuity {
  notes?: Notes2;
  object_notes?: ObjectNotes;
  objects?: Objects;
  previous_episode_id?: PreviousEpisodeId;
  summary?: Summary1;
}
export interface ObjectNotes {
  /**
   * This interface was referenced by `ObjectNotes`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Curve".
 */
export interface Curve {
  interpolation: Interpolation;
  keys: Keys;
  limits: ParameterLimit;
  outside?: Outside;
  scope: Scope;
  target: Target;
  unit: Unit;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "CurveKey".
 */
export interface CurveKey {
  frame: Frame;
  value: Value;
}
/**
 * This interface was referenced by `ParameterLimits`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "ParameterLimit".
 */
export interface ParameterLimit {
  maximum: Maximum;
  minimum: Minimum;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "LandmarkEvent".
 */
export interface LandmarkEvent {
  asset: AssetRef;
  end_frame: EndFrame2;
  id: Id5;
  repeat?: Repeat1;
  scene_id: SceneId2;
  slot_id?: SlotId;
  start_frame: StartFrame2;
  type: Type;
  world_x?: WorldX;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "PropEvent".
 */
export interface PropEvent {
  frame: Frame1;
  id: Id6;
  location: Location;
  object_id: ObjectId;
  scene_id: SceneId3;
  type: Type1;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "RandomActionTiming".
 */
export interface RandomActionTiming {
  action_id: ActionId1;
  channel: Channel1;
  duration_frames: DurationFrames1;
  end_frame: EndFrame3;
  id: Id8;
  maximum_gap_frames: MaximumGapFrames;
  minimum_gap_frames: MinimumGapFrames;
  pack: AssetRef;
  repeat?: Repeat2;
  scene_id: SceneId4;
  start_frame: StartFrame3;
  version: Version4;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "SceneInstance".
 */
export interface SceneInstance {
  anchor?: Anchor;
  character_outfit_id?: CharacterOutfitId;
  continuity?: Continuity1;
  curves?: Curves1;
  end_frame: EndFrame4;
  events?: Events1;
  final_state?: SceneState | null;
  id: Id9;
  initial_state: SceneState;
  purpose?: Purpose1;
  slot_assignments?: SlotAssignments;
  start_frame: StartFrame4;
  template: AssetRef;
  transition_in?: Transition;
  transition_out?: Transition;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "SceneState".
 */
export interface SceneState {
  body_pose: BodyPose;
  cabin_light?: CabinLight;
  facial_overlay?: FacialOverlay;
  props?: Props;
  travel_distance_px?: TravelDistancePx;
  weather_phase_frame?: WeatherPhaseFrame;
}
export interface Props {
  /**
   * This interface was referenced by `Props`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
export interface SlotAssignments {
  [k: string]: AssetRef;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Transition".
 */
export interface Transition {
  character_policy?: CharacterPolicy;
  kind?: Kind1;
  match_action?: AssetRef | null;
  note?: Note1;
  overlap_frames?: OverlapFrames;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
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
  sample_rate?: SampleRate1;
  start_sample: StartSample;
  trim_end_sample: TrimEndSample;
  trim_start_sample: TrimStartSample;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "ActionPack".
 */
export interface ActionPack {
  actions: Actions1;
  alpha_mode: AlphaMode1;
  anchor: Point;
  approval?: Approval;
  camera_id: CameraId;
  canvas: Canvas;
  document_type: DocumentType3;
  fps: FrameRate;
  id: Id12;
  outfit_id?: OutfitId;
  revision?: Revision2;
  schema_version: SchemaVersion2;
  template: AssetRef;
  version: Version6;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Action".
 */
export interface Action {
  channel: Channel2;
  clip: AssetRef;
  compatible_body_poses?: CompatibleBodyPoses;
  end_pose: EndPose;
  frame_count: FrameCount1;
  id: Id11;
  kind: Kind2;
  loop?: FrameInterval | null;
  occupies_channels?: OccupiesChannels;
  requires_props?: RequiresProps;
  resulting_props?: ResultingProps;
  start_pose: StartPose;
  version: Version5;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "FrameInterval".
 */
export interface FrameInterval {
  end_frame: EndFrame5;
  start_frame: StartFrame5;
}
export interface RequiresProps {
  /**
   * This interface was referenced by `RequiresProps`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
export interface ResultingProps {
  /**
   * This interface was referenced by `ResultingProps`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "ReleaseRecord".
 */
export interface ReleaseRecord {
  artist: Artist;
  claim_notes?: ClaimNotes;
  creative_review?: ReviewRecord | null;
  disclosure_notes?: DisclosureNotes;
  disclosure_reviewed?: DisclosureReviewed;
  document_type: DocumentType4;
  id: Id13;
  published_at?: PublishedAt;
  release_links?: ReleaseLinks;
  release_title: ReleaseTitle;
  revision?: Revision3;
  rights_status?: RightsStatus;
  schema_version: SchemaVersion3;
  status?: Status1;
  technical_report?: MediaPath | null;
  tracks: Tracks1;
  upc?: Upc;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "ReviewRecord".
 */
export interface ReviewRecord {
  content_sha256: ContentSha2561;
  note?: Note2;
  reviewed_at: ReviewedAt1;
  reviewer: Reviewer1;
}
export interface ReleaseLinks {
  /**
   * This interface was referenced by `ReleaseLinks`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "ReleaseTrack".
 */
export interface ReleaseTrack {
  ai_use_notes?: AiUseNotes;
  asset: AssetRef;
  channels: Channels2;
  commercial_use_status?: CommercialUseStatus;
  credits?: Credits;
  duration_samples: DurationSamples1;
  explicit_content?: ExplicitContent;
  isrc?: Isrc;
  master: MediaPath;
  release_url?: ReleaseUrl;
  sample_rate: SampleRate2;
  sha256?: Sha2562;
  source_project?: MediaPath | null;
  title: Title1;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "Credit".
 */
export interface Credit {
  name: Name;
  role: Role1;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "SceneTemplate".
 */
export interface SceneTemplate {
  anchors: Anchors;
  approval?: Approval;
  camera_id: CameraId1;
  capabilities: Capabilities;
  channels: Channels3;
  design_canvas: Canvas;
  document_type: DocumentType5;
  fit?: Fit;
  id: Id14;
  mask_semantics: MaskSemantics;
  parameter_limits?: ParameterLimits;
  revision?: Revision4;
  schema_version: SchemaVersion5;
  slots: Slots;
  version: Version7;
}
export interface Anchors {
  [k: string]: Point;
}
export interface ParameterLimits {
  [k: string]: ParameterLimit;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "LayerSlot".
 */
export interface LayerSlot {
  anchor?: Anchor1;
  asset?: AssetRef | null;
  depth_factor?: DepthFactor;
  effect?: EffectSpec | null;
  id: Id15;
  kind: Kind4;
  mask?: AssetRef | null;
  opacity?: Opacity;
  tile_period?: TilePeriod;
  z: Z;
}
/**
 * This interface was referenced by `WebCatalog`'s JSON-Schema
 * via the `definition` "EffectSpec".
 */
export interface EffectSpec {
  color?: Color;
  default_strength?: DefaultStrength;
  kind: Kind3;
  loop?: FrameInterval | null;
  strength_target: StrengthTarget;
}
