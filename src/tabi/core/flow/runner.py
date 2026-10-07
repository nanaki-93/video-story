"""One next action, bounded credits and resumable assisted generation."""

import hashlib
from uuid import uuid4

from ..models.base import content_hash
from ..models.flow import FlowAttempt, FlowBeat, FlowEpisode, FlowState
from .prompts import compile_prompt
from .service import FlowError, references_hash, updated
from .shots import all_beats, current_shot, frames_in_shot, missing_reference


def action_complete(beat: FlowBeat, state: FlowState | None) -> bool:
    if state is None:
        return False
    if beat.kind in {"pickup", "sip"}:
        return state.cup_position == "held" and state.hands == "holding_cup"
    if beat.kind == "return_cup":
        return state.cup_position == "table" and state.hands == "resting"
    if beat.kind == "look":
        return state.pose == "watching"
    if beat.kind == "sway":
        return state.hands == "resting"
    if beat.kind == "district":
        return state.district == beat.district
    return True


def credited_units(episode: FlowEpisode) -> int:
    return sum(
        item.observed_credits if item.observed_credits is not None else item.reserved_credits
        for item in episode.attempts
    )


def completed_beats(episode: FlowEpisode) -> set[str]:
    attempts = {item.id: item for item in episode.attempts}
    active = {item.id: item for item in episode.candidates if item.id in episode.accepted_ids}
    return {
        attempts[item.attempt_id].beat.id
        for item in active.values()
        if action_complete(attempts[item.attempt_id].beat, item.observed_state)
    }


def next_beat(episode: FlowEpisode) -> FlowBeat:
    completed = completed_beats(episode)
    shot = current_shot(episode)
    frames = frames_in_shot(episode, shot) if shot else episode.accepted_frames
    for beat in shot.beats if shot else episode.recipe.beats:
        if beat.id not in completed and beat.target_frame <= frames:
            return beat
    return FlowBeat(id=f"{shot.id if shot else 'rest'}-{frames}", kind="rest", target_frame=frames)


def export_ranges(episode: FlowEpisode) -> list[tuple]:
    """Only an explicitly reviewed final ending may shorten the target-crossing clip."""
    completed = completed_beats(episode)
    if any(beat.id not in completed for beat in all_beats(episode.recipe)):
        raise FlowError("Complete the remaining actions before finishing the video.")
    remaining, result = episode.recipe.target_frames, []
    for identity in episode.accepted_ids:
        candidate = next(item for item in episode.candidates if item.id == identity)
        count = min(remaining, candidate.usable_frames)
        end = candidate.trim.start_frame + count
        if count < candidate.usable_frames and candidate.safe_end_frame != end:
            raise FlowError(
                "The target cuts inside an unreviewed ending; review a quiet cut or retry."
            )
        result.append((candidate, candidate.trim.start_frame, end))
        remaining -= count
        if not remaining:
            return result
    raise FlowError("More accepted footage is needed to reach the target.")


def preview_ranges(episode: FlowEpisode) -> list[tuple]:
    """Preserve an incomplete plan while previewing its reviewed active prefix."""
    if not episode.paused:
        raise FlowError("Stop and save progress before exporting a partial preview.")
    if not 0 < episode.accepted_frames < episode.recipe.target_frames:
        raise FlowError("A partial preview needs accepted footage shorter than the full plan.")
    candidates = {item.id: item for item in episode.candidates}
    attempts = {item.id: item for item in episode.attempts}
    result = []
    for identity in episode.accepted_ids:
        candidate = candidates[identity]
        if not action_complete(attempts[candidate.attempt_id].beat, candidate.observed_state):
            raise FlowError("An accepted action is incomplete; review it before previewing.")
        result.append((candidate, candidate.trim.start_frame, candidate.trim.end_frame))
    return result


