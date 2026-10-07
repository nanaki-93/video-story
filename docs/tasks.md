# Reusable Tabi train videos with outfits, cabins and journeys

Extend the working asset-based lo-fi workflow so each video can select a compatible Tabi
outfit, train interior and varied Tokyo journey, with two or three restrained character
motions. This is the implementation plan requested on 8 October 2026; L07–L13 are planned,
and their behavior has not been implemented or visually accepted.

The L05 pilot already renders through video-story. Its master paints Tabi, clothing, cabin
and table together, so independent changes require preparing separate artwork first. Marco
likes the test; that feedback does not resolve L06's book correction or approve new assets.

The intended everyday workflow is **New video → outfit → cabin → Tokyo journey → motion
set → short preview → export**. New artwork is prepared once per pack and reused. The local
app assembles and renders imported assets; an image editor available in Codex is not an API
that the standalone app can silently call. No new subscription, paid generator or top-up is
part of this plan.

Use one fixed camera/layout family first. Reuse the existing `SceneTemplate` type for its
immutable contract: camera, canvas, character anchor, ordered layer slots, window masks and
scenery periods. Cabin finishes, upholstery and wall details may change within that layout.
A different viewpoint, window opening, seating geometry or character pose needs a new family
and matching assets. Lighting must also match; swapping a daytime exterior does not relight
a sunset character automatically.

Marco selected gentle loops: blinking, breathing and a small gill/head movement. Start with
gill movement while keeping the face aligned. These are two or three motion types recurring
quietly, not a claim that arbitrary gestures can be generated from one still. A new outfit
needs matching body frames; face frames are reused only when alignment and lighting pass
review. Sipping and page-turning remain a later extension requiring authored hand/prop
ownership and entry/exit poses.

Preserve all artwork, music, original footage, exports and saved projects. Keep L01–L06 below
as implementation history and the outstanding correction. The retired Flow history remains
in `docs/archive/flow-tasks.md`. L07 is the next independent engineering task; L06 does not
block synthetic schema, composition or UI work. At implementation time, update
`docs/tasks/INDEX.md`, this file and `docs/progress.md` with each completed task's evidence,
and commit that verified step using its ID. This planning pass changes only `docs/tasks.md`.

## L01 — Retire the Flow execution path

**Status** [x] 286 core checks, 61 schemas, four frontend checks and production web build pass. Initial sandbox socket failures passed with authorized loopback execution. All 669 protected files retain their hashes.

