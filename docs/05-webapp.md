# Local web app reference

The implemented UI uses TypeScript/Vite served by FastAPI on the same authenticated loopback
origin. Python owns authoring, compatibility, timelines, audio, rendering and saved documents.
The browser displays renderer-produced proxies/stills and sends guarded edits.

## Normal workflow

Navigation exposes Create video, Asset library, Preview, Music, Export and Projects.

| Step | Behavior |
| --- | --- |
| Import | Stream local stills, grayscale masks, ordered transparent PNG sequences and music into the asset registry |
| Save a scene | Choose master, fps, optional scenery layers, optional loop intervals/delays and save with revision checks |
| Make a video | Reuse a scene, order complete tracks, set seconds or fit music; Python creates the episode |
| Preview | Render a real proxy or exact global frame; repeat playback to inspect movement and joins |
| Export | Freeze, review as required, estimate and queue the shared local render job; play/download verified output |

Scene settings collapse once saved. Dirty scene forms block video creation and warn before
navigation; a late save cannot clear newer changes. IDs/versions and precise source bounds
are secondary controls. Source approvals and production reviews are not inferred from saving.
Seconds are a transport convenience only; persisted schedules remain integer frames/samples.

## Advanced tools

Asset details/review, still templates, layered story/action editing, notes, release and backup
remain available. They serve existing projects and production review rather than duplicating
the normal scene workflow. The old whole-scene generation queue is removed and never resumed.
The app does not migrate or delete records in older external projects.

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

The planned reference-generation and modular-pack controls are specified in [the final plan](../PLAN.md) and [reference asset contract](39-reference-assets.md).
Current product acceptance is recorded in [V1 acceptance](38-v1-acceptance.md).
