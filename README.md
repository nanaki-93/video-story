# Tabi Story Studio

A local web application for authored Tabi music stories, backed by Python and FFmpeg. The browser edits project documents and plays rendered previews; Python owns all timeline, asset, audio and rendering behavior. Music creation and manual publishing remain separate workflows.

**Current state:** M0 is complete (T01, T03, T02): Python bootstrap, strict contracts, 16 generated schemas, safe local persistence, a toolchain doctor and a verified synthetic media test. Software H.264 and VideoToolbox both passed on the M5 Pro. The web UI and episode renderer remain planned. See [progress](docs/progress.md), [toolchain checks](docs/10-toolchain.md) and the [implementation/asset review](docs/09-implementation-review.md).

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

`make setup` installs the locked development and image-audit dependencies. It uses `.tools/bin/uv` if present, or `uv` on PATH; override with `make setup UV=/path/to/uv`. Pydantic and PyYAML provide the shared document contracts and loading. Node/frontend tooling enters in T25, and is planned as a build dependency only.

## Media toolchain check

Install FFmpeg externally (on macOS, `brew install ffmpeg`), then run:

```sh
make doctor
make test-media
.venv/bin/tabi --config examples/settings.macos.toml render-spike --output-dir .local/spikes --encoder libx264 --json
.venv/bin/tabi --config examples/settings.macos.toml render-spike --output-dir .local/spikes --encoder h264_videotoolbox --json
```

`doctor` checks tool identity, versions, filters, advertised encoders and writable disk space. Only `render-spike` actually renders and verifies output. It creates a unique run folder containing generated inputs, graph/command logs, decoded frames and a report; the watermarked MP4 is published only after verification. All clips stay ignored by Git. `make check` runs the unit/contract checks; `make test-media` explicitly runs the real FFmpeg checks. See [reproduction and limits](docs/10-toolchain.md).

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

Precedence is defaults, then file values, then `TABI_PROJECT_ROOT`, `TABI_CACHE_ROOT`, `TABI_FFMPEG`, `TABI_FFPROBE`. File-relative paths resolve beside the config file; environment/CLI-relative paths resolve against the working directory. Bare executable names remain PATH lookups for the future doctor. JSON command data goes to stdout, JSON diagnostic records to stderr. These developer settings are separate from T03's project/episode schemas.

## Plans and implementation order

1. Read [PLAN.md](PLAN.md) and [AGENTS.md](AGENTS.md).
2. Review [assets](docs/01-assets.md), [architecture](docs/02-architecture.md), [contracts](docs/03-contracts.md), [rendering](docs/04-rendering.md), [web app UX](docs/05-webapp.md), [publishing](docs/06-publishing.md), and [QA](docs/07-qa.md).
3. Execute the [task index](docs/tasks/INDEX.md) in its dependency order. T04 is next: the reusable synthetic fixture pack.
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
