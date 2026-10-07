# Tabi Story Studio

A local app for lo-fi music videos made from **reusable artwork and small animation loops**.
Save a scene once, choose music and duration, render a short preview, then export locally.

The master illustration keeps TABI, the cabin and props stable. Optional scenery scrolls behind
a fixed window mask. Prepared transparent PNG loops add small movements such as blinks or rain;
each uses its own timing without restarting the exterior. Python owns composition, timing,
audio and rendering; the browser provides the controls. No per-video JSON editing is required.

The Flow generation, prompting, retries and separate export path have been removed. Earlier
media and project files remain on disk. This route uses the existing local tools, with no new
paid apps, models or credit top-ups. Real TABI artwork, masks, loops, Tokyo strips and music
still need preparation and visual/rights approval before publication.

| Start here | |
| --- | --- |
| Make a video | [Installation](docs/32-installation.md), [asset workflow](docs/37-operations.md#make-a-lo-fi-video) |
| Prepare a reusable scene | [Scene assets](docs/37-operations.md#prepare-a-scene-once), [UI reference](docs/05-webapp.md) |
| Continue development | [Product plan](PLAN.md), [agent rules](AGENTS.md), [active tasks](docs/tasks/INDEX.md) |
| Review status | [Progress](docs/progress.md), [acceptance](docs/38-v1-acceptance.md), [documentation guide](docs/README.md) |

## Run from a development checkout

Install Python, Node/npm, uv and FFmpeg externally. The tested versions and installed-wheel
workflow are recorded in the installation guide. With uv available on PATH:

```sh
make setup
cd web
npm ci --ignore-scripts --no-audit --no-fund
cd ..
make web-build
.venv/bin/tabi --config examples/settings.macos.toml setup-check
.venv/bin/tabi --config examples/settings.macos.toml web
```

The Mac config selects exact tested Homebrew Cellar paths; use it only if those binaries exist.
Otherwise configure the actual installed tools below. `make setup` uses `.tools/bin/uv` when
present, then uv on PATH; `UV=/path/to/uv` overrides it. Dependencies are locked in `uv.lock`
and `web/package-lock.json`. Node is a build dependency, not an installed-app runtime dependency.

The launcher opens an authenticated loopback session. Keep its terminal open; closing the
browser leaves renders running. Enter `open` to reopen, `stop` to finish the active job and exit,
or Ctrl-C to cancel owned work while preserving verified chunks. Registered roots limit local
file access. See operations for recovery and external-drive relinking.

## Development checks and examples

```sh
make check
make web-check
make web-build
TABI_CONFIG=examples/settings.macos.toml make test-media
make package
```

`make check` covers unit checks, lint/format and schema drift; `make test-media` renders actual
synthetic media. The [acceptance report](docs/38-v1-acceptance.md) records the last complete
Mac gate and remaining limits. Regenerate contracts with `make schemas`.

`make fixtures` creates a new reproducible, visibly synthetic project; set `FIXTURE_OUTPUT`
to choose another new directory. [Preview instructions](docs/15-preview-workflow.md) explain
how to render it. The ordinary [JSON examples](examples/README.md) use illustrative IDs and
are not production projects; the [supplied-image walkthrough](docs/37-operations.md#reproducible-supplied-reference-draft)
provides concrete source-preserving request files.

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

## Source artwork and Git

The [source audit](docs/09-implementation-review.md) and [hash inventory](docs/asset-inventory.json)
record the supplied media and missing preparation. No import or technical test grants artistic
or publication approval. Local MP4 sources and bulk preparation variants are deliberately absent from a fresh checkout.
The [media guide](docs/assets/README.md) and [hash inventory](docs/evidence/f13-local-media-inventory.json)
record preserved local files. Selected static references stay tracked; production media belongs
in backed-up local project storage. Existing Git history has not been rewritten.

Never commit MP4s, including source clips and exports, in any letter case. Keep production
media and backups in local project storage. Do not delete source art when clearing caches.
The detailed [engineering rules](AGENTS.md) also require task-scoped verified commits and
preservation of unrelated staged work.
