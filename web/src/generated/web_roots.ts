/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "web_roots";
export type Id = string;
export type Path = string;
export type Roots = WebRoot[];
export type SchemaVersion = "1.0";

export interface WebRoots {
  document_type?: DocumentType;
  roots: Roots;
  schema_version: SchemaVersion;
}
/**
 * This interface was referenced by `WebRoots`'s JSON-Schema
 * via the `definition` "WebRoot".
 */
export interface WebRoot {
  id: Id;
  path: Path;
}