**Target files**
- `src/tabi/core/flow/shots.py`
- `src/tabi/core/flow/service.py`
- `src/tabi/core/flow/runner.py`
- `src/tabi/core/flow/media.py`
- `src/tabi/core/flow/__init__.py`
- `src/tabi/core/flow/review.py`
- `src/tabi/core/flow/prompts.py`
- `src/tabi/core/flow/assembly.py`
- `src/tabi/api/flow.py`
- `src/tabi/cli/flow.py`
- `src/tabi/core/models/flow.py`
- `src/tabi/core/models/generation.py`
- `tests/unit/test_flow_shot_contracts.py`
- `tests/unit/test_flow_release_contracts.py`
- `tests/unit/test_flow_runner.py`
- `tests/unit/test_flow_review.py`
- `tests/unit/test_flow_contracts.py`
- `tests/unit/test_flow_prompts.py`
- `tests/unit/test_flow_shot_api.py`
- `tests/unit/test_flow_shot_runner.py`
- `tests/unit/test_flow_service.py`
- `tests/unit/test_flow_cli.py`
- `tests/unit/test_web_flow_contracts.py`
- `tests/integration/test_web_flow.py`
- `tests/integration/test_flow_import.py`
- `tests/integration/test_flow_audio.py`
- `tests/integration/test_flow_workflow.py`
- `tests/integration/test_flow_review_media.py`
- `tests/integration/test_flow_shot_workflow.py`
- `tests/integration/test_flow_assembly.py`
- `tests/integration/test_flow_release.py`
- `web/src/flow.ts`
- `web/src/flow-state.ts`
- `web/tests/flow-state.test.mjs`
- `tests/fixtures/flow-u04-recipe.json`
- `src/tabi/core/models/settings.py`
- `src/tabi/api/runtime.py`
- `src/tabi/api/app.py`
- `src/tabi/api/contracts.py`
- `src/tabi/api/release.py`
- `src/tabi/cli/main.py`
- `src/tabi/core/models/__init__.py`
- `src/tabi/core/models/publishing.py`
- `src/tabi/core/persistence.py`
- `src/tabi/core/publishing.py`
- `web/src/main.ts`
- `web/src/workspace.ts`
- `web/src/wireframes.ts`
- `web/src/release.ts`
- `web/scripts/contracts.mjs`
- `tests/unit/test_contracts.py`
- `tests/unit/test_lofi_retirement.py`
- `docs/archive/flow-tasks.md`
- `docs/archive/flow-task-index.md`
- `schemas/cache_entry.schema.json`
- `schemas/random_action_timing.schema.json`
- `schemas/generation_run.schema.json`
- `schemas/app_preferences.schema.json`
- `schemas/render_spike_report.schema.json`
- `schemas/fixture_manifest.schema.json`
- `schemas/flow_attempt.schema.json`
- `schemas/web_upload.schema.json`
- `schemas/release_preparation.schema.json`
- `schemas/generation_status.schema.json`
- `schemas/cache_prune_report.schema.json`
- `schemas/export_verification.schema.json`
- `schemas/compiled_snapshot.schema.json`
- `schemas/web_flow.schema.json`
- `schemas/public_release.schema.json`
- `schemas/comfy_workflow.schema.json`
- `schemas/web_project.schema.json`
- `schemas/portable_roots.schema.json`
- `schemas/render_report.schema.json`
- `schemas/job_progress.schema.json`
- `schemas/web_projects.schema.json`
- `schemas/capability_report.schema.json`
- `schemas/render_job.schema.json`
- `schemas/cache_inventory.schema.json`
- `schemas/web_render_plan.schema.json`
- `schemas/web_catalog.schema.json`
- `schemas/web_settings.schema.json`
- `schemas/asset.schema.json`
- `schemas/scene_template.schema.json`
- `schemas/flow_export.schema.json`
- `schemas/preview_selection.schema.json`
- `schemas/release_bundle_report.schema.json`
- `schemas/storyboard_report.schema.json`
- `schemas/web_roots.schema.json`
- `schemas/track_placement.schema.json`
- `schemas/web_frame.schema.json`
- `schemas/audio_mix_report.schema.json`
- `schemas/action_pack.schema.json`
- `schemas/backup_manifest.schema.json`
- `schemas/waveform_report.schema.json`
- `schemas/web_recents.schema.json`
- `schemas/import_request.schema.json`
- `schemas/release_record.schema.json`
- `schemas/web_audio_mix.schema.json`
- `schemas/project.schema.json`
- `schemas/web_preview.schema.json`
- `schemas/asset_health.schema.json`
- `schemas/web_cache.schema.json`
- `schemas/web_jobs.schema.json`
- `schemas/web_releases.schema.json`
- `schemas/compilation_result.schema.json`
- `schemas/job_event.schema.json`
- `schemas/validation_report.schema.json`
- `schemas/flow_episode.schema.json`
- `schemas/web_directory.schema.json`
- `schemas/audio_edit_plan.schema.json`
- `schemas/curve.schema.json`
- `schemas/audio_timeline_report.schema.json`
- `schemas/episode.schema.json`
- `schemas/web_backup.schema.json`
- `schemas/release_inspection.schema.json`
- `schemas/action.schema.json`
- `schemas/web_session.schema.json`
- `schemas/web_editor.schema.json`
- `schemas/web_audio.schema.json`
- `schemas/action_request.schema.json`
- `schemas/storage_estimate.schema.json`
- `schemas/scene_instance.schema.json`
- `web/src/generated/comfy_workflow.ts`
- `web/src/generated/storage_estimate.ts`
- `web/src/generated/release_record.ts`
- `web/src/generated/project.ts`
- `web/src/generated/web_project.ts`
- `web/src/generated/web_releases.ts`
- `web/src/generated/compiled_snapshot.ts`
- `web/src/generated/action_request.ts`
- `web/src/generated/web_frame.ts`
- `web/src/generated/render_spike_report.ts`
- `web/src/generated/compilation_result.ts`
- `web/src/generated/scene_instance.ts`
- `web/src/generated/audio_edit_plan.ts`
- `web/src/generated/web_settings.ts`
- `web/src/generated/render_report.ts`
- `web/src/generated/job_event.ts`
- `web/src/generated/validators.cjs`
- `web/src/generated/web_jobs.ts`
- `web/src/generated/generation_status.ts`
- `web/src/generated/app_preferences.ts`
- `web/src/generated/cache_entry.ts`
- `web/src/generated/preview_selection.ts`
- `web/src/generated/web_projects.ts`
- `web/src/generated/audio_timeline_report.ts`
- `web/src/generated/web_editor.ts`
- `web/src/generated/generation_run.ts`
- `web/src/generated/web_roots.ts`
- `web/src/generated/release_inspection.ts`
- `web/src/generated/import_request.ts`
- `web/src/generated/cache_inventory.ts`
- `web/src/generated/release_preparation.ts`
- `web/src/generated/asset_health.ts`
- `web/src/generated/random_action_timing.ts`
- `web/src/generated/web_audio.ts`
- `web/src/generated/curve.ts`
- `web/src/generated/action.ts`
- `web/src/generated/track_placement.ts`
- `web/src/generated/web_backup.ts`
- `web/src/generated/job_progress.ts`
- `web/src/generated/backup_manifest.ts`
- `web/src/generated/scene_template.ts`
- `web/src/generated/validators.d.cts`
- `web/src/generated/web_session.ts`
- `web/src/generated/web_flow.ts`
- `web/src/generated/capability_report.ts`
- `web/src/generated/web_upload.ts`
- `web/src/generated/documents.ts`
- `web/src/generated/validation_report.ts`
- `web/src/generated/export_verification.ts`
- `web/src/generated/web_audio_mix.ts`
- `web/src/generated/episode.ts`
- `web/src/generated/asset.ts`
- `web/src/generated/audio_mix_report.ts`
- `web/src/generated/web_render_plan.ts`
- `web/src/generated/fixture_manifest.ts`
- `web/src/generated/web_cache.ts`
- `web/src/generated/flow_attempt.ts`
- `web/src/generated/action_pack.ts`
- `web/src/generated/public_release.ts`
- `web/src/generated/web_directory.ts`
- `web/src/generated/release_bundle_report.ts`
- `web/src/generated/web_recents.ts`
- `web/src/generated/waveform_report.ts`
- `web/src/generated/flow_episode.ts`
- `web/src/generated/portable_roots.ts`
- `web/src/generated/web_preview.ts`
- `web/src/generated/render_job.ts`
- `web/src/generated/web_catalog.ts`
- `web/src/generated/storyboard_report.ts`
- `web/src/generated/cache_prune_report.ts`
- `web/src/generated/flow_export.ts`
- `PLAN.md`
- `docs/tasks/INDEX.md`
- `docs/progress.md`
- `docs/38-v1-acceptance.md`
- `docs/tasks.md`

