# Local web app reference

The implemented UI uses TypeScript/Vite served by FastAPI on the same authenticated loopback
origin. Python owns authoring, compatibility, timelines, audio, rendering and saved documents.
The browser displays renderer-produced proxies/stills and sends guarded edits.

## Current screens

| Current destination | Implemented behavior / guide |
| --- | --- |
| Projects, New episode | Local folders, recent projects, saved episodes and explicit setup — [guide](26-project-workflows.md) |
| Assets, Asset inspector | Import, inspect, new versions, still-template creation, metadata and explicit approval — [guide](26-project-workflows.md) |
| Story, Timeline, Continuity notebook | Shared scene/action document, semantic edits and continuity — [guide](27-editor.md) |
| Audio | Ordered tracks, sample edits, auditions and factual release metadata — [guide](29-audio-editor.md) |
| Preview | Rendered proxies, stale detection and exact frame PNGs — [guide](28-preview.md) |
| Renders, Settings | Frozen export plans, durable queue, recovery, tool settings and cache — [guide](30-render-queue.md) |
| Release | Public/private preparation, manual reviews and backup/restore — [guide](31-release-and-backups.md) |

The twelve navigation entries are useful tools but do not form a clear beginner journey.
The [new workflow plan](tasks.md) proposes guided asset import, a visual scene builder and
standard defaults. That proposal supersedes the original navigation design; it is not yet an
implemented UI. The [first-scene walkthrough](37-operations.md#first-scene-from-an-existing-image)
uses controls available today.

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
