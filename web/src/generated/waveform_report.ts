/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Id = string;
export type Version = string;
export type AssetContentSha256 = string;
/**
 * @minItems 1
 * @maxItems 8192
 */
export type Bins = [WaveformBin, ...WaveformBin[]];
export type EndSample = number;
/**
 * @minItems 1
 * @maxItems 2
 */
export type Maximum = [number] | [number, number];
/**
 * @minItems 1
 * @maxItems 2
 */
export type Minimum = [number] | [number, number];
/**
 * @minItems 1
 * @maxItems 2
 */
export type Rms = [number] | [number, number];
export type StartSample = number;
export type Channels = 1 | 2;
export type DocumentType = "waveform_report";
export type DurationSamples = number;
export type LeadingSilenceSamples = number;
export type SampleRate = number;
export type SchemaVersion = "1.0";
export type Silent = boolean;
export type SourceSha256 = string;
export type Synthetic = boolean;
export type TrailingSilenceSamples = number;

export interface WaveformReport {
  asset: AssetRef;
  asset_content_sha256: AssetContentSha256;
  bins: Bins;
  channels: Channels;
  document_type?: DocumentType;
  duration_samples: DurationSamples;
  leading_silence_samples: LeadingSilenceSamples;
  sample_rate: SampleRate;
  schema_version: SchemaVersion;
  silent: Silent;
  source_sha256: SourceSha256;
  synthetic: Synthetic;
  trailing_silence_samples: TrailingSilenceSamples;
}
/**
 * This interface was referenced by `WaveformReport`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `WaveformReport`'s JSON-Schema
 * via the `definition` "WaveformBin".
 */
export interface WaveformBin {
  end_sample: EndSample;
  maximum: Maximum;
  minimum: Minimum;
  rms: Rms;
  start_sample: StartSample;
}
