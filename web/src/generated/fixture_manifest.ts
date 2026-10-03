/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "fixture_manifest";
export type Episode = string;
/**
 * @minItems 1
 */
export type Files = [HashedFile, ...HashedFile[]];
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
export type Generator = "tabi-fixtures-v1";
export type GeneratorSha256 = string;
export type ProductionApproved = boolean;
export type Project = string;
export type SchemaVersion = "1.0";
export type Synthetic = boolean;

export interface FixtureManifest {
  document_type?: DocumentType;
  episode?: Episode;
  files: Files;
  generator?: Generator;
  generator_sha256: GeneratorSha256;
  production_approved?: ProductionApproved;
  project?: Project;
  schema_version: SchemaVersion;
  synthetic?: Synthetic;
}
/**
 * This interface was referenced by `FixtureManifest`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `FixtureManifest`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
