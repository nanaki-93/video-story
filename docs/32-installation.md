# Install and launch the local application

The distribution is a Python wheel containing the static browser UI. Python 3.11 or 3.12,
FFmpeg/ffprobe and Safari or Chromium remain external dependencies. Node, npm and a JDK
are unnecessary at runtime. The tested target is Apple Silicon macOS 27.0.1, M5 Pro with
48 GiB RAM, Python 3.11.16 and FFmpeg 9.0.2. Other POSIX platforms are unqualified;
Windows is unsupported. This is not a signed/notarized macOS app or DMG.

## Build a distribution

From this repository with the locked Python environment and Node/npm available:

```sh
make setup
make check
make package
make web-check
```

The outputs are `.local/packages/tabi_story_studio-0.1.0-py3-none-any.whl`, the source
archive and `requirements.txt`. The build installs the locked frontend packages, checks
schemas, typechecks/builds the UI, copies third-party notices and stamps source/output
hashes. Ordinary wheel/sdist builds reject absent, stale or altered static output. Editable
development installation is allowed before building the frontend. The build uses the
[Hatch custom hook interface](https://hatch.pypa.io/latest/plugins/build-hook/reference/)
and [wheel force-inclusion](https://hatch.pypa.io/latest/plugins/builder/wheel/).

## Install outside the checkout

Copy the wheel and its generated requirements file to a local installation folder. With
Python 3.11 already installed, run from that folder:

```sh
python3.11 -m venv "Tabi runtime"
"Tabi runtime/bin/python" -m pip install --require-hashes -r requirements.txt
"Tabi runtime/bin/python" -m pip install --no-deps tabi_story_studio-0.1.0-py3-none-any.whl
"Tabi runtime/bin/tabi" --version
```

Package installation needs network access unless those dependency wheels are already
available in a local wheelhouse. Normal rendering is local and works offline. The lock
contains exact versions/hashes; compatible binaries must exist for the chosen platform.
The wheel does not include original media, models, Python, FFmpeg or commercial fonts.
See [distribution notices](../THIRD-PARTY.md).

Install FFmpeg separately if needed. On a Mac with Homebrew, `brew install ffmpeg` provides
both tools. Create a config file such as `tabi.toml`:

```toml
schema_version = "1.0"
[paths]
project_root = "~/Tabi Story Studio/projects"
cache_root = "~/.cache/tabi"
[tools]
ffmpeg = "/opt/homebrew/bin/ffmpeg"
ffprobe = "/opt/homebrew/bin/ffprobe"
```

Use the actual paths on the machine. Pin Cellar paths for reproducible production; upgrades
can invalidate resumable jobs that recorded a different toolchain. The check reports exact
versions, required filters/encoders, disk availability and bundled frontend integrity:

```sh
"Tabi runtime/bin/tabi" --config tabi.toml setup-check --json
"Tabi runtime/bin/tabi" --config tabi.toml web
```

Missing tools or altered frontend hashes produce actionable errors and exit status 2.
The check does not render video; the first synthetic preview exercises the actual codecs.
The worker binds only an ephemeral loopback port. Its private readiness handshake checks
the owned process, protocol and session before the launcher opens a one-time browser link.
Do not share that initial link. After authentication, the address contains no session secret.

## Projects, permissions and recovery

The default configured project folder is created at launch. Explicit roots must exist:

```sh
"Tabi runtime/bin/tabi" --config tabi.toml web --root studio="/Volumes/Media/Tabi projects"
```

Only registered folders and imported project media are accessible. macOS may request access
to a chosen folder or removable drive; select an accessible folder if access is denied. Full
Disk Access is not required. Avoid protected folders that have not been granted access.

Keep the launcher terminal running. Closing/reloading a tab does not cancel jobs. Enter
`open` for a new authenticated browser session; enter `stop` to finish active work and exit.
Ctrl-C cancels owned work. After restarting, open the project and choose Renders → Resume
verified progress. Do not change tools or the installed app during a resumable job. A changed
pipeline/toolchain requires a new render; retained outputs and source media are preserved.

Use [project workflows](26-project-workflows.md), [story/timeline](27-editor.md),
[preview](28-preview.md), [audio](29-audio-editor.md), [render queue](30-render-queue.md)
and [release/backup](31-release-and-backups.md) for the complete authoring flow. A backup
includes private evidence and music: keep it private and test restoration to a new folder.

## Installed verification

T33 installed the built wheel into `/private/tmp/tabi-t33-install-wcc5wlhg/Tabi runtime 東京`,
outside this checkout. Runtime PATH contained only that environment and `/usr/bin:/bin`;
Node was unavailable and imports resolved to installed site-packages. `setup-check` returned
ready with verified bundled hashes. A 90-second synthetic pilot, tab-close survival,
restart/resume and native-browser playback checks are recorded in [T33](tasks/t33.md).
Temporary verification paths are evidence, not the recommended permanent installation.

T38 repeated fresh installation for the completed application with all 17 locked runtime
packages, Node absent from PATH and verified bundled frontend hashes. The installed CLI
reverified the supplied-reference 1080p draft; Chrome played/sought it, rendered a new proxy
and displayed an exact frame. See [final acceptance](38-v1-acceptance.md) and the
[installation report](evidence/t38-installed-runtime.json). Follow the [operations guide](37-operations.md)
for a complete authoring, recovery and backup workflow.
