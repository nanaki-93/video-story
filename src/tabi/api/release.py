"""Factual release preparation and bounded private project portability."""

import mimetypes

from fastapi import APIRouter, HTTPException, Request
from pydantic import TypeAdapter

from tabi.core.authoring import AuthoringService
from tabi.core.models.base import Identifier
from tabi.core.models.publishing import ReleaseBundleReport, ReleasePreparation
from tabi.core.portability import BackupService
from tabi.core.publishing import ReleaseService

from .contracts import (
    BackupTarget,
    ExportRelease,
    ReleaseReview,
    RestoreBackup,
    SaveRelease,
    WebBackup,
    WebReleases,
)


def routes(runtime):
    router = APIRouter(prefix="/api/v1")

    def service(handle):
        return ReleaseService(runtime.get(handle).assets, runtime.settings)

    @router.get("/projects/{handle}/releases", response_model=WebReleases)
    def preparations(handle: str):
        return WebReleases(
            schema_version="1.0",
            flow_exports=[
                e
                for e in runtime.flow_service(runtime.get(handle)).exports()
                if e.state == "verified"
            ],
            preparations=AuthoringService(runtime.get(handle).assets).documents(
                "publishing", ReleasePreparation
            ),
        )

    @router.post("/projects/{handle}/releases")
    def save(handle: str, body: SaveRelease):
        current = service(handle)
        try:
            old = current.load(body.preparation.id)
        except FileNotFoundError:
            old = None
        if any(
            getattr(body.preparation, k) != (getattr(old, k) if old else None)
            for k in ("creative_review", "metadata_review")
        ):
            raise ValueError("Record reviews using the explicit content-hash review controls")
        return current.save(body.preparation, expected_revision=body.expected_revision)

    @router.post("/projects/{handle}/releases/{identity}/inspect")
    def inspect(handle: str, identity: str):
        current = service(handle)
        with runtime.local_operation(runtime.get(handle)):
            return current.inspect(current.load(identity))

    @router.post("/projects/{handle}/releases/{identity}/review")
    def review(handle: str, identity: str, body: ReleaseReview):
        with runtime.local_operation(runtime.get(handle)):
            return service(handle).review(identity, **body.model_dump())

    @router.post("/projects/{handle}/releases/{identity}/export")
    def export(handle: str, identity: str, body: ExportRelease):
        with runtime.local_operation(runtime.get(handle)):
            return service(handle).export(
                identity, body.bundle_id, require_ready=body.require_ready
            )

    @router.api_route(
        "/projects/{handle}/bundles/{identity}/files/{index}", methods=["GET", "HEAD"]
    )
    def bundle_file(handle: str, identity: str, index: int, request: Request):
        TypeAdapter(Identifier).validate_python(identity)
        item = runtime.get(handle)
        report = item.assets.store.read(f"bundles/{identity}/manifest.json")
        if (
            not isinstance(report, ReleaseBundleReport)
            or report.bundle_path != f"bundles/{identity}"
        ):
            raise ValueError("bundle identity differs from its manifest")
        if not 0 <= index < len(report.files):
            raise HTTPException(404, "Bundle file not found")
        file = report.files[index]
        # Private records are retained on disk, never linked from the shareable file list.
        if not file.location.path.startswith(f"bundles/{identity}/public/"):
            raise HTTPException(403, "This record is private backup evidence")
        return runtime.artifacts.response(
            item.assets.store,
            file.location.path,
            file.sha256,
            request,
            media_type=mimetypes.guess_type(file.location.path)[0] or "application/octet-stream",
        )

    @router.post("/projects/{handle}/backup", response_model=WebBackup)
    def backup(handle: str, body: BackupTarget):
        parent = runtime.roots.directory(body.root_id, body.parent)
        result = BackupService(runtime.get(handle).assets).export(parent / body.folder)
        return WebBackup(
            schema_version="1.0",
            root_id=body.root_id,
            path="/".join(p for p in (body.parent, body.folder) if p),
            manifest=result,
        )

    @router.post("/backups/restore")
    def restore(body: RestoreBackup):
        source = runtime.roots.directory(body.source_root_id, body.source_path)
        parent = runtime.roots.directory(body.root_id, body.parent)
        BackupService.restore(source, parent / body.folder)
        return runtime.open(
            body.root_id, "/".join(p for p in (body.parent, body.folder) if p)
        ).info()

    return router
