import hashlib
import json
from pathlib import Path

import pytest
from test_flow_service import new_service

from tabi.core.flow.runner import FlowRunner, credited_units, export_ranges, preview_ranges
from tabi.core.flow.service import FlowError, default_recipe, updated
from tabi.core.flow.shots import current_shot, reference_for, reference_instruction
from tabi.core.models.base import Canvas, FrameInterval, HashedFile, MediaPath
from tabi.core.models.flow import (
    FlowBeat,
    FlowCandidate,
    FlowRecipe,
    FlowReference,
    FlowShot,
    FlowState,
)


def facts(**changes):
    return FlowState.model_validate(
        {
            "cup_kind": "takeaway",
            "cup_position": "table",
            "has_handle": False,
            "has_saucer": False,
            "hands": "resting",
            "pose": "watching",
            **changes,
        }
    )


def context(tmp_path, with_refs=True):
    service, episode = new_service(tmp_path)
    recipe = FlowRecipe(
        target_frames=24,
        shots=[
            FlowShot(
                id=key,
                title=key,
                reference_key=key,
                framing=key,
                duration_frames=12,
                beats=[FlowBeat(id=key, kind="rest", target_frame=0)],
            )
            for key in ("wide", "close")
        ],
    )
    episode = service.save(
        updated(episode, recipe=recipe, limits=updated(episode.limits, estimated_start_credit=10)),
        expected_revision=episode.revision,
    )
    if with_refs:
        for key in ("wide", "close"):
            path = service.store.root / f"sources/{key}.png"
            path.write_bytes(key.encode())  # Storage fixture; never rendered or published.
            reference = FlowReference(
                title=key,
                key=key,
                starting_state=facts(),
                review_note="Unit fixture only",
                synthetic=True,
                media=HashedFile(
                    location=MediaPath(path=f"sources/{key}.png"),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    size_bytes=path.stat().st_size,
                ),
            )
            episode = service.add_reference(episode.id, reference, episode.revision)
    return service, episode, FlowRunner(service)


def receipt(service, episode, frames=8):
    attempt = episode.attempts[-1]
    identity = f"clip-{len(episode.candidates)}"
    path = service.store.root / f"sources/{identity}.mp4"
    path.write_bytes(identity.encode())  # Unit storage fixture; actual media covered separately.
    candidate = FlowCandidate(
        id=identity,
        attempt_id=attempt.id,
        parent_id=attempt.parent_id,
        parent_sha256=attempt.parent_sha256,
        media=HashedFile(
            location=MediaPath(path=f"sources/{identity}.mp4"),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            size_bytes=path.stat().st_size,
        ),
        fps=episode.recipe.fps,
        canvas=Canvas(width=96, height=54),
        frame_count=frames,
        trim=FrameInterval(start_frame=0, end_frame=frames),
        technical_ok=True,
    )
    return service.save(
        updated(
            episode,
            attempts=[*episode.attempts[:-1], updated(attempt, state="received")],
            candidates=[*episode.candidates, candidate],
        ),
        expected_revision=episode.revision,
    )


def review(service, episode, decision="accepted", **values):
    candidate = episode.candidates[-1]
    return service.review(
        episode.id,
        candidate.id,
        revision=episode.revision,
        media_sha256=candidate.media.sha256,
        decision=decision,
        **{
            "note": "Unit fixture only",
            "observed_state": facts() if decision == "accepted" else None,
            **values,
        },
    )


def test_default_plan_is_90_seconds_with_independent_views_and_quiet_actions():
    recipe = default_recipe()
    assert [s.duration_frames for s in recipe.shots] == [180] * 12
    assert sum(s.duration_frames for s in recipe.shots) == 2160
    assert len({s.reference_key for s in recipe.shots}) == 12
    assert len({s.exterior for s in recipe.shots}) == 6
    assert {b.kind for s in recipe.shots for b in s.beats} == {"rest", "look"}
    assert all(s.max_extensions == 0 for s in recipe.shots)
    for first, second in zip(recipe.shots[::2], recipe.shots[1::2], strict=True):
        assert first.exterior == second.exterior
        assert {first.framing, second.framing} == {"wide", "medium"}
    for shot in recipe.shots:
        instruction = reference_instruction(recipe, shot.reference_key)
        assert shot.exterior in instruction and "fixed window frame" in instruction
        assert "not a verified real railway route" in instruction
        assert "independent camera shot" in instruction


