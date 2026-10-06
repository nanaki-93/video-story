"""Small shot plans and reference guidance; no provider or rendering implementation."""

from ..models.flow import FlowBeat, FlowEpisode, FlowRecipe, FlowShot, FlowState


def planned_recipe() -> FlowRecipe:
    views = [
        (
            "sumida",
            "Sumida River and a distant Skytree",
            "wide",
            "rest",
            "A Sumida River-inspired view: broad water with sunset reflections, "
            "a riverside bridge and Tokyo Skytree small in the distant skyline.",
        ),
        (
            "yanaka",
            "Yanaka's old rooftops",
            "medium",
            "look",
            "A Yanaka-inspired view: varied low tiled rooftops, a quiet lane, "
            "small wooden storefronts and trees, with open sky between the buildings.",
        ),
        (
            "akihabara",
            "Akihabara's colorful shopping streets",
            "wide",
            "rest",
            "An Akihabara-inspired view: colorful electronics storefronts and vertical "
            "signboards along a busy shopping street, with different building silhouettes.",
        ),
        (
            "ueno",
            "Ueno's trees and pond",
            "medium",
            "look",
            "A Ueno-inspired park view: leafy trees, pond water catching warm light "
            "and a distant pavilion, with spacious gaps instead of a wall of apartments.",
        ),
        (
            "shinjuku",
            "Shinjuku's evening skyline",
            "wide",
            "rest",
            "A Shinjuku-inspired view: a varied cluster of tall modern towers "
            "catching sunset light above smaller streets and rooftops.",
        ),
        (
            "odaiba",
            "Tokyo Bay and Rainbow Bridge",
            "wide",
            "look",
            "An Odaiba-inspired closing view: broad Tokyo Bay water, Rainbow Bridge "
            "in the middle distance and a low waterfront skyline under the warm evening sky.",
        ),
    ]
    return FlowRecipe(
        shots=[
            FlowShot(
                id=identity,
                title=title,
                framing=framing,
                reference_key=identity,
                exterior=exterior,
                duration_frames=15 * 24,
                max_extensions=1,
                beats=[FlowBeat(id=f"{identity}-{kind}", kind=kind, target_frame=0)],
            )
            for identity, title, framing, kind, exterior in views
        ]
    )


def shot_by_id(episode, identity):
    return next((shot for shot in episode.recipe.shots if shot.id == identity), None)


def frames_in_shot(episode: FlowEpisode, shot: FlowShot) -> int:
    attempts = {item.id: item for item in episode.attempts}
    return sum(
        clip.usable_frames
        for clip in episode.candidates
        if clip.id in episode.accepted_ids and attempts[clip.attempt_id].shot_id == shot.id
    )


def current_shot(episode: FlowEpisode) -> FlowShot | None:
    return next(
        (s for s in episode.recipe.shots if frames_in_shot(episode, s) < s.duration_frames), None
    )


def reference_for(episode, shot):
    return next((r for r in episode.references if r.key == shot.reference_key), None)


def required_references(recipe):
    return list(dict.fromkeys(s.reference_key for s in recipe.shots))


def missing_reference(episode):
    present = {r.key for r in episode.references}
    return next((key for key in required_references(episode.recipe) if key not in present), None)


def remaining_frames(episode):
    shot = current_shot(episode)
    return (
        shot.duration_frames - frames_in_shot(episode, shot)
        if shot
        else episode.recipe.target_frames - episode.accepted_frames
    )


def all_beats(recipe):
    if not recipe.shots:
        return recipe.beats
    result, offset = [], 0
    for shot in recipe.shots:
        result.extend(
            FlowBeat.model_validate({**b.model_dump(), "target_frame": offset + b.target_frame})
            for b in shot.beats
        )
        offset += shot.duration_frames
    return result


def continuity_issue(before: FlowState | None, after: FlowState | None) -> str | None:
    """Compare visible facts only. Different framing may hide hands or the cup."""
    if before is None or after is None:
        return None
    for name in ("cup_kind", "cup_position", "has_handle", "has_saucer", "hands"):
        first, second = getattr(before, name), getattr(after, name)
        if first not in (None, "unknown") and second not in (None, "unknown") and first != second:
            return (
                f"The camera cut changes {name.replace('_', ' ')}. "
                "Match the clean frame and ending."
            )
    return None


def reference_instruction(recipe, key):
    shot = next(s for s in recipe.shots if s.reference_key == key)
    framing = {
        "wide": "A fixed wide view across the aisle, showing TABI, the table and the window.",
        "medium": "A fixed medium view showing the complete head and gills, "
        "torso, both hands and table.",
        "close": "A fixed closer view of the complete head, every gill and connected shoulders, "
        "with window context.",
    }[shot.framing]
    scenery = (
        " Prepare this specific view outside the window: "
        + shot.exterior
        + " Keep a generous visible window area so the location reads clearly. "
        "The exterior stays behind the fixed window frame and table, with a level horizon "
        "and perspective consistent with the carriage. This is an illustrated Tokyo journey "
        "with time passing at district cuts, not a verified real railway route."
        if shot.exterior
        else ""
    )
    return (
        "Use the attached approved train image as the visual source. Prepare one clean starting "
        "image for the same journey. " + framing + " Keep the same character design and markings, "
        "outfit, train layout, cup, book, pen, bag, sunset and side of the window. Carriage air "
        "is clear; highlights remain painted on solid surfaces. The subject rests with a small "
        "closed-mouth smile and the cup on the table. Keep the travel direction consistent. "
        "Preserve the source image; save this as a new reference version." + scenery
    )


def shot_progress(episode):
    result, offset = [], 0
    active = current_shot(episode)
    for index, shot in enumerate(episode.recipe.shots):
        frames = frames_in_shot(episode, shot)
        result.append(
            {
                "id": shot.id,
                "title": shot.title,
                "framing": shot.framing,
                "reference_key": shot.reference_key,
                "index": index + 1,
                "start_frame": offset,
                "duration_frames": shot.duration_frames,
                "accepted_frames": frames,
                "state": "complete"
                if frames == shot.duration_frames
                else "current"
                if active == shot
                else "pending",
            }
        )
        offset += shot.duration_frames
    return result
