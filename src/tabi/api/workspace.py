"""Project/asset/episode transport. All authoring and media checks live in core services."""

import mimetypes
import os

from fastapi import APIRouter, HTTPException, Query, Request
from starlette.concurrency import run_in_threadpool

from tabi.core.authoring import AuthoringService, NewEpisode
from tabi.core.models import ActionPack, ImportRequest, ReleaseRecord
from tabi.core.models.base import AssetRef
from tabi.core.persistence import ProjectStore

from .contracts import (
    AssetRelink,
    AssetRevision,
    BeginUpload,
    CreateProject,
    ImportUploads,
    InstallDocument,
    ProxyVersion,
    Review,
    StillTemplate,
    WebCatalog,
)
from .files import open_local
from .uploads import CHUNK_BYTES, Uploads


def routes(runtime):
    router = APIRouter(prefix="/api/v1")

    def service(handle):
        return AuthoringService(runtime.get(handle).assets)

    @router.get("/recents")
    def recents():
        return runtime.recents()

    @router.post("/projects/create")
    def create(body: CreateProject):
        if "/" in body.folder:
            raise ValueError("project folder must be one name inside the chosen directory")
        parent = runtime.roots.directory(body.root_id, body.parent)
        with ProjectStore(parent)._directory(()) as descriptor:
            os.mkdir(body.folder, mode=0o700, dir_fd=descriptor)
        ProjectStore.initialize(parent / body.folder, body.title)
        path = f"{body.parent}/{body.folder}" if body.parent else body.folder
        return runtime.open(body.root_id, path).info()

    @router.get("/projects/{handle}/catalog", response_model=WebCatalog)
    def catalog(handle: str):
        author = service(handle)
        return WebCatalog(
            schema_version="1.0",
            assets=author.assets.list_assets(),
            templates=author.templates(),
            packs=author.documents("registry/actions", ActionPack),
            episodes=author.episodes(),
            releases=author.documents("releases", ReleaseRecord),
        )

    @router.post("/projects/{handle}/documents")
    def install(handle: str, body: InstallDocument):
        return service(handle).install(body.document, expected_revision=body.expected_revision)

    @router.post("/projects/{handle}/templates/still")
    def still(handle: str, body: StillTemplate):
        return service(handle).still_template(
            body.asset, identity=body.id, version=body.version, camera_id=body.camera_id
        )

    @router.post("/projects/{handle}/episodes")
    def new_episode(handle: str, body: NewEpisode):
        return service(handle).create_episode(body)

    @router.get("/projects/{handle}/episodes/{identity}")
    def episode(handle: str, identity: str):
        return service(handle).episode(identity)

    @router.post("/projects/{handle}/assets/import")
    def asset_import(handle: str, body: ImportRequest):
        item = runtime.get(handle)
        # Native chooser paths are bounded and cannot refer through internal symlinks either.
        for path in body.paths:
            root = (
                item.assets.store
                if path.root_id == "project"
                else ProjectStore(runtime.roots.root(path.root_id))
            )
            with open_local(root, path.path):
                pass
        return item.assets.import_asset(body)

    @router.get("/projects/{handle}/assets/{identity}/{version}/health")
    def asset_health(handle: str, identity: str, version: str):
        return runtime.get(handle).assets.check(AssetRef(id=identity, version=version))

    @router.post("/projects/{handle}/assets/{identity}/{version}/version")
    def asset_version(handle: str, identity: str, version: str, body: AssetRevision):
        return service(handle).asset_version(
            AssetRef(id=identity, version=version),
            version=body.version,
            provenance=body.provenance,
            compatibility=body.compatibility,
        )

    @router.post("/projects/{handle}/assets/{identity}/{version}/relink")
    def asset_relink(handle: str, identity: str, version: str, body: AssetRelink):
        return runtime.get(handle).assets.relink(
            AssetRef(id=identity, version=version), version=body.version, paths=body.paths
        )

    @router.post("/projects/{handle}/assets/{identity}/{version}/approve")
    def approve(handle: str, identity: str, version: str, body: Review):
        return runtime.get(handle).assets.approve(
            AssetRef(id=identity, version=version), **body.model_dump()
        )

    @router.post("/projects/{handle}/assets/{identity}/{version}/proxy")
    def proxy(handle: str, identity: str, version: str, body: ProxyVersion):
        return runtime.get(handle).assets.image_proxies(
            AssetRef(id=identity, version=version), **body.model_dump()
        )

    @router.api_route(
        "/projects/{handle}/assets/{identity}/{version}/media", methods=["GET", "HEAD"]
    )
    def asset_media(
        handle: str,
        identity: str,
        version: str,
        request: Request,
        index: int = Query(default=0, ge=0),
        proxy: bool = False,
    ):
        item = runtime.get(handle)
        asset = item.assets.load(AssetRef(id=identity, version=version))
        records = asset.proxies if proxy else asset.files
        if index >= len(records) or asset.kind == "font":
            raise HTTPException(404, "selected media is unavailable")
        record = records[index]
        root = (
            item.assets.store
            if record.location.root_id == "project"
            else ProjectStore(runtime.roots.root(record.location.root_id))
        )
        return runtime.artifacts.response(
            root,
            record.location.path,
            record.sha256,
            request,
            media_type=mimetypes.guess_type(record.location.path)[0] or "application/octet-stream",
        )

    @router.post("/projects/{handle}/uploads")
    def upload_start(handle: str, body: BeginUpload):
        return Uploads(runtime.get(handle).assets.store).start(body)

    @router.get("/projects/{handle}/uploads/{identity}")
    def upload_read(handle: str, identity: str):
        return Uploads(runtime.get(handle).assets.store).read(identity)

    @router.put("/projects/{handle}/uploads/{identity}/chunk")
    async def upload_chunk(handle: str, identity: str, request: Request, offset: int = Query(ge=0)):
        item = await run_in_threadpool(runtime.get, handle)
        data = bytearray()
        async for part in request.stream():
            if len(data) + len(part) > CHUNK_BYTES:
                raise HTTPException(413, "upload chunk exceeds 4 MiB")
            data.extend(part)
        if len(data) != int(request.headers["content-length"]):
            raise HTTPException(400, "upload chunk length differs from request")
        return await run_in_threadpool(Uploads(item.assets.store).chunk, identity, offset, data)

    @router.post("/projects/{handle}/uploads/{identity}/finish")
    def upload_finish(handle: str, identity: str):
        return Uploads(runtime.get(handle).assets.store).finish(identity)

    @router.post("/projects/{handle}/uploads/{identity}/discard")
    def upload_discard(handle: str, identity: str):
        return Uploads(runtime.get(handle).assets.store).discard(identity)

    @router.post("/projects/{handle}/uploads/import")
    def upload_import(handle: str, body: ImportUploads):
        item = runtime.get(handle)
        copies = Uploads(item.assets.store)
        if "paths" in body.request or "mode" in body.request:
            raise ValueError("uploaded imports receive their verified paths from the worker")
        request = ImportRequest.model_validate(
            {**body.request, "mode": "copy", "paths": [copies.location(i) for i in body.uploads]}
        )
        return item.assets.import_asset(request)

    return router
