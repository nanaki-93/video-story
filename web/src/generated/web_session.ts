/* Generated from schemas/ by scripts/contracts.mjs. Do not edit. */

export type Csrf = string;
export type DocumentType = "web_session";
export type ExpiresIn = number;
export type Pid = number;
export type Protocol = "1";
export type SchemaVersion = "1.0";
export type SessionId = string;
export type Stopping = boolean;

export interface WebSession {
  csrf: Csrf;
  document_type?: DocumentType;
  expires_in: ExpiresIn;
  pid: Pid;
  protocol?: Protocol;
  schema_version: SchemaVersion;
  session_id: SessionId;
  stopping: Stopping;
}