class FlowRunner:
    def __init__(self, service):
        self.service = service

    def status(self, episode: FlowEpisode) -> dict:
        parent_id = episode.accepted_ids[-1] if episode.accepted_ids else None
        base = {
            "accepted_frames": episode.accepted_frames,
            "target_frames": episode.recipe.target_frames,
            "credit_units": credited_units(episode),
            "parent_id": parent_id,
            "attempt_id": None,
            "candidate_id": None,
            "beat": None,
            "next_retry_limit": None,
            "restart_shot_id": None,
        }

        def result(action, message, **values):
            if action in {"prepare", "needs_attention"}:
                shot = current_shot(episode)
                if shot and frames_in_shot(episode, shot):
                    values["restart_shot_id"] = shot.id
            return {**base, "action": action, "message": message, **values}

        if episode.paused:
            return result("paused", "Progress is saved. Resume when ready.")
        # Unknown remote outcomes must be reconciled even after changing branches.
        uncertain = next(
            (item for item in reversed(episode.attempts) if item.state in {"submitted", "unknown"}),
            None,
        )
        if uncertain:
            return result(
                "waiting_flow",
                "Reconcile the pending Flow result before another request.",
                attempt_id=uncertain.id,
                beat=uncertain.beat.model_dump(mode="json"),
            )
        for candidate in reversed(episode.candidates):
            if candidate.review == "pending" and candidate.parent_id == parent_id:
                return result(
                    "review",
                    "Watch the clip and its join, then accept or retry.",
                    candidate_id=candidate.id,
                    attempt_id=candidate.attempt_id,
                )
        pending = next(
            (
                item
                for item in reversed(episode.attempts)
                if item.state in {"prepared", "awaiting_external"}
            ),
            None,
        )
        if pending:
            return result(
                "waiting_flow",
                "Use the saved prompt in Flow, then import its native result.",
                attempt_id=pending.id,
                beat=pending.beat.model_dump(mode="json"),
            )
        if episode.accepted_frames >= episode.recipe.target_frames:
            try:
                export_ranges(episode)
            except FlowError as error:
                if all(beat.id in completed_beats(episode) for beat in all_beats(episode.recipe)):
                    return result("needs_attention", str(error))
            else:
                return result(
                    "finish", "The reviewed footage covers the target. Preview and export."
                )
        missing = missing_reference(episode)
        if missing:
            return result(
                "choose_reference", f"Choose and review the clean {missing} starting image."
            )
        if (
            not parent_id
            and episode.recipe.opening_mode == "image_motion"
            and not episode.references
        ):
            return result("choose_reference", "Choose TABI's opening reference image.")
        beat = next_beat(episode)
        shot = current_shot(episode)
        fresh_shot = shot is not None and frames_in_shot(episode, shot) == 0
        if shot and not fresh_shot:
            attempts = {a.id: a for a in episode.attempts}
            extensions = sum(
                attempts[c.attempt_id].mode == "extend"
                for c in episode.candidates
                if c.id in episode.accepted_ids and attempts[c.attempt_id].shot_id == shot.id
            )
            if extensions >= shot.max_extensions:
                return result(
                    "needs_attention",
                    "This shot reached its extension limit. "
                    "Keep the saved footage and review the shot.",
                )
        related = [
            item
            for item in episode.attempts
            if item.parent_id == parent_id and item.beat.id == beat.id
        ]
        next_cost = (
            episode.limits.estimated_start_credit
            if (fresh_shot or parent_id is None)
            and episode.limits.estimated_start_credit is not None
            else episode.limits.estimated_credit_per_attempt
        )
        cost = credited_units(episode) + next_cost
        if len(episode.attempts) >= episode.limits.max_attempts or cost > min(
            episode.limits.credit_ceiling, episode.limits.remaining_allowance
        ):
            return result(
                "needs_attention",
                "The run's attempt or credit limit is reached. Progress is saved.",
            )
        parent = self.service.candidate(episode, parent_id) if parent_id else None
        try:
            compile_prompt(episode, beat, parent)
        except FlowError as error:
            return result("needs_attention", str(error), beat=beat.model_dump(mode="json"))
        if related and len(related) > episode.limits.max_retries_per_beat:
            next_limit = episode.limits.max_retries_per_beat + 1
            return result(
                "needs_attention",
                "Retry limit reached. Review the evidence or return to a clean parent.",
                next_retry_limit=next_limit
                if next_limit <= 3 and len(related) <= next_limit
                else None,
            )
        return result(
            "prepare",
            "Start the next shot from its clean reference."
            if fresh_shot
            else "Prepare the next focused prompt.",
            beat=beat.model_dump(mode="json"),
        )

    def increase_retry_limit(self, episode_id, revision):
        episode = self.service.get(episode_id)
        if revision != episode.revision:
            raise FlowError("Video changed; reload its next action.")
        next_limit = self.status(episode)["next_retry_limit"]
        if next_limit is None:
            raise FlowError("A retry-limit increase is not available for this next action.")
        return self.service.save(
            updated(
                episode,
                limits=updated(episode.limits, max_retries_per_beat=next_limit),
            ),
            expected_revision=revision,
        )

    def restart_shot(self, episode_id, revision):
        episode = self.service.get(episode_id)
        if revision != episode.revision:
            raise FlowError("Video changed; reload its next action.")
        shot_id = self.status(episode)["restart_shot_id"]
        if shot_id is None:
            raise FlowError("Only an idle partial shot can restart from its clean image.")
        attempts = {item.id: item for item in episode.attempts}
        parent_id = None
        for identity in episode.accepted_ids:
            candidate = self.service.candidate(episode, identity)
            if attempts[candidate.attempt_id].shot_id == shot_id:
                break
            parent_id = identity
        return self.service.branch_from(episode.id, parent_id, revision)

    def prepare(self, episode_id, revision):
        episode = self.service.get(episode_id)
        if revision != episode.revision:
            raise FlowError("Video changed; reload its next action.")
        status = self.status(episode)
        if status["action"] == "waiting_flow":
            return episode  # Resume the durable attempt; never submit twice on refresh.
        if status["action"] != "prepare":
            raise FlowError(status["message"])
        parent = (
            self.service.candidate(episode, status["parent_id"]) if status["parent_id"] else None
        )
        if parent:
            self.service.verify_file(parent.media)
        for reference in episode.references:
            self.service.verify_file(reference.media)
        beat = FlowBeat.model_validate(status["beat"])
        previous = [
            item
            for item in episode.attempts
            if item.parent_id == status["parent_id"] and item.beat.id == beat.id
        ]
        reason = None
        focus = None
        if previous:
            candidate = next(
                (item for item in episode.candidates if item.attempt_id == previous[-1].id), None
            )
            reason = candidate.review_note if candidate else previous[-1].diagnostic
            focus = candidate.retry_focus if candidate else None
            reason = reason or "Keep the current action and continuity stable."
        mode, prompt = compile_prompt(episode, beat, parent, retry_reason=reason, retry_focus=focus)
        shot = current_shot(episode)
        cost = (
            episode.limits.estimated_start_credit
            if mode != "extend" and episode.limits.estimated_start_credit is not None
            else episode.limits.estimated_credit_per_attempt
        )
        attempt = FlowAttempt(
            schema_version="1.0",
            id=uuid4().hex,
            episode_id=episode.id,
            parent_id=parent.id if parent else None,
            parent_sha256=parent.media.sha256 if parent else None,
            recipe_sha256=content_hash(episode.recipe),
            references_sha256=references_hash(episode),
            beat=beat,
            shot_id=shot.id if shot else None,
            mode=mode,
            prompt=prompt,
            prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
            state="awaiting_external",
            template_version="2",
            reserved_credits=cost,
            retry_index=len(previous),
            retry_reason=reason,
        )
        return self.service.save(
            updated(episode, attempts=[*episode.attempts, attempt]), expected_revision=revision
        )

    def transition(
        self, episode_id, attempt_id, *, revision, state, diagnostic=None, observed_credits=None
    ):
        episode = self.service.get(episode_id)
        attempt = next((item for item in episode.attempts if item.id == attempt_id), None)
        if attempt is None or attempt.state in {"received", "failed"}:
            raise FlowError("Attempt is missing or already closed.")
        if state not in {"submitted", "unknown", "failed"}:
            raise FlowError("Use a pending, unknown or confirmed failed outcome.")
        attempt = updated(
            attempt, state=state, diagnostic=diagnostic, observed_credits=observed_credits
        )
        return self.service.save(
            updated(
                episode,
                attempts=[attempt if item.id == attempt.id else item for item in episode.attempts],
            ),
            expected_revision=revision,
        )

    def pause(self, episode_id, revision, *, paused=True):
        episode = self.service.get(episode_id)
        return self.service.save(updated(episode, paused=paused), expected_revision=revision)
