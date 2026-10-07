# Application architecture and repository

## Module ownership

The Python core owns schemas, asset registry, timeline compiler, state evaluation, rendering, audio scheduling, job persistence and release preparation. CLI and API are adapters. TypeScript owns browser UI state, forms, timeline interaction and proxy playback. A Python launcher owns the local server and worker lifecycle. Resolve/Fusion is an optional source-authoring tool; it is not required by the runtime.

Logical flow: approved assets + music + episode document → validation → compiled immutable snapshot → render plan → chunk jobs → assembled video and continuous audio → export verification → release preparation.

## Repository structure

| Path | Responsibility |
| --- | --- |
| `AGENTS.md`, `README.md`, `Makefile` | Agent rules, setup and development entry points |
| `pyproject.toml`, lockfile | Python dependency and tool versions |
| `src/tabi/core/models/` | Versioned asset, scene, episode, job and release models |
| `src/tabi/core/documents.py`, `src/tabi/core/persistence.py` | Strict document loading, atomic local storage, revisions, locks, snapshots and migration backups (T03) |
| `src/tabi/core/toolchain.py`, `src/tabi/core/process.py` | Tool identity/capability/storage checks and bounded subprocess execution (T02) |
| `src/tabi/core/lofi.py`, `models/lofi.py` | Reusable master/scenery/overlay recipes, validation and scene-to-episode compilation |
| `src/tabi/core/assets/` | Import, probing, normalization, approval, registry |
| `src/tabi/core/timeline/` | Curves, scheduling, transitions, state evaluation |
| `src/tabi/core/render/`, `src/tabi/core/cache/` | Renderer interface, FFmpeg backend, normalization and caches |
| `src/tabi/core/audio/` | WAV probe, track timeline, mix and loudness report |
| `src/tabi/core/jobs/` | Journal, process runner, cancellation, recovery |
| `src/tabi/core/publishing.py` | Metadata, rights summary, preparation bundle |
| `src/tabi/cli/`, `src/tabi/api/` | CLI and FastAPI adapters |
| `web/` | TypeScript/Vite browser UI and bundled static assets |
| `schemas/` | Generated JSON Schemas, checked against browser DTOs and tests |
| `tests/unit/`, `tests/integration/`, `tests/fixtures/` | Small synthetic media and semantic tests |
| `docs/`, `scripts/` | Decisions, setup, operations, fixture generator |
| `assets-source/` | Optional local source art workspace, ignored by default |

Application source goes in git; expensive personal artwork and recordings live in the user's project storage with backups. The existing reference PNG/JPG collection is preserved. Never commit MP4 files, including sources, test clips, previews and final exports; `.gitignore` covers case variants. Untrack with `git rm --cached` while keeping local files. If large assets are intentionally versioned externally, document that mechanism. Do not commit caches, exports, commercial packs, licences containing personal details, or credentials.

## Local project layout

Each project folder contains `project.json`, `episodes/`, `registry/`, `assets/`, `audio/`, `rights/`, `sources/`, `snapshots/`, `exports/`, and a disposable `.cache/`. Episode drafts reference project-relative media or registered external roots. On portable-project export, copy referenced approved media and rewrite references, verify checksums, and report omitted editable sources.

Use atomic writes and a single-writer project lock. Readers can inspect snapshots while editing occurs. Maintain an append-only job event journal and periodically compact to a job document. Recover unfinished jobs as interrupted, not successful. A schema migration produces a backup first and is explicit when destructive conversions would be necessary.

