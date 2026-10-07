"""Reusable lo-fi scene recipes; all saved animation times are integer frames."""

from typing import Literal, Self

from pydantic import Field, model_validator

from .assets import ApprovableDocument
from .base import AssetRef, Frame, FrameRate, Identifier, Model, Number, Text, Version, unique
from .scenes import LoopTiming


class SceneryLayer(Model):
    id: Identifier
    asset: AssetRef
    repeat_width: int = Field(gt=0)
    depth: Number = Field(default=1.0, ge=0, le=4)


class OverlayLayer(Model):
    id: Identifier
    asset: AssetRef
    timing: LoopTiming
    mask: AssetRef | None = None
    opacity: Number = Field(default=1.0, ge=0, le=1)


class LofiScene(ApprovableDocument):
    document_type: Literal["lofi_scene"] = "lofi_scene"
    version: Version = "1.0"
    title: Text
    master: AssetRef
    fps: FrameRate = Field(default_factory=lambda: FrameRate(num=30, den=1))
    window_mask: AssetRef | None = None
    scenery: list[SceneryLayer] = Field(default_factory=list, max_length=3)
    speed: Number = Field(default=24.0, ge=0, le=1000)
    overlays: list[OverlayLayer] = Field(default_factory=list, max_length=8)
    notes: str = ""

    @model_validator(mode="after")
    def layer_ids(self) -> Self:
        unique([layer.id for layer in [*self.scenery, *self.overlays]], "lo-fi layer IDs")
        if self.scenery and self.window_mask is None:
            raise ValueError("moving scenery needs a window mask")
        return self


class OverlaySeconds(Model):
    repeat_seconds: Number = Field(gt=0, le=21600)
    delay_seconds: Number = Field(default=0, ge=0, le=21600)


class SaveLofiScene(Model):
    scene: LofiScene
    expected_revision: Frame | None
    # UI convenience. Only the service converts these to the persisted integer frames.
    timing_seconds: dict[Identifier, OverlaySeconds] = Field(default_factory=dict)


class CreateLofiVideo(Model):
    id: Identifier
    title: Text
    scene: AssetRef
    expected_scene_revision: Frame
    # Transport convenience only: the persisted episode always contains integer frames.
    # None explicitly means fit the complete selected music, never repeat it implicitly.
    duration_seconds: int | None = Field(default=90, ge=1, le=21600)
    music: list[AssetRef] = Field(default_factory=list, max_length=100)
