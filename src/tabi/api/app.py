"""Same-origin API, static UI, durable job events and authenticated artifacts."""

import asyncio
import mimetypes
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse, StreamingResponse

from tabi.core.documents import DocumentError
from tabi.core.models.production import RenderJob
from tabi.core.persistence import ProjectBusy, ProjectStore, RevisionConflict, UnsafePath

from .contracts import Bootstrap, FileSelection, Shutdown, SubmitJob, WebJobs, WebSession
from .security import SecurityBoundary


def create_app(runtime, origin, web_root, *, drive_jobs=True):
    web_root = Path(web_root).resolve(strict=True)
    if not (web_root / "index.html").is_file():
        raise ValueError("Built web UI missing; run make web-build or install a packaged build")

    @asynccontextmanager
    async def lifespan(app):
        if drive_jobs:
            runtime.start()
        yield
        runtime.stop(cancel=True)
        if runtime.thread:
            await run_in_threadpool(runtime.thread.join, 30)

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(SecurityBoundary, sessions=runtime.sessions, origin=origin)
    app.state.runtime = runtime

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request, error):
        return JSONResponse(
            {"detail": [{"location": list(e["loc"]), "message": e["msg"]} for e in error.errors()]},
            status_code=422,
        )

    @app.exception_handler(ValueError)
    async def invalid_operation(request, error):
        if isinstance(error, DocumentError):
            return JSONResponse(error.report().model_dump(mode="json"), status_code=422)
        return JSONResponse(
            {"detail": str(error)},
            status_code=409 if isinstance(error, (ProjectBusy, RevisionConflict)) else 400,
        )

    @app.exception_handler(OSError)
    async def unavailable_file(request, error):
        return JSONResponse(
            {"detail": "Local file unavailable or permission denied; check the registered folder"},
            status_code=404,
        )

    @app.post("/api/v1/bootstrap", response_model=WebSession)
    def bootstrap(body: Bootstrap, response: Response):
        if not runtime.sessions.exchange(body.secret):
            raise HTTPException(401, "Browser ticket expired or already used; reopen from launcher")
        response.set_cookie(
            runtime.sessions.cookie_name,
            runtime.sessions.cookie,
            httponly=True,
            samesite="strict",
            path="/api/",
            max_age=runtime.sessions.lifetime,
        )
        return runtime.sessions.info(runtime.stopping.is_set())

    @app.get("/api/v1/session", response_model=WebSession)
    def session():
        return runtime.sessions.info(runtime.stopping.is_set())

    @app.post("/api/v1/bootstrap-ticket")
    def ticket(request: Request):
        if not request.state.bearer:
            raise HTTPException(403, "Only the owning launcher can open a fresh browser session")
        return {"secret": runtime.sessions.ticket()}

    @app.post("/api/v1/shutdown")
    def shutdown(body: Shutdown):
        runtime.stop(cancel=body.mode == "cancel")
        return {"stopping": True, "mode": body.mode}

    @app.get("/api/v1/roots")
    def roots():
        return runtime.roots.listing()

    @app.get("/api/v1/files")
    def files(root_id: str, path: str = "", offset: int = Query(default=0, ge=0)):
        return runtime.roots.browse(root_id, path, offset)

    @app.get("/api/v1/projects")
    def projects():
        return runtime.listing()

    @app.post("/api/v1/projects/open")
    def open_project(body: FileSelection):
        return runtime.open(body.root_id, body.path, body.expected_project_id).info()

    @app.get("/api/v1/projects/{handle}")
    def project(handle: str):
        return runtime.get(handle).info()

    @app.get("/api/v1/projects/{handle}/jobs", response_model=WebJobs)
    def jobs(handle: str):
        return WebJobs(schema_version="1.0", jobs=runtime.get(handle).jobs.ledger.all())

    @app.post("/api/v1/projects/{handle}/jobs", response_model=RenderJob)
    def submit(handle: str, body: SubmitJob):
        if runtime.stopping.is_set():
            raise HTTPException(409, "Worker is stopping; the project and existing jobs are saved")
        result = runtime.get(handle).jobs.submit(
            body.snapshot_sha256,
            body.profile,
            body.destination,
            first_frame=body.first_frame,
            end_frame=body.end_frame,
            max_chunk_frames=body.max_chunk_frames,
        )
        runtime.wake.set()
        return result

    @app.get("/api/v1/projects/{handle}/jobs/{identity}", response_model=RenderJob)
    def job(handle: str, identity: str):
        return runtime.get(handle).jobs.ledger.get(identity)

    @app.post("/api/v1/projects/{handle}/jobs/{identity}/cancel", response_model=RenderJob)
    def cancel(handle: str, identity: str):
        return runtime.cancel(runtime.get(handle), identity)

    @app.post("/api/v1/projects/{handle}/jobs/{identity}/resume", response_model=RenderJob)
    def resume(handle: str, identity: str):
        if runtime.stopping.is_set():
            raise HTTPException(409, "Worker is stopping")
        result = runtime.get(handle).jobs.resume(identity)
        runtime.wake.set()
        return result

    @app.get("/api/v1/projects/{handle}/jobs/{identity}/events")
    async def events(handle: str, identity: str, request: Request):
        item = await run_in_threadpool(runtime.get, handle)
        await run_in_threadpool(item.jobs.ledger.get, identity)
        try:
            cursor = int(request.headers.get("last-event-id", "-1"))
            if cursor < -1:
                raise ValueError
        except ValueError:
            raise HTTPException(400, "Invalid event cursor") from None

        async def updates():
            nonlocal cursor
            while not runtime.stopping.is_set():
                if not request.state.bearer and not runtime.sessions.valid_cookie(
                    request.cookies.get(runtime.sessions.cookie_name)
                ):
                    yield "event: session-expired\ndata: {}\n\n"
                    return
                records = await run_in_threadpool(item.jobs.ledger.events, identity)
                for record in records:
                    if record.sequence > cursor:
                        yield (
                            f"id: {record.sequence}\nevent: job\n"
                            f"data: {record.model_dump_json()}\n\n"
                        )
                        cursor = record.sequence
                yield ": heartbeat\n\n"
                if await request.is_disconnected():
                    return
                await asyncio.sleep(0.5)

        return StreamingResponse(updates(), media_type="text/event-stream")

    @app.api_route("/api/v1/projects/{handle}/jobs/{identity}/video", methods=["GET", "HEAD"])
    def video(handle: str, identity: str, request: Request):
        item = runtime.get(handle)
        job = item.jobs.ledger.get(identity)
        if job.state != "verified" or job.output is None:
            raise HTTPException(409, "Video is not verified yet")
        if job.output.location.root_id != "project" or job.output.location.path != job.destination:
            raise ValueError("job video is not a registered project artifact")
        return runtime.artifacts.response(
            item.assets.store, job.destination, job.output.sha256, request
        )

    from .workspace import routes as workspace_routes

    app.include_router(workspace_routes(runtime))
    from .preview import routes as preview_routes

    app.include_router(preview_routes(runtime))

    @app.api_route("/{path:path}", methods=["GET", "HEAD"])
    def static(path: str, request: Request):
        if path.startswith("api/"):
            raise HTTPException(404, "API route not found")
        relative = path or "index.html"
        # No SPA fallback for unknown files and no project paths under this static root.
        if relative != "index.html" and not relative.startswith("assets/"):
            raise HTTPException(404, "Static asset not found")
        try:
            return runtime.artifacts.response(
                ProjectStore(web_root),
                relative,
                None,
                request,
                media_type=mimetypes.guess_type(relative)[0] or "application/octet-stream",
            )
        except UnsafePath:
            raise HTTPException(404, "Static asset unavailable") from None

    return app