def test_independent_shot_uses_fixed_cut_and_never_extends_a_short_source(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = service.save(
        updated(
            episode,
            recipe=updated(
                episode.recipe,
                shots=[updated(s, max_extensions=0) for s in episode.recipe.shots],
            ),
        ),
        expected_revision=episode.revision,
    )
    episode = review(service, receipt(service, runner.prepare(episode.id, episode.revision), 8))
    assert runner.status(episode)["action"] == "needs_attention"
    previous = episode
    with pytest.raises(FlowError, match="extension"):
        runner.prepare(episode.id, episode.revision)
    assert service.get(episode.id) == previous
    episode = runner.restart_shot(episode.id, episode.revision)
    for _ in range(2):
        episode = receipt(service, runner.prepare(episode.id, episode.revision), 16)
        assert episode.attempts[-1].mode == "shot_start"
        assert "selected clip" not in episode.attempts[-1].prompt
        with pytest.raises(FlowError, match="ending at clip frame 12"):
            review(service, episode)
        episode = review(service, episode, safe_end_frame=12)
    assert runner.status(episode)["action"] == "finish"
    assert episode.accepted_frames == 24
    assert all(a.mode == "shot_start" for a in episode.attempts)
    assert all(c.frame_count == 16 and c.trim.end_frame == 12 for c, _, _ in export_ranges(episode))
    assert sum(end - start for _, start, end in export_ranges(episode)) == 24


def test_shot_scenery_survives_retry_continuation_and_only_changes_at_the_cut(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = service.save(
        updated(
            episode,
            recipe=updated(
                episode.recipe,
                shots=[
                    updated(shot, exterior=scenery)
                    for shot, scenery in zip(
                        episode.recipe.shots,
                        ["River and bridge.", "Shopping street."],
                        strict=True,
                    )
                ],
            ),
        ),
        expected_revision=episode.revision,
    )
    episode = runner.prepare(episode.id, episode.revision)
    opening = episode.attempts[-1]
    assert "River and bridge." in opening.prompt and "Shopping street." not in opening.prompt
    assert "breathes subtly" in opening.prompt and "slow visible rise" not in opening.prompt
    episode = review(
        service, receipt(service, episode), "rejected", retry_focus="motion", note="Wrong panorama"
    )
    episode = runner.prepare(episode.id, episode.revision)
    assert episode.attempts[-1].prompt.startswith(opening.prompt)
    assert "scrolling smoothly through the final frame" in episode.attempts[-1].prompt
    episode = review(service, receipt(service, episode))
    episode = runner.prepare(episode.id, episode.revision)
    assert episode.attempts[-1].mode == "extend"
    assert "River and bridge." in episode.attempts[-1].prompt
    assert "Shopping street." not in episode.attempts[-1].prompt
    episode = review(service, receipt(service, episode), safe_end_frame=4)
    episode = runner.prepare(episode.id, episode.revision)
    assert episode.attempts[-1].mode == "shot_start"
    assert "Shopping street." in episode.attempts[-1].prompt
    assert "River and bridge." not in episode.attempts[-1].prompt


def test_changed_window_view_variation_requires_fresh_references(tmp_path):
    service, episode, _ = context(tmp_path)
    changed = service.clone(
        episode.id,
        "River version",
        recipe=updated(
            episode.recipe,
            shots=[
                updated(episode.recipe.shots[0], exterior="River and bridge."),
                episode.recipe.shots[1],
            ],
        ),
    )
    assert [r.key for r in changed.references] == ["close"]
    assert changed.references[0] == episode.references[1] and not changed.attempts
    assert service.get(episode.id) == episode


def test_independent_variation_reuses_the_six_matching_saved_u04_views(tmp_path):
    service, episode = new_service(tmp_path)
    recipe = FlowRecipe.model_validate(
        json.loads(
            (Path(__file__).resolve().parents[1] / "fixtures/flow-u04-recipe.json").read_text()
        )
    )
    episode = service.save(updated(episode, recipe=recipe), expected_revision=episode.revision)
    for shot in recipe.shots:
        data = shot.reference_key.encode()
        path = service.store.root / f"sources/{shot.reference_key}.png"
        path.write_bytes(data)
        episode = service.add_reference(
            episode.id,
            FlowReference(
                title=shot.title,
                key=shot.reference_key,
                starting_state=facts(),
                review_note="Unit fixture only",
                synthetic=True,
                media=HashedFile(
                    location=MediaPath(path=f"sources/{path.name}"),
                    sha256=hashlib.sha256(data).hexdigest(),
                    size_bytes=len(data),
                ),
            ),
            episode.revision,
        )
    clone = service.clone(episode.id, "Independent variation", recipe=default_recipe())
    assert clone.references == episode.references
    assert len(clone.references) == 6 and len(clone.recipe.shots) == 12
    assert FlowRunner(service).status(clone)["action"] == "choose_reference"
    assert not clone.attempts and not clone.accepted_ids
    assert service.get(episode.id) == episode


def test_restart_partial_shot_keeps_earlier_shots_history_and_retry_accounting(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = review(
        service,
        receipt(service, runner.prepare(episode.id, episode.revision), 12),
        safe_end_frame=12,
    )
    first = episode.accepted_ids[:]
    episode = review(service, receipt(service, runner.prepare(episode.id, episode.revision), 4))
    previous = episode
    assert runner.status(episode)["restart_shot_id"] == "close"
    episode = runner.restart_shot(episode.id, episode.revision)
    assert episode.accepted_ids == first and episode.accepted_frames == 12
    assert episode.candidates == previous.candidates and episode.attempts == previous.attempts
    assert episode.references == previous.references and episode.recipe == previous.recipe
    assert episode.limits == previous.limits and credited_units(episode) == credited_units(previous)
    assert runner.status(episode)["restart_shot_id"] is None
    with pytest.raises(FlowError, match="changed"):
        runner.restart_shot(episode.id, previous.revision)
    episode = runner.prepare(episode.id, episode.revision)
    attempt = episode.attempts[-1]
    assert attempt.mode == "shot_start" and attempt.shot_id == "close" and attempt.retry_index == 1
    assert attempt.parent_id == first[-1]
    assert service.get(episode.id) == episode


@pytest.mark.parametrize("state", ["empty", "paused", "awaiting_external", "unknown", "review"])
def test_restart_shot_refuses_unresolved_work_and_empty_shots(tmp_path, state):
    service, episode, runner = context(tmp_path)
    if state != "empty":
        episode = review(service, receipt(service, runner.prepare(episode.id, episode.revision), 4))
    if state == "paused":
        episode = runner.pause(episode.id, episode.revision)
    elif state in {"awaiting_external", "unknown", "review"}:
        episode = runner.prepare(episode.id, episode.revision)
        if state == "unknown":
            episode = runner.transition(
                episode.id,
                episode.attempts[-1].id,
                revision=episode.revision,
                state="unknown",
                diagnostic="Unresolved remote result",
            )
        elif state == "review":
            episode = receipt(service, episode, 4)
    assert runner.status(episode)["restart_shot_id"] is None
    with pytest.raises(FlowError, match="idle partial"):
        runner.restart_shot(episode.id, episode.revision)
    assert service.get(episode.id) == episode


def test_changed_outfit_variation_requires_fresh_references(tmp_path):
    service, episode, _ = context(tmp_path)
    same = service.clone(episode.id, "Same journey")
    assert same.references == episode.references
    changed = service.clone(
        episode.id, "New outfit", recipe=updated(episode.recipe, outfit="Blue coat")
    )
    assert not changed.references and not changed.attempts
    assert service.get(episode.id).references == episode.references


def test_reference_collection_precedes_generation_and_freezes_when_started(tmp_path):
    service, episode, runner = context(tmp_path, with_refs=False)
    assert runner.status(episode)["action"] == "choose_reference"
    assert not episode.attempts
    service, episode, runner = context(tmp_path / "ready")
    episode = runner.prepare(episode.id, episode.revision)
    with pytest.raises(FlowError, match="immutable"):
        service.save(
            updated(episode, references=episode.references[::-1]),
            expected_revision=episode.revision,
        )
    with pytest.raises(FlowError, match="variation"):
        service.add_reference(episode.id, episode.references[0], episode.revision)


def test_exact_shot_cut_starts_fresh_and_accounts_for_different_costs(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = runner.prepare(episode.id, episode.revision)
    assert episode.attempts[-1].mode == "shot_start"
    assert episode.attempts[-1].reserved_credits == 10
    episode = review(service, receipt(service, episode))
    episode = runner.prepare(episode.id, episode.revision)
    assert episode.attempts[-1].mode == "extend"
    assert episode.attempts[-1].reserved_credits == 5
    episode = receipt(service, episode)
    with pytest.raises(FlowError, match="ending at clip frame 4"):
        review(service, episode)
    episode = review(service, episode, safe_end_frame=4)
    assert episode.accepted_frames == 12 and episode.candidates[-1].usable_frames == 4
    predecessor = episode.accepted_ids[-1]
    episode = runner.prepare(episode.id, episode.revision)
    attempt = episode.attempts[-1]
    assert attempt.mode == "shot_start" and attempt.parent_id == predecessor
    assert attempt.shot_id == "close" and "selected clip" not in attempt.prompt
    assert reference_for(episode, current_shot(episode)).key == "close"
    episode = review(service, receipt(service, episode, frames=12))
    assert runner.status(episode)["action"] == "finish"
    assert credited_units(episode) == 25
    assert sum(end - start for _, start, end in export_ranges(episode)) == 24


def test_retry_keeps_clean_reference_and_compiles_only_one_correction(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = runner.prepare(episode.id, episode.revision)
    first = episode.attempts[-1]
    note = "Particles. Mouth changes. This full diagnostic paragraph must remain evidence only."
    episode = review(
        service, receipt(service, episode), "rejected", note=note, retry_focus="particles"
    )
    episode = runner.prepare(episode.id, episode.revision)
    retry = episode.attempts[-1]
    assert retry.mode == first.mode == "shot_start"
    assert retry.references_sha256 == first.references_sha256
    assert retry.retry_reason == note and note not in retry.prompt
    assert "Carriage air stays clear" in retry.prompt and "diagnostic" not in retry.prompt
    assert len(retry.prompt.split()) < 110
    episode = review(service, receipt(service, episode), "rejected", retry_focus="particles")
    assert runner.status(episode)["action"] == "needs_attention"
    assert not episode.accepted_ids


def test_unknown_receipt_survives_reopen_without_another_request(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = runner.prepare(episode.id, episode.revision)
    episode = runner.transition(
        episode.id,
        episode.attempts[-1].id,
        revision=episode.revision,
        state="unknown",
        diagnostic="Checking Flow",
    )
    assert runner.prepare(episode.id, episode.revision) == service.get(episode.id)
    assert len(episode.attempts) == 1 and credited_units(episode) == 10


def test_extension_limit_does_not_loop_or_pad_a_short_shot(tmp_path):
    service, episode, runner = context(tmp_path)
    for _ in range(2):
        episode = runner.prepare(episode.id, episode.revision)
        episode = review(service, receipt(service, episode, frames=4))
    assert episode.accepted_frames == 8
    assert "extension limit" in runner.status(episode)["message"]


def test_new_shot_cost_can_block_before_any_provider_handoff(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = service.save(
        updated(episode, limits=updated(episode.limits, credit_ceiling=9)),
        expected_revision=episode.revision,
    )
    assert runner.status(episode)["action"] == "needs_attention"
    with pytest.raises(FlowError, match="credit limit"):
        runner.prepare(episode.id, episode.revision)
    assert not service.get(episode.id).attempts


def test_camera_cut_cannot_teleport_a_held_cup_back_to_table(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = receipt(service, runner.prepare(episode.id, episode.revision), frames=12)
    with pytest.raises(FlowError, match="cup position"):
        review(service, episode, observed_state=facts(cup_position="held", hands="holding_cup"))


def test_a_short_clip_cannot_skip_unfinished_shot_actions(tmp_path):
    service, episode, runner = context(tmp_path)
    shot = episode.recipe.shots[0]
    shot = updated(
        shot,
        beats=[
            FlowBeat(id="pick", kind="pickup", target_frame=0),
            FlowBeat(id="sip", kind="sip", target_frame=4),
            FlowBeat(id="put-down", kind="return_cup", target_frame=8),
        ],
    )
    episode = service.save(
        updated(episode, recipe=updated(episode.recipe, shots=[shot, episode.recipe.shots[1]])),
        expected_revision=episode.revision,
    )
    episode = receipt(service, runner.prepare(episode.id, episode.revision), frames=12)
    with pytest.raises(FlowError, match="remaining actions"):
        review(service, episode, observed_state=facts(cup_position="held", hands="holding_cup"))


def test_partial_preview_preserves_plan_and_excludes_unaccepted_and_old_branch(tmp_path):
    service, episode, runner = context(tmp_path)
    with pytest.raises(FlowError, match="accepted footage"):
        preview_ranges(updated(episode, paused=True))
    episode = receipt(service, runner.prepare(episode.id, episode.revision), frames=16)
    # Section review has already selected this interval before acceptance.
    episode = service.save(
        updated(
            episode,
            candidates=[
                updated(episode.candidates[0], trim=FrameInterval(start_frame=4, end_frame=16))
            ],
        ),
        expected_revision=episode.revision,
    )
    episode = review(service, episode)
    first = episode.candidates[-1]
    with pytest.raises(FlowError, match="Stop and save"):
        preview_ranges(episode)
    episode = receipt(service, runner.prepare(episode.id, episode.revision), frames=12)
    # Pending and then rejected footage never becomes part of the prefix.
    assert preview_ranges(updated(episode, paused=True)) == [(first, 4, 16)]
    episode = review(service, episode, decision="rejected")
    episode = runner.pause(episode.id, episode.revision)
    before = episode.model_dump_json()
    assert preview_ranges(episode) == [(first, 4, 16)]
    with pytest.raises(FlowError, match="remaining actions"):
        export_ranges(episode)
    assert service.get(episode.id).model_dump_json() == before
    empty = service.branch_from(episode.id, None, episode.revision)
    with pytest.raises(FlowError, match="accepted footage"):
        preview_ranges(updated(empty, paused=True))
    assert len(empty.candidates) == 2


def test_partial_preview_cannot_bypass_action_or_full_video_validation(tmp_path):
    service, episode, runner = context(tmp_path)
    episode = review(service, receipt(service, runner.prepare(episode.id, episode.revision), 12))
    attempt = updated(episode.attempts[0], beat=FlowBeat(id="wide", kind="look", target_frame=0))
    candidate = updated(episode.candidates[0], observed_state=facts(pose="resting"))
    invalid_action = updated(episode, attempts=[attempt], candidates=[candidate], paused=True)
    with pytest.raises(FlowError, match="action is incomplete"):
        preview_ranges(invalid_action)
    episode = review(service, receipt(service, runner.prepare(episode.id, episode.revision), 12))
    with pytest.raises(FlowError, match="shorter than the full plan"):
        preview_ranges(updated(episode, paused=True))
    assert sum(end - start for _, start, end in export_ranges(episode)) == 24
