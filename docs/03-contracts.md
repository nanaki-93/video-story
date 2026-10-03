# Data contracts and application interfaces

## Versioning and units

Every top-level document has `schema_version` such as `1.0`. Reject unknown major versions; migrate supported minor versions explicitly. Treat additional unknown fields as validation errors unless they belong to a documented extension object. Author YAML if desired, normalize to canonical JSON in snapshots. Never hash YAML formatting.

Timeline values are integer frames at `fps.num/fps.den`. V1 default is exactly 30/1 fps. Frame intervals are half-open `[start_frame,end_frame)`. Frame zero is the episode origin; the final frame index is `duration_frames - 1`. Audio positions are integer samples at 48000 Hz. Convert boundary frame `n` to sample using a documented rounding rule, `round(n * sample_rate * fps.den / fps.num)`, with ties-to-even. Use integer/rational arithmetic, not cumulative floating-point additions.

Spatial positions and pivots are pixel coordinates in a documented design canvas, origin top-left. Opacity is 0–1. Speed uses design pixels/second, gain uses dB, rotations use degrees. Scaling from design canvas to output resolution is uniform with an explicit crop/letterbox policy.

## Required models

| Model | Fields and constraints |
| --- | --- |
| Project | ID, title, schema version, project root, registered media roots, created/updated, episode IDs |
| Asset | Stable ID/version, kind, source/proxy paths, hashes, probe data, rights/approval, compatibility |
| Action | ID/version, channel, start/end pose, loop range or one-shot, clip reference, required/resulting props, camera/template pack |
| SceneTemplate | ID/version, design canvas, ordered layer slots, masks, character anchors, supported channels/effects, parameter limits |
| Episode | ID/title/format, fps, canvas, duration, seed, scenes, tracks, actions, curves, continuity, asset lock references |
| SceneInstance | ID, template version, interval, slot assignments, anchor selection, initial state, scoped curves and events |
| TrackPlacement | Track asset/version, start sample, trim start/end sample, gain, fade intervals, release metadata reference |
| ActionRequest | Scene ID, action ID/version, desired start frame, repeat policy, channel and explicit conflict behavior |
| Curve | Scope, target, ordered frame/value keys, interpolation mode, domain limits |
| CompiledSnapshot | Canonical episode, locked hashes, expanded schedule, absolute placements, compiler/version fingerprint |
| RenderJob | ID, snapshot hash, output profile, backend fingerprint, state, chunk ledger, progress/error/report paths |
| ReleaseRecord | Artist/title, track credits, known ISRC/UPC, rights status, platform links, disclosure and claim notes |

Examples in `examples/` illustrate these models. The implementing agent must produce schemas for the entire nested structure and schema-validation tests; this plan does not substitute a partially specified example for a contract.

## Validation rules

Check missing assets, duplicate IDs, version mismatch, unapproved production inputs, incompatible camera/action packs, invalid paths, corrupt media, unsupported color/alpha/fps, insufficient loop frames, masks/canvas mismatch, out-of-range crop, uncovered scene intervals, unintended overlapping scenes, action channel conflicts, invalid pose transitions, props missing or appearing without an event, weather/lighting discontinuity, track truncation, silent gaps and render profile feasibility.

Validation has `error`, `warning`, `info` severities with code, location, message and suggested fix. Structural errors block compilation. Draft assets can render with a preview-only flag; final export may also be produced as a draft, but cannot gain publish-ready status. Creative issues are review warnings; they cannot be automatically certified.

Use explicit scene transitions: a cut or an authored overlap. Reject accidental gaps. If both scenes have Tabi, use a cut or an approved matched character transition; blindly dissolving two character poses is not valid continuity.

## State and continuity

State includes body pose, facial overlay, props/locations, cabin light, weather phase and accumulated travel distance. Body actions are exclusive per scene character; blink may overlap body actions only when the action pack says it is compatible. One-shot actions end once and change state. Loop actions maintain their phase through chunk boundaries.

Within a scene, planner inserts only transitions that exist in the approved action graph. If no transition exists, validation fails with the missing edge. Across scenes, initial/final states must agree or a deliberate cut/reset is declared. Episode continuity notes capture persistent story objects (postcard, ticket, sketchbook) without pretending to track every physical property automatically.

Randomization is limited to optional idle/blink timing within approved ranges. Store the seed, PRNG algorithm/version and the expanded scheduled events. Recompiling the same inputs must produce the same schedule. Export uses the frozen schedule, not a newly randomized one.

## CLI specification

| Command | Behavior |
| --- | --- |
| `tabi doctor --json` | Probe runtime, tools, codecs, storage, target features |
| `tabi project init PATH` | Create safe local project folder with versioned defaults |
| `tabi assets import --project PATH --file FILE --kind KIND` | Register original, probe, copy or link explicitly |
| `tabi assets approve --project PATH --id ID --version VERSION` | Record user-reviewed approval with hashes |
| `tabi validate EPISODE --report FILE` | Structured validation; no rendering |
| `tabi compile EPISODE --output SNAPSHOT` | Resolve versions and expand schedule |
| `tabi preview SNAPSHOT --range START:END --profile proxy` | Render global-frame range; placeholders are labeled |
| `tabi frame SNAPSHOT --frame N --output PNG` | Exact frame inspection |
| `tabi render SNAPSHOT --profile youtube-1080 --output MP4` | Persist job and render asynchronously or wait by flag |
| `tabi jobs status JOB_ID --json` | Return journal state and verified artifact paths |
| `tabi jobs cancel JOB_ID` | Cancel owned job safely |
| `tabi jobs resume JOB_ID` | Check fingerprints and resume valid chunks |
| `tabi release prepare JOB_ID --output DIR` | Release preparation; never upload |
| `tabi cache prune --project PATH --dry-run` | Show disposable entries and reclaim estimate |

Frame ranges use the same half-open convention. CLI exit codes: 0 success, 2 validation/usage, 3 missing dependency, 4 render/I/O failure, 5 cancellation. JSON output goes to stdout; logs to stderr. Avoid embedding secrets or private licence files in logs.

## Local service API

Proposed routes, versioned under `/api/v1`:

- `GET /health`, `GET /capabilities`: protocol/runtime state and tool support.
- `POST /projects/open`, `GET /projects/{id}`, `PUT /projects/{id}`: opened projects with revision guard.
- `GET /projects/{id}/assets`, `POST /projects/{id}/assets/import`, `POST /assets/{id}/normalize`, `POST /assets/{id}/approve`.
- `GET /episodes/{id}`, `PUT /episodes/{id}` with expected revision; `POST /episodes/{id}/validate`, `/compile`.
- `POST /previews` and `POST /renders`: return job ID and frozen input hash.
- `GET /jobs/{id}`, `POST /jobs/{id}/cancel`, `/resume`; `GET /jobs/{id}/events` as server-sent events.
- `GET /artifacts/{id}` serves only registered job artifacts within approved roots, supports range requests for proxy playback.
- `POST /releases/prepare`: return folder and validation report.

Requests use typed bodies; long jobs return immediately. Job errors include stable code, user message and diagnostic log reference. Every edit uses a project/episode revision to prevent lost updates. API payloads refer to registered asset IDs, not arbitrary shell arguments. The worker token is required even on loopback.
