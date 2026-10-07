# Operating Tabi Story Studio

Use **Create video → Preview → Export** with a saved scene and your music. Import source
assets in **Asset library**. Python renders the complete video locally. Real TABI appearance,
music, rights and final creative review remain separate [acceptance gates](38-v1-acceptance.md).

## Install, check and launch

Follow [installation](32-installation.md) for the wheel, locked dependencies and tool paths.
Node is required to build the UI, not to run the installed application. From an installed shell:

```sh
tabi --config '/path/to/tabi.toml' setup-check --json
tabi --config '/path/to/tabi.toml' web --root studio='/path/to/Tabi projects'
```

Use a directory the Mac can access. The launcher registers only the specified roots, binds
loopback on a fresh port, checks its own worker's handshake and opens a single-use session.
Keep the launcher alive. Enter `open` for a fresh browser session, `stop` to finish current work
and exit, or Ctrl-C to cancel owned work while preserving verified chunks. Restart through the
launcher after changing tools; do not bookmark or share the initial authentication link.

In development, prefix the examples below with `.venv/bin/` if `tabi` is not on PATH. Use
`TABI_CONFIG=examples/settings.macos.toml` only when its exact tested Cellar paths exist.

## Prepare a scene once

1. Open/create a project in **Projects**. In **Asset library → Import media**, copy your master
   illustration (`still`), optional grayscale window mask (`mask`), scrolling panorama (`still`),
   transparent PNG frames (`sequence`) and music (`audio`). Record only known provenance and
   rights. Each changed asset needs a new version. Sequence files must be in the intended order
   and have the authored frame rate; the app displays their order before import.
2. Open **Create video → New scene**. Name the scene, choose the fixed master and frame rate.
   A still master by itself is a valid scene; motion is optional. The master determines the
   scene canvas. Keep TABI, furniture, hands, cup and other contact points fixed for the first pack.
3. For a moving view, choose a window mask and **Add scenery layer**. White reveals the view;
   black protects the window frame and every overlapping character/prop edge. A mask must be
   grayscale and match the visible master canvas exactly.
4. Choose a prepared strip and its repeat width. It must have the master height and at least
   **repeat width + master width** of pixels. The padding after the repeat width must copy the
   opening master-width pixels exactly; saving rejects mismatches. Compose interesting Tokyo
   districts along the strip with consistent perspective, horizon and lighting. This is prepared
   scenery, not automatic geographic routing. Up to three depth layers can share the travel speed.
5. For a blink or ambient movement, **Add animation loop**. Supply aligned full-canvas RGBA PNGs
   at the scene frame rate. Choose repeat interval and first-play delay in seconds. Python saves
   exact frame timings. The sequence must fit entirely inside its repeat interval; gaps reveal
   the unchanged master. Source frame bounds, an optional mask and opacity are under Details.
6. **Save reusable scene**. The scene is a draft configuration, not an approval. Editing it uses
   revision checks. **Make a new scene version** copies the configuration for a variation; imported
   media stays immutable. Previously created videos retain their original scene configuration.

Prepare blinks with clean underlying face coverage and authored eyelid states. A transparent
closed-eye line drawn over an open eye does not remove the original eye. Inspect the opening,
closing, edges and return to the base face. The app validates dimensions, alpha and timing but
cannot establish character likeness or make damaged generated frames look correct.

## Make a lo-fi video

1. Choose the saved scene in **Create video**. Its settings stay collapsed for reuse.
2. Enter a video title. Add finished music masters in playback order. Choose **Fit selected music**
   to use their complete combined length, or specify whole seconds up to six hours. Overlong music
   is rejected. A longer fixed video has silence after the tracks; music is never implicitly looped
   or stretched. No music creates a silent draft.
3. **Create video and open preview** saves an ordinary episode through Python. Choose a short
   frame range and **Generate proxy**. Play it, repeat playback if useful, and inspect exact frames
   for blinks, mask edges, panorama wraps and chunk joins. Browser seeking is approximate.
4. Open **Music** if tracks need arrangement, fades or loudness adjustments. Changed videos need
   a new preview. The soundtrack uses the shared sample-accurate mixer.
5. **Continue to export**: choose draft or production purpose, **Freeze saved episode**, choose
   output size/encoder/destination, **Estimate export storage**, then **Queue frozen export**. Jobs continue
   while the browser is closed; verified output has a player and download link. A production export
   requires real approved inputs, template and frozen snapshot review. Synthetic assets cannot be
   production approved.
6. For another video, return to **Create video**, keep the saved scene and change the music/title/
   duration. There is no generated-clip matching or repeat generation step.

A long panorama plus independent small loops avoids tying the scenery cycle to every blink.
Do not assume the end of an arbitrary video duration matches its beginning: review the full
scene's final-to-first join when a seamless whole-video loop is required. Frame/chunk continuity
within the video is deterministic; artistic continuity depends on the prepared assets.

