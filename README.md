# Tabi Story Studio

A local web application for authored Tabi music stories, backed by Python and FFmpeg. The browser edits project documents and plays rendered previews; Python owns all timeline, asset, audio and rendering behavior. Music creation and manual publishing remain separate workflows.

**Current state:** The local web app implements projects, assets and metadata approval, episode/story/timeline editing, audio, exact previews, resumable renders, release preparation, settings and backup/restore. Python owns the shared CLI/API services and 64 strict schemas. Café templates, activity/outfit packs and an optional local generation adapter are implemented. A 45-minute native 1080p export passed crash recovery and all boundary checks; native 4K passed its 60-second qualification on the M5 Pro. The wheel bundles the UI and needs no Node at runtime. Real Tabi art preparation, original music and creative approval remain pending. Start with [installation](docs/32-installation.md), [operations](docs/37-operations.md) and the [acceptance report](docs/38-v1-acceptance.md).

## Run the web app

For an installed wheel, follow [installation and dependency checks](docs/32-installation.md). In a development checkout with Python, Node/npm and FFmpeg installed:

```sh
make setup
cd web
npm ci --ignore-scripts --no-audit --no-fund
cd ..
make web-build
.venv/bin/tabi --config examples/settings.macos.toml setup-check
.venv/bin/tabi --config examples/settings.macos.toml web
```

The launcher opens a private authenticated loopback session. Keep its terminal open while rendering; closing the browser leaves jobs running. Enter `open` to reopen or `stop` to finish the current job and exit. Ctrl-C cancels owned work and preserves verified chunks. Use Renders → Resume after relaunch. The default project folder is created on first launch; `--root library="/path/to/existing/library"` restricts the browser to another existing folder.

## Development setup

Tested on Apple M5 Pro/48 GiB, macOS 27.0.1, Python 3.11.16, uv 0.11.0 and FFmpeg/ffprobe 9.0.2. Python is recorded in `.python-version`; Python dependencies are locked in `uv.lock`. FFmpeg is an external installation. The [Mac settings example](examples/settings.macos.toml) selects the exact tested Homebrew Cellar paths; it fails clearly if that installation is missing.

With uv already installed, run `make setup`. Otherwise bootstrap uv locally:

```sh
python3 -m venv .tools
.tools/bin/python -m pip install uv==0.11.0
make setup
make check
make help
.venv/bin/tabi --version
.venv/bin/tabi config --json
```

`make setup` installs the locked development and image-audit dependencies. It uses `.tools/bin/uv` if present, or `uv` on PATH; override with `make setup UV=/path/to/uv`. Pydantic and PyYAML provide the shared document contracts and loading. Node/npm are development/build dependencies only.

## Media toolchain check

Install FFmpeg externally (on macOS, `brew install ffmpeg`), then run:

```sh
make doctor
TABI_CONFIG=examples/settings.macos.toml make test-media
.venv/bin/tabi --config examples/settings.macos.toml render-spike --output-dir .local/spikes --encoder libx264 --json
.venv/bin/tabi --config examples/settings.macos.toml render-spike --output-dir .local/spikes --encoder h264_videotoolbox --json
```

`doctor` checks tool identity, versions, filters, advertised encoders and writable disk space. Only `render-spike` actually renders and verifies output. It creates a unique run folder containing generated inputs, graph/command logs, decoded frames and a report; the watermarked MP4 is published only after verification. All clips stay ignored by Git. `make check` runs the unit/contract checks; `make test-media` explicitly runs the real FFmpeg checks. See [reproduction and limits](docs/10-toolchain.md).

Final gates: **296 Python unit checks, 61 actual-media integration checks and four frontend tests
passed**. The final wheel was installed outside the checkout and verified with Node absent from
PATH. [Acceptance evidence and remaining creative inputs](docs/38-v1-acceptance.md).

## Reusable synthetic project

```sh
make fixtures
# Or choose a new output folder:
.venv/bin/tabi fixtures --output ".local/My synthetic project" --json
```

Generation requires a new directory and preserves existing projects. It creates 14 synthetic assets, separated scenery/masks, body and blink sequences, two WAV files, a registry and a ten-second episode. The manifest hashes 69 files; repeated generation with the pinned runtime produces identical bytes. These fixtures are visibly synthetic and never approved for publication. Use the [preview workflow](docs/15-preview-workflow.md) to validate, compile and render them. See [fixture evidence](docs/tasks/t04.md).

## Projects and document validation

Create a local project in a new or empty directory, then reopen its saved index:

```sh
.venv/bin/tabi project init ".local/My Tabi project" --title "My Tabi project" --json
.venv/bin/tabi project show ".local/My Tabi project" --json
.venv/bin/tabi document validate ".local/My Tabi project/project.json"
.venv/bin/tabi document validate examples/episode.pilot.json
```

