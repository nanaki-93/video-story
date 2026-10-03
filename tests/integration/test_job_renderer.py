import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from tabi.cli.main import main
from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import file_hash, generate_fixtures
from tabi.core.jobs import JobService
from tabi.core.models.base import Canvas
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore
from tabi.core.timeline.compiler import ActionCompiler

pytestmark = pytest.mark.media


def queue(tmp_path, *, effects=False):
    root = tmp_path / "Jobs' 東京 project"
    generate_fixtures(root, profile="effects" if effects else "story")
    assets = AssetService(ProjectStore(root))
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(
        assets.store.read("episodes/episode.synthetic.json")
    )
    digest = assets.store.save_snapshot(snapshot)
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    service = JobService(assets, settings)
    profile = OutputProfile(
        id="test",
        canvas=Canvas(width=640, height=360),
        fps=snapshot.episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
        audio_codec="aac",
    )
    return service, digest, profile


def test_cli_job_renders_real_global_interval_and_commits_verified_artifacts(tmp_path, capsys):
    service, digest, _ = queue(tmp_path)
    project = ["--project", str(service.store.root)]
    assert (
        main(
            [
                "jobs",
                "submit",
                digest,
                *project,
                "--output",
                "exports/verified 東京.mp4",
                "--start",
                "140",
                "--end",
                "186",
                "--width",
                "640",
                "--height",
                "360",
            ]
        )
        == 0
    )
    submitted = json.loads(capsys.readouterr().out)
    assert submitted["state"] == "queued"
    assert main(["jobs", "work", *project, "--once"]) == 0
    completed = json.loads(capsys.readouterr().out)[0]
    job = service.ledger.get(submitted["id"])
    assert completed["state"] == job.state == "verified"
    assert job.first_frame == 140 and job.completed_frames == 46
    assert service.store.read(job.chunks[0].report_path).audio_verification is None
    assert file_hash(service.store.root / job.output.location.path) == job.output.sha256
    report = service.store.read(job.report_path)
    assert report.first_frame == 140 and report.frame_count == 46
    assert report.audio_verification.intended_samples == 73600
    assert report.full_decode_passed and report.timestamps_verified
    assert report.output == str(service.store.root / job.destination)
    assert [event.kind for event in service.ledger.events(job.id)] == [
        "queued",
        "started",
        "toolchain_locked",
        "chunk_started",
        "chunk_verified",
        "assembly_verified",
        "verified",
    ]
    assert main(["jobs", "events", job.id, *project]) == 0
    assert json.loads(capsys.readouterr().out)[-1]["job"]["state"] == "verified"


@pytest.mark.parametrize("stage", ["before", "after", "conflict"])
def test_actual_worker_crash_retains_verified_video_and_continuous_audio(tmp_path, stage):
    service, digest, profile = queue(tmp_path)
    job = service.submit(digest, profile, "exports/after-crash.mp4", first_frame=140, end_frame=186)
    script = """
import os, sys
from pathlib import Path
from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.jobs import JobService
from tabi.core.persistence import ProjectStore
settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
service = JobService(AssetService(ProjectStore(Path(sys.argv[1]))), settings)
original = service._publish
def crash(source, destination):
    if sys.argv[2] != 'before':
        original(source, destination)
    os._exit(29)
service._publish = crash
service.work()
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(service.store.root), stage], check=False, timeout=60
    )
    assert result.returncode == 29
    previous = service.ledger.get(job.id)
    assert previous.state == "running" and previous.completed_frames == 46
    artifact = service.store.root / previous.chunks[0].output.location.path
    digest_before = file_hash(artifact)
    recovered = service.recover()[0]
    assert recovered.state == "interrupted" and recovered.completed_frames == 46
    assert recovered.chunks[0].state == "verified"
    assert file_hash(artifact) == digest_before == recovered.chunks[0].output.sha256
    assert service.store.read(recovered.report_path).audio_verification.intended_samples == 73600
    destination = service.store.root / job.destination
    assert destination.exists() == (stage != "before")
    if stage == "conflict":
        destination.write_bytes(b"existing user export must be preserved")
    assert service.resume(job.id).completed_frames == 46
    graphs = []
    service.on_process = lambda process: (
        graphs.append(process) if "-/filter_complex" in process.args else None
    )
    result = service.work()[0]
    assert graphs == []  # Retained verified video is never rendered again.
    if stage == "conflict":
        assert result.state == "failed" and "preserved" in result.error.message
        assert destination.read_bytes() == b"existing user export must be preserved"
    else:
        assert result.state == "verified", result.error
        assert file_hash(destination) == result.output.sha256
    assert file_hash(artifact) == digest_before


def test_pause_during_actual_chunk_then_resume_keeps_verified_media(tmp_path):
    service, digest, profile = queue(tmp_path)
    sources = {p: file_hash(p) for p in service.store.root.rglob("*.wav")}
    job = service.submit(digest, profile, "exports/paused.mp4", end_frame=90, max_chunk_frames=30)
    requested = []

    def pause(process):
        if "-/filter_complex" in process.args and not requested:
            requested.append(service.pause(job.id))

    service.on_process = pause
    result = service.work(once=True)[0]
    assert requested and result.state == "paused" and result.owner is None
    assert result.completed_frames == 30
    retained = result.chunks[0].output
    assert file_hash(service.store.root / retained.location.path) == retained.sha256
    assert not (service.store.root / result.destination).exists()
    service.on_process = None
    assert service.resume(job.id).completed_frames == 30
    result = service.work(once=True)[0]
    assert result.state == "verified", result.error
    assert result.chunks[0].output == retained
    assert service.store.read(result.report_path).audio_verification.intended_samples == 144000
    assert service.progress(job.id)["measured_fps"] > 0
    assert all(file_hash(p) == h for p, h in sources.items())


def test_cancel_running_ffmpeg_job_preserves_other_process_and_sources(tmp_path):
    service, digest, profile = queue(tmp_path, effects=True)
    job = service.submit(digest, profile, "exports/cancelled.mp4")
    source = service.store.root / "assets/fixture.idle/000000.png"
    original_hash = file_hash(source)
    started, children = threading.Event(), []

    def observe(process):
        if "-/filter_complex" in process.args:
            children.append(process)
            started.set()

    service.on_process = observe
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(service.work)
            assert started.wait(15)
            controller = JobService(service.assets, service.settings)
            assert controller.cancel(job.id).cancel_requested
            result = future.result(timeout=15)[0]
        assert result.state == "cancelled" and result.completed_frames == 0
        assert children and all(child.poll() is not None for child in children)
        assert unrelated.poll() is None
        assert not (service.store.root / job.destination).exists()
        assert not list((service.store.root / "jobs/artifacts" / job.id).glob("*.mp4"))
        assert not list((service.store.root / "jobs/artifacts" / job.id).glob(".tabi-render-*"))
        assert file_hash(source) == original_hash
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)