The `tabi lofi list`, `tabi lofi save` and `tabi lofi create-video` CLI commands call these same
services. `save` takes a `SaveLofiScene` request (scene, expected revision, optional overlay
seconds). `create-video` takes an ID, title, scene reference/revision, optional ordered music
references and `duration_seconds` (`null` means fit music). Existing asset/author/render commands
remain available for advanced projects.

## Planned reference generation

The next phase adds reference selection, local asset generation, comparison and reusable
outfit/cabin/journey packs. See the [final plan](../PLAN.md) and
[generation contract](39-reference-assets.md). Those controls are not available yet; the
instructions here describe the implemented fixed-scene workflow.

Retired generation queues are never resumed. The R01 cleanup removes inspected obsolete local
experiments while preserving supplied source folders and the successful L05 pilot. Existing
external project files are not migrated or deleted by the app. Shared project, asset, audio,
render, backup and release services remain in use.

## First scene from an existing image

Import the supplied [train composition](assets/scenario/tabi-train-example.png) as a still, with
factual provenance and rights pending until reviewed. Choose it as the master in **New scene**,
leave scenery/loops empty, save, and create a short silent draft. This preserves all the pixels
of the existing artwork; it does not separate the window or animate the character. Moving scenery
and eye patches require prepared assets as described above. The supplied 1664×936 reference is
not a native 4K master or an approved production pack.

## Produce an Advanced layered episode

1. **Projects:** create a new folder or open an existing project. Reopening retains saved edits
   and immutable IDs. Use Relink after moving a project to another registered root.
2. **Assets:** import owned/licensed stills, transparent sequences and WAV masters. Record only
   known provenance, source frame rates, compatibility and rights. Inspect the actual media and
   its health report. Ordered sequence frames require their real authored rate; a PNG directory
   does not establish timing. New edits and relinks create new versions.
3. **Templates and packs:** use Create still scene template for one image. For layered animation,
   import prepared draft `scene_template` and `action_pack` documents from Assets. The [asset
   brief](01-assets.md), [contracts](03-contracts.md), [café example](33-cafe-template.md) and
   [activity packs](34-activity-packs.md) define masks, channels, anchors, poses and compatibility.
   Review media first, template second and pack third. In Assets → Review templates and action
   packs, inspect the exact JSON/hash and record your own review. Dependencies are rechecked.
4. **New episode:** choose the template, rational frame rate, canvas and integer frame duration.
   Select finished music in order. Complete songs are placed in integer samples; overlong music
   fails rather than being silently trimmed or stretched.
5. **Story / Timeline / Continuity notebook:** write the scene purpose, story beats, actions,
   prop state and carry-over notes. Add scenes and cuts; edit travel, weather and light curves.
   Body coverage, transitions, face ownership and outfit compatibility are compiler checks.
   Save edits before navigating. Undo/redo creates a new guarded revision.
6. **Audio:** inspect source waveforms; enter trims, gains, fades and ambience loops in prepared
   48 kHz samples. Review timing changes before Apply. Music resequencing preserves the visual
   story; conflicts require an explicit story or audio edit. Audition up to 120 seconds, inspect
   measured peaks/LUFS and listen. A meter reading is not listening approval.
7. **Preview:** generate a draft proxy. Use the exact-frame PNG controls for transitions and
   masks; browser seeking is approximate. Mark frames with review notes. Editing inputs makes
   earlier previews stale without deleting them. Review alpha edges, loops, face attachment,
   parallax gaps, weather placement, story continuity and musical boundaries.
8. **Renders:** freeze the saved episode. Draft/synthetic exports remain visibly labeled.
   Production requires approved inputs and a separate explicit snapshot hash review. Choose
   the profile and new `exports/` destination, inspect the storage estimate, then queue it.
   The default processes one export at a time. Progress counts verified frames; ETA excludes
   final assembly. Use Open verified export and Playback seconds to inspect the result.
9. **Release:** enter factual titles, credits, chapter frames, disclosure and an approved
   thumbnail. Inspect the public metadata and technical/rights report. Record creative and
   metadata reviews against the displayed hashes after actually viewing/listening. A draft
   bundle can retain blockers; Require ready for manual upload rejects them. Unknown ISRC/UPC,
   licence or claim information stays unknown. Upload only the appropriate `public/` files
   manually after your external platform checks; keep `private/` evidence private.
10. **Backup:** pause/finish jobs, export a private backup to a new folder on another volume,
    inspect it and restore to a new folder as a drill. Verify the restored media before relying
    on that backup. Keep the original masters separately too.

