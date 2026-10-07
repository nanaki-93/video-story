"""Authenticated transport for reusable scenes; Python owns the complete episode schedule."""

from fastapi import APIRouter

from tabi.core.lofi import LofiService
from tabi.core.models.lofi import CreateLofiVideo, SaveLofiScene

from .contracts import WebLofi


def routes(runtime):
    router = APIRouter(prefix="/api/v1/projects/{handle}/lofi")

    def service(handle):
        return LofiService(runtime.get(handle).assets)

    @router.get("", response_model=WebLofi)
    def catalog(handle: str):
        current = service(handle)
        return WebLofi(
            schema_version="1.0",
            scenes=current.scenes(),
        )

    @router.post("/scenes")
    def save(handle: str, body: SaveLofiScene):
        return service(handle).save(
            body.scene,
            expected_revision=body.expected_revision,
            timing_seconds=body.timing_seconds,
        )

    @router.post("/videos")
    def create(handle: str, body: CreateLofiVideo):
        return service(handle).create_video(body)

    return router
