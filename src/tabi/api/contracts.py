"""Strict transport contracts, separate from portable project documents."""

from typing import Literal

from pydantic import Field

from tabi.core.models import ActionPack, Asset, Episode, Project, ReleaseRecord, SceneTemplate
from tabi.core.models.assets import Compatibility, Provenance
from tabi.core.models.base import (
    SHA256,
    AssetRef,
    Document,
    Frame,
    Identifier,
    MediaPath,
    Model,
    RelativePath,
    Text,
    Version,
)
from tabi.core.models.production import OutputProfile, RenderJob

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


class InstallDocument(Model):
    document: dict
    expected_revision: Frame | None = None


class StillTemplate(Model):
    asset: AssetRef
    id: Identifier
    version: Version = "1.0"
    camera_id: Identifier = "still"


class AssetRevision(Model):
    version: Version
    provenance: Provenance
    compatibility: Compatibility


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
