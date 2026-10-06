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


def failed_attempt(runner, episode):
    episode = runner.prepare(episode.id, episode.revision)
    return runner.transition(
        episode.id,
        episode.attempts[-1].id,
        revision=episode.revision,
        state="failed",
        diagnostic="Confirmed provider failure",
    )


def test_retry_recovery_preserves_accepted_history_parent_and_global_caps(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = accept(service, add_candidate(service, episode))
    parent = episode.candidates[0]
    episode = failed_attempt(runner, failed_attempt(runner, episode))
    assert runner.status(episode)["next_retry_limit"] == 2
    previous = episode
    episode = runner.increase_retry_limit(episode.id, episode.revision)
    assert service.get(episode.id) == episode
    assert episode.accepted_ids == previous.accepted_ids and episode.accepted_frames == 192
    assert episode.attempts == previous.attempts and episode.candidates == previous.candidates
    assert episode.recipe == previous.recipe and episode.references == previous.references
    assert episode.limits == updated(previous.limits, max_retries_per_beat=2)
    assert credited_units(episode) == credited_units(previous)
    assert runner.status(episode)["action"] == "prepare"
    with pytest.raises(FlowError, match="changed"):
        runner.increase_retry_limit(episode.id, previous.revision)
    episode = runner.prepare(episode.id, episode.revision)
    attempt = episode.attempts[-1]
    assert attempt.retry_index == 2
    assert attempt.parent_id == parent.id and attempt.parent_sha256 == parent.media.sha256
    assert episode.accepted_ids == previous.accepted_ids


def test_retry_recovery_stops_at_hard_maximum_and_cannot_bypass_budget(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = failed_attempt(runner, failed_attempt(runner, episode))
    for changes in ({"credit_ceiling": 10}, {"max_attempts": 2}):
        blocked = service.save(
            updated(episode, limits=updated(episode.limits, **changes)),
            expected_revision=episode.revision,
        )
        assert runner.status(blocked)["next_retry_limit"] is None
        with pytest.raises(FlowError, match="not available"):
            runner.increase_retry_limit(blocked.id, blocked.revision)
        episode = service.save(
            updated(blocked, limits=episode.limits), expected_revision=blocked.revision
        )
    for expected_limit in (2, 3):
        episode = runner.increase_retry_limit(episode.id, episode.revision)
        assert episode.limits.max_retries_per_beat == expected_limit
        episode = failed_attempt(runner, episode)
    assert runner.status(episode)["next_retry_limit"] is None
    with pytest.raises(FlowError, match="not available"):
        runner.increase_retry_limit(episode.id, episode.revision)


@pytest.mark.parametrize("state", ["ready", "paused", "awaiting_external", "unknown", "review"])
def test_retry_recovery_refuses_other_workflow_states(tmp_path, state):
    service, episode, runner = context(tmp_path)
    if state == "paused":
        episode = runner.pause(episode.id, episode.revision)
    elif state in {"awaiting_external", "unknown"}:
        episode = runner.prepare(episode.id, episode.revision)
        if state == "unknown":
            episode = runner.transition(
                episode.id,
                episode.attempts[-1].id,
                revision=episode.revision,
                state="unknown",
                diagnostic="No known provider outcome",
            )
    elif state == "review":
        episode = add_candidate(service, episode)
    assert runner.status(episode)["next_retry_limit"] is None
    with pytest.raises(FlowError, match="not available"):
        runner.increase_retry_limit(episode.id, episode.revision)
    assert service.get(episode.id) == episode
