# Global frame evaluation

T09 provides `Timeline` and `CurveEvaluator` for independent frame queries. Every interval is half-open; frame `duration_frames` is an integration boundary, not a displayable frame. Frame/sample conversion uses exact rational arithmetic and ties-to-even rounding. `loop_frame` takes an explicit global phase origin and a source loop interval, so seeking never restarts a clip.

```sh
.venv/bin/tabi timeline inspect .local/fixtures-v1/episodes/episode.synthetic.json --frame 151
.venv/bin/tabi timeline expand /path/to/episode.json
```

`inspect` reports rational seconds, the exact 48 kHz sample boundary, active scene IDs, curve values and travel distance. It is semantic inspection, not a rendered preview.

Curve keys are global frames. Constant curves hold the left key until the next key; linear curves interpolate between adjacent keys. `outside: clamp` holds the first/last values; `zero` is zero strictly outside the first/last key. The value at the final key is still that key's value; this isolated endpoint adds no integration area. A one-key zero-outside curve therefore has zero integral.

Travel distance integrates speed analytically: constant rectangles or linear trapezoids, with a rational prefix-area table. Decimal JSON values are interpreted as exact decimal rationals before integration. No per-frame float sum or current-speed-times-elapsed-time approximation is used. A scene's explicit initial travel distance is added to its scoped integral. The state compiler supplies a preserved base across cuts in T10; callers can pass that base without changing curve semantics.

A scene-specific curve overrides the episode curve for its entire interval. A duplicated `(scope,target)` fails, including duplicates spread between the episode and scene lists. Unknown scene scopes, out-of-range keys, reverse travel and incorrect travel-speed units fail. A renderer must additionally compare parameters against template capabilities.

Optional `random_actions` describe a scene, pack/action version, channel, interval, duration, and inclusive minimum/maximum gaps in frames. Timing uses the episode seed and a separate stream for each request ID. `tabi-sha256-counter` version 1 hashes canonical UTF-8 JSON objects containing `domain`, `version`, `seed`, `id` and `counter`. Digest integers are big-endian. Rejection sampling avoids modulo bias. The first gap follows the requested start; each subsequent gap follows the previous action's end. Only whole actions fitting inside the interval are emitted.

Manual/random channel collisions are errors. Random expansion never silently drops conflicts or invents compatible poses; the action compiler validates those. Expanded IDs are deterministic and schedules are sorted canonically. The frozen snapshot records both the PRNG fingerprint and the expanded schedule; rendering never rerolls it. Compilation caps expansion at 100,000 actions.

Verification: [T09 task](archive/v1-tasks.md#t09) and [measured synthetic frame/schedule report](evidence/t09-timeline.json). Tests cover exact area through acceleration/stop/restart, out-of-order queries, interval additivity at every split, a noninteger frame rate, ties-to-even samples, scope precedence, duplicate rejection and a fixed random reference vector independently checked with OpenSSL.

## Action compiler (T10)

`ActionCompiler(AssetService(store), purpose="synthetic_test").compile(episode)` resolves registry media and returns a strict `CompiledSnapshot`. `state_at(snapshot, scene_id, frame)` returns active clip/source frames, body pose, props and travel. The compiler records every transitive template/pack/clip/media hash plus its implementation and PRNG fingerprints. Preview/production CLI adapters enter with the renderer in T13.

A loop request describes a complete window. If its start pose differs from current state, the compiler searches that pack's directed one-shot graph for a route with satisfied prop requirements, inserts the entry clips, fills the hold with whole loop cycles, and returns to the prior pose. `return_pose` can explicitly choose another final pose. A one-shot defaults to its authored end pose and must fit exactly once; it cannot be silently stretched. Transition search uses fewest clips, ordered by action ID for deterministic ties. Inserting explicit transition requests gives the author direct control when several routes exist.

Body requests cover the entire character scene. Whole loops end at reviewed pose boundaries; an incompatible window fails with the remaining frame count. Prepared clip frame count, fps, canvas, alpha, camera, declared channel and optional anchor/template restrictions must match the pack and scene. Face overlays declare compatible held body poses and cannot overlap a body clip occupying the face channel. They cannot move props. A blink never restarts the body loop.

Prop results apply at an action's exclusive end boundary. Explicit prop events at the same frame apply after completed action results and before new action precondition checks. Independent frame inspection replays only these finite scheduled state changes. The body pose during a transition remains its start-pose label until the end; the active prepared clip supplies the actual moving pixels.

For cuts with `continuity: preserve`, the next declared initial state must match the previous compiled final state, including distance, props and weather phase origin. A deliberate change needs `deliberate_reset`. Declared final states are checked against compiled results. The compiler currently rejects scene overlaps; T18 supplies their explicit semantics. Historical snapshots stay unchanged when a draft is edited.

Production compilation requires actual hash-bound asset/pack/template approval and rights. `synthetic_test` requires synthetic source media and never permits production approval. [T10 evidence](evidence/t10-compiled-state.json) is a synthetic semantic verification only; actual Tabi motion/transition approval remains T07/T14.