**Inputs / dependencies**
User request of 7 October; existing shared renderer and provenance/security contracts.

**Implementation rules**
Delete Flow prompting, credits, retries, native imports, queue, release adapter, obsolete generation contracts and their dedicated tests. Keep shared rendering, scene, audio, jobs, approvals and security. Saved Flow data/exports stay on disk; no automatic migration. Remove retired schema outputs. Keep provenance generation metadata for imported assets. Preserve unrelated staged IDE files.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml make check web-check web-build`

## L02 — Compile reusable lo-fi scenes through the shared renderer

**Status** [x] 298 core checks, 14 focused core/actual-media checks, 63 schemas and four frontend checks pass. See `docs/evidence/l02-lofi-render.json`.

**Target files**
- `src/tabi/core/authoring.py`
- `src/tabi/core/fixture_lofi.py`
- `tests/unit/test_contracts.py`
- `src/tabi/core/models/lofi.py`
- `src/tabi/core/models/scenes.py`
- `src/tabi/core/models/__init__.py`
- `src/tabi/core/lofi.py`
- `src/tabi/core/persistence.py`
- `src/tabi/core/timeline/effects.py`
- `src/tabi/core/render/ffmpeg.py`
- `src/tabi/api/lofi.py`
- `src/tabi/api/app.py`
- `src/tabi/api/contracts.py`
- `src/tabi/cli/lofi.py`
- `src/tabi/cli/main.py`
- `tests/unit/test_lofi.py`
- `tests/integration/test_lofi_render.py`
- `docs/evidence/l02-lofi-render.json`
- `schemas/cache_entry.schema.json`
- `schemas/random_action_timing.schema.json`
- `schemas/generation_run.schema.json`
- `schemas/app_preferences.schema.json`
- `schemas/render_spike_report.schema.json`
- `schemas/fixture_manifest.schema.json`
- `schemas/flow_attempt.schema.json`
- `schemas/web_upload.schema.json`
- `schemas/release_preparation.schema.json`
- `schemas/generation_status.schema.json`
- `schemas/cache_prune_report.schema.json`
- `schemas/export_verification.schema.json`
- `schemas/compiled_snapshot.schema.json`
- `schemas/web_flow.schema.json`
- `schemas/public_release.schema.json`
- `schemas/comfy_workflow.schema.json`
- `schemas/web_project.schema.json`
- `schemas/portable_roots.schema.json`
- `schemas/render_report.schema.json`
- `schemas/job_progress.schema.json`
- `schemas/web_projects.schema.json`
- `schemas/capability_report.schema.json`
- `schemas/render_job.schema.json`
- `schemas/cache_inventory.schema.json`
- `schemas/web_render_plan.schema.json`
- `schemas/web_catalog.schema.json`
- `schemas/web_settings.schema.json`
- `schemas/asset.schema.json`
- `schemas/scene_template.schema.json`
- `schemas/flow_export.schema.json`
- `schemas/preview_selection.schema.json`
- `schemas/release_bundle_report.schema.json`
- `schemas/storyboard_report.schema.json`
- `schemas/web_roots.schema.json`
- `schemas/track_placement.schema.json`
- `schemas/web_frame.schema.json`
- `schemas/audio_mix_report.schema.json`
- `schemas/action_pack.schema.json`
- `schemas/backup_manifest.schema.json`
- `schemas/waveform_report.schema.json`
- `schemas/web_recents.schema.json`
- `schemas/import_request.schema.json`
- `schemas/release_record.schema.json`
- `schemas/web_audio_mix.schema.json`
- `schemas/project.schema.json`
- `schemas/web_preview.schema.json`
- `schemas/asset_health.schema.json`
- `schemas/web_cache.schema.json`
- `schemas/web_jobs.schema.json`
- `schemas/web_releases.schema.json`
- `schemas/compilation_result.schema.json`
- `schemas/job_event.schema.json`
- `schemas/validation_report.schema.json`
- `schemas/flow_episode.schema.json`
- `schemas/web_directory.schema.json`
- `schemas/audio_edit_plan.schema.json`
- `schemas/curve.schema.json`
- `schemas/audio_timeline_report.schema.json`
- `schemas/episode.schema.json`
- `schemas/web_backup.schema.json`
- `schemas/release_inspection.schema.json`
- `schemas/action.schema.json`
- `schemas/web_session.schema.json`
- `schemas/web_editor.schema.json`
- `schemas/web_audio.schema.json`
- `schemas/action_request.schema.json`
- `schemas/storage_estimate.schema.json`
- `schemas/scene_instance.schema.json`
- `web/src/generated/comfy_workflow.ts`
- `web/src/generated/storage_estimate.ts`
- `web/src/generated/release_record.ts`
- `web/src/generated/project.ts`
- `web/src/generated/web_project.ts`
- `web/src/generated/web_releases.ts`
- `web/src/generated/compiled_snapshot.ts`
- `web/src/generated/action_request.ts`
- `web/src/generated/web_frame.ts`
- `web/src/generated/render_spike_report.ts`
- `web/src/generated/compilation_result.ts`
- `web/src/generated/scene_instance.ts`
- `web/src/generated/audio_edit_plan.ts`
- `web/src/generated/web_settings.ts`
- `web/src/generated/render_report.ts`
- `web/src/generated/job_event.ts`
- `web/src/generated/validators.cjs`
- `web/src/generated/web_jobs.ts`
- `web/src/generated/generation_status.ts`
- `web/src/generated/app_preferences.ts`
- `web/src/generated/cache_entry.ts`
- `web/src/generated/preview_selection.ts`
- `web/src/generated/web_projects.ts`
- `web/src/generated/audio_timeline_report.ts`
- `web/src/generated/web_editor.ts`
- `web/src/generated/generation_run.ts`
- `web/src/generated/web_roots.ts`
- `web/src/generated/release_inspection.ts`
- `web/src/generated/import_request.ts`
- `web/src/generated/cache_inventory.ts`
- `web/src/generated/release_preparation.ts`
- `web/src/generated/asset_health.ts`
- `web/src/generated/random_action_timing.ts`
- `web/src/generated/web_audio.ts`
- `web/src/generated/curve.ts`
- `web/src/generated/action.ts`
- `web/src/generated/track_placement.ts`
- `web/src/generated/web_backup.ts`
- `web/src/generated/job_progress.ts`
- `web/src/generated/backup_manifest.ts`
- `web/src/generated/scene_template.ts`
- `web/src/generated/validators.d.cts`
- `web/src/generated/web_session.ts`
- `web/src/generated/web_flow.ts`
- `web/src/generated/capability_report.ts`
- `web/src/generated/web_upload.ts`
- `web/src/generated/documents.ts`
- `web/src/generated/validation_report.ts`
- `web/src/generated/export_verification.ts`
- `web/src/generated/web_audio_mix.ts`
- `web/src/generated/episode.ts`
- `web/src/generated/asset.ts`
- `web/src/generated/audio_mix_report.ts`
- `web/src/generated/web_render_plan.ts`
- `web/src/generated/fixture_manifest.ts`
- `web/src/generated/web_cache.ts`
- `web/src/generated/flow_attempt.ts`
- `web/src/generated/action_pack.ts`
- `web/src/generated/public_release.ts`
- `web/src/generated/web_directory.ts`
- `web/src/generated/release_bundle_report.ts`
- `web/src/generated/web_recents.ts`
- `web/src/generated/waveform_report.ts`
- `web/src/generated/flow_episode.ts`
- `web/src/generated/portable_roots.ts`
- `web/src/generated/web_preview.ts`
- `web/src/generated/render_job.ts`
- `web/src/generated/web_catalog.ts`
- `web/src/generated/storyboard_report.ts`
- `web/src/generated/cache_prune_report.ts`
- `web/src/generated/flow_export.ts`
- `schemas/lofi_scene.schema.json`
- `schemas/web_lofi.schema.json`
- `web/src/generated/lofi_scene.ts`
- `web/src/generated/web_lofi.ts`
- `PLAN.md`
- `docs/tasks/INDEX.md`
- `docs/progress.md`
- `docs/38-v1-acceptance.md`
- `docs/tasks.md`

**Inputs / dependencies**
L01. Use existing media dependencies; no new generator, app or model.

**Implementation rules**
Add strict versioned reusable scene recipes: master illustration, optional white-visible window mask and prepared scrolling layers, optional transparent loop overlays with independent global timing. Validate dimensions, alpha, fps, strip padding and source bounds. Python alone constructs scene templates and episodes. Keep drafts atomic, approved records immutable, jobs and music on existing services. Provide API/CLI save, list and create-video paths, duration from explicit seconds or selected music. Retain original assets; no per-video JSON editing.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/unit/test_lofi.py tests/integration/test_lofi_render.py`

