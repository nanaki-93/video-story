/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "web_project";
export type Handle = string;
export type Path = string;
export type CreatedAt = string;
export type DocumentType1 = "project";
export type EpisodeIds = string[];
export type Id = string;
export type Revision = number;
export type Root = ".";
export type SchemaVersion = "1.0";
export type Title = string;
export type UpdatedAt = string;
export type RootId = string;
export type SchemaVersion1 = "1.0";

export interface WebProject {
  document_type?: DocumentType;
  handle: Handle;
  path: Path;
  project: Project;
  root_id: RootId;
  schema_version: SchemaVersion1;
}
/**
 * This interface was referenced by `WebProject`'s JSON-Schema
 * via the `definition` "Project".
 */
export interface Project {
  created_at: CreatedAt;
  document_type: DocumentType1;
  episode_ids?: EpisodeIds;
  id: Id;
  media_roots?: MediaRoots;
  revision?: Revision;
  root?: Root;
  schema_version: SchemaVersion;
  title: Title;
  updated_at: UpdatedAt;
}
export interface MediaRoots {
  /**
   * This interface was referenced by `MediaRoots`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
