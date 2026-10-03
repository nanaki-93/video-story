/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

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
 * This interface was referenced by `Action`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `Action`'s JSON-Schema
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
