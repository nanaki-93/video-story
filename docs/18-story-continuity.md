# Story beats and scene transitions

T18 adds authored scene purposes, frame-based story beats linked to real music placements, and an object notebook. `tabi story inspect SNAPSHOT_SHA --project ROOT` reads a frozen snapshot and reports missing scene/cut intent, missing intent at each music start/end, and undeclared persistent objects. These are editorial warnings, not an assertion of creative approval. Beat IDs, scene intervals, music links and notebook identities are validated by the shared contracts.

Cuts retain explicit `preserve` or `deliberate_reset` continuity. During an overlap the incoming initial state must match the outgoing scene **at the incoming start frame**, before the outgoing scene ends. Both scene contracts declare the same duration and purpose. No gaps, containment or three-way overlaps are accepted.

Supported overlap policies:

- `matched`: both scenes have exactly one character. `match_action` identifies the prepared clip asset, not the action pack. Body and face source frames, loop phases, pose/prop state, anchor placement, canvas, framing, camera, opacity and mask must agree across the complete overlap. State resets and incompatible poses fail with a diagnostic. This conservative rule supports scenery dissolves around one unchanged character; it does not infer matching between different drawings.
- `single_visible`: at most one of the scenes contains a character. The whole scene fades into or out of an environment. Use a cut or a proven matched clip for transitions between two character scenes.

The blend is linear in composed RGB, with weights 0 and 1 on the first and last overlapping frames. Duration must be at least two frames. Global progress is preserved when inspecting a still or rendering a range starting inside the overlap. Spatial compositing needs no temporal handles. Artistic transitions and light/weather changes still require visual review.

## Synthetic verification

Generate a fresh demonstration with `tabi fixtures --profile story --output ROOT`. Its 300-frame, 30 fps story overlaps at frames `[144,180)`. Two parallax arrangements share the same idle character; the table remains in the notebook and both scenes. Three beats explain departure, handover and resolution against the owned test signal.

The saved example is `.local/t18-story`, with snapshot `70aa12354f2e2adeeaa92f75252908782575706b2daa6c449ed17b28cb8b94e4`. [Storyboard](evidence/t18-storyboard.json), [inspected frame 162](evidence/t18-story-frame-162.png), [still report](evidence/t18-still-report.json) and [preview report](evidence/t18-preview-report.json) retain actual evidence. The ignored `.local/t18-story-verified.mp4` contains 300 verified video frames and 480,000 decoded stereo AAC samples. Render/mix/mux took 4.877 seconds on the development M5 Pro with concurrent tests; this is not a controlled performance benchmark.

Thirteen unit cases cover overlap-entry state, divergent phase/geometry/facial/prop state, incorrect match clips, single-character policy, dangling story metadata, editorial warnings and scoped curve overrides. Actual media tests compare fourteen stills against independent Pillow compositions (at most three RGB levels) and compare overlapping video ranges after BT.709/4:2:0 conversion (99.9th-percentile error at most 15; range-to-range at most 10). The latter conversion is necessary for saturated edges in a lossy delivery format. Source approval cannot be inferred from these fixtures.

Remaining T18 acceptance: Marco's real story outline, finished music, approved separated artwork and review of the resulting narrative/transition intent. T19's publishable 5–10-minute story cannot be completed with these placeholders.
