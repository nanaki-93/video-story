"""Focused prompt templates; no model calls or hidden generation parameters."""

import re

from ..models.flow import FlowBeat, FlowCandidate, FlowEpisode, FlowState
from .service import FlowError, updated


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
            f"TABI gently reaches with his existing hand and grips {grip}. "
            "Lift it smoothly to chest height, below his mouth. His hand leaves its resting "
            "position and follows the cup. End holding the cup steadily; do not sip yet."
        )
    if beat.kind in {"sip", "return_cup"} and state.cup_position != "held":
        raise FlowError("This action needs the confirmed cup already held in TABI's hands.")
    if beat.kind == "sip":
        return (
            "From the current held position, TABI brings the same cup to his mouth for one "
            "small sip. Keep a continuous natural grip and the cup rigid. End still holding "
            "the cup comfortably below his mouth. Do not put it down yet."
        )
    if beat.kind == "return_cup":
        return (
            "TABI slowly lowers the held cup and puts it back in its original place on the "
            "table. His existing hand follows it until contact, then relaxes. End with the "
            "cup stationary on the table and both hands resting."
        )
    if beat.kind == "look":
        return (
            "TABI slowly shifts his eyes and makes a small head turn toward the existing "
            "window. His seated body and current hand positions remain stable. End quietly "
            "watching the passing view with visible gentle breathing."
        )
    if beat.kind == "sway":
        if state.hands != "resting":
            raise FlowError("Music sway needs resting hands; finish the cup action first.")
        return (
            "TABI enjoys an imagined relaxed beat with a tiny rhythmic head and shoulder "
            "sway. Keep his body seated and hands resting. End relaxed, breathing naturally."
        )
    if beat.kind == "deep_breath":
        return (
            "TABI takes one clearly visible slow deep breath: his chest and shoulders rise "
            "smoothly, pause comfortably, then settle on a long relaxed exhale. Keep his "
            "current hands and seated body stable. Complete the exhale and return to "
            "quiet breathing."
        )
    if beat.kind == "district":
        if state.district == beat.district:
            raise FlowError("That district is already established; keep its ongoing scenery.")
        return (
            f"As the current {state.district} buildings naturally leave the window, "
            f"a {beat.district}-inspired streetscape gradually enters building by building. "
            "Preserve existing landmarks until they leave view. Keep exposure, sunset, travel "
            "speed and depth consistent. TABI maintains his current pose and gentle breathing."
        )
    return (
        "TABI holds his current relaxed pose, breathes visibly with a smooth rise and fall "
        "of chest and shoulders, and blinks once. Keep hands and objects in their current "
        "positions. Continue quietly through the final frame."
    )


def compile_prompt(
    episode: FlowEpisode,
    beat: FlowBeat,
    parent: FlowCandidate | None,
    *,
    retry_reason: str | None = None,
    override: str | None = None,
) -> tuple[str, str]:
    if parent is None:
        if beat.kind != "rest":
            raise FlowError("Establish a quiet opening before scheduling an action.")
        if episode.recipe.opening_mode == "image_motion":
            if not episode.references:
                raise FlowError("Choose the opening reference image before preparing its prompt.")
            prompt = (
                "Animate the supplied image as one continuous shot. TABI quietly watches the "
                "window, breathing visibly through a small smooth rise and fall of chest and "
                "shoulders, with one relaxed blink. Keep his mouth in its resting expression. "
                "The camera stays fixed relative to the carriage. "
                + episode.recipe.exterior
                + " Keep the pictured objects stationary. End while the view is still moving."
            )
        else:
            recipe = episode.recipe
            prompt = " ".join(
                [
                    recipe.identity,
                    recipe.outfit,
                    recipe.setting,
                    recipe.camera,
                    "Objects: " + "; ".join(recipe.opening_inventory) + ".",
                    recipe.exterior,
                    action_text(FlowState(), beat),
                ]
            )
        mode = episode.recipe.opening_mode
    else:
        if parent.review != "accepted" or parent.observed_state is None:
            raise FlowError("Continue only from a visually accepted parent.")
        state = parent.observed_state
        props = "; ".join(state.inventory) or "only the objects already visible"
        cup = f"Cup: {state.cup_kind}, position: {state.cup_position}."
        if state.has_handle is not None:
            cup += " Existing handle." if state.has_handle else " No handle."
        if state.has_saucer is not None:
            cup += " Existing saucer stays stationary." if state.has_saucer else " No saucer."
        prompt = (
            "Continue directly from the selected parent's final moment as one uninterrupted "
            "shot. Preserve the original referenced TABI identity, connected neck/outfit, "
            "attached gills and exactly two existing arms. Keep camera and interior fixed. "
            f"Confirmed objects: {props}. {cup} Current hands: {state.hands}; "
            f"pose: {state.pose}; outside: {state.district}. "
            "Continue the current exterior positions, direction and speed without reset. "
            "Gentle visible breathing continues. " + action_text(state, beat)
        )
        mode = "extend"
        if override:
            # A small compatibility guard, not a general semantic classifier.
            if (
                not state.has_handle and re.search(r"(?:grip|hold|grab).*handle", override, re.I)
            ) or (
                not state.has_saucer and re.search(r"(?:on|empty|matching).*saucer", override, re.I)
            ):
                raise FlowError("The override requires a handle or saucer not present in the clip.")
            if beat.kind in {"pickup", "sip", "return_cup"} and re.search(
                r"hands? (?:remain|stay|rest).*lap", override, re.I
            ):
                raise FlowError("Moving hands cannot simultaneously stay on the lap.")
    prompt += " Clear cabin air; no floating particles, new objects, cuts, dialogue or music."
    if retry_reason:
        prompt += " Focused correction for this same action: " + retry_reason.strip()
    if override:
        prompt += " Additional instruction for this action: " + override.strip()
    return mode, prompt
