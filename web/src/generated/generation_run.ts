/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "generation_run";
/**
 * @maxItems 16
 */
export type Downloads =
  | []
  | [HashedFile]
  | [HashedFile, HashedFile]
  | [HashedFile, HashedFile, HashedFile]
  | [HashedFile, HashedFile, HashedFile, HashedFile]
  | [HashedFile, HashedFile, HashedFile, HashedFile, HashedFile]
  | [HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile]
  | [HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile]
  | [HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile]
  | [HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile, HashedFile]
  | [
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile
    ]
  | [
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile
    ]
  | [
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile
    ]
  | [
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile
    ]
  | [
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile
    ]
  | [
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile
    ]
  | [
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile,
      HashedFile
    ];
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
export type Endpoint = string;
export type Error = string | null;
export type Id = string;
/**
 * @maxItems 16
 */
export type ImportedAssets =
  | []
  | [AssetRef]
  | [AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef, AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef]
  | [AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef, AssetRef]
  | [
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef
    ]
  | [
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef
    ]
  | [
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef
    ]
  | [
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef
    ]
  | [
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef,
      AssetRef
    ];
export type Id1 = string;
export type Version = string;
export type Description = string;
export type DocumentType1 = "comfy_workflow";
export type Id2 = string;
/**
 * @minItems 1
 * @maxItems 32
 */
export type Models = [ModelBinding, ...ModelBinding[]];
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
export type Version1 = string;
export type ManifestSha256 = string;
/**
 * @maxItems 16
 */
export type Outputs =
  | []
  | [GenerationOutput]
  | [GenerationOutput, GenerationOutput]
  | [GenerationOutput, GenerationOutput, GenerationOutput]
  | [GenerationOutput, GenerationOutput, GenerationOutput, GenerationOutput]
  | [GenerationOutput, GenerationOutput, GenerationOutput, GenerationOutput, GenerationOutput]
  | [GenerationOutput, GenerationOutput, GenerationOutput, GenerationOutput, GenerationOutput, GenerationOutput]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ]
  | [
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput,
      GenerationOutput
    ];
export type Filename = string;
export type NodeId1 = string;
export type Subfolder = string;
export type Type = "output";
export type PromptId = string;
export type QueuePosition = number | null;
export type Revision1 = number;
export type SchemaVersion1 = "1.0";
export type State = "submitting" | "unknown" | "queued" | "running" | "succeeded" | "failed" | "imported";

export interface GenerationRun {
  document_type?: DocumentType;
  downloads?: Downloads;
  endpoint: Endpoint;
  error?: Error;
  id: Id;
  imported_assets?: ImportedAssets;
  manifest: ComfyWorkflow;
  manifest_sha256: ManifestSha256;
  outputs?: Outputs;
  prompt_id: PromptId;
  queue_position?: QueuePosition;
  revision?: Revision1;
  schema_version: SchemaVersion1;
  state: State;
}
/**
 * This interface was referenced by `GenerationRun`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `GenerationRun`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `GenerationRun`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
/**
 * This interface was referenced by `GenerationRun`'s JSON-Schema
 * via the `definition` "ComfyWorkflow".
 */
export interface ComfyWorkflow {
  description: Description;
  document_type?: DocumentType1;
  id: Id2;
  models: Models;
  node_definitions: NodeDefinitions;
  output_nodes: OutputNodes;
  revision?: Revision;
  schema_version: SchemaVersion;
  seed?: Seed;
  synthetic_fixture?: SyntheticFixture;
  version: Version1;
  workflow: HashedFile;
}
/**
 * This interface was referenced by `GenerationRun`'s JSON-Schema
 * via the `definition` "ModelBinding".
 */
export interface ModelBinding {
  file: HashedFile;
  input_name: InputName;
  node_id: NodeId;
  server_name: ServerName;
}
export interface NodeDefinitions {
  [k: string]: string;
}
/**
 * This interface was referenced by `GenerationRun`'s JSON-Schema
 * via the `definition` "GenerationOutput".
 */
export interface GenerationOutput {
  filename: Filename;
  node_id: NodeId1;
  subfolder?: Subfolder;
  type?: Type;
}
