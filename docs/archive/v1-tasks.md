# V1 task records — T01–T38

Historical implementation records, consolidated on 4 October 2026. These are not the active backlog. Use the [current task index](../tasks/INDEX.md), [current progress](../progress.md) and [V1 acceptance report](../38-v1-acceptance.md) for current status. Original completion evidence and pending creative gates are retained below.


<a id="t01"></a>

## T01 Bootstrap repository and developer commands

Status: complete

Scope: mandatory

Dependencies: None

### Implementation

Create the Python package, test layout, docs/progress.md, lockfile and Makefile. Add structured CLI logging, application version and config resolution. Record chosen compatible runtime versions. Preserve existing repository instructions.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Fresh environment can install dependencies, run CLI help and execute checks. No media generator or web UI is required yet.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T01: bootstrap Python core and plan local web app`, 3 October 2026; see [progress](../progress.md).

Implemented behavior: Python package/CLI, version, strict TOML local settings with explicit precedence and normalized paths, JSON diagnostics, locked tooling and Makefile entry points. Media commands and HTTP/UI services are not exposed.

Verification commands and results: `make check` passed lint/format and 18 tests. `UV_PROJECT_ENVIRONMENT=.local/t01-fresh-env .tools/bin/uv sync --frozen --group audit` installed a fresh environment; its CLI help/version and `python -m pytest` passed (18 tests).

Representative output/screenshot: `tabi 0.1.0`; `tabi config --json` returns resolved settings. No UI or media deliverable applies.

Machine and tool versions: Apple M5 Pro/arm64, macOS 27.0.1; Python 3.11.16, uv 0.11.0, pytest 9.1.1, Ruff 0.16.10, Pillow 12.3.0, Hatchling 1.27.0. Exact dependencies in `uv.lock`.

Remaining limits: T03 domain schemas/persistence, T02 FFmpeg probing/render spike and all UI/media work remain planned. Neither FFmpeg nor ffprobe is currently on PATH. No creative approval or render-performance claim.


<a id="t02"></a>

## T02 Probe toolchain and renderer capabilities

Status: complete

Scope: mandatory

Dependencies: T01

### Implementation

Implement doctor for Python, ffmpeg/ffprobe paths and versions, required filters, software/HW encoders, output writable space and platform. Add the tiny overlay/alpha/speed encoder spike and capture machine-specific report.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Missing tools give actionable errors. A 10-second synthetic clip decodes correctly. Report does not claim target-Mac verification when run elsewhere.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

M5 Pro needed for hardware claims.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Step 1: `5d48ed2` — `T02: add local toolchain doctor and capability reports`.

Implemented doctor for Python/platform/CPU/memory, configured executable resolution, FFmpeg/ffprobe identity/version/hash, required filters/software encoders, advertised hardware capabilities and a real temporary storage write/free-space check. Subprocesses use argument arrays, timeouts and bounded output reads. Reports are typed/versioned with a generated JSON Schema and explicitly mark encoders `listed_only`.

Verification: `make check` passes 120 tests plus lint, formatting and 15 schema checks. New checks cover missing/wrong tools, incompatible versions, capability listing variants, full/unwritable storage, literal Unicode/shell-character arguments, subprocess failure/timeout/output bounds and avoiding false target-Mac claims. `tabi doctor --json` passed on Apple M5 Pro/48 GiB, macOS 27.0.1, Python 3.11.16, Homebrew FFmpeg/ffprobe 9.0.2. The machine report is [t02-doctor-m5-pro.json](../evidence/t02-doctor-m5-pro.json).

Step 2: `T02: verify synthetic rendering with software and VideoToolbox`.

Implemented a bounded, watermarked ten-second scene and verified output publication. Generated inputs, explicit straight-alpha composition, window masking, numbered-strip stop/restart, frame-scoped rectangle visibility, foreground occlusion and an owned tone feed the actual FFmpeg graph. Both libx264 and H.264 VideoToolbox (`-allow_sw 0`) produce H.264/AAC output that passes full decode, exact 300-frame/30 fps timing, color tags, 110 pixel checks, 97 motion-boundary checks and audio duration/tone checks. The core/CLI retain per-run diagnostics; failed output never replaces an existing export.

Final verification: `make check` passed 122 unit tests, lint/format and 16 schema checks (seven opt-in media tests skipped); `make test-media` passed all seven actual media tests on this Mac. Negative renders expose inverted masks, incorrect alpha interpretation, early entry and incorrect restart speed. Truncated output and a failed-verification publication path are also rejected. Both pinned-config CLI runs passed and their typed reports reopened successfully.

Evidence and reproduction: [toolchain report](../10-toolchain.md), [software JSON](../evidence/t02-software-m5-pro.json), [hardware JSON](../evidence/t02-hardware-m5-pro.json), [software frame](../evidence/t02-software-frame-090.png), [hardware frame](../evidence/t02-hardware-frame-090.png). All MP4s remain in ignored `.local/`; the reports contain exact paths and hashes. Visual inspection confirmed the synthetic mask/alpha/occlusion and watermark, not art approval.

Measured software/hardware render subprocess times: 0.515/0.613 seconds for the low-complexity 960×540 test; no full-scene performance conclusion follows. Each decoded output has 480,000 audio samples, zero stripe displacement error and maximum RGB error 2/3 respectively. Machine/tools remain M5 Pro/48 GiB, macOS 27.0.1, Python 3.11.16, FFmpeg/ffprobe 9.0.2.

Remaining limits: no real artwork, reusable episode renderer, alpha-video interchange, browser playback, 1080p/4K quality/resource benchmark, render job recovery or creative approval. M0 acceptance passes. T04 is the next unblocked task.


<a id="t03"></a>

## T03 Define schemas and safe project persistence

Status: complete

Scope: mandatory

Dependencies: T01

### Implementation

Implement all models from contracts; publish JSON Schemas. Add atomic save, revisions, project lock, paths and backups. Validate the supplied examples after adapting them to final schemas. Add migration infrastructure and reject unsupported major versions.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Malformed fields, invalid intervals and incompatible versions fail usefully; reopen preserves document state; migration backup survives failure.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Step 1 — contracts complete (`8551cf2`, `T03: define strict contracts and publish JSON schemas`).

Implemented behavior: typed nested contracts for all specified models; strict version/field/unit validation, normalized media references, hash-bound approval, scene/action/audio interval checks, canonical JSON and safe YAML loading. Published 14 JSON Schemas and adapted all five supplied/example documents; the added synthetic asset records the actual hash of a two-pixel owned fixture.

Verification: `make schemas && make check` passed lint, formatting, schema drift checks and 81 tests. All example documents validate both through Python and their generated JSON Schema. Tests include malformed nested fields, incompatible versions, traversal paths, exact rational sample rounding, unsafe/ambiguous YAML, scene gaps/overlaps, channel conflicts, approval invalidation and missing snapshot locks.

Machine/tools: M5 Pro, macOS 27.0.1, Python 3.11.16; Pydantic 2.13.5, PyYAML 6.0.3, jsonschema 4.26.0. Lockfile records exact dependencies.

Step 2 — persistence complete (`T03: persist projects atomically with revision and migration guards`).

Implemented behavior: safe project initialization/reopening; canonical document saves with revision guards, verified temporary writes and exact-byte backups; POSIX single-writer locking; metadata symlink rejection and registered-root media containment; immutable hash-addressed snapshots; explicit same-major migration infrastructure with backups before transforms. Approved registry versions and snapshots cannot be overwritten or migrated in place. Added `tabi project init`, `tabi project show` and `tabi document validate` over the shared services.

Verification: `make check` passed lint, formatting, all 14 schema drift checks and **108 tests**. The 21 persistence tests cover reopen fidelity, stale revisions, cross-process lock contention/recovery, failed writes/fsync/verification, process termination immediately before publication, immutable/tampered snapshots, approved-version guards, path traversal/symlinks, successful migration and four migration failure modes. Ten CLI tests cover real subprocess commands, Unicode paths, invalid document reports, missing files and repeated initialization without overwrites.

Representative output: the installed `.venv/bin/tabi` created and reopened `.local/t03-cli-smoke-ebp0oi21/Marco's 東京 project` with identical JSON; document validation returned `valid: true`, `scope: structure`. The ignored smoke directory contains `init.json`, `show.json` and `validation.json`. No UI screenshot or rendered clip applies to this storage task.

Limits: verified on the local Mac filesystem, not network storage or power loss. Abrupt termination can leave an unused hidden temporary file; backup/orphan pruning and restoration UX remain later work. No production migration exists before schema 1.0; a test-only 1.1 model verifies migration behavior. Whole-project transactions, media probing/rendering, service authentication and artistic approval are not established. Next task: T02.


<a id="t04"></a>

## T04 Generate synthetic fixture pack

Status: complete

Scope: mandatory

Dependencies: T02, T03

### Implementation

