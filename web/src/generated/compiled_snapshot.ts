/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type ContentSha256 = string | null;
export type Note = string | null;
export type ReviewedAt = string | null;
export type Reviewer = string | null;
export type Status = "draft" | "review" | "approved" | "rejected";
export type Id = string;
export type Version = string;
export type FadeInSamples = number;
export type FadeOutSamples = number;
export type GainDb = number;
export type Id1 = string;
export type LoopCrossfadeSamples = number;
export type LoopDurationSamples = number | null;
export type ReleaseId = string | null;
export type Role = "music" | "ambience";
export type SampleRate = 48000;
export type StartSample = number;
export type TrimEndSample = number;
export type TrimStartSample = number;
export type AudioPlacements = TrackPlacement[];
export type Name = string;
export type Sha256 = string;
export type Version1 = string;
export type DocumentType = "compiled_snapshot";
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
export type Height = number;
export type Width = number;
export type Notes = string[];
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
export type DocumentType1 = "episode";
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
export type Den = number;
export type Num = number;
export type Id7 = string;
export type Notes1 = string | null;
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
export type Revision = number;
/**
 * @minItems 1
 */
export type Scenes = [SceneInstance, ...SceneInstance[]];
export type Anchor = string | null;
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
export type Kind = "cut" | "overlap";
export type Note1 = string | null;
export type OverlapFrames = number;
export type SchemaVersion = "1.0";
export type Seed = number;
export type Title = string;
export type Tracks = TrackPlacement[];
export type Id10 = string;
export type Id11 = string;
export type Sha2562 = string;
export type Version5 = string;
export type LockedAssets = ResolvedAssetLock[];
export type Purpose2 = "preview" | "production" | "synthetic_test";
export type Revision1 = number;
export type ActionId2 = string;
export type Channel2 = "body" | "face";
export type EndFrame5 = number;
export type EndPose = string;
export type Id12 = string;
export type EndFrame6 = number;
export type StartFrame5 = number;
export type PhaseOriginFrame = number;
export type SceneId5 = string;
export type SourceStartFrame = number;
export type StartFrame6 = number;
export type StartPose = string;
export type Type2 = "action";
export type Schedule = (ScheduledAction | LandmarkEvent | PropEvent)[];
export type SchemaVersion1 = "1.0";

export interface CompiledSnapshot {
  approval?: Approval;
  audio_placements: AudioPlacements;
  compiler: Fingerprint;
  document_type: DocumentType;
  episode: Episode;
  id: Id10;
  locked_assets: LockedAssets;
  prng: Fingerprint;
  purpose: Purpose2;
  revision?: Revision1;
  schedule: Schedule;
  schema_version: SchemaVersion1;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "TrackPlacement".
 */
export interface TrackPlacement {
  asset: AssetRef;
  fade_in_samples?: FadeInSamples;
  fade_out_samples?: FadeOutSamples;
  gain_db?: GainDb;
  id: Id1;
  loop_crossfade_samples?: LoopCrossfadeSamples;
  loop_duration_samples?: LoopDurationSamples;
  release_id?: ReleaseId;
  role?: Role;
  sample_rate?: SampleRate;
  start_sample: StartSample;
  trim_end_sample: TrimEndSample;
  trim_start_sample: TrimStartSample;
}
/**
 * This interface was referenced by `SlotAssignments`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "Fingerprint".
 */
export interface Fingerprint {
  name: Name;
  sha256: Sha256;
  version: Version1;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "Episode".
 */
export interface Episode {
  actions?: Actions;
  asset_locks?: AssetLocks;
  beats?: Beats;
  canvas: Canvas;
  continuity?: Continuity;
  curves?: Curves;
  document_type: DocumentType1;
  duration_frames: DurationFrames;
  events?: Events;
  format: Format;
  fps: FrameRate;
  id: Id7;
  notes?: Notes1;
  random_actions?: RandomActions;
  revision?: Revision;
  scenes: Scenes;
  schema_version: SchemaVersion;
  seed: Seed;
  title: Title;
  tracks?: Tracks;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "AssetLock".
 */
export interface AssetLock {
  id: Id3;
  sha256?: Sha2561;
  version: Version3;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "Continuity".
 */
export interface Continuity {
  notes?: Notes;
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "CurveKey".
 */
export interface CurveKey {
  frame: Frame;
  value: Value;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "ParameterLimit".
 */
export interface ParameterLimit {
  maximum: Maximum;
  minimum: Minimum;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "SceneInstance".
 */
export interface SceneInstance {
  anchor?: Anchor;
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
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
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "Transition".
 */
export interface Transition {
  character_policy?: CharacterPolicy;
  kind?: Kind;
  match_action?: AssetRef | null;
  note?: Note1;
  overlap_frames?: OverlapFrames;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "ResolvedAssetLock".
 */
export interface ResolvedAssetLock {
  id: Id11;
  sha256: Sha2562;
  version: Version5;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "ScheduledAction".
 */
export interface ScheduledAction {
  action_id: ActionId2;
  channel: Channel2;
  clip: AssetRef;
  end_frame: EndFrame5;
  end_pose: EndPose;
  id: Id12;
  loop?: FrameInterval | null;
  pack: AssetRef;
  phase_origin_frame: PhaseOriginFrame;
  resulting_props?: ResultingProps;
  scene_id: SceneId5;
  source_start_frame: SourceStartFrame;
  start_frame: StartFrame6;
  start_pose: StartPose;
  type: Type2;
}
/**
 * This interface was referenced by `CompiledSnapshot`'s JSON-Schema
 * via the `definition` "FrameInterval".
 */
export interface FrameInterval {
  end_frame: EndFrame6;
  start_frame: StartFrame5;
}
export interface ResultingProps {
  /**
   * This interface was referenced by `ResultingProps`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
