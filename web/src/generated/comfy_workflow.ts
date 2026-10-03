/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Description = string;
export type DocumentType = "comfy_workflow";
export type Id = string;
/**
 * @minItems 1
 * @maxItems 32
 */
export type Models = [ModelBinding, ...ModelBinding[]];
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
export type InputName = string;
export type NodeId = string;
export type ServerName = string;
/**
 * @minItems 1
 * @maxItems 16
 */
export type OutputNodes =
  | [string]
  | [string, string]
  | [string, string, string]
  | [string, string, string, string]
  | [string, string, string, string, string]
  | [string, string, string, string, string, string]
  | [string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string, string, string]
  | [string, string, string, string, string, string, string, string, string, string, string, string, string, string]
  | [
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string
    ]
  | [
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string,
      string
    ];
export type Revision = number;
export type SchemaVersion = "1.0";
export type Seed = number | null;
export type SyntheticFixture = boolean;
export type Version = string;

export interface ComfyWorkflow {
  description: Description;
  document_type?: DocumentType;
  id: Id;
  models: Models;
  node_definitions: NodeDefinitions;
  output_nodes: OutputNodes;
  revision?: Revision;
  schema_version: SchemaVersion;
  seed?: Seed;
  synthetic_fixture?: SyntheticFixture;
  version: Version;
  workflow: HashedFile;
}
/**
 * This interface was referenced by `ComfyWorkflow`'s JSON-Schema
 * via the `definition` "ModelBinding".
 */
export interface ModelBinding {
  file: HashedFile;
  input_name: InputName;
  node_id: NodeId;
  server_name: ServerName;
}
/**
 * This interface was referenced by `ComfyWorkflow`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `ComfyWorkflow`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
export interface NodeDefinitions {
  [k: string]: string;
}