Write reproducible PNG/mask/animation/WAV fixture generator with unmistakable placeholder visuals. Include loop, one-shot landmark, blink and transition fixtures. Produce registry records and demo episode.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Fixture generator runs without AI models or copyrighted assets; every fixture has synthetic provenance and a small predictable hash manifest.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T04: generate reproducible synthetic fixture projects`.

Implemented behavior: `tabi fixtures --output PATH` and `make fixtures` generate a new project containing 14 draft synthetic assets, cabin/window mask/foreground, three seamless numbered parallax strips, a one-shot landmark, five body/face sequences, stereo tone/silence WAVs, a scene template, action pack, and a 300-frame episode. A strict fixture manifest records 69 file hashes and sizes (2,173,410 bytes). Generation refuses existing output directories; failures remove only its own staging directory. Fixture timestamps are fixed test sentinels, not claimed creation history.

Verification commands and results: `make schemas && make check`: 17 schema drift checks, Ruff passed, 126 tests passed; seven opt-in T02 media tests skipped. Independent Pillow/WAV reads verify masks, alpha, loop/transition endpoints, repeated strip tiles, sample counts, and silence. Two generated projects in Unicode/space/apostrophe paths have identical manifests and bytes. Failure injection and occupied-directory tests preserve existing source files. Installed CLI generated `.local/fixtures-v1` successfully.

Representative output/screenshot: [manifest](../evidence/t04-fixtures-manifest.json), [sequence contact sheet](../evidence/t04-fixture-actions.png); local full project `.local/fixtures-v1`. The contact sheet is a static fixture inspection, not an episode render.

Machine and tool versions: M5 Pro/48 GiB, macOS 27.0.1, Python 3.11.16, Pillow 12.3.0; dependencies pinned in `uv.lock`.

Remaining limits: synthetic geometry deliberately does not reproduce Tabi. Every asset is marked synthetic/draft and cannot receive production approval. Rendering the reusable episode is T11–T13; no rendered episode is claimed here. Reproducibility applies to the pinned generator/runtime.


<a id="t05"></a>

## T05 Create asset importer and immutable registry

Status: complete

Scope: mandatory

Dependencies: T03, T04

### Implementation

Implement copy/link import, ffprobe/Pillow checks as needed, content hashing, proxy records, source preservation, approval versions and relinking. Track missing files and rights pending states.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Import/reopen/relink works for Unicode paths; file changes invalidate hash approval; cleanup never removes originals.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T05: import and verify immutable asset versions`.

Implemented behavior: shared `AssetService` and `tabi asset` commands import copied or explicitly linked media, decode images/WAV/video/fonts, hash every file, reopen/list the registry, report missing/changed/inaccessible files and pending rights, create image proxy records in a newer draft, relink matching bytes as a new version, and accept explicit hash-bound human review. Sequence ordering and rational source fps must be supplied; inconsistent frames, corrupt sources and variable video timing fail. Copies preserve original bytes and publication occurs after verification. Disposable import cleanup targets only its own UUID staging/output directory.

Verification commands and results: `make schemas && make check`: 19 schemas, Ruff passed, 137 tests passed (eight media checks skipped after adding the import integration test). `uv run --frozen pytest --run-media tests/integration/test_asset_import.py`: one passed with actual FFmpeg encode/decode at 30000/1001 fps. Tests cover Unicode/space/apostrophe paths, source preservation, stale review hashes, in-place changes invalidating effective approval, missing roots, hash-matched relinking, alpha-preserving proxies, truncated WAV/video, inconsistent sequence canvases and injected disk-full failure. CLI import/proxy/check succeeded on a fresh local project.

Representative output/screenshot: [asset health](../evidence/t05-asset-health.json); local `.local/t05-registry-check/Marco 東京 project`. No real asset was approved.

Machine and tool versions: M5 Pro/48 GiB, macOS 27.0.1, Python 3.11.16, Pillow 12.3.0, FFmpeg/ffprobe 9.0.2.

Remaining limits: WAV import accepts uncompressed PCM; compressed music must be exported as a WAV master. PNG thumbnails are previews, not color-approved production masters. Untagged image color stays unknown in original probe metadata. External roots require explicit caller registration on reopen; project declarations do not authorize filesystem access. A hard crash can leave an unreferenced media directory for later storage review. No source-media cleanup command is exposed. Physical external-drive loss, rather than equivalent missing-root tests, remains an operations check.


<a id="t06"></a>

## T06 Prepare approved Tabi style and seated sources

Status: source review pending

Scope: mandatory

Dependencies: T05

### Implementation

Start from the supplied character profile and train scene identified in the asset review; record which original content hash Marco approves. Create style/contact sheets, aligned seated character pieces, hidden-region repairs, anchors and mask specifications. Keep source artwork editable. Existing flattened PNGs do not replace editable masters. Coding infrastructure continues with fixtures while approval or missing layers are pending.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Actual reference comparison and user review recorded; no new likeness is silently substituted. Draft assets cannot gain production approval.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Approved Tabi reference and Marco art review.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T06: prepare actual Tabi source review and palette evidence`.

Implemented behavior: registered the supplied profile and seated train image as linked draft references, recorded original SHA-256 identities and measured palette samples, compared both actual images, and prepared a concrete layer/repair review specification. The original profile already contains the turnaround/expression/style contact sheet.

Verification commands and results: both images fully decoded with Pillow; hashes and sizes are recorded in the [reference evidence](../evidence/t06-reference-review.json). Confirmed no editable PSD/ORA/KRA/SVG/XCF master exists in the supplied asset folder. Both draft records reopen through the T05 registry, and originals remain unchanged.

Representative output/screenshot: [source review packet and original image links](../12-tabi-art-review.md); local `.local/pilot-asset-review`.

Machine and tool versions: same target Mac/Python/Pillow as T05.

Remaining limits: Marco's selection of the exact reference hashes, separated editable seated pieces, hidden-region repairs, reviewed anchors/pivots, and creator/rights evidence are pending. This is not completed art authoring or production approval. Continue independent synthetic implementation as authorized by the plan.


<a id="t07"></a>

## T07 Author core action pack and transition graph

Status: synthetic implementation complete; real animation and timing review pending

Scope: mandatory

Dependencies: T06

### Implementation

Prepare idle, blink overlay, idle-to-observing, observing hold/loop and observing-to-idle. First inspect the supplied 97-frame breath and 129-frame drink sequences; their source fps and loop intervals are undocumented. The breath sequence contains baked blinks and table-shaped occlusion, so mark its face channel occupied and camera/foreground compatibility explicitly if reused. The short MP4 tests are 25 fps, while the pilot is 30/1: require a reviewed normalization policy rather than silently changing duration. Export frame-accurate transparent media and metadata. Define exclusive body and compatible face channels.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Light/dark alpha, loop boundaries and transition endpoints reviewed; start/end poses, anchor and props match; no duplicated or drifting face.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Animation authoring and Marco approval.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: T04 fixtures, T10 compiler, T35 activity packs and T38 acceptance audit.

Implemented behavior: reproducible synthetic idle, blink, entry, observing and exit clips with
explicit loop intervals, poses, anchors and channel ownership. T10 validates transition paths,
full body coverage, face conflicts, compatibility and persistent props. T35 adds atomic outfit
switching and explicit sip/read/sleep transitions through those same contracts. No supplied
animation was assigned an invented source rate or approved as a production pack.

Verification commands and results: unit compiler/activity checks and real media tests cover
loop/transition boundaries, chunk splits, alpha/occlusion and face ownership. The full T38 gate
and test counts are in [V1 acceptance](../38-v1-acceptance.md). The source inventory and video
audit retain measured frame counts and actual MP4 rates.

Representative output/screenshot: [asset audit](../09-implementation-review.md),
[renderer](../14-renderer.md), [activity evidence](../34-activity-packs.md).

Machine and tool versions: M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2.

Remaining limits: real breath/drink source timing and loop intervals, reviewed 25→30 fps policy
where applicable, separated editable poses, face/foreground compatibility and Marco's
light/dark-alpha/loop/transition approval. This task's real animation authoring and creative
acceptance remain incomplete; the supporting implementation is complete.


<a id="t08"></a>

## T08 Prepare train interior and Tokyo environment

Status: synthetic implementation complete; separated environment art and review pending

Scope: mandatory

Dependencies: T05, T06

### Implementation

Use the supplied train still and six Tokyo panoramas as composition references. They are flattened RGB images, not the separate masks/depth layers required here. Author cabin/foreground/window mask and three exterior layers with completed hidden regions. Separate repeatable strips from scheduled landmarks already visible in the reference panoramas. Normalize the inconsistent panorama dimensions explicitly; add day/dusk reference stills and provenance.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Maximum parallax exposes no gaps; strips wrap cleanly; landmark not repeated; template masks and layer order reviewed.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Artwork preparation and Marco approval.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: T04 fixtures, T11–T12 renderer/environment, T17 effects and T38 audit.

Implemented behavior: reproducible synthetic cabin, foreground, grayscale window mask, three
repeatable exterior depth layers and independently scheduled landmark. The scene system handles
masked motion, global travel integration, fixed occlusion, rain/reflections and lighting without
train-specific renderer branches. T34 independently proves a café template. T38 imports the
unchanged supplied flattened train reference and renders it as an explicitly silent draft still.

Verification commands and results: actual media checks verify window confinement, alpha,
parallax continuity, wrap/landmark schedules, stop/restart, effects and chunk boundaries.
The T37 45-minute benchmark passes all 184 boundary comparisons. T38's reference walkthrough
retains the original image hash and verifies 300 frames / 480000 silent audio samples.
See the [final gates](../38-v1-acceptance.md).

Representative output/screenshot: [supplied asset audit](../09-implementation-review.md),
[café](../33-cafe-template.md), [long-form evidence](../36-longform.md),
[reference walkthrough](../evidence/t38-reference-walkthrough.json).

Machine and tool versions: M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2.

Remaining limits: flattened reference panoramas do not supply editable cabin/window/depth
layers or hidden-region repairs. Their real masks, wrap boundaries, panorama normalization,
day/dusk looks, geographic intent and rights need authored assets and Marco's review. Rendering
the original still does not complete that art preparation; all supporting software is implemented.


<a id="t09"></a>

## T09 Implement global timeline and curves

Status: complete

Scope: mandatory

Dependencies: T03, T04

### Implementation

Build rational frame/sample mapping, half-open intervals, keyframe interpolation and analytically integrated travel distance. Implement scoped scene/episode parameters and deterministic random timing expansion.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Acceleration-stop-restart remains continuous; any global frame is evaluated independently; same inputs compile to identical schedule.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T09: evaluate global curves and deterministic action timing`.

