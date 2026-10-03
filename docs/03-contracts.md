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
| `tabi --version`, `tabi config --json` | T01: application version and resolved local developer settings; no media probing |
| `tabi web` | T26: launch authenticated local web app, register configured roots, verify worker readiness and open browser |
| `tabi doctor --json [--output-dir PATH]` | T02: probe runtime/tools, listed filters/encoders and writable storage; no rendering |
| `tabi render-spike --output-dir PATH [--encoder ENCODER] [--json]` | T02: render/verify a fixed synthetic ten-second scene and save per-run evidence |
| `tabi project init PATH --title TITLE [--json]` | T03: create a safe local project folder with versioned defaults |
| `tabi project show PATH [--json]` | T03: reopen and inspect the saved project index |
| `tabi document validate FILE` | T03: validate JSON/YAML structure and print a JSON report; no media probing |
| `tabi assets import --project PATH --file FILE --kind KIND` | Register original, probe, copy or link explicitly |
| `tabi assets approve --project PATH --id ID --version VERSION` | Record user-reviewed approval with hashes |
| `tabi validate EPISODE --project PATH [--purpose PURPOSE]` | T13: structured compiler validation; no rendering |
| `tabi compile EPISODE --project PATH [--output NEW_JSON]` | T13: resolve versions, expand schedule and save immutable snapshot |
| `tabi preview SNAPSHOT_SHA --project PATH --start N --end N --output MP4` | T13: render global-frame range; placeholders are labeled |
| `tabi frame SNAPSHOT_SHA --project PATH --frame N --output PNG` | T13: exact frame inspection |
| `tabi snapshot show/review SNAPSHOT_SHA --project PATH` | T13: inspect frozen content or record an explicit hash-bound review |
| `tabi render SNAPSHOT --profile youtube-1080 --output MP4` | Persist job and render asynchronously or wait by flag |
| `tabi jobs status JOB_ID --json` | Return journal state and verified artifact paths |
| `tabi jobs cancel JOB_ID` | Cancel owned job safely |
| `tabi jobs resume JOB_ID` | Check fingerprints and resume valid chunks |
| `tabi release prepare JOB_ID --output DIR` | Release preparation; never upload |
| `tabi cache prune --project PATH --dry-run` | Show disposable entries and reclaim estimate |

Frame ranges use the same half-open convention. CLI exit codes: 0 success, 2 validation/usage, 3 missing dependency, 4 render/I/O failure, 5 cancellation. JSON output goes to stdout; logs to stderr. Avoid embedding secrets or private licence files in logs.

Commands with task IDs above are implemented. The T05 asset commands use singular `tabi asset`; their exact syntax is in [asset registry](11-asset-registry.md). T13 syntax, snapshot review requirements and limits are in [preview workflow](15-preview-workflow.md). The remaining commands describe planned behavior and are not exposed as placeholders. `render-spike` remains a bounded capability test.

## Local service API

Proposed routes, versioned under `/api/v1`:

- `POST /session`: exchange one-time browser bootstrap secret; authenticated `GET /session` returns protocol and CSRF context for reconnect.
- `GET /roots`, `GET /roots/{id}/entries`: browse only launcher-registered local roots, with normalized relative paths and traversal/symlink checks.
- `GET /health`, `GET /capabilities`: protocol/runtime state and tool support.
- `POST /projects/open`, `GET /projects/{id}`, `PUT /projects/{id}`: opened projects with revision guard.
- `GET /projects/{id}/assets`, `POST /projects/{id}/assets/import`, `POST /assets/{id}/normalize`, `POST /assets/{id}/approve`.
- `GET /episodes/{id}`, `PUT /episodes/{id}` with expected revision; `POST /episodes/{id}/validate`, `/compile`.
- `POST /previews` and `POST /renders`: return job ID and frozen input hash.
- `GET /jobs/{id}`, `POST /jobs/{id}/cancel`, `/resume`; `GET /jobs/{id}/events` as server-sent events.
- `GET /artifacts/{id}` serves only registered job artifacts within approved roots, supports range requests for proxy playback.
- `POST /releases/prepare`: return folder and validation report.

Requests use typed bodies; long jobs return immediately. Job errors include stable code, user message and diagnostic log reference. Every edit uses a project/episode revision to prevent lost updates. API payloads refer to registered asset IDs, not arbitrary shell arguments. Authentication is required even on loopback: ephemeral bearer tokens for CLI clients, or the verified session cookie for browsers, including video range and SSE requests. Browser mutations also require exact Origin/Host validation and a CSRF header. No credentials in artifact URLs. The full bootstrap and root-access policy is specified in [architecture](02-architecture.md).

## Implemented version-1 contract details (T03)

Python models in `src/tabi/core/models/` are the source of truth. T03 introduced 14 Draft 2020-12 schemas under `schemas/`. Nine domain root types require `schema_version: "1.0"` and `document_type`: project, asset, action_pack, scene_template, episode, compiled_snapshot, render_job and release_record, plus validation_report. Five schemas describe nested action, scene_instance, track_placement, action_request and curve values. T02 adds `capability_report` and `render_spike_report`, for 16 schemas in total; `make schemas` publishes them and `make check` detects drift. Diagnostic reports are observations, not mutable project drafts or approved snapshots.

