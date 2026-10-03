/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "preview_selection";
export type Id = string;
export type JobId = string;
export type Frame = number;
export type Id1 = string;
export type Note = string;
export type SnapshotSha256 = string;
/**
 * @maxItems 10000
 */
export type Markers = PreviewMarker[];
export type Name = string;
export type Sha256 = string;
export type Version = string;
export type PreviousJobId = string | null;
export type Revision = number;
export type SchemaVersion = "1.0";
export type SnapshotSha2561 = string;

export interface PreviewSelection {
  document_type?: DocumentType;
  id: Id;
  job_id: JobId;
  markers?: Markers;
  pipeline: Fingerprint;
  previous_job_id?: PreviousJobId;
  revision?: Revision;
  schema_version: SchemaVersion;
  snapshot_sha256: SnapshotSha2561;
}
/**
 * This interface was referenced by `PreviewSelection`'s JSON-Schema
 * via the `definition` "PreviewMarker".
 */
export interface PreviewMarker {
  frame: Frame;
  id: Id1;
  note: Note;
  snapshot_sha256: SnapshotSha256;
}
/**
 * This interface was referenced by `PreviewSelection`'s JSON-Schema
 * via the `definition` "Fingerprint".
 */
export interface Fingerprint {
  name: Name;
  sha256: Sha256;
  version: Version;
}