Implemented behavior: half-open frame queries, explicit loop phase, exact rational sample boundaries, constant/linear curve evaluation and prefix-based analytic integration, scene/episode scope precedence, duplicate/unit rejection, and versioned SHA-256 counter timing expansion with deterministic IDs. CLI `timeline inspect/expand` invokes the same services. Expanded channel conflicts fail rather than being dropped.

Verification commands and results: `make schemas && make check`: 20 schemas, Ruff passed, **148 tests passed**, eight opt-in media tests skipped. Eleven new timeline cases cover acceleration/stop/restart, every split's integral additivity, out-of-order queries, 30000/1001 fps, exact half-sample rounding, extrapolation, scope precedence, duplicate curves, whole random actions, collisions and a frozen SHA-256 vector independently verified with OpenSSL. Installed CLI frame 151 reports distance 184 px and audio sample 241600.

Representative output/screenshot: [timeline evidence](../evidence/t09-timeline.json), local `.local/t09-timeline/episode.json` and `expanded.json`; semantic data, not a rendered clip.

Machine and tool versions: same target Mac/Python as T05; no runtime dependency added.

Remaining limits: action/pose/prop and template compatibility are T10; renderer pixels and chunk equivalence are later gates. Synthetic schedules provide no artistic approval. [Exact semantics](../13-timeline.md).


<a id="t10"></a>

## T10 Compile actions and persistent state

Status: core complete; real-art review pending

Scope: mandatory

Dependencies: T07, T09

### Implementation

Implement pose transition graph, entry/hold/exit expansion, compatible facial overlay, prop preconditions/results, action conflicts and declared resets across scene cuts. Fixture graph can unblock coding before real art.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Missing transition and props fail clearly; one-shots occur once; blink does not restart body loop; observing exits to approved idle.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Real action pack required for visual gate.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T10: compile pose transitions and persistent scene state`.

Implemented behavior: resolves template/pack/clip versions and transitive hashes; expands loop windows through compatible entry/hold/exit paths; preserves one-shot durations, body-loop phase, prop preconditions/results and independent face timing. Rejects camera/fps/alpha/anchor/channel conflicts, missing transitions, body gaps, stale media and mismatched final states. Cuts preserve the declared prior final state or require `deliberate_reset`. Produces a deterministic `CompiledSnapshot`; `state_at` evaluates clips, props and travel at any global frame. Production mode rejects unapproved packs/media.

Verification commands and results: `make schemas && make check`: 20 schemas, Ruff passed, **160 tests passed**, eight opt-in media tests skipped. Twelve compiler cases cover entry/hold/exit, missing paths/props, one-shot repeat rejection, frame-rate/camera conflicts, baked face-channel conflicts, independent blink/body phase, prop updates at exact boundaries, explicit scene resets, tampered sources and frozen snapshot reopening. The semantic check detected T04's incomplete final travel metadata; the generator now declares the measured 780 px final distance instead of the default zero.

Representative output/screenshot: [compiled state report](../evidence/t10-compiled-state.json); fresh local `.local/t10-compiler-fixtures` with hash-addressed snapshot `7918e4895e38a8913938a216b91fc62650e4b78d19aca72dcfb54e4e88642521` (eight events, 15 transitive locks). No rendered/artistic approval claimed.

Machine and tool versions: same target Mac/Python as T05, no dependency added.

Remaining limits: real Tabi action-pack review remains dependent on T06/T07. Whole body-loop cycles are required at authored boundaries; no silent retiming/seam repair. Optional scene overlaps enter in T18; current compiler explicitly rejects them. [Compiler semantics](../13-timeline.md).


<a id="t11"></a>

## T11 Implement scene renderer and window masking

Status: core complete; real-art review pending

Scope: mandatory

Dependencies: T02, T08, T09

### Implementation

Create renderer interface and FFmpeg backend for normalized media, ordered layers, masks, clip placements and still/clip preview. Use scene capabilities rather than hardcoded train fields.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Synthetic pixel checks prove mask and occlusion correctness; approved train stills match template; color/alpha behavior documented.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Approved art for creative comparison.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T11: render locked scene layers with verified masks and alpha`.

Implemented behavior: renderer protocol, frozen registry verification, owned PNG normalization, template-ordered FFmpeg composition, grayscale coverage multiplied by source alpha, opacity, prepared action placement/phase, explicit crop/letterbox and cut concatenation. Frame and video requests share one graph builder. Draft/synthetic outputs carry a visible label. H.264 output is decoded and checked for exact count/rational timestamps/BT.709 format before atomic no-clobber publication; sources are checked again after rendering. Production requires an approved frozen snapshot and approved locked inputs.

Verification commands and results: `make check` passed Ruff/21 schema drift checks and **163 tests**, 14 opt-in media checks skipped. Six new actual-media cases passed: 12 still renders compared against independent Pillow composition within two RGB levels, both binary and partial alpha/masks; transition-spanning video verified at six sampled frames within 15 RGB levels; invalid masks, changed locks and injected verification failure never publish a final file. `make test-media`: **all 14 actual-media checks passed**, including the prior software/VideoToolbox gate. Normalization tests verify premultiplied-to-straight conversion, exact raw mask values, untouched originals and rejection of unknown production color.

Representative output/screenshot: [frame 37](../evidence/t11-synthetic-frame-37.png), [still report](../evidence/t11-still-report.json), [clip report](../evidence/t11-clip-report.json). Local `.local/t11-renderer/synthetic-static-scene.mp4` is a verified ten-second, 300-frame, 640×360, 30/1 H.264 clip with no audio. FFmpeg render subprocess measured 0.601 seconds; normalization/verification excluded. Visually inspected the frame's masks, blink, foreground occlusion and synthetic labels.

Machine and tool versions: M5 Pro/48 GiB, macOS 27.0.1, Python 3.11.16, Pillow 12.3.0, FFmpeg/ffprobe 9.0.2.

Remaining limits: real train-art comparison is pending T06/T08. T11 uses explicitly cropped stationary exterior layers; parallax/landmarks follow in T12. Effects and overlaps are rejected until their tasks. Backend accepts reviewed PNG sequences as the alpha interchange fallback; video sources need prepared frame exports. Bounded ranges cap at 7,200 frames/128 inputs. Audio mix is T16. This proxy is not 1080p/4K performance or creative approval.


<a id="t12"></a>

## T12 Add parallax and scheduled landmarks

Status: complete

Scope: mandatory

Dependencies: T09, T11

### Implementation

Implement shared travel-distance motion, wrapped repeatable strips, near/far coefficients, one-time sprites and tested crop limits.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Numbered-strip fixture stays continuous at speed changes and stops; landmark enters and exits once at intended frames.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T12: render continuous parallax and one-time landmarks`.

Implemented behavior: global travel integrals drive wrapped tile strips with per-layer depth factors and nonwrapping landmark sprites. Tile periods/crop coverage are verified from normalized pixels. Landmarks use explicit scene anchors, optional source pivots/crops, authored half-open intervals and optional `slot_id` for multiple sprite layers. Missing/ambiguous slots and incompatible strips fail. Fixture landmarks now have an explicit design-space origin at y=150.

Verification commands and results: `make schemas && make check`: 21 schemas, Ruff passed, **163 tests passed**, 18 media checks skipped. Focused T11/T12 media suite: **10 passed**. T12 compares 24 actual PNG renders with independent rational-distance/Pillow references at acceleration, stop, restart and wrap boundaries (at most two RGB levels). A decoded 300-frame clip has exactly one continuous landmark visibility interval and no later repeat. A preview beginning at global frame 149 retains the same restart phase. Wrong tile period and missing sprite slot fail without publishing.

The frame checks exposed and fixed the pinned FFmpeg build's one-based overlay-position counter; generic enable/crop counters remain zero-based. Both positional conventions are covered by actual renders.

Representative output/screenshot: [frame 149](../evidence/t12-synthetic-frame-149.png), [still report](../evidence/t12-still-report.json), [clip report](../evidence/t12-clip-report.json). Local `.local/t12-motion/synthetic-motion.mp4`: 300 frames, 640×360, 30/1, BT.709 H.264, no audio; render subprocess 0.815 seconds excluding preparation/verification. Visually inspected scenery depth, landmark placement, observing pose, occlusion and synthetic labels.

Machine and tool versions: M5 Pro/48 GiB, macOS 27.0.1, Python 3.11.16, Pillow 12.3.0, FFmpeg/ffprobe 9.0.2.

Remaining limits: synthetic technical verification does not approve real environment seams/hidden artwork. No reverse travel or automatic tiling repair. Audio, weather and approved art remain separate tasks.


<a id="t13"></a>

## T13 Add preview CLI and frozen snapshots

Status: complete

Scope: mandatory

Dependencies: T05, T10, T11, T12

### Implementation

Implement validate/compile/frame/preview commands, immutable snapshot asset locks, structured issue reports and global-frame range previews. Draft fixture previews have clear labels.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Proxy and stills use same compiler; out-of-range requests fail; edits create new snapshots rather than changing approved render inputs.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T13: expose frozen compilation and verified preview workflows`.

Implemented behavior: shared EpisodeService and validate/compile/frame/preview/snapshot commands; structured compile reports, saved immutable locks, global-frame ranges and explicit hash-bound snapshot review. Repeated compilation is idempotent; exports never overwrite existing files.

