import test from "node:test";
import assert from "node:assert/strict";
import { SceneDraft } from "../src/lofi-state.ts";
import validators from "../src/generated/validators.cjs";

test("late saves cannot clear newer scene edits or a different selection", () => {
  const draft = new SceneDraft();
  draft.change();
  const pending = draft.ticket();
  draft.change();
  assert.equal(draft.accept(pending), false);
  assert.equal(draft.dirty, true);
  assert.equal(draft.accept(draft.ticket()), true);
  assert.equal(draft.dirty, false);
  const previous = draft.ticket();
  draft.reset();
  draft.change();
  assert.equal(draft.accept(previous), false);
  assert.equal(draft.dirty, true);
});

test("scene transport rejects old generator fields and fractional saved loop timing", () => {
  const scene = {
    schema_version: "1.0",
    id: "scene.test",
    title: "Test",
    master: { id: "master", version: "1.0" },
    overlays: [
      {
        id: "blink",
        asset: { id: "eyes", version: "1.0" },
        timing: { source: { start_frame: 0, end_frame: 4 }, repeat_frames: 72 },
      },
    ],
  };
  assert.equal(validators.lofi_scene(scene), true);
  assert.equal(validators.lofi_scene({ ...scene, prompt: "generate" }), false);
  assert.equal(
    validators.lofi_scene({ ...scene, schema_version: "2.0" }),
    false,
  );
  const fractional = structuredClone(scene);
  fractional.overlays[0].timing.repeat_frames = 2.5;
  assert.equal(validators.lofi_scene(fractional), false);
});
