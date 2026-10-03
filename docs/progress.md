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

## Next task and pending gates

**Next: T03 — schemas and safe project persistence.** T02 follows with a real FFmpeg capability/render spike; neither tool was on PATH during this audit. M0 remains incomplete until those gates pass. All other application tasks remain planned; this repository cannot render or launch a web UI yet.

Pending target-Mac checks: installed FFmpeg/ffprobe, mask/alpha/speed rendering, VideoToolbox quality, render time/memory, browser seeking/audio/authentication, local packaged launch, cancellation/resume and backup recovery. Native decoding on this M5 Pro does not establish those capabilities.

Pending creative inputs: selected reference/hash approval, editable separated art and masks/depth layers, sequence timing/anchors/loop ranges/transition poses, provenance and rights records, and finished original music. Continue independent synthetic infrastructure work while these remain pending.
