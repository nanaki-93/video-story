"""Explicit local workflow execution policy and durable generation receipts."""

import ipaddress
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import AfterValidator, Field, model_validator

from .base import (
    SHA256,
    AssetRef,
    Document,
    DraftDocument,
    Frame,
    HashedFile,
    Identifier,
    Model,
    RelativePath,
    Text,
    Version,
    relative_path,
    unique,
)


def loopback_endpoint(value):
    url = urlsplit(value)
    try:
        local = ipaddress.ip_address(url.hostname or "").is_loopback
    except ValueError:
        local = False
    if (
        url.scheme != "http"
        or not local
        or url.port is None
        or url.username
        or url.password
        or url.path not in {"", "/"}
        or url.query
        or url.fragment
    ):
        raise ValueError("use an explicit HTTP loopback IP and port, without credentials or a path")
    return value.rstrip("/")


Endpoint = Annotated[str, AfterValidator(loopback_endpoint)]


class GenerationPolicy(Model):
    enabled: bool = False
    endpoint: Endpoint = "http://127.0.0.1:8188"
    allowed_workflow_hashes: list[SHA256] = Field(default_factory=list, max_length=100)
    max_output_bytes: int = Field(default=64 * 1024**2, ge=1024, le=256 * 1024**2)


class ModelBinding(Model):
    node_id: Identifier
    input_name: Identifier
    server_name: RelativePath
    file: HashedFile


class ComfyWorkflow(DraftDocument):
    document_type: Literal["comfy_workflow"] = "comfy_workflow"
    version: Version
    description: Text
    workflow: HashedFile
    models: list[ModelBinding] = Field(min_length=1, max_length=32)
    node_definitions: dict[Text, SHA256] = Field(min_length=1, max_length=64)
    output_nodes: list[Identifier] = Field(min_length=1, max_length=16)
    seed: Frame | None = None
    synthetic_fixture: bool = False

    @model_validator(mode="after")
    def unique_bindings(self) -> Self:
        unique([(m.node_id, m.input_name) for m in self.models], "model bindings")
        unique(self.output_nodes, "output nodes")
        for model in self.models:
            if model.file.location.path.split("/")[-1] != model.server_name.split("/")[-1]:
                raise ValueError("model file basename must match its configured server name")
        return self


class GenerationOutput(Model):
    node_id: Identifier
    filename: RelativePath
    subfolder: str = ""
    type: Literal["output"] = "output"

    @model_validator(mode="after")
    def safe_source(self) -> Self:
        if "/" in self.filename:
            raise ValueError("output filename must be a basename")
        if self.subfolder:
            relative_path(self.subfolder)
        if not self.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            raise ValueError("generation imports support PNG, JPEG and WebP stills only")
        return self


class GenerationRun(DraftDocument):
    document_type: Literal["generation_run"] = "generation_run"
    endpoint: Endpoint
    prompt_id: Identifier
    manifest: ComfyWorkflow
    manifest_sha256: SHA256
    state: Literal["submitting", "unknown", "queued", "running", "succeeded", "failed", "imported"]
    queue_position: Frame | None = None
    error: Text | None = None
    outputs: list[GenerationOutput] = Field(default_factory=list, max_length=16)
    downloads: list[HashedFile] = Field(default_factory=list, max_length=16)
    imported_assets: list[AssetRef] = Field(default_factory=list, max_length=16)


class GenerationStatus(Document):
    document_type: Literal["generation_status"] = "generation_status"
    policy: GenerationPolicy
    availability: Literal["unchecked", "disabled", "online", "offline"] = "unchecked"
    message: str = ""
    workflows: list[ComfyWorkflow] = Field(default_factory=list)
    workflow_hashes: dict[str, SHA256] = Field(default_factory=dict)
    runs: list[GenerationRun] = Field(default_factory=list)
