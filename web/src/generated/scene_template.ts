/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type X = number;
export type Y = number;
export type ContentSha256 = string | null;
export type Note = string | null;
export type ReviewedAt = string | null;
export type Reviewer = string | null;
export type Status = "draft" | "review" | "approved" | "rejected";
export type CameraId = string;
export type Capabilities = string[];
export type Channels = ("body" | "face")[];
export type Height = number;
export type Width = number;
export type DocumentType = "scene_template";
export type Fit = "crop" | "letterbox";
export type Id = string;
export type MaskSemantics = "white_visible_black_hidden";
export type Maximum = number;
export type Minimum = number;
export type Revision = number;
export type SchemaVersion = "1.0";
/**
 * @minItems 1
 */
export type Slots = [LayerSlot, ...LayerSlot[]];
export type Anchor = string | null;
export type Id1 = string;
export type Version = string;
export type DepthFactor = number;
export type Color = [number, number, number] | null;
export type DefaultStrength = number;
export type Kind = "tint" | "rain" | "reflection";
export type EndFrame = number;
export type StartFrame = number;
export type StrengthTarget = string;
export type Id2 = string;
export type Kind1 = "still" | "tile_strip" | "scheduled_sprite" | "character" | "effect";
export type Opacity = number;
export type TilePeriod = number | null;
export type Z = number;
export type Version1 = string;

export interface SceneTemplate {
  anchors: Anchors;
  approval?: Approval;
  camera_id: CameraId;
  capabilities: Capabilities;
  channels: Channels;
  design_canvas: Canvas;
  document_type: DocumentType;
  fit?: Fit;
  id: Id;
  mask_semantics: MaskSemantics;
  parameter_limits?: ParameterLimits;
  revision?: Revision;
  schema_version: SchemaVersion;
  slots: Slots;
  version: Version1;
}
export interface Anchors {
  [k: string]: Point;
}
/**
 * This interface was referenced by `Anchors`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `SceneTemplate`'s JSON-Schema
 * via the `definition` "Point".
 */
export interface Point {
  x: X;
  y: Y;
}
/**
 * This interface was referenced by `SceneTemplate`'s JSON-Schema
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
 * This interface was referenced by `SceneTemplate`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
export interface ParameterLimits {
  [k: string]: ParameterLimit;
}
/**
 * This interface was referenced by `ParameterLimits`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `SceneTemplate`'s JSON-Schema
 * via the `definition` "ParameterLimit".
 */
export interface ParameterLimit {
  maximum: Maximum;
  minimum: Minimum;
}
/**
 * This interface was referenced by `SceneTemplate`'s JSON-Schema
 * via the `definition` "LayerSlot".
 */
export interface LayerSlot {
  anchor?: Anchor;
  asset?: AssetRef | null;
  depth_factor?: DepthFactor;
  effect?: EffectSpec | null;
  id: Id2;
  kind: Kind1;
  mask?: AssetRef | null;
  opacity?: Opacity;
  tile_period?: TilePeriod;
  z: Z;
}
/**
 * This interface was referenced by `SceneTemplate`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
/**
 * This interface was referenced by `SceneTemplate`'s JSON-Schema
 * via the `definition` "EffectSpec".
 */
export interface EffectSpec {
  color?: Color;
  default_strength?: DefaultStrength;
  kind: Kind;
  loop?: FrameInterval | null;
  strength_target: StrengthTarget;
}
/**
 * This interface was referenced by `SceneTemplate`'s JSON-Schema
 * via the `definition` "FrameInterval".
 */
export interface FrameInterval {
  end_frame: EndFrame;
  start_frame: StartFrame;
}