Detailed screen guides: [projects/assets](26-project-workflows.md), [story](27-editor.md),
[preview](28-preview.md), [audio](29-audio-editor.md), [queue/settings](30-render-queue.md),
[release/backup](31-release-and-backups.md).

## Reproducible supplied-reference draft

Run from this repository. These requests import the unchanged supplied train image with rights
pending, make a single-layer still and save a silent ten-second episode. They do not claim
separated artwork, animation or a finished musical story. Choose a new destination each run.

```sh
tabi project init '.local/Train reference draft' --title 'Tabi supplied reference draft'
tabi asset import '.local/Train reference draft' examples/workflows/train-import.json \
  --root "references=$PWD/docs/assets"
tabi author still-template examples/workflows/train-template.json --project '.local/Train reference draft'
tabi author create-episode examples/workflows/train-episode.json --project '.local/Train reference draft'
tabi author edit train-reference-draft examples/workflows/train-notebook.json --project '.local/Train reference draft'
tabi compile '.local/Train reference draft/episodes/train-reference-draft.json' \
  --purpose preview --project '.local/Train reference draft'
```

Copy the returned `snapshot_sha256` into the next commands. No production review is appropriate
for this draft. The supplied source has SHA-256
`01e4db852ceed7bc4d17708c3d181103d0699e5caed54bbc44eda1d83932473e`.

```sh
tabi jobs submit SNAPSHOT_SHA --preset 1080p --encoder h264_videotoolbox \
  --output exports/train-reference.mp4 --project '.local/Train reference draft'
tabi jobs work --once --project '.local/Train reference draft'
tabi jobs progress JOB_ID --project '.local/Train reference draft'
tabi jobs verify JOB_ID --project '.local/Train reference draft'
tabi web --root "draft=$PWD/.local/Train reference draft"
```

Use the actual returned job ID. `libx264` is available when hardware encoding is unavailable.
The local MP4 remains ignored by Git. For moving synthetic geometry and tone, generate a new
fixture project with `tabi fixtures --output NEW_FOLDER --profile activities`; its entire media
and registry are reproducible and explicitly unsuitable for publication.

## CLI authoring and review

Run `tabi GROUP --help` or `tabi GROUP COMMAND --help` for required arguments. JSON results go
to stdout; diagnostics go to stderr. Nonzero exit status must be handled before reading a
success result. Structural/plan rejection generally returns 2; failed service operations return
4; cancelled CLI work returns 5. Requests accept strict JSON or safe YAML, reject duplicate keys,
unknown fields and YAML aliases, and are bounded to 16 MiB. Document imports also reject
incompatible schema versions.

| Operation | Shared command |
| --- | --- |
| List authored documents | `tabi author catalog --project PROJECT` |
| New episode | `tabi author create-episode REQUEST --project PROJECT` |
| Read saved episode | `tabi author show EPISODE_ID --project PROJECT` |
| Semantic edit | `tabi author edit EPISODE_ID REQUEST --project PROJECT` |
| Timeline lanes | `tabi author lanes EPISODE_ID --project PROJECT` |
| Install draft document | `tabi author install DOCUMENT --project PROJECT [--expected-revision N]` |
| Still template | `tabi author still-template REQUEST --project PROJECT` |
| New provenance/compatibility version | `tabi author asset-version ASSET_ID OLD_VERSION REQUEST --project PROJECT` |
| Inspect template/pack and hash | `tabi author metadata KIND ID VERSION --project PROJECT` |
| Explicit metadata review | `tabi author review KIND ID VERSION --reviewed-hash HASH --reviewer NAME --note NOTE --project PROJECT` |
| Propose/apply audio edits | `tabi audio propose EPISODE_ID REQUEST --project PROJECT` / `audio edit` |
| Audition saved audio | `tabi audio audition EPISODE_ID --expected-revision N --start-sample FIRST --end-sample END --project PROJECT` |
| Local preferences | `tabi preferences show` / `save REQUEST` / `tools REQUEST` |
| Measured render progress | `tabi jobs progress JOB_ID --project PROJECT` |

`KIND` is `scene_template` or `action_pack`. `metadata` reports the exact
`review_content_sha256`; do not guess hashes or edit approval JSON. Review source assets with
the existing `asset check` / `asset approve` workflow first. An approved version cannot change;
create a newer version with revision zero and `approval: {status: draft}`. Asset-version requests
contain `version`, factual `provenance` and `compatibility`.

An editor request contains the revision observed from `author show` and one shared command:

```json
{"expected_revision": 0, "command": {"kind": "title", "title": "The Last Train Home"}}
```

Other supported kinds are `scene`, `append_scene`, `move_cut`, `move_action`, `change_pack`,
`put_action`, `remove_action`, `put_curve`, `remove_curve`, `continuity`, `beats` and `replace`.
Their typed request models live in `src/tabi/core/editor.py`; full documents use the published
schemas. `replace` can restore previously saved content as a new revision. An invalid semantic
edit leaves the existing document untouched. Existing draft imports require both the document's
current `revision` and `--expected-revision`; first installation omits that flag.

