"""Optional, explicitly allowed local ComfyUI bridge. Never part of rendering."""

import hashlib
import json
import shutil
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from uuid import uuid4

from .assets.service import digest_file
from .documents import decode_data
from .models.assets import GenerationRecord, Provenance
from .models.base import AssetRef, HashedFile, MediaPath, canonical_bytes, content_hash
from .models.generation import (
    ComfyWorkflow,
    GenerationOutput,
    GenerationPolicy,
    GenerationRun,
    GenerationStatus,
)
from .models.registry import ImportRequest
from .persistence import ProjectStore
from .preferences import PreferencesService

JSON_LIMIT = 2 * 1024**2
IMAGE_LIMIT = 16 * 1024**2


class GenerationError(ValueError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise GenerationError("generation server redirects are not allowed")


class ComfyClient:
    def __init__(self, endpoint):
        self.endpoint = GenerationPolicy(endpoint=endpoint).endpoint
        self.opener = build_opener(ProxyHandler({}), NoRedirect())

    def request(self, path, body=None, *, limit=JSON_LIMIT, binary=False):
        request = Request(
            self.endpoint + path,
            data=canonical_bytes(body) if body is not None else None,
            headers={"Content-Type": "application/json"} if body is not None else {},
        )
        try:
            with self.opener.open(request, timeout=10) as response:
                payload = response.read(limit + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            raise GenerationError(
                "Local ComfyUI is unavailable or rejected the request; check its endpoint/log."
            ) from error
        if len(payload) > limit:
            raise GenerationError("generation response exceeded its configured byte limit")
        return payload if binary else decode_data(payload)


class GenerationService:
    def __init__(self, assets, settings):
        self.assets, self.store, self.settings = assets, assets.store, settings

    @property
    def policy(self):
        return PreferencesService(self.settings).read()[0].generation

    def _client(self, endpoint=None):
        policy = self.policy
        if not policy.enabled:
            raise GenerationError("Local generation is disabled. Rendering remains available.")
        if endpoint and endpoint != policy.endpoint:
            raise GenerationError(
                "This run belongs to another endpoint; restore its saved endpoint first"
            )
        return ComfyClient(policy.endpoint)

    def status(self, *, probe=False):
        workflows = [
            self.store.read(p.relative_to(self.store.root).as_posix())
            for p in sorted((self.store.root / "registry/workflows").glob("*/*.json"))
        ]
        runs = [
            self.store.read(p.relative_to(self.store.root).as_posix())
            for p in sorted((self.store.root / "generation/runs").glob("*.json"))
        ]
        availability, message = ("unchecked", "Check the optional server when needed.")
        if not self.policy.enabled:
            availability, message = (
                "disabled",
                "Local generation is disabled; rendering is independent.",
            )
        elif probe:
            try:
                self._client().request("/system_stats")
                availability, message = (
                    "online",
                    "Local server responded; workflows still require preflight.",
                )
            except GenerationError as error:
                availability, message = "offline", str(error)
        return GenerationStatus(
            schema_version="1.0",
            policy=self.policy,
            availability=availability,
            message=message,
            workflows=workflows,
            runs=runs,
            workflow_hashes={f"{w.id}@{w.version}": content_hash(w) for w in workflows},
        )

    def _workflow(self, manifest):
        location = self.assets.resolve(manifest.workflow.location)
        if digest_file(location) != (manifest.workflow.sha256, manifest.workflow.size_bytes):
            raise GenerationError("workflow bytes changed since their manifest was prepared")
        payload = ProjectStore(location.parent)._read_bytes(location.name)
        if hashlib.sha256(payload).hexdigest() != manifest.workflow.sha256:
            raise GenerationError("workflow changed while loading")
        workflow = decode_data(payload)
        if not 0 < len(workflow) <= 256:
            raise GenerationError("workflow needs 1–256 API-format nodes")
        seed_inputs = 0
        for identity, node in workflow.items():
            AssetRef(id=identity, version="1.0")
            if (
                not isinstance(node, dict)
                or set(node) - {"class_type", "inputs", "_meta"}
                or node.get("class_type") not in manifest.node_definitions
                or not isinstance(node.get("inputs"), dict)
            ):
                raise GenerationError(
                    "workflow node/type is not declared by the allowlisted manifest"
                )
            for key in ("seed", "noise_seed"):
                if key in node["inputs"]:
                    seed_inputs += 1
                    if node["inputs"][key] != manifest.seed:
                        raise GenerationError("workflow seed differs from the manifest")
        if manifest.seed is not None and not seed_inputs:
            raise GenerationError("manifest seed has no corresponding workflow input")
        if any(
            n not in workflow or workflow[n]["class_type"] != "SaveImage"
            for n in manifest.output_nodes
        ):
            raise GenerationError("declared output nodes must be existing SaveImage nodes")
        bound = {(m.node_id, m.input_name) for m in manifest.models}
        for model in manifest.models:
            node = workflow.get(model.node_id, {})
            if node.get("inputs", {}).get(model.input_name) != model.server_name:
                raise GenerationError("model binding does not match the workflow input")
            if digest_file(self.assets.resolve(model.file.location)) != (
                model.file.sha256,
                model.file.size_bytes,
            ):
                raise GenerationError(
                    "a declared local model changed; review a new workflow manifest"
                )
        for identity, node in workflow.items():
            for key, value in node["inputs"].items():
                if (
                    isinstance(value, str)
                    and value.lower().endswith((".safetensors", ".ckpt", ".pt", ".pth", ".bin"))
                    and (identity, key) not in bound
                ):
                    raise GenerationError("every model filename needs a hashed local model binding")
        return payload, workflow

    def register(self, manifest):
        manifest = ComfyWorkflow.model_validate(manifest)
        if manifest.revision:
            raise GenerationError("register a new workflow version at revision zero")
        self._workflow(manifest)
        # Registration never enables execution or adds an allowlist entry.
        return self.store.save_draft(manifest, expected_revision=None)

    def _load_run(self, identity):
        identity = AssetRef(id=identity, version="1.0").id
        run = self.store.read(f"generation/runs/{identity}.json")
        if not isinstance(run, GenerationRun) or run.id != identity:
            raise GenerationError("generation receipt identity mismatch")
        if content_hash(run.manifest) != run.manifest_sha256:
            raise GenerationError("generation manifest changed inside the receipt")
        return run

    def _save(self, run, **updates):
        data = {**run.model_dump(mode="json"), **updates}
        return self.store.save_draft(
            GenerationRun.model_validate(data), expected_revision=run.revision
        )

    def _evidence(self, run, name, payload):
        relative = f"generation/evidence/{run.id}/{name}"
        try:
            existing = self.store._read_bytes(relative)
        except FileNotFoundError:
            self.store._atomic_write(relative, payload, overwrite=False)
        else:
            if existing != payload:
                raise GenerationError("existing generation evidence changed; it was preserved")
        return relative

    def submit(self, reference, *, expected_hash):
        reference = AssetRef.model_validate(reference)
        with self.store.exclusive_lock(".generation.lock"):
            policy = self.policy
            if not policy.enabled:
                raise GenerationError("Local generation is disabled. Rendering remains available.")
            manifest = self.store.read(
                f"registry/workflows/{reference.id}/{reference.version}.json"
            )
            if not isinstance(manifest, ComfyWorkflow) or (manifest.id, manifest.version) != (
                reference.id,
                reference.version,
            ):
                raise GenerationError("workflow identity does not match its registered path")
            digest = content_hash(manifest)
            if digest != expected_hash or digest not in policy.allowed_workflow_hashes:
                raise GenerationError(
                    "this exact workflow manifest hash is not allowed for execution"
                )
            client = ComfyClient(policy.endpoint)
            payload, workflow = self._workflow(manifest)
            for name, expected in manifest.node_definitions.items():
                actual = client.request("/object_info/" + quote(name, safe=""))
                if name not in actual or content_hash(actual[name]) != expected:
                    raise GenerationError(
                        "installed node definitions changed; review before executing"
                    )
            if self.policy != policy:
                raise GenerationError("generation settings changed; review before executing")
            run = GenerationRun(
                schema_version="1.0",
                id="gen-" + uuid4().hex,
                endpoint=policy.endpoint,
                prompt_id=str(uuid4()),
                manifest=manifest,
                manifest_sha256=digest,
                state="submitting",
            )
            self._evidence(run, "workflow.json", payload)
            self._evidence(run, "manifest.json", canonical_bytes(manifest))
            run = self.store.save_draft(run, expected_revision=None)
            try:
                result = client.request(
                    "/prompt", {"prompt": workflow, "client_id": run.id, "prompt_id": run.prompt_id}
                )
                if result.get("error") or result.get("node_errors"):
                    return self._save(
                        run, state="failed", error=json.dumps(result, ensure_ascii=False)[:2000]
                    )
                if result.get("prompt_id") != run.prompt_id:
                    raise GenerationError(
                        "server did not confirm the prompt ID; inspect history before retrying"
                    )
            except (GenerationError, ValueError) as error:
                # Never retry an uncertain POST; the prewritten ID can be reconciled via history.
                return self._save(run, state="unknown", error=str(error))
            return self._save(run, state="queued", error=None)

    def _history(self, client, run):
        response = client.request("/history/" + quote(run.prompt_id, safe=""))
        history = response.get(run.prompt_id)
        if history is None:
            return None
        if not isinstance(history, dict):
            raise GenerationError("server returned malformed workflow history")
        prompt = history.get("prompt")
        if not isinstance(prompt, list) or len(prompt) < 3 or prompt[1] != run.prompt_id:
            raise GenerationError("server history does not identify the requested prompt")
        payload = self.store._read_bytes(f"generation/evidence/{run.id}/workflow.json")
        if hashlib.sha256(payload).hexdigest() != run.manifest.workflow.sha256:
            raise GenerationError("saved workflow evidence changed")
        if canonical_bytes(prompt[2]) != canonical_bytes(decode_data(payload)):
            raise GenerationError("server history executed a different workflow")
        return history

    def poll(self, identity):
        with self.store.exclusive_lock(".generation.lock"):
            run = self._load_run(identity)
            if run.state in {"succeeded", "failed", "imported"}:
                return run
            client = self._client(run.endpoint)
            history = self._history(client, run)
            if history is not None:
                status = history.get("status", {})
                if not isinstance(status, dict):
                    raise GenerationError("server returned malformed workflow status")
                if status.get("status_str") == "error":
                    self._evidence(run, "history.json", canonical_bytes(history))
                    return self._save(
                        run,
                        state="failed",
                        queue_position=None,
                        error=json.dumps(status, ensure_ascii=False)[:2000],
                    )
                if status.get("completed") is True and status.get("status_str") == "success":
                    outputs = []
                    raw_outputs = history.get("outputs", {})
                    if not isinstance(raw_outputs, dict):
                        raise GenerationError("server returned malformed outputs")
                    for node in run.manifest.output_nodes:
                        node_output = raw_outputs.get(node, {})
                        if not isinstance(node_output, dict) or not isinstance(
                            node_output.get("images", []), list
                        ):
                            raise GenerationError("server returned malformed still outputs")
                        for value in node_output.get("images", []):
                            if not isinstance(value, dict):
                                raise GenerationError("server returned malformed still identity")
                            outputs.append(GenerationOutput(node_id=node, **value))
                    if not outputs or len(outputs) > 16:
                        raise GenerationError(
                            "completed workflow needs 1–16 declared still outputs"
                        )
                    identities = [(o.filename, o.subfolder) for o in outputs]
                    if len(set(identities)) != len(identities):
                        raise GenerationError("duplicate generated output identities")
                    self._evidence(run, "history.json", canonical_bytes(history))
                    return self._save(
                        run,
                        state="succeeded",
                        outputs=[o.model_dump() for o in outputs],
                        error=None,
                        queue_position=None,
                    )
            queue = client.request("/queue")
            for key, state in (("queue_running", "running"), ("queue_pending", "queued")):
                if not isinstance(queue.get(key, []), list):
                    raise GenerationError("server returned malformed queue state")
                for position, entry in enumerate(queue.get(key, [])):
                    if isinstance(entry, list) and len(entry) > 1 and entry[1] == run.prompt_id:
                        return self._save(
                            run,
                            state=state,
                            queue_position=position if state == "queued" else None,
                            error=None,
                        )
            return self._save(
                run,
                state="unknown",
                queue_position=None,
                error="Prompt absent from queue/history. Inspect the server; no automatic retry.",
            )

    def import_results(self, identity):
        with self.store.exclusive_lock(".generation.lock"):
            run = self._load_run(identity)
            if run.state == "imported":
                for reference in run.imported_assets:
                    self.assets.require_valid(reference)
                return run
            if run.state != "succeeded":
                raise GenerationError("poll a successfully completed workflow before importing")
            client = self._client(run.endpoint)
            history = self._history(client, run)
            recorded = self.store._read_bytes(f"generation/evidence/{run.id}/history.json")
            if history is None or canonical_bytes(history) != recorded:
                raise GenerationError("server history changed since completion; import was stopped")
            budget, total, imported = self.policy.max_output_bytes, 0, []
            if shutil.disk_usage(self.store.root).free < budget * 3:
                raise GenerationError(
                    "not enough space for the configured generation import budget"
                )
            for index, output in enumerate(run.outputs):
                suffix = Path(output.filename).suffix.lower()
                relative = f"generation/evidence/{run.id}/output-{index:02d}{suffix}"
                if len(run.downloads) > index:
                    payload = self.store._read_bytes(relative)
                    recorded_file = run.downloads[index]
                    if recorded_file.location != MediaPath(path=relative) or (
                        hashlib.sha256(payload).hexdigest(),
                        len(payload),
                    ) != (recorded_file.sha256, recorded_file.size_bytes):
                        raise GenerationError(
                            "saved generated output changed; preserving existing data"
                        )
                else:
                    query = urlencode(output.model_dump(exclude={"node_id"}))
                    payload = client.request(
                        "/view?" + query, limit=min(IMAGE_LIMIT, budget - total), binary=True
                    )
                    self._evidence(run, f"output-{index:02d}{suffix}", payload)
                    record = HashedFile(
                        location=MediaPath(path=relative),
                        sha256=hashlib.sha256(payload).hexdigest(),
                        size_bytes=len(payload),
                    )
                    run = self._save(
                        run, downloads=[f.model_dump() for f in [*run.downloads, record]]
                    )
                total += len(payload)
                if total > budget:
                    raise GenerationError(
                        "generated stills exceed the configured total byte budget"
                    )
                reference = AssetRef(id=f"generated.{run.id}.{index}", version="1.0")
                hashes = {
                    f"{m.node_id}/{m.input_name}/{m.server_name}": m.file.sha256
                    for m in run.manifest.models
                }
                first = run.manifest.models[0]
                provenance = Provenance(
                    origin="synthetic" if run.manifest.synthetic_fixture else "generated",
                    commercial_use="pending",
                    notes="Generated draft; artwork, model terms and publication need review.",
                    generation=GenerationRecord(
                        model_name=first.server_name,
                        model_sha256=first.file.sha256,
                        model_hashes=hashes,
                        workflow=MediaPath(path=f"generation/evidence/{run.id}/workflow.json"),
                        workflow_sha256=run.manifest.workflow.sha256,
                        manifest_sha256=run.manifest_sha256,
                        seed=run.manifest.seed,
                        prompt_id=run.prompt_id,
                        notes=(
                            "Local file hashes verified before submission; "
                            "server model-directory mapping is operator configured."
                        ),
                    ),
                )
                try:
                    existing = self.assets.load(reference)
                except FileNotFoundError:
                    try:
                        existing = self.assets.import_asset(
                            ImportRequest(
                                **reference.model_dump(),
                                kind="still",
                                paths=[MediaPath(path=relative)],
                                provenance=provenance,
                            )
                        )
                    except OSError as error:
                        raise GenerationError(
                            "generated still is unreadable or cannot be decoded"
                        ) from error
                if (
                    existing.provenance != provenance
                    or len(existing.files) != 1
                    or existing.files[0].sha256 != hashlib.sha256(payload).hexdigest()
                    or existing.approval.status != "draft"
                ):
                    raise GenerationError(
                        "existing import differs; preserving it instead of replacing"
                    )
                self.assets.require_valid(reference)
                imported.append(reference.model_dump())
            return self._save(run, state="imported", imported_assets=imported, error=None)
