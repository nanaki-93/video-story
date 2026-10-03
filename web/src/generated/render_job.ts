/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Name = string;
export type Sha256 = string;
export type Version = string;
export type CancelRequested = boolean;
export type FirstFrame = number;
export type FrameCount = number;
export type Index = number;
export type Path = string;
export type RootId = string;
export type Sha2561 = string;
export type SizeBytes = number;
export type ReportPath = string | null;
export type State = "pending" | "rendering" | "verified" | "failed";
export type Chunks = ChunkRecord[];
export type CompletedFrames = number;
export type Destination = string | null;
export type DocumentType = "render_job";
export type DurationFrames = number;
export type Code = string;
export type LogPath = string | null;
export type Message = string;
export type FirstFrame1 = number;
export type Id = string;
export type Owner = string | null;
export type PauseRequested = boolean;
export type MaxChunkFrames = number;
export type ProfileSha256 = string;
export type TemporalHandles = 0;
export type ToolchainFingerprint = string | null;
export type Version1 = "1";
export type AudioBitrate = number;
export type AudioCodec = string | null;
export type AudioGainDb = number;
export type Height = number;
export type Width = number;
export type ColorSpace = "bt709";
export type Container = "mp4" | "mkv";
export type Den = number;
export type Num = number;
export type Id1 = string;
export type PixelFormat = string;
export type SampleRate = 48000;
export type VideoBitrate = number | null;
export type VideoCodec = string;
export type ReportPath1 = string | null;
export type Revision = number;
export type SchemaVersion = "1.0";
export type SnapshotSha256 = string;
export type State1 = "queued" | "running" | "paused" | "interrupted" | "cancelled" | "failed" | "verified";

export interface RenderJob {
  backend: Fingerprint;
  cancel_requested?: CancelRequested;
  chunks: Chunks;
  completed_frames?: CompletedFrames;
  destination?: Destination;
  document_type: DocumentType;
  duration_frames: DurationFrames;
  error?: JobError | null;
  first_frame?: FirstFrame1;
  id: Id;
  output?: HashedFile | null;
  owner?: Owner;
  pause_requested?: PauseRequested;
  plan?: ChunkPlan | null;
  profile: OutputProfile;
  report_path?: ReportPath1;
  revision?: Revision;
  schema_version: SchemaVersion;
  snapshot_sha256: SnapshotSha256;
  state: State1;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
 * via the `definition` "Fingerprint".
 */
export interface Fingerprint {
  name: Name;
  sha256: Sha256;
  version: Version;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
 * via the `definition` "ChunkRecord".
 */
export interface ChunkRecord {
  first_frame: FirstFrame;
  frame_count: FrameCount;
  index: Index;
  output?: HashedFile | null;
  report_path?: ReportPath;
  state: State;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha2561;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
 * via the `definition` "JobError".
 */
export interface JobError {
  code: Code;
  log_path?: LogPath;
  message: Message;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
 * via the `definition` "ChunkPlan".
 */
export interface ChunkPlan {
  max_chunk_frames: MaxChunkFrames;
  pipeline: Fingerprint;
  profile_sha256: ProfileSha256;
  temporal_handles?: TemporalHandles;
  toolchain_fingerprint?: ToolchainFingerprint;
  version?: Version1;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
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
  id: Id1;
  pixel_format: PixelFormat;
  sample_rate?: SampleRate;
  video_bitrate?: VideoBitrate;
  video_codec: VideoCodec;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `RenderJob`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
