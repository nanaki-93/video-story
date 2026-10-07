# Operating Tabi Story Studio

The normal app guides **Setup → References → Shots → Finish** from Create video.
The app and CLI share Python services; generation happens in Google Flow. Assets and music
stay on this Mac. [Acceptance](38-v1-acceptance.md) separates tested engineering from real
TABI appearance, original music and publication reviews still pending.

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

## Make a 90-second train video

1. Launch the app, choose **Projects**, and create/open a local working folder. Return to
   **Create video**. Setup starts with the train/Tokyo/90-second preset; optional changes are
   under Edit settings. Enter the actual remaining Flow allowance, displayed fresh-shot cost
   and a spending ceiling. The app cannot read your account or buy credits.
2. **References:** use your approved train image as the source for the copyable image prompts.
   Prepare/import two named wide/medium views for each district: Sumida, Yanaka, Akihabara, Ueno,
   Shinjuku and Odaiba. All twelve are reviewed before video begins. Optional window descriptions
   are editable in Setup. Each image comes from the approved art; it does not need the preceding
   generated clip's ending.
   Keep TABI's full gills, connected neck, markings, outfit, train layout and cup design; check
   the air is clear. Confirm the planned scenery, window perspective and visible starting facts.
   The cup starts on the table with hands resting. Hidden facts stay unknown. These image reviews do
   not establish commercial rights. Original artwork remains unchanged.
3. **Start new shot in Flow:** download the exact image shown, choose Frames to Video, attach
   it and select an 8-second landscape result. Copy the saved motion prompt. Download and import
   the new native clip; record the actual model shown in Flow. A preceding-shot player is cut
   context, not the input to this generation. The app saves the attempt before the handoff.
4. **Review:** the app proposes the first 180 frames (7.5 seconds) of each eight-second source.
   Watch the entire selected candidate and the join/camera-cut player. Confirm the actual
   ending facts and compare TABI/props with the assigned reference. Check the expected district,
   level horizon, fixed window/table occlusion, travel direction and foreground/background
   parallax. Scenery must progress through the ending rather than repeat or reset within a shot.
   Check the shot-ending frame when
   offered; the app trims to that reviewed outpoint. A cup still held cannot jump to a table
   across the cut. Reject visible dots, distorted gills/mouth, changing objects, freezes or an
   incomplete action. Choose one correction for Retry; the full note remains in history.
   A retry uses the same clean image. The app never approves appearance. An undersized independent
   shot stops for attention or an explicit restart; it cannot continue with Extend.
   **Keep a section of this clip** offers integer start/end frames (end exclusive). Choose
   **Use this section**, then watch the rebuilt selected player and join before accepting.
   The original remains available separately. A native continuation must retain its opening;
   an early ending can be kept only when it completes the shot or video, so Extend cannot
   silently continue from a different, discarded parent ending.
5. **Finish:** keep silent or import/select a local WAV. A longer master needs the explicit
   first-video-length trim confirmation; a short master is not automatically looped. Export
   and watch the complete verified draft. Output preserves the measured picture resolution
   and frame rate, using H.264 and optional stereo 48 kHz AAC. Music is never uploaded to Flow.
6. **Prepare YouTube delivery:** record factual title, concept, rights, exact model/terms,
   disclosure, thumbnail and listening/creative reviews. Inspect blockers and export the
   existing public/private bundle. Publication remains manual. Keep private evidence private.