## L03 — Make the asset workflow the normal UI

**Status** [x] Six frontend checks, 63 contracts, TypeScript, formatting and build pass. Normal Chrome scene save → video creation → Preview confirmed; see `docs/evidence/l03-lofi-ui.json`.

**Target files**
- `docs/05-webapp.md`
- `web/src/session.ts`
- `web/src/lofi.ts`
- `web/src/lofi-state.ts`
- `web/tests/lofi-state.test.mjs`
- `web/src/main.ts`
- `web/src/wireframes.ts`
- `web/src/workspace.ts`
- `web/src/assets.ts`
- `web/src/preview.ts`
- `web/src/audio.ts`
- `web/src/production.ts`
- `web/src/style.css`
- `README.md`
- `docs/README.md`
- `docs/37-operations.md`
- `examples/README.md`
- `docs/evidence/l03-lofi-ui.json`
- `PLAN.md`
- `docs/tasks/INDEX.md`
- `docs/progress.md`
- `docs/38-v1-acceptance.md`
- `docs/tasks.md`

**Inputs / dependencies**
L02. Existing upload, asset library, preview/audio/render and release APIs.

**Implementation rules**
Start on the reusable scene/video workflow, not Flow. Support loading/editing scene drafts, new versions, assets, optional scenery and overlay timing, soundtrack/duration and creating a real episode. Guide users to actual preview and export controls. Mark placeholders synthetic. Keep progress/errors explicit and protect dirty forms. Do not add a generic editor or a mock renderer; keep useful advanced asset/review tools. Explain that old Flow projects and exports are preserved but generation editing is retired.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml make web-check web-build`

## L04 — Verify the full refactor and preservation

**Status** [x] 298 core, 62 actual-media and six frontend checks pass; package, normal Chrome preview/export/download/reuse, all 669 protected hashes and staged IDE preservation verified. See `docs/evidence/l04-lofi-refactor.json`.

**Target files**
- `web/src/production.ts`
- `docs/02-architecture.md`
- `docs/03-contracts.md`
- `docs/evidence/l04-lofi-refactor.json`
- `README.md`
- `docs/37-operations.md`
- `docs/README.md`
- `PLAN.md`
- `docs/tasks/INDEX.md`
- `docs/progress.md`
- `docs/38-v1-acceptance.md`
- `docs/tasks.md`

**Inputs / dependencies**
L01–L03. Normal-browser asset scene creation, preview playback and export required.

**Implementation rules**
Run all engineering gates and actual-media checks, verify representative normal browser workflow with synthetic media and saved scene reuse, compare preserved media/project hashes, check packaged contents and no tracked MP4. Record real-art preparation and Safari gaps. Update current docs around the final asset workflow. Do not generate/publish real art or claim aesthetic approval from fixtures.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml make check web-check web-build package test-media`

