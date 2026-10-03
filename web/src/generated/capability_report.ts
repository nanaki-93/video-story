/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "capability_report";
export type EncoderVerification = "listed_only";
export type Encoders = string[];
export type Path = string | null;
export type Requested = string;
export type Sha256 = string | null;
export type Version = string | null;
export type VersionOutput = string | null;
export type Filters = string[];
export type Fingerprint = string;
export type HardwareAccelerators = string[];
export type Code = string;
export type Location = (string | number)[];
export type Message = string;
export type Severity = "error" | "warning" | "info";
export type SuggestedFix = string;
export type Issues = ValidationIssue[];
export type Architecture = string;
export type Cpu = string;
export type IsTargetM5Pro = boolean;
export type MemoryBytes = number | null;
export type Os = string;
export type OsVersion = string;
export type PythonExecutable = string;
export type PythonVersion = string;
export type ObservedAt = string;
export type Ready = boolean;
export type RequiredEncoders = string[];
export type RequiredFilters = string[];
export type SchemaVersion = "1.0";
export type FreeBytes = number | null;
export type Path1 = string;
export type RequiredFreeBytes = number;
export type Writable = boolean;

export interface CapabilityReport {
  document_type?: DocumentType;
  encoder_verification?: EncoderVerification;
  encoders: Encoders;
  ffmpeg: ToolInfo;
  ffprobe: ToolInfo;
  filters: Filters;
  fingerprint: Fingerprint;
  hardware_accelerators: HardwareAccelerators;
  issues: Issues;
  machine: MachineInfo;
  observed_at: ObservedAt;
  ready: Ready;
  required_encoders: RequiredEncoders;
  required_filters: RequiredFilters;
  schema_version: SchemaVersion;
  storage: StorageInfo;
}
/**
 * This interface was referenced by `CapabilityReport`'s JSON-Schema
 * via the `definition` "ToolInfo".
 */
export interface ToolInfo {
  path?: Path;
  requested: Requested;
  sha256?: Sha256;
  version?: Version;
  version_output?: VersionOutput;
}
/**
 * This interface was referenced by `CapabilityReport`'s JSON-Schema
 * via the `definition` "ValidationIssue".
 */
export interface ValidationIssue {
  code: Code;
  location: Location;
  message: Message;
  severity: Severity;
  suggested_fix: SuggestedFix;
}
/**
 * This interface was referenced by `CapabilityReport`'s JSON-Schema
 * via the `definition` "MachineInfo".
 */
export interface MachineInfo {
  architecture: Architecture;
  cpu: Cpu;
  is_target_m5_pro: IsTargetM5Pro;
  memory_bytes?: MemoryBytes;
  os: Os;
  os_version: OsVersion;
  python_executable: PythonExecutable;
  python_version: PythonVersion;
}
/**
 * This interface was referenced by `CapabilityReport`'s JSON-Schema
 * via the `definition` "StorageInfo".
 */
export interface StorageInfo {
  free_bytes?: FreeBytes;
  path: Path1;
  required_free_bytes: RequiredFreeBytes;
  writable: Writable;
}
