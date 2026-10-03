"""Conservative additional-space estimate for one frozen render job."""

import math
import shutil

from ..audio.timeline import prepared_samples
from ..models import Asset
from ..models.base import content_hash
from ..models.cache import StorageEstimate
from ..render.backend import FrozenRegistry
from .keys import image_descriptor, video_descriptor, visual_inputs
from .store import CacheStore


def estimate_storage(assets, job):
    snapshot = assets.store.read_snapshot(job.snapshot_sha256)
    registry = FrozenRegistry(assets, snapshot)
    cache = CacheStore(assets.store)
    first, end = job.first_frame, job.first_frame + job.duration_frames
    _, refs = visual_inputs(snapshot, registry, first, end)
    normalization, seen = 0, set()
    for ref in sorted(refs):
        asset = registry.documents[ref]
        if not isinstance(asset, Asset) or asset.kind not in {"still", "mask", "sequence"}:
            continue
        canvas = asset.compatibility.crop or asset.probe.canvas
        for frame in range(len(asset.files)):
            descriptor = image_descriptor(asset, frame, snapshot.purpose)
            key = content_hash(descriptor)
            if key not in seen and cache.lookup("normalized_image", descriptor) is None:
                channels = 1 if asset.kind == "mask" else 4
                # PNG can be larger than raw input: include scanline/container
                # overhead, then independent scratch and persistent cache copies.
                normalization += 2 * math.ceil(
                    (canvas.width * canvas.height * channels + canvas.height + 4096) * 1.02
                )
            seen.add(key)
    fps = job.profile.fps.num / job.profile.fps.den
    seconds = job.duration_frames / fps
    bitrate = job.profile.video_bitrate or max(
        2_000_000, math.ceil(job.profile.canvas.width * job.profile.canvas.height * fps * 0.5)
    )
    total_video = math.ceil(seconds * bitrate / 8 * 1.5) + 1024 * 1024
    chunk_space = 0
    for chunk in job.chunks:
        entry = (
            cache.lookup("video_chunk", video_descriptor(snapshot, registry, job, chunk))
            if job.plan and job.plan.toolchain_fingerprint
            else None
        )
        # A hit is copied into the job. New chunks also populate an independent cache.
        chunk_space += (
            entry.output.size_bytes
            if entry
            else 2 * (math.ceil(total_video * chunk.frame_count / job.duration_frames) + 65536)
        )
    # Assembly/reencode and final mux may coexist. Published files are same-volume links.
    video = chunk_space + 2 * total_video
    audio = 0
    if job.profile.audio_codec:
        samples = job.profile.fps.sample_at(end) - job.profile.fps.sample_at(first)
        audio = samples * 24 + math.ceil(seconds * 192_000 / 8 * 1.5) + 65536
        source_refs = {(p.asset.id, p.asset.version) for p in snapshot.audio_placements}
        for ref in source_refs:
            asset = registry.documents[ref]
            audio += sum(f.size_bytes for f in asset.files)
            if asset.probe.sample_rate != 48000:
                audio += prepared_samples(asset) * asset.probe.channels * 8
    subtotal = normalization + video + audio
    reserve = max(256 * 1024 * 1024, math.ceil(subtotal * 0.1))
    free = shutil.disk_usage(assets.store.root).free
    return StorageEstimate(
        schema_version="1.0",
        snapshot_sha256=job.snapshot_sha256,
        first_frame=first,
        frame_count=job.duration_frames,
        profile=job.profile,
        available_bytes=free,
        normalization_bytes=normalization,
        video_bytes=video,
        audio_bytes=audio,
        reserve_bytes=reserve,
        required_additional_bytes=subtotal + reserve,
        sufficient=free >= subtotal + reserve,
        assumptions=[
            "Additional bytes on the project volume; original media, snapshots and existing "
            "jobs are retained.",
            "Video uses target bitrate or 0.5 bits/pixel/frame (minimum 2 Mbit/s), plus 50% "
            "headroom; encoded size is an estimate, not a bound.",
            "Includes video chunks/cache copies, assembly/fallback and mux; normalized "
            "scratch links share verified cache bytes on this volume.",
            "Audio includes master copies, resampled float64 sources, continuous PCM and "
            "decode buffers; output AAC is encoded once.",
            "Reserve is at least 256 MiB or 10% of the estimate. Other processes can "
            "consume space after this check.",
        ],
    )
