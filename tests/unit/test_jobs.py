import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.jobs import JobOwnershipError, JobService
from tabi.core.jobs.ledger import revised
from tabi.core.models.base import Canvas
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectBusy, ProjectStore, StorageError, UnsafePath
from tabi.core.process import (
    ExecutionScope,
    OperationCancelled,
    ToolError,
    execution_scope,
    run_tool,
)
from tabi.core.timeline.compiler import ActionCompiler


@pytest.fixture
def queue(tmp_path, monkeypatch):
    root = tmp_path / "Queue's 東京"
    generate_fixtures(root)
    assets = AssetService(ProjectStore(root))
    snapshot = ActionCompiler(assets, purpose="synthetic_test").compile(
        assets.store.read("episodes/episode.synthetic.json")
    )
    digest = assets.store.save_snapshot(snapshot)
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    service = JobService(assets, settings)
    monkeypatch.setattr(
        "tabi.core.jobs.service.doctor",
        lambda *args: SimpleNamespace(
            ready=True,
            fingerprint="a" * 64,
            encoders=["libx264", "aac"],
        ),
    )
    profile = OutputProfile(
        id="test",
        canvas=Canvas(width=320, height=180),
        fps=snapshot.episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
    )
    return service, digest, profile


def test_queue_is_fifo_and_cancelled_work_never_starts(queue, monkeypatch):
    service, digest, profile = queue
    one = service.submit(digest, profile, "exports/one.mp4")
    two = service.submit(digest, profile, "exports/two.mp4")
    assert [job.id for job in service.ledger.all()] == [one.id, two.id]
    assert service.cancel(one.id).state == "cancelled"
    calls = []

    def failure(*args):
        calls.append(args)
        raise ToolError("injected owned process failure")

    monkeypatch.setattr("tabi.core.jobs.service.FFmpegRenderer.clip", failure)
    result = service.work()
    assert len(calls) == 1 and [job.id for job in result] == [two.id]
    assert result[0].state == "failed" and result[0].completed_frames == 0
    assert result[0].error.code == "process_failed"
    assert (
        service.store.root / result[0].error.log_path
    ).read_text() == "injected owned process failure"
    assert not list((service.store.root / "exports").iterdir())
    assert service.cancel(two.id) == result[0]


def test_pause_boundary_and_progress_exclude_paused_wall_time(queue, monkeypatch):
    service, digest, profile = queue
    now = [datetime(2026, 10, 4, tzinfo=UTC)]

    class Clock:
        @staticmethod
        def now(zone):
            return now[0]

    monkeypatch.setattr("tabi.core.jobs.ledger.datetime", Clock)
    monkeypatch.setattr("tabi.core.jobs.service.datetime", Clock)
    job = service.submit(digest, profile, "exports/paused.mp4")
    assert service.pause(job.id).state == "paused"
    assert service.work() == []
    assert service.progress(job.id)["elapsed_running_seconds"] == 0
    service.ledger.update(
        job.id, "started", lambda j: revised(j, state="running", owner=service.owner)
    )
    now[0] += timedelta(seconds=10)
    assert service._pause_at_boundary(job.id).state == "paused"
    now[0] += timedelta(hours=2)
    assert service.progress(job.id)["elapsed_running_seconds"] == 10
    service.ledger.update(
        job.id,
        "started",
        lambda j: revised(j, state="running", owner=service.owner, pause_requested=False),
    )
    now[0] += timedelta(seconds=5)
    assert service.progress(job.id)["elapsed_running_seconds"] == 15
    assert service.progress(job.id)["eta_seconds"] is None
    assert service._pause_at_boundary(job.id) is None
    service.cancel(job.id)
    with pytest.raises(OperationCancelled):
        service._pause_at_boundary(job.id)


