/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Name = string;
export type Sha256 = string;
export type Version = string;
export type Channels = 2;
export type DocumentType = "audio_mix_report";
export type FirstSample = number;
export type GainDb = number;
export type IntegratedLufs = number | null;
export type LoudnessRangeLu = number | null;
export type Output = string | null;
export type OutputSha256 = string;
export type OverFullScaleSamples = number;
export type Id = string;
export type Version1 = string;
export type PreparedSamples = number;
export type Resampled = boolean;
export type SourceSampleRate = number;
export type SourceSamples = number;
export type SourceSha256 = string;
export type Preparations = AudioPreparation[];
export type Purpose = "preview" | "production" | "synthetic_test";
export type SampleCount = number;
export type SampleFormat = "float32";
export type SamplePeakDbfs = number | null;
export type SampleRate = 48000;
export type SchemaVersion = "1.0";
export type SnapshotSha256 = string;
export type SuggestedGainDb = number | null;
export type ToolchainFingerprint = string;
export type TruePeakDbtp = number | null;
export type VerifiedSamples = boolean;
export type Warnings = string[];

export interface AudioMixReport {
  backend: Fingerprint;
  channels?: Channels;
  document_type?: DocumentType;
  first_sample: FirstSample;
  gain_db: GainDb;
  integrated_lufs: IntegratedLufs;
  loudness_range_lu: LoudnessRangeLu;
  output?: Output;
  output_sha256: OutputSha256;
  over_full_scale_samples: OverFullScaleSamples;
  preparations: Preparations;
  purpose: Purpose;
  sample_count: SampleCount;
  sample_format?: SampleFormat;
  sample_peak_dbfs: SamplePeakDbfs;
  sample_rate?: SampleRate;
  schema_version: SchemaVersion;
  snapshot_sha256: SnapshotSha256;
  suggested_gain_db: SuggestedGainDb;
  toolchain_fingerprint: ToolchainFingerprint;
  true_peak_dbtp: TruePeakDbtp;
  verified_samples: VerifiedSamples;
  warnings: Warnings;
}
/**
 * This interface was referenced by `AudioMixReport`'s JSON-Schema
 * via the `definition` "Fingerprint".
 */
export interface Fingerprint {
  name: Name;
  sha256: Sha256;
  version: Version;
}
/**
 * This interface was referenced by `AudioMixReport`'s JSON-Schema
 * via the `definition` "AudioPreparation".
 */
export interface AudioPreparation {
  asset: AssetRef;
  prepared_samples: PreparedSamples;
  resampled: Resampled;
  source_sample_rate: SourceSampleRate;
  source_samples: SourceSamples;
  source_sha256: SourceSha256;
}
/**
 * This interface was referenced by `AudioMixReport`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version1;
}
