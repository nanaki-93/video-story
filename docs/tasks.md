# Implementation tasks — reference assets and reusable lo-fi videos

Final scope agreed 8 October 2026. Read [PLAN](../PLAN.md), [agent rules](../AGENTS.md),
[reference generation spec](39-reference-assets.md), [progress](progress.md) and
[acceptance](38-v1-acceptance.md). Tasks appear in execution order; retained L07–L13 identifiers
are stable even though generation tasks L14–L17 now precede them in dependency order.

Implement one coherent task, verify it, record evidence and commit with its ID. Select the first
unblocked task. A model installation or real-art blocker does not stop independent synthetic
engineering. Never mark a generator complete using only mocks. Do not redownload models, call
paid providers, modify source art or silently expand the scope to resolve a failed creative gate.

## Shared implementation and verification rules

- Python owns contracts, generation, preparation and composition; API/CLI call the same services.
  Reuse the existing renderer, `SceneTemplate`, `ActionPack`, `AssetRef`, compiler and job/process
  primitives. Keep the currently working `LofiScene` route readable and functional.
- Use strict versioned documents, integer frames/samples, rational fps, normalized registered
  paths and content hashes. Atomic writes, stale-save rejection, immutable approvals and frozen
  render inputs apply to every new path. No DB or general-purpose creative editor.
- Source files under `docs/assets/`, including ignored `tabi-assets/`, are read-only inputs.
  Put generated media in local project storage. Approved changes create new versions; source
  selection or a candidate's Keep action does not grant production approval.
- Every task updates its entry, `docs/tasks/INDEX.md` and `docs/progress.md` with changed behavior,
  meaningful command results, limitations and small evidence under `docs/evidence/`. Milestone
  tasks also update `docs/38-v1-acceptance.md`. Keep MP4s/model weights out of Git.
- Commands below assume `UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1` and
  `TABI_CONFIG=examples/settings.macos.toml` are set. Use `.tools/bin/uv run --frozen` for Python
  commands. Add `--run-media` only for actual-media integration cases. Network/model installation
  is an explicit separate operation, never an incidental effect of an offline test.
- Whenever contracts change, run `make schemas`, `npm --prefix web run schemas`, focused tests
  and `make web-check`. Each coherent implementation must also pass Ruff and formatting. Run
  `make check web-check web-build package test-media` at a milestone after focused checks pass.

## R01 — Finalize the agreed plan and remove obsolete experiments

**Status:** complete. [Evidence](evidence/r01-repository-cleanup.json): 3,110 obsolete files /
2,187,528,245 bytes removed; all 486 protected hashes and the IDE index preserved. 289 core,
62 actual-media and six frontend checks, 63 schemas, formatting, web build and wheel/sdist pass.
Future generation remains planned; no model was downloaded.

**Dependencies:** inspected implementation, L05 pilot, existing source inventory and user cleanup
request. Protect unrelated staged IDE files and all supplied sources before deletion.

**Targets:** `PLAN.md`; this file; `docs/tasks/INDEX.md`; `docs/39-reference-assets.md`;
`README.md`; `docs/README.md`; `docs/assets/README.md`; `docs/08-sources.md`;
`docs/09-implementation-review.md`; `docs/12-tabi-art-review.md`; `docs/05-webapp.md`;
`docs/01-assets.md`; `docs/02-architecture.md`; `docs/03-contracts.md`; `docs/07-qa.md`;
`docs/37-operations.md`;
`docs/11-asset-registry.md`; `docs/13-timeline.md`; `docs/14-renderer.md`;
`docs/32-installation.md`; `docs/progress.md`; `docs/38-v1-acceptance.md`; `.gitignore`;
`docs/local-source-manifest.json` (rename preserved source inventory);
`docs/evidence/r01-repository-cleanup.json`; `src/tabi/api/contracts.py`;
`src/tabi/api/lofi.py`; `web/src/lofi.ts`; generated `schemas/web_lofi.schema.json`,
`web/src/generated/web_lofi.ts` and `web/src/generated/validators.cjs`.

