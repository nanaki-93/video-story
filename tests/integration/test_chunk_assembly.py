import os
from pathlib import Path

import numpy as np
import pytest

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import file_hash, generate_fixtures
from tabi.core.jobs import JobService
from tabi.core.models import ActionPack, Asset, Episode
from tabi.core.models.base import Canvas, FrameRate
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore
from tabi.core.process import run_tool
from tabi.core.render import assembly
from tabi.core.render.backend import RenderError
from tabi.core.render.ffmpeg import FFmpegRenderer
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


def setup(tmp_path, fixture="story", *, fractional=False):
    root = tmp_path / "Chunks' 東京 project"
    generate_fixtures(root, profile=fixture)
    assets = AssetService(ProjectStore(root))
    episode = assets.store.read("episodes/episode.synthetic.json")
    if fractional:
        rate = FrameRate(num=30000, den=1001)
        for path in (root / "registry/assets").glob("*/*.json"):
            asset = assets.store.read(path.relative_to(root).as_posix())
            if asset.kind == "sequence":
                data = asset.model_dump(mode="json")
                data["probe"]["fps"] = rate.model_dump()
                assets.store.save_draft(
                    Asset.model_validate(data), expected_revision=asset.revision
                )
        pack = assets.store.read("registry/actions/pack.synthetic/1.0.json")
        assets.store.save_draft(
            ActionPack.model_validate({**pack.model_dump(), "fps": rate}),
            expected_revision=pack.revision,
        )
        data = episode.model_dump(mode="json")
        data.update(duration_frames=72, fps=rate.model_dump())
        data["scenes"][0].update(end_frame=72, final_state=None)
        data["actions"] = [{**data["actions"][0], "end_frame": 72}, data["actions"][5]]
        data["curves"][0]["keys"] = [{"frame": 0, "value": 60}, {"frame": 72, "value": 60}]
        data["events"][0]["end_frame"] = 72
        data["tracks"][0]["trim_end_sample"] = rate.sample_at(72)
        episode = Episode.model_validate(data)
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(episode)
    digest = assets.store.save_snapshot(snapshot)
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    service = JobService(assets, settings)
    profile = OutputProfile(
        id="test",
        canvas=Canvas(width=640, height=360),
        fps=episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
        audio_codec="aac",
    )
    return service, snapshot, digest, profile


def sampled_video(settings, path, frames):
    select = "+".join(f"eq(n\\,{frame})" for frame in frames)
    raw = run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-i",
            str(path),
            "-an",
            "-vf",
            f"select={select},scale=in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
            "-fps_mode",
            "passthrough",
            "-f",
            "rawvideo",
            "-",
        ],
        max_bytes=len(frames) * 640 * 360 * 3,
    )
    return np.frombuffer(raw, dtype=np.uint8).reshape(len(frames), 360, 640, 3).astype(np.int16)


def audio(settings, path, samples):
    raw = run_tool(
        [
            settings.ffmpeg,
            "-v",
            "error",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-f",
            "f32le",
            "-c:a",
            "pcm_f32le",
            "-",
        ],
        max_bytes=(samples + 1024) * 8,
    )
    return np.frombuffer(raw, dtype="<f4").reshape(-1, 2)[:samples]


