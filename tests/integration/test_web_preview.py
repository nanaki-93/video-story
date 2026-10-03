from pathlib import Path

import pytest

from tabi.core.fixtures import generate_fixtures


@pytest.mark.media
def test_preview_http_real_video_frame_hash_and_source_preservation(tmp_path):
    import hashlib
    import io
    import time

    from fastapi.testclient import TestClient
    from PIL import Image

    from tabi.api.app import create_app
    from tabi.api.runtime import Runtime
    from tabi.core.config import load_settings

    repo = Path(__file__).resolve().parents[2]
    root = tmp_path / "media"
    generate_fixtures(root, profile="story")
    settings = load_settings(repo / "examples/settings.macos.toml", env={}, cwd=repo, home=tmp_path)
    runtime = Runtime(settings, {"fixtures": tmp_path})
    app = create_app(runtime, "http://testserver", repo / "web/dist")
    sources = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob("*.wav")}
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/bootstrap",
            json={"protocol": "1", "secret": runtime.sessions.ticket()},
            headers={"Origin": "http://testserver"},
        )
        assert response.status_code == 200
        headers = {"Origin": "http://testserver", "X-Tabi-CSRF": response.json()["csrf"]}
        item = client.post(
            "/api/v1/projects/open", headers=headers, json={"root_id": "fixtures", "path": "media"}
        ).json()
        base = f"/api/v1/projects/{item['handle']}"
        route = base + "/episodes/episode.synthetic/preview"
        result = client.post(
            route,
            headers=headers,
            json={"expected_revision": 0, "first_frame": 30, "end_frame": 90},
        )
        assert result.status_code == 200, result.text
        selected = result.json()
        started = time.monotonic()
        while time.monotonic() - started < 90:
            job = client.get(base + f"/jobs/{selected['job_id']}").json()
            assert job["state"] not in {"failed", "cancelled"}, job
            if job["state"] == "verified":
                break
            time.sleep(0.2)
        assert job["state"] == "verified"
        media = base + f"/jobs/{job['id']}/video"
        assert client.get(media, headers={"Range": "bytes=0-3"}).status_code == 206
        body = {"snapshot_sha256": selected["snapshot_sha256"], "frame": 36}
        still = client.post(base + "/frames", headers=headers, json=body)
        assert still.status_code == 200, still.text
        record = still.json()
        image = client.get(base + f"/frames/{record['id']}/image")
        assert hashlib.sha256(image.content).hexdigest() == record["report"]["output_sha256"]
        assert Image.open(io.BytesIO(image.content)).size == (960, 540)
        assert record["report"]["first_frame"] == 36
        repeat = client.post(base + "/frames", headers=headers, json=body).json()
        assert repeat["report"]["output_sha256"] == record["report"]["output_sha256"]
        verified = runtime.get(item["handle"]).jobs.verify_export(job["id"])
        assert verified.video.frame_count == 60 and verified.audio.decoded_samples == 96000
        # A replacement retains the verified proxy even when the browser reconnects.
        replacement = client.post(
            route, headers=headers, json={"expected_revision": 0, "first_frame": 0, "end_frame": 30}
        )
        assert replacement.status_code == 200
        assert client.get(route).json()["previous_job"]["id"] == job["id"]
        runtime.sessions.expires = 0
        assert client.get(media).status_code == 401
        assert client.get(base + f"/frames/{record['id']}/image").status_code == 401
    assert all(
        hashlib.sha256(path.read_bytes()).hexdigest() == digest for path, digest in sources.items()
    )
