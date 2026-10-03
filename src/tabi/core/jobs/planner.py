"""Exact bounded video ranges; all supported filters have zero temporal history."""

import hashlib
from fractions import Fraction
from pathlib import Path

from ..models.base import content_hash
from ..models.production import ChunkPlan, ChunkRecord, Fingerprint, OutputProfile


def pipeline_fingerprint():
    root = Path(__file__).parents[1]
    digest = hashlib.sha256()
    for source in sorted(root.rglob("*.py")):
        digest.update(source.relative_to(root).as_posix().encode() + b"\0" + source.read_bytes())
    return Fingerprint(name="tabi-core-pipeline", version="1", sha256=digest.hexdigest())


def plan_chunks(snapshot, profile, first, end, *, max_frames=None):
    if (
        type(first) is not int
        or type(end) is not int
        or not 0 <= first < end <= snapshot.episode.duration_frames
    ):
        raise ValueError("chunk plan interval must be inside the frozen episode")
    profile = OutputProfile.model_validate(profile)
    if profile.fps != snapshot.episode.fps:
        raise ValueError("chunk profile fps must match its snapshot")
    if max_frames is None:
        max_frames = min(7200, max(1, round(Fraction(30 * profile.fps.num, profile.fps.den))))
    if type(max_frames) is not int or not 1 <= max_frames <= 7200:
        raise ValueError("chunk size must be an integer from 1 to 7200 frames")
    cuts = {
        scene.start_frame
        for scene in snapshot.episode.scenes
        if scene.transition_in.kind == "cut" and first < scene.start_frame < end
    }
    chunks, cursor = [], first
    while cursor < end:
        stop = min(end, cursor + max_frames)
        # Prefer a real scene cut in the last half of a full chunk. Short final
        # remainders are allowed. Overlaps can be split: rendering uses global time.
        if stop < end:
            candidates = [
                cut for cut in cuts if cursor < cut and cursor + max_frames // 2 <= cut <= stop
            ]
            if candidates:
                stop = max(candidates)
        chunks.append(
            ChunkRecord(
                index=len(chunks),
                first_frame=cursor - first,
                frame_count=stop - cursor,
                state="pending",
            )
        )
        cursor = stop
    return ChunkPlan(
        pipeline=pipeline_fingerprint(),
        profile_sha256=content_hash(profile),
        max_chunk_frames=max_frames,
    ), chunks


def video_profile(profile):
    return OutputProfile.model_validate(
        {**profile.model_dump(), "audio_codec": None, "audio_gain_db": 0, "audio_bitrate": 192000}
    )