Verification commands and results: `make schemas && make check` passed 22 schemas, Ruff and 168 tests (19 opt-in media tests skipped). `uv run --frozen pytest tests/unit/test_episode_service.py --run-media tests/integration/test_preview_cli.py` passed six focused checks, including a real CLI frame/range render. Tampering, invalid ranges and invalid review attempts fail; draft edits preserve prior snapshot bytes.

Representative output/screenshot: [workflow and evidence](../15-preview-workflow.md), [frame 151](../evidence/t13-cli-frame-151.png), and local `.local/t13-cli/look-range.mp4` (132 verified frames, 960×540/30).

Machine and tool versions: M5 Pro, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2.

Remaining limits: video-only previews until T16; prepared PNG sequence interchange and the renderer's documented limits apply. T14's real-art pilot review remains pending, with no production approval claimed.


<a id="t14"></a>

## T14 Approve 90 to 120 second visual pilot

Status: real-art inputs and review pending

Scope: mandatory

Dependencies: T07, T08, T13

### Implementation

Assemble real Tabi pilot with idle/blink/look transitions, parallax, landmark and one lighting progression. Render representative close-up transition previews. Fix visible flaws before expanding actions.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Marco can watch an intentional clean scene; alpha, state, loop and parallax checks pass. Synthetic pilot alone is not completion.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Marco visual approval.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference:
Implemented behavior:
Verification commands and results:
Representative output/screenshot:
Machine and tool versions:
Remaining limits: T13's synthetic frame/range workflow is verified, but T07/T08 approved real character actions and separated train/environment art are unavailable. The reference choice in [T06 review](../12-tabi-art-review.md) remains pending. No real pilot or Marco visual approval is claimed. Independent audio/software work proceeds under PLAN's dependency exception.


<a id="t15"></a>

## T15 Implement music import and audio timeline

Status: complete

Scope: mandatory

Dependencies: T03, T05

### Implementation

Import finished WAVs and optional release metadata. Add sample-accurate trims, ordered placements, gain/fades, silence warnings and waveform proxies. Preserve distribution master unchanged.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

PCM reference checks prove boundaries/fades; invalid trims fail; source master hash remains unchanged.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Finished music for real episode.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T15: preserve music masters and validate sample timelines`.

Implemented behavior: exact WAV import reused from T05; bounded PCM reads, deterministic sample trims/gain/fades, waveform proxies with silence evidence, ordered timeline gap/overlap checks, and verified draft release metadata import. CLI and episode validation share the services.

Verification commands and results: `make schemas check` passed Ruff, 24 schema checks and 174 tests, with 19 media tests skipped. Six new cases compare independent PCM references and all split points, decode each supported integer bit depth, reject invalid trims/hashes, verify release metadata and prove original master bytes unchanged.

Representative output/screenshot: [audio workflow/evidence](../16-audio.md), [waveform data](../evidence/t15-tone-waveform.json), [sample timeline](../evidence/t15-audio-timeline.json).

Machine and tool versions: M5 Pro/macOS 27.0.1, Python 3.11.16, locked NumPy 2.4.6.

Remaining limits: integer mono/stereo PCM WAV interchange; actual resampling/mixing and AAC enter T16. Finished real music remains an input for T19 and was not fabricated or approved.


<a id="t16"></a>

## T16 Mix continuous audio and ambience

Status: core complete; listening review pending

Scope: mandatory

Dependencies: T15

### Implementation

Create continuous PCM mix, optional independent ambience loops/gain, technical format conversion and loudness/peak report. Encode final AAC only once.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

No seam clicks or unexpected truncation in fixtures; proposed level adjustment is explicit; ambience does not replace/remaster source music.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Marco listening review.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T16: mix continuous PCM and encode preview audio once`.

Implemented behavior: shared continuous float PCM mixer, 48 kHz technical preparation, independent ambience loops/crossfades, explicit gain, peak/loudness reports and a single AAC encode during verified preview mux. Integer/float/extensible/RF64 WAV support preserves distribution master bytes. Failed verification never publishes a final output.

Verification commands and results: `make schemas check` passed 25 schemas, Ruff and 177 tests. `make test-media` passed all 24 actual-media checks, including five new audio cases. Decoded PCM matches every reference byte, arbitrary ranges preserve global phase, resampling preserves tone frequency/count, loop seams stay within analytic sample bounds, and AAC timing/fidelity plus the single-encode count pass. Overloaded float samples remain unchanged until an explicit gain is supplied.

Representative output/screenshot: [audio workflow/evidence](../16-audio.md); local `.local/t16-audio/synthetic-mix.wav` and `synthetic-audio-preview.mp4` (480,000 stereo samples, 300 frames/30).

Machine and tool versions: M5 Pro/macOS 27.0.1, Python 3.11.16, NumPy 2.4.6, FFmpeg/ffprobe 9.0.2.

Remaining limits: real music and Marco listening review remain pending. Synthetic verification cannot approve a finished soundtrack. Long-form disk/memory estimates and resumable final assembly follow in T21/T22/T37; compressed/multichannel input needs explicit preparation.


<a id="t17"></a>

## T17 Add restrained lighting rain and reflections

Status: core complete; effect review pending

Scope: mandatory

Dependencies: T11, T14

### Implementation

Implement scene-scoped light curves, masked rain/reflections and explicit global phase origin. Add rain buildup/fade and maximum effect limits from reference stills.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Rain remains inside masks, never resets at chunk boundary, and matches approved subtle style; unsupported temporal effects are rejected.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Effect/palette approval.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T17: render bounded masked effects with global phase`.

Implemented behavior: explicit tint/rain/reflection slots, reviewed-template strength bounds, scoped curves, prepared alpha loop validation, independent global weather origin and masked layer composition. Effects fixtures are reproducible and visibly synthetic. Unsupported temporal histories fail.

Verification commands and results: `make check` passes 25 schemas, Ruff and 180 tests (26 media checks skipped). Three new unit cases validate limits/masks/phase/fps/loop requirements and fixture reproducibility. Two actual-media tests pass: thirteen independent still comparisons within three RGB levels and nonzero full/split preview ranges with global phase intact. Existing static/motion media regression tests also passed.

Representative output/screenshot: [effects documentation/evidence](../17-effects.md), [frame 151](../evidence/t17-effects-frame-151.png), local `.local/t17-effects-verified.mp4` (300 frames, 640×360/30, 480,000 stereo samples).

Machine and tool versions: M5 Pro/macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2. Latest fixture render/mix/mux interval 20.097 seconds; no 1080p/4K benchmark claim.

Remaining limits: actual effect/palette and real Tabi review remain pending. Synthetic strength bounds are technical fixtures, not approved art. CPU effect cost and long-form storage need T22/T37 evaluation; temporal blur/trails are unsupported.


<a id="t18"></a>

## T18 Author episode continuity and scene transitions

Status: core complete; story review pending

Scope: mandatory

Dependencies: T10, T13, T16, T17

### Implementation

Add cut/approved overlap semantics, scene initial/final state, storyboard beat notes and persistent object notebook data. Align a real short story to musical sections.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

No unintended gaps, duplicate Tabi or disappearing props; each music boundary and visual transition has an authored purpose.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Story outline and Marco review.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T18: author story beats and verify scene overlaps`.
Implemented behavior: story purposes and musical beat links, persistent object notebook, cut/reset continuity, matched-character and single-character overlaps. Entry state is evaluated at overlap start. Scoped curves use the active scene's override and bounds.
Verification commands and results: `make schemas check` passed 26 schemas, Ruff and 193 unit checks; actual media suite recorded in progress. Thirteen new unit cases and two media cases cover state divergence, metadata links, endpoints and global range parity.
Representative output/screenshot: [workflow and evidence](../18-story-continuity.md), including a ten-second 300-frame preview with continuous 480,000-sample audio and inspected frame 162.
Machine and tool versions: macOS 27.0.1 / M5 Pro, Python 3.11.16, FFmpeg/ffprobe 9.0.2, Pillow 12.3.0.
Remaining limits: real narrative, source artwork/music and Marco review are unavailable. Conservative overlaps only; different poses require cuts. No production approval or publishable episode is claimed.


<a id="t19"></a>

## T19 Complete first short music story

Status: original music, approved art and creative review pending

Scope: mandatory

Dependencies: T18

### Implementation

Produce a 5–10-minute episode from approved artwork and finished original music, with beginning/development/ending. Inspect all transitions and retain editable manifest/source evidence.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Episode is publishable on creative grounds according to Marco; full-duration audio/video review recorded; no placeholder assets remain.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Original music and Marco creative approval.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T19: record short-story production input gate`.
Implemented behavior: T18's shared compiler/renderer and storyboard report now support the required scene/story structure. Production is deliberately not marked complete.
Verification commands and results: T18 passed all 28 actual-media checks and 193 unit checks using visibly synthetic assets. Those checks prove implementation, not this creative acceptance gate.
Representative output/screenshot: [T18 developmental evidence](../18-story-continuity.md); no purported publishable 5–10-minute episode exists.
Machine and tool versions: T18 evidence was captured on the target M5 Pro with FFmpeg 9.0.2.
Remaining limits: the supplied flattened references are not an approved, separated action/environment pack. Finished original music masters/credits and Marco's reference/story approval have not been supplied in this session. Pending requests identify the exact reference hashes and ask for the music folder. Once supplied: freeze approved versions, author the full story to the real tracks, render 5–10 minutes, inspect every transition and retain Marco's full-duration creative review. T20 and other independent engineering work continue meanwhile.


<a id="t20"></a>

## T20 Implement jobs cancellation and persistence

Status: complete

Scope: mandatory

Dependencies: T13

### Implementation

Implement queue, journal, safe subprocess ownership, atomic chunk commit, progress and errors. Cancel only owned jobs; crash recovery marks interrupted work.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Injected process/worker failure retains verified outputs and useful diagnostics; cancel preview cannot kill unrelated render.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T20: persist owned jobs and recover verified progress`.
Implemented behavior: durable FIFO queue, hash-linked immutable event journal, atomic checkpoint recovery, worker lease, scoped child-process cancellation, verified chunk/output publication and useful failure logs. CLI and future API share the same Python service.
Verification commands and results: `make schemas check` passed 27 schemas and 201 unit checks. Eight new unit cases and three actual-media cases cover crashes, cancellation isolation, changed inputs and real global-range outputs; broader media result is recorded in progress.
Representative output/screenshot: [job/event evidence](../evidence/t20-jobs.json), [verified preview report](../evidence/t20-preview-report.json), and [operations](../19-jobs.md). A 46-frame verified chunk survived an actual worker exit before export publication.
Machine and tool versions: M5 Pro / macOS 27.0.1, Python 3.11.16, FFmpeg/ffprobe 9.0.2.
Remaining limits: T20 runs one bounded chunk; chunk planning/resume and continuous final assembly follow in T21. Background local-service lifecycle follows in T26. Recovery retains interrupted artifacts and never signals saved PIDs; explicit cleanup follows in T22. No production/art approval is implied.


