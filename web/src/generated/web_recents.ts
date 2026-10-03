/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "web_recents";
export type Id = string;
export type Path = string;
export type RootId = string;
export type RootPath = string;
export type Title = string;
/**
 * @maxItems 30
 */
export type Projects = RecentProject[];
export type SchemaVersion = "1.0";

export interface WebRecents {
  document_type?: DocumentType;
  projects: Projects;
  schema_version: SchemaVersion;
}
/**
 * This interface was referenced by `WebRecents`'s JSON-Schema
 * via the `definition` "RecentProject".
 */
export interface RecentProject {
  id: Id;
  path: Path;
  root_id: RootId;
  root_path: RootPath;
  title: Title;
}
