# Application architecture and repository

## Module ownership

The Python core owns schemas, asset registry, timeline compiler, state evaluation, rendering, audio scheduling, job persistence and release preparation. CLI and API are adapters. Kotlin owns UI state, forms, timeline interaction, proxy playback, file selection and worker lifecycle. Resolve/Fusion is an optional source-authoring tool; it is not required by the runtime.

Logical flow: approved assets + music + episode document → validation → compiled immutable snapshot → render plan → chunk jobs → assembled video and continuous audio → export verification → release preparation.

## Proposed repository structure

| Path | Responsibility |
| --- | --- |
| `AGENTS.md`, `README.md`, `Makefile` | Agent rules, setup and development entry points |
| `pyproject.toml`, lockfile | Python dependency and tool versions |
| `src/tabi/core/models/` | Versioned asset, scene, episode, job and release models |
| `src/tabi/core/assets/` | Import, probing, normalization, approval, registry |
| `src/tabi/core/timeline/` | Curves, scheduling, transitions, state evaluation |
| `src/tabi/core/render/` | Renderer interface, FFmpeg backend, graph compiler, cache |
| `src/tabi/core/audio/` | WAV probe, track timeline, mix and loudness report |
| `src/tabi/core/jobs/` | Journal, process runner, cancellation, recovery |
| `src/tabi/core/releases/` | Metadata, rights summary, preparation bundle |
| `src/tabi/cli/`, `src/tabi/api/` | CLI and FastAPI adapters |
| `desktop/` | Gradle/Kotlin Compose project |
| `schemas/` | Generated JSON Schemas, published to desktop and tests |
| `tests/unit/`, `tests/integration/`, `tests/fixtures/` | Small synthetic media and semantic tests |
| `docs/`, `scripts/` | Decisions, setup, operations, fixture generator |
| `assets-source/` | Optional local source art workspace, ignored by default |

Application source goes in git; expensive personal artwork and recordings live in the user's project storage with backups. If large assets are intentionally versioned externally, document that mechanism. Do not commit caches, exports, commercial packs, licences containing personal details, or credentials.

## Local project layout

Each project folder contains `project.json`, `episodes/`, `registry/`, `assets/`, `audio/`, `rights/`, `sources/`, `snapshots/`, `exports/`, and a disposable `.cache/`. Episode drafts reference project-relative media or registered external roots. On portable-project export, copy referenced approved media and rewrite references, verify checksums, and report omitted editable sources.

Use atomic writes and a single-writer project lock. Readers can inspect snapshots while editing occurs. Maintain an append-only job event journal and periodically compact to a job document. Recover unfinished jobs as interrupted, not successful. A schema migration produces a backup first and is explicit when destructive conversions would be necessary.

## Core services

- `AssetService`: import/probe/normalize/approve/version/relink.
- `EpisodeService`: load/save/migrate/validate/compile and calculate duration.
- `TimelineEvaluator`: deterministic pose, props, curves, visibility and positions for a global frame.
- `RenderPlanner`: divide shots into resumable chunks and derive fingerprints.
- `Renderer`: preview still/clip and render a chunk from a snapshot.
- `AudioService`: build sample-accurate placements, mix continuous PCM and report peaks/loudness.
- `JobService`: queue/run/cancel/recover, persist progress and expose artifacts.
- `ReleaseService`: package verified exports and factual metadata.

Avoid importing HTTP or UI concerns into these services. Define storage and renderer interfaces so a later backend can replace FFmpeg without rewriting episode semantics.

## Worker lifecycle

Desktop launches the installed Python worker using an argument array. Worker binds `127.0.0.1` on an ephemeral port, writes a one-time readiness JSON message to its dedicated startup channel, and returns protocol version, PID, session ID and bearer token. Desktop confirms health/protocol before opening projects. Application logs never include the token.

The worker is local and single-user. It receives only project paths chosen by the user; filesystem access is bounded to configured project/media roots where practical. Validate imported archive paths to prevent extraction outside the project. Reject URL media sources in V1. Do not expose the worker on LAN or rely on a guessed fixed port.

One render job active by default; queued jobs store frozen input snapshots. Desktop crash does not destroy completed chunks. Explicit shutdown offers cancel or leave worker running where supported; stale session recovery reconnects only after verifying recorded process/session ownership. Never kill an arbitrary process by PID alone.

## Dependency and packaging choices

Use typed Python validation (Pydantic or equivalent), Typer or argparse for CLI, FastAPI for service, YAML parsing in safe mode, and pytest for meaningful checks. Use NumPy/Pillow only for needed fixture/image operations. FFmpeg/ffprobe are external tools whose version, filters, encoders and alpha capabilities are probed by `doctor`.

Use Kotlin coroutines and serializable DTOs generated from or checked against schemas. Select the exact desktop media player only after a macOS spike proves MP4 playback, seeking, audio and distribution work. V1 may open proxies in the system player while an embedded player remains pending, but full desktop completion requires the documented preview behavior.

Create a macOS application/DMG using the supported Compose distribution tooling on macOS. Initially use a configured external FFmpeg and Python environment for development. For the packaged personal app, bundle a tested Python runtime/worker and either a licensed compatible FFmpeg build or a clearly documented first-run dependency check. Test packaging paths and runtime dylibs on a machine without developer tooling.

Signing/notarization is conditional on credentials and distribution needs. An unsigned personal build is a valid documented intermediate, not equivalent to a verified signed distribution. Record binary redistribution obligations for every bundled dependency.

## Development commands to implement

`make setup`, `make doctor`, `make fixtures`, `make check`, `make test-media`, `make run-worker`, `make run-desktop`, `make pilot`, `make package-macos`, and `make clean-cache`.

Each target delegates to documented scripts. `clean-cache` requires a project/cache root and only deletes disposable cache entries. A fresh checkout must render the synthetic pilot without ComfyUI or real music.
