from pathlib import Path

from fastapi.testclient import TestClient

from tabi.api.app import create_app
from tabi.api.runtime import Runtime
from tabi.core.config import load_settings
from tabi.core.fixtures import generate_fixtures
from tabi.core.jobs.ledger import revised


def test_export_plan_is_not_queued_and_http_pause_respects_ownership(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    generate_fixtures(tmp_path / "preview")
    settings = load_settings(None, env={}, cwd=tmp_path, home=tmp_path)
    runtime = Runtime(settings, {"work": tmp_path})
    with TestClient(
        create_app(runtime, "http://testserver", repo / "web/dist", drive_jobs=False)
    ) as client:
        boot = client.post(
            "/api/v1/bootstrap",
            json={"protocol": "1", "secret": runtime.sessions.ticket()},
            headers={"Origin": "http://testserver"},
        )
        headers = {"Origin": "http://testserver", "X-Tabi-CSRF": boot.json()["csrf"]}
        opened = client.post(
            "/api/v1/projects/open", headers=headers, json={"root_id": "work", "path": "preview"}
        ).json()
        base = f"/api/v1/projects/{opened['handle']}"
        frozen = client.post(
            base + "/episodes/episode.synthetic/compile",
            headers=headers,
            json={"expected_revision": 0, "purpose": "preview"},
        )
        assert frozen.status_code == 200, frozen.text
        assert (
            client.post(
                base + "/episodes/episode.synthetic/compile",
                headers=headers,
                json={"expected_revision": 1},
            ).status_code
            == 409
        )
        body = {
            "snapshot_sha256": frozen.json()["snapshot_sha256"],
            "preset": "proxy",
            "encoder": "libx264",
            "destination": "exports/test.mp4",
            "end_frame": 90,
            "max_chunk_frames": 30,
        }
        plan = client.post(base + "/renders/plan", headers=headers, json=body)
        assert plan.status_code == 200, plan.text
        assert len(plan.json()["job"]["chunks"]) == 3
        assert plan.json()["storage"]["required_additional_bytes"] > 0
        assert client.get(base + "/jobs").json()["jobs"] == []
        job = client.post(base + "/renders", headers=headers, json=body).json()
        paused = client.post(base + f"/jobs/{job['id']}/pause", headers=headers, json={})
        assert paused.status_code == 200 and paused.json()["state"] == "paused"
        service = runtime.get(opened["handle"]).jobs
        service.ledger.update(
            job["id"], "started", lambda j: revised(j, state="running", owner="another-worker")
        )
        assert (
            client.post(base + f"/jobs/{job['id']}/pause", headers=headers, json={}).status_code
            == 409
        )
        service.ledger.update(
            job["id"], "stopped", lambda j: revised(j, state="paused", owner=None)
        )
        prefs = client.get("/api/v1/settings").json()["preferences"]
        prefs["cache_budget_bytes"] = 0
        assert (
            client.post(
                "/api/v1/settings/preferences",
                headers=headers,
                json={"preferences": prefs, "expected_revision": None},
            ).status_code
            == 200
        )
        assert client.get(base + "/cache").json()["budget_bytes"] == 0
