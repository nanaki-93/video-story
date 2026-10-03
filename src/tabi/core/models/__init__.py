"""Versioned contracts shared by CLI, storage, future API and schema export."""

from .assets import Action, ActionPack, Asset
from .episode import ActionRequest, Episode, TrackPlacement
from .production import CompiledSnapshot, ReleaseRecord, RenderJob, ValidationReport
from .projects import Project
from .scenes import Curve, SceneInstance, SceneTemplate

DOCUMENT_MODELS = {
    "project": Project,
    "asset": Asset,
    "action_pack": ActionPack,
    "scene_template": SceneTemplate,
    "episode": Episode,
    "compiled_snapshot": CompiledSnapshot,
    "render_job": RenderJob,
    "release_record": ReleaseRecord,
    "validation_report": ValidationReport,
}

SCHEMA_MODELS = {
    **DOCUMENT_MODELS,
    "action": Action,
    "scene_instance": SceneInstance,
    "track_placement": TrackPlacement,
    "action_request": ActionRequest,
    "curve": Curve,
}

__all__ = [
    "DOCUMENT_MODELS",
    "SCHEMA_MODELS",
    "Action",
    "ActionPack",
    "ActionRequest",
    "Asset",
    "CompiledSnapshot",
    "Curve",
    "Episode",
    "Project",
    "ReleaseRecord",
    "RenderJob",
    "SceneInstance",
    "SceneTemplate",
    "TrackPlacement",
    "ValidationReport",
]
