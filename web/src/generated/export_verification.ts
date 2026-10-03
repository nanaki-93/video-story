/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Channels = 2;
export type Codec = "aac";
export type DecodedSamples = number;
export type IntendedSamples = number;
export type PaddingSamples = number;
export type SampleRate = 48000;
export type DocumentType = "export_verification";
export type JobId = string;
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
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
export type SampleRate1 = 48000;
export type VideoBitrate = number | null;
export type VideoCodec = string;
export type SchemaVersion = "1.0";
export type SnapshotSha256 = string;
export type BitRate = number | null;
export type Codec1 = "h264";
export type ColorRange = "tv";
export type ColorSpace1 = "bt709";
export type ContainerDurationSeconds = number;
export type DurationSeconds = number;
export type FrameCount = number;
export type FullDecodePassed = true;
export type Level = number;
export type FastStart = true;
export type FirstMdatOffset = number;
export type MoovOffset = number;
export type PixelFormat1 = "yuv420p";
export type Profile = "High";
export type Progressive = true;
export type TimestampsVerified = true;

export interface ExportVerification {
  audio?: AudioVerification | null;
  document_type?: DocumentType;
  job_id: JobId;
  output: HashedFile;
  profile: OutputProfile;
  schema_version: SchemaVersion;
  snapshot_sha256: SnapshotSha256;
  video: VideoVerification;
}
/**
 * This interface was referenced by `ExportVerification`'s JSON-Schema
 * via the `definition` "AudioVerification".
 */
export interface AudioVerification {
  channels?: Channels;
  codec?: Codec;
  decoded_samples: DecodedSamples;
  intended_samples: IntendedSamples;
  padding_samples: PaddingSamples;
  sample_rate?: SampleRate;
}
/**
 * This interface was referenced by `ExportVerification`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `ExportVerification`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `ExportVerification`'s JSON-Schema
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
  sample_rate?: SampleRate1;
  video_bitrate?: VideoBitrate;
  video_codec: VideoCodec;
}
/**
 * This interface was referenced by `ExportVerification`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `ExportVerification`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `ExportVerification`'s JSON-Schema
 * via the `definition` "VideoVerification".
 */
export interface VideoVerification {
  bit_rate?: BitRate;
  canvas: Canvas;
  codec?: Codec1;
  color_range?: ColorRange;
  color_space?: ColorSpace1;
  container_duration_seconds: ContainerDurationSeconds;
  duration_seconds: DurationSeconds;
  fps: FrameRate;
  frame_count: FrameCount;
  full_decode_passed?: FullDecodePassed;
  level: Level;
  mp4: MP4Layout;
  pixel_format?: PixelFormat1;
  profile?: Profile;
  progressive?: Progressive;
  timestamps_verified?: TimestampsVerified;
}
/**
 * This interface was referenced by `ExportVerification`'s JSON-Schema
 * via the `definition` "MP4Layout".
 */
export interface MP4Layout {
  fast_start?: FastStart;
  first_mdat_offset: FirstMdatOffset;
  moov_offset: MoovOffset;
}
