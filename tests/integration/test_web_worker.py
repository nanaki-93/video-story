import hashlib
import json
import time
from pathlib import Path

import httpx
import pytest

from tabi.api.launcher import OwnedWorker
from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.episodes import EpisodeService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models.base import Canvas
from tabi.core.models.production import OutputProfile
from tabi.core.persistence import ProjectStore
from tabi.core.render.profiles import preset_profile

pytestmark = pytest.mark.media
REPO = Path(__file__).resolve().parents[2]


def wait_for(worker, path, condition, *, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = worker.request("GET", path)
        if condition(result):
            return result
        assert result["state"] not in {"failed", "cancelled"}, result.get("error")
        time.sleep(0.1)
    raise AssertionError("owned HTTP job did not reach the expected state")


def test_live_worker_render_cookie_ranges_sse_disconnect_shutdown_and_resume(tmp_path):
    project = tmp_path / "HTTP's 東京"
    generate_fixtures(project, profile="story")
    settings = load_settings(REPO / "examples/settings.macos.toml", env={}, cwd=REPO, home=tmp_path)
    assets = AssetService(ProjectStore(project), ffmpeg=settings.ffmpeg, ffprobe=settings.ffprobe)
    service = EpisodeService(assets, settings)
    episode = assets.store.read("episodes/episode.synthetic.json")
    snapshot = service.compile(episode, purpose="synthetic_test")
    profile = OutputProfile.model_validate(
        {
            **preset_profile("proxy", fps=episode.fps).model_dump(),
            "canvas": Canvas(width=320, height=180),
        }
    )
    sources = {
        path: hashlib.sha256(path.read_bytes()).hexdigest() for path in project.rglob("*.wav")
    }
    worker = OwnedWorker(settings, {"fixtures": tmp_path}, REPO / "web/dist")
    next_worker = None
    try:
        opened = worker.request(
            "POST", "/api/v1/projects/open", {"root_id": "fixtures", "path": project.name}
        )
        path = f"/api/v1/projects/{opened['handle']}/jobs"
        with httpx.Client(base_url=worker.origin, timeout=30) as browser:
            # Actual cookie exchange, including the Origin sent by a same-origin browser.
            response = browser.post(
                "/api/v1/bootstrap",
                json={"protocol": "1", "secret": worker.ready.bootstrap},
                headers={"Origin": worker.origin},
            )
            assert response.status_code == 200
            assert worker.ready.bootstrap not in response.text
            assert browser.get("/api/v1/session").status_code == 200
            headers = {"Origin": worker.origin, "X-Tabi-CSRF": response.json()["csrf"]}
            body = {
                "snapshot_sha256": snapshot.snapshot_sha256,
                "profile": profile.model_dump(mode="json"),
                "destination": "exports/http-owned.mp4",
                "max_chunk_frames": 30,
            }
            submitted = browser.post(path, json=body, headers=headers)
            assert submitted.status_code == 200, submitted.text
            job_id = submitted.json()["id"]
            status = f"{path}/{job_id}"
            started = time.monotonic()
            assert browser.get("/api/v1/session").status_code == 200
            assert time.monotonic() - started < 2
            with browser.stream("GET", f"{status}/events") as response:
                assert response.status_code == 200
                first = next(line for line in response.iter_lines() if line.startswith("id:"))
                assert first == "id: 0"
            with browser.stream(
                "GET", f"{status}/events", headers={"Last-Event-ID": "0"}
            ) as response:
                resumed = next(line for line in response.iter_lines() if line.startswith("id:"))
                assert int(resumed[3:]) > 0
            assert len(browser.get(path).json()["jobs"]) == 1
        # Closing the client has no job cancellation effect.
        partial = wait_for(
            worker, status, lambda job: job["completed_frames"] >= 30 and job["state"] == "running"
        )
        worker.stop(cancel=True)
        retained = assets.store.read(f"jobs/{job_id}.json")
        assert (
            retained.state == "cancelled"
            and retained.completed_frames >= partial["completed_frames"]
        )
        preserved = [chunk.output.sha256 for chunk in retained.chunks if chunk.state == "verified"]
        next_worker = OwnedWorker(settings, {"fixtures": tmp_path}, REPO / "web/dist")
        reopened = next_worker.request(
            "POST", "/api/v1/projects/open", {"root_id": "fixtures", "path": project.name}
        )
        assert reopened["handle"] == opened["handle"]
        next_worker.request("POST", f"{status}/resume")
        complete = wait_for(next_worker, status, lambda job: job["state"] == "verified")
        assert complete["completed_frames"] == episode.duration_frames
        assert [
            chunk["output"]["sha256"] for chunk in complete["chunks"][: len(preserved)]
        ] == preserved
        with httpx.Client(base_url=next_worker.origin, timeout=30) as browser:
            assert browser.get(f"{status}/video").status_code == 401
            response = browser.post(
                "/api/v1/bootstrap",
                json={"protocol": "1", "secret": next_worker.ready.bootstrap},
                headers={"Origin": next_worker.origin},
            )
            assert response.status_code == 200
            for bounds in ("bytes=0-1", "bytes=-32"):
                media = browser.get(f"{status}/video", headers={"Range": bounds})
                assert media.status_code == 206 and media.headers["content-type"] == "video/mp4"
            assert browser.head(f"{status}/video").status_code == 200
            assert (
                browser.get(
                    f"{status}/events", headers={"Origin": "https://foreign.example"}
                ).status_code
                == 403
            )
        from tabi.core.jobs import JobService

        verified = JobService(assets, settings).verify_export(job_id)
        assert verified.video.frame_count == episode.duration_frames
        assert verified.audio.decoded_samples == episode.fps.sample_at(episode.duration_frames)
        assert all(
            hashlib.sha256(path.read_bytes()).hexdigest() == digest
            for path, digest in sources.items()
        )
        assert len(next_worker.request("GET", path)["jobs"]) == 1
        (tmp_path / "web-verification.json").write_text(
            json.dumps(
                {
                    "verification": verified.model_dump(mode="json"),
                    "retained_verified_chunks": len(preserved),
                    "source_masters_unchanged": True,
                    "sse_first_event": first,
                    "sse_resumed_event": resumed,
                    "browser_disconnect_did_not_cancel": True,
                    "session_responded_during_render_under_seconds": 2,
                },
                indent=2,
            )
            + "\n"
        )
        print(
            json.dumps(
                {
                    "frames": verified.video.frame_count,
                    "retained_chunks": len(preserved),
                    "video_sha256": verified.output.sha256,
                    "source_masters_unchanged": True,
                }
            )
        )
    finally:
        worker.stop()
        if next_worker:
            next_worker.stop()
