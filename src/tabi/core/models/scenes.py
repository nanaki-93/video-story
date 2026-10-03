"""Template capabilities and typed, global-frame scene inputs."""

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .assets import ApprovableDocument, Channel
from .base import (
    AssetRef,
    Canvas,
    FractionValue,
    Frame,
    FrameInterval,
    Identifier,
    Model,
    Number,
    Point,
    PositiveInt,
    Version,
    unique,
)


class ParameterLimit(Model):
    minimum: Number
    maximum: Number

    @model_validator(mode="after")
    def bounds(self) -> Self:
        if self.minimum > self.maximum:
            raise ValueError("minimum exceeds maximum")
        return self


class CurveKey(Model):
    frame: Frame
    value: Number


class Curve(Model):
    scope: Identifier  # "episode" or a scene ID
    target: Identifier
    unit: Literal["design_px_per_second", "fraction", "degrees", "design_px", "db"]
    interpolation: Literal["constant", "linear"]
    outside: Literal["clamp", "zero"] = "clamp"
    limits: ParameterLimit
    keys: list[CurveKey] = Field(min_length=1)

    @model_validator(mode="after")
    def ordered_keys(self) -> Self:
        frames = [key.frame for key in self.keys]
        if frames != sorted(set(frames)):
            raise ValueError("curve frames must be strictly increasing")
        if any(not self.limits.minimum <= key.value <= self.limits.maximum for key in self.keys):
            raise ValueError("curve value is outside declared limits")
        if self.unit == "fraction" and not (0 <= self.limits.minimum <= self.limits.maximum <= 1):
            raise ValueError("fraction curves must stay within 0..1")
        if self.target == "travel_speed" and self.limits.minimum < 0:
            raise ValueError("reverse travel is unsupported in V1")
        return self


class LayerSlot(Model):
    id: Identifier
    z: Frame
    kind: Literal["still", "tile_strip", "scheduled_sprite", "character", "effect"]
    asset: AssetRef | None = None
    mask: AssetRef | None = None
    anchor: Identifier | None = None
    depth_factor: Annotated[float, Field(ge=0)] = 1.0
    tile_period: PositiveInt | None = None
    opacity: FractionValue = 1.0

    @model_validator(mode="after")
    def slot_requirements(self) -> Self:
        if self.kind == "character" and self.anchor is None:
            raise ValueError("character slot requires a declared anchor")
        if self.kind == "tile_strip" and self.tile_period is None:
            raise ValueError("tile strip requires an explicit pixel period")
        return self


class SceneTemplate(ApprovableDocument):
    document_type: Literal["scene_template"]
    version: Version
    camera_id: Identifier
    design_canvas: Canvas
    fit: Literal["crop", "letterbox"] = "letterbox"
    capabilities: list[Identifier]
    channels: list[Channel]
    anchors: dict[Identifier, Point]
    slots: list[LayerSlot] = Field(min_length=1)
    parameter_limits: dict[Identifier, ParameterLimit] = Field(default_factory=dict)
    mask_semantics: Literal["white_visible_black_hidden"]

    @model_validator(mode="after")
    def template_shape(self) -> Self:
        unique([slot.id for slot in self.slots], "layer IDs")
        z = [slot.z for slot in self.slots]
        if z != sorted(set(z)):
            raise ValueError("layer slots must have strictly increasing z order")
        for slot in self.slots:
            if slot.anchor is not None and slot.anchor not in self.anchors:
                raise ValueError(f"unknown anchor {slot.anchor}")
        for anchor in self.anchors.values():
            if not (
                0 <= anchor.x <= self.design_canvas.width
                and 0 <= anchor.y <= self.design_canvas.height
            ):
                raise ValueError("anchor is outside the design canvas")
        unique(self.capabilities, "capabilities")
        unique(self.channels, "channels")
        return self


class Transition(Model):
    kind: Literal["cut", "overlap"] = "cut"
    overlap_frames: Frame = 0
    character_policy: Literal["cut", "single_visible", "matched"] = "cut"
    match_action: AssetRef | None = None

    @model_validator(mode="after")
    def explicit_overlap(self) -> Self:
        if self.kind == "cut":
            if self.overlap_frames or self.character_policy != "cut" or self.match_action:
                raise ValueError("cuts cannot have overlap metadata")
        else:
            if self.overlap_frames == 0 or self.character_policy == "cut":
                raise ValueError("overlaps require duration and a character visibility policy")
            if (self.character_policy == "matched") != (self.match_action is not None):
                raise ValueError("matched transitions require a matching action reference")
        return self


class SceneState(Model):
    body_pose: Identifier
    facial_overlay: Identifier | None = None
    props: dict[Identifier, Identifier] = Field(default_factory=dict)
    cabin_light: Identifier | None = None
    weather_phase_frame: Frame = 0
    travel_distance_px: Annotated[float, Field(ge=0)] = 0.0


class LandmarkEvent(FrameInterval):
    type: Literal["landmark"]
    id: Identifier
    scene_id: Identifier
    asset: AssetRef
    repeat: bool = Field(default=False, json_schema_extra={"const": False})
    world_x: Number = 0.0

    @model_validator(mode="after")
    def one_shot(self) -> Self:
        if self.repeat:
            raise ValueError("landmarks cannot repeat")
        return self


class PropEvent(Model):
    type: Literal["prop"]
    id: Identifier
    scene_id: Identifier
    frame: Frame
    object_id: Identifier
    location: Identifier


Event = Annotated[LandmarkEvent | PropEvent, Field(discriminator="type")]


class SceneInstance(FrameInterval):
    id: Identifier
    template: AssetRef
    slot_assignments: dict[Identifier, AssetRef] = Field(default_factory=dict)
    anchor: Identifier | None = None
    initial_state: SceneState
    final_state: SceneState | None = None
    continuity: Literal["preserve", "deliberate_reset"] = "preserve"
    transition_in: Transition = Field(default_factory=Transition)
    transition_out: Transition = Field(default_factory=Transition)
    curves: list[Curve] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)

    @model_validator(mode="after")
    def scoped_values(self) -> Self:
        for curve in self.curves:
            if curve.scope != self.id:
                raise ValueError("scene curve scope must match its scene ID")
            if any(not self.start_frame <= key.frame <= self.end_frame for key in curve.keys):
                raise ValueError("scene curve key is outside its interval")
        for event in self.events:
            check_event(event, self)
        return self


def check_event(event: LandmarkEvent | PropEvent, scene: SceneInstance) -> None:
    if event.scene_id != scene.id:
        raise ValueError("event references the wrong scene")
    if isinstance(event, LandmarkEvent):
        if not scene.start_frame <= event.start_frame < event.end_frame <= scene.end_frame:
            raise ValueError("landmark is outside its scene")
    elif not scene.start_frame <= event.frame < scene.end_frame:
        raise ValueError("prop event is outside its scene")