def test_event_commit_survives_failed_checkpoint_and_recovery_is_idempotent(queue, monkeypatch):
    service, digest, profile = queue
    job = service.submit(digest, profile, "exports/recover.mp4")
    original = service.store._atomic_write

    def fail_checkpoint(relative, payload, **options):
        if relative == f"jobs/{job.id}.json":
            raise OSError("simulated interruption before checkpoint")
        return original(relative, payload, **options)

    monkeypatch.setattr(service.store, "_atomic_write", fail_checkpoint)
    with pytest.raises(OSError, match="before checkpoint"):
        service.ledger.update(
            job.id,
            "started",
            lambda value: revised(
                value,
                state="running",
                owner="previous-worker",
                chunks=[value.chunks[0].model_copy(update={"state": "rendering"})],
            ),
        )
    assert service.store.read(f"jobs/{job.id}.json").state == "queued"
    assert service.ledger.get(job.id).state == "running"
    monkeypatch.setattr(service.store, "_atomic_write", original)
    recovered = service.recover()
    assert len(recovered) == 1 and recovered[0].state == "interrupted"
    assert recovered[0].chunks[0].state == "pending" and recovered[0].owner is None
    assert service.recover() == []
    assert service.store.read(f"jobs/{job.id}.json") == recovered[0]


def test_journal_gap_and_modified_history_are_detected(queue):
    service, digest, profile = queue
    job = service.submit(digest, profile, "exports/journal.mp4")
    service.cancel(job.id)
    journal = service.store.root / "jobs/.journals" / job.id
    path = journal / "00000000.json"
    original = path.read_bytes()
    data = json.loads(original)
    data["kind"] = "altered-history"
    path.write_text(json.dumps(data))
    with pytest.raises(StorageError, match="hash chain"):
        service.ledger.get(job.id)
    path.write_bytes(original)
    path.unlink()
    with pytest.raises(StorageError, match="missing event"):
        service.ledger.get(job.id)


def test_lease_excludes_other_workers_but_allows_cancellation_requests(queue):
    service, digest, profile = queue
    job = service.submit(digest, profile, "exports/owned.mp4")
    service.ledger.update(
        job.id,
        "started",
        lambda value: revised(
            value,
            state="running",
            owner=service.owner,
        ),
    )
    other = JobService(service.assets, service.settings)
    with service.store.exclusive_lock(".tabi-worker.lock"):
        with pytest.raises(ProjectBusy):
            other.work()
        with pytest.raises(ProjectBusy):
            other.recover()
        assert other.cancel(job.id).cancel_requested
        assert service._cancelled(job.id)
        with pytest.raises(JobOwnershipError):
            other._cancelled(job.id)
    assert other.recover()[0].state == "interrupted"


def test_job_paths_reject_traversal_existing_outputs_and_symlink_parents(queue, tmp_path):
    service, digest, profile = queue
    for bad in ["../x.mp4", "assets/source.mp4", "exports/output.txt"]:
        with pytest.raises(ValueError):
            service.submit(digest, profile, bad)
    (service.store.root / "exports").mkdir()
    (service.store.root / "exports/existing.mp4").write_bytes(b"untouched")
    with pytest.raises(ValueError, match="already exists"):
        service.submit(digest, profile, "exports/existing.mp4")
    (service.store.root / "exports/escape").symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(UnsafePath):
        service.submit(digest, profile, "exports/escape/output.mp4")
    with pytest.raises(ValueError):
        service.cancel("../../other")
    assert (service.store.root / "exports/existing.mp4").read_bytes() == b"untouched"


def test_cancellation_reaps_only_its_live_child_and_leaves_other_scope_running():
    cancelled, started = threading.Event(), threading.Event()
    handles = []

    def observe(process):
        handles.append(process)
        started.set()

    def target():
        with execution_scope(ExecutionScope(cancelled.is_set, observe)):
            return run_tool([sys.executable, "-c", "import time; time.sleep(10)"], timeout=15)

    def unrelated():
        with execution_scope(ExecutionScope(lambda: False)):
            return run_tool([sys.executable, "-c", "import time; time.sleep(.5); print('intact')"])

    with ThreadPoolExecutor(max_workers=2) as pool:
        owned, other = pool.submit(target), pool.submit(unrelated)
        assert started.wait(3)
        cancelled.set()
        with pytest.raises(OperationCancelled):
            owned.result(timeout=5)
        assert other.result(timeout=5).strip() == b"intact"
    assert len(handles) == 1 and handles[0].poll() is not None


