"""Resolve prepared actions into a deterministic, renderer-independent schedule."""

import hashlib
from collections import deque
from pathlib import Path

from ..assets import AssetService
from ..audio.timeline import validate_placement
from ..models import ActionPack, CompiledSnapshot, Episode
from ..models.assets import Action, ApprovableDocument
from ..models.base import AssetRef, ResolvedAssetLock, content_hash
from ..models.episode import ActionRequest
from ..models.production import Fingerprint, ScheduledAction
from ..models.scenes import LandmarkEvent, PropEvent, SceneInstance
from .curves import Timeline, TimelineError, contains, loop_frame
from .effects import validate_effects
from .random import expand_random_actions, prng_fingerprint
from .state import scene_state, state_parts
from .transitions import validate_transitions


class CompileError(TimelineError):
    pass


def compiler_fingerprint() -> Fingerprint:
    sources = sorted(Path(__file__).parent.glob("*.py"))
    sources.append(Path(__file__).parents[1] / "audio" / "timeline.py")
    digest = hashlib.sha256()
    for source in sources:
        digest.update(source.name.encode() + b"\0" + source.read_bytes())
    return Fingerprint(name="tabi-timeline", version="1", sha256=digest.hexdigest())


def require_props(action: Action, props: dict[str, str]) -> None:
    missing = {
        name: location
        for name, location in action.requires_props.items()
        if props.get(name) != location
    }
    if missing:
        raise CompileError(f"{action.id} requires props {missing}; current state is {props}")


def transition_route(pack: ActionPack, start: str, end: str, props: dict[str, str]) -> list[Action]:
    if start == end:
        return []
    queue = deque([(start, dict(props), [])])
    visited = {(start, tuple(sorted(props.items())))}
    transitions = sorted(
        (a for a in pack.actions if a.channel == "body" and a.kind == "one_shot"),
        key=lambda a: a.id,
    )
    while queue:
        pose, state, path = queue.popleft()
        for action in transitions:
            if action.start_pose != pose or any(
                state.get(k) != v for k, v in action.requires_props.items()
            ):
                continue
            next_state = {**state, **action.resulting_props}
            route = [*path, action]
            if action.end_pose == end:
                return route
            key = (action.end_pose, tuple(sorted(next_state.items())))
            if key not in visited:
                visited.add(key)
                queue.append((action.end_pose, next_state, route))
            if len(visited) > 10000:
                raise CompileError("transition graph exceeds 10,000 pose/prop states")
    raise CompileError(f"missing compatible transition {start} → {end} in {pack.id}; props={props}")


