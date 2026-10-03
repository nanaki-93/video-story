/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type CacheBudgetBytes = number;
export type DocumentType = "app_preferences";
export type Encoder = "libx264" | "h264_videotoolbox";
export type ExportPreset = "proxy" | "1080p" | "4k";
export type Id = "local";
export type Revision = number;
export type SchemaVersion = "1.0";
export type Theme = "dusk" | "contrast";

export interface AppPreferences {
  cache_budget_bytes?: CacheBudgetBytes;
  document_type?: DocumentType;
  encoder?: Encoder;
  export_preset?: ExportPreset;
  id?: Id;
  revision?: Revision;
  schema_version: SchemaVersion;
  theme?: Theme;
}
