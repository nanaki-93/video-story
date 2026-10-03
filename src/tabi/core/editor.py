"""Revision-guarded, semantic authoring commands. No client-owned timeline semantics."""

from fractions import Fraction
from typing import Annotated, Literal

from pydantic import Field

from .authoring import AuthoringService
from .documents import validate_data
from .models import ActionRequest, Curve, Episode
from .models.base import AssetRef, Frame, Identifier, Model, PositiveInt, Text
from .models.episode import Continuity, StoryBeat
from .models.scenes import SceneInstance
from .persistence import RevisionConflict
from .timeline.compiler import ActionCompiler


class TitleEdit(Model):
    kind: Literal["title"]
    title: Text


class SceneEdit(Model):
    kind: Literal["scene"]
    scene: SceneInstance


class AppendScene(Model):
    kind: Literal["append_scene"]
    id: Identifier
    template: AssetRef
    duration_frames: PositiveInt
    purpose: Text
    pack: AssetRef | None = None
    action_id: Identifier | None = None


class MoveCut(Model):
    kind: Literal["move_cut"]
    scene_id: Identifier
    frame: Frame


class MoveAction(Model):
    kind: Literal["move_action"]
    id: Identifier
    start_frame: Frame


class ChangePack(Model):
    kind: Literal["change_pack"]
    scene_id: Identifier
    pack: AssetRef


class PutAction(Model):
    kind: Literal["put_action"]
    action: ActionRequest


class RemoveAction(Model):
    kind: Literal["remove_action"]
    id: Identifier


class PutCurve(Model):
    kind: Literal["put_curve"]
    curve: Curve


class RemoveCurve(Model):
    kind: Literal["remove_curve"]
    scope: Identifier
    target: Identifier


class NotebookEdit(Model):
    kind: Literal["continuity"]
    continuity: Continuity


class BeatsEdit(Model):
    kind: Literal["beats"]
    beats: list[StoryBeat]


class ReplaceEdit(Model):
    kind: Literal["replace"]
    episode: Episode


EditCommand = Annotated[
    TitleEdit
    | SceneEdit
    | AppendScene
    | MoveCut
    | MoveAction
    | ChangePack
    | PutAction
    | RemoveAction
    | PutCurve
    | RemoveCurve
    | NotebookEdit
    | BeatsEdit
    | ReplaceEdit,
    Field(discriminator="kind"),
]


class EditRequest(Model):
    expected_revision: Frame
    command: EditCommand


