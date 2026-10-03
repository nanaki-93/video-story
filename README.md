# Tabi Story Studio

A local web application for authored Tabi music stories, backed by Python and FFmpeg. The browser edits project documents and plays rendered previews; Python owns all timeline, asset, audio and rendering behavior. Music creation and manual publishing remain separate workflows.

**Current state:** T01 is implemented. T03 contracts and generated schemas are available; safe project persistence is in progress. The CLI currently exposes settings/version; the web UI and renderer remain planned. See [progress](docs/progress.md) and the [implementation/asset review](docs/09-implementation-review.md).

## Development setup

Tested on Apple M5 Pro, macOS 27.0.1, Python 3.11.16 and uv 0.11.0. The Python version is recorded in `.python-version`; dependency versions are in `uv.lock`. FFmpeg is not needed for T01. It is not installed on PATH in the audited setup; T02 must probe an explicit installation before any rendering claims.

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
3. Execute the [task index](docs/tasks/INDEX.md) in its dependency order. T03 persistence is in progress; T02 then proves the actual media toolchain.
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
