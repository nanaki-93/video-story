# Implementation progress

Updated 3 October 2026 (Asia/Manila). This is a task/acceptance record, not a production approval. Each verified implementation step is committed separately with its task ID.

## T01 — complete

Delivered the `tabi-story-studio` Python package and `tabi` entry point, help and version, strict versioned TOML developer settings, explicit config/environment precedence, normalized Unicode/space-containing paths and JSON diagnostics on stderr. Config inspection does not create directories or run tools. Unknown fields/versions, invalid types and missing explicit files fail with exit code 2. Project/episode schemas and persistence remain T03.

Added `pyproject.toml`, `uv.lock`, `.python-version`, real Makefile setup/check/test targets, unit tests and the test-layout documentation. No stub renderer, HTTP server or UI was exposed. Runtime settings currently use Python's standard library; the audit dependency group contains Pillow.

Verification performed:

- `make check`: Ruff lint/format passed; **18 tests passed** (CLI stream separation, config precedence, invalid inputs, relative/Unicode paths and no-write behavior).
- `UV_PROJECT_ENVIRONMENT=.local/t01-fresh-env .tools/bin/uv sync --frozen --group audit`: fresh virtual environment installed successfully from the lock.
- Fresh-environment `tabi --help`, `tabi --version`: passed, version **0.1.0**.
- `.local/t01-fresh-env/bin/python -m pytest`: **18 passed**.

Machine: Apple M5 Pro, arm64, macOS 27.0.1 (26A434). Tools: Python 3.11.16, uv 0.11.0, pytest 9.1.1, Ruff 0.16.10, Pillow 12.3.0; build backend Hatchling 1.27.0. The lock records transitive package versions. These are tested versions, not a claim that every dependency is the newest available.

Representative output: `tabi 0.1.0`; `tabi config --json` reports resolved paths and tool names without claiming those executables exist. No UI screenshot or rendered clip applies to this bootstrap task.

## Documentation and supplied asset review — complete

Updated the plan/specifications and browser tasks for a local web app replacing Kotlin/Compose. Reviewed all specifications, all 38 task documents, examples and review templates. The [review](09-implementation-review.md) records architecture tradeoffs, asset readiness and the revised first-task order.

All 322 media files were hashed; all 317 images decoded; PNG sequences cover 1–97 and 1–129 with no gaps. Reviewed all image contact sheets and sampled each video. All five videos decoded completely through native AVFoundation (1,887 frames total), with no audio tracks. Detailed evidence is in [asset-inventory.json](asset-inventory.json) and [asset-video-audit.json](asset-video-audit.json). Video audit script and derived contact sheets remain local under `.local/asset-audit/`. This is technical source inspection, not a T02 renderer integration test or artistic approval.

Five staged MP4 additions were removed from Git's index, preserving local files. The ignore pattern covers case variants and the rule is recorded in AGENTS.md. The pre-existing staged IDE files were left intact.

Final repository checks: all 56 reviewed Markdown files have valid local links;
the 38-task dependency graph is acyclic and index/task statuses agree;
`git diff --check` passed. `git ls-files` contains zero MP4 paths,
`git check-ignore --stdin` accepted all four tested capitalization variants,
and a final SHA-256 pass matched all 322 original inventory entries. All five
local MP4 files remain present.

## T03 — complete

Bootstrap committed as `e5ae06b` (`T01: bootstrap Python core and plan local web app`).
The contracts step is committed as `8551cf2` (`T03: define strict contracts and publish JSON schemas`). Persistence is committed separately as `T03: persist projects atomically with revision and migration guards`.

Implemented all required nested model families, nine root document types and 14 generated JSON Schemas. Added strict scalar/version/field checks, canonical JSON, safe YAML with duplicate/alias/tag rejection, hash-bound approvals, rational frame/sample boundaries and structural scene/action/audio/snapshot validation. All five example documents now validate; the two-pixel fixture is synthetic and has a real recorded hash. Media existence, compiler behavior and artistic approval remain separate future gates.

Step 1 verification: `make schemas && make check` generated/checked 14 schemas; Ruff passed; **81 tests passed**. Runtime dependencies added and locked: Pydantic 2.13.5 and PyYAML 6.0.3; jsonschema 4.26.0 is a development verification dependency.

Step 2 implements `ProjectStore`: safe initialization and strict reopening, revision-checked atomic draft saves, exact-byte backups, a persistent POSIX writer lock, symlink/path containment, hash-addressed immutable snapshots and explicit migration infrastructure. Approved versions require a new version to edit; migrations back up before transformation and cannot alter approved documents/snapshots in place. CLI creation, inspection and structural validation use those same services.

Final verification:

- `make check`: Ruff lint/format and all 14 schema drift checks passed; **108 tests passed** on the same M5 Pro/Mac/Python environment recorded above.
- Failure-injection tests preserve original documents and backups after transform, validation, rename, flush or verification errors. A spawned writer terminated immediately before publication leaves the old project readable; a subsequent writer succeeds. A separate process-lock test verifies contention and kernel lock release after exit.
- Snapshot tests verify idempotent saves, changed-content identities, tamper detection and immutable-version guards. Storage tests reject traversal and symlink escapes without touching outside targets.
- Installed CLI smoke: project initialization and reopening produced identical JSON; validation returned `valid: true`, `scope: structure`. Reports live locally in `.local/t03-cli-smoke-ebp0oi21/`; the project path contains spaces, an apostrophe and Japanese characters. CLI tests also cover safe repeated initialization, missing files and useful nested-field errors.
- Repository checks: all 58 Markdown files have valid local links; all 38 task statuses match the index; `git diff --check` passed. No MP4 is tracked, all five local clips remain present and all four tested extension capitalization variants are ignored. Unrelated staged IDE files remain excluded from implementation commits.

