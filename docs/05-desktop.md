# Desktop pages and interaction specification

## Visual treatment

Use a calm dark interface with soft neutral surfaces, lavender/peach accents taken from approved Tabi artwork, restrained contrast and icons with short labels. The production app should make episode structure understandable without resembling a full professional video editor. Keep technical diagnostics in expandable panels.

Proposed initial theme tokens: background #171820, surface #22232D, raised surface #2D2E39, text #ECE8E7, muted text #A8A4B1, lavender accent #B3A1D4, peach accent #D8AE9A. These are UI proposals, not replacement colors for Tabi. Verify readable contrast, focus visibility, scalable text and keyboard operation.

Navigation: Projects, Assets, Story, Audio, Preview, Renders, Release. Settings is a persistent utility entry. Within an episode, retain selected frame and zoom when moving between Story and Preview.

## Page specifications

| Page | Main content and actions | Required states |
| --- | --- | --- |
| Projects | Recent local projects, create/open, missing-path relink, backup/export | Empty, loading, unavailable disk, incompatible version |
| New episode | Title, Story/Session/Track, scene template, fps/resolution, ordered music | No assets, draft inputs, duration conflicts |
| Asset library | Pack cards, type filters, version/approval badges, import, inspect, normalize, approve | Missing reference, corrupt media, rights pending |
| Asset inspector | Source/proxy, alpha background toggle, pivots/masks, action poses, provenance | Incompatible camera, new version, failed normalization |
| Story editor | Scene cards, story beat text, duration, transition, persistent objects | Gap, overlap, missing transition, unapproved asset |
| Timeline | Lanes for scenes/music/Tabi/weather/light/speed, zoom, frame snapping, inspector | Invalid action, unresolved duration, pending preview |
| Audio | Ordered tracks, waveform proxies, trims, gain, fades, ambience and report | Silence gaps, clipping, missing WAV, pending analysis |
| Preview | Cached renderer proxy, play/pause, seek, frame step, mark review issue, render range | Stale proxy, job pending, missing player, canceled render |
| Render queue | Profile, folder, disk estimate, progress, pause-after-chunk/cancel/resume, logs | Queued, rendering, interrupted, failed, verified |
| Release preparation | Export status, title/description/chapters, thumbnail and rights/disclosure notes | Incomplete rights, unreviewed creative output, draft bundle |
| Settings | Tool paths, worker status, media roots, cache budget, theme, export defaults | Unsupported FFmpeg, offline generation, no disk space |
| Continuity notebook | Episode summaries and carried objects, manual add/edit/link | Unresolved object, deliberately discontinuous story |

Each page needs a concrete implementation task, UI screenshots and functional verification. Wireframe mockups are not included as finished image assets in this package; T25 requires all page wireframes before desktop implementation.

## Editor behavior

Represent scenes as a readable storyboard above the timeline. Clicking a scene selects its interval and relevant parameters. Dragging a block snaps to frames and applies one undoable command. Curves use typed keyframes with explicit interpolation; expose simple presets first, and allow numeric editing in an inspector. Reject impossible actions immediately with a useful message.

Undo/redo is command-based for document edits; importing large media or rendering a job is not silently undone. Save drafts atomically with autosave and last-known-good backups. Closing with unsaved edits or active jobs displays the actual consequence, without requiring confirmation for ordinary reversible edits.

Set musical markers manually or from imported metadata, rather than claiming automatic story generation. Reordering tracks recalculates placements and offers a preview of affected scenes. Never silently retime Tabi actions or trim the song to hide a duration mismatch.

## Preview semantics

Proxy playback displays snapshot/hash and stale status. Edits invalidate affected preview ranges; keep the old proxy playable as explicitly stale. Render still-frame requests for precise scrubbing, debounce rapid requests, and cancel only superseded preview jobs. Proxy and final use identical compiler semantics and media versions.

Local media player selection requires a macOS technical spike. Embed playback if the tested player can seek and package reliably; keep a system-player fallback and clear limitations. Waveforms are derived proxy data, not the source audio. The timeline cursor maps to global frames regardless of proxy timestamp rounding.

## Job interactions

Render approval captures a snapshot; edits afterward create a new version and do not mutate the running job. Progress combines completed frame counts with current chunk progress. ETA is measured and labeled approximate. Cancel terminates the owned subprocess safely and keeps verified chunks. A pause-after-chunk option completes the current chunk before stopping; do not advertise instant pause if unavailable.

If the worker dies, show interrupted state, offer diagnostics and restart/recover. Desktop handles worker version mismatch explicitly. UI must remain responsive during probing, hashing, waveforms and renders; run I/O work outside the UI thread.

## Accessibility and completion

Support keyboard navigation, visible focus, space for play/pause, frame-step keys, undo/redo, standard macOS file dialogs, descriptive errors and readable tooltips. Do not depend on color alone for draft/approved/error badges. Test on scaled displays and smaller laptop windows. Add no fake analytics or invented platform status.
