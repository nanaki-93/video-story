# Reusable assets for lo-fi videos

Marco authorizes refactoring the app and deleting unnecessary old code. Preserve all artwork, music, original footage, exports and saved project files. The earlier Flow queue is retired; its task history is in `docs/archive/flow-tasks.md`. Implement one task at a time, verify and commit with its ID.

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

**Status** [ ]

**Target files**
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

**Status** [ ]

**Target files**
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
