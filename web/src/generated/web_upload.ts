/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Complete = boolean;
export type DocumentType = "web_upload";
export type Id = string;
export type Name = string;
export type ReceivedBytes = number;
export type SchemaVersion = "1.0";
export type Sha256 = string | null;
export type SizeBytes = number;

export interface WebUpload {
  complete?: Complete;
  document_type?: DocumentType;
  id: Id;
  name: Name;
  received_bytes: ReceivedBytes;
  schema_version: SchemaVersion;
  sha256?: Sha256;
  size_bytes: SizeBytes;
}
