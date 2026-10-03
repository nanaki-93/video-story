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

## Next task and pending gates

**Next: T05 — asset importer and immutable registry.** The web UI and reusable episode renderer remain planned. T02's deliberately bounded experiment does not implement those layers.

Pending target-Mac checks: alpha-capable video interchange, real-scene VideoToolbox quality and 1080p/4K render time/memory, browser seeking/audio/authentication, local packaged launch, render cancellation/resume and user-facing backup restoration. The small synthetic pass does not establish those capabilities.

Pending creative inputs: selected reference/hash approval, editable separated art and masks/depth layers, sequence timing/anchors/loop ranges/transition poses, provenance and rights records, and finished original music. Continue independent synthetic infrastructure work while these remain pending.