Known limits: no network-filesystem or power-loss guarantee; whole-project transactions, backup restoration UI and automatic backup/temp pruning remain later work. A killed writer may leave an unused `.tmp` file. Schema 1.0 is the first production format, so no historical migration is registered; test-only 1.1 contracts exercise the migration infrastructure. These storage checks do not establish rendering or art approval.

## T02 — complete; M0 acceptance passed

Step 1 (`5d48ed2`, `T02: add local toolchain doctor and capability reports`) implements `tabi doctor --json` / `make doctor`, typed machine/capability reports, executable hashes, matching tool versions and writable-storage checks. Its 120 tests passed. FFmpeg/ffprobe 9.0.2 were installed externally through Homebrew; the [Mac settings example](../examples/settings.macos.toml) selects those exact Cellar paths. The [machine report](evidence/t02-doctor-m5-pro.json) records this M5 Pro/48 GiB and explicitly distinguishes listed encoders from verified renders.

Step 2 (`T02: verify synthetic rendering with software and VideoToolbox`) adds the fixed ten-second render experiment, explicit color/alpha handling, output verification and `tabi render-spike`. It checks a moving numbered exterior through a window mask, straight-alpha rectangle entry/exit, foreground occlusion and an owned stereo tone. Inputs and preview are visibly synthetic; no supplied artwork or music is used. MP4 publication occurs only after media verification, without clobbering existing exports.

Final evidence:

- `make check`: lint/format and 16 schemas passed; **122 tests passed**, seven opt-in media tests skipped. `make test-media`: **seven passed**, no skips on this Mac. Together these cover 129 tests.
- Both libx264 and H.264 VideoToolbox (software fallback disabled) fully decode: 300 frames at 30/1 fps, ten seconds, 960×540, tagged BT.709 YUV420P, stereo 48 kHz AAC and 480,000 decoded audio samples.
- Eleven sampled frames verify 110 pixel positions and 97 scrolling boundaries. Maximum RGB-channel errors are 2 (software) and 3 (hardware), within 12; motion displacement error is zero pixels. Audio RMS/tone-energy checks pass in both channels.
- Real negative renders with inverted mask, incorrect alpha metadata, early clip entry or wrong restart speed fail verification. Truncation fails; injected verification failure never publishes a final file or overwrites an existing export.
- Pinned-config CLI renders succeeded through paths containing spaces, an apostrophe and Japanese characters. Reports retain machine, executable/input/graph/output identities. Software and hardware frame 90 were visually inspected; masks, translucent borders, occlusion and permanent synthetic labels are clear.
- Final repository audit: all 59 Markdown files have valid local links; all 38 task statuses match. Three machine reports pass Python/JSON Schema validation; both media hashes match disk and both encoders used identical input/graph hashes. `git diff --check` passes, no MP4 is tracked and the five original local clips remain present. Unrelated staged IDE files remain excluded.

Reproduction, reports and committed PNG evidence: [T02 toolchain checks](10-toolchain.md). Local MP4 paths are recorded in the [software](evidence/t02-software-m5-pro.json) and [hardware](evidence/t02-hardware-m5-pro.json) reports. Measured render subprocess times are 0.515/0.613 seconds for this simple proxy only, excluding generation/verification. These do not establish real-scene 1080p/4K performance or hardware filtering.

M0 now meets its gate: pinned Python dependencies and tested external media build, CLI, strict schemas/persistence, actual tool capabilities and synthetic media verification. No production/art approval follows.

## T04 — complete

`T04: generate reproducible synthetic fixture projects` adds `tabi fixtures --output PATH`, `make fixtures` and the strict fixture-manifest contract (17 schemas total). A generated project has 14 draft synthetic assets: original geometric cabin, window mask, foreground, tiled depth strips, a one-time landmark, fixed-canvas idle/observe/entry/exit/blink sequences, stereo tone/silence, registry records and a ten-second authored episode. Body/face channels, transition poses, anchors, travel speed changes and sample counts are explicit. Fixed timestamps are test sentinels, not production provenance.

Verification: `make schemas && make check` passed Ruff and schema drift with **126 tests passed**, seven opt-in T02 media tests skipped. Tests decode actual PNG/WAV files, inspect mask/alpha and loop/transition endpoints, and compare all bytes from two independently generated Unicode/space/apostrophe projects. Refusing occupied output and injected generation failure both preserve source data. The installed CLI generated `.local/fixtures-v1`: **69 hashed files, 2,173,410 bytes**. [Manifest](evidence/t04-fixtures-manifest.json) and [visually inspected action contact sheet](evidence/t04-fixture-actions.png) are committed evidence; generated source media stays local. Machine/runtime as above, with Pillow 12.3.0 now a runtime dependency.

This completes reusable fixtures, not episode rendering or art approval. No MP4 is added. Unrelated staged IDE files remain excluded.

## T05 — complete

`T05: import and verify immutable asset versions` adds the shared asset registry and CLI import/list/show/check/relink/proxy/approve commands. Copy import preserves exact originals; linked files use explicitly trusted roots. Pillow, PCM WAV reads and ffprobe plus strict full FFmpeg decode inspect real inputs. Ordered sequences require an explicit rational fps and consistent frames. New proxy/relink versions start as drafts. Hash checking makes changed or missing media unusable and invalidates effective approval while retaining the immutable historical review record. Rights remain pending unless supplied; no actual artwork or music was approved.