**Removals:** retired `docs/archive/`, browser prototype/generation-bridge specifications,
Flow/3D/camera/calm-rig trial evidence; `scripts/verify_character_pipeline.py` and its dedicated
unit test; rejected local P01/Flow/independent-shot trials and superseded pilot preparations.
The exact scopes/hashes are in the cleanup evidence and its local manifest. Preserve
`docs/assets/`, L05 `generated/`, `prepared-v3/`, `deliverables/`, request and launcher, the
current synthetic lo-fi regression project, useful engineering evidence and shared runtime.

**Rules / verification:** remove only inspected obsolete scopes. Remove the obsolete Flow
presence banner and response field; retain read-only legacy settings/release compatibility and
the no-execution retirement regression. Regenerate contracts; check all retained Markdown links,
source/pilot hashes and IDE index. Run the full milestone command; record actual results. This
cleanup does not approve a model, correct the book or implement the future Generate button.

## L07 — Define reusable cabin, look, journey and recipe contracts

**Status:** planned; first unblocked engineering task after R01.

**Dependencies:** implemented L02 scene service and L05 pilot; `docs/34-activity-packs.md`.

**Targets:** new `src/tabi/core/models/lofi_packs.py`; `src/tabi/core/models/__init__.py`;
`src/tabi/core/persistence.py`; new `tests/unit/test_lofi_packs.py`;
new generated `schemas/lofi_cabin_pack.schema.json`, `schemas/lofi_look_pack.schema.json`,
`schemas/lofi_journey_pack.schema.json`, `schemas/lofi_recipe.schema.json` and corresponding
`web/src/generated/lofi_cabin_pack.ts`, `lofi_look_pack.ts`, `lofi_journey_pack.ts`,
`lofi_recipe.ts`, plus `documents.ts` and `validators.cjs` in that generated directory.

**Rules:** add `LofiCabinPack`, `LofiLookPack`, `LofiJourneyPack`, `LofiRecipe` as versioned,
hash-reviewed documents. Every pack binds one exact existing `SceneTemplate` layout family,
thumbnail, lighting/style and explicit role assignments. Cabin assigns background/mask/foreground;
journey assigns scenery slots; look references an existing `ActionPack`, outfit and supported
idle/blink/accent actions. Reject duplicate roles, incompatible template versions and invalid
intervals. Recipes select exact versions, motion, seed, travel and duration semantics; distinguish
continuous exports from whole-output loops. Preserve old `LofiScene` documents unchanged.

**Verify:** `.tools/bin/uv run --frozen pytest -q tests/unit/test_lofi_packs.py tests/unit/test_lofi.py tests/unit/test_persistence.py tests/unit/test_contracts.py`.
Cover round trips, invalid mixes, legacy hashes, stale writes and approval immutability; run
shared schema/frontend checks.

## L14 — Define reference generation and provenance contracts

**Status:** planned. **Dependencies:** L07; generation spec sections on requests and execution.

**Targets:** new `src/tabi/core/models/asset_generation.py`;
`src/tabi/core/models/__init__.py`; `src/tabi/core/persistence.py`;
new `tests/unit/test_asset_generation_contracts.py`;
new generated `schemas/asset_generation_request.schema.json`,
`schemas/asset_generation_job.schema.json`, `schemas/asset_model_manifest.schema.json`,
`schemas/asset_reference_catalog.schema.json`; matching files in `web/src/generated/`
(`asset_generation_request.ts`, `asset_generation_job.ts`, `asset_model_manifest.ts`,
`asset_reference_catalog.ts`), `documents.ts` and `validators.cjs`.

**Rules:** strict typed reference roles, source/crop/mask hashes, output kind, dimensions, seed,
prompt, model manifest and allowlisted settings. Include exact versions/terms review state,
normalized input and output identities, lifecycle/failure details and measured effort. Require
identity for character generation and a target for a correction. Validate reference limits
against model capabilities; reject unknown options and unqualified model manifests. No arbitrary
commands/URLs. Keep generation job records distinct from render-job schema; reuse ownership
primitives. Keeping a result creates a draft; no self-asserted approval or invented provenance.

