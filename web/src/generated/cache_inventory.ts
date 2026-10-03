/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "cache_inventory";
export type CreatedAt = string;
export type Key = string;
export type Kind = "normalized_image" | "video_chunk";
export type Message = string | null;
export type Protected = boolean;
export type Sha256 = string;
export type SizeBytes = number;
export type Valid = boolean;
export type Entries = CacheSummary[];
export type EntryBytes = number;
export type InventorySha256 = string;
export type Root = string;
export type SchemaVersion = "1.0";
export type Warnings = string[];

export interface CacheInventory {
  document_type?: DocumentType;
  entries: Entries;
  entry_bytes: EntryBytes;
  inventory_sha256: InventorySha256;
  root: Root;
  schema_version: SchemaVersion;
  warnings?: Warnings;
}
/**
 * This interface was referenced by `CacheInventory`'s JSON-Schema
 * via the `definition` "CacheSummary".
 */
export interface CacheSummary {
  created_at: CreatedAt;
  key: Key;
  kind: Kind;
  message?: Message;
  protected?: Protected;
  sha256: Sha256;
  size_bytes: SizeBytes;
  valid: Valid;
}
