/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type CreatedAt = string;
export type DocumentType = "project";
export type EpisodeIds = string[];
export type Id = string;
export type Revision = number;
export type Root = ".";
export type SchemaVersion = "1.0";
export type Title = string;
export type UpdatedAt = string;

export interface Project {
  created_at: CreatedAt;
  document_type: DocumentType;
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
