/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type DocumentType = "validation_report";
export type Code = string;
export type Location = (string | number)[];
export type Message = string;
export type Severity = "error" | "warning" | "info";
export type SuggestedFix = string;
export type Issues = ValidationIssue[];
export type SchemaVersion = "1.0";
export type Scope = "structure" | "compile";
export type Valid = boolean;

export interface ValidationReport {
  document_type: DocumentType;
  issues: Issues;
  schema_version: SchemaVersion;
  scope?: Scope;
  valid: Valid;
}
/**
 * This interface was referenced by `ValidationReport`'s JSON-Schema
 * via the `definition` "ValidationIssue".
 */
export interface ValidationIssue {
  code: Code;
  location: Location;
  message: Message;
  severity: Severity;
  suggested_fix: SuggestedFix;
}
