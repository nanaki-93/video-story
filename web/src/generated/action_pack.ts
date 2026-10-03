/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

/**
 * @minItems 1
 */
export type Actions = [Action, ...Action[]];
export type Channel = "body" | "face";
export type Id = string;
export type Version = string;
export type CompatibleBodyPoses = string[];
export type EndPose = string;
export type FrameCount = number;
export type Id1 = string;
export type Kind = "loop" | "one_shot";
export type EndFrame = number;
export type StartFrame = number;
export type OccupiesChannels = ("body" | "face")[];
export type StartPose = string;
export type Version1 = string;
export type AlphaMode = "straight" | "premultiplied";
export type X = number;
export type Y = number;
export type ContentSha256 = string | null;
export type Note = string | null;
export type ReviewedAt = string | null;
export type Reviewer = string | null;
export type Status = "draft" | "review" | "approved" | "rejected";
export type CameraId = string;
export type Height = number;
export type Width = number;
export type DocumentType = "action_pack";
export type Den = number;
export type Num = number;
export type Id2 = string;
export type Revision = number;
export type SchemaVersion = "1.0";
export type Version2 = string;

export interface ActionPack {
  actions: Actions;
  alpha_mode: AlphaMode;
  anchor: Point;
  approval?: Approval;
  camera_id: CameraId;
  canvas: Canvas;
  document_type: DocumentType;
  fps: FrameRate;
  id: Id2;
  revision?: Revision;
  schema_version: SchemaVersion;
  template: AssetRef;
  version: Version2;
}
/**
 * This interface was referenced by `ActionPack`'s JSON-Schema
 * via the `definition` "Action".
 */
export interface Action {
  channel: Channel;
  clip: AssetRef;
  compatible_body_poses?: CompatibleBodyPoses;
  end_pose: EndPose;
  frame_count: FrameCount;
  id: Id1;
  kind: Kind;
  loop?: FrameInterval | null;
  occupies_channels?: OccupiesChannels;
  requires_props?: RequiresProps;
  resulting_props?: ResultingProps;
  start_pose: StartPose;
  version: Version1;
}
/**
 * This interface was referenced by `ActionPack`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `ActionPack`'s JSON-Schema
 * via the `definition` "FrameInterval".
 */
export interface FrameInterval {
  end_frame: EndFrame;
  start_frame: StartFrame;
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
 * This interface was referenced by `ActionPack`'s JSON-Schema
 * via the `definition` "Point".
 */
export interface Point {
  x: X;
  y: Y;
}
/**
 * This interface was referenced by `ActionPack`'s JSON-Schema
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
 * This interface was referenced by `ActionPack`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `ActionPack`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
