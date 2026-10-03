"""Pixel dependencies deliberately exclude soundtrack and editorial-only changes."""

import hashlib
import platform
from pathlib import Path

import PIL
from PIL import features

from ..models.production import ScheduledAction
from ..models.scenes import LandmarkEvent, PropEvent


def image_descriptor(asset, frame, purpose):
    normalizer = Path(__file__).parents[1] / "render/normalize.py"
    return {
        "version": "1",
        "kind": "normalized_image",
        "purpose": purpose,
        "algorithm_sha256": hashlib.sha256(normalizer.read_bytes()).hexdigest(),
        "pillow": PIL.__version__,
        "codecs": {name: features.version(name) for name in ("zlib", "jpg", "littlecms2")},
        "asset_kind": asset.kind,
        "source": asset.files[frame].model_dump(mode="json"),
        "probe": asset.probe.model_dump(mode="json"),
        "crop": asset.compatibility.crop.model_dump(mode="json")
        if asset.compatibility.crop
        else None,
    }


def visual_inputs(snapshot, registry, first, end):
    scenes = [
        scene
        for scene in snapshot.episode.scenes
        if scene.start_frame < end and first < scene.end_frame
    ]
    scene_ids = {scene.id for scene in scenes}
    schedule = [
        event
        for event in snapshot.schedule
        if event.scene_id in scene_ids
        and (isinstance(event, PropEvent) or (event.start_frame < end and first < event.end_frame))
    ]
    refs = set()

    def add(ref):
        if ref:
            refs.add((ref.id, ref.version))

    for scene in scenes:
        add(scene.template)
        template = registry.get(scene.template, "scene_template")
        for slot in template.slots:
            add(scene.slot_assignments.get(slot.id, slot.asset))
            add(slot.mask)
        for transition in (scene.transition_in, scene.transition_out):
            add(transition.match_action)
    for event in schedule:
        if isinstance(event, ScheduledAction):
            add(event.pack)
            add(event.clip)
        elif isinstance(event, LandmarkEvent):
            add(event.asset)
    scene_data = []
    for scene in scenes:
        data = scene.model_dump(mode="json", exclude={"purpose", "final_state"})
        for name in ("transition_in", "transition_out"):
            data[name].pop("note", None)
        scene_data.append(data)
    return {
        "scenes": scene_data,
        "curves": [
            curve.model_dump(mode="json")
            for curve in snapshot.episode.curves
            if curve.scope in {*scene_ids, "episode"}
        ],
        "schedule": [event.model_dump(mode="json") for event in schedule],
        "locks": [
            lock.model_dump(mode="json")
            for lock in snapshot.locked_assets
            if (lock.id, lock.version) in refs
        ],
    }, refs


def video_descriptor(snapshot, registry, job, chunk):
    from ..jobs.planner import video_profile

    first = job.first_frame + chunk.first_frame
    visual, _ = visual_inputs(snapshot, registry, first, first + chunk.frame_count)
    profile = video_profile(job.profile).model_dump(mode="json", exclude={"id"})
    return {
        "version": "1",
        "kind": "video_chunk",
        "python": platform.python_version(),
        "pillow": PIL.__version__,
        "codecs": {name: features.version(name) for name in ("zlib", "jpg", "littlecms2")},
        "purpose": snapshot.purpose,
        "first_frame": first,
        "frame_count": chunk.frame_count,
        "fps": snapshot.episode.fps.model_dump(),
        "visual": visual,
        "compiler": snapshot.compiler.model_dump(),
        "prng": snapshot.prng.model_dump(),
        "pipeline": job.plan.pipeline.model_dump(),
        "backend": job.backend.model_dump(),
        "toolchain": job.plan.toolchain_fingerprint,
        "profile": profile,
    }