An audio request contains `expected_revision`, complete `tracks`, and optional
`resequence_music: true`. Each track uses the same `TrackPlacement` contract as an episode.
`propose` reports whether it fits without saving; `edit` repeats validation and saves atomically.
`audition` returns a generated WAV path and verified mix report under `audio/previews/`.

For preferences, start from `preferences show` and save
`{"preferences": <current document with edits>, "expected_revision": N}`. Use null only for
the first save when `preferences_saved` is false. Tool requests contain `ffmpeg`, `ffprobe` and
`expected_hash` equal to the observed `config_sha256` (null only when no config exists). Exact
previous bytes are backed up. Environment overrides still take precedence after a restart.

Existing [compile/frame/preview/snapshot](15-preview-workflow.md), [audio](16-audio.md),
[jobs](19-jobs.md), [cache](21-cache-storage.md) and [release](23-release-preparation.md)
commands complete the Advanced headless workflow. Use `tabi lofi --help` for the guided route.
Production
`snapshot review` returns a **new** snapshot SHA; submit that reviewed SHA, not the earlier draft.

## Troubleshooting and recovery

| Symptom | Action that preserves work |
| --- | --- |
| Missing FFmpeg/ffprobe or codec | Run `setup-check`/`doctor`; correct the actual installed paths and restart. Encoder advertisement alone is not a successful render test. |
| Stale/altered frontend | Rebuild the distribution or reinstall a verified wheel. Do not bypass the bundled hash check. |
| Expired session or worker unavailable | Use `open` in the live launcher, or restart it and reopen the saved project. Reloading a page is not a render submission. |
| Port occupied or readiness mismatch | Let the launcher use a fresh ephemeral port. It must not adopt or kill an unrelated process. |
| Stale revision/hash | Reload the saved document, compare your changes and apply them to the current revision. Do not force-write over another tab. |
| Source missing / external drive disconnected | Reconnect the original drive, or relink matching bytes from a registered root. Changed bytes need a new asset version. |
| macOS denies a folder | Choose a permitted project/source folder or grant access yourself through normal OS controls. The app cannot bypass an OS denial. |
| Render failed or worker crashed | Inspect the job diagnostic; correct the cause, then Recover/Resume. Verified chunks are retained. Recovery checks ownership and never kills a saved PID blindly. |
| Tool/pipeline/asset fingerprint changed | Preserve the old job and start a new snapshot/job with current inputs. Do not reuse chunks across incompatible fingerprints. |
| Low disk space | Pause work, inspect estimates and managed cache, back up masters, then prune the proposed unprotected entries. Estimates are conservative planning, not an exact peak-disk promise. |
| Audio over full scale or duration conflict | Lower gain or explicitly edit trims/placements; preview/listen again. Extend the story explicitly if needed. |
| Output destination already exists | Choose a new output name. Final files are published only after verification and are never silently clobbered. |
| Backup cannot restore | Preserve the original backup, inspect its manifest/hash error and create a fresh complete copy. Restore always targets a new folder. |

After an interrupted CLI render:

```sh
tabi jobs list --project PROJECT
tabi jobs recover --project PROJECT
tabi jobs resume JOB_ID --project PROJECT
tabi jobs work --once --project PROJECT
tabi jobs verify JOB_ID --project PROJECT
```

Only resume after the prior owner has stopped. Keep exact tool/app versions during a job. The
queue decides which chunks remain valid; do not edit its journal/checkpoints by hand. Pause and
cancel control the owned process, while stopping a preview does not cancel an unrelated export.

## Storage, privacy and release boundaries

Project folders hold source copies, versioned registry data, drafts, `.backups`, snapshots,
previews, jobs, exports and release preparations. Project `.cache/tabi-v1` is managed disposable
work; global `cache_root/launcher` holds preferences and recent paths. Cache cleanup never
authorizes removal of source artwork. Approved inputs and snapshots are immutable.

Private backup bundles include music and rights/review evidence and are not encrypted. Copy
the whole bundle; do not treat a public release folder as a project backup. A fresh Git checkout
contains neither ignored MP4s nor the generated `.local` evidence projects. Keep those on backed-up
media storage. **Never commit any MP4**, including uppercase extensions, FFmpeg binaries or
unreviewed commercial fonts.

Publication stays manual. The application makes no platform eligibility, monetization or
distribution-acceptance guarantee. Check current external policies at release time using the
[publishing references](08-sources.md), and record factual decisions in the release record.
Actual Tabi style, motion, original music, rights, disclosure and final creative acceptance must
come from their authorized reviewers, not from synthetic tests.
