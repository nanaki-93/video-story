# Current progress

Updated 4 October 2026 (Asia/Manila).

## Current state

The Python core, CLI and local web application implement the V1 production services. The last
full engineering gate recorded **296 unit checks, 61 real-media checks and four frontend tests**,
plus schema/type/build/package checks and installed Mac/browser verification. These are the
recorded T38 results, not new test runs for the documentation change.

[V1 acceptance](38-v1-acceptance.md) is the authoritative engineering/creative acceptance record.
Approved real character/environment packs, original music, pilot/story listening and visual
review, and publication decisions remain pending. Simplifying the app does not approve them.

## T39 — documentation cleanup and workflow plan

Status: complete; application redesign remains planned.

Marco clarified that the priority is importing existing Tabi images/animation files with useful
defaults, then understanding how to build a scene from them. New artwork generation is outside
the requested workflow. The [plan](tasks.md) starts with those tasks and continues through music,
preview and export. The [task index](tasks/INDEX.md) is the single execution entry point.

Cleanup consolidates the 38 old task files into [one archive](archive/v1-tasks.md), moves the
chronological build log into [history](archive/v1-progress.md), removes the redundant agent
kickoff template, and replaces obsolete implementation orders, speculative command/route lists
and sprawling navigation with current references. The [documentation guide](README.md) gives
short paths into setup, first-scene help, implementation work and technical evidence.
Source artwork, evidence reports, screenshots, working project media and application code are
preserved. A concrete [current-app image walkthrough](37-operations.md#first-scene-from-an-existing-image)
explains the available still-scene path and its animation limits.

Verification: `.venv/bin/python .local/docs-cleanup/check_docs.py` passed for **53 Markdown
files and 734 local paths/fragments**, all **38 archived task bodies**, the complete rebased
V1 log, and all **nine planned tasks / 127 target-file references**. Dependencies are ordered;
new target files are declared explicitly. `git diff --check` passed. Only Markdown changed,
zero MP4s are tracked, and the pre-existing staged IDE patch is unchanged. The local audit
script and baseline copies stay under ignored `.local/docs-cleanup/`.

No renderer regression run is needed for this documentation-only change. The guided workflow's
browser and media checks remain part of T48, and no redesigned UI screenshot or runtime
behavior is claimed here.

## T14 — continuous train draft follow-up

Status: corrected draft rendered and technically verified; Marco's visual acceptance remains
pending. The first 90-second montage was rejected because character shots and baked-in scenery
jumped. The replacement uses one seated idle/blink source, a window mask derived with built-in
imagegen under Marco's explicit authorization, and the supplied Yanaka panorama moving on the
episode's independent travel curve. The original character/cabin pixels and source files are
preserved. Larger sip/read actions are not part of this consistent-pose draft.

The local app exported **2700 frames / 90 seconds at 1920×1080, 30/1 fps**, with the selected
Lo-Fi-Walz music, stereo 48 kHz AAC, and the draft label. The eight-second app preview crossed
the first idle repeat; the full export was opened, played and sought in Chrome. Independent
strict decode/hash verification passed. All **15 sampled panorama positions** matched their
expected global offsets, and the character remained aligned at all **four animation repeats
and two render chunk joins**. [Recorded preparation and verification](evidence/t14-continuous-train-draft.json).

Project: `/Users/marcoandreose/Tabi Story Studio/projects/Tabi train test 90s`.
Episode: `tabi-train-continuous-90s`. Output:
`exports/Tabi-Continuous-Train-90s-Lo-Fi-Walz-DRAFT.mp4`. Preparation scripts, generated-mask
prompts, source hashes and detailed checks are retained under `sources/continuous-train-v1/`;
local working evidence is in `.local/train-continuous/`. The rejected montage is retained for
comparison. No MP4 is tracked, no application code changed, and the staged IDE patch is preserved.

This panorama pass travels 1260 design pixels without wrapping. It does not establish a
seamless long-form environment or an approved activity pack. The guided plan now explicitly
requires independent scenery motion and a complete-scene loop review; T40–T48 remain planned.
Human art/music/rights and publication acceptance are still open.

## T14 — actions and faster scenery follow-up

Status: saved working draft; media integrity verified, animation polish still required.
Marco accepted the continuous-scene direction, identified a cup-lid cropping error, and asked
for more movements, more exterior views and faster travel. The new scene places the complete
TABI/cup foreground **above** the independently scrolling exterior, over one restored empty
cabin. Built-in imagegen prepared the empty cabin and glass matte from the supplied reference;
the character imagery comes from the supplied cutouts/read/look footage. Originals and the
earlier drafts are retained.

TABI breathes, leans down to read, picks up/sips/returns coffee, turns to watch the window, and
returns to the relaxed pose. A **900-frame / 30-second routine repeats three times** with
identical first/last foreground frames. Source read/look/drink clips measure 25/1 fps and
129 frames; their presentation is explicitly conformed to 30/1 fps. The untimed breath cutouts
receive a newly authored cadence. Short foreground motion bridges soften source pose changes;
the cabin and scenery never enter those bridges. Read/look video mattes and bridges remain
creative review items, rather than an approved reusable animation master.

Yanaka rooftops, the Sumida-style skyline and the bay/bridge panorama form one strip with
540-pixel spatial feather joins. Travel is **72 design pixels/second**, 5.14 times the previous
14, covering 6480 pixels without a wrap or reset. Feather joins can blend building details;
this finite pilot does not establish seamless long-form scenery or an exact real train route.

The app verified a 900-frame proxy and the full **2700-frame / 90-second 1080p/30 export** with
the same Lo-Fi-Walz track and stereo 48 kHz AAC. Chrome played both exports to their ends and
sought the full export to 74 seconds. Independent full decode, timing and hash checks passed;
**29 sampled exterior offsets** matched global travel, both repeat/chunk joins retained zero
character translation, and **eight cup-lid checks** retained the source coverage above alpha
128 with low RGB error. The cup-component extraction removes a small low-coverage edge fringe;
no opaque lid pixels are removed. Tests cannot confer visual approval.

[Preparation, hashes and verification evidence](evidence/t14-train-actions-draft.json).
Episode: `tabi-train-actions-90s`, in the same `Tabi train test 90s` project. Output:
`exports/Tabi-Actions-Faster-Journey-90s-Lo-Fi-Walz-DRAFT.mp4`. The reusable scene/template,
routine, prompts and preparation scripts are retained under `sources/train-actions-v2/`;
working checks and screenshots are in `.local/train-actions-v2/`. No application code changed;
T40–T48 remain planned. No MP4 is tracked, and unrelated staged IDE changes are preserved.

### Saved review checkpoint — 4 October 2026

Marco reports that the result is almost the desired video, but **TABI sometimes disappears**
during the animation. At this checkpoint the creative baseline was one fixed cabin,
consistent character, breathing/read/sip/look actions, three connected exterior views moving
at 72 pixels/second, and the selected Lo-Fi-Walz music. This feedback accepts the direction;
it does not approve the defective animation or close the pilot's creative gate.

The project, frozen snapshot, prepared layers and export are already saved on disk. The
[review checkpoint](evidence/t14-train-actions-review-2026-10-04.json) records their exact
identities and Marco's feedback. Precise disappearance frames and the cause were not yet established.
The prior sampled travel, lid and repeat checks do not prove uninterrupted visibility across
all intermediate action frames; the reported defect remained open at that checkpoint.

The requested next creative pass was to locate the affected frames in the full export, inspect the source
alpha, extracted silhouettes, foreground bridges and scheduled channel coverage, then repair
the identified cause in a new derived version. Review the entire 900-frame routine and both
repeats for disappearing body parts, transparency flashes, rough edges and pose jumps before
exporting a replacement. Keep the cabin, continuous exterior travel and music as the baseline.

## T14 — calm window ride animation polish

Status: new calmer draft exported and technically verified; Marco's visual acceptance is pending.
Marco requested consistent animation, more outside watching and fewer actions, with music polish
deferred. The replacement watches outside for **36 seconds**, takes **one 12-second coffee break**,
then watches for **42 seconds**. The window-facing hold uses the actual supplied head-turn pose
with at most one pixel of authored breathing over six seconds; the cup stays fixed during holds.

Inspection found partial foreground loss rather than a completely blank TABI frame. The old
900-frame routine includes opacity holes in its foreground bridges, and supplied sip mattes omit
hands that still exist in their RGB pixels. These defects are visible in the old export at frames
365, 474 and 495. The new preparation repairs enclosed alpha and selected hand edges, excludes
stray window-pole alpha beside the turning head, and keeps matching-pose bridges opaque.
It uses native sip frames 0–63 forward and then in reverse to put the cup down, avoiding the
defective native return, including frames 82, 100 and 102. Source RGB and original assets are
preserved. The two native clips were measured at 25/1 fps; selected/reversed motion and the
30/1 fps presentation are explicitly authored. This is not approval or repair of the full sip source.

All **540 prepared foreground frames** have no enclosed alpha holes or soft interiors in the
eroded silhouette checks; all selected native hand cores are preserved. Both coffee endpoints
match the idle pixels exactly, and the schedule covers every frame without gaps. The app's
14-second proxy crosses the entire break. The full export is **90 seconds / 2700 frames,
1920×1080, 30/1 fps** and passed full decode and frozen-job hash verification. All 2700 decoded
frames match the expected opaque character regions and global exterior travel within lossy-video
tolerances. Maximum RGB error averages are 3.66 for head/gills, 4.12 for hands/cup and 3.23 for the
clear window region. Both action boundaries and render chunk boundaries pass continuity checks.

The cabin, glass mask and three-view exterior remain unchanged at **72 design pixels/second**,
travelling 6480 pixels without reset or wrap. Episode audio tracks and the exported AAC stream
are identical to the previous draft; no music tuning was performed. Visual review of the two
short motion bridges, source edges and existing scenery feathers remains necessary. Music and
rights/publication gates remain open; music polish is deferred by Marco.

[Preparation, diagnosis and complete verification evidence](evidence/t14-calm-window-ride-draft.json).
Episode: `tabi-train-calm-90s`, revision 0, in the existing `Tabi train test 90s` project. Output:
`exports/Tabi-Calm-Window-Ride-90s-Lo-Fi-Walz-DRAFT.mp4`. New asset identities and
`pack.tabi.calm-ride` preserve the prior versions. Prepared/native layers, scripts, every-frame
audits and app screenshots are saved under `sources/train-polish-v3/`. The verified video is
open in the local app. No application code changed and no MP4 is tracked.

Verification: `.venv/bin/python .local/train-polish-v3/audit_prepared.py` and
`.venv/bin/python .local/train-polish-v3/verify_export.py` passed on the target Mac.
Unrelated staged IDE files remain untouched. T40–T48 are still planned.

## Next work

Review the calmer T14 draft for visual acceptance and any remaining source-edge/bridge polish.
Preserve its long outside-watching holds, infrequent actions and independent scenery travel.
Music polish is deferred until the picture is settled. The new draft is the continuation point;
the earlier rejected/defective drafts remain saved for comparison.

T40 remains the first unblocked application implementation task: infer safe import parameters from actual media
and explain the remaining choices. T41 exposes that as a simple importer. Scene preparation,
animation binding and a visual builder follow before the wider workflow/navigation work.
See [T40–T48](tasks/INDEX.md) for dependencies and verification commands.

The complete V1 history is retained separately to avoid confusing completed build steps with
the current queue. Creative gates are summarized in the index and detailed in the acceptance
report; they can proceed independently when the real inputs are available.
