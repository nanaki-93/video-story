import numpy as np
import pytest
from PIL import Image, ImageDraw
from test_chunk_assembly import audio, setup

from tabi.core.cache.store import CacheStore
from tabi.core.fixtures import file_hash
from tabi.core.models import Asset, Episode
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


def test_audio_edit_reuses_video_corrupt_cache_rerenders_and_visual_edit_invalidates(tmp_path):
    service, snapshot, digest, profile = setup(tmp_path, "core")
    graphs, aac = [], []

    def observe(process):
        if "-/filter_complex" in process.args:
            graphs.append(process.args)
        if "-c:a" in process.args and process.args[process.args.index("-c:a") + 1] == "aac":
            aac.append(process.args)

    service.on_process = observe

    def render(snapshot_digest, name):
        service.submit(
            snapshot_digest, profile, f"exports/{name}.mp4", end_frame=72, max_chunk_frames=36
        )
        result = service.work()[0]
        assert result.state == "verified", result.error
        return result

    original = render(digest, "first")
    assert len(graphs) == 2 and len(aac) == 1
    data = snapshot.episode.model_dump(mode="json")
    data["tracks"][0]["gain_db"] = -6
    edited = ActionCompiler(service.assets, purpose="synthetic_test").compile(
        Episode.model_validate(data)
    )
    new_digest = service.store.save_snapshot(edited)
    assert new_digest != digest
    graphs.clear()
    aac.clear()
    reused = render(new_digest, "quieter")
    assert not graphs and len(aac) == 1
    reports = [service.store.read(c.report_path) for c in reused.chunks]
    assert all(r.cache_reuse.origin_snapshot_sha256 == digest for r in reports)
    assert all(r.snapshot_sha256 == new_digest for r in reports)
    assert [c.output.sha256 for c in reused.chunks] == [c.output.sha256 for c in original.chunks]
    first_audio = audio(service.settings, service.store.root / original.destination, 115200)
    second_audio = audio(service.settings, service.store.root / reused.destination, 115200)
    ratio = np.sqrt(np.mean(second_audio**2) / np.mean(first_audio**2))
    assert abs(ratio - 10 ** (-6 / 20)) < 0.005

    cache = CacheStore(service.store)
    key = reports[0].cache_reuse.key
    payload = service.store.root / cache.identity("video_chunk", key) / "payload.mp4"
    payload.write_bytes(b"corrupt cached video")
    assert file_hash(service.store.root / reused.chunks[0].output.location.path) == (
        reused.chunks[0].output.sha256
    )
    graphs.clear()
    repaired = render(new_digest, "repaired")
    assert len(graphs) == 1
    assert service.store.read(repaired.chunks[0].report_path).cache_reuse is None
    assert service.store.read(repaired.chunks[0].report_path).normalized_cache_hits > 0
    assert service.store.read(repaired.chunks[1].report_path).cache_reuse is not None
    assert all(entry.valid for entry in cache.inventory().entries)

    data["curves"][0]["keys"][0]["value"] = 100
    data["scenes"][0]["final_state"] = None
    changed = ActionCompiler(service.assets, purpose="synthetic_test").compile(
        Episode.model_validate(data)
    )
    graphs.clear()
    invalidated = render(service.store.save_snapshot(changed), "different-motion")
    assert len(graphs) == 2
    assert all(service.store.read(c.report_path).cache_reuse is None for c in invalidated.chunks)
    assert invalidated.chunks[0].output.sha256 != repaired.chunks[0].output.sha256

    # Changing real source bytes invalidates old snapshots, including cached ones.
    source = service.store.root / "assets/fixture.idle/000000.png"
    with Image.open(source) as image:
        ImageDraw.Draw(image).rectangle((20, 20, 60, 60), fill=(255, 0, 255, 255))
        image.save(source)
    with pytest.raises(ValueError):
        service.submit(digest, profile, "exports/stale.mp4", end_frame=72)
    asset = service.store.read("registry/assets/fixture.idle/1.0.json")
    metadata = asset.model_dump(mode="json")
    metadata["files"][0].update(sha256=file_hash(source), size_bytes=source.stat().st_size)
    service.store.save_draft(Asset.model_validate(metadata), expected_revision=asset.revision)
    changed = ActionCompiler(service.assets, purpose="synthetic_test").compile(
        Episode.model_validate(data)
    )
    graphs.clear()
    new_source = render(service.store.save_snapshot(changed), "new-source")
    assert len(graphs) == 2
    assert new_source.chunks[0].output.sha256 != invalidated.chunks[0].output.sha256
