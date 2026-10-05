import hashlib

import pytest
from test_flow_contracts import episode_data
from test_flow_service import accept, add_candidate, new_service

from tabi.core.flow.runner import FlowRunner, credited_units, export_ranges
from tabi.core.flow.service import FlowError, updated
from tabi.core.models.base import HashedFile, MediaPath
from tabi.core.models.flow import FlowCandidate, FlowRecipe


def context(tmp_path, target=2160):
    service, episode = new_service(tmp_path)
    episode = service.save(
        updated(episode, recipe=FlowRecipe(opening_mode="text_reference", target_frames=target)),
        expected_revision=episode.revision,
    )
    return service, episode, FlowRunner(service)


def test_refresh_and_unknown_submission_reuse_the_saved_attempt(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = runner.prepare(episode.id, episode.revision)
    assert runner.prepare(episode.id, episode.revision) == episode
    attempt = episode.attempts[-1]
    episode = runner.transition(
        episode.id,
        attempt.id,
        revision=episode.revision,
        state="unknown",
        diagnostic="Browser disconnected after submission",
    )
    assert runner.status(episode)["action"] == "waiting_flow"
    assert runner.prepare(episode.id, episode.revision) == episode
    assert len(episode.attempts) == 1 and credited_units(episode) == 5
    assert service.get(episode.id) == episode


def test_refund_is_explicit_and_retry_is_bounded(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = runner.prepare(episode.id, episode.revision)
    episode = runner.transition(
        episode.id,
        episode.attempts[-1].id,
        revision=episode.revision,
        state="failed",
        diagnostic="Confirmed provider failure",
        observed_credits=0,
    )
    assert credited_units(episode) == 0
    episode = runner.prepare(episode.id, episode.revision)
    assert episode.attempts[-1].retry_index == 1
    episode = runner.transition(
        episode.id,
        episode.attempts[-1].id,
        revision=episode.revision,
        state="failed",
        diagnostic="Failed again",
    )
    assert runner.status(episode)["action"] == "needs_attention"
    assert credited_units(episode) == 5


def test_credit_ceiling_blocks_a_new_attempt_and_pause_is_durable(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = service.save(
        updated(episode, limits=updated(episode.limits, credit_ceiling=4)),
        expected_revision=episode.revision,
    )
    assert runner.status(episode)["action"] == "needs_attention"
    with pytest.raises(FlowError, match="credit limit"):
        runner.prepare(episode.id, episode.revision)
    episode = runner.pause(episode.id, episode.revision)
    assert runner.status(service.get(episode.id))["action"] == "paused"


def test_target_crossing_requires_the_exact_reviewed_cut(tmp_path):
    service, episode, runner = context(tmp_path, target=180)
    episode = accept(service, add_candidate(service, episode))
    assert runner.status(episode)["action"] == "needs_attention"
    candidate = updated(episode.candidates[0], safe_end_frame=180)
    episode = service.save(
        updated(episode, candidates=[candidate]), expected_revision=episode.revision
    )
    assert runner.status(episode)["action"] == "finish"
    assert export_ranges(episode)[0][2] == 180


def test_old_descendants_and_unfinished_actions_do_not_complete_progress(tmp_path):
    service, episode, runner = context(tmp_path, target=192)
    episode = accept(service, add_candidate(service, episode))
    episode = service.branch_from(episode.id, None, episode.revision)
    assert runner.status(episode)["accepted_frames"] == 0
    assert runner.status(episode)["action"] == "prepare"


def test_late_result_closes_unknown_attempt_without_another_reservation(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = runner.prepare(episode.id, episode.revision)
    attempt = episode.attempts[0]
    episode = runner.transition(
        episode.id,
        attempt.id,
        revision=episode.revision,
        state="unknown",
        diagnostic="Connection lost",
    )
    path = service.store.root / "sources/late.mp4"
    path.write_bytes(b"unit storage fixture only")
    media = HashedFile(
        location=MediaPath(path="sources/late.mp4"),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        size_bytes=path.stat().st_size,
    )
    candidate = FlowCandidate.model_validate(episode_data()["candidates"][0])
    candidate = updated(
        candidate,
        attempt_id=attempt.id,
        media=media,
        review="pending",
        reviewed_sha256=None,
        review_note=None,
        observed_state=None,
    )
    episode = service.save(
        updated(
            episode,
            attempts=[updated(episode.attempts[0], state="received")],
            candidates=[candidate],
        ),
        expected_revision=episode.revision,
    )
    assert runner.status(episode)["action"] == "review"
    episode = accept(service, episode)
    assert episode.accepted_frames == 192
    assert len(episode.attempts) == 1 and credited_units(episode) == 5