**Verify:** `.tools/bin/uv run --frozen pytest -q tests/unit/test_asset_generation_contracts.py tests/unit/test_persistence.py tests/unit/test_contracts.py`.
Cover incomplete provenance, invalid masks/roles, duplicate references, unknown settings,
unsupported versions, hash changes and job state transitions; shared schema/frontend checks.

## L15 — Catalog the existing references without moving originals

**Status:** planned. **Dependencies:** L14.

**Targets:** new `src/tabi/core/asset_references.py`; `src/tabi/core/assets/service.py`;
new `tests/unit/test_asset_references.py`; `scripts/audit_assets.py` only if a shared read-only
probe is extracted; `docs/assets/README.md`; `docs/evidence/l15-reference-catalog.json`.

**Rules:** discover supported files in registered roots including Git-ignored sources, deduplicate
nested roots, group numbered PNG sequences and expose outfit/emotion/pose/scenery categories.
Offer explicit role assignment and optional crop; do not infer approval or sequence fps. Use
existing path security, source hashing and thumbnail caching. Detect missing/changed sources,
reject symlink escapes and invalidate stale references. Never rewrite or reorganize the supplied
folders. The historical JSON inventory seeds review, not a fixed list that hides new assets.

**Verify:** `.tools/bin/uv run --frozen pytest -q tests/unit/test_asset_references.py tests/unit/test_assets.py`.
Use small synthetic Unicode/space paths, ignored files, nested roots, a sequence, a changed hash
and a traversal case. Perform a read-only scan of both actual source folders, recording counts,
representative paths and before/after hashes without treating their art as approved.

## L16 — Qualify the free local reference model on this Mac

**Status:** planned; actual execution requires explicit model installation and completed terms review.
**Dependencies:** L15. L08 can proceed with local/synthetic assets while this gate is pending.

**Targets:** `docs/08-sources.md`; new `docs/model-qualification.md`;
new `scripts/qualify_asset_generator.py` (bounded repeatable harness);
new `tests/unit/test_asset_generator_qualification.py` (manifest/budget checks);
`docs/evidence/l16-reference-generator.json`; local `.local/asset-generator-qualification/`.
Do not change core requirements/lockfiles until the selected backend and compatible environment
are justified by this evidence.

**Rules:** first evaluate FLUX.2 klein **4B** via MFLUX/MLX, not the non-commercial 9B variant.
Pin exact revisions/checksums of adapter, model and all weight/runtime dependencies and record
official terms, notices, review date and restrictions before use. Disclose storage/download size;
installation is explicit, isolated and optional. No paid fallback or cloud upload. Do not reuse
old 3D/Flow machinery. If dependencies cannot be cleared or the model cannot run, stop that gate
with diagnostics; imported assets remain usable.

Use actual identity + pose + clothing references for an outfit change, layout + style for an
interior change, and the supplied Tokyo imagery for a panorama variation. Maximum two attempts
per category (six images total), no automatic quality retries. Preserve source hashes and record
commands, refs, prompt/settings, image comparisons, memory, latency and operator time. Human
review covers Tabi's eyes/gills/headphones/anatomy, adherence, perspective and editing effort.
No speed, quality or throughput claim until measured. Do not call fixtures a provider result.

**Verify:** `.tools/bin/uv run --frozen pytest -q tests/unit/test_asset_generator_qualification.py`;
record the exact qualified environment and live harness commands/results in the evidence. A
passing terms/runtime check is separate from Marco's creative/effort decision. Failed required
categories stay unresolved; backend integration cannot claim a production-ready generator.

## L17 — Run real reference generation as an owned local job

**Status:** planned. **Dependencies:** L14–L16 qualified backend/runtime.

