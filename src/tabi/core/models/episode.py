"""Authored episode structure; semantic compilation remains T09/T10/T13."""

from typing import Literal, Self

from pydantic import Field, model_validator

from .assets import Channel
from .base import (
    AssetLock,
    AssetRef,
    Canvas,
    DraftDocument,
    Frame,
    FrameInterval,
    FrameRate,
    Identifier,
    Model,
    Number,
    PositiveInt,
    Text,
    Version,
    unique,
)
from .scenes import Curve, Event, LandmarkEvent, SceneInstance, check_event


class TrackPlacement(Model):
    id: Identifier
    asset: AssetRef
    start_sample: Frame
    trim_start_sample: Frame
    trim_end_sample: Frame
    sample_rate: Literal[48000] = 48000
    gain_db: Number = 0.0
    fade_in_samples: Frame = 0
    fade_out_samples: Frame = 0
    role: Literal["music", "ambience"] = "music"
    release_id: Identifier | None = None

    @property
    def duration_samples(self) -> int:
        return self.trim_end_sample - self.trim_start_sample

    @model_validator(mode="after")
    def trims_and_fades(self) -> Self:
        if self.duration_samples <= 0:
            raise ValueError("audio trim must be nonempty")
        if self.fade_in_samples + self.fade_out_samples > self.duration_samples:
            raise ValueError("fades exceed trimmed audio duration")
        return self


class ActionRequest(FrameInterval):
    id: Identifier
    scene_id: Identifier
    pack: AssetRef
    action_id: Identifier
    version: Version
    channel: Channel
    repeat: Literal["once", "loop_to_fill"]
    conflict_behavior: Literal["error"] = "error"


class RandomActionTiming(FrameInterval):
    id: Identifier
    scene_id: Identifier
    pack: AssetRef
    action_id: Identifier
    version: Version
    channel: Channel
    repeat: Literal["once", "loop_to_fill"] = "once"
    duration_frames: PositiveInt
    minimum_gap_frames: PositiveInt
    maximum_gap_frames: PositiveInt

    @model_validator(mode="after")
    def timing_range(self) -> Self:
        if self.maximum_gap_frames < self.minimum_gap_frames:
            raise ValueError("maximum random gap must be at least the minimum")
        if self.duration_frames > self.end_frame - self.start_frame:
            raise ValueError("random action cannot fit in its declared interval")
        return self


class Continuity(Model):
    summary: Text | None = None
    objects: list[Identifier] = Field(default_factory=list)
    previous_episode_id: Identifier | None = None
    notes: list[Text] = Field(default_factory=list)