<a id="t21"></a>

## T21 Implement chunk planner and resumable assembly

Status: complete

Scope: mandatory

Dependencies: T16, T18, T20

### Implementation

Plan exact global ranges, effect handles where supported, compatible codec/timestamps, validated concat and fallback, continuous audio final mux. Add backend/profile fingerprint checks.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Monolithic/chunked frames agree to reference tolerances; final duration within one frame; interrupted job resumes safely.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Target-Mac encoder verification later.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T21: resume verified video chunks and assemble continuous audio`.
Implemented behavior: exact bounded global ranges, cut-aware planning, zero handles for supported spatial effects, frozen profile/pipeline/toolchain checks, full verified-chunk reuse, codec-aware concat and explicit verified re-encode fallback, one continuous PCM/AAC mux, safe interrupted-export reconciliation.
Verification commands and results: `make schemas check` passed 27 schemas, Ruff and 214 unit checks. Thirteen new unit cases and five new chunk-media cases pass; crash tests additionally exercise before/after-publication restart and conflicting-export preservation. Full suite outcome is recorded in progress.
Representative output/screenshot: [workflow and evidence](../20-chunk-assembly.md), including the 300-frame resumed story with 480,000 AAC samples, unchanged retained neighbour, and decoded frame 174.
Machine and tool versions: M5 Pro / macOS 27.0.1, Python 3.11.16, FFmpeg/ffprobe 9.0.2; software H.264 at 30 and 30000/1001 fps.
Remaining limits: temporal-history effects remain unsupported. T20 unplanned jobs require new submission. Cross-job cache reuse/prune follows in T22; final-resolution/VideoToolbox quality and sustained long-form performance follow in T23/T37. No production artwork/music approval is implied.


<a id="t22"></a>

## T22 Implement caches storage estimates and pruning

Status: complete

Scope: mandatory

Dependencies: T05, T21

### Implementation

Hash all relevant media/parameters/tool versions; reuse normalized media and verified chunks; distinguish audio/video invalidation. Add disk estimates and explicit safe prune.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Content change invalidates stale chunks; audio-only change can reuse video; corrupt chunk rerenders; pruning preserves source and snapshots.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T22: reuse verified media and guard cache pruning`.
Implemented behavior: project-local normalized PNG and video chunk caches with content/runtime/tool fingerprints, audio-independent video keys, independent job copies and fresh decode verification; typed disk estimates and worker preflight; explicit inventory-bound pruning with source, snapshot and process-ownership protection.
Verification commands and results: `make check` passes Ruff, 31 schemas and 222 unit checks. `make test-media` passed all 39 actual-media checks; the expanded cache/source-content test passed again after runtime fingerprints were added. Eight new unit cases cover cache/storage safety. The actual-media test measures changed AAC gain, zero video graphs after an audio-only edit, exactly one graph after cache corruption, and rerender after changed motion/source bytes.
Representative output/screenshot: [workflow](../21-cache-storage.md) and [retained run evidence](../evidence/t22-cache.json). The 300-frame story used 4, 0 and 1 video graphs for initial, audio-edited and cache-repaired runs respectively, with one AAC encode each. Pruning removed 29 managed entries and preserved all 54 checked source/snapshot/export files. Local clips remain under `.local/t22-cache/Marco 東京 project/exports/` and are ignored.
Machine and tool versions: M5 Pro / macOS 27.0.1; Python 3.11.16, Pillow 12.3.0, FFmpeg/ffprobe 9.0.2.
Remaining limits: encoded size is an estimate; concurrent external disk use is not reserved. Cache reuse is project-local and conservative. Unknown interrupted scratch data remains available for manual inspection rather than unsafe automatic deletion. No art or music approval is implied.


<a id="t23"></a>

## T23 Verify final export profiles

Status: complete

Scope: mandatory

Dependencies: T02, T21, T22

### Implementation

Add proxy/1080p/4K presets, color/timestamp/frame probes, final encode quality checks and web metadata placement. Benchmark worst-case 60 seconds on target Mac.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Report actual time/memory/quality; no unsupported encoder silently selected; export decodes correctly with expected dimensions/audio/color.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

M5 Pro benchmark.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T23: verify final export profiles and target-Mac performance`.

Implemented behavior: shared explicit proxy/1080p/4K profiles, selected-encoder availability checks,
AAC-LC delivery rates, High Profile/CABAC/closed GOPs, BT.709, bounded Fast Start inspection,
exact frame/PTS and audio-sample verification, and a CLI for independently verifying completed
exports. Hardware B frames are disabled after a reproduced timestamp defect. Effect opacity now
uses per-frame timeline values and an alpha LUT, with independent pixel parity checks.

Verification commands and results: `make check` passes Ruff, 32 schemas and 224 unit tests;
`make test-media` passes all 48 actual-media tests in 195.12 seconds. These include all three presets
with software and hardware encoding, damaged-export rejection, fractional-rate hardware chunks,
global-range/step opacity parity, recovery and prior audio/story gates. Both 60-second stress jobs
verify 1,800 frames / 2,880,000 samples. Software 1080p: 94.22 seconds, 19.10 fps, 3.58 GiB sampled
RSS. Hardware 4K: 260.69 seconds, 6.90 fps, 3.15 GiB. All six sampled quality checks pass per run.

Representative output/screenshot: [methods, reports and inspected PNGs](../22-export-profiles.md).
MP4s remain ignored in `.local/t23-1080-software-lut/exports/` and
`.local/t23-4k-hardware-lut/exports/`.

Machine and tool versions: Apple M5 Pro / 48 GiB, macOS 27.0.1 arm64, Python 3.11.16,
FFmpeg/ffprobe 9.0.2; exact identities are in the retained reports.

Remaining limits: synthetic geometry cannot approve real Tabi art or music. The 4K stress export
scales a native 1080p composition; native 4K and long-form measurements remain T37. RSS excludes
kernel/unreported GPU allocations. Bitrate targets are not measured constant rates. No publishing
or platform eligibility is implied.


<a id="t24"></a>

## T24 Build release preparation exporter

Status: core complete; production inputs and review pending

Scope: mandatory

Dependencies: T19, T23

### Implementation

Generate release folder, factual track list, artist/credits, chapters when valid, rights/disclosure notes, render report and snapshot. Separate public metadata from private evidence.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Bundle matches approved export; unknown IDs remain null; pending rights prevents ready label; no automatic upload or leaked private documents.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Credits/licences and release decisions.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T24: prepare verified release bundles with private evidence`.

Implemented behavior: strict release preparation/public/report contracts, revision-guarded drafts,
verified export and report checks, factual sample-based track lists, valid chapter export, explicit
hash-bound audiovisual and metadata/disclosure reviews, pending-rights gates, approved PNG thumbnail
selection, public allowlists, private evidence and atomic independent bundle copies. CLI invokes the
shared Python service; there is no upload path.

Verification commands and results: `make schemas check` passes Ruff, 36 schemas and 227 unit checks.
`pytest --run-media tests/integration/test_release_export.py` passes its actual render/copy/privacy,
pending-review, revision, concurrent-edit and corruption checks. Unit cases cover chapter boundaries,
formula-safe CSV and review invalidation. The CLI prepares an actual 60-second draft from the T23
1080p export, preserves its video hash, exports valid 00:00/00:20/00:40 chapters and retains null IDs.

Representative output/screenshot: [workflow and evidence](../23-release-preparation.md);
local `.local/t23-1080-software-lut/bundles/t24-draft/`. MP4 remains ignored.

Machine and tool versions: Apple M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16,
FFmpeg/ffprobe 9.0.2.

Remaining limits: the ready production bundle acceptance depends on T19's approved artwork,
original music, credits/licences and human audiovisual/disclosure decisions. The working fixture
bundle is explicitly synthetic and blocked from readiness. Whole-second chapter authoring is
conservative at rational fps; private source-document backup follows in T32. No human approval or
platform status is inferred.


<a id="t25"></a>

## T25 Design web app pages and browser playback spike

Status: complete

Scope: mandatory

Dependencies: T03, T13

### Implementation

Create wireframes for every page in the web app spec. Spike a TypeScript/Vite frontend with schema-checked DTOs and native HTML video. Pin frontend tools, verify H.264/AAC playback, seeking and audio in Safari and Chromium on the target Mac, and use renderer stills for exact frame inspection. Keep all compilation/render semantics in Python. Record file selection, same-origin artifact serving and local distribution tradeoffs. No Node server is required at runtime.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

