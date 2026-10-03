/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "web_preview";
export type ActionId = string;
export type Channel = "body" | "face";
export type ConflictBehavior = "error";
export type EndFrame = number;
export type Id = string;
export type Id1 = string;
export type Version = string;
export type Repeat = "once" | "loop_to_fill";
export type ReturnPose = string | null;
export type SceneId = string;
export type StartFrame = number;
export type Version1 = string;
export type Actions = ActionRequest[];
export type Id2 = string;
export type Sha256 = string | null;
export type Version2 = string;
export type AssetLocks = AssetLock[];
export type EndFrame1 = number;
export type Id3 = string;
export type MusicPlacements = string[];
export type Purpose = string;
export type SceneId1 = string;
export type StartFrame1 = number;
export type Summary = string;
export type Beats = StoryBeat[];
export type Height = number;
export type Width = number;
export type Notes = string[];
export type Objects = string[];
export type PreviousEpisodeId = string | null;
export type Summary1 = string | null;
export type Interpolation = "constant" | "linear";
/**
 * @minItems 1
 */
export type Keys = [CurveKey, ...CurveKey[]];
export type Frame = number;
export type Value = number;
export type Maximum = number;
export type Minimum = number;
export type Outside = "clamp" | "zero";
export type Scope = string;
export type Target = string;
export type Unit = "design_px_per_second" | "fraction" | "degrees" | "design_px" | "db";
export type Curves = Curve[];
export type DocumentType1 = "episode";
export type DurationFrames = number;
export type EndFrame2 = number;
export type Id4 = string;
export type Repeat1 = false;
export type SceneId2 = string;
export type SlotId = string | null;
export type StartFrame2 = number;
export type Type = "landmark";
export type WorldX = number;
export type Frame1 = number;
export type Id5 = string;
export type Location = string;
export type ObjectId = string;
export type SceneId3 = string;
export type Type1 = "prop";
export type Events = (LandmarkEvent | PropEvent)[];
export type Format = "story" | "session" | "track";
export type Den = number;
export type Num = number;
export type Id6 = string;
export type Notes1 = string | null;
export type ActionId1 = string;
export type Channel1 = "body" | "face";
export type DurationFrames1 = number;
export type EndFrame3 = number;
export type Id7 = string;
export type MaximumGapFrames = number;
export type MinimumGapFrames = number;
export type Repeat2 = "once" | "loop_to_fill";
export type SceneId4 = string;
export type StartFrame3 = number;
export type Version3 = string;
export type RandomActions = RandomActionTiming[];
export type Revision = number;
/**
 * @minItems 1
 */
export type Scenes = [SceneInstance, ...SceneInstance[]];
export type Anchor = string | null;
export type CharacterOutfitId = string | null;
export type Continuity1 = "preserve" | "deliberate_reset";
export type Curves1 = Curve[];
export type EndFrame4 = number;
export type Events1 = (LandmarkEvent | PropEvent)[];
export type BodyPose = string;
export type CabinLight = string | null;
export type FacialOverlay = string | null;
export type TravelDistancePx = number;
export type WeatherPhaseFrame = number;
export type Id8 = string;
export type Purpose1 = string | null;
export type StartFrame4 = number;
export type CharacterPolicy = "cut" | "single_visible" | "matched";
export type Kind = "cut" | "overlap";
export type Note = string | null;
export type OverlapFrames = number;
export type SchemaVersion = "1.0";
export type Seed = number;
export type Title = string;
export type FadeInSamples = number;
export type FadeOutSamples = number;
export type GainDb = number;
export type Id9 = string;
export type LoopCrossfadeSamples = number;
export type LoopDurationSamples = number | null;
export type ReleaseId = string | null;
export type Role = "music" | "ambience";
export type SampleRate = 48000;
export type StartSample = number;
export type TrimEndSample = number;
export type TrimStartSample = number;
export type Tracks = TrackPlacement[];
export type Issue = string | null;
export type Name = string;
export type Sha2561 = string;
export type Version4 = string;
export type CancelRequested = boolean;
export type FirstFrame = number;
export type FrameCount = number;
export type Index = number;
export type Path = string;
export type RootId = string;
export type Sha2562 = string;
export type SizeBytes = number;
export type ReportPath = string | null;
export type State = "pending" | "rendering" | "verified" | "failed";
export type Chunks = ChunkRecord[];
export type CompletedFrames = number;
export type Destination = string | null;
export type DocumentType2 = "render_job";
export type DurationFrames2 = number;
export type Code = string;
export type LogPath = string | null;
export type Message = string;
export type FirstFrame1 = number;
export type Id10 = string;
export type Owner = string | null;
export type PauseRequested = boolean;
export type MaxChunkFrames = number;
export type ProfileSha256 = string;
export type TemporalHandles = 0;
export type ToolchainFingerprint = string | null;
export type Version5 = "1";
export type AudioBitrate = number;
export type AudioCodec = string | null;
export type AudioGainDb = number;
export type ColorSpace = "bt709";
export type Container = "mp4" | "mkv";
export type Id11 = string;
export type PixelFormat = string;
export type SampleRate1 = 48000;
export type VideoBitrate = number | null;
export type VideoCodec = string;
export type ReportPath1 = string | null;
export type Revision1 = number;
export type SchemaVersion1 = "1.0";
export type SnapshotSha256 = string;
export type State1 = "queued" | "running" | "paused" | "interrupted" | "cancelled" | "failed" | "verified";
export type SchemaVersion2 = "1.0";
export type DocumentType3 = "preview_selection";
export type Id12 = string;
export type JobId = string;
export type Frame2 = number;
export type Id13 = string;
export type Note1 = string;
export type SnapshotSha2561 = string;
/**
 * @maxItems 10000
 */
