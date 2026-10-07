/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "web_lofi";
export type ContentSha256 = string | null;
export type Note = string | null;
export type ReviewedAt = string | null;
export type Reviewer = string | null;
export type Status = "draft" | "review" | "approved" | "rejected";
export type DocumentType1 = "lofi_scene";
export type Den = number;
export type Num = number;
export type Id = string;
export type Id1 = string;
export type Version = string;
export type Notes = string;
/**
 * @maxItems 8
 */
export type Overlays =
  | []
  | [OverlayLayer]
  | [OverlayLayer, OverlayLayer]
  | [OverlayLayer, OverlayLayer, OverlayLayer]
  | [OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer]
  | [OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer]
  | [OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer]
  | [OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer]
  | [OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer, OverlayLayer];
export type Id2 = string;
export type Opacity = number;
export type FirstFrame = number;
export type RepeatFrames = number;
export type EndFrame = number;
export type StartFrame = number;
export type Revision = number;
/**
 * @maxItems 3
 */
export type Scenery = [] | [SceneryLayer] | [SceneryLayer, SceneryLayer] | [SceneryLayer, SceneryLayer, SceneryLayer];
export type Depth = number;
export type Id3 = string;
export type RepeatWidth = number;
export type SchemaVersion = "1.0";
export type Speed = number;
export type Title = string;
export type Version1 = string;
export type Scenes = LofiScene[];
export type SchemaVersion1 = "1.0";

export interface WebLofi {
  document_type?: DocumentType;
  scenes: Scenes;
  schema_version: SchemaVersion1;
}
/**
 * This interface was referenced by `WebLofi`'s JSON-Schema
 * via the `definition` "LofiScene".
 */
export interface LofiScene {
  approval?: Approval;
  document_type?: DocumentType1;
  fps?: FrameRate;
  id: Id;
  master: AssetRef;
  notes?: Notes;
  overlays?: Overlays;
  revision?: Revision;
  scenery?: Scenery;
  schema_version: SchemaVersion;
  speed?: Speed;
  title: Title;
  version?: Version1;
  window_mask?: AssetRef | null;
}
/**
 * This interface was referenced by `WebLofi`'s JSON-Schema
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
 * This interface was referenced by `WebLofi`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `WebLofi`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
/**
 * This interface was referenced by `WebLofi`'s JSON-Schema
 * via the `definition` "OverlayLayer".
 */
export interface OverlayLayer {
  asset: AssetRef;
  id: Id2;
  mask?: AssetRef | null;
  opacity?: Opacity;
  timing: LoopTiming;
}
/**
 * This interface was referenced by `WebLofi`'s JSON-Schema
 * via the `definition` "LoopTiming".
 */
export interface LoopTiming {
  first_frame?: FirstFrame;
  repeat_frames: RepeatFrames;
  source: FrameInterval;
}
/**
 * This interface was referenced by `WebLofi`'s JSON-Schema
 * via the `definition` "FrameInterval".
 */
export interface FrameInterval {
  end_frame: EndFrame;
  start_frame: StartFrame;
}
/**
 * This interface was referenced by `WebLofi`'s JSON-Schema
 * via the `definition` "SceneryLayer".
 */
export interface SceneryLayer {
  asset: AssetRef;
  depth?: Depth;
  id: Id3;
  repeat_width: RepeatWidth;
}
