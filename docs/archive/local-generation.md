# Retired ComfyUI bridge

Archived 6 October 2026. The execution bridge, CLI/API and UI controls were removed in F13. Commands below are historical and no longer available. Data schemas remain readable for existing project evidence. Use the [Flow workflow](../37-operations.md#make-a-90-second-train-video).

# Optional local generation

Generation is disabled by default and independent of rendering. Install and operate ComfyUI
separately with models and custom nodes you have chosen and have permission to use. This app
never downloads models, installs extensions, launches a server or interrupts another queue.
Use an explicit loopback endpoint such as `http://127.0.0.1:8188`; remote endpoints, DNS names,
credentials, redirects and proxy forwarding are rejected.

## Prepare a workflow

1. Export an **API-format** workflow from your installed ComfyUI. Keep it and the actual model
   files beneath the project or explicit registered local roots. Record the server's model
   directory mapping; the local file must actually be the model that its input name selects.
2. In Settings → Local ComfyUI execution settings, enable the selected endpoint with an empty
   allowlist and an explicit import budget. Save preferences. This permits status and node
   inspection, but no workflow execution.
3. Obtain each used node class's installed definition and canonical SHA-256 with
   `tabi generation node-info PROJECT CLASS`. Review the workflow, model licences and installed
   nodes yourself. A definition hash detects API changes; it does **not** attest the Python
   implementation of a custom node or the server's model directory mapping.
4. Prepare a `comfy_workflow` manifest using [the schema](../../schemas/comfy_workflow.schema.json).
   Each file record contains its `location: {root_id, path}`, `sha256` of its exact bytes and
   `size_bytes`. Each model binding contains `node_id`, `input_name`, the exact `server_name`
   input value, and that model's file record. `node_definitions` maps every node class to the
   hash obtained above. `output_nodes` lists the SaveImage node IDs to import. Set `seed` only
   when it matches the workflow's actual seed/noise_seed inputs. Set `synthetic_fixture` only
   for explicitly synthetic tests. Use a new ID/version whenever these inputs change.
5. Register the manifest through Settings → Register a workflow manifest or the CLI below.
   Registration verifies local files but grants no execution permission. Copy the resulting
   **manifest** hash from generation status into the execution allowlist after reviewing it.
   This differs from the raw workflow file's hash.

```sh
tabi generation register '/path/Project' '/path/workflow-manifest.json' --root models='/path/ComfyUI/models'
tabi generation status '/path/Project' --probe --root models='/path/ComfyUI/models'
tabi generation submit '/path/Project' my.workflow 1.0 --expected-hash MANIFEST_SHA256 --root models='/path/ComfyUI/models'
```

For the web worker, register those same roots at launch with `tabi web --root models=...`.
The browser never chooses arbitrary filesystem paths. File locations use normalized relative
paths and support spaces and Unicode. Raw file hashes can be calculated with `shasum -a 256`
and byte counts with `wc -c < FILE`; the manifest hash uses the app's canonical JSON, not the
indented on-disk manifest. Node definitions are canonical JSON hashes too.

## Run and review

In Settings, choose the registered version, click **Submit selected workflow**, then refresh
its history. Submission rechecks workflow/model bytes, installed node definitions and the
saved policy. A prompt ID is durably saved **before** sending the request. If a reply is lost,
the run remains `unknown`: refresh that ID to reconcile the server's queue/history before
considering another submission. There is no automatic POST retry or fabricated progress/ETA.

Completed output stays on the server until **Import drafts**. The app validates history
against the exact submitted workflow, accepts only bounded PNG/JPEG/WebP stills, downloads
atomically and records content/model/workflow/manifest hashes and the prompt ID. Imports
remain drafts with commercial rights pending. Approval requires a separate human review;
synthetic fixtures cannot be production-approved. The CLI equivalents are:

```sh
tabi generation refresh '/path/Project' gen-RUN_ID
tabi generation import '/path/Project' gen-RUN_ID
```

Run history and byte-checked evidence live under `generation/`. Interrupted imports can be
retried without replacing existing assets; altered partial downloads are rejected. A run
belongs to its saved endpoint, so restore that endpoint before refreshing or importing it.
Changes to model or workflow files require a newly reviewed manifest and allowlist entry.
Manage cancellation in ComfyUI itself: its global interrupt cannot safely identify job
ownership. To disable generation, save disabled preferences or use
`tabi generation configure POLICY.json` with `{"enabled":false}`. Rendering remains available.

The default import budget is 64 MiB, configurable from 1 KiB to 256 MiB; an individual image
is capped at 16 MiB, JSON replies at 2 MiB and outputs at 16 stills. Private backup preserves
project-local evidence. External model installations and ComfyUI custom-node code require
separate installation/backup and licence review; they are not bundled in the app.

## Evidence and limits

Eighteen focused tests use a clearly labelled, owned synthetic HTTP protocol server to exercise
allowlisting, queue/history, uncertain replies, changed model/workflow/node/settings rejection,
unsafe outputs, bounded downloads, partial import integrity, API authentication and CLI disable.
Chrome submitted one fixture request, refreshed completion, explicitly imported a draft and
showed `still · draft · rights pending` in Assets. The server was then made unavailable without
losing history. [Browser evidence](../evidence/t36-generation.jpg).

A separate real FFmpeg check renders 30 frames / 48000 samples with an enabled but unreachable
generation endpoint. Its synthetic clip is at
`.local/tests-t36/test_real_renderer_is_independ0/Offline generation render/exports/offline.mp4`
and is ignored by Git. This proves renderer independence; it is not an approved-art render.
No real inference, model quality, model licence or approved workflow has been validated. Those
inputs remain pending. The protocol fixture contains a text placeholder instead of weights
and must never be used as a real inference workflow.

Integration follows the official [ComfyUI server routes](https://docs.comfy.org/development/comfyui-server/comms_routes)
and [API example](https://github.com/comfyanonymous/ComfyUI/blob/master/script_examples/websockets_api_example.py)
inspected on 2026-10-04. Validate your chosen installation against this contract before production.