## L05 — Prepare and test a complete silent TABI Tokyo video

**Status** [x] Prepared real master/mask/six-district strip/blink assets; 2,700-frame silent 1080p
export passes full decode/timestamps. Fixed regions and next-cycle frame match exactly.
14 focused tests and source-preservation checks pass. Creative review remains pending; the
user's subsequent book-orientation correction is L06. Evidence: `docs/evidence/l05-tokyo-lofi-pilot.json`.

**Target files**
- `scripts/prepare_tokyo_lofi.py`
- `docs/evidence/l05-tokyo-lofi-pilot.json`
- `docs/tasks.md`
- `docs/tasks/INDEX.md`
- `docs/progress.md`
- `docs/38-v1-acceptance.md`
- `.local/tokyo-lofi-pilot-v1/` (prepared media, project, prompts, evidence and exports; untracked)

**Inputs / dependencies**
L01–L04. User request on 8 October: prepare all assets and try a full TABI Tokyo video, no music.
Use the original train still/profile and matching six Tokyo panoramas. Ninety seconds follows
the established trial length. Do not alter originals, invent source rights or approve artwork.

**Implementation rules**
Prepare a stable master, exact exterior mask, compatible varied scenery and restrained aligned
eye loops if they pass visual review. Reuse existing local rendering services; no new paid
dependency or video generator. Check official output terms before new image generation, record
exposed model/revision facts and unknowns. Preserve original content hashes. Save a reusable
scene and render the complete silent video through Python, verify timing, full decode, source
regions, motion/loop/chunk joins and actual visual playback. Keep all MP4s out of Git.

**Verification**
Asset dimensions/alpha/fps/hash checks; representative exact frames and contact sheets; full
90-second render/decode with zero audible content; normal-app preview/playback; preservation
audit. Record every limit honestly and commit verified scripts/evidence without media.

## L06 — Orient the sketchbook toward Tabi

**Status** [ ] Built-in image edit tool unavailable on the follow-up turn. Marco requested a
recheck; it remains absent from the current callable tools. A local perspective edit was offered
but not selected. No API fallback or image correction has been executed or claimed.

**Inputs / dependencies**
L05 original master and completed silent pilot. User asks to correct the upside-down book in
the train image and consider the next step. Preserve every original and existing asset version.

**Implementation rules**
Turn page content/book to face Tabi, keeping the table perspective, character, cup, pen and
lighting intact. Save a new master asset version and reusable scene; reuse the validated
window/panorama/blink timing. Do not rerun whole-scene video generation. Rebuild the silent
90-second pilot and inspect the corrected book, static regions, video decode and loop seam.
Source rights/creative approval remain separate. A longer silent playback test follows visual
acceptance; music stays absent from the current requested output.

## L07 — Define reusable cabin, look, journey and recipe contracts

**Status** [ ] Planned; first unblocked engineering task for the new request.

**Target files**
- `src/tabi/core/models/lofi_packs.py` — new strict pack and recipe models.
- `src/tabi/core/models/__init__.py` — register the four new document types.
- `src/tabi/core/persistence.py` — versioned registry paths for those types.
- `schemas/lofi_cabin_pack.schema.json` — new generated schema.
- `schemas/lofi_look_pack.schema.json` — new generated schema.
- `schemas/lofi_journey_pack.schema.json` — new generated schema.
- `schemas/lofi_recipe.schema.json` — new generated schema.
- `web/src/generated/lofi_cabin_pack.ts` — new generated browser type.
- `web/src/generated/lofi_look_pack.ts` — new generated browser type.
- `web/src/generated/lofi_journey_pack.ts` — new generated browser type.
- `web/src/generated/lofi_recipe.ts` — new generated browser type.
- `web/src/generated/documents.ts` — generated type registry.
- `web/src/generated/validators.cjs` — generated validators.
- `tests/unit/test_lofi_packs.py` — new contract and persistence coverage.
- `docs/tasks/INDEX.md` — register L07–L13 and retain L06's outstanding correction.
- `docs/progress.md` — record verified schema behavior when implemented.
- `docs/tasks.md` — record task status and evidence when implemented.

**Inputs / dependencies**
L02 and L05; `SceneTemplate`, `ActionPack`, `AssetRef`, `ApprovableDocument` and the
compatibility rules in `docs/34-activity-packs.md`. No generated artwork is required.

**Implementation rules**
- Add `LofiCabinPack`, `LofiLookPack`, `LofiJourneyPack` and `LofiRecipe` as versioned,
  hash-reviewed documents. Reject unknown fields, unsupported schema versions, duplicate
  slots/action roles and invalid frame intervals. Preserve old `LofiScene` serialization.
- Each pack names one exact existing `SceneTemplate` reference as its layout family, a title,
  thumbnail reference and explicit lighting/style compatibility. A cabin maps background
  and foreground roles to assets; a journey maps scenery slots to prepared strips; a look
  references an existing `ActionPack`, outfit ID and supported idle/blink/accent action IDs.
  Reuse `Action` and its pose/prop rules; do not introduce another animation clip format.
