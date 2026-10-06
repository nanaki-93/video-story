/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type District = string | null;
export type Id = string;
export type Kind = "rest" | "look" | "pickup" | "sip" | "return_cup" | "sway" | "deep_breath" | "district";
export type TargetFrame = number;
export type Diagnostic = string | null;
export type DocumentType = "flow_attempt";
export type EpisodeId = string;
export type Id1 = string;
export type Mode = "text_reference" | "image_motion" | "extend" | "shot_start";
export type ObservedCredits = number | null;
export type ParentId = string | null;
export type ParentSha256 = string | null;
export type Prompt = string;
export type PromptSha256 = string;
export type ProviderClipId = string | null;
export type ProviderModel = string | null;
export type RecipeSha256 = string;
export type ReferencesSha256 = string;
export type ReservedCredits = number;
export type RetryIndex = number;
export type RetryReason = string | null;
export type Revision = number;
export type SchemaVersion = "1.0";
export type ShotId = string | null;
export type State = "prepared" | "awaiting_external" | "submitted" | "unknown" | "received" | "failed";
export type TemplateVersion = "1" | "2";

export interface FlowAttempt {
  beat: FlowBeat;
  diagnostic?: Diagnostic;
  document_type?: DocumentType;
  episode_id: EpisodeId;
  id: Id1;
  mode: Mode;
  observed_credits?: ObservedCredits;
  parent_id?: ParentId;
  parent_sha256?: ParentSha256;
  prompt: Prompt;
  prompt_sha256: PromptSha256;
  provider_clip_id?: ProviderClipId;
  provider_model?: ProviderModel;
  recipe_sha256: RecipeSha256;
  references_sha256: ReferencesSha256;
  reserved_credits: ReservedCredits;
  retry_index?: RetryIndex;
  retry_reason?: RetryReason;
  revision?: Revision;
  schema_version: SchemaVersion;
  shot_id?: ShotId;
  state: State;
  template_version?: TemplateVersion;
}
/**
 * This interface was referenced by `FlowAttempt`'s JSON-Schema
 * via the `definition` "FlowBeat".
 */
export interface FlowBeat {
  district?: District;
  id: Id;
  kind: Kind;
  target_frame: TargetFrame;
}
