"""Conservative overlap semantics: no dissolve of incompatible character states."""

from ..models.production import ScheduledAction
from ..models.scenes import PropEvent
from .curves import Timeline, loop_frame
from .state import scene_state


def active_action(actions, scene_id, channel, frame):
    return next(
        (
            action
            for action in actions
            if action.scene_id == scene_id
            and action.channel == channel
            and action.start_frame <= frame < action.end_frame
        ),
        None,
    )


def source_at(action, frame):
    return (
        loop_frame(frame, action.phase_origin_frame, action.loop)
        if action.loop
        else action.source_start_frame + frame - action.start_frame
    )


def character_geometry(scene, template, slot, pack):
    anchor = template.anchors[scene.anchor or slot.anchor]
    return (
        template.design_canvas,
        template.fit,
        template.camera_id,
        pack.canvas,
        anchor.x - pack.anchor.x,
        anchor.y - pack.anchor.y,
        slot.opacity,
        slot.mask,
    )


def validate_transitions(episode, schedule, resolve):
    timeline = Timeline(episode)
    actions = [event for event in schedule if isinstance(event, ScheduledAction)]
    events = [event for event in schedule if isinstance(event, PropEvent)]
    for previous, incoming in zip(episode.scenes, episode.scenes[1:], strict=False):
        transition = incoming.transition_in
        if transition.kind == "cut":
            continue
        left_template = resolve(previous.template, "scene_template")
        right_template = resolve(incoming.template, "scene_template")
        left_slots = [slot for slot in left_template.slots if slot.kind == "character"]
        right_slots = [slot for slot in right_template.slots if slot.kind == "character"]
        if transition.character_policy == "single_visible":
            if len(left_slots) + len(right_slots) > 1:
                raise ValueError(
                    "single_visible overlap permits a character in only one scene; "
                    "use a cut or matched clip"
                )
            continue
        if len(left_slots) != 1 or len(right_slots) != 1:
            raise ValueError("matched overlap needs exactly one character in each scene")
        match = resolve(transition.match_action, "asset")
        if match.kind not in {"sequence", "video"}:
            raise ValueError("matched action must refer to its prepared character clip asset")
        if incoming.continuity != "preserve":
            raise ValueError("matched overlap cannot reset character or prop state; use a cut")
        first, end = incoming.start_frame, previous.end_frame
        boundaries = {first, end}
        for action in actions:
            if action.scene_id in {previous.id, incoming.id}:
                boundaries.update(
                    n for n in (action.start_frame, action.end_frame) if first < n < end
                )
        boundaries.update(
            event.frame
            for event in events
            if event.scene_id in {previous.id, incoming.id} and first < event.frame < end
        )
        boundaries = sorted(boundaries)
        for start, stop in zip(boundaries, boundaries[1:], strict=False):
            left_state = scene_state(previous, actions, events, timeline, start)
            right_state = scene_state(incoming, actions, events, timeline, start)
            if (left_state.body_pose, left_state.props, left_state.facial_overlay) != (
                right_state.body_pose,
                right_state.props,
                right_state.facial_overlay,
            ):
                raise ValueError("matched overlap has divergent pose, facial or prop state")
            for channel in ("body", "face"):
                left = active_action(actions, previous.id, channel, start)
                right = active_action(actions, incoming.id, channel, start)
                if left is None and right is None and channel == "face":
                    continue
                if (
                    left is None
                    or right is None
                    or left.clip != right.clip
                    or left.loop != right.loop
                    or source_at(left, start) != source_at(right, start)
                    or source_at(left, stop - 1) != source_at(right, stop - 1)
                ):
                    raise ValueError(
                        "matched overlap requires identical character/face source frames and phase"
                    )
                if channel == "body" and left.clip != transition.match_action:
                    raise ValueError("matched overlap body differs from the declared prepared clip")
                left_pack, right_pack = (
                    resolve(left.pack, "action_pack"),
                    resolve(right.pack, "action_pack"),
                )
                if character_geometry(
                    previous, left_template, left_slots[0], left_pack
                ) != character_geometry(incoming, right_template, right_slots[0], right_pack):
                    raise ValueError(
                        "matched overlap character placement/camera differs; use a cut"
                    )
