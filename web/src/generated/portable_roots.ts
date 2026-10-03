/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "portable_roots";
/**
 * @maxItems 1000
 */
export type Roots = string[];
export type SchemaVersion = "1.0";

export interface PortableRoots {
  document_type?: DocumentType;
  roots: Roots;
  schema_version: SchemaVersion;
}
