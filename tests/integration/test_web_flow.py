import time
from pathlib import Path

import httpx
import pytest
from test_flow_assembly import ready_video
from test_flow_import import make_clip

from tabi.api.launcher import OwnedWorker
from tabi.core.flow.service import updated

pytestmark = pytest.mark.media
REPO = Path(__file__).resolve().parents[2]


def test_live_flow_import_review_export_ranges_and_reopen(tmp_path):
    settings, sources, service, episode = ready_video(tmp_path, counts=(48,))
    worker = OwnedWorker(settings, {"work": tmp_path}, REPO / "web/dist")
    try:
        opened = worker.request(
            "POST",
            "/api/v1/projects/open",
            {"root_id": "work", "path": service.store.root.relative_to(tmp_path).as_posix()},
        )
        base = f"/api/v1/projects/{opened['handle']}/flow"
        fresh = worker.request(
            "POST",
            base,
            {
                "limits": episode.limits.model_dump(),
                "recipe": episode.recipe.model_dump(mode="json"),
            },
        )
        path = base + "/" + fresh["episode"]["id"]
        data = worker.request(
            "POST", path + "/prepare", {"expected_revision": fresh["episode"]["revision"]}
        )
        data = worker.request(
            "POST",
            path + "/import",
            {
                "expected_revision": data["episode"]["revision"],
                "attempt_id": data["next_step"]["attempt_id"],
                "source": {
                    "root_id": "work",
                    "path": (sources / "clip 0 東京.mp4").relative_to(tmp_path).as_posix(),
                },
                "synthetic": True,
            },
        )
        assert data["review"]["images"] and data["next_step"]["accepted_frames"] == 0
        candidate = data["episode"]["candidates"][-1]
        review_path = path + "/clips/" + candidate["id"] + "/review"
        body = {
            "expected_revision": data["episode"]["revision"],
            "media_sha256": candidate["media"]["sha256"],
            "decision": "rejected",
            "note": "Synthetic visual retry",
        }
        data = worker.request("POST", review_path, body)
        assert data["next_step"]["accepted_frames"] == 0
        retry = sources / "retry.mp4"
        make_clip(settings, retry, frames=48, hue=90)
        data = worker.request(
            "POST", path + "/prepare", {"expected_revision": data["episode"]["revision"]}
        )
        data = worker.request(
            "POST",
            path + "/import",
            {
                "expected_revision": data["episode"]["revision"],
                "attempt_id": data["next_step"]["attempt_id"],
                "source": {"root_id": "work", "path": retry.relative_to(tmp_path).as_posix()},
                "synthetic": True,
            },
        )
        candidate = data["episode"]["candidates"][-1]
        body = {
            "expected_revision": data["episode"]["revision"],
            "media_sha256": candidate["media"]["sha256"],
            "decision": "accepted",
            "note": "Synthetic continuity reviewed",
            "observed_state": {
                "cup_kind": "takeaway",
                "cup_position": "table",
                "has_handle": False,
                "has_saucer": False,
                "hands": "resting",
                "pose": "watching",
            },
        }
        data = worker.request("POST", path + "/clips/" + candidate["id"] + "/review", body)
        assert data["next_step"]["action"] == "finish"
        data = worker.request(
            "POST", path + "/exports", {"expected_revision": data["episode"]["revision"]}
        )
        identity = data["exports"][-1]["id"]
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            data = worker.request("GET", path)
            export = next(e for e in data["exports"] if e["id"] == identity)
            assert export["state"] not in {"failed", "cancelled"}, export["diagnostic"]
            if export["state"] == "verified":
                break
            time.sleep(0.1)
        assert export["state"] == "verified"
        video = path + f"/exports/{identity}/video"
        with httpx.Client(base_url=worker.origin) as browser:
            assert browser.get(video).status_code == 401
            response = browser.post(
                "/api/v1/bootstrap",
                json={"protocol": "1", "secret": worker.ready.bootstrap},
                headers={"Origin": worker.origin},
            )
            assert response.status_code == 200
            response = browser.get(video, headers={"Range": "bytes=0-99"})
            assert response.status_code == 206 and len(response.content) == 100
        worker.stop()
        # A retained running marker is recovered without repeating remote generation.
        saved = service.get_export(identity)
        service.save_export(
            updated(saved, state="running", owner="lost-worker", output=None),
            expected_revision=saved.revision,
        )
        worker = OwnedWorker(settings, {"work": tmp_path}, REPO / "web/dist")
        worker.request(
            "POST",
            "/api/v1/projects/open",
            {"root_id": "work", "path": service.store.root.relative_to(tmp_path).as_posix()},
        )
        data = worker.request("GET", path)
        assert data["exports"][-1]["state"] == "interrupted"
        assert len(data["episode"]["attempts"]) == 2
        worker.request(
            "POST",
            path + f"/exports/{identity}/resume",
            {"expected_revision": data["exports"][-1]["revision"]},
        )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            data = worker.request("GET", path)
            if data["exports"][-1]["state"] == "verified":
                break
            time.sleep(0.1)
        assert data["exports"][-1]["state"] == "verified"
    finally:
        worker.stop(cancel=True)