Verification: 19 schema checks, Ruff and **137 unit/contract tests passed**; the new actual-media integration test also passed at 30000/1001 fps and rejected a truncated MP4. Tests exercise source preservation, missing roots/files, Unicode paths, stale review hashes, relinking exact bytes, transparent PNG proxies, inconsistent sequence frames and disk-full injection. Installed CLI import/proxy/check succeeded in `.local/t05-registry-check/Marco 東京 project`; [health evidence](evidence/t05-asset-health.json) records valid source/proxy hashes, pending rights and no publication approval. No MP4 is tracked; staged IDE files remain excluded.

Known limits and reproduction: [asset registry](11-asset-registry.md). Long compressed audio is intentionally not assigned guessed sample boundaries; import PCM WAV masters. Thumbnail color interpretation never changes originals. A process crash can leave an unreferenced owned copy, never a partially published registry/source overwrite.

## T06 — source review prepared; art input pending

`T06: prepare actual Tabi source review and palette evidence` registers two linked draft source references in `.local/pilot-asset-review` and records their exact file identities and measured palette samples. Reopened and visually compared the actual character profile and seated train composition. [Review packet](12-tabi-art-review.md) links both originals and describes the separate pieces/hidden-region repairs still required. [Evidence](evidence/t06-reference-review.json) records unapproved, rights-pending provenance. No artwork was changed, no replacement likeness was invented, and no editable master was claimed from flattened images.

The source-hash choice, separated seated masters, anchors/pivots and art review remain pending; T06 is not marked complete. Independent synthetic/compiler work continues under PLAN's explicit allowance.

## T09 — complete

`T09: evaluate global curves and deterministic action timing` implements rational frame/sample mapping, half-open scene queries, explicit loop origins, global constant/linear curves, exact prefix integrals, scope precedence and deterministic optional action timing. Same-frame queries do not depend on playback or chunk history. Scene-state bases remain explicit for T10 continuity. Random collisions fail; no event is silently dropped.

Verification: `make schemas && make check` passed Ruff, **20 schemas and 148 tests**, eight media tests skipped. Eleven new cases cover analytic acceleration/stop/restart, all interval splits, out-of-order queries, rational fps/sample rounding, curve bounds/scopes, reproducible whole actions and conflict errors. An OpenSSL check independently confirms the pinned random reference vector. CLI inspection/expansion passed; [evidence](evidence/t09-timeline.json) records the fixture stop at 180 px, restart frame 151 at 184 px/sample 241600, final distance 780 px and four seeded blink requests. This is semantic evidence, not rendered/art-approved output.

## T10 — core complete; real-art review pending

`T10: compile pose transitions and persistent scene state` adds deterministic action compilation and frame inspection. It resolves transitive asset identities, expands compatible entry/hold/exit routes, preserves authored one-shots/whole loops, checks props and channel/camera/fps/alpha compatibility, and enforces declared continuity or explicit resets at cuts. Facial overlays leave the body's global phase intact. Production compilation rejects unapproved packs and invalid media.

Verification: `make schemas && make check` passed Ruff, 20 schema checks and **160 tests** (eight media tests skipped). Twelve new compiler cases verify missing transitions/props, fixed one-shot duration, action conflicts, blink independence, exact prop boundaries, cuts/resets, changed source rejection and deterministic snapshot reopening. Fresh `.local/t10-compiler-fixtures` compiles to eight events with 15 resolved locks; [state evidence](evidence/t10-compiled-state.json) records frames around each blink/transition and the 780 px final travel state. This caught and corrected the fixture generator's previous default-zero final travel metadata; previous T04 evidence remains a historical record of that earlier generator.

Core implementation is complete against fixtures. Real Tabi motion approval remains pending; scene overlaps are explicitly unsupported until T18. No real artwork or publication status was approved.

## T11 — core complete; real-art review pending

`T11: render locked scene layers with verified masks and alpha` implements a renderer interface and shared FFmpeg still/clip backend. Frozen records/files are verified before and after rendering. Owned PNG copies normalize straight/premultiplied alpha and tagged color without editing originals; masks retain raw coverage. Ordered template slots control masks, opacity, prepared body/face clips, foreground occlusion, framing and cuts. Synthetic/draft labels are always visible. Verified outputs publish without overwriting existing files; failure cleans only owned temporary work.

Verification: `make check`: Ruff, **21 schemas and 163 tests passed**, 14 media tests skipped. `make test-media`: **all 14 actual-media tests passed**, including prior software/VideoToolbox checks. Six new media cases passed, including 12 frame comparisons against independent Pillow composition (maximum two RGB levels) with both binary and partial mask/alpha, and a look-transition video checked against six sampled global frames (15-level tolerance). Changed locks, invalid masks and injected output-verification rejection preserve originals and publish nothing. The separate ten-second/300-frame/640×360 clip fully decodes with rational timestamps and BT.709 H.264 tags; measured FFmpeg subprocess time is 0.601 seconds, excluding preparation/verification. [Still](evidence/t11-synthetic-frame-37.png) was visually inspected; [still report](evidence/t11-still-report.json) and [clip report](evidence/t11-clip-report.json) retain identities and timings. MP4 stays local under `.local/t11-renderer/`.

This completes static/masked scene rendering against synthetic assets. Moving strips/landmarks, effects, audio and real Tabi artwork remain their respective tasks. PNG sequences are the supported prepared alpha interchange; unknown production color, unsupported effects and unapproved production snapshots fail explicitly. No final-art or 4K readiness is claimed.

## T12 — complete