All pages have reviewable wireframes; prototype opens/plays/seeks an actual proxy on Mac in both browsers; keyboard/resize behavior checked. User visual review stays separate from technical completion. Mock wireframes never count as implemented production flows.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Marco UI preference review and macOS.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T25: build browser wireframes and verify native playback`

Implemented behavior: twelve navigable design pages, strict generated DTOs and precompiled
validators, native video with actual decoded-audio diagnostics, Python exact-frame inspection,
keyboard controls and responsive layout. Static build is served by a synthetic-only Python spike.

Verification commands and results: `make check` (36 schemas, 229 unit checks); browser
`npm run check`, `npm test` (two checks), `npm run build`; actual Safari/Chrome play, seek,
decoded audio, frame inspection, resize and HTTP range/boundary checks pass.

Representative output/screenshot: [T25 evidence and all page screenshots](../24-browser-foundation.md).

Machine and tool versions: M5 Pro / macOS 27.0.1; Safari 27.0.1, Chrome 154; Node 25.8.2,
npm 11.14.1, Vite 8.3.2 and TypeScript 7.0.2, locked dependencies.

Remaining limits: UI preference/listening approval remains with Marco. Eleven pages are
wireframes, not production flows. Authenticated service and installed distribution follow
in T26/T33. Initial all-schema bundle size warning is documented.


<a id="t26"></a>

## T26 Implement authenticated local service and worker lifecycle

Status: complete

Scope: mandatory

Dependencies: T20, T25

### Implementation

Add typed API adapters and a Python launcher owning the local worker. Implement loopback ephemeral port, readiness/protocol handshake, one-time browser bootstrap, cookie/bearer session authentication, Host/Origin and CSRF checks, job SSE and authenticated byte-range artifact serving. Serve the built UI from the API origin. Bound filesystem browsing/import to registered roots. Browser closure leaves owned jobs running; explicit shutdown and restart preserve the job ledger.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Launcher and browser can launch/connect/recover safely; port collision and version mismatch handled; logs/URLs omit secrets; all routes call shared core. Test bootstrap replay, missing auth on media/SSE, CSRF, foreign origins, traversal/symlink escape, and browser reconnect without duplicate jobs.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T26: authenticate local worker sessions and media`

Implemented behavior: owned Python launcher/private readiness handshake, ephemeral loopback
server, one-time browser tickets, cookie/bearer/CSRF/origin controls, registered-root chooser,
shared-core durable job API, SSE replay, authenticated verified byte ranges and safe shutdown.

Verification commands and results: `make check` (42 schemas, 238 unit checks); frontend checks,
two tests and build; nine focused HTTP/lifecycle checks plus actual render/cancel/restart/resume
test pass. Native Safari/Chrome bootstrap, refresh, media, seek, expiry and reopening verified.

Representative output/screenshot: [Local service evidence](../25-local-service.md), including
300-frame/480,000-sample resumed output and six browser screenshots.

Machine and tool versions: target M5 Pro/macOS 27.0.1; Safari 27.0.1, Chrome 154; Python 3.11.16,
FastAPI 0.142.2, Starlette 1.7.0, Uvicorn 0.54.0, external FFmpeg/ffprobe 9.0.2.

Remaining limits: production pages/import streaming follow T27–T32, installation packaging T33.
The documented test-client deprecation and frontend bundle-size warnings do not fail the checks.
No creative approval or publication is implied.


<a id="t27"></a>

## T27 Implement projects assets and episode setup pages

Status: complete

Scope: mandatory

Dependencies: T05, T25, T26

### Implementation

Build real project create/open, missing-drive relink, asset browser/inspector/import/version/approval and new episode forms. Browse only launcher-registered roots; stream selected-file copies into local import staging without requiring browser filesystem extensions. Include empty/error/loading, inaccessible-path, interrupted-upload and stale-revision states.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

User creates/open/reopens project and imports media through UI; draft/rights status accurate; no mock data left in completed flows.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: T27 implementation commit (see Git history).
Implemented behavior: bounded project create/open/relink with identity checks; durable recent locations; asset catalog/inspection/provenance/version/proxies/relink/hash approval; resumable 4 MiB browser uploads; authored metadata import; still template and new episode forms with Python music placement and duration rejection.
Verification commands and results: `make check` passed 242 tests (50 opt-in media tests skipped); focused HTTP checks passed 13 tests, including actual PNG import/proxy streaming, upload restart/tamper/CSRF/size limits, stale draft rejection, project identity mismatch and durable reopen; `npm run check`, `npm test`, `npm run build` passed. Chrome created `.local/t27 UI 東京`; Safari opened it, selected the local PNG with its native file picker, imported it as synthetic, created a still template and saved `browser-draft` (300 frames).
Representative output/screenshot: [import](../evidence/t27-safari-import.png), [episode](../evidence/t27-safari-episode.png); ignored project `.local/t27 UI 東京/` and source `.local/t27-synthetic.png` remain local.
Machine and tool versions: macOS 27.0.1 arm64 / M5 Pro, Safari 27, Chrome 154, Python 3.11.16; locked frontend and Python dependencies.
Remaining limits: linked paths and authored multi-layer/pack metadata use validated JSON forms. Recent locations are disposable launcher-cache data; missing media still requires the original matching bytes. This task does not approve artwork, licences or music. Chrome automation could not directly set file inputs because its extension lacks file-URL access; the complete native Safari upload flow passed without changing that permission.


<a id="t28"></a>

## T28 Implement story editor and timeline

Status: complete

Scope: mandatory

Dependencies: T09, T10, T18, T27

### Implementation

Add scene cards, frame snapping, lanes, keyframe inspector, action selection, continuity notes, undo/redo and atomic autosave. Expose only supported effects.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Edits roundtrip to core models; invalid states explain fixes; undo restores document; moving actions does not silently retime clips.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: T28 implementation commit (see Git history).
Implemented behavior: shared Python editor commands; scene cards/append/cut/state and transition edits; server-derived frame/sample lanes; integer frame cursor, zoom, action drag/numeric movement; registered action selection; declared-parameter keyframes; story beats and continuity notebook; serialized undo/redo, atomic revision-guarded saves and debounced title/purpose autosave.
Verification commands and results: `make check` 246 passed, 50 opt-in media tests skipped; targeted editor/workspace tests 8 passed after the persistent-object lane update; frontend check/build passed and four browser-contract/history tests passed. Core tests confirm preserved action durations, invalid overlap/range rejection without disk changes, stale-tab rejection, undo as a new revision, notebook validation and exact sample labels. Chrome UI: title autosaved at revision 1, undo restored title at revision 2, redo revision 3, scene append produced [300,360), restart reopened revision 4, a second tab's stale edit was rejected, reload showed revision 5, notebook saved revision 6 and selected frame/zoom survived navigation.
Representative output/screenshot: [timeline](../evidence/t28-timeline.jpg), [conflict](../evidence/t28-conflict.jpg), [notebook](../evidence/t28-notebook.jpg); ignored `.local/t27 UI 東京/episodes/browser-draft.json` and its `.backups` contain the real browser edits.
Machine and tool versions: M5 Pro / macOS 27.0.1, Chrome 154, Python 3.11.16 and pinned dependencies.
Remaining limits: explicit paired edits and complex state/transition/beat data use validated JSON inspectors; this is a focused authoring UI, not a rig editor. Undo history is session-local (100 commands); disk revision backups survive restarts. Title/purpose fields autosave, while structured inspectors save on Apply. Media import/render is never included in document undo. Actual art/story approval remains pending separately.


<a id="t29"></a>

## T29 Implement preview and frame inspection page

Status: complete

Scope: mandatory

Dependencies: T13, T26, T28

### Implementation

Add renderer proxy generation, HTML video controls/seeking, exact Python-rendered frame requests, review markers, stale-cache display and request debouncing. Use the cookie-authenticated range endpoint, not secrets in media URLs or a browser-side compositor.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Editing marks old proxy stale; still/frame cursor semantics consistent; player handles missing media, expired sessions and worker failure. Safari and Chromium playback, seek, audio and refresh/reconnect pass on the target Mac; approximate browser time is never presented as an exact rendered frame.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

