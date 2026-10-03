/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Assumptions = string[];
export type AudioBytes = number;
export type AvailableBytes = number;
export type DocumentType = "storage_estimate";
export type FirstFrame = number;
export type FrameCount = number;
export type NormalizationBytes = number;
export type AudioBitrate = number;
export type AudioCodec = string | null;
export type AudioGainDb = number;
export type Height = number;
export type Width = number;
export type ColorSpace = "bt709";
export type Container = "mp4" | "mkv";
export type Den = number;
export type Num = number;
export type Id = string;
export type PixelFormat = string;
export type SampleRate = 48000;
export type VideoBitrate = number | null;
export type VideoCodec = string;
export type RequiredAdditionalBytes = number;
export type ReserveBytes = number;
export type SchemaVersion = "1.0";
export type SnapshotSha256 = string;
export type Sufficient = boolean;
export type VideoBytes = number;

export interface StorageEstimate {
  assumptions: Assumptions;
  audio_bytes: AudioBytes;
  available_bytes: AvailableBytes;
  document_type?: DocumentType;
  first_frame: FirstFrame;
  frame_count: FrameCount;
  normalization_bytes: NormalizationBytes;
  profile: OutputProfile;
  required_additional_bytes: RequiredAdditionalBytes;
  reserve_bytes: ReserveBytes;
  schema_version: SchemaVersion;
  snapshot_sha256: SnapshotSha256;
  sufficient: Sufficient;
  video_bytes: VideoBytes;
}
/**
 * This interface was referenced by `StorageEstimate`'s JSON-Schema
 * via the `definition` "OutputProfile".
 */
export interface OutputProfile {
  audio_bitrate?: AudioBitrate;
  audio_codec?: AudioCodec;
  audio_gain_db?: AudioGainDb;
  canvas: Canvas;
  color_space: ColorSpace;
  container: Container;
  fps: FrameRate;
  id: Id;
  pixel_format: PixelFormat;
  sample_rate?: SampleRate;
  video_bitrate?: VideoBitrate;
  video_codec: VideoCodec;
}
/**
 * This interface was referenced by `StorageEstimate`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `StorageEstimate`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
