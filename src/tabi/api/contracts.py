"""Strict transport contracts, separate from portable project documents."""

from typing import Literal

from pydantic import Field, field_validator

from tabi.core.models import (
    ActionPack,
    Asset,
    Episode,
    Project,
    ReleaseRecord,
    SceneTemplate,
    ValidationReport,
)
from tabi.core.models.audio import AudioMixReport, AudioTimelineReport
from tabi.core.models.base import (
    SHA256,
    Document,
    Frame,
    Identifier,
    MediaPath,
    Model,
    RelativePath,
    Text,
    Version,
)
from tabi.core.models.cache import CacheInventory, StorageEstimate
from tabi.core.models.portability import BackupManifest
from tabi.core.models.preview import PreviewSelection
from tabi.core.models.production import OutputProfile, RenderJob
from tabi.core.models.publishing import ReleasePreparation
from tabi.core.models.rendering import RenderReport
from tabi.core.models.settings import AppPreferences


class AudioSource(Model):
    asset: Asset
    prepared_samples: Frame


PROTOCOL = "1"


class Bootstrap(Model):
    protocol: Literal["1"]
    secret: str = Field(min_length=32, max_length=256, repr=False)


class WebSession(Document):
    document_type: Literal["web_session"] = "web_session"
    protocol: Literal["1"] = "1"
    session_id: Identifier
    pid: int = Field(gt=0)
    csrf: str = Field(min_length=32, repr=False)
    expires_in: int = Field(ge=0)
    stopping: bool


class WebRoot(Model):
    id: Identifier
    path: Text


class WebRoots(Document):
    document_type: Literal["web_roots"] = "web_roots"
    roots: list[WebRoot]


class FileSelection(Model):
    root_id: Identifier
    path: str = ""
    expected_project_id: Identifier | None = None


class CreateProject(Model):
    root_id: Identifier
    parent: str = ""
    folder: RelativePath
    title: Text


class WebCatalog(Document):
    document_type: Literal["web_catalog"] = "web_catalog"
    assets: list[Asset]
    templates: list[SceneTemplate]
    packs: list[ActionPack]
    episodes: list[Episode]
    releases: list[ReleaseRecord]
    metadata_hashes: dict[str, SHA256]


class TimelineItem(Model):
    id: Text
    label: Text
    start_frame: Frame
    end_frame: Frame
    action_id: Identifier | None = None


class TimelineLane(Model):
    id: Identifier
    title: Text
    items: list[TimelineItem]


class WebEditor(Document):
    document_type: Literal["web_editor"] = "web_editor"
    episode: Episode
    lanes: list[TimelineLane]
    validation: ValidationReport


class WebPreview(Document):
    document_type: Literal["web_preview"] = "web_preview"
    episode: Episode
    snapshot_episode: Episode | None
    selection: PreviewSelection | None
    stale: bool
    issue: Text | None
    job: RenderJob | None
    previous_job: RenderJob | None


class PreviewRequest(Model):
    expected_revision: Frame
    first_frame: Frame
    end_frame: Frame


class FrameRequest(Model):
    snapshot_sha256: SHA256
    frame: Frame


class MarkerRequest(FrameRequest):
    note: Text = Field(max_length=4000)


class WebFrame(Document):
    document_type: Literal["web_frame"] = "web_frame"
    id: Identifier
    report: RenderReport


class WebAudio(Document):
    document_type: Literal["web_audio"] = "web_audio"
    episode: Episode
    timeline: AudioTimelineReport
    sources: list[AudioSource]


class AudioAudition(Model):
    expected_revision: Frame
    first_sample: Frame
    end_sample: Frame


class WebAudioMix(Document):
    document_type: Literal["web_audio_mix"] = "web_audio_mix"
    id: Identifier
    report: AudioMixReport


class MusicMetadata(Model):
    record: ReleaseRecord
    expected_revision: Frame | None = None


class CompileRequest(Model):
    expected_revision: Frame
    purpose: Literal["preview", "production"] = "preview"


class RenderRequest(Model):
    snapshot_sha256: SHA256
    preset: Literal["proxy", "1080p", "4k"]
    encoder: Literal["libx264", "h264_videotoolbox"]
    destination: RelativePath
    first_frame: Frame = 0
    end_frame: Frame | None = None
    max_chunk_frames: int = Field(default=900, ge=1, le=7200)


class WebRenderPlan(Document):
    document_type: Literal["web_render_plan"] = "web_render_plan"
    job: RenderJob
    storage: StorageEstimate


class WebReleases(Document):
    document_type: Literal["web_releases"] = "web_releases"
    preparations: list[ReleasePreparation]


class SaveRelease(Model):
    preparation: ReleasePreparation
    expected_revision: Frame | None = None


class ReleaseReview(Model):
    kind: Literal["creative", "metadata"]
    expected_hash: SHA256
    expected_revision: Frame
    reviewer: Text
    note: Text


