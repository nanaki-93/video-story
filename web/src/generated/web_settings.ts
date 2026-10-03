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
  id?: Id;
  revision?: Revision;
  schema_version: SchemaVersion;
  theme?: Theme;
}
