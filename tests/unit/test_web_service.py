import hashlib
import json
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import ValidationError

from tabi.api.app import create_app
from tabi.api.files import Artifacts
from tabi.api.launcher import OwnedWorker, validate_ready
from tabi.api.runtime import Runtime
from tabi.api.security import Sessions
from tabi.core.config import load_settings
from tabi.core.persistence import ProjectStore


@pytest.fixture
def workspace(tmp_path):
    settings = load_settings(None, env={}, cwd=tmp_path, home=tmp_path)
    static = tmp_path / "ui"
    static.mkdir()
    (static / "index.html").write_text("<!doctype html><title>Local worker test</title>")
    projects = tmp_path / "Projects 東京"
    projects.mkdir()
    ProjectStore.initialize(projects / "Test project", "Synthetic HTTP test")
    runtime = Runtime(settings, {"work": projects})
    origin = "http://127.0.0.1:53123"
    app = create_app(runtime, origin, static, drive_jobs=False)
    with TestClient(app, base_url=origin) as client:
        yield runtime, client, origin, static


def connect(runtime, client, origin):
    secret = runtime.sessions.ticket()
    response = client.post(
        "/api/v1/bootstrap", json={"protocol": "1", "secret": secret}, headers={"Origin": origin}
    )
    assert response.status_code == 200
    return response, {"Origin": origin, "X-Tabi-CSRF": response.json()["csrf"]}, secret


def test_bootstrap_cookie_replay_expiry_and_secret_redaction(workspace):
    runtime, client, origin, _ = workspace
    for route in (
        "/api/v1/session",
        "/api/v1/projects/x/jobs/y/video",
        "/api/v1/projects/x/jobs/y/events",
    ):
        assert client.get(route).status_code == 401
    response, headers, secret = connect(runtime, client, origin)
    cookie = response.headers["set-cookie"]
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie and "Path=/api/" in cookie
    assert secret not in response.text and runtime.sessions.bearer not in response.text
    assert client.get("/api/v1/session").status_code == 200
    assert (
        client.post(
            "/api/v1/bootstrap", json={"protocol": "1", "secret": secret}, headers=headers
        ).status_code
        == 401
    )
    incompatible = client.post(
        "/api/v1/bootstrap",
        json={"protocol": "2", "secret": secret, "unknown": secret},
        headers=headers,
    )
    assert incompatible.status_code == 422 and secret not in incompatible.text
    runtime.sessions.expires = 0
    assert client.get("/api/v1/session").status_code == 401
    assert client.get("/").status_code == 200  # Shell remains available to explain reconnection.
    assert client.get("/", headers={"Sec-Fetch-Site": "cross-site"}).status_code == 200


def test_origin_csrf_bearer_and_bootstrap_boundaries(workspace):
    runtime, client, origin, _ = workspace
    secret = runtime.sessions.ticket()
    body = {"protocol": "1", "secret": secret}
    assert client.post("/api/v1/bootstrap", json=body).status_code == 403
    assert (
        client.post(
            "/api/v1/bootstrap", json=body, headers={"Origin": "https://foreign.example"}
        ).status_code
        == 403
    )
    _, headers, _ = connect(runtime, client, origin)
    body = {"root_id": "work", "path": "Test project"}
    assert (
        client.post("/api/v1/projects/open", json=body, headers={"Origin": origin}).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/projects/open", json=body, headers={**headers, "X-Tabi-CSRF": "bad"}
        ).status_code
        == 403
    )
    assert client.get("/api/v1/roots", headers={"Host": "foreign.example"}).status_code == 403
    assert (
        client.get("/api/v1/roots", headers={"Origin": "https://foreign.example"}).status_code
        == 403
    )
    assert client.get("/api/v1/roots", headers={"Sec-Fetch-Site": "cross-site"}).status_code == 403
    assert client.post("/api/v1/bootstrap-ticket", json={}, headers=headers).status_code == 403
    bearer = {"Authorization": f"Bearer {runtime.sessions.bearer}"}
    assert client.post("/api/v1/bootstrap-ticket", json={}, headers=bearer).status_code == 200
    assert (
        client.post(
            "/api/v1/bootstrap-ticket",
            json={},
            headers={**bearer, "Origin": "https://foreign.example"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/projects/open",
            content=b"{}",
            headers={**headers, "Content-Type": "text/plain"},
        ).status_code
        == 415
    )


def test_registered_roots_unicode_traversal_and_symlink_rejection(workspace, tmp_path):
    runtime, client, origin, static = workspace
    _, headers, _ = connect(runtime, client, origin)
    root = runtime.roots.root("work")
    (root / "escape").symlink_to(tmp_path, target_is_directory=True)
    (root / "internal").symlink_to(root / "Test project", target_is_directory=True)
    (static / "assets").mkdir()
    (static / "assets/secret.js").symlink_to(root / "Test project/project.json")
    listed = client.get("/api/v1/files", params={"root_id": "work"})
    assert listed.status_code == 200
    assert [item["name"] for item in listed.json()["entries"]] == ["Test project"]
    for path in ("../", "/etc", "escape", "internal", "Test project/../../", "https://example.com"):
        assert (
            client.get("/api/v1/files", params={"root_id": "work", "path": path}).status_code == 400
        )
    assert client.get("/api/v1/files", params={"root_id": "missing"}).status_code == 400
    assert client.get("/assets/secret.js").status_code == 404
    opened = client.post(
        "/api/v1/projects/open", json={"root_id": "work", "path": "Test project"}, headers=headers
    )
    assert opened.status_code == 200
    handle = opened.json()["handle"]
    assert client.get(f"/api/v1/projects/{handle}/jobs").json()["jobs"] == []
    # Reloading and reopening the same project never submits a job or duplicates its handle.
    for _ in range(3):
        assert client.get("/api/v1/session").status_code == 200
        assert (
            client.post(
                "/api/v1/projects/open",
                json={"root_id": "work", "path": "Test project"},
                headers=headers,
            ).json()["handle"]
            == handle
        )
    assert len(client.get("/api/v1/projects").json()["projects"]) == 1
    assert client.get(f"/api/v1/projects/{handle}/jobs").json()["jobs"] == []


def test_tickets_are_atomic_single_use_and_expire(monkeypatch):
    now = [100]
    monkeypatch.setattr("tabi.api.security.time.monotonic", lambda: now[0])
    sessions = Sessions(bootstrap_lifetime=10)
    secret = sessions.ticket()
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(sessions.exchange, [secret] * 16)) == 1
    secret = sessions.ticket()
    now[0] = 111
    assert not sessions.exchange(secret)
    assert Sessions().cookie_name != sessions.cookie_name


