import hashlib

import pytest

from tabi.core.flow.service import FlowError, FlowService, references_hash, updated
from tabi.core.models.base import Canvas, FrameInterval, HashedFile, MediaPath, content_hash
from tabi.core.models.flow import (
    FlowAttempt,
    FlowBeat,
    FlowCandidate,
    FlowLimits,
    FlowRecipe,
    FlowState,
)
from tabi.core.persistence import ProjectStore, RevisionConflict


def new_service(tmp_path):
    store = ProjectStore.initialize(tmp_path / "東京 project", "Train test")
    service = FlowService(store)
    episode = service.create(
        "Tokyo",
        FlowLimits(
            credit_ceiling=100,
            remaining_allowance=100,
            estimated_credit_per_attempt=5,
            allowance_checked_at="2026-10-06",
        ),
        recipe=FlowRecipe(),
    )
    return service, episode


def add_candidate(service, episode, name="clip1", parent=None):
    path = service.store.root / f"sources/{name}.mp4"
    path.write_bytes(name.encode())  # Storage fixture only; no render or artwork approval.
    media = HashedFile(
        location=MediaPath(path=f"sources/{name}.mp4"),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        size_bytes=path.stat().st_size,
    )
    prompt = "Keep breathing."
    attempt = FlowAttempt(
        schema_version="1.0",
        id=f"attempt-{name}",
        episode_id=episode.id,
        parent_id=parent.id if parent else None,
        parent_sha256=parent.media.sha256 if parent else None,
        recipe_sha256=content_hash(episode.recipe),
        references_sha256=references_hash(episode),
        beat=FlowBeat(id=name, kind="rest", target_frame=0),
        mode="extend" if parent else "image_motion",
        prompt=prompt,
        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
        state="received",
        reserved_credits=5,
    )
    candidate = FlowCandidate(
        id=name,
        attempt_id=attempt.id,
        parent_id=attempt.parent_id,
        parent_sha256=attempt.parent_sha256,
        media=media,
        fps=episode.recipe.fps,
        canvas=Canvas(width=1280, height=720),
        frame_count=192,
        trim=FrameInterval(start_frame=0, end_frame=192),
        technical_ok=True,
    )
    return service.save(
        updated(
            episode,
            attempts=[*episode.attempts, attempt],
            candidates=[*episode.candidates, candidate],
        ),
        expected_revision=episode.revision,
    )


def accept(service, episode, name="clip1"):
    candidate = service.candidate(episode, name)
    return service.review(
        episode.id,
        name,
        revision=episode.revision,
        media_sha256=candidate.media.sha256,
        decision="accepted",
        note="Reviewed storage fixture only.",
        observed_state=FlowState(pose="watching"),
        safe_end_frame=192,
    )


def test_acceptance_survives_reopen_and_clone_resets_reviews(tmp_path):
    service, episode = new_service(tmp_path)
    episode = accept(service, add_candidate(service, episode))
    reopened = FlowService(ProjectStore(service.store.root)).get(episode.id)
    assert reopened == episode
    clone = service.clone(episode.id, "Next train")
    assert not clone.accepted_ids and not clone.attempts and not clone.candidates
    assert clone.recipe == episode.recipe
    assert len(list((service.store.root / "flow/history" / episode.id).glob("*.json"))) == 3


def test_stale_revision_and_changed_source_refuse_acceptance(tmp_path):
    service, episode = new_service(tmp_path)
    episode = add_candidate(service, episode)
    candidate = service.candidate(episode, "clip1")
    with pytest.raises(RevisionConflict):
        service.review(
            episode.id,
            "clip1",
            revision=0,
            media_sha256=candidate.media.sha256,
            decision="accepted",
            note="Fixture",
            observed_state=FlowState(),
        )
    (service.store.root / "sources/clip1.mp4").write_bytes(b"replacement")
    with pytest.raises(FlowError, match="changed"):
        accept(service, episode)
    assert not service.get(episode.id).accepted_ids


def test_backtracking_preserves_old_descendants_but_excludes_progress(tmp_path):
    service, episode = new_service(tmp_path)
    episode = accept(service, add_candidate(service, episode))
    first = service.candidate(episode, "clip1")
    episode = accept(service, add_candidate(service, episode, "clip2", first), "clip2")
    assert episode.accepted_frames == 384
    episode = service.branch_from(episode.id, first.id, episode.revision)
    assert episode.accepted_frames == 192
    assert service.candidate(episode, "clip2").review == "accepted"
    episode = accept(service, add_candidate(service, episode, "replacement", first), "replacement")
    assert episode.accepted_ids == ["clip1", "replacement"]


def test_attempt_prompt_and_history_cannot_be_rewritten(tmp_path):
    service, episode = new_service(tmp_path)
    episode = add_candidate(service, episode)
    with pytest.raises(FlowError, match="erased"):
        service.save(
            updated(episode, attempts=[], candidates=[]), expected_revision=episode.revision
        )
    old = episode.attempts[0]
    attempt = updated(
        old, prompt="Different", prompt_sha256=hashlib.sha256(b"Different").hexdigest()
    )
    with pytest.raises(FlowError, match="immutable"):
        service.save(updated(episode, attempts=[attempt]), expected_revision=episode.revision)


def test_orphan_evidence_after_interruption_is_not_adopted(tmp_path, monkeypatch):
    service, episode = new_service(tmp_path)

    def interrupted(*args, **kwargs):
        raise OSError("simulated interruption before draft rename")

    monkeypatch.setattr(service.store, "save_draft", interrupted)
    with pytest.raises(OSError):
        service.save(updated(episode, paused=True), expected_revision=episode.revision)
    assert not service.get(episode.id).paused
    assert service.get(episode.id).revision == 0
