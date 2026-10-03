/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "audio_timeline_report";
export type DurationSamples = number;
export type Code = string;
export type Location = (string | number)[];
export type Message = string;
export type Severity = "error" | "warning" | "info";
export type SuggestedFix = string;
export type Issues = ValidationIssue[];
export type EndSample = number;
export type StartSample = number;
export type MusicGaps = SampleRange[];
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
export type StartSample1 = number;
export type TrimEndSample = number;
export type TrimStartSample = number;
export type Placements = TrackPlacement[];
export type SampleRate1 = 48000;
export type SchemaVersion = "1.0";

export interface AudioTimelineReport {
  document_type?: DocumentType;
  duration_samples: DurationSamples;
  issues: Issues;
  music_gaps: MusicGaps;
  placements: Placements;
  sample_rate?: SampleRate1;
  schema_version: SchemaVersion;
}
/**
 * This interface was referenced by `AudioTimelineReport`'s JSON-Schema
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
 * This interface was referenced by `AudioTimelineReport`'s JSON-Schema
 * via the `definition` "SampleRange".
 */
export interface SampleRange {
  end_sample: EndSample;
  start_sample: StartSample;
}
/**
 * This interface was referenced by `AudioTimelineReport`'s JSON-Schema
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
  start_sample: StartSample1;
  trim_end_sample: TrimEndSample;
  trim_start_sample: TrimStartSample;
}
/**
 * This interface was referenced by `AudioTimelineReport`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