T03 implements the document storage foundation with `.tabi.lock`, `.backups/`, revision guards and hash-addressed snapshots. Job journals and recovery are implemented in the [job service](19-jobs.md). See the [persistence contract](03-contracts.md#implemented-project-persistence-t03) for implemented behavior and failure boundaries.

## Core services

- `LofiService`: validate/save versioned scene recipes; convert input seconds to integer frames; create content-addressed templates and ordinary episodes through shared services.
- `AssetService`: import/probe/normalize/approve/version/relink.
- `EpisodeService`: load/save/migrate/validate/compile and calculate duration.
- `TimelineEvaluator`: deterministic pose, props, curves, visibility and positions for a global frame.
- `RenderPlanner`: divide shots into resumable chunks and derive fingerprints.
- `Renderer`: preview still/clip and render a chunk from a snapshot.
- `AudioService`: build sample-accurate placements, mix continuous PCM and report peaks/loudness.
- `JobService`: queue/run/cancel/recover, persist progress and expose artifacts.
- `ReleaseService`: package verified exports and factual metadata.

Avoid importing HTTP or UI concerns into these services. Define storage and renderer interfaces so a later backend can replace FFmpeg without rewriting episode semantics.

## Local launch, browser session and worker lifecycle

The `tabi web` launcher starts the installed Python server using an argument array. Bind `127.0.0.1` on an ephemeral port and return protocol version, PID, session ID and a one-time bootstrap secret over a private readiness channel. The launcher verifies the protocol before opening the browser. No fixed-port discovery or connection to an unrelated process is allowed. See the [local service guide](25-local-service.md) for implemented lifecycle behavior.

Serve the built frontend and `/api/v1` on the same origin. The launcher opens a URL with the one-time secret in its fragment; the frontend removes the fragment immediately and exchanges the secret through a same-origin request for an HttpOnly, SameSite=Strict session cookie. Reject replay/expired secrets. Give each worker session a distinct cookie name; validate the exact Host and Origin, and require a per-session CSRF header on mutations. Cookie-authenticated GETs allow native `<video>` range requests and SSE without credentials in URLs. An authenticated same-origin session endpoint supports refresh/reconnect and reports protocol compatibility. CLI API callers can use the ephemeral bearer token through a private channel. Never log, persist in browser storage, or put these secrets in query strings. Test this flow in Safari and Chromium.

The worker is local and single-user. Register allowed project/media roots through launcher arguments or explicit local configuration. The UI chooses existing paths through a server-backed browser scoped to those roots, or streams user-selected files to a local import staging directory. Resolve symlinks and reject traversal/root escapes before filesystem operations. Browser file pickers do not supply unrestricted absolute paths. Do not require the File System Access API for V1. Validate imported archive paths; reject URL media sources. Do not expose the worker on LAN. Production requires no CORS; any development proxy/origin exception is explicit and local only.

One render job is active by default; queued jobs store frozen input snapshots. Closing or refreshing a browser tab leaves the server and jobs running. Reopening reconnects to owned work with session/protocol verification. Explicit shutdown is a separate authenticated operation that describes active-job consequences. Server failure marks jobs interrupted and preserves verified chunks. Never kill a process by PID alone. Project files live in local folders, not browser storage; asset approval and jobs cannot depend on a tab staying open.

## Dependency and packaging choices

The implementation uses Pydantic validation, argparse for CLI, FastAPI for the service, safe YAML parsing and pytest for checks. Use NumPy/Pillow only for needed fixture/image operations. FFmpeg/ffprobe are external tools whose version, filters, encoders and alpha capabilities are probed by `doctor`.

Use TypeScript DTOs generated from or checked against schemas. Start with Vite, HTML/CSS, forms and scene cards; no general editor framework is required. Frontend tooling is pinned in the npm lockfile. The browser plays renderer-generated H.264/AAC proxies with native `<video>`; exact frame inspection asks Python for a still. Test seeking, audio, stale-proxy handling and authenticated range serving on Safari and Chromium before declaring preview complete. Browser playback is not the frame-accurate renderer.

T33 builds frontend assets into the Python distribution and provides a local launcher/install workflow. No Node server is required at runtime. Initially use a configured external Python and FFmpeg installation with an actionable dependency check. Test installed launch outside the development checkout and document external-drive permissions. Bundled runtimes or FFmpeg require a licence review first; do not commit binaries. Kotlin/Compose, native DMG and signing/notarization are deferred.

## Development commands

The current `Makefile` provides `setup`, `check`, `test`, `test-media`, `schemas`, `doctor`,
`fixtures`, `web-check`, `web-build`, `run-web`, `run-worker`, `package` and `clean-cache`.
See [README](../README.md) for use and [installation](32-installation.md) for packaging.
`clean-cache` previews managed-cache pruning by default; applying it requires the observed
inventory. Sources, approved snapshots and active job artifacts remain protected.