class Episode(DraftDocument):
    document_type: Literal["episode"]
    title: Text
    format: Literal["story", "session", "track"]
    fps: FrameRate
    canvas: Canvas
    duration_frames: Frame = Field(gt=0)
    seed: Frame
    asset_locks: list[AssetLock] = Field(default_factory=list)
    scenes: list[SceneInstance] = Field(min_length=1)
    tracks: list[TrackPlacement] = Field(default_factory=list)
    actions: list[ActionRequest] = Field(default_factory=list)
    random_actions: list[RandomActionTiming] = Field(default_factory=list)
    curves: list[Curve] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    continuity: Continuity = Field(default_factory=Continuity)
    notes: Text | None = None

    def references(self) -> set[tuple[str, str]]:
        refs = [(lock.id, lock.version) for lock in self.asset_locks]
        for scene in self.scenes:
            refs.append((scene.template.id, scene.template.version))
            refs.extend((ref.id, ref.version) for ref in scene.slot_assignments.values())
            for transition in (scene.transition_in, scene.transition_out):
                if transition.match_action:
                    refs.append((transition.match_action.id, transition.match_action.version))
        refs.extend((track.asset.id, track.asset.version) for track in self.tracks)
        refs.extend((request.pack.id, request.pack.version) for request in self.actions)
        refs.extend((request.pack.id, request.pack.version) for request in self.random_actions)
        for event in [*self.events, *(event for scene in self.scenes for event in scene.events)]:
            if isinstance(event, LandmarkEvent):
                refs.append((event.asset.id, event.asset.version))
        return set(refs)

    @model_validator(mode="after")
    def structure(self) -> Self:
        unique([scene.id for scene in self.scenes], "scene IDs")
        if any(scene.id == "episode" for scene in self.scenes):
            raise ValueError("scene ID 'episode' is reserved for global curve scope")
        unique([a.id for a in self.actions], "action request IDs")
        unique([a.id for a in self.random_actions], "random timing IDs")
        unique([t.id for t in self.tracks], "track placement IDs")
        unique([lock.id for lock in self.asset_locks], "asset lock IDs")
        if self.scenes[0].start_frame != 0 or self.scenes[-1].end_frame != self.duration_frames:
            raise ValueError("scenes must cover the complete episode interval")
        if (
            self.scenes[0].transition_in.kind != "cut"
            or self.scenes[-1].transition_out.kind != "cut"
        ):
            raise ValueError("episode boundaries must use cuts")
        for index, scene in enumerate(self.scenes):
            if scene.end_frame > self.duration_frames:
                raise ValueError("scene extends past episode end")
            if index:
                previous = self.scenes[index - 1]
                overlap = previous.end_frame - scene.start_frame
                if (
                    scene.start_frame <= previous.start_frame
                    or scene.end_frame <= previous.end_frame
                ):
                    raise ValueError("scenes must be ordered without containment")
                if overlap < 0:
                    raise ValueError("uncovered gap between scenes")
                if overlap == 0:
                    if previous.transition_out.kind != "cut" or scene.transition_in.kind != "cut":
                        raise ValueError("non-overlapping scenes require cuts")
                elif (
                    previous.transition_out != scene.transition_in
                    or scene.transition_in.kind != "overlap"
                    or scene.transition_in.overlap_frames != overlap
                ):
                    raise ValueError("scene overlap must match both explicit transition contracts")
                if index > 1 and scene.start_frame < self.scenes[index - 2].end_frame:
                    raise ValueError("three-way scene overlaps are unsupported")
        scenes = {scene.id: scene for scene in self.scenes}
        for curve in self.curves:
            if curve.scope == "episode":
                start, end = 0, self.duration_frames
            elif curve.scope in scenes:
                start, end = scenes[curve.scope].start_frame, scenes[curve.scope].end_frame
            else:
                raise ValueError("curve refers to an unknown scene scope")
            if any(not start <= key.frame <= end for key in curve.keys):
                raise ValueError("curve key is outside its scope")
        all_events = [*self.events, *(event for scene in self.scenes for event in scene.events)]
        unique([event.id for event in all_events], "event IDs")
        for event in all_events:
            if event.scene_id not in scenes:
                raise ValueError("event refers to an unknown scene")
            check_event(event, scenes[event.scene_id])
        channels: dict[tuple[str, str], list[ActionRequest]] = {}
        for timing in self.random_actions:
            scene = scenes.get(timing.scene_id)
            if scene is None or not (
                scene.start_frame <= timing.start_frame < timing.end_frame <= scene.end_frame
            ):
                raise ValueError("random timing is outside its scene")
        for action in self.actions:
            scene = scenes.get(action.scene_id)
            if (
                scene is None
                or not scene.start_frame <= action.start_frame < action.end_frame <= scene.end_frame
            ):
                raise ValueError("action is outside its scene")
            channels.setdefault((action.scene_id, action.channel), []).append(action)
        for actions in channels.values():
            actions.sort(key=lambda a: a.start_frame)
            if any(a.end_frame > b.start_frame for a, b in zip(actions, actions[1:], strict=False)):
                raise ValueError("overlapping actions on an exclusive channel")
        audio_end = self.fps.sample_at(self.duration_frames)
        if any(track.start_sample + track.duration_samples > audio_end for track in self.tracks):
            raise ValueError("audio placement exceeds the episode sample boundary")
        return self
