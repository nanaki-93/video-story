import test from "node:test";
import assert from "node:assert/strict";
import { EditHistory } from "../src/edit-history.ts";

test("queued edits and undo redo use latest revisions and restore content", async () => {
  let saved = { revision: 0, title: "Initial", frames: 300 };
  const revisions = [];
  const history = new EditHistory(saved, async (revision, command) => {
    revisions.push(revision);
    assert.equal(revision, saved.revision);
    saved = {
      ...(command.kind === "replace"
        ? command.episode
        : { ...saved, title: command.title }),
      revision: revision + 1,
    };
    return structuredClone(saved);
  });
  const first = history.apply({ kind: "title", title: "One" });
  const second = history.apply({ kind: "title", title: "Two" });
  await Promise.all([first, second]);
  assert.equal(history.current.title, "Two");
  await history.undo();
  assert.equal(history.current.title, "One");
  await history.undo();
  assert.equal(history.current.title, "Initial");
  await history.redo();
  assert.equal(history.current.title, "One");
  await history.apply({ kind: "title", title: "New branch" });
  assert.equal(history.future.length, 0);
  assert.deepEqual(revisions, [0, 1, 2, 3, 4, 5]);
  assert.equal(history.current.frames, 300);
});

test("a rejected save cannot mutate history or discard the saved document", async () => {
  let reject = false;
  const history = new EditHistory(
    { revision: 0, title: "Saved" },
    async (revision, command) => {
      if (reject) throw new Error("stale revision");
      return { revision: revision + 1, title: command.title };
    },
  );
  await history.apply({ title: "New" });
  reject = true;
  await assert.rejects(history.undo(), /stale revision/);
  assert.equal(history.current.title, "New");
  assert.equal(history.past.length, 1);
  assert.equal(history.future.length, 0);
  await history.tail;
  assert.equal(history.pending, 0);
});
