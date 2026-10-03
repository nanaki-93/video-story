/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "web_directory";
export type Kind = "directory" | "file";
export type Name = string;
export type Path = string;
export type SizeBytes = number | null;
export type Entries = FileEntry[];
export type NextOffset = number | null;
export type Path1 = string;
export type RootId = string;
export type SchemaVersion = "1.0";

export interface WebDirectory {
  document_type?: DocumentType;
  entries: Entries;
  next_offset?: NextOffset;
  path: Path1;
  root_id: RootId;
  schema_version: SchemaVersion;
}
/**
 * This interface was referenced by `WebDirectory`'s JSON-Schema
 * via the `definition` "FileEntry".
 */
export interface FileEntry {
  kind: Kind;
  name: Name;
  path: Path;
  size_bytes?: SizeBytes;
}