class EditorService(AuthoringService):
    def lanes(self, episode):
        def span(identity, label, start, end, action_id=None):
            return dict(
                id=identity, label=label, start_frame=start, end_frame=end, action_id=action_id
            )

        lanes = [
            dict(
                id="scenes",
                title="Scenes",
                items=[
                    span(s.id, s.purpose or s.id, s.start_frame, s.end_frame)
                    for s in episode.scenes
                ],
            )
        ]
        audio = []
        for track in episode.tracks:

            def frame(sample):
                return round(Fraction(sample * episode.fps.num, 48000 * episode.fps.den))

            audio.append(
                span(
                    track.id,
                    f"{track.id} · samples {track.start_sample}–"
                    f"{track.start_sample + track.duration_samples}",
                    frame(track.start_sample),
                    frame(track.start_sample + track.duration_samples),
                )
            )
        lanes.append(dict(id="music", title="Music / ambience (frame display)", items=audio))
        for channel in ("body", "face"):
            lanes.append(
                dict(
                    id=channel,
                    title=f"Actions · {channel}",
                    items=[
                        span(a.id, a.action_id, a.start_frame, a.end_frame, a.id)
                        for a in episode.actions
                        if a.channel == channel
                    ],
                )
            )
        objects = []
        for scene in episode.scenes:
            for identity, location in scene.initial_state.props.items():
                objects.append(
                    span(
                        f"{scene.id}-{identity}",
                        f"{identity}: {location}",
                        scene.start_frame,
                        scene.start_frame,
                    )
                )
        for event in [*episode.events, *(e for s in episode.scenes for e in s.events)]:
            if event.type == "prop":
                objects.append(
                    span(event.id, f"{event.object_id}: {event.location}", event.frame, event.frame)
                )
        lanes.append(dict(id="props", title="Persistent objects", items=objects))
        curves = [*episode.curves, *(c for s in episode.scenes for c in s.curves)]
        for label, targets in (("Travel speed", {"travel_speed"}), ("Light / weather", None)):
            items = []
            for curve in curves:
                if (curve.target == "travel_speed") != (targets is not None):
                    continue
                for key in curve.keys:
                    items.append(
                        span(
                            f"{curve.scope}-{curve.target}-{key.frame}",
                            f"{curve.scope}/{curve.target}: {key.value}",
                            key.frame,
                            key.frame,
                        )
                    )
            lanes.append(dict(id="speed" if targets else "effects", title=label, items=items))
        return lanes

    def edit(self, identity, request: EditRequest):
        request = EditRequest.model_validate(request)
        before = self.episode(identity)
        if before.revision != request.expected_revision:
            raise RevisionConflict(
                f"stale revision; current revision is {before.revision}. "
                "Reload before applying edits"
            )
        data = before.model_dump(mode="json")
        command = request.command
        if isinstance(command, TitleEdit):
            data["title"] = command.title
        elif isinstance(command, SceneEdit):
            if command.scene.id not in {s.id for s in before.scenes}:
                raise ValueError("unknown scene; append a new scene explicitly")
            data["scenes"] = [
                command.scene.model_dump(mode="json")
                if s.id == command.scene.id
                else s.model_dump(mode="json")
                for s in before.scenes
            ]
        elif isinstance(command, AppendScene):
            compiled = ActionCompiler(self.assets).compile(before)
            data["duration_frames"] += command.duration_frames
            start, end = before.duration_frames, data["duration_frames"]
            data["scenes"].append(
                {
                    "id": command.id,
                    "template": command.template.model_dump(),
                    "start_frame": start,
                    "end_frame": end,
                    "initial_state": compiled.episode.scenes[-1].final_state.model_dump(),
                    "purpose": command.purpose,
                }
            )
            if command.pack:
                pack = self.store.read(
                    f"registry/actions/{command.pack.id}/{command.pack.version}.json"
                )
                action = next((a for a in pack.actions if a.id == command.action_id), None)
                if action is None:
                    raise ValueError("choose a registered action in this pack")
                data["scenes"][-1]["character_outfit_id"] = pack.outfit_id
                data["actions"].append(
                    ActionRequest(
                        id=f"{command.id}-body",
                        scene_id=command.id,
                        pack=command.pack,
                        action_id=action.id,
                        version=action.version,
                        channel=action.channel,
                        repeat="loop_to_fill" if action.kind == "loop" else "once",
                        start_frame=start,
                        end_frame=end,
                    ).model_dump(mode="json")
                )
        elif isinstance(command, MoveCut):
            index = next((i for i, s in enumerate(before.scenes) if s.id == command.scene_id), -1)
            if index < 1 or before.scenes[index].transition_in.kind != "cut":
                raise ValueError(
                    "choose a cut between two scenes; edit overlaps as a paired transition"
                )
            data["scenes"][index - 1]["end_frame"] = command.frame
            data["scenes"][index]["start_frame"] = command.frame
        elif isinstance(command, MoveAction):
            action = next((a for a in data["actions"] if a["id"] == command.id), None)
            if action is None:
                raise ValueError("unknown action")
            length = action["end_frame"] - action["start_frame"]
            action.update(start_frame=command.start_frame, end_frame=command.start_frame + length)
        elif isinstance(command, ChangePack):
            scene = next((s for s in data["scenes"] if s["id"] == command.scene_id), None)
            if scene is None:
                raise ValueError("unknown scene")
            pack = self.store.read(
                f"registry/actions/{command.pack.id}/{command.pack.version}.json"
            )
            scene["character_outfit_id"] = pack.outfit_id
            actions = {a.id: a for a in pack.actions}
            for request in data["actions"]:
                if request["scene_id"] != command.scene_id:
                    continue
                if request["action_id"] not in actions:
                    raise ValueError(f"replacement pack lacks action {request['action_id']}")
                request.update(
                    pack=command.pack.model_dump(mode="json"),
                    version=actions[request["action_id"]].version,
                )
            for timing in data.get("random_actions", []):
                if timing["scene_id"] == command.scene_id:
                    raise ValueError("edit seeded actions atomically when changing their pack")
        elif isinstance(command, PutAction):
            data["actions"] = [a for a in data["actions"] if a["id"] != command.action.id]
            data["actions"].append(command.action.model_dump(mode="json"))
        elif isinstance(command, RemoveAction):
            data["actions"] = [a for a in data["actions"] if a["id"] != command.id]
        elif isinstance(command, (PutCurve, RemoveCurve)):
            scope, target = (
                (command.curve.scope, command.curve.target)
                if isinstance(command, PutCurve)
                else (command.scope, command.target)
            )
            # Normalize this one authored curve location without duplicating an override.
            data["curves"] = [
                c for c in data["curves"] if (c["scope"], c["target"]) != (scope, target)
            ]
            for scene in data["scenes"]:
                scene["curves"] = [
                    c for c in scene["curves"] if (c["scope"], c["target"]) != (scope, target)
                ]
            if isinstance(command, PutCurve):
                data["curves"].append(command.curve.model_dump(mode="json"))
        elif isinstance(command, NotebookEdit):
            data["continuity"] = command.continuity.model_dump(mode="json")
        elif isinstance(command, BeatsEdit):
            data["beats"] = [b.model_dump(mode="json") for b in command.beats]
        elif isinstance(command, ReplaceEdit):
            if command.episode.id != before.id:
                raise ValueError("replacement cannot change episode identity")
            data = command.episode.model_dump(mode="json")
            data["revision"] = before.revision  # Undo restores content as a new guarded revision.
        candidate = validate_data(data, model=Episode)
        ActionCompiler(self.assets).compile(candidate)
        # The store repeats the revision check after potentially slow semantic/asset validation.
        return self.store.save_draft(candidate, expected_revision=before.revision)
