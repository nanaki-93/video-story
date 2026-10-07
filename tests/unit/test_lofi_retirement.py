"""Retiring a workflow must not mutate or resume its saved projects."""

from fastapi.testclient import TestClient

from tabi.api.app import create_app
from tabi.api.runtime import Runtime
from tabi.core.config import load_settings
from tabi.core.persistence import ProjectStore


def test_open_retired_project_preserves_records_and_has_no_generation_routes(tmp_path):
    projects = tmp_path / "Projects"
    project = projects / "Earlier Tokyo"
    ProjectStore.initialize(project, "Earlier Tokyo")
    old = {
        "flow/exports/queued.json": b'{"state":"queued","historical":"retained"}',
        "flow/episodes/old.json": b'{"retired":"do not migrate"}',
        "publishing/old.json": b'{"source_kind":"flow","id":"old"}',
        "exports/old.mp4": b"preserved historical media sentinel",
    }
    for name, payload in old.items():
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    settings = load_settings(None, env={}, cwd=tmp_path, home=tmp_path)
    runtime = Runtime(settings, {"projects": projects})
    static = tmp_path / "web"
    static.mkdir()
    (static / "index.html").write_text("Synthetic test UI")
    origin = "http://127.0.0.1:53123"
    app = create_app(runtime, origin, static, drive_jobs=False)
    with TestClient(app, base_url=origin) as client:
        connected = client.post(
            "/api/v1/bootstrap",
            json={"protocol": "1", "secret": runtime.sessions.ticket()},
            headers={"Origin": origin},
        )
        headers = {"Origin": origin, "X-Tabi-CSRF": connected.json()["csrf"]}
        response = client.post(
            "/api/v1/projects/open",
            json={"root_id": "projects", "path": "Earlier Tokyo"},
            headers=headers,
        )
        assert response.status_code == 200
        prefix = f"/api/v1/projects/{response.json()['handle']}"
        assert client.get(prefix + "/jobs").json()["jobs"] == []
        assert client.get(prefix + "/catalog").status_code == 200
        assert client.get(prefix + "/releases").json()["preparations"] == []
        assert client.get(prefix + "/flow").status_code == 404
    assert {name: (project / name).read_bytes() for name in old} == old
