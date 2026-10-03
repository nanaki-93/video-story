import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import validators from "../src/generated/validators.cjs";

test("browser DTOs reject incompatible majors, unknown fields and noninteger frames", async () => {
  const episode = JSON.parse(
    await readFile(
      new URL("../../examples/episode.pilot.json", import.meta.url),
    ),
  );
  assert.equal(validators.episode(episode), true);
  for (const changed of [
    { ...episode, schema_version: "2.0" },
    { ...episode, guessed_field: true },
    { ...episode, duration_frames: 2.5 },
  ]) {
    assert.equal(validators.episode(changed), false);
  }
  const changed = structuredClone(episode);
  changed.scenes[0].surprise = "rejected";
  assert.equal(validators.episode(changed), false);
});

test("precompiled validators need no runtime code generation", async () => {
  const text = await readFile(
    new URL("../src/generated/validators.cjs", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(text, /new Function\(|eval\(/);
  const request = {
    schema_version: "1.0",
    document_type: "release_preparation",
    id: "demo",
    job_id: "job-demo",
    title: "Draft",
    revision: 0,
    description: "",
    disclosure_notes: "",
    chapters: [],
    thumbnail: null,
    creative_review: null,
    metadata_review: null,
  };
  assert.equal(validators.release_preparation(request), true);
  assert.equal(
    validators.release_preparation({ ...request, private_token: "never" }),
    false,
  );
});
