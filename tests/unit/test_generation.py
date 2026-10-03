import io
import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import pytest
from PIL import Image

from tabi.core.assets import AssetService
from tabi.core.config import load_settings
from tabi.core.generation import ComfyClient, GenerationError, GenerationService
from tabi.core.models.base import AssetRef, MediaPath, canonical_bytes, content_hash
from tabi.core.models.generation import ComfyWorkflow, GenerationPolicy
from tabi.core.persistence import ProjectStore
from tabi.core.preferences import PreferencesService


@contextmanager
def protocol_server():
    # A test protocol server, not a ComfyUI installation or inference/model validation.
    state = {"mode": "pending", "posts": [], "requests": [], "lost_reply": False}
    buffer = io.BytesIO()
    Image.new("RGB", (24, 24), (192, 64, 160)).save(buffer, format="PNG")
    state["image"] = buffer.getvalue()
    state["definitions"] = {
        name: {"fixture": True, "name": name} for name in ("CheckpointLoaderSimple", "SaveImage")
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, value, code=200):
            payload = value if isinstance(value, bytes) else json.dumps(value).encode()
            self.send_response(code)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            path = urlsplit(self.path).path
            state["requests"].append(path)
            if state.get("offline"):
                return self.send({}, 503)
            if path == "/system_stats":
                return self.send({"fixture": True})
            if path.startswith("/object_info/"):
                name = path.rsplit("/", 1)[-1]
                return self.send({name: state["definitions"][name]})
            if path == "/redirect":
                self.send_response(302)
                self.send_header("Location", "http://example.invalid/")
                self.end_headers()
                return
            if path == "/queue":
                body = state["posts"][-1] if state["posts"] else {"prompt_id": "none"}
                return self.send({"queue_" + state["mode"]: [[0, body["prompt_id"]]]})
            if path.startswith("/history/"):
                if state["mode"] not in {"done", "error"}:
                    return self.send({})
                body = state["posts"][-1]
                workflow = {} if state.get("wrong_workflow") else body["prompt"]
                entry = {
                    "prompt": [
                        0,
                        body["prompt_id"],
                        workflow,
                        {"client_id": body["client_id"]},
                        ["2"],
                    ],
                    "status": {
                        "completed": True,
                        "status_str": "success" if state["mode"] == "done" else "error",
                    },
                    "outputs": {
                        "2": {
                            "images": [
                                {
                                    "filename": state.get("filename", "owned synthetic.png"),
                                    "subfolder": "",
                                    "type": "output",
                                }
                            ]
                        }
                    },
                }
                return self.send({body["prompt_id"]: entry})
            if path == "/view":
                return self.send(state["image"])
            return self.send({}, 404)

        def do_POST(self):
            assert self.path == "/prompt"
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            state["posts"].append(body)
            if state["lost_reply"]:
                self.close_connection = True
                return
            self.send({"prompt_id": body["prompt_id"], "number": 0, "node_errors": {}})

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", state
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def prepare(tmp_path, endpoint, state):
    root = tmp_path / "Generation 東京"
    store = ProjectStore.initialize(root, "Synthetic protocol check — not inference")
    assets = AssetService(store)
    (root / "demo.safetensors").write_bytes(b"SYNTHETIC PROTOCOL FIXTURE, NOT A MODEL")
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "demo.safetensors"}},
        "2": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
    }
    (root / "workflow.json").write_bytes(canonical_bytes(workflow))
    config = tmp_path / "settings.toml"
    config.write_text(
        'schema_version = "1.0"\n'
        + f"[paths]\ncache_root = {json.dumps(str(tmp_path / 'cache'))}\n"
    )
    settings = load_settings(config, env={}, cwd=tmp_path, home=tmp_path)
    service = GenerationService(assets, settings)
    manifest = ComfyWorkflow(
        schema_version="1.0",
        id="protocol.fixture",
        version="1.0",
        description="Synthetic protocol test only",
        workflow=assets._record(MediaPath(path="workflow.json")),
        synthetic_fixture=True,
        models=[
            {
                "node_id": "1",
                "input_name": "ckpt_name",
                "server_name": "demo.safetensors",
                "file": assets._record(MediaPath(path="demo.safetensors")),
            }
        ],
        node_definitions={k: content_hash(v) for k, v in state["definitions"].items()},
        output_nodes=["2"],
    )
    service.register(manifest)
    preferences = PreferencesService(settings)
    prefs, _ = preferences.read()
    preferences.save(
        prefs.model_copy(
            update={
                "generation": GenerationPolicy(
                    enabled=True,
                    endpoint=endpoint,
                    allowed_workflow_hashes=[content_hash(manifest)],
                )
            }
        ),
        None,
    )
    return service, manifest


