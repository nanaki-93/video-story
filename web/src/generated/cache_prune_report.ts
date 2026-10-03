/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "cache_prune_report";
export type RemainingEntryBytes = number;
export type Removed = string[];
export type RemovedEntryBytes = number;
export type SchemaVersion = "1.0";

export interface CachePruneReport {
  document_type?: DocumentType;
  remaining_entry_bytes: RemainingEntryBytes;
  removed: Removed;
  removed_entry_bytes: RemovedEntryBytes;
  schema_version: SchemaVersion;
}