`T12: render continuous parallax and one-time landmarks` uses shared analytic travel distance for all depths. Repeating strips validate their declared tile period and duplicated crop coverage; landmarks translate without wrapping through explicit anchors/intervals. Missing/ambiguous sprite slots fail, and optional `slot_id` supports deliberate routing. Fixture landmark placement is now explicit.

Verification: **163 tests and 21 schema checks passed**, 18 media tests skipped; focused T11/T12 media suite **10 passed**. Twenty-four actual motion stills match independent references within two RGB levels across acceleration, stop, restart and wrap. The decoded full clip shows one continuous landmark pass and no recurrence; a range starting at frame 149 keeps global phase. Wrong strip periods and missing sprite slots fail. These tests caught and fixed a one-frame overlay-position convention mismatch in FFmpeg.

[Inspected frame 149](evidence/t12-synthetic-frame-149.png), [still report](evidence/t12-still-report.json) and [clip report](evidence/t12-clip-report.json) retain output/backend/toolchain identities. The local ten-second clip is `.local/t12-motion/synthetic-motion.mp4` (300 frames, 640×360/30, no audio); FFmpeg subprocess measured 0.815 seconds, excluding preparation/verification. No real-art or long-form performance approval follows.

## T13 — complete

`T13: expose frozen compilation and verified preview workflows` adds the shared episode workflow and CLI validation, immutable compilation, snapshot inspection/review, exact PNG frames and global-range MP4 previews. Inputs are locked and reverified; prior snapshots and existing output files remain unchanged. Explicit production review requires the exact content hash and creates a new snapshot. Synthetic content cannot gain production approval.

Verification: `make schemas && make check` passed **22 schemas and 168 tests**, Ruff clean, 19 opt-in media tests skipped. The six focused workflow checks passed, including actual CLI encoding/decoding. Repeated compilation, draft edits, read-only validation, stale/tampered inputs, invalid frames and review gates were exercised. [Workflow/evidence](15-preview-workflow.md) records a visually inspected frame and a verified 132-frame global-range clip at 960×540/30; FFmpeg subprocess time was 0.999 seconds. MP4 remains ignored at `.local/t13-cli/look-range.mp4`.

Video-only preview is intentional at this step; T16 supplies continuous audio. Real Tabi artwork and snapshot approval remain pending.

## Next task and pending gates

**Next software task: T23 — final export profiles and target-Mac measurements.** T14 requires T07/T08 real artwork and Marco's visual review; T16–T19 real soundtrack/effect/story review remains pending. Independent software work continues while creative inputs are pending.

Pending target-Mac checks: alpha-capable video interchange, real-scene VideoToolbox quality and 1080p/4K render time/memory, browser seeking/audio/authentication, local packaged launch/recovery and user-facing backup restoration. Core CLI cancellation/resume is verified in T20/T21; the small synthetic pass does not establish the remaining capabilities.

Pending creative inputs: selected reference/hash approval, editable separated art and masks/depth layers, sequence timing/anchors/loop ranges/transition poses, provenance and rights records, and finished original music. Continue independent synthetic infrastructure work while these remain pending.

## T15 — complete

`T15: preserve music masters and validate sample timelines` extends exact WAV import with bounded PCM reading, explicit sample envelopes, source waveform proxies, timeline gap/overlap/silence warnings and strict draft release-metadata import. CLI and episode validation share the same rules. Metadata cannot substitute a different master or invent identifiers; original and copied WAV bytes remain unchanged.

Verification: `make schemas check` passed Ruff, **24 schemas and 174 tests**, 19 opt-in FFmpeg checks skipped. Six new audio cases cover independent PCM values and every split boundary, signed 24-bit decoding, source waveform statistics, silence, invalid trims/hashes and preserved metadata/master bytes. [Audio documentation/evidence](16-audio.md) records the ten-second/480,000-sample fixture and waveform. NumPy 2.4.6 is locked. Current interchange is integer mono/stereo PCM WAV; technical conversion and continuous mixing follow in T16. Real music/listening review remain pending.

## T16 — core complete; listening review pending

`T16: mix continuous PCM and encode preview audio once` implements source-preserving technical preparation, continuous stereo float PCM, authored ambience loop/crossfade phases, explicit gain, peak/loudness measurement and one AAC encode during preview mux. WAV import/read now supports float, extensible and RF64 containers. Byte/sample verification precedes atomic publication; overload is reported without clipping the float mix and prevents AAC export until explicitly adjusted.

Verification: `make schemas check` passed Ruff, **25 schemas and 177 tests**. `make test-media` passed **all 24 media tests**. New checks prove exact PCM trim/fade samples and range parity, real 44.1→48 kHz conversion, loop seam bounds, silence, failure cleanup, explicit overload handling, one AAC encode and global-range audio fidelity/timing. [Mix](evidence/t16-mix-report.json) and [preview](evidence/t16-preview-report.json) evidence records 480,000 decoded stereo samples and 300 frames at 960×540/30. Outputs remain local under `.local/t16-audio`; no MP4 is committed. [Audio documentation](16-audio.md) records limits and reproduction.

No finished real music/listening approval was supplied; an asynchronous request for its local folder is pending. This completes the software pipeline against owned test signals, not the M3 creative gate.

## T17 — core complete; effect review pending

`T17: render bounded masked effects with global phase` adds explicit template tint/rain/reflection slots, scoped strength curves, required masks, bounds and prepared-loop validation. Temporal phase uses a retained global origin, independent of seek/range boundaries. Unknown history-dependent effects fail. A reproducible effects profile extends the synthetic fixture to 17 assets/86 files; no Tabi palette approval is inferred.

