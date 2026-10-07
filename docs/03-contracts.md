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

## CLI and API adapters

The implemented command reference is in [operations](37-operations.md#cli-authoring-and-review),
with detailed [asset](11-asset-registry.md), [preview](15-preview-workflow.md),
[audio](16-audio.md), [job](19-jobs.md), [cache](21-cache-storage.md) and
[release](23-release-preparation.md) guides. Run `tabi --help` or the relevant command's
`--help` for exact arguments. The former speculative command list has been removed.

The actual `/api/v1` routes and typed request/response boundaries are defined in
`src/tabi/api/app.py`, `workspace.py`, `uploads.py`, `preview.py`, `audio.py`, `production.py`,
`release.py`, `lofi.py` and `contracts.py`. The [service guide](25-local-service.md)
covers authenticated startup, media and worker lifecycle; the browser invokes these same
Python core services rather than constructing renderer commands.

Every mutation validates its current revision/hash and registered paths. Browser requests use
the verified session cookie with exact Host/Origin and CSRF checks; media ranges and SSE are
authenticated too. No secrets appear in media URLs. Frame ranges remain half-open and all
source references remain versioned. JSON CLI output goes to stdout, diagnostics to stderr.

## Implemented version-1 contract details (T03)

Python models in `src/tabi/core/models/` and transport contracts in `src/tabi/api/contracts.py`
are the source of truth. T38 records 64 published JSON Schemas; `make schemas` regenerates
`schemas/` and `make check` detects drift. All document roots require a supported
`schema_version` and `document_type`. Diagnostic reports are observations, not mutable drafts
or approved snapshots. The original T03 contract and persistence decisions below still apply.

Every nested model forbids unknown fields. Scalar time values are strict integers (booleans, strings and fractions are rejected); fps is a reduced positive rational. Curve keys use global frames and may include an end boundary for interpolation. Audio placements and fades use samples; the frame/sample conversion uses exact rational arithmetic with ties-to-even.

Media locations have `root_id` (default `project`) and a normalized relative POSIX `path`. Traversal, absolute/URL/drive paths, backslashes and control characters are rejected. Project `root` is `.` for portability; separately registered media roots are absolute local paths. The persistence layer additionally enforces filesystem/symlink containment. Scene slots, clips, actions and tracks use typed ID/version references rather than embedding renderer commands or uncontrolled paths.

Asset approval binds `content_sha256` to canonical document content excluding only `approval` and the draft `revision`; file hashes and metadata are part of that content. Edits invalidate the approval. Synthetic assets/snapshots cannot gain production approval. Unknown rights and release identifiers remain pending/null; structural validation cannot establish real rights or human review.

Canonical JSON v1 uses the validated model's JSON values, explicit defaults/nulls, sorted object keys, compact separators, UTF-8 and finite numbers. It is a project encoding rule, not a claim of RFC 8785 conformance. YAML is decoded safely, rejects duplicate/non-string keys, unsafe tags, anchors/aliases and non-finite values, and passes through the same JSON validation. Limits are 16 MiB and 64 nesting levels. In-memory models are field-frozen; persistence revalidates nested collections before writing.

Generated JSON Schema describes structural fields and nested types; Python additionally checks cross-field intervals, references, path normalization and approval hashes. A frontend must use the Python validation result for these semantics. Validation reports identify their scope as `structure` or, from T13, `compile`. The latter checks locked files and action compilation but does not certify final playback or creative quality. T13 adds the `compilation_result` document, bringing the current total to 22 published schemas.

## Implemented project persistence (T03)

`src/tabi/core/persistence.py` is shared by CLI and API services. `ProjectStore.initialize` creates a project index and standard folders only in a new/empty directory; `read` parses stored JSON through the strict contracts. Project roots remain portable (`.`). Saved episode files are authoritative; `AuthoringService` enumerates them rather than relying on a separately updated project episode index.

Draft storage is fixed by identity: `project.json`, `episodes/{id}.json`, `jobs/{id}.json`, `releases/{id}.json`, and `registry/{assets|templates|actions}/{id}/{version}.json`. Creation requires revision 0 and `expected_revision=None`. An edit requires both the submitted revision and expected revision to match the stored revision, then increments it. Project creation time is preserved and update time refreshed. An approved registry version cannot be overwritten, even by submitting a draft approval status; edits create a new version.

Every writer holds a nonblocking POSIX `flock` on `.tabi.lock`; contention fails explicitly. The lock file is persistent and must not be deleted to unlock a live project. Kernel locks release when the owning process exits. Metadata reads/writes use bounded relative paths, directory descriptors and `O_NOFOLLOW`; symlinked metadata folders/files are rejected. `resolve_media_path` accepts only caller-registered media roots and checks resolved containment; paths claimed by imported documents do not grant filesystem access. This is application containment, not a sandbox against other local processes that already have permission to modify the project.

Before replacing an existing draft, save its exact original bytes under `.backups/` with its relative path, revision and a unique suffix. Write the replacement to a same-directory temporary file, flush/fsync, reread/verify its bytes, then atomically replace the target and fsync its directory. New documents, backups and snapshots use atomic no-clobber hard-link publication followed by temporary-link removal. Failed writes before publication preserve the old target. Abrupt process exit can leave a hidden `.tmp` file, which is never selected as the current document; reopening uses the unchanged canonical path. No automatic backup or orphan pruning is implemented.

Snapshots live at `snapshots/{sha256}.json`, where the digest covers their complete canonical bytes. A repeated identical save does not rewrite the file; changed content creates a different path. Reads verify the filename digest and contract. An altered file is an error, never silently overwritten. No in-place snapshot migration is supported.

`MigrationRegistry` accepts explicit, forward, same-major transformations. `ProjectStore.migrate` checks revision, rejects approved documents, backs up exact source bytes before invoking a transformation, validates the target model/identity and publishes atomically. Transformation, validation and pre-publication I/O failures leave the source and backup intact. Production supports schema 1.0 only; a synthetic 1.1 model exercises the infrastructure in tests without claiming a historical migration exists.

Verified on this Mac's local filesystem, including process termination during a save. Whole-project transactions, backup restoration UX, network-filesystem semantics and power-loss durability are not verified by T03. A directory fsync failure after atomic publication may mean the new target is already visible; callers should reread its revision before retrying. Keep source media backups separately; this layer backs up documents, not artwork or music.

## Fixture manifest (T04)

The `fixture_manifest` document records the generator identity and hash, synthetic/publication flags, project and episode paths, and unique project-relative SHA-256/size records. T04 brings the generated schema count to 17. A fixture manifest is reproducibility evidence, never production approval.

## Reusable lo-fi scenes (L02)

`lofi_scene` is a strict versioned registry document at `registry/lofi/<id>/<version>.json`.
It holds a still master, rational fps, optional window mask, up to three scrolling scenery
layers and up to eight aligned transparent PNG overlays. Loop source ranges, repeat intervals
and first-frame offsets are integer frames; gaps reveal the unchanged master.

`SaveLofiScene` accepts optional per-overlay seconds as transport convenience. Python rounds
those using the rational fps and validates the resulting complete intervals before atomic save.
`CreateLofiVideo` accepts whole duration seconds or null to fit complete selected music samples.
It validates and compiles before the episode is first persisted. The resulting content-addressed
template leaves already-created episodes unchanged when the scene draft changes.

The authenticated `/api/v1/projects/{handle}/lofi` catalog, `/lofi/scenes` save and `/lofi/videos`
create endpoints use `LofiService`, as do the CLI adapters. Retired generation documents in
older external projects are not in the executable schema registry; no worker resumes them.
