/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "render_spike_report";
export type Encoder = "libx264" | "h264_videotoolbox";
export type FfmpegVersion = string;
export type FixtureVersion = "t02-v1";
export type GraphSha256 = string;
export type HardwareRequired = boolean;
export type Architecture = string;
export type Cpu = string;
export type IsTargetM5Pro = boolean;
export type MemoryBytes = number | null;
export type Os = string;
export type OsVersion = string;
export type PythonExecutable = string;
export type PythonVersion = string;
export type ObservedAt = string;
export type Output = string;
export type OutputBytes = number;
export type OutputSha256 = string;
export type ProductionApproved = boolean;
export type RenderFps = number;
export type RenderSeconds = number;
export type SchemaVersion = "1.0";
export type Synthetic = boolean;
export type ToolchainFingerprint = string;
export type AudioRms = number[];
export type ContinuousTimestamps = boolean;
export type DecodedAudioSamples = number;
export type DecodedFrames = number;
export type FullDecodePassed = boolean;
export type MaxBoundaryErrorPixels = number;
export type MaxRgbError = number;
export type MotionBoundaryChecks = number;
export type PixelChecks = number;
export type RgbTolerance = number;
export type SampledFrames = number[];
export type ToneEnergyRatio = number[];

export interface RenderSpikeReport {
  document_type?: DocumentType;
  encoder: Encoder;
  ffmpeg_version: FfmpegVersion;
  fixture_version?: FixtureVersion;
  graph_sha256: GraphSha256;
  hardware_required: HardwareRequired;
  input_hashes: InputHashes;
  machine: MachineInfo;
  observed_at: ObservedAt;
  output: Output;
  output_bytes: OutputBytes;
  output_sha256: OutputSha256;
  production_approved?: ProductionApproved;
  render_fps: RenderFps;
  render_seconds: RenderSeconds;
  schema_version: SchemaVersion;
  synthetic?: Synthetic;
  toolchain_fingerprint: ToolchainFingerprint;
  verification: SpikeVerification;
}
export interface InputHashes {
  [k: string]: string;
}
/**
 * This interface was referenced by `RenderSpikeReport`'s JSON-Schema
 * via the `definition` "MachineInfo".
 */
export interface MachineInfo {
  architecture: Architecture;
  cpu: Cpu;
  is_target_m5_pro: IsTargetM5Pro;
  memory_bytes?: MemoryBytes;
  os: Os;
  os_version: OsVersion;
  python_executable: PythonExecutable;
  python_version: PythonVersion;
}
/**
 * This interface was referenced by `RenderSpikeReport`'s JSON-Schema
 * via the `definition` "SpikeVerification".
 */
export interface SpikeVerification {
  audio_rms: AudioRms;
  continuous_timestamps: ContinuousTimestamps;
  decoded_audio_samples: DecodedAudioSamples;
  decoded_frames: DecodedFrames;
  full_decode_passed: FullDecodePassed;
  max_boundary_error_pixels: MaxBoundaryErrorPixels;
  max_rgb_error: MaxRgbError;
  motion_boundary_checks: MotionBoundaryChecks;
  pixel_checks: PixelChecks;
  rgb_tolerance: RgbTolerance;
  sampled_frames: SampledFrames;
  tone_energy_ratio: ToneEnergyRatio;
}