export type Markers = PreviewMarker[];
export type PreviousJobId = string | null;
export type Revision2 = number;
export type SchemaVersion3 = "1.0";
export type SnapshotSha2562 = string;
export type Stale = boolean;

export interface WebPreview {
  document_type?: DocumentType;
  episode: Episode;
  issue: Issue;
  job: RenderJob | null;
  previous_job: RenderJob | null;
  schema_version: SchemaVersion2;
  selection: PreviewSelection | null;
  snapshot_episode: Episode | null;
  stale: Stale;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "Episode".
 */
export interface Episode {
  actions?: Actions;
  asset_locks?: AssetLocks;
  beats?: Beats;
  canvas: Canvas;
  continuity?: Continuity;
  curves?: Curves;
  document_type: DocumentType1;
  duration_frames: DurationFrames;
  events?: Events;
  format: Format;
  fps: FrameRate;
  id: Id6;
  notes?: Notes1;
  random_actions?: RandomActions;
  revision?: Revision;
  scenes: Scenes;
  schema_version: SchemaVersion;
  seed: Seed;
  title: Title;
  tracks?: Tracks;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "ActionRequest".
 */
export interface ActionRequest {
  action_id: ActionId;
  channel: Channel;
  conflict_behavior?: ConflictBehavior;
  end_frame: EndFrame;
  id: Id;
  pack: AssetRef;
  repeat: Repeat;
  return_pose?: ReturnPose;
  scene_id: SceneId;
  start_frame: StartFrame;
  version: Version1;
}
/**
 * This interface was referenced by `SlotAssignments`'s JSON-Schema definition
 * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
 *
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "AssetLock".
 */
export interface AssetLock {
  id: Id2;
  sha256?: Sha256;
  version: Version2;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "StoryBeat".
 */
export interface StoryBeat {
  end_frame: EndFrame1;
  id: Id3;
  music_placements?: MusicPlacements;
  purpose: Purpose;
  scene_id: SceneId1;
  start_frame: StartFrame1;
  summary: Summary;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "Continuity".
 */
export interface Continuity {
  notes?: Notes;
  object_notes?: ObjectNotes;
  objects?: Objects;
  previous_episode_id?: PreviousEpisodeId;
  summary?: Summary1;
}
export interface ObjectNotes {
  /**
   * This interface was referenced by `ObjectNotes`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "Curve".
 */
export interface Curve {
  interpolation: Interpolation;
  keys: Keys;
  limits: ParameterLimit;
  outside?: Outside;
  scope: Scope;
  target: Target;
  unit: Unit;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "CurveKey".
 */
export interface CurveKey {
  frame: Frame;
  value: Value;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "ParameterLimit".
 */
export interface ParameterLimit {
  maximum: Maximum;
  minimum: Minimum;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "LandmarkEvent".
 */
export interface LandmarkEvent {
  asset: AssetRef;
  end_frame: EndFrame2;
  id: Id4;
  repeat?: Repeat1;
  scene_id: SceneId2;
  slot_id?: SlotId;
  start_frame: StartFrame2;
  type: Type;
  world_x?: WorldX;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "PropEvent".
 */
export interface PropEvent {
  frame: Frame1;
  id: Id5;
  location: Location;
  object_id: ObjectId;
  scene_id: SceneId3;
  type: Type1;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "RandomActionTiming".
 */
export interface RandomActionTiming {
  action_id: ActionId1;
  channel: Channel1;
  duration_frames: DurationFrames1;
  end_frame: EndFrame3;
  id: Id7;
  maximum_gap_frames: MaximumGapFrames;
  minimum_gap_frames: MinimumGapFrames;
  pack: AssetRef;
  repeat?: Repeat2;
  scene_id: SceneId4;
  start_frame: StartFrame3;
  version: Version3;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "SceneInstance".
 */
export interface SceneInstance {
  anchor?: Anchor;
  character_outfit_id?: CharacterOutfitId;
  continuity?: Continuity1;
  curves?: Curves1;
  end_frame: EndFrame4;
  events?: Events1;
  final_state?: SceneState | null;
  id: Id8;
  initial_state: SceneState;
  purpose?: Purpose1;
  slot_assignments?: SlotAssignments;
  start_frame: StartFrame4;
  template: AssetRef;
  transition_in?: Transition;
  transition_out?: Transition;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "SceneState".
 */
export interface SceneState {
  body_pose: BodyPose;
  cabin_light?: CabinLight;
  facial_overlay?: FacialOverlay;
  props?: Props;
  travel_distance_px?: TravelDistancePx;
  weather_phase_frame?: WeatherPhaseFrame;
}
export interface Props {
  /**
   * This interface was referenced by `Props`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
export interface SlotAssignments {
  [k: string]: AssetRef;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "Transition".
 */
export interface Transition {
  character_policy?: CharacterPolicy;
  kind?: Kind;
  match_action?: AssetRef | null;
  note?: Note;
  overlap_frames?: OverlapFrames;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "TrackPlacement".
 */
export interface TrackPlacement {
  asset: AssetRef;
  fade_in_samples?: FadeInSamples;
  fade_out_samples?: FadeOutSamples;
  gain_db?: GainDb;
  id: Id9;
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
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "RenderJob".
 */
export interface RenderJob {
  backend: Fingerprint;
  cancel_requested?: CancelRequested;
  chunks: Chunks;
  completed_frames?: CompletedFrames;
  destination?: Destination;
  document_type: DocumentType2;
  duration_frames: DurationFrames2;
  error?: JobError | null;
  first_frame?: FirstFrame1;
  id: Id10;
  output?: HashedFile | null;
  owner?: Owner;
  pause_requested?: PauseRequested;
  plan?: ChunkPlan | null;
  profile: OutputProfile;
  report_path?: ReportPath1;
  revision?: Revision1;
  schema_version: SchemaVersion1;
  snapshot_sha256: SnapshotSha256;
  state: State1;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "Fingerprint".
 */
export interface Fingerprint {
  name: Name;
  sha256: Sha2561;
  version: Version4;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
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
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha2562;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "JobError".
 */
export interface JobError {
  code: Code;
  log_path?: LogPath;
  message: Message;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "ChunkPlan".
 */
export interface ChunkPlan {
  max_chunk_frames: MaxChunkFrames;
  pipeline: Fingerprint;
  profile_sha256: ProfileSha256;
  temporal_handles?: TemporalHandles;
  toolchain_fingerprint?: ToolchainFingerprint;
  version?: Version5;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
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
  id: Id11;
  pixel_format: PixelFormat;
  sample_rate?: SampleRate1;
  video_bitrate?: VideoBitrate;
  video_codec: VideoCodec;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "PreviewSelection".
 */
export interface PreviewSelection {
  document_type?: DocumentType3;
  id: Id12;
  job_id: JobId;
  markers?: Markers;
  pipeline: Fingerprint;
  previous_job_id?: PreviousJobId;
  revision?: Revision2;
  schema_version: SchemaVersion3;
  snapshot_sha256: SnapshotSha2562;
}
/**
 * This interface was referenced by `WebPreview`'s JSON-Schema
 * via the `definition` "PreviewMarker".
 */
export interface PreviewMarker {
  frame: Frame2;
  id: Id13;
  note: Note1;
  snapshot_sha256: SnapshotSha2561;
}
