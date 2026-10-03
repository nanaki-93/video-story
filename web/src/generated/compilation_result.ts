/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "compilation_result";
export type DurationFrames = number;
export type LockedInputs = number;
export type Purpose = "preview" | "production" | "synthetic_test";
export type ReviewContentSha256 = string;
export type ScheduledEvents = number;
export type SchemaVersion = "1.0";
export type SnapshotPath = string;
export type SnapshotSha256 = string;

export interface CompilationResult {
  document_type?: DocumentType;
  duration_frames: DurationFrames;
  locked_inputs: LockedInputs;
  purpose: Purpose;
  review_content_sha256: ReviewContentSha256;
  scheduled_events: ScheduledEvents;
  schema_version: SchemaVersion;
  snapshot_path: SnapshotPath;
  snapshot_sha256: SnapshotSha256;
}
