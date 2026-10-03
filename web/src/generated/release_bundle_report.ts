/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type BundlePath = string;
export type DocumentType = "release_bundle_report";
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
export type Files = HashedFile[];
export type Blockers = string[];
export type DocumentType1 = "release_inspection";
export type JobId = string;
export type MetadataSha256 = string;
export type PreparationId = string;
export type Height = number;
export type Width = number;
export type ChapterStatus = "not_requested" | "valid" | "invalid";
export type StartFrame = number;
export type Title = string;
export type Chapters = Chapter[];
export type Description = string;
export type DisclosureNotes = string;
export type DocumentType2 = "public_release";
export type FirstFrame = number;
export type Den = number;
export type Num = number;
export type FrameCount = number;
export type Purpose = "preview" | "production" | "synthetic_test";
export type Approved = boolean;
export type Id = string;
export type Version = string;
export type CommercialUse = "pending" | "confirmed" | "not-permitted";
export type Synthetic = boolean;
export type Rights = PublicAssetRights[];
export type SchemaVersion = "1.0";
export type SnapshotSha256 = string;
export type ThumbnailSha256 = string | null;
export type Title1 = string;
export type Artist = string | null;
export type Name = string;
export type Role = string;
export type Credits = Credit[];
export type EndSample = number;
export type ExplicitContent = boolean | null;
export type Isrc = string | null;
export type PlacementId = string;
export type ReleaseUrl = string | null;
export type SourceSha256 = string;
export type StartSample = number;
export type Title2 = string | null;
export type Upc = string | null;
export type Tracks = PublicTrack[];
export type VideoSha256 = string;
export type RenderReportSha256 = string;
export type SchemaVersion1 = "1.0";
export type Status = "technically_verified" | "creatively_reviewed" | "rights_reviewed" | "ready_for_manual_upload";
export type Warnings = string[];
export type SchemaVersion2 = "1.0";

export interface ReleaseBundleReport {
  bundle_path: BundlePath;
  document_type?: DocumentType;
  files: Files;
  inspection: ReleaseInspection;
  schema_version: SchemaVersion2;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "ReleaseInspection".
 */
export interface ReleaseInspection {
  blockers: Blockers;
  document_type?: DocumentType1;
  job_id: JobId;
  metadata_sha256: MetadataSha256;
  preparation_id: PreparationId;
  public: PublicRelease;
  render_report_sha256: RenderReportSha256;
  schema_version: SchemaVersion1;
  status: Status;
  warnings: Warnings;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "PublicRelease".
 */
export interface PublicRelease {
  canvas: Canvas;
  chapter_status: ChapterStatus;
  chapters: Chapters;
  description: Description;
  disclosure_notes: DisclosureNotes;
  document_type?: DocumentType2;
  first_frame: FirstFrame;
  fps: FrameRate;
  frame_count: FrameCount;
  purpose: Purpose;
  rights: Rights;
  schema_version: SchemaVersion;
  snapshot_sha256: SnapshotSha256;
  thumbnail_sha256: ThumbnailSha256;
  title: Title1;
  tracks: Tracks;
  video_sha256: VideoSha256;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height;
  width: Width;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "Chapter".
 */
export interface Chapter {
  start_frame: StartFrame;
  title: Title;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "PublicAssetRights".
 */
export interface PublicAssetRights {
  approved: Approved;
  asset: AssetRef;
  commercial_use: CommercialUse;
  synthetic: Synthetic;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "PublicTrack".
 */
export interface PublicTrack {
  artist?: Artist;
  asset: AssetRef;
  credits?: Credits;
  end_sample: EndSample;
  explicit_content?: ExplicitContent;
  isrc?: Isrc;
  placement_id: PlacementId;
  release_url?: ReleaseUrl;
  source_sha256: SourceSha256;
  start_sample: StartSample;
  title?: Title2;
  upc?: Upc;
}
/**
 * This interface was referenced by `ReleaseBundleReport`'s JSON-Schema
 * via the `definition` "Credit".
 */
export interface Credit {
  name: Name;
  role: Role;
}
