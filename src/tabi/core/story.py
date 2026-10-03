"""Inspect compiled story intent and notebook coverage; never claim human review."""

from .models.base import content_hash
from .models.production import ValidationIssue
from .models.story import MusicBoundary, StoryboardReport


def inspect_story(snapshot):
    episode = snapshot.episode
    issues, boundaries = [], []
    for scene in episode.scenes:
        if scene.purpose is None:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="scene_purpose_missing",
                    location=["scenes", scene.id],
                    message="This scene has no authored story purpose.",
                    suggested_fix=(
                        "Describe what develops here and why the transition belongs in the story."
                    ),
                )
            )
        if scene.start_frame and scene.transition_in.note is None:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="transition_purpose_missing",
                    location=["scenes", scene.id, "transition_in"],
                    message="This cut has no authored transition purpose.",
                    suggested_fix="Explain why the cut belongs at this story or musical boundary.",
                )
            )
    for track in episode.tracks:
        if track.role != "music":
            continue
        for kind, sample in [
            ("start", track.start_sample),
            ("end", track.start_sample + track.duration_samples),
        ]:
            purposes = [
                beat.purpose
                for beat in episode.beats
                if track.id in beat.music_placements
                and episode.fps.sample_at(beat.start_frame)
                <= sample
                <= episode.fps.sample_at(beat.end_frame)
            ]
            boundaries.append(
                MusicBoundary(placement_id=track.id, sample=sample, kind=kind, purposes=purposes)
            )
            if not purposes:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="music_boundary_purpose_missing",
                        location=["tracks", track.id, sample],
                        message=(
                            f"Music {kind} at sample {sample} has no linked story-beat purpose."
                        ),
                        suggested_fix=(
                            "Link an authored beat to this musical boundary "
                            "or explain the intentional gap."
                        ),
                    )
                )
    declared = set(episode.continuity.objects)
    observed = {
        obj
        for scene in episode.scenes
        for state in [scene.initial_state, scene.final_state]
        if state is not None
        for obj in state.props
    }
    for obj in sorted(observed - declared):
        issues.append(
            ValidationIssue(
                severity="warning",
                code="notebook_object_missing",
                location=["continuity", obj],
                message=f"Persistent object {obj} is absent from the continuity notebook.",
                suggested_fix="Add the object's identity and intended location to the notebook.",
            )
        )
    return StoryboardReport(
        schema_version="1.0",
        snapshot_sha256=content_hash(snapshot),
        scenes=episode.scenes,
        beats=episode.beats,
        music_boundaries=sorted(
            boundaries, key=lambda item: (item.sample, item.placement_id, item.kind)
        ),
        continuity=episode.continuity,
        issues=issues,
    )
