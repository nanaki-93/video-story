"""Versioned contracts shared by CLI, storage, future API and schema export."""

from .assets import Action, ActionPack, Asset
from .diagnostics import CapabilityReport, RenderSpikeReport
from .episode import ActionRequest, Episode, RandomActionTiming, TrackPlacement
from .fixtures import FixtureManifest
from .production import CompiledSnapshot, ReleaseRecord, RenderJob, ValidationReport
from .projects import Project
from .registry import AssetHealth, ImportRequest
from .rendering import RenderReport
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
    "capability_report": CapabilityReport,
    "render_spike_report": RenderSpikeReport,
    "fixture_manifest": FixtureManifest,
    "asset_health": AssetHealth,
    "render_report": RenderReport,
}

SCHEMA_MODELS = {
    **DOCUMENT_MODELS,
    "action": Action,
    "scene_instance": SceneInstance,
    "track_placement": TrackPlacement,
    "action_request": ActionRequest,
    "curve": Curve,
    "import_request": ImportRequest,
    "random_action_timing": RandomActionTiming,
}

__all__ = [
    "DOCUMENT_MODELS",
    "SCHEMA_MODELS",
    "Action",
    "ActionPack",
    "ActionRequest",
    "Asset",
    "CapabilityReport",
    "CompiledSnapshot",
    "Curve",
    "Episode",
    "FixtureManifest",
    "Project",
    "ReleaseRecord",
    "RenderJob",
    "RenderSpikeReport",
    "SceneInstance",
    "SceneTemplate",
    "TrackPlacement",
    "ValidationReport",
]
