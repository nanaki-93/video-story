# T25 browser foundation and playback

Historical T25 evidence: at this checkpoint the shell had twelve design pages, eleven of
which were wireframes. T27–T32 subsequently implemented the product screens. Use the
[current UI reference](05-webapp.md) and [operations](37-operations.md) for normal work.
The standalone playback experiment was removed in F13 after the authenticated production
player replaced it. The commands and screenshots below are historical evidence.

## Build and run

```sh
cd web
npm ci --ignore-scripts
npm run check
npm test
npm run build
cd ..
.tools/bin/uv run python scripts/web_playback_spike.py \
  --config examples/settings.macos.toml --project .local/t25-browser \
  --job job-83c9ff1bf8f848c2b9e168a626415b69
```

That job ID is local evidence, not a fresh-checkout fixture. Any complete synthetic-test job
with AAC, a full snapshot range and at most 1,800 frames can be supplied. The script verifies
its bytes and decoded media before serving it on an ephemeral loopback port. It exposes only
that video, its Python-rendered stills and the built frontend. This test server is not the
authenticated production service; T26 replaces it. Ctrl-C closes this owned test server.

Node 25.8.2/npm 11.14.1 built the frontend on the target Mac. `.node-version` and the npm lock
pin the tested environment: TypeScript 7.0.2, Vite 8.3.2, AJV 8.20.0, ajv-formats 3.0.1,
json-schema-to-typescript 16.0.0 and Prettier 3.9.9. The local npm cache avoids changing the
user's existing cache permissions. All 36 Python JSON Schemas generate checked DTOs and
precompiled validators; strict unknown-field, major-version and integer-frame rules survive
the browser boundary. Validators need no runtime eval and comply with the restrictive CSP.

Node is only a build dependency. Python serves the static output; no CDN, remote font,
service worker or Node runtime is required. The initial all-schema validator bundle is
1.52 MB minified / 135 KB gzip and triggers Vite's size warning. Later page splitting can
reduce initial parsing cost. See [Vite's official guide](https://vite.dev/guide/) and
[AJV's schema guide](https://ajv.js.org/guide/schema-language.html).

## Observed target-Mac checks

The [verified proxy report](evidence/t25-browser-proxy.json) records an actual 10-second,
300-frame, 960×540 H.264/AAC render with 480,000 audio samples. Source and output hashes
are visible in the UI. It uses geometric synthetic art and an owned test signal, not Tabi
artwork or approved music. The MP4 remains ignored under `.local/t25-browser/exports/`.

- Chrome 154: native playback, midpoint seek and pause; 284 decoded frames and nonzero
  decoded audio RMS 0.01130. [Downloaded observations](evidence/t25-chrome-playback.json),
  [desktop screenshot](evidence/t25-chrome-preview.jpg).
- Safari 27.0.1: native playback, midpoint seek and pause at 7.605 seconds; 68 decoded
  frames after seeking and audio RMS 0.01119. [Accessibility observations](evidence/t25-safari-playback.txt)
  and [visible native-player screenshot](evidence/t25-safari-preview.png). Safari initially
  suspended animation callbacks while the window was in the background; media events and
  a 250 ms observation timer now update diagnostics. Bringing the Safari window to the
  front also exposed its composited video layer to the screenshot capture. The earlier
  black background-window capture was not treated as visible playback evidence.
- Python returned exact frames 151 and 152 with matching one-frame reports. Arrow keys
  step renderer stills; typing in a number field does not trigger the global shortcut.
- The [700-pixel layout](evidence/t25-chrome-compact.jpg) has a document scroll width of
  exactly 700 pixels after fixing the sidebar grid minimum. Native controls, focus rings,
  labels and a skip link are retained. User aesthetic and listening review remain separate.
- [Actual HTTP checks](evidence/t25-http-checks.json) verify MIME, closed/suffix byte ranges,
  HEAD, unsatisfied ranges, foreign Host/Origin rejection and traversal rejection.

`make check`: 36 schemas and 229 passing unit checks, Ruff clean. Browser `check`, two
contract tests and the production build pass. The actual proxy was rendered and reverified;
the core renderer is unchanged by this task.

## Reviewable page wireframes

| Page | Screenshot |
| --- | --- |
| Projects | [Projects](evidence/t25-wireframe-projects.jpg) |
| New episode | [Setup](evidence/t25-wireframe-setup.jpg) |
| Asset library | [Assets](evidence/t25-wireframe-assets.jpg) |
| Asset inspector | [Inspector](evidence/t25-wireframe-inspector.jpg) |
| Story | [Story](evidence/t25-wireframe-story.jpg) |
| Timeline | [Timeline](evidence/t25-wireframe-timeline.jpg) |
| Audio | [Audio](evidence/t25-wireframe-audio.jpg) |
| Preview | [Working prototype](evidence/t25-chrome-preview.jpg) |
| Render queue | [Renders](evidence/t25-wireframe-renders.jpg) |
| Release | [Release](evidence/t25-wireframe-release.jpg) |
| Settings | [Settings](evidence/t25-wireframe-settings.jpg) |
| Continuity notebook | [Notebook](evidence/t25-wireframe-notebook.jpg) |

## File access and distribution decisions

The production UI uses a server-backed chooser scoped to launcher-registered roots and
streaming file inputs for selected media. Browser file inputs do not reveal reliable local
absolute paths; a mandatory File System Access API would exclude Safari. Authenticated
same-origin artifact URLs will supply native range playback without URL credentials.
T26 implements bootstrap/session/CSRF and ownership; T33 packages the built assets with
Python and tests installed launch outside this checkout. T25 does not expose private media,
uploads, project mutation, approval or publication.
