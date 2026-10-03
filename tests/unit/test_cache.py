import errno
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from tabi.cli.main import main
from tabi.core.assets import AssetService
from tabi.core.cache.keys import image_descriptor, video_descriptor
from tabi.core.cache.storage import estimate_storage
from tabi.core.cache.store import CacheStore
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.jobs import JobService
from tabi.core.models import Asset, Episode
from tabi.core.models.base import Canvas, content_hash
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectBusy, ProjectStore, StorageError, UnsafePath
from tabi.core.render.backend import FrozenRegistry
from tabi.core.render.normalize import ImageNormalizer
from tabi.core.timeline.compiler import ActionCompiler


@pytest.fixture
def cached_project(tmp_path):
    root = tmp_path / "Cache's 東京"
    generate_fixtures(root)
    assets = AssetService(ProjectStore(root))
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(
        assets.store.read("episodes/episode.synthetic.json")
    )
    digest = assets.store.save_snapshot(snapshot)
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    service = JobService(assets, settings)
    profile = OutputProfile(
        id="cache-test",
        canvas=Canvas(width=320, height=180),
        fps=snapshot.episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
        audio_codec="aac",
    )
    job = service.submit(digest, profile, "exports/test.mp4", end_frame=72, max_chunk_frames=36)
    return service, snapshot, job


def image_cache(cached_project, tmp_path):
    service, snapshot, _ = cached_project
    registry = FrozenRegistry(service.assets, snapshot)
    asset = registry.documents[("fixture.idle", "1.0")]
    normalizer = ImageNormalizer(registry, tmp_path / "normalized")
    result = normalizer.prepare(asset)
    descriptor = image_descriptor(asset, 0, snapshot.purpose)
    cache = CacheStore(service.store)
    return cache, descriptor, result, asset, registry


def test_normalized_cache_reuses_verified_pixels_and_repairs_corruption(cached_project, tmp_path):
    cache, descriptor, first, asset, registry = image_cache(cached_project, tmp_path)
    expected = first.read_bytes()
    second = ImageNormalizer(registry, tmp_path / "second")
    assert second.prepare(asset).read_bytes() == expected
    assert second.cache_hits == 1
    entry = cache.lookup("normalized_image", descriptor)
    payload = cache.store.root / entry.output.location.path
    payload.write_bytes(b"corrupted")
    third = ImageNormalizer(registry, tmp_path / "third")
    assert third.prepare(asset).read_bytes() == expected
    assert third.cache_hits == 0
    assert cache.lookup("normalized_image", descriptor).output == entry.output
    registry.verify()


def test_video_key_ignores_audio_but_tracks_visual_content_and_versions(
    cached_project, monkeypatch
):
    service, snapshot, job = cached_project
    registry = FrozenRegistry(service.assets, snapshot)
    key = content_hash(video_descriptor(snapshot, registry, job, job.chunks[0]))
    data = snapshot.episode.model_dump(mode="json")
    data["tracks"][0]["gain_db"] = -6
    changed = ActionCompiler(service.assets, purpose="synthetic_test").compile(
        Episode.model_validate(data)
    )
    updated = job.model_copy(
        update={
            "profile": job.profile.model_copy(
                update={"id": "renamed", "audio_gain_db": -3, "audio_codec": None}
            )
        }
    )
    assert content_hash(video_descriptor(changed, registry, updated, job.chunks[0])) == key
    data["curves"][0]["keys"][0]["value"] = 61
    data["scenes"][0]["final_state"] = None
    changed = ActionCompiler(service.assets, purpose="synthetic_test").compile(
        Episode.model_validate(data)
    )
    assert content_hash(video_descriptor(changed, registry, job, job.chunks[0])) != key
    for replacement in (
        job.model_copy(
            update={
                "profile": job.profile.model_copy(update={"canvas": Canvas(width=640, height=360)})
            }
        ),
        job.model_copy(
            update={"plan": job.plan.model_copy(update={"toolchain_fingerprint": "a" * 64})}
        ),
    ):
        assert content_hash(video_descriptor(snapshot, registry, replacement, job.chunks[0])) != key
    asset = registry.documents[("fixture.idle", "1.0")]
    descriptor = image_descriptor(asset, 0, snapshot.purpose)
    assert image_descriptor(asset, 1, snapshot.purpose) != descriptor
    assert image_descriptor(asset, 0, "production") != descriptor
    monkeypatch.setattr("tabi.core.cache.keys.PIL.__version__", "different runtime")
    assert content_hash(video_descriptor(snapshot, registry, job, job.chunks[0])) != key
    assert image_descriptor(asset, 0, snapshot.purpose) != descriptor