def submit(service, manifest):
    return service.submit(
        AssetRef(id=manifest.id, version=manifest.version), expected_hash=content_hash(manifest)
    )


def test_real_http_allowlist_history_hashes_draft_import_and_idempotence(tmp_path):
    with protocol_server() as (endpoint, state):
        service, manifest = prepare(tmp_path, endpoint, state)
        with pytest.raises(GenerationError, match="not allowed"):
            service.submit(
                AssetRef(id=manifest.id, version=manifest.version), expected_hash="0" * 64
            )
        assert not state["posts"]
        run = submit(service, manifest)
        assert run.state == "queued" and not service.assets.list_assets()
        assert service.poll(run.id).queue_position == 0
        state["mode"] = "running"
        assert service.poll(run.id).state == "running"
        state["mode"] = "done"
        assert service.poll(run.id).state == "succeeded" and not service.assets.list_assets()
        imported = service.import_results(run.id)
        asset = service.assets.load(imported.imported_assets[0])
        assert asset.approval.status == "draft" and asset.provenance.commercial_use == "pending"
        assert asset.provenance.origin == "synthetic"
        record = asset.provenance.generation
        assert record.workflow_sha256 == manifest.workflow.sha256
        assert record.model_sha256 == manifest.models[0].file.sha256
        assert (
            record.manifest_sha256 == content_hash(manifest) and record.prompt_id == run.prompt_id
        )
        count = len(state["requests"])
        assert service.import_results(run.id) == imported
        assert len(state["posts"]) == 1 and len(state["requests"]) == count


def test_unknown_submission_reconciles_without_a_second_post(tmp_path):
    with protocol_server() as (endpoint, state):
        service, manifest = prepare(tmp_path, endpoint, state)
        state["lost_reply"] = True
        run = submit(service, manifest)
        assert run.state == "unknown"
        assert service._load_run(run.id).prompt_id == state["posts"][0]["prompt_id"]
        assert service.poll(run.id).state == "queued"
        state["mode"] = "done"
        assert service.poll(run.id).state == "succeeded"
        assert len(state["posts"]) == 1


def test_policy_change_during_preflight_does_not_submit(tmp_path, monkeypatch):
    with protocol_server() as (endpoint, state):
        service, manifest = prepare(tmp_path, endpoint, state)
        original = service._workflow

        def change_policy(workflow):
            result = original(workflow)
            preferences = PreferencesService(service.settings)
            prefs, _ = preferences.read()
            preferences.save(
                prefs.model_copy(
                    update={"generation": prefs.generation.model_copy(update={"enabled": False})}
                ),
                prefs.revision,
            )
            return result

        monkeypatch.setattr(service, "_workflow", change_policy)
        with pytest.raises(GenerationError, match="settings changed"):
            submit(service, manifest)
        assert not state["posts"]
        assert not list((service.store.root / "generation/runs").glob("*.json"))


def test_declared_seed_must_be_present_in_workflow(tmp_path):
    with protocol_server() as (endpoint, state):
        service, manifest = prepare(tmp_path, endpoint, state)
        with pytest.raises(GenerationError, match="corresponding workflow input"):
            service.register(manifest.model_copy(update={"version": "1.1", "seed": 42}))


@pytest.mark.parametrize("change", ["model", "workflow", "node"])
def test_preflight_rejects_changed_allowed_inputs_before_submission(tmp_path, change):
    with protocol_server() as (endpoint, state):
        service, manifest = prepare(tmp_path, endpoint, state)
        if change == "node":
            state["definitions"]["SaveImage"]["changed"] = True
        else:
            name = "demo.safetensors" if change == "model" else "workflow.json"
            (service.store.root / name).write_bytes(b"changed after registration")
        with pytest.raises(GenerationError, match="changed"):
            submit(service, manifest)
        assert not state["posts"]


@pytest.mark.parametrize("problem", ["path", "workflow", "bytes", "offline"])
def test_server_failures_do_not_create_approved_or_wrong_assets(tmp_path, problem):
    with protocol_server() as (endpoint, state):
        service, manifest = prepare(tmp_path, endpoint, state)
        run = submit(service, manifest)
        state["mode"] = "done"
        if problem == "path":
            state["filename"] = "../escape.png"
        elif problem == "workflow":
            state["wrong_workflow"] = True
        elif problem == "offline":
            state["offline"] = True
            assert service.status(probe=True).availability == "offline"
        else:
            state["image"] = b"not an image"
        with pytest.raises(ValueError):
            service.poll(run.id)
            service.import_results(run.id)
        assert not service.assets.list_assets()