**Targets:** new `src/tabi/core/asset_generation.py`,
`src/tabi/core/asset_backends/__init__.py`, `src/tabi/core/asset_backends/mflux.py`;
`src/tabi/core/process.py` only for reusable owned-process needs;
`src/tabi/core/config.py`; `src/tabi/core/models/asset_generation.py`;
new `tests/unit/test_asset_generation.py`, `tests/integration/test_asset_generation.py`;
`pyproject.toml`, `uv.lock` only for justified optional compatible dependencies, otherwise a
pinned optional backend environment specification at `backends/mflux/requirements.txt`;
`THIRD-PARTY.md`; `docs/32-installation.md`; `docs/evidence/l17-reference-generator.json`.

**Rules:** one frozen request produces one candidate by default. Submit actual image references
to the qualified adapter; retain factual normalization and model evidence. Enforce one heavy job
at a time, bounded resources and useful progress/cancellation. Use subprocess argument arrays,
owned PIDs and registered output roots. Persist/recover interrupted jobs; never kill unrelated
processes or mark partial output complete. Decode/hash/verify before atomic registration.
Protected-region correction composites only inside the reviewed mask; full-image variants require
full review. No model download inside a render or automatic start on app launch. Rendering and
import work when the optional generator is absent. Do not promise byte-identical GPU images.

**Verify:** `.tools/bin/uv run --frozen pytest --run-media tests/unit/test_asset_generation.py tests/integration/test_asset_generation.py`.
Exercise cancellation, interrupted writes, stale inputs, malicious paths, concurrency and output
validation with bounded fixtures. Separately record at least one real qualified multi-reference
run, a kept version and source preservation. Offline/mocked tests alone cannot complete L17.

## L08 — Prepare aligned reusable assets and gentle motion states

**Status:** planned. **Dependencies:** L07, L14, L15; real generated inputs also require L17.

**Targets:** new `src/tabi/core/lofi_preparation.py`; `src/tabi/core/models/lofi_packs.py`;
`src/tabi/core/fixture_lofi.py`; new `tests/unit/test_lofi_preparation.py`,
`tests/integration/test_lofi_preparation.py`; `tests/unit/test_lofi_packs.py`;
`docs/evidence/l08-lofi-preparation.json`.

**Rules:** accept generated or imported candidates through the same bounded preparation service.
Prepare clean cabin background, foreground occlusion, character alpha, window matte and compatible
scenery. Provide deterministic crop/alignment/mask transforms and small authored motion cycles
with recorded settings. Do not pretend segmentation or hidden-region inpainting exists until
implemented and visually checked. AI generates selected stills/key states, not every frame.
A failed matte needs a clear correction path, not automatic approval.

Keep one exact template per family; cabin/character anchors, canvas/fps, prop zones and lighting
must match. Use outfit-specific breathing/gill frames, fixed head and aligned open/half/closed eye
states; every cycle returns to its authored rest. Face ownership prevents duplicate blinking.
Supplied sequences require explicit source timing and loop/anchor review. Normalize panoramas,
prepare/review district joins and exact repeated padding. Record every transform and hash;
source originals and previous versions remain unchanged. No claim of a universal auto-rig.

**Verify:** `.tools/bin/uv run --frozen pytest --run-media tests/unit/test_lofi_preparation.py tests/unit/test_lofi_packs.py tests/integration/test_lofi_preparation.py`.
Check masks/alpha on contrasting backgrounds, complete clean-plate coverage, source preservation,
loop seams, padding, unknown fps and rejection of mismatched anchors. Use synthetic images first;
real-art quality remains L13's separate gate.

## L09 — Compose the selected packs through the existing renderer

**Status:** planned. **Dependencies:** L08.

**Targets:** new `src/tabi/core/lofi_composition.py`; `src/tabi/core/lofi_preparation.py`;
`src/tabi/core/fixture_lofi.py`; new `tests/unit/test_lofi_composition.py`,
`tests/integration/test_lofi_composition.py`; `docs/evidence/l09-lofi-composition.json`.

**Rules:** resolve exact pack versions and validate template, lighting/style, canvas, fps, poses
and props in Python. Bind assets through normal scene slot assignments; use the look's matching
`ActionPack`. Do not synthesize another template/action binding per combination. Fill all body
frames with compatible idle/rest behavior. Freeze content in existing episode/snapshot jobs;
later recipe edits leave existing outputs unchanged. Preserve optional music and exact duration;
silent output has no audio streams. No second rendering/FFmpeg path.