def test_prune_is_explicit_and_preserves_unknown_files_sources_and_snapshots(
    cached_project, tmp_path, capsys
):
    cache, descriptor, _, _, registry = image_cache(cached_project, tmp_path)
    entry = cache.lookup("normalized_image", descriptor)
    payload = cache.store.root / entry.output.location.path
    unknown = payload.parent / "keep.txt"
    unknown.write_text("not managed by this cache")
    before = {p: p.read_bytes() for p in (cache.store.root / "snapshots").glob("*.json")}
    project = ["--project", str(cache.store.root)]
    assert main(["cache", "prune", *project, "--all"]) == 0
    inventory = json.loads(capsys.readouterr().out)
    assert payload.exists()
    assert main(["cache", "prune", *project, "--all", "--apply"]) == 4
    assert payload.exists()
    assert (
        main(
            [
                "cache",
                "prune",
                *project,
                "--all",
                "--apply",
                "--inventory",
                inventory["inventory_sha256"],
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["removed"] == [entry.key]
    assert not payload.exists() and unknown.read_text() == "not managed by this cache"
    assert all(p.read_bytes() == data for p, data in before.items())
    registry.verify()


def test_prune_rejects_stale_inventory_and_worker_contention(cached_project, tmp_path):
    cache, descriptor, _, _, _ = image_cache(cached_project, tmp_path)
    observed = cache.inventory()
    payload = cache.store.root / cache.lookup("normalized_image", descriptor).output.location.path
    with cache.store.exclusive_lock(".tabi-worker.lock"), pytest.raises(ProjectBusy):
        cache.prune([observed.entries[0].key], expected_inventory=observed.inventory_sha256)
    payload.write_bytes(b"changed")
    with pytest.raises(StorageError, match="inventory changed"):
        cache.prune([observed.entries[0].key], expected_inventory=observed.inventory_sha256)
    assert payload.read_bytes() == b"changed"
    latest = cache.inventory()
    assert not latest.entries[0].valid
    assert cache.prune([latest.entries[0].key], expected_inventory=latest.inventory_sha256).removed


def test_cache_that_became_authored_source_cannot_be_pruned_or_replaced(cached_project, tmp_path):
    cache, descriptor, source, asset, _ = image_cache(cached_project, tmp_path)
    entry = cache.lookup("normalized_image", descriptor)
    data = asset.model_dump(mode="json")
    data["source"] = entry.output.location.model_dump()
    cache.store.save_draft(Asset.model_validate(data), expected_revision=asset.revision)
    observed = cache.inventory()
    assert observed.entries[0].protected
    with pytest.raises(StorageError, match="referenced as source"):
        cache.prune([entry.key], expected_inventory=observed.inventory_sha256)
    payload = cache.store.root / entry.output.location.path
    payload.write_bytes(b"preserve even a changed authored source")
    assert cache.put("normalized_image", descriptor, source, refresh=True) is None
    assert payload.read_bytes() == b"preserve even a changed authored source"


def test_cache_refuses_symlinks_and_path_escape(cached_project, tmp_path):
    cache, descriptor, _, _, _ = image_cache(cached_project, tmp_path)
    entry = cache.lookup("normalized_image", descriptor)
    payload = cache.store.root / entry.output.location.path
    original = tmp_path / "original.png"
    original.write_bytes(payload.read_bytes())
    payload.unlink()
    payload.symlink_to(original)
    with pytest.raises(UnsafePath):
        cache.lookup("normalized_image", descriptor)
    assert cache.inventory().warnings
    with pytest.raises(ValueError):
        cache.identity("normalized_image", "../../original.png")
    assert original.exists()


def test_cross_volume_export_never_deletes_an_existing_destination(
    cached_project, tmp_path, monkeypatch
):
    cache, descriptor, _, _, _ = image_cache(cached_project, tmp_path)
    destination = tmp_path / "existing.png"
    destination.write_bytes(b"user file")

    def cross_device(*args, **kwargs):
        raise OSError(errno.EXDEV, "test cross-volume copy")

    monkeypatch.setattr("tabi.core.cache.store.os.link", cross_device)
    with pytest.raises(FileExistsError):
        cache.lookup("normalized_image", descriptor, destination=destination)
    assert destination.read_bytes() == b"user file"


def test_storage_preflight_stops_before_rendering_and_accounts_for_warm_images(
    cached_project, tmp_path, monkeypatch
):
    service, _, job = cached_project
    cold = estimate_storage(service.assets, job)
    image_cache(cached_project, tmp_path)
    warm = estimate_storage(service.assets, job)
    assert 0 < warm.normalization_bytes < cold.normalization_bytes
    assert cold.audio_bytes > 72 * 1600 * 24 and cold.reserve_bytes >= 256 * 1024 * 1024
    monkeypatch.setattr(
        "tabi.core.cache.storage.shutil.disk_usage", lambda p: SimpleNamespace(free=1)
    )
    monkeypatch.setattr(
        "tabi.core.jobs.service.doctor",
        lambda *a: SimpleNamespace(
            ready=True,
            fingerprint="a" * 64,
            encoders=["libx264", "aac"],
        ),
    )
    monkeypatch.setattr(
        "tabi.core.jobs.service.FFmpegRenderer.clip",
        lambda *a: pytest.fail("insufficient storage reached the renderer"),
    )
    result = service.work()[0]
    assert result.state == "failed" and result.completed_frames == 0
    assert "insufficient project storage" in result.error.message
    assert not (service.store.root / job.destination).exists()