@pytest.mark.parametrize("fixture", ["story", "effects"])
def test_chunked_frames_and_one_aac_encode_match_monolithic_global_range(tmp_path, fixture):
    service, snapshot, digest, profile = setup(tmp_path, fixture)
    encoded_audio = []

    def observe(process):
        if "-c:a" in process.args and process.args[process.args.index("-c:a") + 1] == "aac":
            encoded_audio.append(process.args)

    service.on_process = observe
    job = service.submit(
        digest, profile, "exports/chunked.mp4", first_frame=32, end_frame=280, max_chunk_frames=71
    )
    completed = service.work()[0]
    assert completed.state == "verified", completed.error
    assert len(encoded_audio) == 1
    assert [chunk.frame_count for chunk in completed.chunks] == [71, 71, 71, 35]
    for chunk in completed.chunks:
        assert service.store.read(chunk.report_path).audio_mix is None
    result = service.store.root / completed.destination
    report = service.store.read(completed.report_path)
    assert report.audio_verification.intended_samples == 396800
    assert report.assembly.mode == "stream_copy"
    monolithic = tmp_path / "monolithic.mp4"
    FFmpegRenderer(service.assets, service.settings).clip(snapshot, 32, 280, monolithic, profile)
    global_frames = [
        35,
        36,
        41,
        42,
        83,
        84,
        89,
        90,
        102,
        103,
        143,
        144,
        149,
        150,
        151,
        173,
        174,
        178,
        179,
        180,
        209,
        210,
        215,
        216,
        244,
        245,
        269,
        270,
        275,
        276,
        279,
    ]
    frames = [frame - 32 for frame in global_frames]
    diff = np.abs(
        sampled_video(service.settings, result, frames)
        - sampled_video(service.settings, monolithic, frames)
    )
    assert np.quantile(diff, 0.999) <= 15
    actual_audio, expected_audio = (
        audio(service.settings, result, 396800),
        audio(service.settings, monolithic, 396800),
    )
    assert np.sqrt(np.mean((actual_audio - expected_audio) ** 2)) < 0.0001
    assert np.corrcoef(actual_audio[:, 0], expected_audio[:, 0])[0, 1] > 0.9999
    assert job.snapshot_sha256 == report.snapshot_sha256


def test_resume_restores_corrupt_job_chunk_from_independent_verified_cache(tmp_path):
    service, _, digest, profile = setup(tmp_path)
    job = service.submit(digest, profile, "exports/resumed.mp4", max_chunk_frames=77)
    graph_count = []

    def cancel_third(process):
        if "-/filter_complex" in process.args:
            graph_count.append(process)
            if len(graph_count) == 3:
                service.cancel(job.id)

    service.on_process = cancel_third
    interrupted = service.work()[0]
    assert interrupted.state == "cancelled" and interrupted.completed_frames == 154
    first, second = interrupted.chunks[:2]
    corrupt = service.store.root / first.output.location.path
    retained = service.store.root / second.output.location.path
    retained_mtime = retained.stat().st_mtime_ns
    corrupt_size = corrupt.stat().st_size // 2
    with corrupt.open("r+b") as stream:
        stream.truncate(corrupt_size)
    queued = service.resume(job.id)
    assert queued.completed_frames == 77 and queued.error.code == "chunk_invalidated"
    assert queued.chunks[1] == second
    graph_count.clear()
    service.on_process = lambda process: (
        graph_count.append(process) if "-/filter_complex" in process.args else None
    )
    completed = service.work()[0]
    assert completed.state == "verified" and completed.completed_frames == 300, completed.error
    assert len(graph_count) == 2
    assert service.store.read(completed.chunks[0].report_path).cache_reuse is not None
    assert retained.stat().st_mtime_ns == retained_mtime
    assert file_hash(retained) == second.output.sha256
    assert corrupt.stat().st_size == corrupt_size
    assert completed.chunks[0].output.location.path != first.output.location.path
    assert service.store.read(completed.report_path).audio_verification.intended_samples == 480000


@pytest.mark.parametrize("fallback", [False, True])
def test_rational_fps_chunk_assembly_and_verified_reencode_fallback(
    tmp_path, monkeypatch, fallback
):
    service, _, digest, profile = setup(tmp_path, "core", fractional=True)
    if fallback:
        original = assembly.verify_video
        calls = []

        def fail_first_copy(settings, path, profile, frames):
            original(settings, path, profile, frames)
            if path.name == "assembled-video.mp4" and not calls:
                calls.append(path)
                raise RenderError("injected stream-copy timestamp rejection")

        monkeypatch.setattr(assembly, "verify_video", fail_first_copy)
    service.submit(digest, profile, "exports/rational.mp4", max_chunk_frames=37)
    completed = service.work()[0]
    assert completed.state == "verified", completed.error
    report = service.store.read(completed.report_path)
    assert report.frame_count == 72 and report.fps == FrameRate(num=30000, den=1001)
    assert report.audio_verification.intended_samples == 115315
    assert report.assembly.mode == ("reencode" if fallback else "stream_copy")
    if fallback:
        assert "injected" in report.assembly.fallback_reason
    assert report.full_decode_passed and report.timestamps_verified