Initialization preserves existing files and refuses occupied directories. JSON/YAML validation reports have scope `structure`: a valid example does not imply that its media exists, is approved or can render. Exit codes are 0 for success, 2 for validation/usage errors and 4 for I/O errors.

The shared Python `ProjectStore` handles revision-checked draft saves, exact-byte backups in `.backups/`, a single-writer POSIX lock, and immutable snapshots addressed by SHA-256. It verifies temporary bytes before atomic publication and rejects metadata symlinks. Approved versions require a new version to edit. Explicit migration infrastructure is available; schema 1.0 is the first production version, so no legacy migration is registered. See the [persistence contract](docs/03-contracts.md#implemented-project-persistence-t03) for layout and recovery limits.

## Timeline inspection

`tabi timeline inspect EPISODE --frame N` evaluates global curves, travel distance and the exact audio sample. `tabi timeline expand EPISODE` expands optional seeded action timing. See [semantics and verification](docs/13-timeline.md).

## Asset registry

Use `tabi asset import`, `list`, `show`, `check`, `relink`, `proxy` and explicit `approve` commands. They invoke the shared Python service. See [requests, commands and source-preservation rules](docs/11-asset-registry.md). Rights and art review stay pending until provided.

`tabi author` creates/edits episodes, installs draft templates/packs and records explicit metadata
review. `tabi audio propose/edit/audition`, `tabi preferences` and `tabi jobs progress` expose the
same revision/hash guards and services as the UI. The [operations guide](docs/37-operations.md)
includes a working supplied-train-reference walkthrough using [request files](examples/workflows/).
Its ten-second output is a silent, watermarked draft; it does not imply animation or approval.

## Local configuration

`tabi --config PATH config --json` loads an explicit TOML file. Otherwise `TABI_CONFIG` selects it, then `$XDG_CONFIG_HOME/tabi/config.toml` (default `~/.config/tabi/config.toml`). A missing default file uses defaults; a missing explicit file, malformed TOML, unsupported version or unknown key fails with exit code 2. This command resolves settings without creating project/cache folders or probing tools.

```toml
schema_version = "1.0"

[paths]
project_root = "~/Tabi Story Studio/projects"
cache_root = "~/.cache/tabi"

[tools]
ffmpeg = "ffmpeg"
ffprobe = "ffprobe"
```

Precedence is defaults, then file values, then `TABI_PROJECT_ROOT`, `TABI_CACHE_ROOT`, `TABI_FFMPEG`, `TABI_FFPROBE`. File-relative paths resolve beside the config file; environment/CLI-relative paths resolve against the working directory. Bare executable names use PATH lookup. JSON command data goes to stdout, JSON diagnostic records to stderr. These tool settings are separate from project/episode schemas and saved application preferences.

Rendering caches use each project's `.cache/tabi-v1`; global `cache_root` stores launcher preferences and recent project locations. See [cache inspection, pruning and disk estimates](docs/21-cache-storage.md).

## Plans and implementation order

1. Read [PLAN.md](PLAN.md) and [AGENTS.md](AGENTS.md).
2. Review [assets](docs/01-assets.md), [architecture](docs/02-architecture.md), [contracts](docs/03-contracts.md), [rendering](docs/04-rendering.md), [web app UX](docs/05-webapp.md), [publishing](docs/06-publishing.md), and [QA](docs/07-qa.md).
3. Use the [task index](docs/tasks/INDEX.md) and [acceptance report](docs/38-v1-acceptance.md) to see completed software and exact outstanding creative inputs. Every V1 page uses implemented services; the optional activity/outfit and local generation paths are also implemented. Production readiness still requires approved real art, original music and human review.
4. Record behavior, checks and remaining approvals in [progress](docs/progress.md).

The JSON [examples](examples/README.md) contain illustrative IDs and nonexistent media paths. They now pass structural schema validation; they are not working production projects. Regenerate/check published contracts with `make schemas` and `make check`.

## Supplied assets and Git policy

The [asset review](docs/09-implementation-review.md) covers all supplied images and clips. The [inventory](docs/asset-inventory.json) records relative paths, SHA-256 hashes, dimensions, alpha and sequence coverage. It is technical evidence, not an approval or rights registry. The local MP4 clips are deliberately absent from Git; a fresh checkout will not contain them.

**Never commit MP4 files**, including source clips, previews and exports, in any letter case. Existing indexed clips have been untracked while preserving local copies. Keep large production media in project storage with backups. Generated audit contact sheets live under ignored `.local/`.

Reproduce the image/hash audit with the files available locally:

```sh
.venv/bin/python scripts/audit_assets.py --output docs/asset-inventory.json --contact-dir .local/asset-audit/contact-sheets
```

The script fully decodes still images and hashes all files, including videos. Video decoding is a separate native/FFmpeg check documented in the review. No assets are approved, generated or altered by this audit.
