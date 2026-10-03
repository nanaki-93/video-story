/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type StartFrame = number;
export type Title = string;
export type Chapters = Chapter[];
export type ContentSha256 = string;
export type Note = string | null;
export type ReviewedAt = string;
export type Reviewer = string;
export type Description = string;
export type DisclosureNotes = string;
export type DocumentType = "release_preparation";
export type Id = string;
export type JobId = string;
export type Revision = number;
export type SchemaVersion = "1.0";
export type Id1 = string;
export type Version = string;
export type Title1 = string;

export interface ReleasePreparation {
  chapters?: Chapters;
  creative_review?: ReviewRecord | null;
  description?: Description;
  disclosure_notes?: DisclosureNotes;
  document_type?: DocumentType;
  id: Id;
  job_id: JobId;
  metadata_review?: ReviewRecord | null;
  revision?: Revision;
  schema_version: SchemaVersion;
  thumbnail?: AssetRef | null;
  title: Title1;
}
/**
 * This interface was referenced by `ReleasePreparation`'s JSON-Schema
 * via the `definition` "Chapter".
 */
export interface Chapter {
  start_frame: StartFrame;
  title: Title;
}
/**
 * This interface was referenced by `ReleasePreparation`'s JSON-Schema
 * via the `definition` "ReviewRecord".
 */
export interface ReviewRecord {
  content_sha256: ContentSha256;
  note?: Note;
  reviewed_at: ReviewedAt;
  reviewer: Reviewer;
}
/**
 * This interface was referenced by `ReleasePreparation`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
