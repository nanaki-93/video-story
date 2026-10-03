import validators from "./generated/validators.cjs";
import type { Documents } from "./generated/documents";

export type { Documents };

export function document<K extends keyof Documents>(
  kind: K,
  data: unknown,
): Documents[K] {
  const validate = validators[kind];
  if (!validate(data)) {
    const details = validate.errors
      ?.map((error) => `${error.instancePath || "/"}: ${error.message}`)
      .join("; ");
    throw new Error(
      `Incompatible ${kind}: ${details || "schema validation failed"}`,
    );
  }
  return data as Documents[K];
}

export async function fetchDocument<K extends keyof Documents>(
  url: string,
  kind: K,
  signal?: AbortSignal,
): Promise<Documents[K]> {
  const response = await fetch(url, {
    credentials: "same-origin",
    cache: "no-store",
    signal,
  });
  if (!response.ok)
    throw new Error(
      `Request failed (${response.status}). Reconnect to the local worker.`,
    );
  return document(kind, await response.json());
}
