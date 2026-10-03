/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Availability = "unchecked" | "disabled" | "online" | "offline";
export type DocumentType = "generation_status";
export type Message = string;
/**
 * @maxItems 100
 */
export type AllowedWorkflowHashes = string[];
export type Enabled = boolean;
export type Endpoint = string;
export type MaxOutputBytes = number;
export type DocumentType1 = "generation_run";
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
export type Endpoint1 = string;
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
export type DocumentType2 = "comfy_workflow";
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
export type Runs = GenerationRun[];
export type SchemaVersion2 = "1.0";
export type Workflows = ComfyWorkflow[];

export interface GenerationStatus {
  availability?: Availability;
  document_type?: DocumentType;
  message?: Message;
  policy: GenerationPolicy;
  runs?: Runs;
  schema_version: SchemaVersion2;
  workflow_hashes?: WorkflowHashes;
  workflows?: Workflows;
}
/**
 * This interface was referenced by `GenerationStatus`'s JSON-Schema
 * via the `definition` "GenerationPolicy".
 */
export interface GenerationPolicy {
  allowed_workflow_hashes?: AllowedWorkflowHashes;
  enabled?: Enabled;
  endpoint?: Endpoint;
  max_output_bytes?: MaxOutputBytes;
}
/**
 * This interface was referenced by `GenerationStatus`'s JSON-Schema
 * via the `definition` "GenerationRun".
 */
export interface GenerationRun {
  document_type?: DocumentType1;
  downloads?: Downloads;
  endpoint: Endpoint1;
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
 * This interface was referenced by `GenerationStatus`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `GenerationStatus`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `GenerationStatus`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
/**
 * This interface was referenced by `GenerationStatus`'s JSON-Schema
 * via the `definition` "ComfyWorkflow".
 */
export interface ComfyWorkflow {
  description: Description;
  document_type?: DocumentType2;
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
 * This interface was referenced by `GenerationStatus`'s JSON-Schema
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
 * This interface was referenced by `GenerationStatus`'s JSON-Schema
 * via the `definition` "GenerationOutput".
 */
export interface GenerationOutput {
  filename: Filename;
  node_id: NodeId1;
  subfolder?: Subfolder;
  type?: Type;
}
export interface WorkflowHashes {
  [k: string]: string;
}
