import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.jobs import JobService
from tabi.core.jobs.ledger import revised
from tabi.core.jobs.planner import plan_chunks
from tabi.core.models import Episode
from tabi.core.models.base import Canvas, FrameRate
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore
from tabi.core.timeline.compiler import ActionCompiler


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    generate_fixtures(tmp_path / "plan", profile="story")
    assets = AssetService(ProjectStore(tmp_path / "plan"))
    episode = assets.store.read("episodes/episode.synthetic.json")
    compiler = ActionCompiler(assets, purpose="synthetic_test")
    snapshot = compiler.compile(episode)
    profile = OutputProfile(
        id="test",
        canvas=Canvas(width=640, height=360),
        fps=episode.fps,
        container="mp4",
        video_codec="libx264",
        pixel_format="yuv420p",
        color_space="bt709",
    )
    settings = load_settings(None, env=os.environ, cwd=Path.cwd(), home=Path.home())
    service = JobService(assets, settings)
    monkeypatch.setattr(
        "tabi.core.jobs.service.doctor",
        lambda *args: SimpleNamespace(
            ready=True, fingerprint="a" * 64, encoders=["libx264", "aac"]
        ),
    )
    return compiler, snapshot, profile, service


def test_planner_prefers_real_cuts_preserving_exact_nonzero_global_range(inputs):
    compiler, snapshot, profile, _ = inputs
    data = snapshot.episode.model_dump(mode="json")
    data["scenes"][0].update(final_state=None, transition_out={"kind": "cut"})
    data["scenes"][1].update(start_frame=180, transition_in={"kind": "cut"}, final_state=None)
    data["scenes"][1]["initial_state"]["travel_distance_px"] = 300
    data["actions"][1]["start_frame"] = 180
    data["beats"] = []
    snapshot = compiler.compile(Episode.model_validate(data))
    plan, chunks = plan_chunks(snapshot, profile, 17, 299, max_frames=100)
    assert plan.temporal_handles == 0
    assert [(17 + c.first_frame, 17 + c.first_frame + c.frame_count) for c in chunks] == [
        (17, 117),
        (117, 180),
        (180, 280),
        (280, 299),
    ]
    assert all(c.frame_count <= 100 for c in chunks)
    _, singles = plan_chunks(snapshot, profile, 179, 182, max_frames=1)
    assert [c.frame_count for c in singles] == [1, 1, 1]


def test_overlap_splits_do_not_move_authored_timing(inputs):
    _, snapshot, profile, _ = inputs
    _, chunks = plan_chunks(snapshot, profile, 140, 186, max_frames=12)
    assert [(c.first_frame, c.frame_count) for c in chunks] == [
        (0, 12),
        (12, 12),
        (24, 12),
        (36, 10),
    ]
    assert snapshot.episode.scenes[1].start_frame == 144


def test_long_plan_and_noninteger_rate_have_no_rounding_drift(inputs):
    compiler, snapshot, profile, _ = inputs
    data = snapshot.episode.model_dump(mode="json")
    data["duration_frames"] = 30000
    data["scenes"] = [data["scenes"][0]]
    data["scenes"][0].update(end_frame=30000, final_state=None, transition_out={"kind": "cut"})
    data["actions"] = [data["actions"][0]]
    data["actions"][0]["end_frame"] = 30000
    data["beats"] = []
    extended = compiler.compile(Episode.model_validate(data))
    rate = FrameRate(num=30000, den=1001)
    # Only planning arithmetic is under test; real-rate media normalization has a media test.
    extended = extended.model_copy(
        update={"episode": extended.episode.model_copy(update={"fps": rate})}
    )
    profile = profile.model_copy(update={"fps": rate})
    plan, chunks = plan_chunks(extended, profile, 0, 30000)
    assert plan.max_chunk_frames == 899
    assert sum(chunk.frame_count for chunk in chunks) == 30000
    assert rate.sample_at(sum(c.frame_count for c in chunks)) == 48048000
    assert all(
        a.first_frame + a.frame_count == b.first_frame
        for a, b in zip(chunks, chunks[1:], strict=False)
    )


@pytest.mark.parametrize("size", [0, -1, True, 7201, 1.5])
def test_unbounded_or_noninteger_chunk_sizes_fail(inputs, size):
    _, snapshot, profile, _ = inputs
    with pytest.raises(ValueError, match="chunk size"):
        plan_chunks(snapshot, profile, 0, 300, max_frames=size)


@pytest.mark.parametrize("change", ["pipeline", "profile", "toolchain", "source"])
def test_resume_rejects_stale_dependencies_without_rewriting_artifacts(inputs, monkeypatch, change):
    _, snapshot, profile, service = inputs
    digest = service.store.save_snapshot(snapshot)
    job = service.submit(digest, profile, "exports/stale.mp4", max_chunk_frames=77)
    service.cancel(job.id)
    if change == "pipeline":
        monkeypatch.setattr(
            "tabi.core.jobs.service.pipeline_fingerprint",
            lambda: job.plan.pipeline.model_copy(update={"sha256": "b" * 64}),
        )
    elif change == "profile":
        service.ledger.update(
            job.id,
            "invalid-edit",
            lambda current: revised(
                current, profile=current.profile.model_copy(update={"audio_gain_db": -6})
            ),
        )
    elif change == "toolchain":
        service.ledger.update(
            job.id,
            "old-tools",
            lambda current: revised(
                current, plan=current.plan.model_copy(update={"toolchain_fingerprint": "b" * 64})
            ),
        )
    else:
        (service.store.root / "assets/fixture.idle/000000.png").write_bytes(b"changed")
    with pytest.raises(ValueError):
        service.resume(job.id)
    assert service.ledger.get(job.id).state == "cancelled"
    assert not (service.store.root / "jobs/artifacts").exists()


def test_cancelled_pending_job_requeues_with_same_frozen_ranges(inputs):
    _, snapshot, profile, service = inputs
    digest = service.store.save_snapshot(snapshot)
    job = service.submit(
        digest, profile, "exports/resumed.mp4", first_frame=140, end_frame=186, max_chunk_frames=12
    )
    service.cancel(job.id)
    resumed = service.resume(job.id)
    assert resumed.state == "queued" and not resumed.cancel_requested
    assert resumed.chunks == job.chunks and resumed.snapshot_sha256 == digest
    assert resumed.plan.toolchain_fingerprint == "a" * 64
