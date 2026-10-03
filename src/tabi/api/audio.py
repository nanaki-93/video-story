"""Audio forms use sample-based core editing, measured auditions and factual metadata."""

from fastapi import APIRouter, Query, Request

from tabi.core.audio import AudioService
from tabi.core.audio.editor import AudioEdit, AudioEditor
from tabi.core.audio.timeline import prepared_samples
from tabi.core.models.base import AssetRef
from tabi.core.process import ExecutionScope, execution_scope

from .contracts import AudioAudition, MusicMetadata, WebAudio, WebAudioMix


def routes(runtime):
    router = APIRouter(prefix="/api/v1/projects/{handle}")

    def editor(handle):
        return AudioEditor(runtime.get(handle).assets, runtime.settings)

    @router.get("/episodes/{identity}/audio", response_model=WebAudio)
    def inspect(handle: str, identity: str):
        service = editor(handle)
        episode = service.author.episode(identity)
        return WebAudio(
            schema_version="1.0",
            episode=episode,
            timeline=AudioService(service.assets).inspect(episode),
            sources=[
                {"asset": a, "prepared_samples": prepared_samples(a)}
                for a in service.assets.list_assets()
                if a.kind == "audio"
            ],
        )

    @router.post("/episodes/{identity}/audio/plan")
    def plan(handle: str, identity: str, body: AudioEdit):
        return editor(handle).propose(identity, body)[0]

    @router.post("/episodes/{identity}/audio")
    def save(handle: str, identity: str, body: AudioEdit):
        return editor(handle).apply(identity, body)

    @router.get("/assets/{identity}/{version}/waveform")
    def waveform(
        handle: str, identity: str, version: str, bins: int = Query(default=512, ge=1, le=8192)
    ):
        return AudioService(runtime.get(handle).assets).waveform(
            AssetRef(id=identity, version=version), bins=bins
        )

    @router.post("/episodes/{identity}/audio/audition", response_model=WebAudioMix)
    def audition(handle: str, identity: str, body: AudioAudition):
        with execution_scope(ExecutionScope(runtime.stopping.is_set)):
            identity, report = editor(handle).audition(
                identity, body.expected_revision, body.first_sample, body.end_sample
            )
            return WebAudioMix(schema_version="1.0", id=identity, report=report)

    @router.api_route("/audio/auditions/{identity}/media", methods=["GET", "HEAD"])
    def media(handle: str, identity: str, request: Request):
        service = editor(handle)
        relative, report = service.audition_report(identity)
        return runtime.artifacts.response(
            service.store, relative, report.output_sha256, request, media_type="audio/wav"
        )

    @router.post("/music-metadata")
    def metadata(handle: str, body: MusicMetadata):
        return AudioService(runtime.get(handle).assets).save_release(
            body.record, expected_revision=body.expected_revision
        )

    return router