Every nested model forbids unknown fields. Scalar time values are strict integers (booleans, strings and fractions are rejected); fps is a reduced positive rational. Curve keys use global frames and may include an end boundary for interpolation. Audio placements and fades use samples; the frame/sample conversion uses exact rational arithmetic with ties-to-even.

Media locations have `root_id` (default `project`) and a normalized relative POSIX `path`. Traversal, absolute/URL/drive paths, backslashes and control characters are rejected. Project `root` is `.` for portability; separately registered media roots are absolute local paths. The persistence layer additionally enforces filesystem/symlink containment. Scene slots, clips, actions and tracks use typed ID/version references rather than embedding renderer commands or uncontrolled paths.

Asset approval binds `content_sha256` to canonical document content excluding only `approval` and the draft `revision`; file hashes and metadata are part of that content. Edits invalidate the approval. Synthetic assets/snapshots cannot gain production approval. Unknown rights and release identifiers remain pending/null; structural validation cannot establish real rights or human review.

Canonical JSON v1 uses the validated model's JSON values, explicit defaults/nulls, sorted object keys, compact separators, UTF-8 and finite numbers. It is a project encoding rule, not a claim of RFC 8785 conformance. YAML is decoded safely, rejects duplicate/non-string keys, unsafe tags, anchors/aliases and non-finite values, and passes through the same JSON validation. Limits are 16 MiB and 64 nesting levels. In-memory models are field-frozen; persistence revalidates nested collections before writing.

Generated JSON Schema describes structural fields and nested types; Python additionally checks cross-field intervals, references, path normalization and approval hashes. A frontend must use the Python validation result for these semantics. Validation reports identify their scope as `structure` or, from T13, `compile`. The latter checks locked files and action compilation but does not certify final playback or creative quality. T13 adds the `compilation_result` document, bringing the current total to 22 published schemas.

## Implemented project persistence (T03)

`src/tabi/core/persistence.py` is shared by CLI and future services. `ProjectStore.initialize` creates a project index and standard folders only in a new/empty directory; `read` parses stored JSON through the strict contracts. Project roots remain portable (`.`). Saving an episode does not implicitly alter the project's episode index; a future service owns that coordinated operation.

Draft storage is fixed by identity: `project.json`, `episodes/{id}.json`, `jobs/{id}.json`, `releases/{id}.json`, and `registry/{assets|templates|actions}/{id}/{version}.json`. Creation requires revision 0 and `expected_revision=None`. An edit requires both the submitted revision and expected revision to match the stored revision, then increments it. Project creation time is preserved and update time refreshed. An approved registry version cannot be overwritten, even by submitting a draft approval status; edits create a new version.

Every writer holds a nonblocking POSIX `flock` on `.tabi.lock`; contention fails explicitly. The lock file is persistent and must not be deleted to unlock a live project. Kernel locks release when the owning process exits. Metadata reads/writes use bounded relative paths, directory descriptors and `O_NOFOLLOW`; symlinked metadata folders/files are rejected. `resolve_media_path` accepts only caller-registered media roots and checks resolved containment; paths claimed by imported documents do not grant filesystem access. This is application containment, not a sandbox against other local processes that already have permission to modify the project.

Before replacing an existing draft, save its exact original bytes under `.backups/` with its relative path, revision and a unique suffix. Write the replacement to a same-directory temporary file, flush/fsync, reread/verify its bytes, then atomically replace the target and fsync its directory. New documents, backups and snapshots use atomic no-clobber hard-link publication followed by temporary-link removal. Failed writes before publication preserve the old target. Abrupt process exit can leave a hidden `.tmp` file, which is never selected as the current document; reopening uses the unchanged canonical path. No automatic backup or orphan pruning is implemented.

Snapshots live at `snapshots/{sha256}.json`, where the digest covers their complete canonical bytes. A repeated identical save does not rewrite the file; changed content creates a different path. Reads verify the filename digest and contract. An altered file is an error, never silently overwritten. No in-place snapshot migration is supported.

`MigrationRegistry` accepts explicit, forward, same-major transformations. `ProjectStore.migrate` checks revision, rejects approved documents, backs up exact source bytes before invoking a transformation, validates the target model/identity and publishes atomically. Transformation, validation and pre-publication I/O failures leave the source and backup intact. Production supports schema 1.0 only; a synthetic 1.1 model exercises the infrastructure in tests without claiming a historical migration exists.

Verified on this Mac's local filesystem, including process termination during a save. Whole-project transactions, backup restoration UX, network-filesystem semantics and power-loss durability are not verified by T03. A directory fsync failure after atomic publication may mean the new target is already visible; callers should reread its revision before retrying. Keep source media backups separately; this layer backs up documents, not artwork or music.

## Fixture manifest (T04)

The `fixture_manifest` document records the generator identity and hash, synthetic/publication flags, project and episode paths, and unique project-relative SHA-256/size records. T04 brings the generated schema count to 17. A fixture manifest is reproducibility evidence, never production approval.
