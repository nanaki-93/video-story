/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type CacheRoot = string;
export type ConfigFile = string;
export type ConfigSha256 = string | null;
export type DocumentType = "web_settings";
export type Ffmpeg = string;
export type Ffprobe = string;
export type CacheBudgetBytes = number;
export type DocumentType1 = "app_preferences";
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
export type PreferencesSaved = boolean;
export type SchemaVersion1 = "1.0";

export interface WebSettings {
  cache_root: CacheRoot;
  config_file: ConfigFile;
  config_sha256: ConfigSha256;
  document_type?: DocumentType;
  ffmpeg: Ffmpeg;
  ffprobe: Ffprobe;
  preferences: AppPreferences;
  preferences_saved: PreferencesSaved;
  schema_version: SchemaVersion1;
}
/**
 * This interface was referenced by `WebSettings`'s JSON-Schema
 * via the `definition` "AppPreferences".
 */
export interface AppPreferences {
  cache_budget_bytes?: CacheBudgetBytes;
  document_type?: DocumentType1;
  encoder?: Encoder;
  export_preset?: ExportPreset;
  generation?: GenerationPolicy;
  id?: Id;
  revision?: Revision;
  schema_version: SchemaVersion;
  theme?: Theme;
}
/**
 * This interface was referenced by `WebSettings`'s JSON-Schema
 * via the `definition` "GenerationPolicy".
 */
export interface GenerationPolicy {
  allowed_workflow_hashes?: AllowedWorkflowHashes;
  enabled?: Enabled;
  endpoint?: Endpoint;
  max_output_bytes?: MaxOutputBytes;
}
