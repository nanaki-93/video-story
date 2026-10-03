/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type ActionId = string;
export type Channel = "body" | "face";
export type ConflictBehavior = "error";
export type EndFrame = number;
export type Id = string;
export type Id1 = string;
export type Version = string;
export type Repeat = "once" | "loop_to_fill";
export type ReturnPose = string | null;
export type SceneId = string;
export type StartFrame = number;
export type Version1 = string;

export interface ActionRequest {
  action_id: ActionId;
  channel: Channel;
  conflict_behavior?: ConflictBehavior;
  end_frame: EndFrame;
  id: Id;
  pack: AssetRef;
  repeat: Repeat;
  return_pose?: ReturnPose;
  scene_id: SceneId;
  start_frame: StartFrame;
  version: Version1;
}
/**
 * This interface was referenced by `ActionRequest`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
