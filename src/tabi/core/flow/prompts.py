"""Motion-first prompts; appearance and defect history stay in reference/review records."""

import re

from ..models.flow import FlowBeat, FlowCandidate, FlowEpisode, FlowState
from .service import FlowError, updated
from .shots import continuity_issue, current_shot, frames_in_shot, reference_for


def expected_ending(state: FlowState, beat: FlowBeat) -> FlowState:
    if beat.kind == "pickup":
        return updated(state, cup_position="held", hands="holding_cup")
    if beat.kind == "sip":
        return updated(state, pose="sipping")
    if beat.kind == "return_cup":
        return updated(state, cup_position="table", hands="resting", pose="resting")
    if beat.kind == "look":
        return updated(state, pose="watching")
    if beat.kind == "district":
        return updated(state, district=beat.district)
    return state


def action_text(state: FlowState, beat: FlowBeat) -> str:
    if beat.kind == "pickup":
        if state.cup_kind not in {"takeaway", "ceramic"} or (
            state.cup_position != "table" or state.hands != "resting"
        ):
            raise FlowError("Pickup needs a confirmed cup on the table and resting hands.")
        grip = "its existing handle" if state.has_handle else "the body of that same cup"
        return (
            f"The character gently grips {grip} and lifts it to chest height. "
            "The existing hand follows the cup. End holding it steadily below the mouth."
        )
    if beat.kind in {"sip", "return_cup"} and state.cup_position != "held":
        raise FlowError(
            "This action needs the confirmed cup already held in the character's hands."
        )
    if beat.kind == "sip":
        return (
            "The character brings the held cup to the mouth for one small sip, maintaining a "
            "continuous grip and rigid cup shape. End still holding the cup below the mouth."
        )
    if beat.kind == "return_cup":
        return (
            "The character lowers the held cup to its original place on the table. The hand "
            "follows it until contact, then relaxes. End with the cup on the table "
            "and hands resting."
        )
    if beat.kind == "look":
        return (
            "The character slowly shifts the eyes and turns the head slightly toward the window. "
            "End quietly watching the view, breathing gently, with hands in their current position."
        )
    if beat.kind == "sway":
        if state.hands not in {"resting", "unknown"}:
            raise FlowError("Music sway needs resting hands; finish the cup action first.")
        return (
            "The character makes a tiny rhythmic head and shoulder sway while seated. "
            "Hands rest in place. End relaxed with gentle breathing and the same closed smile."
        )
    if beat.kind == "deep_breath":
        return (
            "The character takes one slow deep breath: chest and shoulders rise, pause, then "
            "settle on a long relaxed exhale. The mouth keeps its closed smile. Complete the "
            "exhale and return to quiet breathing."
        )
    if beat.kind == "district":
        if state.district == beat.district:
            raise FlowError("That district is already established; keep its ongoing scenery.")
        return (
            f"A {beat.district}-inspired streetscape gradually enters building by building as "
            "the existing view leaves the window. Keep speed and sunset steady. "
            "The character stays relaxed and breathes gently."
        )
    return (
        "The character breathes with a slow visible rise and fall of chest and shoulders, "
        "and blinks once. The mouth holds its resting smile. Hands and table objects stay in place."
    )


CORRECTIONS = {
    "particles": "Carriage air stays clear, with stable painted highlights on solid surfaces.",
    "mouth": "The mouth holds the same small closed smile throughout the movement.",
    "identity": "The gills stay attached and the neck stays connected to the outfit.",
    "props": "Only the object involved in this action moves; its shape stays rigid.",
    "motion": "The exterior keeps scrolling smoothly through the final frame.",
    "action": "Complete this single action and settle comfortably before the shot ends.",
}


def correction_text(focus, reason, beat):
    if focus is None:
        # Older rejection notes have no selected focus. Do not send their paragraphs to Flow.
        text = (reason or "").lower()
        focus = next(
            (
                key
                for key, words in [
                    ("particles", ("dot", "particle", "fleck")),
                    ("mouth", ("mouth",)),
                    ("identity", ("gill", "ear", "neck", "identity")),
                    ("props", ("cup", "object", "hand")),
                    ("motion", ("freeze", "motion", "scenery")),
                ]
                if any(word in text for word in words)
            ),
            "action",
        )
    if focus == "mouth" and beat.kind == "sip":
        return (
            "During the sip, the lips meet the rim naturally and return to the same resting "
            "shape as the cup lowers."
        )
    return CORRECTIONS[focus]


def compile_prompt(
    episode: FlowEpisode,
    beat: FlowBeat,
    parent: FlowCandidate | None,
    *,
    retry_reason: str | None = None,
    retry_focus: str | None = None,
    override: str | None = None,
) -> tuple[str, str]:
    shot = current_shot(episode)
    fresh_shot = shot is not None and frames_in_shot(episode, shot) == 0
    if parent is not None and (parent.review != "accepted" or parent.observed_state is None):
        raise FlowError("Continue only from a visually accepted parent.")
    if fresh_shot:
        reference = reference_for(episode, shot)
        if reference is None:
            raise FlowError("Choose the clean starting reference image for this shot.")
        state = reference.starting_state
        issue = continuity_issue(parent.observed_state if parent else None, state)
        if issue:
            raise FlowError(issue)
        mode, opening = "shot_start", "Animate the supplied clean starting image."
    elif parent is not None:
        state = parent.observed_state
        mode, opening = "extend", "Continue the selected clip's current movement."
    else:
        if beat.kind != "rest":
            raise FlowError("Establish a quiet opening before scheduling an action.")
        state = FlowState()
        mode = episode.recipe.opening_mode
        if mode == "image_motion":
            if not episode.references:
                raise FlowError("Choose the opening reference image before preparing its prompt.")
            opening = "Animate the supplied image."
        else:
            recipe = episode.recipe
            opening = " ".join(
                [
                    recipe.identity,
                    recipe.outfit,
                    recipe.setting,
                    recipe.camera,
                    "Objects: " + "; ".join(recipe.opening_inventory) + ".",
                ]
            )
    prompt = " ".join(
        [
            opening,
            action_text(state, beat),
            "The camera stays fixed.",
            episode.recipe.exterior,
            "The outside view keeps moving through the final frame.",
        ]
    )
    if retry_reason or retry_focus:
        prompt += " " + correction_text(retry_focus, retry_reason, beat)
    if override:
        if (not state.has_handle and re.search(r"(?:grip|hold|grab).*handle", override, re.I)) or (
            not state.has_saucer and re.search(r"(?:on|empty|matching).*saucer", override, re.I)
        ):
            raise FlowError("The override requires a handle or saucer not present in the clip.")
        if beat.kind in {"pickup", "sip", "return_cup"} and re.search(
            r"hands? (?:remain|stay|rest).*lap", override, re.I
        ):
            raise FlowError("Moving hands cannot simultaneously stay on the lap.")
        prompt += " " + override.strip()
    return mode, prompt
