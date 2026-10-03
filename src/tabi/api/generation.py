"""Optional generation controls use the same bounded core adapter as the CLI."""

from fastapi import APIRouter

from tabi.core.generation import GenerationService
from tabi.core.models.base import SHA256, AssetRef, Model
from tabi.core.models.generation import ComfyWorkflow, GenerationRun, GenerationStatus


class SubmitGeneration(Model):
    workflow: AssetRef
    expected_hash: SHA256


def routes(runtime):
    router = APIRouter(prefix="/api/v1/projects/{handle}/generation")

    def service(handle):
        return GenerationService(runtime.get(handle).assets, runtime.settings)

    @router.get("", response_model=GenerationStatus)
    def status(handle: str, probe: bool = False):
        return service(handle).status(probe=probe)

    @router.post("/workflows", response_model=ComfyWorkflow)
    def register(handle: str, body: ComfyWorkflow):
        return service(handle).register(body)

    @router.post("/submit", response_model=GenerationRun)
    def submit(handle: str, body: SubmitGeneration):
        return service(handle).submit(body.workflow, expected_hash=body.expected_hash)

    @router.post("/{identity}/refresh", response_model=GenerationRun)
    def refresh(handle: str, identity: str):
        return service(handle).poll(identity)

    @router.post("/{identity}/import", response_model=GenerationRun)
    def import_results(handle: str, identity: str):
        return service(handle).import_results(identity)

    return router
