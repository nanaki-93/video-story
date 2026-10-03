/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

/**
 * @minItems 1
 */
export type ChunkSha256 = [string, ...string[]];
export type FallbackReason = string | null;
export type Mode = "stream_copy" | "reencode";
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
export type Channels1 = 2;
export type Codec = "aac";
export type DecodedSamples = number;
export type IntendedSamples = number;
export type PaddingSamples = number;
export type SampleRate1 = 48000;
export type Key = string;
export type OriginSnapshotSha256 = string;
export type Height = number;
export type Width = number;
export type DocumentType1 = "render_report";
export type FirstFrame = number;
export type Den = number;
export type Num = number;
export type FrameCount = number;
export type FullDecodePassed = boolean;
export type GraphSha256 = string;
export type NormalizedCacheHits = number;
export type NormalizedImages = number;
export type Output1 = string;
export type OutputBytes = number;
export type OutputSha2561 = string;
export type Purpose1 = "preview" | "production" | "synthetic_test";
export type RenderSeconds = number;
export type SchemaVersion1 = "1.0";
export type SnapshotSha2561 = string;
export type TimestampsVerified = boolean;
export type ToolchainFingerprint1 = string;
export type BitRate = number | null;
export type Codec1 = "h264";
export type ColorRange = "tv";
export type ColorSpace = "bt709";
export type ContainerDurationSeconds = number;
export type DurationSeconds = number;
export type FrameCount1 = number;
export type FullDecodePassed1 = true;
export type Level = number;
export type FastStart = true;
export type FirstMdatOffset = number;
export type MoovOffset = number;
export type PixelFormat = "yuv420p";
export type Profile = "High";
export type Progressive = true;
export type TimestampsVerified1 = true;
export type Warnings1 = string[];

export interface RenderReport {
  assembly?: AssemblyInfo | null;
  audio_mix?: AudioMixReport | null;
  audio_verification?: AudioVerification | null;
  backend: Fingerprint;
  cache_reuse?: CacheReuse | null;
  canvas: Canvas;
  document_type?: DocumentType1;
  first_frame: FirstFrame;
  fps: FrameRate;
  frame_count: FrameCount;
  full_decode_passed: FullDecodePassed;
  graph_sha256: GraphSha256;
  normalized_cache_hits?: NormalizedCacheHits;
  normalized_images: NormalizedImages;
  output: Output1;
  output_bytes: OutputBytes;
  output_sha256: OutputSha2561;
  purpose: Purpose1;
  render_seconds: RenderSeconds;
  schema_version: SchemaVersion1;
  snapshot_sha256: SnapshotSha2561;
  timestamps_verified: TimestampsVerified;
  toolchain_fingerprint: ToolchainFingerprint1;
  video_verification?: VideoVerification | null;
  warnings?: Warnings1;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "AssemblyInfo".
 */
export interface AssemblyInfo {
  chunk_sha256: ChunkSha256;
  fallback_reason?: FallbackReason;
  mode: Mode;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "AudioMixReport".
 */
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
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "Fingerprint".
 */
export interface Fingerprint {
  name: Name;
  sha256: Sha256;
  version: Version;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
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
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version1;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "AudioVerification".
 */
export interface AudioVerification {
  channels?: Channels1;
  codec?: Codec;
  decoded_samples: DecodedSamples;
  intended_samples: IntendedSamples;
  padding_samples: PaddingSamples;
  sample_rate?: SampleRate1;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "CacheReuse".
 */
export interface CacheReuse {
  key: Key;
  origin_snapshot_sha256: OriginSnapshotSha256;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "VideoVerification".
 */
export interface VideoVerification {
  bit_rate?: BitRate;
  canvas: Canvas;
  codec?: Codec1;
  color_range?: ColorRange;
  color_space?: ColorSpace;
  container_duration_seconds: ContainerDurationSeconds;
  duration_seconds: DurationSeconds;
  fps: FrameRate;
  frame_count: FrameCount1;
  full_decode_passed?: FullDecodePassed1;
  level: Level;
  mp4: MP4Layout;
  pixel_format?: PixelFormat;
  profile?: Profile;
  progressive?: Progressive;
  timestamps_verified?: TimestampsVerified1;
}
/**
 * This interface was referenced by `RenderReport`'s JSON-Schema
 * via the `definition` "MP4Layout".
 */
export interface MP4Layout {
  fast_start?: FastStart;
  first_mdat_offset: FirstMdatOffset;
  moov_offset: MoovOffset;
}
