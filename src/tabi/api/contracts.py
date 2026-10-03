"""Strict transport contracts, separate from portable project documents."""

from typing import Literal

from pydantic import Field

from tabi.core.models import Project
from tabi.core.models.base import SHA256, Document, Frame, Identifier, Model, RelativePath, Text
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
