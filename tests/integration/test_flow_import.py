import hashlib
import os
from pathlib import Path

import pytest

from tabi.core.config import load_settings
from tabi.core.flow.media import FlowMedia
from tabi.core.flow.service import FlowError, FlowService, references_hash, updated
from tabi.core.models.base import FrameInterval, MediaPath, content_hash
from tabi.core.models.flow import FlowAttempt, FlowBeat, FlowLimits, FlowRecipe, FlowState
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool

pytestmark = pytest.mark.media


def media_context(tmp_path, *, target=2160):
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    sources = tmp_path / "native 東京 files"
    sources.mkdir()
    store = ProjectStore.initialize(tmp_path / "project", "Synthetic Flow test")
    service = FlowService(store, {"source": sources})
    episode = service.create(
        "Synthetic train",
        FlowLimits(
            credit_ceiling=0,
            remaining_allowance=0,
            estimated_credit_per_attempt=0,
            allowance_checked_at="2026-10-06 synthetic",
        ),
        recipe=FlowRecipe(opening_mode="text_reference", target_frames=target),
    )
    return settings, sources, service, episode


def pending(service, episode):
    parent = service.candidate(episode, episode.accepted_ids[-1]) if episode.accepted_ids else None
    prompt = "Synthetic fixture, no provider submission."
    attempt = FlowAttempt(
        schema_version="1.0",
        id=f"attempt-{len(episode.attempts)}",
        episode_id=episode.id,
        parent_id=parent.id if parent else None,
        parent_sha256=parent.media.sha256 if parent else None,
        recipe_sha256=content_hash(episode.recipe),
        references_sha256=references_hash(episode),
        beat=FlowBeat(id=f"beat-{len(episode.attempts)}", kind="rest", target_frame=0),
        mode="extend" if parent else "text_reference",
        prompt=prompt,
        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
        state="awaiting_external",
        reserved_credits=0,
    )
    return service.save(
        updated(episode, attempts=[*episode.attempts, attempt]), expected_revision=episode.revision
    )


def make_clip(settings, path, frames=192, hue=0, gap=False):
    filters = f"hue=h={hue}"
    if gap:
        filters += ",setpts=PTS+gte(N\\,96)/TB"
    run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=96x54:rate=24",
            "-frames:v",
            str(frames),
            "-vf",
            filters,
            "-fps_mode",
            "passthrough",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ]
    )


def accept_last(service, episode):
    candidate = episode.candidates[-1]
    return service.review(
        episode.id,
        candidate.id,
        revision=episode.revision,
        media_sha256=candidate.media.sha256,
        decision="accepted",
        note="Synthetic fixture reviewed only for testing.",
        observed_state=FlowState(cup_kind="none", hands="resting", pose="watching"),
        safe_end_frame=candidate.trim.end_frame,
    )


def test_8_7_7_native_frames_preserved_and_receipt_is_idempotent(tmp_path):
    settings, sources, service, episode = media_context(tmp_path)
    importer = FlowMedia(service, settings)
    originals = []
    for index, frames in enumerate([192, 168, 168]):
        path = sources / f"clip {index}.mp4"
        make_clip(settings, path, frames, index * 40)
        originals.append(path.read_bytes())
        episode = pending(service, episode)
        attempt = episode.attempts[-1]
        episode = importer.import_result(
            episode.id,
            attempt.id,
            MediaPath(root_id="source", path=path.name),
            revision=episode.revision,
            synthetic=True,
        )
        assert episode.candidates[-1].frame_count == frames
        repeated = importer.import_result(
            episode.id,
            attempt.id,
            MediaPath(root_id="source", path=path.name),
            revision=episode.revision,
            synthetic=True,
        )
        assert repeated == episode
        episode = accept_last(service, episode)
    assert episode.accepted_frames == 528
    assert [path.read_bytes() for path in sorted(sources.glob("*.mp4"))] == originals
    assert all(
        service.verify_file(item.media).read_bytes() == originals[index]
        for index, item in enumerate(episode.candidates)
    )


def test_scene_gap_needs_explicit_preparation_and_preserves_original(tmp_path):
    settings, sources, service, episode = media_context(tmp_path)
    path = sources / "scene with gap.mp4"
    make_clip(settings, path, gap=True)
    original = path.read_bytes()
    episode = pending(service, episode)
    importer = FlowMedia(service, settings)
    source = MediaPath(root_id="source", path=path.name)
    with pytest.raises(FlowError, match="frame range"):
        importer.import_result(
            episode.id,
            episode.attempts[-1].id,
            source,
            revision=episode.revision,
            source_kind="scene",
        )
    with pytest.raises(ValueError, match="frame rate|timestamps"):
        importer.import_result(
            episode.id, episode.attempts[-1].id, source, revision=episode.revision
        )
    episode = importer.import_result(
        episode.id,
        episode.attempts[-1].id,
        source,
        revision=episode.revision,
        source_kind="scene",
        source_range=FrameInterval(start_frame=0, end_frame=192),
        prepare_timestamp_gap=True,
        synthetic=True,
    )
    candidate = episode.candidates[-1]
    assert candidate.frame_count == 192 and candidate.original is not None
    assert service.verify_file(candidate.original).read_bytes() == original == path.read_bytes()
    assert candidate.media.sha256 != candidate.original.sha256


def test_interruption_after_asset_copy_reuses_the_bound_source(tmp_path, monkeypatch):
    settings, sources, service, episode = media_context(tmp_path)
    path = sources / "clip.mp4"
    make_clip(settings, path, frames=24)
    episode = pending(service, episode)
    importer = FlowMedia(service, settings)
    original_save = service.save

    def crash(*args, **kwargs):
        raise OSError("interrupted after media registration")

    monkeypatch.setattr(service, "save", crash)
    with pytest.raises(OSError):
        importer.import_result(
            episode.id,
            episode.attempts[-1].id,
            MediaPath(root_id="source", path=path.name),
            revision=episode.revision,
            synthetic=True,
        )
    monkeypatch.setattr(service, "save", original_save)
    episode = importer.import_result(
        episode.id,
        episode.attempts[-1].id,
        MediaPath(root_id="source", path=path.name),
        revision=episode.revision,
        synthetic=True,
    )
    assert len(episode.candidates) == 1