macOS playback validation.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T29: connect renderer previews and exact frame review`.
Implemented behavior: persisted preview snapshots, durable proxy queue, previous verified video retention, input/renderer staleness, cancellable debounced exact PNG requests, authenticated media, integer-frame markers and frame/zoom continuity.
Verification commands and results: `make check` 247 passed / 51 opt-in skipped; focused preview unit + actual-media checks 2 passed; frontend contract/type/format/build and four tests passed. Safari 27.0.1 and Chrome 154 played and sought the new 300-frame proxy, measured nonzero decoded audio, refreshed without re-queuing, and displayed the same exact frame-150 PNG hash. Edit → stale and worker-stop error states were checked. Rapid 148 → 149 → 151 scrubbing settled on frame 151.
Representative output/screenshot: [Chrome](../evidence/t29-chrome-preview.jpg), [Safari exact frame](../evidence/t29-safari-frame.jpg), [stale snapshot](../evidence/t29-stale.jpg); local `.local/t25-browser/exports/previews/` and `previews/frames/`.
Machine and tool versions: target M5 Pro / macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2.
Remaining limits: synthetic media only; artistic/listening approval is manual. Stills are retained as verified project artifacts; repeated requests render again. Snapshot staleness is refreshed on navigation, focus and explicit refresh, not continuous background hashing. No MP4 is tracked.


<a id="t30"></a>

## T30 Implement audio page and release metadata forms

Status: core complete; listening review pending

Scope: mandatory

Dependencies: T15, T16, T27

### Implementation

Add WAV import, waveform proxy, ordered tracks, trims/gain/fades, ambience, effective duration and clipping/loudness report.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Audible preview reflects edits; source stays unchanged; conflicts with story duration visible rather than silently repaired.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Marco listening review.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T30: edit audio placements and audition measured mixes`.
Implemented behavior: sample-based track/ambience editor, Python timing proposals and conflict rejection, ordered music placement, gain/trims/fades/loops, waveform proxies, guarded saves/undo/redo, measured 120-second auditions, and factual draft music metadata. WAV import reuses the streaming Assets workflow.
Verification commands and results: `make check` 248 passed / 52 opt-in skipped; focused audio editor + real HTTP media checks 2 passed. Actual mixed PCM matches the requested -6 dB change within 1e-7, fades start at zero, source WAV hashes remain unchanged, malformed metadata and stale revisions reject. Frontend checks/build/four tests pass. Chrome rejected a 600,000-sample placement against 480,000 samples, saved gain/fades, undid/redid, drew the source waveform, played the complete 10-second float WAV, and saved metadata with null ISRC/UPC.
Representative output/screenshot: [audio editor](../evidence/t30-audio-editor.jpg), [duration conflict](../evidence/t30-duration-conflict.jpg); local `.local/t25-browser/audio/previews/` and `releases/music-release.json`.
Machine and tool versions: M5 Pro, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2, Chrome 154.
Remaining limits: Marco's listening review and original music remain pending. Auditions are bounded to 120 seconds and retained separately; full-length audio verification uses the final render workflow. Fields are applied explicitly; unsaved drafts warn on browser close. No artistic approval was inferred.


<a id="t31"></a>

## T31 Implement render queue settings and recovery UI

Status: complete

Scope: mandatory

Dependencies: T22, T23, T26

### Implementation

Build profile/output chooser, space estimate, frozen snapshot queue, progress/ETA, cancel/pause-after-chunk/resume, diagnostics, tool/media/cache settings.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

UI responsive during renders; crash restart recovery works; cache removal safe; ETA labeled measured estimate.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

None.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: T31 implementation commit.
Implemented behavior: [Queue/settings guide](../30-render-queue.md): frozen export planning and storage estimates, measured ETA, pause at verified boundaries, cancel/resume/verify, guarded preferences/tool config backups, registered roots and protected cache cleanup.
Verification commands and results: `make check` 252 passed / 53 opt-in skipped; 57 schemas checked. `make web-check` and frontend build passed (four browser contract/history tests). Two actual-media checks passed, including pause during FFmpeg, 30 retained frames and resume to 90 frames / 144000 samples. HTTP ownership, dry planning, revision/hash conflicts and protected cache selection tested. Existing T26/T21 crash recovery checks remain applicable.
Representative output/screenshot: `.local/t25-browser/exports/t31-browser.mp4`, verified 300 frames, 1920×1080, 480000 audio samples. Chrome paused after 180 frames and resumed; Settings remained responsive during rendering. [Resume/ETA](../evidence/t31-resumed-queue.jpg), [verified queue](../evidence/t31-verified-queue.jpg), [preferences/cache](../evidence/t31-settings.jpg).
Machine and tool versions: Apple M5 Pro, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2, Chrome 154.
Remaining limits: progress advances on verified chunk boundaries; ETA excludes final assembly. Cache cleanup is explicit. Runtime tool paths apply after restart. Synthetic media is not creative approval. Browser validator bundle still triggers the build size advisory.


<a id="t32"></a>

## T32 Implement release page and project portability

Status: core complete; production rights and disclosure review pending

Scope: mandatory

Dependencies: T24, T30, T31

### Implementation

Build release checklist/bundle preview, metadata edits, manual URL/claim notes, backup export/import and project relink flow. Preserve approval tied to hash.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

No invented platform status; portable project opens with verified copied assets; backups restore edits and approved snapshots.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Rights/disclosure decisions.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: T32 implementation commit.
Implemented behavior: [Release/backup guide](../31-release-and-backups.md). Saved release forms, verified checklist/public metadata preview, exact-hash reviews, draft/ready bundle export, authenticated public artifact links, private manual URL/claim notes. Private directory backup/restore copies linked media into bounded embedded roots without rewriting approved documents. Projects already supplies identity-checked relinking.
Verification commands and results: `make check` 255 passed / 54 opt-in skipped, 61 schemas; frontend checks/build/four tests pass. Four focused backup tests pass after final additions (external drive disconnected, reviewed-document bytes preserved, private source package copied, missing historical sources warned, corruption/symlink/traversal/concurrent edit rejected). Actual HTTP media test passes: render → release blockers/draft bundle → guarded edit → backup → restore → identical frame-150 PNG → restored video verification and byte match. Copied bytes are rehashed before publication.
Representative output/screenshot: `.local/t25-browser/bundles/t32-browser-draft/`, `.local/t32-private-backup/` (186 files / 23297976 bytes), `.local/t32-restored-東京/`. Chrome exercised draft save/inspection/export/backup/restore and the restored release checklist. [Bundle](../evidence/t32-release-bundle.jpg), [restored project](../evidence/t32-restored-project.jpg).
Machine and tool versions: Apple M5 Pro, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2, Chrome 154.
Remaining limits: private uncompressed folders, no encryption or archive transport; copy the complete folder. Pause or finish jobs before backup. Missing historical originals are listed explicitly; required media must be available. Human production rights/disclosure decisions remain pending, and synthetic material never becomes upload-ready. Nothing was published.


<a id="t33"></a>

## T33 Package and verify local web app launch

Status: complete

Scope: mandatory

Dependencies: T26, T29, T31, T32

### Implementation

Build the frontend into the Python distribution, provide local launch/install instructions and an actionable Python/FFmpeg dependency check. Test installation outside the checkout on Apple Silicon with no Node/JDK requirement at runtime. Review licences before bundling any runtime/media binaries. Native DMG and signing are deferred.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Installed local launcher verifies worker readiness and opens the browser outside the development checkout. It runs a synthetic pilot, plays/seeks the proxy in Safari/Chromium, preserves renders across tab close, and resumes interrupted work. Document required external dependencies, permissions and exact setup steps; do not equate developer launch with a portable installation.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Apple Silicon Mac and supported Safari/Chromium versions.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T33: package and verify the installed local web app`.

Implemented behavior: a checked static frontend and exact third-party licence notices are
included in the wheel/sdist; stale/missing/altered UI builds fail packaging. Editable developer
setup remains possible before npm installation. `setup-check` validates Python, bundled hashes,
FFmpeg capabilities and storage. Default launch creates the configured project folder; explicit
registered roots remain existing bounded folders. [Install guide](../32-installation.md).

Verification commands and results: `make check` **259 passed / 54 opt-in skipped**, 61 schemas;
frontend checks, four tests and build passed; `make package` produced a wheel, sdist and locked
hashed runtime requirements. Wheel inspection found the static index, JS/CSS, notices and build
manifest, with no MP4, fonts or runtime binaries. Installed that wheel with locked dependencies
into a new Unicode-path environment outside the checkout. With Node absent from runtime PATH,
`setup-check` returned ready and verified installed frontend hashes. All imports resolved to
that environment's site-packages.

The installed Chrome UI queued a 90-second synthetic proxy, then the browser tab was closed.
The worker continued, retained 1,800 frames on cancellation/restart and the new browser session
resumed the same job to **2,700 frames / 4,320,000 samples**. Both retained chunk SHA-256s
remained unchanged. Chrome 154 and Safari 27.0.1 played and sought near 45 seconds, measured
audio RMS around 0.0676 and displayed exact frame 1350 with identical PNG hash
`51fb4bbae9d48a00874e04007b85f32a362ebb9842318d3f606010f6be63b978`.
The installed package also passed all three real process-exit recovery cases from
`test_actual_worker_crash_retains_verified_video_and_continuous_audio` (3 passed in 19.54 s):
before publication, after publication and preservation of a conflicting user destination.

Representative output/screenshot: [Chrome installed preview](../evidence/t33-installed-chrome.jpg).
Local pilot `/private/tmp/tabi-t33-install-wcc5wlhg/SYNTHETIC installed pilot/exports/previews/e0f9f8dcfb2446aba03203f6bee14823.mp4`,
SHA-256 `2640b45dd2dd27927198bca98648bc717ac11314cac4198cae7368c3eb344580`.
The wheel and locked requirements are retained in ignored `.local/packages/`.

Machine and tool versions: M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2,
uv 0.11.0; Node 25.8.2/npm 11.14.1 for build only.

Remaining limits: external Python/FFmpeg installation is required; no DMG/signing/notarization
or automatic updates. Browser validators form a large static JS chunk (about 265 KB gzip);
Vite reports an advisory. Tests qualify this Mac, not other OS/runtime combinations. Synthetic
media does not satisfy real artwork, original music, listening or publication approval.


<a id="t34"></a>

## T34 Add café scene template and prove extensibility

Status: core complete; café art review pending

Scope: mandatory

Dependencies: T11, T28

### Implementation

Prepare simple café pack/window view and alternate anchor, slow outside pedestrians/clouds rather than train scrolling. Use same timeline/assets/audio/render architecture.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Café renders and edits without adding train-specific assumptions to core; compatible action pack declared explicitly.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Café art or approved fixture for technical gate.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T34: prove café templates with shared rendering and editing`.

Implemented behavior: `tabi fixtures --profile cafe` generates an independent static-room
template, window mask, slow cloud/pedestrian motion, alternate anchor and explicitly compatible
action pack. Existing compiler, editor, renderer, audio and chunk services are unchanged.