Verification: `make check` passes **25 schemas and 180 tests**, Ruff clean. Three new unit cases and two new actual-media cases pass, including thirteen independent PNG comparisons (maximum three RGB levels), protected foreground/character pixels, and full/split global range checks. Existing static and motion regression checks passed. [Inspected frame](evidence/t17-effects-frame-151.png) and [reports](17-effects.md) record a 300-frame/640×360 preview with 480,000 AAC samples. Latest render/mix/mux interval: 20.097 seconds, versus an earlier 42.855 seconds before reducing expression work to alpha planes; these are development observations with concurrent tests, not controlled benchmarks.

Real effect/palette approval and 1080p/4K performance remain pending. The MP4 stays ignored at `.local/t17-effects-verified.mp4`.

## T18 — core complete; story review pending

`T18: author story beats and verify scene overlaps` adds scene/transition purposes, beats linked to musical placements and an object notebook, with a frozen storyboard inspection command. Conservative overlap validation prevents doubled or divergent characters. The renderer blends in global frame time; cut and overlap entry states share one pose/prop/travel evaluator. Active scoped curves are checked against their scene capabilities.

Verification: `make schemas check` passes **26 schemas and 193 unit checks**, Ruff clean; `make test-media` passes **all 28 actual-media checks**. Thirteen new unit cases cover continuity, phase, placement, face/prop divergence, metadata and scope. The new media cases verify matched and single-character overlaps, including endpoints and starts inside a transition, against independent composition and global-range comparisons. [Evidence](18-story-continuity.md) retains a 300-frame/640×360 preview with 480,000 AAC samples and an inspected midpoint PNG. MP4 stays local and ignored.

The outline, original music, approved artwork and Marco's creative review remain pending. No synthetic output is considered publishable or approved.

## T19 — production input gate pending

`T19: record short-story production input gate` records the missing approved separated art/action/environment pack, finished original music masters and credits, real story outline and full-duration Marco review. T18's working synthetic demonstration cannot satisfy the 5–10-minute publishable-story acceptance. Reference selection and music-folder requests remain unanswered; no permissions, release identifiers or creative approvals are inferred. Independent engineering continues with T20.

## T20 — complete

`T20: persist owned jobs and recover verified progress` implements a durable FIFO queue, append-only hash-linked events, atomic current-state checkpoints and replay, a single-worker project lease, scoped subprocess cancellation, verified chunk publication and failure diagnostics. CLI queue operations invoke the same service intended for the web API. Original sources and other live processes are preserved.

Verification: `make schemas check` passes **27 schemas and 201 unit checks**, Ruff clean; `make test-media` passes **all 31 actual-media checks**. Eight new unit cases cover durable state and ownership; three new actual-media cases pass, including an actual worker exit with a verified 46-frame chunk retained and cancellation of a live FFmpeg graph without touching another process. [Evidence and operations](19-jobs.md) retain completed, process-failed, cancelled and interrupted runs, with an unchanged WAV source hash. The verified 300-frame preview has 480,000 AAC samples. All MP4s remain ignored.

One bounded chunk is the T20 execution unit. T21 adds planning/resume/assembly; T26/T33 add background service and packaged lifecycle. An OS-killed worker's leftover temporary work is never claimed as success or adopted by PID.

## T21 — complete

`T21: resume verified video chunks and assemble continuous audio` adds bounded global frame planning, preferred scene cuts, frozen profile/core/toolchain compatibility, verified chunk reuse and safe retry paths. Video-only chunks are assembled with validated stream copy or a recorded, verified re-encode fallback. Continuous PCM is mixed once and AAC encoded once at final mux. Crashes before/after export publication preserve recoverable artifacts; a conflicting existing export is never overwritten.

Verification: `make schemas check` passes **27 schemas and 214 unit checks**, Ruff clean; `make test-media` passes **all 38 actual-media checks**. Thirteen new unit cases and five new chunk-media cases pass. Story/effect ranges match monolithic exports within the documented lossy tolerance; rational 30000/1001 fps retains exact frame/sample intent. Worker-exit tests cover both sides of publication and external export conflicts. [Retained evidence](20-chunk-assembly.md) records cancellation at 154 verified frames, detection of a truncated chunk, reuse of the valid 77-frame neighbour and a final 300-frame / 480,000-sample export. Its decoded midpoint was visually inspected. MP4 stays ignored.

Cross-job caching/storage management follows in T22. Final-resolution hardware quality and sustained long-form resource checks remain T23/T37; no artistic approval is inferred.

## T22 — complete

`T22: reuse verified media and guard cache pruning` adds project-local normalized PNG and video caches, content/runtime/tool fingerprints, audio-independent video reuse, independent job copies with full decode validation, disk estimates/preflight and explicit inventory-bound pruning. Sources, approved/frozen metadata, unknown files and active workers are protected. No arbitrary scratch directory is recursively deleted.

Verification: `make check` passes **31 schemas and 222 unit checks**, Ruff clean. `make test-media` passes **all 39 actual-media checks**; the cache test was expanded and rerun after adding runtime-version fingerprints. Actual audio edits reuse video and change decoded gain, corrupted cache payloads rerender, and changed motion/source bytes invalidate cached output. [Retained evidence](21-cache-storage.md) records 4 initial video graphs, 0 for an audio-only edit and 1 after corrupting one cached chunk, with one AAC encode each. Explicit pruning removes 29 entries while all 54 checked source/snapshot/export files retain their hashes. All MP4s stay ignored.

Disk requirements remain conservative estimates rather than reserved space. Project-local cache storage is implemented; the early global `cache_root` setting is reserved. T23/T37 still own final-resolution quality and sustained performance checks.

