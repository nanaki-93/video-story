"""One source of pose, prop and continuous-state boundary semantics."""

from ..models.production import ScheduledAction
from ..models.scenes import PropEvent, SceneState


def state_parts(initial, actions, events, scene_id, frame):
    pose, props = initial.body_pose, dict(initial.props)
    changes = [
        (action.end_frame, 0, action.id, action)
        for action in actions
        if action.channel == "body" and action.end_frame <= frame and action.scene_id == scene_id
    ]
    changes.extend(
        (event.frame, 1, event.id, event)
        for event in events
        if isinstance(event, PropEvent) and event.scene_id == scene_id and event.frame <= frame
    )
    for _, _, _, change in sorted(changes):
        if isinstance(change, PropEvent):
            props[change.object_id] = change.location
        else:
            pose = change.end_pose
            props.update(change.resulting_props)
    return pose, props


def scene_state(scene, actions, events, timeline, frame):
    pose, props = state_parts(scene.initial_state, actions, events, scene.id, frame)
    face = next(
        (
            action.action_id
            for action in actions
            if isinstance(action, ScheduledAction)
            and action.scene_id == scene.id
            and action.channel == "face"
            and action.start_frame <= frame < action.end_frame
        ),
        None,
    )
    return SceneState.model_validate(
        {
            **scene.initial_state.model_dump(),
            "body_pose": pose,
            "props": props,
            "facial_overlay": face,
            "travel_distance_px": float(timeline.travel_at(scene.id, frame)),
        }
    )
