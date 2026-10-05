"""Assisted Flow handoffs; all timing, reviews and media work stay in Python."""

import json
from uuid import uuid4

from fastapi import APIRouter, Request

from tabi.core.audio.timeline import prepared_samples
from tabi.core.flow.assembly import FlowAssembler
from tabi.core.flow.media import FlowMedia
from tabi.core.flow.review import FlowReview
from tabi.core.flow.runner import FlowRunner
from tabi.core.flow.service import updated
from tabi.core.models.assets import Provenance
from tabi.core.models.base import HashedFile
from tabi.core.models.registry import ImportRequest
from tabi.core.persistence import ProjectStore

from .contracts import (
    FlowBranch,
    FlowClone,
    FlowCreate,
    FlowExportRequest,
    FlowImport,
    FlowReferenceRequest,
    FlowReviewRequest,
    FlowRevision,
    FlowSource,
    FlowTransition,
    WebFlow,
)
from .uploads import Uploads


def routes(runtime):
    router = APIRouter(prefix="/api/v1/projects/{handle}/flow")

    def services(handle):
        item = runtime.get(handle)
        return item, runtime.flow_service(item)

    def view(handle, identity=None):
        item, service = services(handle)
        episode = service.get(identity) if identity else None
        data = {"schema_version": "1.0", "episodes": service.list(), "episode": episode}
        if episode:
            step = FlowRunner(service).status(episode)
            base = f"/api/v1/projects/{handle}/flow/{identity}"
            candidate = (
                service.candidate(episode, step["candidate_id"]) if step["candidate_id"] else None
            )
            parent = service.candidate(episode, step["parent_id"]) if step["parent_id"] else None
            data.update(
                next_step=step,
                exports=service.exports(identity),
                reference_urls=[f"{base}/references/{i}" for i in range(len(episode.references))],
                parent_url=f"{base}/clips/{parent.id}/video" if parent else None,
                candidate_url=f"{base}/clips/{candidate.id}/video" if candidate else None,
                target_samples=episode.recipe.fps.sample_at(episode.recipe.target_frames),
                audio_sources=[
                    {"asset": a, "prepared_samples": prepared_samples(a)}
                    for a in item.assets.list_assets()
                    if a.kind == "audio"
                ],
            )
            if candidate:
                remaining = episode.recipe.target_frames - episode.accepted_frames
                if 0 < remaining <= candidate.trim.end_frame - candidate.trim.start_frame:
                    data["safe_cut_frame"] = candidate.trim.start_frame + remaining
                if candidate.review_packet:
                    packet = FlowReview(service, runtime.settings).read(candidate)
                    data["review"] = {
                        "images": [
                            {
                                "role": image["role"],
                                "frame": image["frame"],
                                "url": f"{base}/clips/{candidate.id}/images/{index}",
                            }
                            for index, image in enumerate(packet["images"])
                        ],
                        "join_url": f"{base}/clips/{candidate.id}/join"
                        if packet["join_video"]
                        else None,
                        "diagnostics": [
                            f"{key}: {json.dumps(value)}"
                            for key, value in packet["diagnostics"].items()
                        ],
                        "checklist": packet["review_checklist"],
                    }
        return WebFlow.model_validate(data)

    def source(item, body):
        return (
            Uploads(item.assets.store).location(body.upload_id) if body.upload_id else body.source
        )

    def media_response(item, media, request, media_type="video/mp4"):
        store = (
            item.assets.store
            if media.location.root_id == "project"
            else ProjectStore(runtime.roots.root(media.location.root_id))
        )
        return runtime.artifacts.response(
            store, media.location.path, media.sha256, request, media_type=media_type
        )

    @router.get("", response_model=WebFlow)
    def listing(handle: str):
        return view(handle)

    @router.post("", response_model=WebFlow)
    def create(handle: str, body: FlowCreate):
        _, service = services(handle)
        episode = service.create(body.title, body.limits, recipe=body.recipe)
        return view(handle, episode.id)

    @router.get("/{identity}", response_model=WebFlow)
    def inspect(handle: str, identity: str):
        return view(handle, identity)

    @router.post("/{identity}/clone", response_model=WebFlow)
    def clone(handle: str, identity: str, body: FlowClone):
        _, service = services(handle)
        episode = service.clone(identity, body.title)
        if body.recipe or body.limits:
            episode = service.save(
                updated(
                    episode,
                    recipe=body.recipe or episode.recipe,
                    limits=body.limits or episode.limits,
                ),
                expected_revision=episode.revision,
            )
        return view(handle, episode.id)

    @router.post("/{identity}/reference", response_model=WebFlow)
    def reference(handle: str, identity: str, body: FlowReferenceRequest):
        item, service = services(handle)
        episode = service.get(identity)
        if episode.attempts:
            raise ValueError("Start a variation to change references after generation began.")
        with runtime.local_operation(item):
            ref = FlowMedia(service, runtime.settings).reference(
                source(item, body), title=body.title, synthetic=body.synthetic
            )
            service.save(
                updated(episode, references=[*episode.references, ref]),
                expected_revision=body.expected_revision,
            )
        return view(handle, identity)

    @router.post("/{identity}/prepare", response_model=WebFlow)
    def prepare(handle: str, identity: str, body: FlowRevision):
        _, service = services(handle)
        FlowRunner(service).prepare(identity, body.expected_revision)
        return view(handle, identity)

    @router.post("/{identity}/import", response_model=WebFlow)
    def import_result(handle: str, identity: str, body: FlowImport):
        item, service = services(handle)
        with runtime.local_operation(item):
            result = FlowMedia(service, runtime.settings).import_result(
                identity,
                body.attempt_id,
                source(item, body),
                revision=body.expected_revision,
                **body.model_dump(
                    exclude={
                        "expected_revision",
                        "attempt_id",
                        "upload_id",
                        "source",
                        "source_range",
                    }
                ),
                source_range=body.source_range,
            )
            candidate = next(c for c in result.candidates if c.attempt_id == body.attempt_id)
            if not candidate.review_packet:
                FlowReview(service, runtime.settings).prepare(
                    identity, candidate.id, revision=result.revision
                )
        return view(handle, identity)

    @router.post("/{identity}/clips/{candidate_id}/review", response_model=WebFlow)
    def review(handle: str, identity: str, candidate_id: str, body: FlowReviewRequest):
        _, service = services(handle)
        service.review(
            identity,
            candidate_id,
            revision=body.expected_revision,
            **body.model_dump(exclude={"expected_revision", "observed_state", "trim"}),
            observed_state=body.observed_state,
            trim=body.trim,
        )
        return view(handle, identity)

    @router.post("/{identity}/attempts/{attempt_id}", response_model=WebFlow)
    def transition(handle: str, identity: str, attempt_id: str, body: FlowTransition):
        _, service = services(handle)
        FlowRunner(service).transition(
            identity,
            attempt_id,
            revision=body.expected_revision,
            **body.model_dump(exclude={"expected_revision"}),
        )
        return view(handle, identity)

    @router.post("/{identity}/branch", response_model=WebFlow)
    def branch(handle: str, identity: str, body: FlowBranch):
        _, service = services(handle)
        service.branch_from(identity, body.parent_id, body.expected_revision)
        return view(handle, identity)

    @router.post("/{identity}/pause", response_model=WebFlow)
    @router.post("/{identity}/resume", response_model=WebFlow)
    def pause(handle: str, identity: str, body: FlowRevision, request: Request):
        operation = request.url.path.rsplit("/", 1)[-1]
        _, service = services(handle)
        FlowRunner(service).pause(identity, body.expected_revision, paused=operation == "pause")
        return view(handle, identity)

    @router.post("/{identity}/music/import", response_model=WebFlow)
    def music(handle: str, identity: str, body: FlowSource):
        item, service = services(handle)
        episode = service.get(identity)
        if episode.revision != body.expected_revision:
            raise ValueError("Video changed; reload before importing music")
        with runtime.local_operation(item):
            item.assets.import_asset(
                ImportRequest(
                    id=f"flow-music-{uuid4().hex}",
                    version="1.0",
                    kind="audio",
                    paths=[source(item, body)],
                    provenance=Provenance(
                        origin="synthetic" if body.synthetic else "user_supplied"
                    ),
                )
            )
        return view(handle, identity)

    @router.post("/{identity}/exports", response_model=WebFlow)
    def export(handle: str, identity: str, body: FlowExportRequest):
        item, service = services(handle)
        with runtime.local_operation(item):
            FlowAssembler(service, runtime.settings).freeze(
                identity, revision=body.expected_revision, profile=body.profile, tracks=body.tracks
            )
        runtime.wake.set()
        return view(handle, identity)

    @router.post("/{identity}/exports/{export_id}/{operation}", response_model=WebFlow)
    def export_control(
        handle: str, identity: str, export_id: str, operation: str, body: FlowRevision
    ):
        item, service = services(handle)
        export = service.get_export(export_id)
        if export.episode_id != identity or export.revision != body.expected_revision:
            raise ValueError("Export changed; reload before continuing")
        if operation == "cancel":
            runtime.flow_cancel(item, export_id)
        elif operation == "resume" and export.state in {"interrupted", "failed"}:
            service.save_export(
                updated(export, state="queued", diagnostic=None), expected_revision=export.revision
            )
            runtime.wake.set()
        else:
            raise ValueError("This export cannot perform that operation")
        return view(handle, identity)

    @router.api_route("/{identity}/references/{index}", methods=["GET", "HEAD"])
    def ref_media(handle: str, identity: str, index: int, request: Request):
        item, service = services(handle)
        refs = service.get(identity).references
        if not 0 <= index < len(refs):
            raise ValueError("Reference is missing")
        media = refs[index].media
        return media_response(item, media, request, "image/png")

    @router.api_route("/{identity}/clips/{candidate_id}/{kind}", methods=["GET", "HEAD"])
    def clip_media(handle: str, identity: str, candidate_id: str, kind: str, request: Request):
        item, service = services(handle)
        candidate = service.candidate(service.get(identity), candidate_id)
        if kind == "video":
            media = candidate.media
        elif kind == "join":
            raw = FlowReview(service, runtime.settings).read(candidate)["join_video"]
            if raw is None:
                raise ValueError("An opening has no previous join")
            media = HashedFile.model_validate(raw)
        else:
            raise ValueError("Unknown clip artifact")
        return media_response(item, media, request)

    @router.api_route("/{identity}/clips/{candidate_id}/images/{index}", methods=["GET", "HEAD"])
    def image_media(handle: str, identity: str, candidate_id: str, index: int, request: Request):
        item, service = services(handle)
        packet = FlowReview(service, runtime.settings).read(
            service.candidate(service.get(identity), candidate_id)
        )
        if not 0 <= index < len(packet["images"]):
            raise ValueError("Review image is missing")
        return media_response(
            item, HashedFile.model_validate(packet["images"][index]["media"]), request, "image/png"
        )

    @router.api_route("/{identity}/exports/{export_id}/video", methods=["GET", "HEAD"])
    def export_media(handle: str, identity: str, export_id: str, request: Request):
        item, service = services(handle)
        export = service.get_export(export_id)
        if export.episode_id != identity or export.state != "verified":
            raise ValueError("Video export is not verified yet")
        return media_response(item, export.output, request)

    return router
