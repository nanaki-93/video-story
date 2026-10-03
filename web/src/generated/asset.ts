/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type ContentSha256 = string | null;
export type Note = string | null;
export type ReviewedAt = string | null;
export type Reviewer = string | null;
export type Status = "draft" | "review" | "approved" | "rejected";
export type X = number;
export type Y = number;
export type Cameras = string[];
export type Channels = ("body" | "face")[];
export type Height = number;
export type Width = number;
export type X1 = number;
export type Y1 = number;
export type Outfits = string[];
export type Id = string;
export type Version = string;
export type Templates = AssetRef[];
export type DocumentType = "asset";
/**
 * @minItems 1
 */
export type Files = [HashedFile, ...HashedFile[]];
export type Path = string;
export type RootId = string;
export type Sha256 = string;
export type SizeBytes = number;
export type Id1 = string;
export type Kind = "still" | "mask" | "sequence" | "video" | "audio" | "font";
export type AlphaMode = "none" | "straight" | "premultiplied" | "unknown";
export type Height1 = number;
export type Width1 = number;
export type Channels1 = number | null;
export type Codec = string | null;
export type ColorSpace = "srgb" | "bt709" | "grayscale" | "unknown";
export type DurationSamples = number | null;
export type Den = number;
export type Num = number;
export type FrameCount = number | null;
export type PixelFormat = string | null;
export type SampleRate = number | null;
export type CommercialUse = "pending" | "confirmed" | "not-permitted";
export type Creator = string | null;
export type ManifestSha256 = string | null;
export type ModelName = string | null;
export type ModelSha256 = string | null;
export type Notes = string | null;
export type PromptId = string | null;
export type Seed = number | null;
export type WorkflowSha256 = string | null;
export type LicenceEvidence = MediaPath[];
export type Notes1 = string | null;
export type Origin = "unknown" | "user_supplied" | "synthetic" | "generated";
export type ReferenceIds = string[];
export type Proxies = HashedFile[];
export type Revision = number;
export type SchemaVersion = "1.0";
export type Version1 = string;

export interface Asset {
  approval?: Approval;
  compatibility?: Compatibility;
  document_type: DocumentType;
  files: Files;
  id: Id1;
  kind: Kind;
  probe: ProbeData;
  provenance?: Provenance;
  proxies?: Proxies;
  revision?: Revision;
  schema_version: SchemaVersion;
  source: MediaPath;
  version: Version1;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "Approval".
 */
export interface Approval {
  content_sha256?: ContentSha256;
  note?: Note;
  reviewed_at?: ReviewedAt;
  reviewer?: Reviewer;
  status?: Status;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "Compatibility".
 */
export interface Compatibility {
  anchor?: Point | null;
  cameras?: Cameras;
  channels?: Channels;
  crop?: Crop | null;
  outfits?: Outfits;
  pivot?: Point | null;
  templates?: Templates;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "Point".
 */
export interface Point {
  x: X;
  y: Y;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "Crop".
 */
export interface Crop {
  height: Height;
  width: Width;
  x: X1;
  y: Y1;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "HashedFile".
 */
export interface HashedFile {
  location: MediaPath;
  sha256: Sha256;
  size_bytes: SizeBytes;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "ProbeData".
 */
export interface ProbeData {
  alpha_mode?: AlphaMode;
  canvas?: Canvas | null;
  channels?: Channels1;
  codec?: Codec;
  color_space?: ColorSpace;
  duration_samples?: DurationSamples;
  fps?: FrameRate | null;
  frame_count?: FrameCount;
  pixel_aspect?: FrameRate;
  pixel_format?: PixelFormat;
  sample_rate?: SampleRate;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "Canvas".
 */
export interface Canvas {
  height: Height1;
  width: Width1;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "Provenance".
 */
export interface Provenance {
  commercial_use?: CommercialUse;
  creator?: Creator;
  generation?: GenerationRecord | null;
  licence_evidence?: LicenceEvidence;
  notes?: Notes1;
  origin?: Origin;
  reference_ids?: ReferenceIds;
}
/**
 * This interface was referenced by `Asset`'s JSON-Schema
 * via the `definition` "GenerationRecord".
 */
export interface GenerationRecord {
  manifest_sha256?: ManifestSha256;
  model_hashes?: ModelHashes;
  model_name?: ModelName;
  model_sha256?: ModelSha256;
  notes?: Notes;
  prompt_id?: PromptId;
  seed?: Seed;
  workflow?: MediaPath | null;
  workflow_sha256?: WorkflowSha256;
}
export interface ModelHashes {
  [k: string]: string;
}