- A recipe selects exact cabin/look/journey versions, fps, a supported motion set, integer
  frame timing, seed and a travel setting. Distinguish an ordinary continuous export from
  a requested whole-video loop. Use existing request conversion for seconds and music;
  persisted times stay frames/samples. Keep referenced content hashes in preparation and
  render evidence so an unchanged label cannot disguise an asset edit.
- Do not make the old master field optional or reinterpret old scenes as modular art. New
  assets/approvals are new versions, and an imported recipe cannot assert source approval.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest -q tests/unit/test_lofi_packs.py tests/unit/test_lofi.py tests/unit/test_persistence.py tests/unit/test_contracts.py`

Generate with `UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 make schemas` and
`npm --prefix web run schemas`; check with `UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 make web-check`.
Verify legacy hashes, stale saves, immutable approvals and round trips of every new type.

## L08 — Prepare compatible layered assets once per pack

**Status** [ ] Planned.

**Target files**
- `src/tabi/core/lofi_preparation.py` — new bounded local preparation/import service.
- `src/tabi/core/models/lofi_packs.py` — strict preparation request types where needed.
- `src/tabi/core/fixture_lofi.py` — extend synthetic fixtures with a modular train family.
- `tests/unit/test_lofi_preparation.py` — new preparation and source-preservation tests.
- `tests/unit/test_lofi_packs.py` — pack compatibility cases.
- `tests/integration/test_lofi_preparation.py` — new actual-media conforming checks.
- `docs/progress.md` — preparation evidence and limits.
- `docs/tasks.md` — task status and evidence.

**Inputs / dependencies**
L07; existing `AssetService`, the L05 logic in `scripts/prepare_tokyo_lofi.py`, and the
locally configured Pillow/FFmpeg toolchain. Use small synthetic media first. The existing
pilot script and completed pilot remain reproducible.

**Implementation rules**
- Register a new modular train template with body/face channels, a character anchor, ordered
  background/scenery/character/foreground slots, fixed window masks and strip periods.
  The current flat pilot template remains a valid legacy scene; it has no character slot.
- Support a clean empty cabin backplate, transparent Tabi body/face frames, foreground table
  and fixed props, the family's window mask, and prepared panoramic strips. A character
  motion replaces the idle body; it must not be composited over a Tabi painted in the cabin.
- Accept already separated/painted artwork and prepared poses. Normalize dimensions, color,
  alpha and fps, validate frame bounds and anchors, and register immutable media versions.
  Cutting a character out does not restore the hidden seat or wall: clean plates require
  image preparation and visual review. Do not claim to infer missing artwork automatically.
- Generalize deterministic strip preparation from the pilot with explicit crop/horizon,
  ordering and join parameters. For the first family, conform journeys to the family's
  fixed strip period and exact opening-pixel padding. Reject unusable sources rather than
  stretching landmarks to conceal a length mismatch. Review each district join; repeated
  foliage and pixel padding alone do not establish an attractive panorama.
- Conform authored motion frames and optionally bake small bounded cyclic movements of
  separately supplied body/gill parts using the existing image toolchain. Protect the face,
  headphones, book and hands unless their matching poses are supplied. A new look may reuse
  a motion recipe, but its exported frames and alignment must be reviewed for that look.
- Validate template, camera, canvas, lighting, alpha, masks and action/outfit compatibility.
  Keep useful errors tied to the actual missing/mismatched asset. Bound source sizes/frame
  counts, resolve only registered roots, and use temporary outputs plus atomic promotion.
- Record source hashes and factual provenance; synthetic fixtures remain visibly synthetic.
  Use no new generator, model, font or external service in this task. Original media and the
  L05 output are never overwritten. Preparation does not grant artistic approval.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/unit/test_lofi_preparation.py tests/unit/test_lofi_packs.py tests/integration/test_lofi_preparation.py`

Check valid imports, wrong dimensions/fps/alpha, incomplete frames, nonperiodic padding,
spaces/Unicode, symlink/root escapes and failed preparation leaving sources/registry intact.

## L09 — Compose selected packs through the existing renderer

**Status** [ ] Planned.

**Target files**
- `src/tabi/core/lofi_composition.py` — new recipe-to-episode adapter.
- `src/tabi/core/lofi_preparation.py` — shared semantic pack validation.
- `src/tabi/core/fixture_lofi.py` — two synthetic looks, cabins and journeys.
- `tests/unit/test_lofi_composition.py` — new composition and version tests.
- `tests/integration/test_lofi_composition.py` — new compositing pixel checks.
- `docs/progress.md` — composition evidence.
- `docs/tasks.md` — task status and evidence.

**Inputs / dependencies**
L07–L08; `AuthoringService.prepare_episode`, `SceneInstance.slot_assignments`, the existing
body/face `ActionCompiler`, preview/snapshot services and FFmpeg renderer.

**Implementation rules**
- Keep a single immutable template per supported family. Apply cabin and journey assets
  with existing scene slot assignments, and select the look's exact action pack/outfit ID.
  `ActionPack.template` must still match the scene template; do not relax that check or
  generate a different template for each color/outfit combination. Family masks, anchors
  and strip periods stay fixed; geometry changes create a new family and matching packs.
- Render in authored order: empty cabin, masked exterior, character body/face, foreground
  occluders/props. Use the existing character slot. Reject incorrect asset kinds and role
  assignments before rendering; metadata checks cannot replace a real ghosting/edge review.
- Initially cover the whole episode with the look's valid idle action. Use authored complete
  cycles and an explicit compatible rest/hold for any remainder; no body timeline gaps.
  Music-free creation produces zero audio streams. Retain existing optional soundtrack and
  duration behavior for normal use.