**Verify:** `.tools/bin/uv run --frozen pytest --run-media tests/unit/test_lofi_composition.py tests/unit/test_activity_packs.py tests/unit/test_lofi.py tests/integration/test_lofi_composition.py tests/integration/test_lofi_render.py`.
Exercise eight synthetic 2×2×2 combinations; verify independent selection regions, no duplicate
body, background coverage, foreground occlusion, mismatched outfit rejection and unchanged pilot.

## L10 — Schedule breathing, blinking and gill motion without phase jumps

**Status:** planned. **Dependencies:** L09.

**Targets:** new `src/tabi/core/lofi_motion.py`; `src/tabi/core/lofi_composition.py`;
`src/tabi/core/fixture_lofi.py`; new `tests/unit/test_lofi_motion.py`;
`tests/integration/test_lofi_composition.py`; `docs/evidence/l10-lofi-motion.json`.

**Rules:** use existing `ActionRequest`, pose/prop/channel rules and versioned seeded randomness.
Cover every body frame, schedule sparse compatible face windows, and use authored entry/exit
states. Reject impossible intervals/conflicts; no silent dropping, gesture stretching or gap
patching with arbitrary frames. Keep head still initially. Global timing survives nonzero
previews/chunking. Whole-output loop requests validate all phases including scenery; otherwise
label an ordinary continuous export. Show which motion needs better assets rather than jittering
or misaligning the eyes to force it to fit.

**Verify:** `.tools/bin/uv run --frozen pytest --run-media tests/unit/test_lofi_motion.py tests/unit/test_compiler.py tests/integration/test_lofi_composition.py`.
Check reproducible schedules, body/face occupancy, irregular-duration rest coverage, nonzero seek,
chunk boundary and compatible/incompatible whole-output joins with independent pixel checks.

## L11 — Expose references, generation, preparation and recipes to API/CLI

**Status:** planned. **Dependencies:** L10, L17.

**Targets:** new `src/tabi/api/asset_generation.py`, `src/tabi/cli/asset_generation.py`;
`src/tabi/api/app.py`; `src/tabi/api/runtime.py`; `src/tabi/cli/main.py`;
`src/tabi/api/lofi.py`; `src/tabi/cli/lofi.py`; `src/tabi/api/contracts.py`;
new `tests/unit/test_asset_generation_api.py`, `tests/unit/test_lofi_pack_api.py`;
new generated `schemas/web_lofi_packs.schema.json`, `schemas/web_asset_generation.schema.json`,
`web/src/generated/web_lofi_packs.ts`, `web/src/generated/web_asset_generation.ts`,
`web/src/generated/documents.ts`, `web/src/generated/validators.cjs`;
`docs/evidence/l11-reference-api.json`.

**Rules:** thin adapters expose catalog, model readiness, generation job status/cancel, immutable
candidate comparison/keep, preparation validation and pack/recipe creation. Apply existing
loopback token, registered roots, Host/Origin/CSRF, authenticated media/SSE, upload limits and
owned cancellation. Avoid exposing sensitive prompts/paths outside the session. CLI and browser
must get the same compatibility errors and frozen identities. Missing model returns a useful
readiness response while existing import/preview/export works. No placeholder success jobs.

**Verify:** `.tools/bin/uv run --frozen pytest -q tests/unit/test_asset_generation_api.py tests/unit/test_lofi_pack_api.py tests/unit/test_web_service.py tests/unit/test_web_workspace.py`.
Check security, API/CLI parity, concurrent stale saves, job ownership and exact output versions;
shared schema/frontend checks. Real generator evidence from L17 is required for live endpoints.

## L12 — Build the complete reference-to-video interface

**Status:** planned. **Dependencies:** L11.

