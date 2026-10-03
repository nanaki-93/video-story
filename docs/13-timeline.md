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

Verification: [T09 task](tasks/t09.md) and [measured synthetic frame/schedule report](evidence/t09-timeline.json). Tests cover exact area through acceleration/stop/restart, out-of-order queries, interval additivity at every split, a noninteger frame rate, ties-to-even samples, scope precedence, duplicate rejection and a fixed random reference vector independently checked with OpenSSL.