- Freeze selected asset identities, pack versions and recipe content in the normal episode/
  snapshot path before jobs run. Later recipe selections must not change an existing render.
  Keep save conflicts, hash validation, cache identity and failure atomicity intact.
- Compare every pack's template, light/style, canvas/fps and prop expectations in Python.
  Reject incompatible mixes with actionable messages. No browser composition engine, new
  FFmpeg command path, database or whole-scene generation service is needed.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/unit/test_lofi_composition.py tests/unit/test_activity_packs.py tests/unit/test_lofi.py tests/integration/test_lofi_composition.py tests/integration/test_lofi_render.py`

Exercise all eight synthetic 2×2×2 combinations; check that each selection changes only its
intended region, including cabin pixels exposed behind a moving character. Verify exact
template binding, outfit rejection, foreground occlusion and preservation of the old pilot.

## L10 — Schedule three quiet motions without phase jumps

**Status** [ ] Planned; Marco chose gentle loops.

**Target files**
- `src/tabi/core/lofi_motion.py` — new bounded recipe motion scheduler.
- `src/tabi/core/lofi_composition.py` — invoke the scheduler before shared compilation.
- `src/tabi/core/fixture_lofi.py` — synthetic matching idle, blink and gill action frames.
- `tests/unit/test_lofi_motion.py` — new coverage, channel and looping tests.
- `tests/integration/test_lofi_composition.py` — nonzero-range and chunk-boundary checks.
- `docs/progress.md` — motion evidence and limits.
- `docs/tasks.md` — task status and evidence.

**Inputs / dependencies**
L09; existing `ActionRequest`, global-frame timeline, transition/prop rules and versioned
seeded randomness in `src/tabi/core/timeline/random.py`. No new motion generator is required.

**Implementation rules**
- Offer prepared per-look motion sets containing slow breathing, sparse blinks and an
  occasional small gill movement. Keep the head still for the first real set so blinking
  stays registered to the eyes. Head movement is allowed only with matching face frames,
  or a full-body clip that owns the face channel for that interval.
- Fill the body channel for every frame. Alternate authored idle/accent cycles with valid
  entry/exit poses and complete returns to rest; never stretch or crossfade a gesture to
  make it fit. Preserve body/face occupancy and prop constraints from the existing compiler.
- Choose deterministic compatible blink windows after body scheduling. Reuse the existing
  versioned PRNG where variation is needed. Unresolvable conflicts or impossible timings
  fail with a useful error; do not drop requested motions silently.
- Compile the full schedule once in episode-global frames. Previews, chunked export and
  resume use that same schedule and phase. Do not restart breathing or blinks per chunk.
- For an explicitly requested whole-video loop, require returning body/prop state, seamless
  authored clip boundaries and matching scenery phase at the output seam. If the chosen
  duration/speed cannot satisfy them, explain the compatible settings rather than silently
  speeding up the train or trimming a gesture. Ordinary continuous videos need no claim
  of a seamless end-to-start cut.
- Tests establish schedule/phase correctness; real review must check eye placement, gill
  edges and breathing amplitude. Sipping, page-turning and an arbitrary skeleton/rig editor
  are outside this task.
- As soon as L06 and separated real artwork are available, preview one real look with all
  three motions before expanding the library. Record preparation effort and visible defects;
  a poor result should narrow the motion set before UI polish. Synthetic implementation can
  proceed while that independent art preparation is unavailable.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/unit/test_lofi_motion.py tests/unit/test_timeline.py tests/unit/test_activity_packs.py tests/integration/test_lofi_composition.py tests/integration/test_activity_render.py`

Cover identical-seed schedules, different seeds within bounds, idle remainders, action/face
collisions, rational fps, export duration failures, nonzero preview starts and every chunk
join. Inspect adjacent seam frames as well as the repeated-cycle frame identity.

## L11 — Expose pack preparation and recipe creation to CLI and API

**Status** [ ] Planned.

**Target files**
- `src/tabi/api/lofi.py` — authenticated pack catalog/preparation and recipe routes.
- `src/tabi/api/contracts.py` — new `WebLofiPacks` response contract.
- `src/tabi/cli/lofi.py` — corresponding commands using the same Python services.
- `schemas/web_lofi_packs.schema.json` — new generated response schema.
- `web/src/generated/web_lofi_packs.ts` — new generated browser type.
- `web/src/generated/documents.ts` — generated type registry.
- `web/src/generated/validators.cjs` — generated validators.
- `tests/unit/test_lofi_pack_api.py` — new API/CLI parity and boundary checks.
- `docs/progress.md` — transport verification.
- `docs/tasks.md` — task status and evidence.

**Inputs / dependencies**
L08–L10; existing authenticated runtime, root registration, import/media endpoints, revision
guards and job ownership checks. Existing lo-fi scene routes remain compatible.

**Implementation rules**
- Add a pack catalog with exact versions, thumbnails, approval status and compatibility
  reasons; add guarded recipe save/create-video and bounded preparation entry points.
  Reuse the existing upload/import flow. API and CLI call the same services with typed
  requests; neither should construct its own timeline or image-processing command.
- Return real validation failures for missing packs, stale revisions, wrong family/light,
  unavailable motions and invalid loop duration. Publish only fully validated preparation
  results. Long preparation, if required by actual measured inputs, uses owned jobs and
  cancellation; do not add a separate task queue speculatively.
