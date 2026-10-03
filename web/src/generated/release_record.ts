/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Artist = string;
export type ClaimNotes = string | null;
export type ContentSha256 = string;
export type Note = string | null;
export type ReviewedAt = string;
export type Reviewer = string;
export type DisclosureNotes = string | null;
export type DisclosureReviewed = boolean;
export type DocumentType = "release_record";
export type Id = string;
export type PublishedAt = string | null;
export type ReleaseTitle = string;
export type Revision = number;
export type RightsStatus = "pending" | "confirmed" | "not-permitted";
export type SchemaVersion = "1.0";
export type Status =
  | "draft"
  | "technically_verified"
  | "creatively_reviewed"
  | "rights_reviewed"
  | "ready_for_manual_upload"
  | "uploaded"
  | "published";
export type Path = string;
export type RootId = string;
/**
 * @minItems 1
 */
export type Tracks = [ReleaseTrack, ...ReleaseTrack[]];
export type AiUseNotes = string | null;
export type Id1 = string;
export type Version = string;
export type Channels = number;
export type CommercialUseStatus = "pending" | "confirmed" | "not-permitted";
export type Name = string;
export type Role = string;
export type Credits = Credit[];
export type DurationSamples = number;
export type ExplicitContent = boolean | null;
export type Isrc = string | null;
export type ReleaseUrl = string | null;
export type SampleRate = number;
export type Sha256 = string | null;
export type Title = string;
export type Upc = string | null;

export interface ReleaseRecord {
  artist: Artist;
  claim_notes?: ClaimNotes;
  creative_review?: ReviewRecord | null;
  disclosure_notes?: DisclosureNotes;
  disclosure_reviewed?: DisclosureReviewed;
  document_type: DocumentType;
  id: Id;
  published_at?: PublishedAt;
  release_links?: ReleaseLinks;
  release_title: ReleaseTitle;
  revision?: Revision;
  rights_status?: RightsStatus;
  schema_version: SchemaVersion;
  status?: Status;
  technical_report?: MediaPath | null;
  tracks: Tracks;
  upc?: Upc;
}
/**
 * This interface was referenced by `ReleaseRecord`'s JSON-Schema
 * via the `definition` "ReviewRecord".
 */
export interface ReviewRecord {
  content_sha256: ContentSha256;
  note?: Note;
  reviewed_at: ReviewedAt;
  reviewer: Reviewer;
}
export interface ReleaseLinks {
  /**
   * This interface was referenced by `ReleaseLinks`'s JSON-Schema definition
   * via the `patternProperty` "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$".
   */
  [k: string]: string;
}
/**
 * This interface was referenced by `ReleaseRecord`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `ReleaseRecord`'s JSON-Schema
 * via the `definition` "ReleaseTrack".
 */
export interface ReleaseTrack {
  ai_use_notes?: AiUseNotes;
  asset: AssetRef;
  channels: Channels;
  commercial_use_status?: CommercialUseStatus;
  credits?: Credits;
  duration_samples: DurationSamples;
  explicit_content?: ExplicitContent;
  isrc?: Isrc;
  master: MediaPath;
  release_url?: ReleaseUrl;
  sample_rate: SampleRate;
  sha256?: Sha256;
  source_project?: MediaPath | null;
  title: Title;
}
/**
 * This interface was referenced by `ReleaseRecord`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id1;
  version: Version;
}
/**
 * This interface was referenced by `ReleaseRecord`'s JSON-Schema
 * via the `definition` "Credit".
 */
export interface Credit {
  name: Name;
  role: Role;
}