Verification commands and results: two focused unit checks pass; actual-media integration
passes in 6.86 s, producing 300 frames and 480000 audio samples in two verified chunks. Pixel
checks prove fixed room/buildings, masked motion, correct anchor and tabletop occlusion.
Wrong-template packs fail without changing the saved episode. `make check` passes 261 checks
with 55 opt-in media cases skipped and 61 schemas current.

Representative output/screenshot: [frame 150](../evidence/t34-cafe-frame.png);
local `.local/tests-t34/test_cafe_static_architecture_0/Café 東京/exports/cafe.mp4`.
[Reproduction and semantics](../33-cafe-template.md).

Machine and tool versions: M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2.

Remaining limits: the geometric artwork and audio are synthetic, unapproved and excluded from
publication. The passing pedestrian is a translating silhouette, not a reviewed walk cycle.
Approved café art and Marco's creative review remain required.


<a id="t35"></a>

## T35 Add optional activity and outfit packs

Status: core complete; activity/outfit art review pending

Scope: optional expansion

Dependencies: T07, T10, T34

### Implementation

Prepare sipping/read/sleep entry-loop-exit or another approved activity with prop ownership. Add camera/outfit compatibility and pack version UI.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Every activity has transitions and consistent props; invalid cross-pack action fails; approved reference remains stable.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

New animation/art review.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `T35: validate activity props and explicit outfit packs`.

Implemented behavior: strict scene/pack/clip outfit compatibility, explicit camera checks,
cut/reset requirements for wardrobe changes, an atomic pack-version switch in Story and a
version/compatibility inspector. Reproducible synthetic sipping/reading/sleeping fixtures have
matching entry-loop-exit frames and cup/book ownership. Approved source/reference files remain
untouched; optional empty fields retain old document hashes.

Verification commands and results: four focused unit checks pass; actual rendering/export
passes in 10.34 s (300 frames, 480000 samples, four verified chunks). Endpoint pixels, prop
preconditions, camera/outfit mismatches, missing actions, atomic saves, new versions and source
preservation are covered. `make check`: 265 passed / 56 opt-in skipped, 61 schemas. Frontend
type/schema/format checks, four tests and build pass. Chrome switched amber → blue, rejected a
missing-action pack and reloaded the unchanged saved revision.

Representative output/screenshot: [browser controls](../evidence/t35-pack-controls.jpg),
[sipping](../evidence/t35-sipping.png), [reading](../evidence/t35-reading.png),
[sleeping](../evidence/t35-sleeping.png), [outfit](../evidence/t35-outfit.png).
Local `.local/tests-t35/test_real_activity_transitions0/Activity café 東京/exports/activities.mp4`.
See [operation details](../34-activity-packs.md).

Machine and tool versions: M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2,
Chrome 154.

Remaining limits: reviewed Tabi activity drawings and wardrobe designs remain blocked on T07
and human art approval. The two geometric outfits are synthetic compatibility fixtures, not
new Tabi designs. No real reference approval or publication readiness is claimed.


<a id="t36"></a>

## T36 Add optional local ComfyUI asset bridge

Status: core complete; real model/workflow validation pending

Scope: optional expansion

Dependencies: T05, T26

### Implementation

Use installed server API to submit versioned allowlisted workflows, monitor progress/history, import results as draft and record model/workflow hashes. Add explicit endpoint/offline/error settings.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

Render of approved episode works when ComfyUI is offline; generated outputs never auto-approve; downloads/custom-node changes require explicit choice.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Approved model/workflow and disk budget.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: T36 implementation commit (this change).
Implemented behavior: shared optional local generation service, strict workflow/policy/run contracts,
version/hash allowlisting, durable prompt IDs and no blind retries, queue/history reconciliation,
bounded verified draft imports with factual provenance, CLI and Settings controls. No installers,
model downloads, remote endpoints or global interruption.
Verification commands and results: 18 focused HTTP/CLI/API tests passed; real offline-generation
render check passed (30 frames / 48000 decoded samples). make check: 283 passed / 57 opt-in
skipped; 64 schemas. Frontend checks, four tests and production build passed. Chrome submitted
one synthetic protocol workflow, imported only on explicit request and displayed draft/rights
pending; offline status preserved imported history.
Representative output/screenshot: docs/evidence/t36-generation.jpg; local offline clip documented
in docs/35-local-generation.md. All fixtures explicitly synthetic and unapproved.
Machine and tool versions: M5 Pro / 48 GiB, macOS 27.0.1 arm64, Python 3.11.16,
FFmpeg/FFprobe 9.0.2, Chrome 154, Node 25.8.2 (build only).
Remaining limits: no approved actual ComfyUI workflow/model supplied; real inference and output
quality are pending. Definition hashes do not attest custom-node code or model-directory mapping.
External weights are not bundled. See docs/35-local-generation.md for operations and bounds.


<a id="t37"></a>

## T37 Benchmark long form and tune resource use

Status: complete

Scope: mandatory reliability

Dependencies: T21, T23, T33, T34

### Implementation

Run complete 45–60-minute synthetic or approved Session, inspect resource slope, file growth, all boundaries and recovery. Restrict concurrency based on actual memory.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

No accumulating decoders/unbounded memory; seekable final export, duration and recovery correct; report supports honest production estimates.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

M5 Pro time/storage.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `312f693`, `8a0c857`, `2f863b5`, `5874e46`; native 4K evidence in this step.
Implemented behavior: bounded incremental journal polling/SSE, interval-pruned balanced curve
expressions, full-duration crash/recovery benchmark, all-boundary comparisons and embedded export review.
Verification commands and results: the complete 45-minute native 1080p run passed: 81000 frames,
129600000 decoded samples, 92 chunks, two retained chunks unchanged and 184/184 boundary comparisons.
The separate 60-second native 4K export passed 1800 frames, 2880000 samples and all six reference
comparisons: 305.746 seconds, 5.887 fps, 11.29 GiB sampled RSS.
Final `make check` passed 286 tests with 59 opt-in media checks skipped and 64 schemas in sync;
the focused actual-media suite and both completed benchmarks provide this task's render evidence.
See [commands, timings and measurement limits](../36-longform.md).
Representative output/screenshot: `.local/t37-session-native1080/exports/session.mp4` (ignored);
[browser seeking](../evidence/t37-longform-seek.jpg) and representative decoded frames in the guide.
Machine and tool versions: Apple M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2.
Remaining limits: no real-art quality approval, parallel-export performance or full-length native
4K Session is claimed. Raw samples/video stay local; reports and small images are committed.


<a id="t38"></a>

## T38 Document operations and complete V1 acceptance

Status: implementation complete; final creative/product acceptance pending

Scope: mandatory

Dependencies: T19, T24, T33, T34, T37

### Implementation

Write setup/normal production/troubleshooting/recovery/backup/licence documentation. Run all mandatory gates, capture acceptance report and list optional/deferred work.

Apply the shared specifications for [assets](../01-assets.md), [architecture](../02-architecture.md), [contracts](../03-contracts.md), [rendering](../04-rendering.md), [web app](../05-webapp.md), [publishing](../06-publishing.md), and [verification](../07-qa.md) where relevant. Do not duplicate domain behavior in the UI or API.

### Acceptance

All V1 capabilities have evidence; creative and target-Mac pending items remain explicit; Marco can produce another episode from docs.

Run meaningful unit or media/UI checks for the behavior added, and keep actual output evidence. A button, mocked output or passing schema alone is not proof that media production works.

### Required human or machine inputs

Marco final product acceptance.

If unavailable, finish useful independent implementation with clearly marked fixtures. Record the exact blocked acceptance item; do not claim production approval.

### Completion record

Commit/change reference: `a8baa3f` explicit metadata review, `d0db033` CLI/operations,
and `T38: document final acceptance and remaining creative gates`.

Implemented behavior: complete [operations manual](../37-operations.md) covering installed setup,
normal production, guarded CLI parity, failures, recovery, private backups and manual release;
explicit hash-bound template/pack review; all missing authoring/audio/preferences CLI adapters;
actual supplied-reference draft walkthrough; [final acceptance register](../38-v1-acceptance.md).
The index now distinguishes completed supporting software from unprovided real animation/art.

Verification commands and results: `make check` passes 296 unit checks, Ruff and 64 schemas;
`make web-check` passes type/format/contracts and four frontend tests. The complete
`TABI_CONFIG=examples/settings.macos.toml make test-media` passes **61 actual-media tests in
231.18 seconds**. `make package` builds wheel/sdist/locked requirements. A fresh installed
environment outside the checkout has no Node on PATH; bundled integrity/setup and export
verification pass. Installed Chrome plays/seeks the 1080p draft, renders its own 300-frame proxy
and displays exact frame 150. Source art is unchanged and remains draft/rights pending.

Representative output/screenshot: [installed preview](../evidence/t38-installed-preview.jpg),
[browser observations](../evidence/t38-installed-browser.json),
[workflow](../evidence/t38-reference-walkthrough.json),
[installation](../evidence/t38-installed-runtime.json),
[repository/package audit](../evidence/t38-repository-package-audit.json).
Local outputs: `.local/Train reference draft/exports/`; all MP4s remain ignored.

Machine and tool versions: M5 Pro / 48 GiB, macOS 27.0.1 arm64, Python 3.11.16,
FFmpeg/ffprobe 9.0.2, uv 0.11.0, Chrome 154; Node 25.8.2/npm 11.14.1 for building only.

Remaining limits: Marco's final product acceptance and the explicitly listed real reference,
separated art, timing, original music, listening, creative/rights/disclosure approvals. Optional
ComfyUI has protocol/offline tests but no downloaded model or real workflow qualification. Full
native-4K long-form work and other hardware/OS combinations need separate measurements. No
publication, licence or creative approval is inferred from these engineering gates.