The default story is twelve independent 7.5-second shots, with two framings for each illustrated
district: Sumida River/Skytree, Yanaka rooftops,
Akihabara shopping streets, Ueno trees/pond, Shinjuku skyline and Tokyo Bay/Rainbow Bridge.
TABI alternates quiet rest and watching with barely perceptible breathing; the cup stays on
the table. District cuts compress travel time rather than claim a surveyed railway journey.
Descriptions draw on the [official Tokyo district guide](https://www.gotokyo.org/en/destinations/index.html),
not imported photographs. Each starting image must contain its own planned view; assigning
different keys to identical image bytes is refused when the exterior descriptions differ.
There are no native extensions or generated end-to-start matches in this preset. Existing
six-shot scenery and drink/breathing projects retain their original plan, media and hashes.
Where a saved recipe allows **Extend this shot in Flow**, use the exact accepted in-shot parent,
its focused prompt and the currently supported model/cost. Import only the new clip. The cap
remains one extension in U04 and two for saved pickup/sip/return actions. Review its opening
and ending before accepting; a discarded native ending cannot become an Extend parent.
The app counts actual reviewed frames; it never loops old footage or pads a freeze to fill a duration.

Stop saves progress; reopening resumes the same attempt. Reconcile an unknown Flow result
before submitting again. During the real trial, Flow sometimes showed “Prompt must be provided”
while its first Extend was actually generating. Wait for a definitive result and inspect the
saved scene before submitting again; the app cannot see duplicate requests made in Flow.

At a retry limit, **Raise retry limit** allows one more correction per action, up to three,
if the next request fits the existing credit and attempt caps. It does not generate or change
the credit ceiling. For persistent drift within an idle partial shot, expand **Start this shot
again** and restart from its clean image. Earlier completed shots stay active; all old takes,
reviews and credit reservations remain in history. The new opening still counts as a retry.
Unknown results and pending reviews must be resolved first. A changed cup may require restarting
pickup, rather than repeatedly extending a sip with hidden prop drift. Confirmed handle-free
cup actions now use both existing hands around the body and explicitly preserve the absent handle.

If the hard retry, extension or credit limits still stop progress, retain the evidence and
review the plan. Do not label a short accepted run as a finished 90-second video.

After **Stop and save progress**, **Export reviewed portion** creates a silent partial preview
from the active accepted clips. It keeps the original target, remaining shots, attempts and
reviews intact. Playback and downloads are labeled partial; rejected or pending takes are
excluded. The complete-video export still requires every planned action and the full duration.
CLI users can request the same service with `flow export --partial-preview` after pausing.

The [U03 target-Mac trial](evidence/u03-tabi-app-trial.json) completed and downloaded a silent
90-second draft through this path. It used 12 native clips, 24 app attempts and 1085 actual
included credits, including 15 from earlier duplicate Flow submissions. All 2160 frames and
timestamps were independently checked; the complete video played in Chrome. The closing
breath now keeps seated hips, resting hands and unchanged clothing coverage. Generated acting
and cup prints can still vary, and clean camera starts reset the exterior. Review these
visually; this run does not establish automatic quality or 30-video monthly capacity.

Marco finds U03 interesting but rejects its final panorama and repetitive exterior, and
requests different Tokyo districts with less trial and error. Eight of the ten rejected takes
were cup handling or deep breathing. The new default avoids those actions; the reduction in
real retries, image-preparation effort and total credits remains to be measured. Marco selected
independent cinematic shots with deliberate cuts; U05 therefore removes all extensions from
new videos. Twelve reference images need initial preparation and twelve fresh generations may
cost more than six starts with cheaper continuations. Unchanged variations can reuse reviewed
images. The U03 MP4 is preserved; new guidance does not repair its pixels.

For another setting/outfit, use **New variation** and enter fresh allowance/cost observations.
It copies stable settings and resets the review chain. Changing one shot's scenery or framing
clears only that reference and retains unaffected images. Character/outfit/interior or shared
outside-movement changes clear references so new matching views must be imported before generation.
Café/walking and each new outfit need visual
qualification. Almost entirely automatic Flow control has not been established; the handoff
above is the supported assisted workflow. No additional paid provider is configured.

On a saved extension-based video, **New Tokyo video without Flow extensions** creates the current
twelve-shot plan as a separate variation. Review its settings and fresh-shot allowance before
creating it. Matching U04 references retain their reviews; the six additional framings need
their own starting images. Changed identity, outfit, carriage, framing or scenery invalidates
affected reuse as usual. Ordinary **New variation** still copies the saved plan.

Existing saved single-shot episodes retain Opening/Continue and their original hashes. For
CLI automation, `flow status` returns shot progress and the next reference instructions;
`flow reference --key sumida --state facts.json --note 'review findings'` imports a reviewed
view (also supply project, source, title and revision). `flow review --correction particles`
stores one focused retry selection with the full review note.

Flow workflow checked 7 October 2026: [Flow model support](https://support.google.com/flow/answer/16352836?hl=en)
documents eight-second Veo Frames to Video and model-specific Extend support;
[Flow input guidance](https://support.google.com/flow/answer/16353334?hl=en) describes starting/ending
frames. The [Flow Agent](https://support.google.com/flow/answer/17093911?hl=en) supports planning
and batch variations inside Flow, with generation consuming credits. This does not establish
an external consumer-account connector for the local app or remove visual review. Camera cuts and
clean starts reduce dependence on an imperfect preceding clip; they cannot repair existing
damaged pixels or guarantee a usable generation. Commercial terms and source rights are checked
again at delivery; no provider change or new paid dependency is part of this update.

## First scene from an existing image

This Advanced walkthrough retains the earlier layered renderer. Open the named tools through
**Advanced**; it is separate from the normal Flow sequence.

This works in the current app. Use the supplied
[train composition](assets/scenario/tabi-train-example.png) for a **static, silent draft**.
The image already includes Tabi, the table and the window scenery. This exercise does not
separate those parts or animate the character.

1. In **Projects**, create/open a project. In **Assets → Import media**, choose that PNG.
2. Set **Asset ID** to `train-reference` (or another unused ID), **New immutable version** to
   `1.0`, and **Media type** to `still`. The sequence/video fps fields are ignored for stills.
   Set **Origin** to `User supplied`, keep **Commercial rights** pending unless actually
   confirmed, and leave unknown creator/history fields empty. The existing evidence default
   `[]` and generation default `null` can stay as they are. Click **Copy and import selected files**.
3. The inspector opens. Scroll to **Use as a still scene**, retain the proposed template ID
   and version, and click **Create still scene template**. No proxy preparation, compatibility
   JSON or approval is required for this draft.
4. Open **New episode**, enter a title and choose the new scene template. Keep the generated
   episode ID, 30 fps, 1920×1080 canvas, `idle` pose, seed `0` and **300 frames** (ten seconds).
   Leave music empty for this visual check. Click **Create draft episode**.
5. Open **Preview**, keep the saved episode selected and render its range from frame `0` to
   `300`. Play the result and inspect the exact-frame image. The draft label is expected.

For animation, importing the breath/drink PNGs is only the first step. Their original timing,
loop/action behavior, matching foreground and scene compatibility still need preparation.
Layered scenes currently require authored template/action-pack documents. The supplied train
still cannot serve as a clean background for a second character without duplicating Tabi.
See the [asset review](12-tabi-art-review.md) and [source audit](09-implementation-review.md).

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
commands complete the Advanced headless workflow. Use `tabi flow --help` for the guided route.
The optional ComfyUI commands have been retired. Production
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
| Flow handoff unavailable | Save progress. Reopen the exact accepted parent in Flow; reconcile any pending result before another request. There is no automatic paid API fallback. |

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
