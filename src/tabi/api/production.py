"""Frozen export setup, measured progress, local preferences and safe cache controls."""

from fastapi import APIRouter, HTTPException, Query

from tabi.core.cache.storage import estimate_storage
from tabi.core.cache.store import CacheStore
from tabi.core.episodes import EpisodeService
from tabi.core.preferences import PreferencesService, SavePreferences, SaveTools
from tabi.core.render.profiles import preset_profile
from tabi.core.toolchain import doctor

from .contracts import (
    CompileRequest,
    PruneCache,
    RenderRequest,
    Review,
    WebCache,
    WebRenderPlan,
    WebSettings,
)


def routes(runtime):
    router = APIRouter(prefix="/api/v1")

    @router.get("/settings", response_model=WebSettings)
    def settings():
        service = PreferencesService(runtime.settings)
        preferences, saved = service.read()
        return WebSettings(
            schema_version="1.0",
            config_file=str(runtime.settings.config_file),
            config_sha256=service.config_hash(),
            ffmpeg=runtime.settings.ffmpeg,
            ffprobe=runtime.settings.ffprobe,
            cache_root=str(runtime.settings.cache_root),
            preferences=preferences,
            preferences_saved=saved,
        )

    @router.post("/settings/preferences")
    def preferences(body: SavePreferences):
        return PreferencesService(runtime.settings).save(body.preferences, body.expected_revision)

    @router.post("/settings/tools")
    def tools(body: SaveTools):
        PreferencesService(runtime.settings).save_tools(
            body.ffmpeg, body.ffprobe, body.expected_hash
        )
        return settings()

    @router.get("/projects/{handle}/doctor")
    def health(handle: str):
        return doctor(runtime.settings, runtime.get(handle).assets.store.root)

    @router.post("/projects/{handle}/episodes/{identity}/compile")
    def compile_episode(handle: str, identity: str, body: CompileRequest):
        return EpisodeService(runtime.get(handle).assets, runtime.settings).compile_saved(
            identity, expected_revision=body.expected_revision, purpose=body.purpose
        )

    @router.post("/projects/{handle}/snapshots/{digest}/review")
    def review(handle: str, digest: str, body: Review):
        return EpisodeService(runtime.get(handle).assets, runtime.settings).review_snapshot(
            digest, **body.model_dump()
        )

    def prepare(handle, body):
        item = runtime.get(handle)
        snapshot = item.assets.store.read_snapshot(body.snapshot_sha256)
        profile = preset_profile(body.preset, fps=snapshot.episode.fps, encoder=body.encoder)
        job = item.jobs.prepare(
            body.snapshot_sha256,
            profile,
            body.destination,
            first_frame=body.first_frame,
            end_frame=body.end_frame,
            max_chunk_frames=body.max_chunk_frames,
        )
        return item, job

    @router.post("/projects/{handle}/renders/plan", response_model=WebRenderPlan)
    def plan(handle: str, body: RenderRequest):
        item, job = prepare(handle, body)
        return WebRenderPlan(
            schema_version="1.0", job=job, storage=estimate_storage(item.assets, job)
        )

    @router.post("/projects/{handle}/renders")
    def submit(handle: str, body: RenderRequest):
        if runtime.stopping.is_set():
            raise HTTPException(409, "Worker is stopping")
        item, job = prepare(handle, body)
        estimate = estimate_storage(item.assets, job)
        if not estimate.sufficient:
            raise ValueError("Insufficient project space for this conservative estimate")
        result = item.jobs.ledger.create(job)
        runtime.wake.set()
        return result

    @router.get("/projects/{handle}/jobs/{identity}/progress")
    def progress(handle: str, identity: str):
        return runtime.get(handle).jobs.progress(identity)

    @router.post("/projects/{handle}/jobs/{identity}/pause")
    def pause(handle: str, identity: str):
        return runtime.pause(runtime.get(handle), identity)

    @router.post("/projects/{handle}/jobs/{identity}/verify")
    def verify(handle: str, identity: str):
        return runtime.get(handle).jobs.verify_export(identity)

    @router.get("/projects/{handle}/cache", response_model=WebCache)
    def cache(handle: str, budget_bytes: int | None = Query(default=None, ge=0)):
        service = CacheStore(runtime.get(handle).assets.store)
        inventory = service.inventory()
        budget = (
            PreferencesService(runtime.settings).read()[0].cache_budget_bytes
            if budget_bytes is None
            else budget_bytes
        )
        return WebCache(
            schema_version="1.0",
            inventory=inventory,
            budget_bytes=budget,
            proposed_keys=service.budget_selection(inventory, budget),
        )

    @router.post("/projects/{handle}/cache/prune")
    def prune(handle: str, body: PruneCache):
        return CacheStore(runtime.get(handle).assets.store).prune(
            body.keys, expected_inventory=body.expected_inventory
        )

    return router