## T23 — complete

`T23: verify final export profiles and target-Mac performance` adds explicit proxy/1080p/4K presets,
AAC-LC rates, shared final encoder arguments, full frame/PTS/color/audio verification, Fast Start
inspection and completed-export revalidation. A reproduced VideoToolbox short-chunk timestamp
defect is rejected and avoided by disabling hardware B frames. Per-frame alpha LUTs replace the
expensive per-pixel opacity expression while retaining independently tested global-frame behavior.

Verification: `make check` passes **32 schemas and 224 unit checks**, Ruff clean; `make test-media`
passes **all 48 actual-media checks** in 195.12 seconds. Both 60-second M5 Pro stress exports verify
1,800 frames and 2,880,000 samples. Software 1080p finishes in **94.22 seconds / 19.10 fps / 3.58 GiB**
sampled RSS; 4K VideoToolbox in **260.69 seconds / 6.90 fps / 3.15 GiB**. All twelve sampled decoded
frame comparisons pass; frame-151 PNGs were visually inspected. [Methods and retained evidence](22-export-profiles.md)
include the earlier cancelled run and rejected hardware packet trace. No MP4 enters Git.

The benchmark uses synthetic art on a native 1080p canvas; the 4K output scales that composition.
Native 4K design and sustained long-form resource use remain T37. Production artwork, music and
creative approval remain pending; delivery verification does not grant publication approval.

## T24 — core complete; production inputs and review pending

`T24: prepare verified release bundles with private evidence` adds strict preparation/public/report
contracts, factual music metadata, clip-relative sample intervals, conservative chapter validation,
hash-bound reviews and readiness checks. Shared Python/CLI services copy independently verified
media into an atomic new bundle, with public allowlists separated from private source/review evidence.
Unknown IDs remain null. Pending rights, synthetic art and missing reviews block upload readiness.

Verification: `make schemas check` passes **36 schemas and 227 unit checks**, Ruff clean. The new
actual-media release test passes render/copy, privacy sentinel, pending review, stale revision,
concurrent edit, existing/traversing destination and corrupted-output checks. [Evidence](23-release-preparation.md)
retains a real CLI bundle from the 60-second T23 1080p export, with the exact video hash and valid
three-chapter layout. Source masters and earlier bundles survive injected failures unchanged.

The production-ready bundle gate remains pending on T19's real art/music/credits/licences and human
reviews. This engineering bundle remains synthetic. No publication or asset approval was performed.

## T25 — complete

`T25: build browser wireframes and verify native playback` adds twelve reviewable design
pages, schema-generated TypeScript DTOs and precompiled browser validation, real H.264/AAC
playback and Python exact-frame requests. Eleven pages remain clearly identified wireframes.

Verification: `make check` passes **36 schemas and 229 unit checks**, Ruff clean; frontend
contract/drift/type/format checks, two tests and Vite build pass. Safari 27.0.1 and Chrome 154
on the target Mac play and seek the actual 300-frame synthetic proxy with measured nonzero
decoded audio. The exact-frame inspector, Space/arrow shortcuts, skip-link focus and 700-pixel
layout were checked. Actual HTTP checks cover ranges, HEAD, MIME and request boundaries.
[All page screenshots, browser observations and reproduction](24-browser-foundation.md) are retained.

The native Safari video was visually confirmed after bringing its window to the front;
background animation throttling no longer leaves diagnostics stale. User visual/listening
approval remains separate. T26 adds the authenticated service; T27–T32 implement the flows.
No MP4 is committed; Node is needed only to build. The initial validator bundle size warning
is documented, and installed distribution remains T33.

## T26 — complete

`T26: authenticate local worker sessions and media` adds an owned loopback Python launcher,
private protocol/PID/socket readiness verification, one-time browser tickets, per-worker cookies,
bearer/CSRF/Host/Origin checks, registered-root browsing, shared-core job adapters, SSE replay
and authenticated verified byte ranges. Tab closure does not cancel work; explicit shutdown
keeps verified chunks, and a fresh worker resumes through the existing core.

Verification: `make check` passes **42 schemas and 238 unit checks**; frontend drift/type/format
checks, two tests and build pass. Nine focused service/lifecycle checks and an actual HTTP
render/cancel/restart/resume case pass, producing **300 frames / 480,000 samples** with one
verified chunk retained and WAV sources unchanged. Startup failure, independent ephemeral
listeners, CLI SIGTERM cleanup, session replay/expiry, CSRF, missing media/SSE auth and unsafe
filesystem paths are covered. [Evidence and operation details](25-local-service.md) are retained.

Safari and Chrome both bootstrap, refresh, play/seek authenticated media, display expiry and
reopen without replacing the worker or duplicating jobs. Reopening an existing tab processes
a fresh fragment ticket. The public shell accepts initial navigation while API origin checks
remain strict. Settings shows real worker/project state; other pages remain wireframes for
T27–T32. Installation packaging remains T33. No MP4 or session secret enters Git.

## T27 — project, asset and episode setup workflows

Completed real project create/open/relink, durable recent locations, asset import and inspection, immutable versions, image proxies, hash-checked relinking and explicit approval forms. Uploads stream bounded chunks, persist receipts across reconnects, compare retried bytes and stay outside the registry until verified. Episode setup invokes shared Python authoring services; it never trims music to fit. All imports retain actual provenance and rights state.

Evidence: `make check` 242 passed / 50 opt-in skipped; focused HTTP checks 13 passed; frontend checks/tests/build passed. Chrome created a Unicode-path project and Safari completed file selection → upload → asset inspection → still template → episode creation. [Import screenshot](evidence/t27-safari-import.png), [saved episode](evidence/t27-safari-episode.png). See [workflow guide](26-project-workflows.md).

