# Local web app reference

The implemented UI uses TypeScript/Vite served by FastAPI on the same authenticated loopback
origin. Python owns authoring, compatibility, timelines, audio, rendering and saved documents.
The browser displays renderer-produced proxies/stills and sends guarded edits.

## Normal workflow

Navigation contains **Create video** and **Projects**, with technical tools under Advanced.
The Python-provided train/Tokyo/90-second preset and next action guide the work:

| Step | Behavior |
| --- | --- |
| Setup | Title, preset, optional scene changes and a current observed allowance/cost |
| Opening | Import stable reference, prepare/copy prompt, open Flow and import the native result |
| Continue | Watch candidate/join, confirm actual ending facts, accept or retry one focused defect |
| Finish | Exact verified export, optional continuous local WAV, full playback and YouTube delivery |

Saved progress resumes the same attempt after reload. Unknown external outcomes need
reconciliation before another submission. Only accepted descendants advance progress. New
variation reuses stable references/recipe while starting a fresh opening and review chain.

Generation is assisted; the installed app does not automate Flow's website. The
[operations guide](37-operations.md#make-a-90-second-train-video) describes actual controls;
[F12 evidence](evidence/f12-flow-workflow.json) separates engineering from real creative acceptance.

## Advanced tools

Existing project/asset import, still templates, layered scene/action editing, audio auditions,
preview, render jobs, cache, release and backup remain available for prior projects. See
[Advanced operations](37-operations.md#produce-an-advanced-layered-episode). The old ComfyUI
execution panel and standalone playback experiment are removed; their documents are historical.

## Interaction constraints to preserve

- Keep project/episode and selected frame context through navigation. Save coherent edits with
  revision guards; show pending/saved/failed states. Document undo creates new saved revisions.
- Render stills through Python for exact-frame review. Native browser playback and seek are
  approximate. Clearly label stale proxies; old verified output remains inspectable.
- Imports use bounded streamed copies or registered-root links. Browser storage contains
  disposable selection/preferences, not authoritative assets, episodes or approvals.
- Closing a browser tab leaves owned jobs running. Reconnect reads saved job state without
  resubmission. Cancellation may affect only the owned process; recovery retains verified chunks.
- Preserve keyboard operation, visible focus, readable scaling and non-color status labels.
  Keep technical details secondary and make each error point to a corrective action.
- Changes to approved content create new versions. Snapshot review, rights and release readiness
  remain factual; no UI interaction silently grants approval.

The [original T25 playback spike](24-browser-foundation.md) is historical test evidence.
Current product acceptance is recorded in [V1 acceptance](38-v1-acceptance.md).
