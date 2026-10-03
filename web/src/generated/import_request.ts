/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type X = number;
export type Y = number;
export type Cameras = string[];
export type Channels = ("body" | "face")[];
export type Height = number;
export type Width = number;
export type X1 = number;
export type Y1 = number;
export type Id = string;
export type Version = string;
export type Templates = AssetRef[];
export type Den = number;
export type Num = number;
export type Id1 = string;
export type Kind = "still" | "mask" | "sequence" | "video" | "audio" | "font";
export type Mode = "copy" | "link";
/**
 * @minItems 1
 */
export type Paths = [MediaPath, ...MediaPath[]];
export type Path = string;
export type RootId = string;
export type CommercialUse = "pending" | "confirmed" | "not-permitted";
export type Creator = string | null;
export type ModelName = string | null;
export type ModelSha256 = string | null;
export type Notes = string | null;
export type Seed = number | null;
export type WorkflowSha256 = string | null;
export type LicenceEvidence = MediaPath[];
export type Notes1 = string | null;
export type Origin = "unknown" | "user_supplied" | "synthetic" | "generated";
export type ReferenceIds = string[];
export type Version1 = string;

export interface ImportRequest {
  compatibility?: Compatibility;
  fps?: FrameRate | null;
  id: Id1;
  kind: Kind;
  mode?: Mode;
  paths: Paths;
  provenance?: Provenance;
  version: Version1;
}
/**
 * This interface was referenced by `ImportRequest`'s JSON-Schema
 * via the `definition` "Compatibility".
 */
export interface Compatibility {
  anchor?: Point | null;
  cameras?: Cameras;
  channels?: Channels;
  crop?: Crop | null;
  pivot?: Point | null;
  templates?: Templates;
}
/**
 * This interface was referenced by `ImportRequest`'s JSON-Schema
 * via the `definition` "Point".
 */
export interface Point {
  x: X;
  y: Y;
}
/**
 * This interface was referenced by `ImportRequest`'s JSON-Schema
 * via the `definition` "Crop".
 */
export interface Crop {
  height: Height;
  width: Width;
  x: X1;
  y: Y1;
}
/**
 * This interface was referenced by `ImportRequest`'s JSON-Schema
 * via the `definition` "AssetRef".
 */
export interface AssetRef {
  id: Id;
  version: Version;
}
/**
 * This interface was referenced by `ImportRequest`'s JSON-Schema
 * via the `definition` "FrameRate".
 */
export interface FrameRate {
  den: Den;
  num: Num;
}
/**
 * This interface was referenced by `ImportRequest`'s JSON-Schema
 * via the `definition` "MediaPath".
 */
export interface MediaPath {
  path: Path;
  root_id?: RootId;
}
/**
 * This interface was referenced by `ImportRequest`'s JSON-Schema
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
 * This interface was referenced by `ImportRequest`'s JSON-Schema
 * via the `definition` "GenerationRecord".
 */
export interface GenerationRecord {
  model_name?: ModelName;
  model_sha256?: ModelSha256;
  notes?: Notes;
  seed?: Seed;
  workflow?: MediaPath | null;
  workflow_sha256?: WorkflowSha256;
}
