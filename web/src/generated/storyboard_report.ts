/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type EndFrame = number;
export type Id = string;
export type MusicPlacements = string[];
export type Purpose = string;
export type SceneId = string;
export type StartFrame = number;
export type Summary = string;
export type Beats = StoryBeat[];
export type Notes = string[];
export type Objects = string[];
export type PreviousEpisodeId = string | null;
export type Summary1 = string | null;
export type DocumentType = "storyboard_report";
export type Code = string;
export type Location = (string | number)[];
export type Message = string;
export type Severity = "error" | "warning" | "info";
export type SuggestedFix = string;
export type Issues = ValidationIssue[];
export type Kind = "start" | "end";
export type PlacementId = string;
export type Purposes = string[];
export type Sample = number;
export type MusicBoundaries = MusicBoundary[];
export type Anchor = string | null;
export type Continuity1 = "preserve" | "deliberate_reset";
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
export type EndFrame1 = number;
export type Id1 = string;
export type Version = string;
export type EndFrame2 = number;
export type Id2 = string;
export type Repeat = false;
export type SceneId1 = string;
export type SlotId = string | null;
export type StartFrame1 = number;
export type Type = "landmark";
export type WorldX = number;
export type Frame1 = number;
export type Id3 = string;
export type Location1 = string;
export type ObjectId = string;
export type SceneId2 = string;
export type Type1 = "prop";
export type Events = (LandmarkEvent | PropEvent)[];
export type BodyPose = string;
export type CabinLight = string | null;
export type FacialOverlay = string | null;
export type TravelDistancePx = number;
export type WeatherPhaseFrame = number;
export type Id4 = string;
export type Purpose1 = string | null;
export type StartFrame2 = number;
export type CharacterPolicy = "cut" | "single_visible" | "matched";
export type Kind1 = "cut" | "overlap";
export type Note = string | null;
export type OverlapFrames = number;
export type Scenes = SceneInstance[];
export type SchemaVersion = "1.0";
export type SnapshotSha256 = string;

export interface StoryboardReport {
  beats: Beats;
  continuity: Continuity;
  document_type?: DocumentType;
  issues: Issues;
  music_boundaries: MusicBoundaries;
  scenes: Scenes;
  schema_version: SchemaVersion;
  snapshot_sha256: SnapshotSha256;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "StoryBeat".
 */
export interface StoryBeat {
  end_frame: EndFrame;
  id: Id;
  music_placements?: MusicPlacements;
  purpose: Purpose;
  scene_id: SceneId;
  start_frame: StartFrame;
  summary: Summary;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
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
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "ValidationIssue".
 */
export interface ValidationIssue {
  code: Code;
  location: Location;
  message: Message;
  severity: Severity;
  suggested_fix: SuggestedFix;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "MusicBoundary".
 */
export interface MusicBoundary {
  kind: Kind;
  placement_id: PlacementId;
  purposes: Purposes;
  sample: Sample;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "SceneInstance".
 */
export interface SceneInstance {
  anchor?: Anchor;
  continuity?: Continuity1;
  curves?: Curves;
  end_frame: EndFrame1;
  events?: Events;
  final_state?: SceneState | null;
  id: Id4;
  initial_state: SceneState;
  purpose?: Purpose1;
  slot_assignments?: SlotAssignments;
  start_frame: StartFrame2;
  template: AssetRef;
  transition_in?: Transition;
  transition_out?: Transition;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
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
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "CurveKey".
 */
export interface CurveKey {
  frame: Frame;
  value: Value;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "ParameterLimit".
 */
export interface ParameterLimit {
  maximum: Maximum;
  minimum: Minimum;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "LandmarkEvent".
 */
export interface LandmarkEvent {
  asset: AssetRef;
  end_frame: EndFrame2;
  id: Id2;
  repeat?: Repeat;
  scene_id: SceneId1;
  slot_id?: SlotId;
  start_frame: StartFrame1;
  type: Type;
  world_x?: WorldX;
}
/**
 * This interface was referenced by `SlotAssignments`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "PropEvent".
 */
export interface PropEvent {
  frame: Frame1;
  id: Id3;
  location: Location1;
  object_id: ObjectId;
  scene_id: SceneId2;
  type: Type1;
}
/**
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
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
 * This interface was referenced by `StoryboardReport`'s JSON-Schema
 * via the `definition` "Transition".
 */
export interface Transition {
  character_policy?: CharacterPolicy;
  kind?: Kind1;
  match_action?: AssetRef | null;
  note?: Note;
  overlap_frames?: OverlapFrames;
}
