/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type CacheBudgetBytes = number;
export type DocumentType = "app_preferences";
export type Encoder = "libx264" | "h264_videotoolbox";
export type ExportPreset = "proxy" | "1080p" | "4k";
/**
 * @maxItems 100
 */
export type AllowedWorkflowHashes = string[];
export type Enabled = boolean;
export type Endpoint = string;
export type MaxOutputBytes = number;
export type Id = "local";
export type Revision = number;
export type SchemaVersion = "1.0";
export type Theme = "dusk" | "contrast";

export interface AppPreferences {
  cache_budget_bytes?: CacheBudgetBytes;
  document_type?: DocumentType;
  encoder?: Encoder;
  export_preset?: ExportPreset;
  generation?: GenerationPolicy;
  id?: Id;
  revision?: Revision;
  schema_version: SchemaVersion;
  theme?: Theme;
}
/**
 * This interface was referenced by `AppPreferences`'s JSON-Schema
 * via the `definition` "GenerationPolicy".
 */
export interface GenerationPolicy {
  allowed_workflow_hashes?: AllowedWorkflowHashes;
  enabled?: Enabled;
  endpoint?: Endpoint;
  max_output_bytes?: MaxOutputBytes;
}