**Targets:** new `web/src/asset-generation.ts`, `web/src/asset-generation-state.ts`,
`web/tests/asset-generation-state.test.mjs`; `web/src/assets.ts`; `web/src/lofi.ts`;
`web/src/lofi-state.ts`; `web/src/session.ts`; `web/src/main.ts`; `web/src/style.css`;
`web/tests/lofi-state.test.mjs`; `docs/05-webapp.md`; `docs/37-operations.md`;
`docs/evidence/l12-reference-ui.json`.

**Rules:** browse existing references with thumbnails/categories and assign their roles. Choose
output kind and requested change, see model readiness and selected inputs, generate a candidate,
compare sources/result and keep a new version. Implement actual mask/alignment/preparation
controls through L08; explain technical failures in user language. Show cancel/failure/recovery
and permit a deliberate retry without endless automatic generation. A prompt-only screen is
not completion. Import remains available.

Select compatible Look/Cabin/Journey packs and motion settings, create a normal episode, preview
and export. Use guarded dirty/stale state and immutable selection versions. Keep existing fixed
scenes usable. Browser owns controls only, no frame scheduling or FFmpeg. No hidden placeholder
buttons. Installation must show size and require a deliberate user action before model download.

**Verify:** `make web-check web-build` plus normal-browser real generator → compare → keep → prepare
→ select → preview → export; inspect playback, cancellation/failure, stale input, unavailable
backend and reuse. Record actual screenshots and jobs; tests of UI state alone are insufficient.

## L06 — Correct the book orientation in the preserved Tokyo pilot

**Status:** pending real edit; previously requested built-in editor was unavailable.
**Dependencies:** an available authorized editor or qualified L17; independent of schema work.

**Targets:** `scripts/prepare_tokyo_lofi.py` only if conforming needs adjustment;
new `docs/evidence/l06-book-correction.json`; local `.local/tokyo-lofi-book-v2/`.

**Rules:** turn the page/book toward Tabi with correct table perspective, preserving the
character, hands, cup, pen and light. Create new master/scene versions and retain the L05 original.
Use a reviewed edit mask and existing scenery/blink timing; no whole-scene video regeneration.
The tool's availability must be rechecked when executing, not assumed from past failure.

**Verify:** source/output comparisons, protected-region pixels, book perspective and hands,
full 90-second silent decode/timestamps/loop review. Record exact hashes and review outcome.
Image availability can block this art task without blocking synthetic implementation.

## L13 — Prove the full workflow with Tabi and a silent Tokyo video

**Status:** planned. **Dependencies:** L06, L12 and prepared real packs.

**Targets:** `docs/evidence/l13-lofi-variants.json`; `docs/37-operations.md`;
`docs/38-v1-acceptance.md`; `docs/progress.md`; local `.local/lofi-variants-v1/`.

**Rules:** use actual supplied references to prepare two outfits, two compatible cabin designs
and two distinct Tokyo journeys. One option can reuse the original style. Capture real generator
inputs/results and reviewed layers/motions, including breathing, blink and gill motion. Compare
Tabi's likeness against the supplied art; do not approve using labels or tests. Preserve the
original pilot and source folders. No music, publishing or purchases in this acceptance.

Review all eight combinations in short previews, then one full 90-second silent export and a
10-minute phase/loop check. Inspect eyes, body stability, hidden regions, foreground occlusion,
district changes, every motion cycle, chunk joins and whole-output seam when requested. Verify
full decode, frame count, absence of audio and unchanged source hashes. Record actual generation
attempts, time, manual adjustments, storage and memory separately from rendering time.

Demonstrate another video by selecting saved packs with no new generation for unchanged assets,
manual clip matching or JSON editing. Two variants prove reuse, not an indefinitely unique
release library. Add/review further outfits/interiors/journeys for future distinct videos.

**Verify:** `make check web-check web-build package test-media` and the normal-browser walkthrough.
Record exact versions/hashes, command results, screenshots/contact sheets and local clip paths.
Marco's visual decision, source/music rights, final Mac/Safari/native-4K/long-form gates and
manual release checks remain explicit; technical tests cannot grant them.