class ActionCompiler:
    def __init__(self, assets: AssetService, *, purpose: str = "preview"):
        if purpose not in {"preview", "production", "synthetic_test"}:
            raise CompileError("unknown compilation purpose")
        self.assets, self.purpose = assets, purpose
        self.resolved: dict[tuple[str, str], ApprovableDocument] = {}
        self.action_specs: dict[str, Action] = {}

    def resolve(self, ref: AssetRef, kind: str):
        key = (ref.id, ref.version)
        if key in self.resolved:
            result = self.resolved[key]
            if result.document_type != kind:
                raise CompileError("asset ID collides across registry document types")
            return result
        if any(
            identity == ref.id and version != ref.version for identity, version in self.resolved
        ):
            raise CompileError(f"conflicting versions of {ref.id} in one snapshot")
        if kind == "asset":
            result = self.assets.require_valid(ref, production=self.purpose == "production")
            if self.purpose == "synthetic_test" and result.provenance.origin != "synthetic":
                raise CompileError("synthetic compilation cannot contain unlabelled real media")
        else:
            folder = {"action_pack": "actions", "scene_template": "templates"}[kind]
            result = self.assets.store.read(f"registry/{folder}/{ref.id}/{ref.version}.json")
            if result.document_type != kind or (result.id, result.version) != key:
                raise CompileError("registry identity does not match its requested path")
            if self.purpose == "production" and result.approval.status != "approved":
                raise CompileError(f"{ref.id} needs hash-bound production approval")
        self.resolved[key] = result
        return result

    def pack(self, ref: AssetRef, scene: SceneInstance, episode: Episode) -> ActionPack:
        pack = self.resolve(ref, "action_pack")
        template = self.resolve(scene.template, "scene_template")
        if pack.template != scene.template or pack.camera_id != template.camera_id:
            raise CompileError("action pack camera/template is incompatible with the scene")
        if pack.outfit_id != scene.character_outfit_id:
            raise CompileError(
                "action pack outfit is incompatible with the scene's declared outfit"
            )
        if pack.fps != episode.fps:
            raise CompileError(
                "action pack fps differs from episode; explicitly normalize and review"
            )
        if "body" not in template.channels:
            raise CompileError("scene template does not support body actions")
        for action in pack.actions:
            clip = self.resolve(action.clip, "asset")
            if clip.kind not in {"sequence", "video"}:
                raise CompileError("actions require prepared sequence or video media")
            if clip.probe.canvas != pack.canvas or clip.probe.fps != pack.fps:
                raise CompileError(f"{action.id} clip canvas/fps differs from its pack")
            if (
                clip.probe.frame_count != action.frame_count
                or clip.probe.alpha_mode != pack.alpha_mode
            ):
                raise CompileError(f"{action.id} frame count/alpha differs from its prepared pack")
            if (
                action.channel not in template.channels
                or action.channel not in clip.compatibility.channels
            ):
                raise CompileError(f"{action.id} does not declare its compatible channel")
            if pack.camera_id not in clip.compatibility.cameras:
                raise CompileError(f"{action.id} has no matching camera declaration")
            if (pack.outfit_id is not None or clip.compatibility.outfits) and (
                pack.outfit_id not in clip.compatibility.outfits
            ):
                raise CompileError(f"{action.id} has no matching outfit declaration")
            if clip.compatibility.templates and scene.template not in clip.compatibility.templates:
                raise CompileError(f"{action.id} clip excludes this template version")
            if clip.compatibility.anchor is not None and clip.compatibility.anchor != pack.anchor:
                raise CompileError(f"{action.id} anchor differs from its pack")
            if action.channel == "face" and (
                not action.compatible_body_poses or action.resulting_props
            ):
                raise CompileError("face overlays need compatible body poses and cannot move props")
        return pack

    def _emit(
        self, request: ActionRequest, action: Action, start: int, duration: int, index: int
    ) -> ScheduledAction:
        identifier = "action." + content_hash({"request": request.id, "index": index})[:24]
        event = ScheduledAction(
            type="action",
            id=identifier,
            scene_id=request.scene_id,
            pack=request.pack,
            action_id=action.id,
            clip=action.clip,
            channel=action.channel,
            start_frame=start,
            end_frame=start + duration,
            source_start_frame=action.loop.start_frame if action.loop else 0,
            phase_origin_frame=start,
            loop=action.loop,
            start_pose=action.start_pose,
            end_pose=action.end_pose,
            resulting_props=action.resulting_props,
        )
        self.action_specs[identifier] = action
        return event

    def _body(
        self, request: ActionRequest, pack: ActionPack, pose: str, props: dict[str, str]
    ) -> list[ScheduledAction]:
        selected = next(
            (a for a in pack.actions if a.id == request.action_id and a.version == request.version),
            None,
        )
        if selected is None or selected.channel != request.channel:
            raise CompileError(
                f"unknown or mismatched action {request.action_id}@{request.version}"
            )
        entry = transition_route(pack, pose, selected.start_pose, props)
        state = dict(props)
        for action in entry:
            require_props(action, state)
            state.update(action.resulting_props)
        require_props(selected, state)
        state.update(selected.resulting_props)
        target = request.return_pose
        if target is None:
            target = pose if selected.kind == "loop" else selected.end_pose
        exit_actions = transition_route(pack, selected.end_pose, target, state)
        available = (
            request.end_frame
            - request.start_frame
            - sum(a.frame_count for a in [*entry, *exit_actions])
        )
        if selected.kind == "one_shot":
            if request.repeat != "once" or available != selected.frame_count:
                raise CompileError("one-shot must play exactly once at its authored frame count")
        else:
            period = selected.loop.end_frame - selected.loop.start_frame
            if (
                available <= 0
                or available % period
                or (request.repeat == "once" and available != period)
            ):
                raise CompileError(
                    f"body loop needs whole {period}-frame cycles after entry/exit; "
                    f"available={available}"
                )
        output, cursor = [], request.start_frame
        for index, action in enumerate([*entry, selected, *exit_actions]):
            duration = available if index == len(entry) else action.frame_count
            output.append(self._emit(request, action, cursor, duration, index))
            cursor += duration
        return output

    def compile(self, episode: Episode) -> CompiledSnapshot:
        episode = Episode.model_validate(episode)
        self.resolved.clear()
        self.action_specs.clear()
        timeline = Timeline(episode)
        requests = expand_random_actions(episode)
        events = [*episode.events, *(event for scene in episode.scenes for event in scene.events)]
        schedule, scenes, previous_state = [], [], None
        for scene in episode.scenes:
            template = self.resolve(scene.template, "scene_template")
            for transition in (scene.transition_in, scene.transition_out):
                if transition.match_action:
                    self.resolve(transition.match_action, "asset")
            if scene.anchor is not None and scene.anchor not in template.anchors:
                raise CompileError("unknown scene character anchor")
            slot_ids = {slot.id for slot in template.slots}
            if not set(scene.slot_assignments).issubset(slot_ids):
                raise CompileError("unknown scene slot assignment")
            sprite_slots = {slot.id for slot in template.slots if slot.kind == "scheduled_sprite"}
            for event in events:
                if isinstance(event, LandmarkEvent) and event.scene_id == scene.id:
                    if event.slot_id is None and len(sprite_slots) != 1:
                        raise CompileError(
                            "landmark needs exactly one sprite slot or an explicit slot_id"
                        )
                    if event.slot_id is not None and event.slot_id not in sprite_slots:
                        raise CompileError("landmark references an unknown sprite slot")
            for slot in template.slots:
                for asset_ref in (scene.slot_assignments.get(slot.id, slot.asset), slot.mask):
                    if asset_ref:
                        self.resolve(asset_ref, "asset")
            validate_effects(scene, template, timeline, self.resolve)
            targets = {
                target for scope, target in timeline.curves if scope in {"episode", scene.id}
            }
            for target in targets:
                evaluator = timeline.curve_for(scene.id, target)
                frames = {scene.start_frame, scene.end_frame}
                frames.update(
                    n for n in evaluator.frames if scene.start_frame <= n <= scene.end_frame
                )
                # Sampling both sides also covers a zero-outside or constant jump.
                frames.update(n - 1 for n in tuple(frames) if n > scene.start_frame)
                limit = template.parameter_limits.get(target)
                if limit is None or any(
                    not limit.minimum <= evaluator.value_at(frame) <= limit.maximum
                    for frame in frames
                ):
                    raise CompileError(
                        f"curve {target} exceeds or lacks template capability limits"
                    )
            initial = scene.initial_state
            if scenes and scene.character_outfit_id != scenes[-1].character_outfit_id:
                if scene.continuity != "deliberate_reset" or scene.transition_in.kind != "cut":
                    raise CompileError("outfit changes require a deliberate_reset at a scene cut")
            if scenes:
                previous_state = scene_state(
                    scenes[-1], schedule, events, timeline, scene.start_frame
                )
            if (
                previous_state is not None
                and scene.continuity == "preserve"
                and initial != previous_state
            ):
                raise CompileError(
                    f"scene {scene.id} initial state differs from the previous scene at entry; "
                    "match it or declare a deliberate_reset"
                )
            body_requests = [r for r in requests if r.scene_id == scene.id and r.channel == "body"]
            body, cursor = [], scene.start_frame
            character = any(slot.kind == "character" for slot in template.slots)
            if not character and body_requests:
                raise CompileError("body actions require a character slot")
            for request in body_requests:
                if request.start_frame != cursor:
                    raise CompileError("body actions must cover the scene without gaps")
                pose, props = state_parts(initial, body, events, scene.id, cursor)
                pack = self.pack(request.pack, scene, episode)
                expanded = self._body(request, pack, pose, props)
                # Prop events occurring during transitions are checked at each real start.
                for action_event in expanded:
                    _, props_at_start = state_parts(
                        initial, [*body, *expanded], events, scene.id, action_event.start_frame
                    )
                    require_props(self.action_specs[action_event.id], props_at_start)
                body.extend(expanded)
                cursor = request.end_frame
            if character and cursor != scene.end_frame:
                raise CompileError("body actions must cover the complete character scene")
            face = []
            for request in [r for r in requests if r.scene_id == scene.id and r.channel == "face"]:
                pack = self.pack(request.pack, scene, episode)
                selected = next(
                    (
                        a
                        for a in pack.actions
                        if a.id == request.action_id and a.version == request.version
                    ),
                    None,
                )
                if selected is None or selected.channel != "face":
                    raise CompileError("unknown face action")
                duration = request.end_frame - request.start_frame
                period = (
                    selected.frame_count
                    if selected.loop is None
                    else selected.loop.end_frame - selected.loop.start_frame
                )
                if (
                    (request.repeat == "once" and duration != period)
                    or (selected.kind == "one_shot" and request.repeat != "once")
                    or (duration % period)
                ):
                    raise CompileError(
                        "facial action must use authored whole frames and repeat policy"
                    )
                overlapping = [
                    event
                    for event in body
                    if event.start_frame < request.end_frame
                    and request.start_frame < event.end_frame
                ]
                if not overlapping:
                    raise CompileError("facial action requires a compatible body")
                for body_event in overlapping:
                    spec = self.action_specs[body_event.id]
                    if "face" in spec.occupies_channels or "body" in selected.occupies_channels:
                        raise CompileError("body clip already occupies the face channel")
                    if (
                        body_event.start_pose != body_event.end_pose
                        or body_event.start_pose not in selected.compatible_body_poses
                    ):
                        raise CompileError(
                            "facial overlay is incompatible with the active body pose/transition"
                        )
                _, props = state_parts(initial, body, events, scene.id, request.start_frame)
                require_props(selected, props)
                face.append(self._emit(request, selected, request.start_frame, duration, 0))
            final = scene_state(scene, [*body, *face], events, timeline, scene.end_frame)
            if scene.final_state is not None and scene.final_state != final:
                raise CompileError(
                    f"scene {scene.id} declared final state differs "
                    "from its compiled actions/curves"
                )
            scenes.append(
                SceneInstance.model_validate({**scene.model_dump(), "final_state": final})
            )
            previous_state = final
            schedule.extend([*body, *face])
        for event in events:
            if hasattr(event, "asset"):
                self.resolve(event.asset, "asset")
        for track in episode.tracks:
            asset = self.resolve(track.asset, "asset")
            validate_placement(track, asset)
        # Explicit authored locks can refer to any registry family; resolve them deterministically.
        for lock in episode.asset_locks:
            if (lock.id, lock.version) not in self.resolved:
                raise CompileError(f"authored lock {lock.id} is not referenced by this episode")
        schedule.extend(events)
        schedule.sort(
            key=lambda event: (
                event.frame if isinstance(event, PropEvent) else event.start_frame,
                event.id,
            )
        )
        frozen_episode = Episode.model_validate({**episode.model_dump(), "scenes": scenes})
        validate_transitions(frozen_episode, schedule, self.resolve)
        resolved_locks = [
            ResolvedAssetLock(id=id, version=version, sha256=content_hash(document))
            for (id, version), document in sorted(self.resolved.items())
        ]
        return CompiledSnapshot(
            schema_version="1.0",
            document_type="compiled_snapshot",
            id="snapshot."
            + content_hash(
                {
                    "episode": episode.model_dump(mode="json"),
                    "locks": [lock.model_dump() for lock in resolved_locks],
                }
            )[:24],
            purpose=self.purpose,
            episode=frozen_episode,
            locked_assets=resolved_locks,
            schedule=schedule,
            audio_placements=sorted(
                episode.tracks, key=lambda track: (track.start_sample, track.id)
            ),
            compiler=compiler_fingerprint(),
            prng=prng_fingerprint(),
        )


def state_at(snapshot: CompiledSnapshot, scene_id: str, frame: int) -> dict:
    timeline = Timeline(snapshot.episode)
    if scene_id not in timeline.active_scenes(frame):
        raise CompileError("scene is not active at this frame")
    scene = timeline.scenes[scene_id]
    actions = [
        event
        for event in snapshot.schedule
        if isinstance(event, ScheduledAction) and event.scene_id == scene_id
    ]
    pose, props = state_parts(scene.initial_state, actions, snapshot.schedule, scene_id, frame)
    active = []
    for action in actions:
        if contains(action, frame):
            source = (
                loop_frame(frame, action.phase_origin_frame, action.loop)
                if action.loop
                else action.source_start_frame + frame - action.start_frame
            )
            active.append(
                {
                    "id": action.id,
                    "action_id": action.action_id,
                    "clip": action.clip.model_dump(),
                    "pack": action.pack.model_dump(),
                    "channel": action.channel,
                    "source_frame": source,
                }
            )
    return {
        "frame": frame,
        "scene_id": scene_id,
        "body_pose": pose,
        "props": props,
        "travel_distance_px": float(timeline.travel_at(scene_id, frame)),
        "actions": active,
    }