class ExportRelease(Model):
    bundle_id: Identifier
    require_ready: bool = False


class BackupTarget(Model):
    root_id: Identifier
    parent: str = ""
    folder: RelativePath

    @field_validator("folder")
    @classmethod
    def single_folder(cls, value):
        if "/" in value:
            raise ValueError("choose one new folder name inside the selected parent")
        return value


class RestoreBackup(BackupTarget):
    source_root_id: Identifier
    source_path: RelativePath


class WebBackup(Document):
    document_type: Literal["web_backup"] = "web_backup"
    root_id: Identifier
    path: RelativePath
    manifest: BackupManifest


class WebSettings(Document):
    document_type: Literal["web_settings"] = "web_settings"
    config_file: Text
    config_sha256: SHA256 | None
    ffmpeg: Text
    ffprobe: Text
    cache_root: Text
    preferences: AppPreferences
    preferences_saved: bool


class WebCache(Document):
    document_type: Literal["web_cache"] = "web_cache"
    inventory: CacheInventory
    budget_bytes: Frame
    proposed_keys: list[SHA256]


class PruneCache(Model):
    expected_inventory: SHA256
    keys: list[SHA256]


class InstallDocument(Model):
    document: dict
    expected_revision: Frame | None = None


class AssetRelink(Model):
    version: Version
    paths: list[MediaPath] = Field(min_length=1)


class Review(Model):
    expected_hash: SHA256
    reviewer: Text
    note: Text


class ProxyVersion(Model):
    version: Version
    max_edge: int = Field(default=640, ge=16, le=4096)


class BeginUpload(Model):
    name: RelativePath
    size_bytes: int = Field(gt=0, le=32 * 1024**3)


class WebUpload(Document):
    document_type: Literal["web_upload"] = "web_upload"
    id: Identifier
    name: RelativePath
    size_bytes: Frame
    received_bytes: Frame
    sha256: SHA256 | None = None
    complete: bool = False


class ImportUploads(Model):
    request: dict
    uploads: list[Identifier] = Field(min_length=1, max_length=10000)


class FileEntry(Model):
    name: Text
    path: RelativePath
    kind: Literal["directory", "file"]
    size_bytes: Frame | None = None


class WebDirectory(Document):
    document_type: Literal["web_directory"] = "web_directory"
    root_id: Identifier
    path: str
    entries: list[FileEntry]
    next_offset: Frame | None = None


class WebProject(Document):
    document_type: Literal["web_project"] = "web_project"
    handle: Identifier
    root_id: Identifier
    path: str
    project: Project


class WebProjects(Document):
    document_type: Literal["web_projects"] = "web_projects"
    projects: list[WebProject]


class RecentProject(Model):
    root_id: Identifier
    root_path: Text
    path: str
    id: Identifier
    title: Text


class WebRecents(Document):
    document_type: Literal["web_recents"] = "web_recents"
    projects: list[RecentProject] = Field(max_length=30)


class WebJobs(Document):
    document_type: Literal["web_jobs"] = "web_jobs"
    jobs: list[RenderJob]


class SubmitJob(Model):
    snapshot_sha256: SHA256
    profile: OutputProfile
    destination: RelativePath
    first_frame: Frame = 0
    end_frame: Frame | None = None
    max_chunk_frames: int | None = Field(default=None, ge=1, le=7200)


class Shutdown(Model):
    mode: Literal["after_job", "cancel"] = "after_job"


class WorkerReady(Model):
    protocol: Literal["1"]
    pid: int = Field(gt=0)
    port: int = Field(ge=1, le=65535)
    session_id: Identifier
    nonce: str = Field(min_length=32, repr=False)
    bootstrap: str = Field(min_length=32, repr=False)
    bearer: str = Field(min_length=32, repr=False)


WEB_SCHEMAS = {
    "web_releases": WebReleases,
    "web_backup": WebBackup,
    "web_render_plan": WebRenderPlan,
    "web_settings": WebSettings,
    "web_cache": WebCache,
    "web_audio": WebAudio,
    "web_audio_mix": WebAudioMix,
    "web_preview": WebPreview,
    "web_frame": WebFrame,
    "web_editor": WebEditor,
    "web_recents": WebRecents,
    "web_catalog": WebCatalog,
    "web_upload": WebUpload,
    "web_session": WebSession,
    "web_roots": WebRoots,
    "web_directory": WebDirectory,
    "web_project": WebProject,
    "web_projects": WebProjects,
    "web_jobs": WebJobs,
}


def schema_documents():
    result = {}
    for name, model in WEB_SCHEMAS.items():
        schema = model.model_json_schema()
        schema.update(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$id": f"urn:tabi:web:1:{name}",
            }
        )
        result[f"{name}.schema.json"] = schema
    return result
