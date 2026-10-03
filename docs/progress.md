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

## Next task and pending gates

**Current: T02 — toolchain and renderer capabilities.** Step 1 implements `tabi doctor --json` / `make doctor`, typed machine/capability reports, executable hashes, strict tool-version compatibility and writable-storage checks. `make check`: 120 tests, lint/format and 15 schemas pass. The [machine report](evidence/t02-doctor-m5-pro.json) records this M5 Pro/48 GiB with FFmpeg/ffprobe 9.0.2 installed through Homebrew. Encoders remain explicitly `listed_only`; the real synthetic render is the next step. M0 remains incomplete until that gate passes. The web UI and episode renderer remain planned.

Pending target-Mac checks: installed FFmpeg/ffprobe, mask/alpha/speed rendering, VideoToolbox quality, render time/memory, browser seeking/audio/authentication, local packaged launch, render cancellation/resume and user-facing backup restoration. Native decoding on this M5 Pro does not establish those capabilities.

Pending creative inputs: selected reference/hash approval, editable separated art and masks/depth layers, sequence timing/anchors/loop ranges/transition poses, provenance and rights records, and finished original music. Continue independent synthetic infrastructure work while these remain pending.
