"""Versioned contracts shared by CLI, storage, future API and schema export."""

from .assets import Action, ActionPack, Asset
from .audio import AudioMixReport, AudioTimelineReport, WaveformReport
from .cache import CacheEntry, CacheInventory, CachePruneReport, StorageEstimate
from .diagnostics import CapabilityReport, RenderSpikeReport
from .episode import ActionRequest, Episode, RandomActionTiming, TrackPlacement
from .fixtures import FixtureManifest
from .preview import PreviewSelection
from .production import CompiledSnapshot, JobEvent, ReleaseRecord, RenderJob, ValidationReport
from .projects import Project
from .publishing import (
    PublicRelease,
    ReleaseBundleReport,
    ReleaseInspection,
    ReleasePreparation,
)
from .registry import AssetHealth, ImportRequest
from .rendering import CompilationResult, ExportVerification, RenderReport
from .scenes import Curve, SceneInstance, SceneTemplate
from .story import StoryboardReport

DOCUMENT_MODELS = {
    "preview_selection": PreviewSelection,
    "project": Project,
    "asset": Asset,
    "action_pack": ActionPack,
    "scene_template": SceneTemplate,
    "episode": Episode,
    "compiled_snapshot": CompiledSnapshot,
    "render_job": RenderJob,
    "job_event": JobEvent,
    "release_record": ReleaseRecord,
    "validation_report": ValidationReport,
    "capability_report": CapabilityReport,
    "render_spike_report": RenderSpikeReport,
    "fixture_manifest": FixtureManifest,
    "asset_health": AssetHealth,
    "render_report": RenderReport,
    "compilation_result": CompilationResult,
    "audio_timeline_report": AudioTimelineReport,
    "waveform_report": WaveformReport,
    "audio_mix_report": AudioMixReport,
    "storyboard_report": StoryboardReport,
    "cache_entry": CacheEntry,
    "cache_inventory": CacheInventory,
    "cache_prune_report": CachePruneReport,
    "storage_estimate": StorageEstimate,
    "export_verification": ExportVerification,
    "release_preparation": ReleasePreparation,
    "public_release": PublicRelease,
    "release_inspection": ReleaseInspection,
    "release_bundle_report": ReleaseBundleReport,
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
