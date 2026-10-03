/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type CanApply = boolean;
export type DocumentType = "audio_edit_plan";
export type EffectiveEndSample = number;
export type EpisodeDurationSamples = number;
export type EpisodeId = string;
export type Issues = string[];
export type Revision = number;
export type SchemaVersion = "1.0";
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
export type Tracks = TrackPlacement[];

export interface AudioEditPlan {
  can_apply: CanApply;
  document_type?: DocumentType;
  effective_end_sample: EffectiveEndSample;
  episode_duration_samples: EpisodeDurationSamples;
  episode_id: EpisodeId;
  issues: Issues;
  revision: Revision;
  schema_version: SchemaVersion;
  tracks: Tracks;
}
/**
 * This interface was referenced by `AudioEditPlan`'s JSON-Schema
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
 * This interface was referenced by `AudioEditPlan`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
