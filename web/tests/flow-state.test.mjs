import test from "node:test";
import assert from "node:assert/strict";
import { FlowRequests } from "../src/flow-state.ts";
function deferred() {
  let resolve;
  const promise = new Promise((r) => {
    resolve = r;
  });
  return { promise, resolve };
}
test("a stale read cannot replace a newer saved revision", async () => {
  const state = new FlowRequests();
  const slow = deferred();
  const first = state.read(() => slow.promise);
  await state.read(async () => ({ revision: 2 }));
  slow.resolve({ revision: 1 });
  assert.equal(await first, undefined);
  assert.equal(state.current.revision, 2);
});
test("repeat clicks submit once and pending reads cannot overwrite a mutation", async () => {
  const state = new FlowRequests();
  const read = deferred(),
    save = deferred();
  const first = state.read(() => read.promise);
  let calls = 0;
  const mutation = state.change(() => {
    calls++;
    return save.promise;
  });
  assert.equal(
    await state.change(() => {
      calls++;
      return save.promise;
    }),
    undefined,
  );
  read.resolve({ revision: 0 });
  await first;
  save.resolve({ revision: 1 });
  await mutation;
  assert.equal(calls, 1);
  assert.equal(state.current.revision, 1);
});
test("failure preserves saved state and reconnect can reload", async () => {
  const state = new FlowRequests();
  await state.read(async () => ({ revision: 3 }));
  await assert.rejects(
    state.change(async () => {
      throw new Error("stale tab");
    }),
  );
  assert.equal(state.current.revision, 3);
  assert.equal(state.busy, false);
  await state.read(async () => ({ revision: 4 }));
  assert.equal(state.current.revision, 4);
  const slow = deferred(),
    pending = state.read(() => slow.promise);
  state.dispose();
  slow.resolve({ revision: 5 });
  assert.equal(await pending, undefined);
  assert.equal(state.current.revision, 4);
});