def test_artifact_ranges_hash_tamper_and_safe_open(tmp_path):
    data = bytes(range(256)) * 4
    (tmp_path / "sample.bin").write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    artifacts, store, app = Artifacts(), ProjectStore(tmp_path), FastAPI()

    @app.api_route("/sample", methods=["GET", "HEAD"])
    def sample(request: Request):
        return artifacts.response(
            store, "sample.bin", expected, request, media_type="application/octet-stream"
        )

    with TestClient(app) as client:
        assert client.get("/sample", headers={"Range": "bytes=0-1"}).content == data[:2]
        assert client.get("/sample", headers={"Range": "bytes=-17"}).content == data[-17:]
        response = client.get("/sample", headers={"Range": "bytes=1000-"})
        assert (
            response.status_code == 206
            and response.headers["content-range"] == "bytes 1000-1023/1024"
        )
        assert client.head("/sample").content == b""
        assert client.head("/sample").headers["content-length"] == "1024"
        assert client.get("/sample", headers={"Range": "bytes=1024-"}).status_code == 416
        (tmp_path / "sample.bin").write_bytes(b"changed")
        with pytest.raises(ValueError, match="changed"):
            client.get("/sample")


def test_readiness_rejects_wrong_protocol_pid_socket_and_nonce():
    payload = {
        "protocol": "1",
        "pid": 42,
        "port": 5000,
        "session_id": "test-session",
        "nonce": "n" * 32,
        "bootstrap": "b" * 32,
        "bearer": "t" * 32,
    }
    assert validate_ready(json.dumps(payload), pid=42, port=5000, nonce="n" * 32).pid == 42
    for key, value in (("protocol", "2"), ("pid", 43), ("port", 5001), ("nonce", "x" * 32)):
        with pytest.raises((ValueError, ValidationError)):
            validate_ready(json.dumps({**payload, key: value}), pid=42, port=5000, nonce="n" * 32)


def test_owned_workers_use_ephemeral_ports_and_shutdown_without_touching_other_sockets(workspace):
    runtime, _, _, static = workspace
    unrelated = socket.socket()
    unrelated.bind(("127.0.0.1", 0))
    unrelated.listen()
    first = OwnedWorker(runtime.settings, runtime.roots.roots, static)
    second = None
    try:
        second = OwnedWorker(runtime.settings, runtime.roots.roots, static)
        assert len({first.port, second.port, unrelated.getsockname()[1]}) == 3
        assert first.request("GET", "/api/v1/session")["pid"] == first.process.pid
        first.stop()
        assert first.process.returncode == 0
        assert second.request("GET", "/api/v1/session")["pid"] == second.process.pid
        assert unrelated.fileno() >= 0
    finally:
        first.stop()
        if second:
            second.stop()
        unrelated.close()


def test_failed_start_does_not_open_or_adopt_a_server(workspace):
    runtime, _, _, static = workspace
    with pytest.raises(ValueError, match="readiness"):
        OwnedWorker(runtime.settings, runtime.roots.roots, static / "missing")


def test_cli_signal_stops_its_owned_child_and_public_output_has_no_tokens(workspace):
    runtime, _, _, static = workspace
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "tabi",
            "web",
            "--no-open",
            "--web-root",
            str(static),
            "--root",
            f"work={runtime.roots.root('work')}",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        line = process.stdout.readline()
        ready = json.loads(line)
        assert set(ready) == {"url", "pid", "protocol"}
        process.terminate()  # Popen ownership; this tests graceful launcher SIGTERM handling.
        out, err = process.communicate(timeout=15)
        assert process.returncode == 0, err
        assert all(word not in line + out + err for word in ("bootstrap=", "bearer", "csrf"))
        with socket.socket() as connection:
            assert connection.connect_ex(("127.0.0.1", int(ready["url"].rsplit(":", 1)[1]))) != 0
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