- Preserve loopback/token/Host/Origin/CSRF protections and authenticated thumbnails/media.
  Client paths do not register new filesystem roots. Keep failed saves from creating a
  partially usable recipe or episode. No provider credentials or external generation route.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest -q tests/unit/test_lofi_pack_api.py tests/unit/test_lofi.py tests/unit/test_web_service.py tests/unit/test_contracts.py`

Regenerate schemas/browser contracts as in L07. Verify API/CLI parity, stale writes, session
authentication, mutation protections, root escapes and failure preservation.

## L12 — Make each new video a guided choice of compatible packs

**Status** [ ] Planned.

**Target files**
- `web/src/lofi.ts` — pack selectors and recipe-to-preview flow.
- `web/src/lofi-state.ts` — selection and dirty/stale state.
- `web/src/assets.ts` — guided import/preparation using existing asset controls.
- `web/src/style.css` — focused layout and thumbnail styles.
- `web/tests/lofi-state.test.mjs` — dependent-selection and stale-form tests.
- `PLAN.md` — document the implemented modular workflow and its preparation limits.
- `docs/05-webapp.md` — daily workflow and pack preparation requirements.
- `docs/37-operations.md` — reuse and importing new artwork.
- `docs/evidence/l12-lofi-packs-ui.json` — new browser verification evidence.
- `docs/progress.md` — implementation evidence.
- `docs/tasks.md` — task status and evidence.

**Inputs / dependencies**
L11 and the working Preview/Export screens. Use synthetic L08 packs until real artwork is
ready; L06 is not a dependency of UI implementation.

**Implementation rules**
- Provide thumbnail selections for Tabi's outfit, cabin and Tokyo journey, followed by
  supported quiet motion sets, duration and the existing optional soundtrack controls.
  Python supplies compatibility/validation; the browser only displays and submits choices.
- Offer creation from a saved recipe. Show the previous outfit/cabin/journey alongside new
  selections so Marco can change all three for each video. Surface unchanged selections
  and available alternatives; an exhausted library cannot produce a new outfit by changing
  its label. Do not invent publishing history or add random auto-generation.
- Let users import a prepared pack through the existing uploader with a clear required-file
  checklist and local preparation feedback. Explain the fixed layout/reference requirements
  when new art is needed. Do not expose a nonfunctional image-generation button.
- Show only compatible selections, but explain why other packs are unavailable. Preserve
  valid choices when switching a pack; surface conflicts rather than silently replacing the
  look or motion. Retain dirty-form protection and optimistic revision checks.
- Save a real recipe and episode, then use the existing short-preview and export services.
  No hand-written JSON should be needed for ordinary video creation. Keep the original
  saved-scene workflow usable, including the L05 pilot. No mock preview or stub controls.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml make web-check web-build`

In the normal browser, import prepared synthetic packs, select a combination, save, preview,
export and start a second video with all three selections changed. Reload both and verify
their stored selections; exercise incompatible packs and a stale-save error. Record actual
screenshots, job/output paths and pending target-Mac/Safari checks in the evidence file.

## L13 — Prove reuse with real Tabi assets and silent Tokyo exports

**Status** [ ] Planned; requires real layered artwork and the functioning pack workflow.

**Target files**
- `docs/evidence/l13-lofi-variants.json` — new source, preparation, render and review evidence.
- `docs/38-v1-acceptance.md` — actual engineering/creative/release gate results.
- `docs/progress.md` — verified outcome and remaining limits.
- `docs/tasks/INDEX.md` — final status of the new milestone and outstanding work.
- `docs/tasks.md` — task status and evidence.

**Inputs / dependencies**
L06 and L08–L12. Reuse the supplied Tabi reference and L05 source images; prepare original
character/cabin layers and two compatible options in each category. The original green
outfit may be one of the two. Image preparation requires an available authorized editor;
an unavailable tool blocks this real-art task, not the earlier synthetic work.

**Implementation rules**
- Correct the book and create clean background, character, face/gill and foreground assets
  as new versions. Compare the actual reference to preserve Tabi's face, proportions and
  headphones. Prepare one additional outfit with its own matched motions, one additional
  cabin design in the same geometry, and two distinct district/view selections for Tokyo.
  Simple re-titling or recoloring the same panorama is not the intended outside variation.
- Check official commercial/output terms before any newly introduced generator, model,
  asset or font; record source/version/review date and unknowns without inventing exposed
  model IDs or rights. Use existing entitlements only, with no new purchase/top-up. Keep
  unconfirmed source rights pending. Record actual art preparation effort and retries.
- Preview all eight 2×2×2 combinations briefly, focusing on separation edges, lighting,
  occlusion, eye/gill alignment and district joins. Use one strongest combination for a
  complete 90-second silent export through the normal app, followed by a 10-minute silent
  duration/phase check. Choose valid loop settings explicitly where a whole-output loop
  is requested. Keep the original pilot playable and unchanged.
- Review actual playback around each motion, district join, chunk boundary and output seam;
  verify full decode, intended frame count, audio-stream absence and source preservation.
  Record engineering evidence separately from Marco's creative decision. A passing render
  does not approve the new outfit or motion style.
- Demonstrate preparing a pack once and creating another video by selecting stored packs
  without manually reconnecting clips or editing source JSON. Two options per category are
  a compatibility test, not an indefinitely unique release library; continued unique videos
  require adding and reviewing more outfits, interiors and journeys.
- Keep generated media and MP4s locally under `.local/lofi-variants-v1/`; commit only small
  permitted evidence/docs. Do not upload, publish, add music or overwrite approved assets.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml make check web-check web-build package test-media`

Complete the normal-browser real-asset walkthrough above and record exact pack/template
versions, content hashes, preparation time, app actions, export paths, frame/decode results
and contact-sheet paths in `docs/evidence/l13-lofi-variants.json`. Broad tests run once after
focused checks pass; any unresolved visual defects remain explicit creative gates.