def test_partial_import_bytes_are_hashed_and_budget_and_redirects_are_bounded(
    tmp_path, monkeypatch
):
    with protocol_server() as (endpoint, state):
        service, manifest = prepare(tmp_path, endpoint, state)
        run = submit(service, manifest)
        state["mode"] = "done"
        service.poll(run.id)
        original = service.assets.import_asset

        def fail(request):
            raise ValueError("synthetic interruption before registry save")

        monkeypatch.setattr(service.assets, "import_asset", fail)
        with pytest.raises(ValueError, match="interruption"):
            service.import_results(run.id)
        receipt = service._load_run(run.id)
        assert receipt.downloads and not receipt.imported_assets
        payload = service.store.root / receipt.downloads[0].location.path
        payload.write_bytes(b"altered local download")
        monkeypatch.setattr(service.assets, "import_asset", original)
        with pytest.raises(GenerationError, match="saved generated output changed"):
            service.import_results(run.id)
        assert not service.assets.list_assets()
        with pytest.raises(GenerationError, match="byte limit"):
            ComfyClient(endpoint).request("/view", binary=True, limit=4)
        with pytest.raises(GenerationError, match="redirects"):
            ComfyClient(endpoint).request("/redirect")


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://127.0.0.1:8188",
        "http://localhost:8188",
        "http://192.168.1.2:8188",
        "http://user:pass@127.0.0.1:8188",
        "http://127.0.0.1:8188/private",
    ],
)
def test_only_explicit_loopback_endpoints_are_accepted(endpoint):
    with pytest.raises(ValueError, match="loopback"):
        GenerationPolicy(endpoint=endpoint)


def test_authenticated_web_bridge_and_cli_disable_share_the_policy(tmp_path, capsys):
    from fastapi.testclient import TestClient

    from tabi.api.app import create_app
    from tabi.api.runtime import Runtime
    from tabi.cli.main import main

    with protocol_server() as (endpoint, state):
        service, manifest = prepare(tmp_path, endpoint, state)
        runtime = Runtime(service.settings, {"test": tmp_path})
        web = tmp_path / "web"
        web.mkdir()
        (web / "index.html").write_text("Synthetic API fixture")
        with TestClient(create_app(runtime, "http://testserver", web, drive_jobs=False)) as client:
            bootstrap = client.post(
                "/api/v1/bootstrap",
                json={"protocol": "1", "secret": runtime.sessions.ticket()},
                headers={"Origin": "http://testserver"},
            ).json()
            headers = {"Origin": "http://testserver", "X-Tabi-CSRF": bootstrap["csrf"]}
            project = client.post(
                "/api/v1/projects/open",
                headers=headers,
                json={"root_id": "test", "path": service.store.root.name},
            ).json()
            route = f"/api/v1/projects/{project['handle']}/generation"
            status = client.get(route).json()
            assert status["workflow_hashes"]["protocol.fixture@1.0"] == content_hash(manifest)
            request = {
                "workflow": {"id": manifest.id, "version": manifest.version},
                "expected_hash": content_hash(manifest),
            }
            assert client.post(route + "/submit", json=request).status_code == 403
            response = client.post(route + "/submit", json=request, headers=headers)
            assert response.status_code == 200, response.text
            run = response.json()
            state["mode"] = "done"
            assert (
                client.post(route + f"/{run['id']}/refresh", json={}, headers=headers).json()[
                    "state"
                ]
                == "succeeded"
            )
            result = client.post(route + f"/{run['id']}/import", json={}, headers=headers)
            assert result.status_code == 200 and result.json()["state"] == "imported"
        policy = tmp_path / "disable.json"
        policy.write_text(GenerationPolicy(endpoint=endpoint).model_dump_json())
        assert (
            main(
                [
                    "--config",
                    str(service.settings.config_file),
                    "generation",
                    "configure",
                    str(policy),
                ]
            )
            == 0
        )
        assert json.loads(capsys.readouterr().out)["generation"]["enabled"] is False
        assert service.status(probe=True).availability == "disabled"
        calls = len(state["requests"])
        with pytest.raises(GenerationError):
            submit(service, manifest)
        assert len(state["requests"]) == calls
