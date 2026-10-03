/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type ApprovalValid = boolean;
export type Id = string;
export type Version = string;
export type ContentSha256 = string;
export type DocumentType = "asset_health";
export type ExpectedSha256 = string;
export type Path = string;
export type RootId = string;
export type Message = string | null;
export type ObservedSha256 = string | null;
export type Status = "ok" | "missing" | "changed" | "inaccessible";
export type Files = FileHealth[];
export type MediaValid = boolean;
export type Proxies = FileHealth[];
export type PublicationReady = boolean;
export type Rights = "pending" | "confirmed" | "not-permitted";
export type SchemaVersion = "1.0";
export type SourceAvailable = boolean;

export interface AssetHealth {
  approval_valid: ApprovalValid;
  asset: AssetRef;
  content_sha256: ContentSha256;
  document_type?: DocumentType;
  files: Files;
  media_valid: MediaValid;
  proxies: Proxies;
  publication_ready: PublicationReady;
  rights: Rights;
  schema_version: SchemaVersion;
  source_available: SourceAvailable;
}
/**
 * This interface was referenced by `AssetHealth`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `AssetHealth`'s JSON-Schema
 * via the `definition` "FileHealth".
 */
export interface FileHealth {
  expected_sha256: ExpectedSha256;
  location: MediaPath;
  message?: Message;
  observed_sha256?: ObservedSha256;
  status: Status;
}
/**
 * This interface was referenced by `AssetHealth`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