def test_real_worker_exit_recovers_without_signalling_saved_pids(queue):
    service, digest, profile = queue
    job = service.submit(digest, profile, "exports/crash.mp4")
    script = """
import os, sys
from tabi.core.jobs.ledger import JobLedger, revised
from tabi.core.persistence import ProjectStore
store = ProjectStore(__import__('pathlib').Path(sys.argv[1]))
with store.exclusive_lock('.tabi-worker.lock'):
    JobLedger(store).update(sys.argv[2], 'started', lambda job: revised(
        job, state='running', owner='crashed-worker'))
    os._exit(23)
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(service.store.root), job.id], check=False
    )
    assert result.returncode == 23
    assert service.recover()[0].error.code == "worker_interrupted"


def test_worker_rejects_changed_inputs_before_rendering(queue, monkeypatch):
    service, digest, profile = queue
    job = service.submit(digest, profile, "exports/changed.mp4")
    (service.store.root / "assets/fixture.idle/000000.png").write_bytes(b"changed")

    def unexpected(*args):
        pytest.fail("changed frozen input reached the renderer")

    monkeypatch.setattr("tabi.core.jobs.service.FFmpegRenderer.clip", unexpected)
    result = service.work()[0]
    assert result.id == job.id and result.state == "failed"
    assert result.completed_frames == 0 and result.error.code == "render_failed"


def test_journal_hot_reads_validate_metadata_and_replay_only_new_events(queue, monkeypatch):
    from tabi.core.jobs.ledger import JobLedger

    service, digest, profile = queue
    job = service.submit(digest, profile, "exports/incremental.mp4", max_chunk_frames=3)
    for n in range(20):
        service.ledger.update(job.id, "observed", lambda j, n=n: revised(j, owner=f"test-{n}"))
    reads = []
    original = service.store._read_at

    def read(directory, name):
        reads.append(name)
        return original(directory, name)

    monkeypatch.setattr(service.store, "_read_at", read)
    assert service.ledger.get(job.id).owner == "test-19"
    assert reads == ["00000020.json"]
    reads.clear()
    for _ in range(5):
        # Even mutating a returned nested list must not alter the verified cache.
        result = service.ledger.get(job.id)
        assert len(result.chunks) == 100
        result.chunks.clear()
        assert service.progress(job.id)["job"].owner == "test-19"
    assert not reads
    # Another service/process can append and be observed on the next poll.
    other = JobLedger(ProjectStore(service.store.root))
    other.update(job.id, "changed", lambda j: revised(j, owner="another-reader"))
    assert service.ledger.get(job.id).owner == "another-reader"
    assert reads == ["00000021.json"]
    # The atomic checkpoint is still only a convenience copy, never authority.
    (service.store.root / f"jobs/{job.id}.json").write_bytes(b"broken checkpoint")
    assert service.ledger.get(job.id).owner == "another-reader"
    assert JobLedger(service.store).get(job.id).owner == "another-reader"


def test_changed_cached_history_cannot_hide_behind_preserved_mtime(queue):
    service, digest, profile = queue
    job = service.submit(digest, profile, "exports/stat-check.mp4")
    service.cancel(job.id)
    service.ledger.get(job.id)
    path = service.store.root / f"jobs/.journals/{job.id}/00000000.json"
    before = path.stat()
    data = path.read_bytes()
    assert b'"kind":"queued"' in data
    path.write_bytes(data.replace(b'"kind":"queued"', b'"kind":"edited"'))
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
    with pytest.raises(StorageError, match="hash chain"):
        service.ledger.get(job.id)
