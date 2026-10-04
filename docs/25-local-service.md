# T26 authenticated local service

`tabi web` starts one owned Python child on an inherited ephemeral `127.0.0.1` socket.
FastAPI 0.142.2, Starlette 1.7.0 and Uvicorn 0.54.0 are locked in `uv.lock`. The child serves
the built frontend, typed project/job adapters, job SSE and verified video byte ranges.
The CLI and API use the same core; no timeline or FFmpeg logic moved into TypeScript.

## Launch and lifecycle

```sh
make web-build
.tools/bin/uv run tabi --config examples/settings.macos.toml web \
  --root "workspace=$PWD/.local"
```

Registered roots must already exist. Repeat `--root ID=PATH` for other explicitly allowed
folders. Without arguments, the configured project root is used. `--no-open` starts the
worker without launching a browser; `--web-root` selects a built static directory. The
public startup JSON contains only the origin, protocol and child PID.

The launcher verifies a private readiness record against the owned child PID, bound port,
nonce and protocol, then verifies the HTTP session identity. It never searches fixed ports,
adopts saved PIDs or signals an unrelated process. The OS chooses the port before spawning;
an unrelated listener cannot be mistaken for this worker.

In the launcher terminal, `open` issues a fresh one-time browser ticket. `stop` finishes the
active job before shutting down and leaves other queued jobs on disk. Ctrl-C, SIGTERM or
SIGHUP requests cancellation of owned work and waits for child shutdown. Cancellation keeps
verified chunks. Closing/refreshing a browser tab has no cancellation side effect. A new
worker opens project ledgers, recovers interrupted states and permits explicit validated
resume. Process crashes never imply successful exports or automatic PID adoption.

One background render lane serves all open projects. Hashing, probing and synchronous core
operations run outside the ASGI event loop. Browser reconnect only reads persisted state;
it never repeats a render submission. A repeated explicit job submission is a new request,
so callers must inspect the queue after an ambiguous network failure rather than retry blindly.

## Session and filesystem boundary

The launcher carries the initial one-time ticket in a browser fragment; the frontend removes
it immediately, then exchanges it through a same-origin POST. Tickets expire after 90 seconds
and can be redeemed once, atomically. A unique per-worker HttpOnly/SameSite=Strict cookie
supports native media and SSE. Browser sessions last 12 hours by default. Expiry leaves
saved work intact and directs the user back to the launcher. Reopening an existing tab also
handles a new bootstrap fragment without requiring a full reload. The launcher has a separate
ephemeral bearer token received only through the readiness pipe.

Exact Host and supplied Origin checks apply to every request; authenticated API requests
also reject cross-site fetches. The public static shell permits an initial top-level navigation
from another page, which carries no project data. Mutations require the browser's exact Origin,
an in-memory CSRF header and bounded JSON. Bearer calls bypass browser CSRF only after token
validation. No CORS, forwarded-proxy trust, URL bearer tokens, browser token storage, request
URL logs or externally loaded scripts are enabled. Strict DTO errors omit supplied secret values.

Root IDs come from launcher arguments, never imported project assertions. The chooser only
lists regular files/directories, skips hidden entries and symlinks, and pages 200 entries.
Traversal, absolute/URL paths and every symlink directory component are rejected. Opening
a project creates a stable handle but does not expand its trusted roots. Artifacts are selected
through a verified job record, opened with directory descriptors/O_NOFOLLOW, hash-checked,
and streamed from that open descriptor. Single closed/open/suffix ranges, HEAD and 416 responses
are supported. A changed inode/size/timestamp invalidates the in-memory hash cache. Stream
descriptors close on success, error and disconnect. This is a local single-user boundary,
not an OS sandbox against another process with the user's filesystem privileges.

## Implemented adapters

| API prefix `/api/v1` | Behavior |
| --- | --- |
| `POST /bootstrap`, `GET /session` | One-time cookie exchange and compatible reconnect |
| `POST /bootstrap-ticket` | Fresh ticket, owning launcher bearer only |
| `POST /shutdown` | Stop after current job or cancel owned active work |
| `GET /roots`, `GET /files` | Registered-root chooser data |
| `GET /projects`, `POST /projects/open`, `GET /projects/{handle}` | Open/read a real project |
| `GET/POST /projects/{handle}/jobs` | Durable listing/submission through JobService |
| `GET /projects/{handle}/jobs/{id}` | Actual persisted state |
| `POST …/{id}/cancel`, `POST …/{id}/resume` | Ownership-checked cancel and validated reuse |
| `GET …/{id}/events` | Authenticated SSE with Last-Event-ID replay and expiry |
| `GET/HEAD …/{id}/video` | Verified, cookie-authenticated byte-range media |

Settings currently shows the actual connected worker, roots, open projects and verified media
links. The production screens, root chooser and streamed imports are implemented; see the
[current UI guide](05-webapp.md) and [project workflows](26-project-workflows.md). Packaged
assets and installed launch are documented in [installation](32-installation.md). No Node server is required at runtime.

## Verification and evidence

`make check`: **42 schemas / 238 unit checks**, including nine HTTP/lifecycle cases. Frontend
drift/type/format checks, two browser contract tests and Vite build pass. Starlette reports a
test-client deprecation warning for httpx 0.28.1; requests still pass. This does not affect the
production Uvicorn server. The initial validator bundle size warning remains documented.

The actual-media HTTP test starts an owned child, exchanges a cookie, submits a real synthetic
render, reads/reconnects SSE, closes the browser client, cancels during rendering, reopens in
a new worker and resumes using the retained chunk. Final verification proves **300 frames /
480,000 samples**, correct hashes/ranges and unchanged WAV sources. Session requests stayed
responsive during rendering. [Retained report](evidence/t26-http-worker.json) and local output
under `.local/t26-http-verification/test_live_worker_render_cookie0/` record this run. MP4 stays ignored.

The nine focused HTTP/lifecycle checks and actual render check pass. They cover bootstrap replay,
expiry/concurrency, unknown fields and protocol mismatches, secret redaction, missing cookie on
media/SSE, CSRF, foreign Origin/Host, root traversal/symlinks, tamper detection, independent
ephemeral listeners, failed startup, CLI signal cleanup and reconnect without duplicate jobs.

Safari 27.0.1 and Chrome 154 on the M5 Pro both exchanged tickets, removed fragments, refreshed
using cookies and opened/played the registered H.264/AAC proxy. Native timeline controls sought
to approximately five seconds. With an explicit 60-second test lifetime, both showed the expired
session page and reopened with a fresh ticket while preserving the same worker/job. Normal
12-hour Safari playback was also captured after those expiry checks.

| Evidence | Chrome | Safari |
| --- | --- | --- |
| Connected session | [Screenshot](evidence/t26-chrome-session.jpg) | [Screenshot](evidence/t26-safari-session.png) |
| Authenticated media | [Screenshot](evidence/t26-chrome-media.jpg) | [Screenshot](evidence/t26-safari-media.png) |
| Expired session | [Screenshot](evidence/t26-chrome-expired.jpg) | [Screenshot](evidence/t26-safari-expired.png) |

Implementation follows FastAPI's [lifespan](https://fastapi.tiangolo.com/advanced/events/) and
[threaded synchronous-handler](https://fastapi.tiangolo.com/async/) contracts. All retained media
is synthetic engineering evidence, separate from human artwork and listening approval.