## T28 — story, timeline and continuity editor

Complete. Python now owns semantic editing commands and the timeline display intervals. The browser offers scene cards, appended scenes, cut boundaries, action selection/movement, declared keyframe parameters, story beats and a continuity notebook. It preserves frame selection/zoom across views. All changes save atomically with revision guards; title/purpose autosave after a short typing pause, while structured inspectors apply one coherent edit. Serialized undo/redo creates new guarded revisions and preserves media imports/jobs.

`make check`: 246 passed / 50 opt-in skipped. Focused editor/workspace checks: 8 passed. Frontend checks/build and four contract/history tests passed. Chrome proved autosave → undo → redo → append → worker restart → stale second-tab rejection → reload → notebook save. [Timeline](evidence/t28-timeline.jpg), [conflict](evidence/t28-conflict.jpg), [notebook](evidence/t28-notebook.jpg). [Editor guide](27-editor.md).

## T29 — renderer preview and exact frame review

Complete. Preview now queues the shared Python renderer, retains verified proxies while replacements render, labels stale snapshots after edits and supports authenticated native video seeking/audio. Exact still requests use integer global frames, debounce and cancel only their own subprocess work. Review notes retain snapshot hashes. Browser checks exposed and fixed native range initialization so frame selection survives Story/Preview navigation.

`make check`: 247 passed / 51 opt-in skipped; focused actual-media and state checks: 2 passed. Frontend checks/build and four tests passed. Chrome and Safari verified new 300-frame playback, seek, nonzero audio and the same frame-150 PNG hash. Refresh, stale edits, newest-frame scrubbing and worker failure were exercised. [Preview guide](28-preview.md) and [screenshots](evidence/t29-chrome-preview.jpg) record synthetic evidence. Human creative review remains pending.

## T30 — audio editor and factual music metadata

Core complete; Marco's listening review remains pending. Audio now edits sample placements, trims, gain, fades and ambience loops through Python proposals, with explicit ordered music placement, visible duration conflicts, guarded save and undo/redo. Waveforms derive from the hashed masters. Auditions use the final renderer's mixer and display measured loudness, true/sample peaks and clipping without applying suggested gain. Metadata forms preserve unknown IDs and validate actual master hashes, samples and rights state.

`make check`: 248 passed / 52 opt-in skipped. Two focused state/media checks pass; actual PCM verifies -6 dB, fades, immutable masters, stale edits and metadata rejection. Frontend checks/build/four tests pass. Chrome proved conflict rejection → save → undo/redo → waveform → complete edited-WAV playback → metadata save. [Guide](29-audio-editor.md), [screenshot](evidence/t30-audio-editor.jpg). No approved original music or creative judgement is implied.

## T31 — render queue, settings and recovery controls

Complete. Frozen export plans and conservative storage estimates feed the real queue. Measured ETA excludes paused time; pause finishes the current verified chunk while cancel stops owned work. Resume and export verification reuse the existing integrity checks. Preferences use revisions; tool configuration uses hashes and exact backups. Cache cleanup uses an observed inventory and protects source media.

`make check`: 252 passed / 53 opt-in skipped, 57 schemas. Frontend checks/build/four tests pass. Two actual-media checks pass. Chrome exported 300 frames of 1080p video with 480000 audio samples, paused at 180 frames, resumed successfully and remained responsive in Settings. [Guide](30-render-queue.md), [queue evidence](evidence/t31-verified-queue.jpg).

## T32 — release page and private portability

Core complete; production rights/disclosure review remains pending. Release now saves public metadata and private manual notes, checks actual exports and rights, records hash-bound human reviews and exports a verified public/private folder. Browser links expose only public manifest entries. Backup/restore streams independent checked copies, preserves reviewed documents and snapshots, embeds linked media beneath bounded local roots and publishes only complete new folders.

`make check`: 255 passed / 54 opt-in skipped; 61 schemas. Frontend checks/build/four tests pass. Four backup checks and an actual-media HTTP release/restore check pass after final copy verification. The restored renderer produces the same frame hash and saved export bytes. Chrome backed up 186 files and opened a new Unicode-path copy with the same six release blockers. [Guide](31-release-and-backups.md), [release evidence](evidence/t32-release-bundle.jpg).

## T33 — installed local web app

Complete. The Python wheel/sdist includes a verified static UI and exact dependency notices.
Build guards detect stale inputs, changed output and prohibited media/runtime binaries.
`setup-check` reports actionable Python, frontend and FFmpeg diagnostics. The default project
folder is created on launch; Node/JDK are unnecessary at runtime.

`make check`: 259 passed / 54 opt-in skipped, 61 schemas. Frontend checks/build/four tests
pass. Installed outside the checkout in a fresh Unicode-path environment without Node on PATH;
setup check verified bundled hashes. Chrome queued a 90-second synthetic pilot, tab closure left
it running, and a new worker resumed 1,800 retained frames to 2,700 frames / 4,320,000 samples.
Chrome and Safari played/sought it and measured nonzero audio. Three actual installed process
crash/recovery cases passed. [Installation](32-installation.md), [evidence](tasks/t33.md),
[installed preview](evidence/t33-installed-chrome.jpg). Real creative approval remains pending.

## T34 — café template

