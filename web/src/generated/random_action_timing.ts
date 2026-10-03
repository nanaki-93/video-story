/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type ActionId = string;
export type Channel = "body" | "face";
export type DurationFrames = number;
export type EndFrame = number;
export type Id = string;
export type MaximumGapFrames = number;
export type MinimumGapFrames = number;
export type Id1 = string;
export type Version = string;
export type Repeat = "once" | "loop_to_fill";
export type SceneId = string;
export type StartFrame = number;
export type Version1 = string;

export interface RandomActionTiming {
  action_id: ActionId;
  channel: Channel;
  duration_frames: DurationFrames;
  end_frame: EndFrame;
  id: Id;
  maximum_gap_frames: MaximumGapFrames;
  minimum_gap_frames: MinimumGapFrames;
  pack: AssetRef;
  repeat?: Repeat;
  scene_id: SceneId;
  start_frame: StartFrame;
  version: Version1;
}
/**
 * This interface was referenced by `RandomActionTiming`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
