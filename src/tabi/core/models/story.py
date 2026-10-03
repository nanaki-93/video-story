"""Reviewable storyboard and sample-boundary intent, without creative certification."""

from typing import Literal

from .base import SHA256, Document, Frame, Identifier, Model, Text
from .episode import Continuity, StoryBeat
from .production import ValidationIssue
from .scenes import SceneInstance


class MusicBoundary(Model):
    placement_id: Identifier
    sample: Frame
    kind: Literal["start", "end"]
    purposes: list[Text]


class StoryboardReport(Document):
    document_type: Literal["storyboard_report"] = "storyboard_report"
    snapshot_sha256: SHA256
    scenes: list[SceneInstance]
    beats: list[StoryBeat]
    music_boundaries: list[MusicBoundary]
    continuity: Continuity
    issues: list[ValidationIssue]