Core complete; café art review remains pending. `fixtures --profile cafe` adds a stationary
room/street, new window geometry and table anchor, slow clouds and one passing pedestrian.
The explicit café-compatible pack reuses geometric clips. No compiler/renderer/editor branch
was needed. Two unit checks and one actual-media check pass, including fixed architecture,
masked motion, anchor/occlusion and a 300-frame / 480000-sample export. `make check`: 261
passed / 55 opt-in skipped, 61 schemas. [Guide](33-cafe-template.md),
[synthetic frame](evidence/t34-cafe-frame.png).

## T35 — activities and outfit compatibility

Core complete; real animation/outfit review remains pending. Scene/pack/clip outfit declarations
join camera/template/version checks. Story offers atomic scene pack switching and a compatibility
inventory. Synthetic sipping, reading and sleeping have explicit entry/loop/exit clips and props;
sleep owns the face channel. Source assets and legacy hashes are preserved.

Four focused checks and a real 300-frame / 480000-sample, four-chunk export pass. Chrome proved
successful outfit switching and rejection without data loss. `make check`: 265 passed / 56
opt-in skipped; 61 schemas. Frontend checks/build/four tests pass. [Guide](34-activity-packs.md),
[controls](evidence/t35-pack-controls.jpg). No new Tabi design or creative approval is implied.

## T36 — optional local generation

Core complete; real model/workflow validation remains pending. ComfyUI runs are explicitly
allowlisted by versioned manifest hashes and saved with durable prompt IDs. The bridge checks
local model/workflow bytes and node definitions, reconciles uncertain replies without resubmitting,
and imports only verified bounded stills as drafts with rights pending. CLI and Settings share it.

Eighteen focused checks pass. A real offline-generation render verifies 30 frames / 48000 samples.
Chrome proved submission → history → explicit draft import → offline state. `make check`: 283
passed / 57 opt-in skipped, 64 schemas; frontend checks/build/four tests pass. [Guide](35-local-generation.md),
[evidence](evidence/t36-generation.jpg). No model download, actual inference or artistic approval
is implied by the synthetic protocol fixture.

## T37 — sustained resource use (complete)

Preflight measured 87.75 ms per journal read with 90 chunks / 181 events. Incremental verified
replay reduced hot reads to 0.83 ms on this Mac. Every event's inode/size/mtime/ctime is rechecked;
changed history forces full hash-chain replay, and disk checkpoints remain untrusted. A bounded
LRU retains one typed tail per recently observed job, instead of all historical chunk lists.

Long curve graphs now keep global integral prefixes while selecting only branches reachable in
the rendered interval, with balanced conditions for dense keys. Thirteen actual-media checks
pass, including 2400-key curves, exact global integrals, opacity at fractional frame rates and
chunk assembly. `make check`: 285 passed / 59 opt-in skipped; 64 schemas. A 45-minute native
1080p synthetic Session has passed its full delivery and all-boundary checks. The native 4K
gate also passed, completing this task's engineering acceptance.

The SSE transport now checks the incremental journal tail before replaying history. Ten local
service checks pass, including a real HTTP stream that emits idle heartbeats at an up-to-date
cursor and then delivers the next committed cancellation event without rendering any media.

T37 export review now plays verified media inside the Renders page, with explicit approximate
second-based seeking. Switching exports or leaving the page pauses and releases the old media.
Settings links select the matching project and open its render queue. This addresses the target
Chrome session blocking raw-MP4 page navigation. The actual 2700-second, 1920×1080 export
loaded at readyState 4; seeking to 2650 seconds played through 2665.71 without a media error,
and the final build sought to 2695 seconds. Navigation removed the player. See
[browser evidence](evidence/t37-browser-seek.json) and [screenshot](evidence/t37-longform-seek.jpg).
Frontend typecheck, formatting, four tests and production build pass. The long-form worker
finished verified; all 184 independent comparisons at every chunk boundary subsequently passed.

The full 45-minute run completed 81000 frames and exactly 129600000 decoded audio samples.
Two chunks (1774 frames) survived the injected worker crash unchanged. The recorded start-to-
verification interval, including recovery, was 4022.756 seconds (20.135 fps overall). Peak measured
worker + tool RSS was 3.05 GiB; worker medians across steady thirds were 151.22 / 157.89 / 158.30 MiB,
with at most one retained live tool and ten descriptors. All 3916 resource samples succeeded.
The benchmark's post-render selector needed balanced expressions to fit FFmpeg's parser; the
verified video was preserved and review resumed successfully. See [complete evidence and limits](36-longform.md).

Native 4K also passed its full 60-second workload: 1800 frames, 2880000 decoded audio samples,
all six reference comparisons, full decode, exact presentation times and fast start. Whole-export
time was 305.746 seconds (5.887 fps); peak sampled worker + tools RSS was 11.29 GiB. The full
report and representative frame are linked in the long-form guide. One active export remains
the default; full-length native 4K and real artwork need separate qualification.
Final T37 `make check`: 286 passed, 59 opt-in media cases skipped, 64 schemas checked. Frontend
typecheck, four tests and production build passed after the export-review change.

## T38 — operations and final acceptance (in progress)

The acceptance audit found that template/action-pack approval needed an explicit operator flow.
Assets now displays their exact metadata and Python-computed review hashes. The shared authoring
service records review only after production dependency checks and a final revision guard; pack
compatibility uses the same validation as episode compilation. Approved versions remain immutable.
Twenty-two focused unit/API checks pass. A real test-only production flow approves temporary owned
geometry, freezes and separately reviews a snapshot, then verifies a three-chunk export with exactly
30 frames and 48000 audio samples. No supplied Tabi artwork was approved. Python lint/format and
the frontend contract/type/build checks pass. Chrome rejected a synthetic template without changing
its draft status; [UI evidence](evidence/t38-metadata-review.jpg). Final broad gates follow.
