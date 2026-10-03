/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type CreatedAt = string;
export type DocumentType = "backup_manifest";
/**
 * @minItems 1
 * @maxItems 100000
 */
export type Files = [HashedFile, ...HashedFile[]];
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
export type ProjectId = string;
export type SchemaVersion = "1.0";
export type TotalBytes = number;
export type Warnings = string[];

export interface BackupManifest {
  created_at: CreatedAt;
  document_type?: DocumentType;
  files: Files;
  project_id: ProjectId;
  schema_version: SchemaVersion;
  total_bytes: TotalBytes;
  warnings?: Warnings;
}
/**
 * This interface was referenced by `BackupManifest`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `BackupManifest`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
