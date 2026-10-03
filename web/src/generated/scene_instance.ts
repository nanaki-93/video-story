/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Anchor = string | null;
export type Continuity = "preserve" | "deliberate_reset";
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
export type EndFrame = number;
export type Id = string;
export type Version = string;
export type EndFrame1 = number;
export type Id1 = string;
export type Repeat = false;
export type SceneId = string;
export type SlotId = string | null;
export type StartFrame = number;
export type Type = "landmark";
export type WorldX = number;
export type Frame1 = number;
export type Id2 = string;
export type Location = string;
export type ObjectId = string;
export type SceneId1 = string;
export type Type1 = "prop";
export type Events = (LandmarkEvent | PropEvent)[];
export type BodyPose = string;
export type CabinLight = string | null;
export type FacialOverlay = string | null;
export type TravelDistancePx = number;
export type WeatherPhaseFrame = number;
export type Id3 = string;
export type Purpose = string | null;
export type StartFrame1 = number;
export type CharacterPolicy = "cut" | "single_visible" | "matched";
export type Kind = "cut" | "overlap";
export type Note = string | null;
export type OverlapFrames = number;

export interface SceneInstance {
  anchor?: Anchor;
  continuity?: Continuity;
  curves?: Curves;
  end_frame: EndFrame;
  events?: Events;
  final_state?: SceneState | null;
  id: Id3;
  initial_state: SceneState;
  purpose?: Purpose;
  slot_assignments?: SlotAssignments;
  start_frame: StartFrame1;
  template: AssetRef;
  transition_in?: Transition;
  transition_out?: Transition;
}
/**
 * This interface was referenced by `SceneInstance`'s JSON-Schema
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
 * This interface was referenced by `SceneInstance`'s JSON-Schema
 * via the `definition` "CurveKey".
 */
export interface CurveKey {
  frame: Frame;
  value: Value;
}
/**
 * This interface was referenced by `SceneInstance`'s JSON-Schema
 * via the `definition` "ParameterLimit".
 */
export interface ParameterLimit {
  maximum: Maximum;
  minimum: Minimum;
}
/**
 * This interface was referenced by `SceneInstance`'s JSON-Schema
 * via the `definition` "LandmarkEvent".
 */
export interface LandmarkEvent {
  asset: AssetRef;
  end_frame: EndFrame1;
  id: Id1;
  repeat?: Repeat;
  scene_id: SceneId;
  slot_id?: SlotId;
  start_frame: StartFrame;
  type: Type;
  world_x?: WorldX;
}
/**
 * This interface was referenced by `SlotAssignments`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `SceneInstance`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `SceneInstance`'s JSON-Schema
 * via the `definition` "PropEvent".
 */
export interface PropEvent {
  frame: Frame1;
  id: Id2;
  location: Location;
  object_id: ObjectId;
  scene_id: SceneId1;
  type: Type1;
}
/**
 * This interface was referenced by `SceneInstance`'s JSON-Schema
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
 * This interface was referenced by `SceneInstance`'s JSON-Schema
 * via the `definition` "Transition".
 */
export interface Transition {
  character_policy?: CharacterPolicy;
  kind?: Kind;
  match_action?: AssetRef | null;
  note?: Note;
  overlap_frames?: OverlapFrames;
}
