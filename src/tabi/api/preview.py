"""Authenticated previews and disconnect-scoped still requests."""

import asyncio
import threading

from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from tabi.core.preview import PreviewService
from tabi.core.process import ExecutionScope, OperationCancelled, execution_scope

from .contracts import FrameRequest, MarkerRequest, PreviewRequest, WebFrame, WebPreview


def routes(runtime):
    router = APIRouter(prefix="/api/v1/projects/{handle}")
    still_lane = threading.Lock()

    def service(handle):
        item = runtime.get(handle)
        return PreviewService(item.assets, runtime.settings, item.jobs)

    @router.get("/episodes/{identity}/preview", response_model=WebPreview)
    def inspect(handle: str, identity: str):
        return service(handle).inspect(identity)

    @router.post("/episodes/{identity}/preview")
    def submit(handle: str, identity: str, body: PreviewRequest):
        if runtime.stopping.is_set():
            raise HTTPException(409, "Worker is stopping; reopen from the launcher")
        result = service(handle).submit(
            identity, body.expected_revision, body.first_frame, body.end_frame
        )
        runtime.wake.set()
        return result

    @router.post("/episodes/{identity}/preview/markers")
    def marker(handle: str, identity: str, body: MarkerRequest):
        return service(handle).marker(identity, body.snapshot_sha256, body.frame, body.note)

    @router.post("/frames", response_model=WebFrame)
    async def frame(handle: str, body: FrameRequest, request: Request):
        cancelled = threading.Event()

        def render():
            if not still_lane.acquire(blocking=False):
                raise HTTPException(409, "An exact frame is finishing; retry in a moment")
            try:
                with execution_scope(
                    ExecutionScope(lambda: cancelled.is_set() or runtime.stopping.is_set())
                ):
                    identity, report = service(handle).frame(body.snapshot_sha256, body.frame)
                    return WebFrame(schema_version="1.0", id=identity, report=report)
            finally:
                still_lane.release()

        task = asyncio.create_task(run_in_threadpool(render))
        try:
            while not task.done():
                await asyncio.wait({task}, timeout=0.1)
                if await request.is_disconnected():
                    cancelled.set()
            return await task
        except OperationCancelled:
            raise HTTPException(409, "Superseded exact-frame request cancelled") from None
        finally:
            cancelled.set()

    @router.api_route("/frames/{identity}/image", methods=["GET", "HEAD"])
    def image(handle: str, identity: str, request: Request):
        item = runtime.get(handle)
        relative, report = service(handle).frame_report(identity)
        return runtime.artifacts.response(
            item.assets.store, relative, report.output_sha256, request, media_type="image/png"
        )

    return router
