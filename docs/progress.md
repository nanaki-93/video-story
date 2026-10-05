# Current progress

Updated 5 October 2026 (Asia/Manila).

## Current state

The Python core, CLI and local web application implement the V1 production services. The last
full engineering gate recorded **296 unit checks, 61 real-media checks and four frontend tests**,
plus schema/type/build/package checks and installed Mac/browser verification. These are the
recorded T38 results, not new test runs for the documentation change.

[V1 acceptance](38-v1-acceptance.md) is the authoritative engineering/creative acceptance record.
Approved real character/environment packs, original music, pilot/story listening and visual
review, and publication decisions remain pending. Simplifying the app does not approve them.

The current creative baseline is Marco's selected [calm-window 90-second
video](#t14--return-to-the-calm-window-baseline). He prefers its animations and rejects the
later direction. Preserve its existing artwork and motion. A separate
[upper-ear comparison](#t14--bounded-ear-comparison-and-app-workflow-assessment) tests a limited
matte repair; it does not replace the preferred baseline or close the visual gate. Later technical
test results remain historical evidence, not a preferred creative result.

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

## T14 — continuous breathing and timed actions

Status: replacement draft exported and technically verified; final Marco visual review pending.
On 5 October Marco called the calmer draft better, reported clipping in TABI's ears, and requested
continuous breathing with five specific actions. The new 90-second schedule is:

| Cue | Authored behavior |
| --- | --- |
| Throughout | One global five-second breathing cycle, at most six design pixels of upper-body lift and gentle chest expansion; seat and resting cup stay anchored. |
| 15 seconds / frame 450 | Turn toward the window, hold, then return before the coffee cue. |
| 30 seconds / frame 900 | Lift/sip/return the coffee once, then rest with continuous breathing. |
| 45 seconds / frame 1350 | Ease into a small rhythmic nod/sway; ease out before the next look. |
| 60 seconds / frame 1800 | Turn toward the window again and keep watching through the end. |
| 75 seconds / frame 2250 | Take one eight-second larger breath, adding at most 16 design pixels of lift and chest expansion above the gentle cycle. |

Actual source RGB contains lower right-ear fringes missing from the supplied alpha. New bounded
native masks restore these lobes and their outlines without the previous thin-fringe erosion.
The hidden fringe's tracked patch stops when the head turns into profile; disconnected scenery
is excluded. All 130 selected native RGB frames remain unchanged. Independent lower-ear core
checks cover 1417 pixels in the head-turn entry and 393 in the coffee entry, both fully opaque.
The existing hand repair is retained and defective native sip return frames 64–128 remain
excluded. Native clips are measured at 25/1 fps and explicitly conformed to 30/1 presentation.
Breathing/nod/deep-breath timing is newly authored, not inferred native breath timing.

The music segment suggests a 0.8-second pulse for the small nod; this is draft motion timing,
not an approved beat map. No audio tuning occurred. The original cabin, mask and three-view
exterior advance independently at 72 design pixels/second, travelling 6480 pixels without reset.
Episode audio tracks and the final AAC essence are identical to the previous calmer export.

All **2700 prepared foreground frames** pass opacity, cue coverage and action-join checks.
The opacity audit distinguishes true full-resolution interiors from narrow open fringe gaps
that close when downsampled. All five joins retain the same breathing phase and matching poses.
The app's eight-second 540p preview crosses the coffee cue. The complete **2700-frame / 90-second,
1920×1080, 30/1 fps** app export passed full strict decode, output hash and every-frame comparison
for foreground, head, ear colours, hands/cup and continuously advancing scenery. All five action
joins, including both 900-frame chunk joins, pass; all 12 sampled exterior offsets match.

[Preparation and verification evidence](evidence/t14-breathing-actions-draft.json).
Episode: `tabi-train-breathing-90s`, revision 0. Pack: `pack.tabi.breathing-actions` at 1.0.
Output: `exports/Tabi-Breathing-Actions-90s-Lo-Fi-Walz-DRAFT.mp4` in the existing
`/Users/marcoandreose/Tabi Story Studio/projects/Tabi train test 90s` project. New derived assets,
native/prepared layers, scripts, complete audits and app screenshots are saved under
`sources/train-polish-v4/`. Previous versions, drafts, snapshots and original media are preserved.
The full video is open in the app. No app code changed and no MP4 is tracked.

Verification: `.venv/bin/python .local/train-polish-v4/audit_prepared.py` and
`.venv/bin/python .local/train-polish-v4/verify_export.py` passed on the target Mac.
Native source pose/fringe shape variation, short foreground bridges and existing exterior
feathers remain subject to human aesthetic review. This does not approve the full sip source,
art, music, rights or publication. Music polish is deferred; T40–T48 remain planned and the
pre-existing staged IDE files remain untouched.

The documentation audit passed for 53 Markdown files, 753 local links, all 38 archived task
bodies and the complete V1 history; all nine planned tasks / 127 target references remain valid.
`git diff --check` passed. No renderer regression suite was repeated for this creative-only
change; the actual app proxy/full jobs and complete foreground/export checks are recorded above.

## T14 — window rest and visible deep breath

Status: exported and technically verified, then rejected by Marco for neck/collar, cup and arm
assembly defects in the subsequent review below. Marco still reported ear defects, did not
perceive the previous big breath, requested stronger normal breathing and selected
`06-looking-out-window.png` for rest.
He explicitly authorized generating missing matching assets for this polish pass.

Built-in imagegen prepared six selected transparent components from the actual reference and
existing train foreground: complete head/frills, closed-eye expression, lowered-arm resting
body, hidden torso, coffee arms and matching cup. Visual comparison preserves the observed
lavender face, six pink frills, forehead star, brown eyes, coral headphones and green/leopard
outfit. These are generated variants, not pixel-identical extraction or approved masters.
The local project retains exact prompts, source/master hashes, selected/intermediate outputs
and paths. The tool does not expose model or seed; none is invented.

The same head/frill master is used throughout, with expression edits confined to the face.
Chest expansion occurs beneath the rigid head. The tail and foot cores remain fixed, and table
occlusion is fixed to the cabin. Previous defective native head/sip frames and optical-flow pose
bridges are excluded. Supplied sources and earlier derived versions remain unchanged; the old
clips are not declared repaired or approved.

| Cue | Authored behavior |
| --- | --- |
| Throughout | Window-facing rest with lowered arms. One global five-second breathing cycle reaches 22 design pixels of lift and up to 4% chest expansion; resting cup, tail core and foot stay anchored. |
| 15 seconds / frame 450 | Ease into a small lean toward the window, then settle before coffee. Default gaze remains toward the window. |
| 30 seconds / frame 900 | Reach, raise the cup, sip once, return it and lower the hands by 39.4 seconds. One continuous cup path. |
| 45 seconds / frame 1350 | Finite rhythmic nod/sway with relaxed eyes; return to window rest by 57 seconds. |
| 60 seconds / frame 1800 | Lean toward the window again; settle before the breath cue. |
| 75 seconds / frame 2250 | Close the eyes, inhale through 78 seconds, hold until 79, then exhale slowly through 85. Reach 62 pixels of lift and up to 9.5% chest expansion. |

All **2700 prepared frames** pass visibility and schedule checks. All **16200 independent frill-core
checks** retain opaque coverage; tail and foot cores match throughout. Maximum adjacent silhouette
area change is 0.347%; all five joins have premultiplied RGBA MAE at most 0.0268.
An intermediate separated-tail prototype exposed a small coat/tail wedge during nodding. The
saved replacement uses continuous deformation into the anchored tail and passes a regional
connection-gap check in all 2700 frames. Other enclosed gaps are recorded for visual review.
Technical checks cannot approve likeness, ear outlines or motion aesthetics.

The app's 13-second 540p preview covers global 75–88 seconds and plays the inhale/hold/exhale.
The full app export verifies **2700 frames / 90 seconds, 1920×1080, 30/1 fps, H.264 and stereo
48 kHz AAC**. Independent strict decode, output hash, all-frame foreground/head/frill-colour/
hand/cup and scenery comparisons, all five action/chunk joins and 12 exact exterior offsets pass.
The panorama travels 6480 design pixels at 72 pixels/second without resets or wrapping.
Episode music tracks and encoded AAC essence match the earlier draft; music is unchanged.

[Preparation and verification evidence](evidence/t14-window-rig-polish-draft.json).
Episode: `tabi-train-window-rest-90s`, revision 0. Pack: `pack.tabi.window-rest` at 1.0.
Output: `exports/Tabi-Window-Rest-Polished-90s-Lo-Fi-Walz-DRAFT.mp4` in the existing
`/Users/marcoandreose/Tabi Story Studio/projects/Tabi train test 90s` project. Masters, prompts,
scripts, motion envelope, complete audits and screenshots are saved under `sources/train-polish-v6/`.
Full job: `job-a8b3b011e1284302ad4ceccbd1254ced`. Snapshot: `34fcd6289b617053f203656b88139c18cf8fb95b96c8349d313892f223a9340a`.

Target-Mac checks: `.venv/bin/python .local/train-polish-v6/audit_prepared.py` and
`.venv/bin/python .local/train-polish-v6/verify_export.py` passed. Core validation and actual app
preview/full rendering were exercised; no broad renderer regression was repeated for this
creative-only pass. Generated likeness/outlines, rigged coffee reach/return, breathing strength
and scenery feather joins remain human review items. Art/music/rights/publication approval
remains open. No private music was uploaded or video published. No app code changed, no MP4
is tracked, and unrelated staged IDE files are preserved. Previous versions remain saved.
The documentation audit passed all 757 local links, preserved archived task/history records
and found no tracked MP4. `git diff --check` passed.

## T14 — anatomy review and complete character frames

Status: the v6 parts rig is rejected for anatomy/prop defects. The method review and a bounded
12-second complete-character coffee diagnostic are saved; no new 90-second replacement or
creative acceptance is claimed.

Marco reported a disconnected neck/outfit, a wrong table cup and resting arms underneath the
moving arms. Comparing the rendered coffee action, generated parts and actual supplied
`06-looking-out-window.png` / drinking references identifies the causes: the head's neck strip
does not tuck into the separately authored collar; the supposedly hidden torso retains upper
sleeve/arm contours beneath the coffee-arm overlay; the replacement cup is tilted in its table
rest. These are visual construction defects. The earlier checks proved opacity and faithful
rendering of those prepared images, not correct anatomy, limb replacement or table contact.

**Preparation decision:** use complete transparent TABI foreground frames from one coherent
master, with cabin, window/exterior and any necessary foreground occlusion kept separate.
Complete frames keep head, chin, collar, body, both arms and cup coherent within each pose.
They still need identity/ear/outline review and matching full entry/exit poses. Do not generate
each frame independently or switch between complete train shots. A parts rig can author these
frames later, but only with hidden-region artwork, reviewed joints/overlaps and explicit arm/prop
replacement. The application consumes prepared frames; this does not add a rig editor.

The short diagnostic reuses 64 complete coffee RGBA frames from the earlier v4 preparation,
including its prior matte/frill repairs. It selects the intact source segment at its recorded
25/1 fps, explicitly conforms it to 30/1 by repetition, holds the sip and reverses the selected
segment back to table rest. All 360 foreground files are byte-identical to their recorded
prepared source; no separate head, moving-arm or replacement-cup image is added. The native cup
stays upright at rest and moves with the hands. This narrow forward/hold/reverse test is not a
new final coffee master or a declaration that the original defective full return is repaired.

| Diagnostic phase | Local seconds |
| --- | --- |
| Upright cup and table rest | 0–2 |
| Reach and lift | 2–4.53 |
| Sip hold | 4.53–6.03 |
| Return along selected source poses | 6.03–8.57 |
| Same complete table-rest frame | 8.57–12 |

Actual app export verifies **360 frames / 12 seconds, 1920×1080, 30/1 fps, H.264**, with an
empty music schedule (the renderer supplies silent stereo 48 kHz AAC). Independent strict decode
and output SHA pass. All 360 rendered frames match the prepared foreground, neck/collar and
arm/cup cores within compression tolerance; all exterior comparisons and ten exact offset
checks pass. Travel advances 864 design pixels at 72 pixels/second, starting at distance 2160.
Native browser playback reaches 12 seconds/ended; app review checks table rest and cup lift.
The visual sample has a coherent collar and replaces the arm pose as a whole. These observations
support the preparation method; they do not close TABI's art gate.

**Remaining defects/scope:** native head/frill shapes still vary and matte edges need polish.
The source coffee-ready rest differs from the requested window-facing/lap rest in reference06.
Matching window-rest endpoints and complete breathing/window-look/coffee/vibe/deep-breath
masters remain to be authored and reviewed. No added breathing is applied in this diagnostic.
The existing 90-second videos and their music are unchanged; final music work remains deferred.

[Method, diagnosis and test evidence](evidence/t14-anatomy-method-review.json).
Episode: `tabi-anatomy-coffee-test-12s`, revision 0. Pack: `pack.tabi.anatomy-coffee-test` at 1.0.
Output: `exports/previews/Tabi-Coffee-Whole-Frames-12s-ANATOMY-TEST.mp4` in the existing
`/Users/marcoandreose/Tabi Story Studio/projects/Tabi train test 90s` project.
Job: `job-dd6ea665c09a48a59f06bf288e7bf1eb`. Snapshot: `c942b4c63476654a63cc2f9074ba4c74e4aee8a9d7b9aa143dcdf18c739622c5`.
Scripts, source index/hash mappings, all-frame audits, reports and app screenshots are saved
under `sources/anatomy-test-v7/`. No original asset, old registered version or previous video is
overwritten. No new raster artwork was generated during this review.

Target-Mac verification: preparation/source-hash audit, core validation/compilation, actual app
rendering/playback and `.venv/bin/python .local/train-anatomy-v7/verify_export.py` pass. No app
code changed, so broad renderer regression is not repeated. Documentation links/archive/task
audit passes all 761 local links, 38 archived tasks and nine planned tasks; `git diff --check`
passes. No MP4 is tracked; unrelated staged IDE changes are preserved.
Human creative approval, final 90-second picture, music/rights and publication remain open.

## T14 — ear stability correction

Status: Marco reported recurring ear flicker in the complete-frame coffee diagnostic. A
corrected 12-second draft is rendered and saved for review. The earlier diagnostic and all
90-second versions remain preserved; T14 creative acceptance is still open.

The complete-frame method avoids the separate neck, duplicate-arm and tilted-cup defects,
but its earlier v4 alpha preparation classifies each source frame separately. The resulting
ear outlines change and retain fragments beside the window. Source coffee RGB also contains
ragged fringe contours, so alpha changes alone cannot repair all the visible ear damage.

**Correction:** one transparent five-frill master was generated with the built-in imagegen
tool using the actual coffee and `06-looking-out-window.png` references. The same three left
and two visible right frills are fitted to nine reviewed pose keys, with smooth transforms
between them. Old ear fragments are removed inside bounded edit regions; new roots tuck
behind the original native head/headphones and cup/hand occlusion. The application receives
complete finished foreground frames, with no additional head, arm or replacement-cup layers.
This is an ear-only draft variant, not exact source extraction or human-approved artwork.
The actual prompt, references and generated master/hash are retained; the tool exposes no
model/seed, and none is invented.

Preparation verifies all **64 native frames and 360 scheduled frames**, including **320
independent opaque-frill core checks**. Native face/head/prop opaque cores are preserved;
all collar-region RGBA pixels and all pixels from y600 downward remain unchanged. All RGBA
pixels outside the bounded ear edit remain unchanged. The 25/1-to-30/1 repeat schedule and
12-second rest/lift/hold/reverse/return timing match the preceding anatomy diagnostic; the
first and final complete foregrounds match. A prototype stretched the left middle frill due
to a broken source contour and retained pink root fragments. Those were corrected before
installation and export; prototype results are not used as final evidence.

Actual app export verifies **360 frames / 12 seconds, 1920×1080, 30/1 fps, H.264** and silent
stereo 48 kHz AAC. Independent strict decode, SHA and all-frame foreground/head/collar/arm/cup
comparisons pass. All **1800 rendered ear-core comparisons** pass within compression tolerance
(maximum ear RGB MAE 4.30 at half resolution). All-frame exterior comparisons and ten exact
offset checks pass: travel advances 864 design pixels at 72 pixels/second from distance 2160.
Native browser playback reaches 12 seconds/ended; app seeks at 0, 3.5, 4.8 and 7.2 seconds
review complete outer ear outlines during rest, lift, sip and return. These observations and
coverage/fidelity checks support review; they do not certify temporal aesthetics or likeness.

[Preparation, preservation and app evidence](evidence/t14-ear-stability-draft.json).
Episode: `tabi-ear-stability-test-12s`, revision 0. Asset: `tabi.actions.anatomy-coffee-test` at
1.1; pack: `pack.tabi.anatomy-coffee-test` at 1.1. Existing 1.0 versions are unchanged.
Output: `exports/previews/Tabi-Coffee-Stable-Ears-12s-DRAFT.mp4` in the existing
`/Users/marcoandreose/Tabi Story Studio/projects/Tabi train test 90s` project.
Job: `job-536f633510f049f1adcda39840c565fa`. Snapshot: `e4866ad0b34da795c1c9ee8e3602376ca2b47aa94651b46155d5f1a0f41fef63`.
Master, prompt, prepared frames, scripts, complete audits and four app screenshots are saved
under `sources/ear-stability-v8/`.

Target-Mac preparation/hash audit, shared Python validation/compilation, actual app rendering
and playback, and `.venv/bin/python .local/train-ear-stability-v8/verify_export.py` pass.
No app code changed, so broad renderer regression is not repeated. Documentation link/archive/
task audit and `git diff --check` pass. No MP4 is tracked; unrelated staged IDE files are preserved.
All older episode drafts are hash-checked unchanged. Music polish remains deferred.

**Remaining:** generated ear likeness and temporal root/outline review; native face/head geometry
and texture still vary. Coffee-ready rest still differs from the requested06 window/lap rest.
This diagnostic adds no breathing and does not replace the90-second routine. Matching complete
window-rest/action masters, the full cue schedule and human creative approval remain required.

## T14 — return to the calm-window baseline

Status: working baseline selected by Marco and verified intact on 5 October 2026. The local
ear-flicker defect remains open. This pass records the correction in direction and inspects the
source; it creates no new animation variant, generated artwork or replacement export.

Marco says the later versions are getting worse and identifies
[Tabi-Calm-Window-Ride-90s-Lo-Fi-Walz-DRAFT.mp4](assets/clip-tests/Tabi-Calm-Window-Ride-90s-Lo-Fi-Walz-DRAFT.mp4)
as the last good point: its animations are good, with some flickering around the ears. That
specific file is now the reference for further polish. Its SHA-256 is
`a0d56de1ca30056ba9744c167aa2ae36c7185f1519afa2ce4b3ee1bfd60424e3`, identical to the original
verified project export. Episode `tabi-train-calm-90s`, revision 0, and pack
`pack.tabi.calm-ride` at 1.0 remain valid and intact, with the original
`sources/train-polish-v3/` assets. The saved snapshot is
`c8ebfbd8987d42500adb5b9fcdbfe7b9cb327a5fc48687bb1694cb59ee427e1d`.

Preserve the entire existing 90-second composition: 36 seconds watching, one 12-second coffee
break and 42 seconds watching, the same native TABI/ear artwork and poses, head/outfit/arms/cup,
subtle six-second idle motion, fixed cabin, independently scrolling scenery at 72 pixels/second
and the existing Lo-Fi-Walz soundtrack. Later parts rigs and the generated replacement-ear
master are superseded experiments. Earlier extra-action and stronger-breathing requests remain
recorded as future work and are deferred while stabilizing this baseline.

Twenty export frames covering the rest, turn, sip and return were inspected. Comparing source
look frames 0, 25 and 40 in RGB, composited cutout and alpha confirms that the cutout removes
part of the lower right fringe in frame0 and trims the outline during the head turn. Frame25
also has ragged ink in the RGB source. A local matte correction should be evaluated first, but
alpha coverage alone cannot establish that all visible edge damage is repaired. Preserve the
original painted shape and motion; changing TABI's design or reassembling body parts is outside
this repair. Compare moving outlines against this exact baseline and retain non-ear pixels.

[Baseline selection, exact identities and inspection evidence](evidence/t14-calm-baseline-selection.json).
Review images and read-only validation evidence are saved in `.local/calm-baseline-review-v9/`.
The selected local video matches the original job's hash, size and 90-second/2700-frame
1080p30 metadata. Shared Python episode validation passes. Existing source assets, episode,
media and soundtrack are unchanged. Documentation links/archive/task checks and
`git diff --check` pass; no MP4 is tracked and the unrelated staged IDE patch is preserved.
No claim that the ear flicker is fixed, no new app implementation, and no final creative or
publication acceptance is made by this baseline selection.

## T14 — bounded ear comparison and app workflow assessment

Status: upper-ear comparison exported through the app and technically verified. The selected
calm baseline remains preferred. The ear defect is not declared fully fixed.

Marco authorized the narrow repair and asked whether this result can become the normal
video-story workflow. The final candidate derives directly from the calm 1.0 foreground:
all painted RGB is identical, the 180-frame idle asset is reused unchanged, and only opacity
within x750–1019/y170–424 is reduced. A small contour filter, motion-compensated temporal
median and bounded removal of source-window colours trim unstable fragments. Every RGBA pixel
at y425 and below is identical to the original, protecting the raised cup, hands, lower face,
neck, outfit and body. Coffee endpoints still match the idle exactly. No generated replacement
ears, separate head/arm/cup layers, new actions, retiming or music changes are included.

Visual review rejected two broader alpha-recovery experiments for halos/ragged edges. The
first exported conservative candidate, pack 1.1, also touched a cup edge because the prop
enters the old repair region during the sip. Its own draft is labeled **REJECTED**; its files
and frozen export are retained for audit. The final 1.2 candidate restores that entire lower
region. This is a specific regression check learned from the composed moving action, not a
claim that opacity statistics establish good art.

Final candidate episode: `tabi-train-calm-upper-ear-comparison-90s`; pack
`pack.tabi.calm-ride@1.2`; coffee asset `tabi.actions.calm-coffee-break@1.2`. Preparation,
scripts and per-frame hashes are saved in the project's `sources/calm-ear-repair-v11/` and
ignored `.local/calm-ear-repair-v11/`. All original assets, the 1.0 pack, original episode and
selected MP4 remain intact. The 90-second schedule, 78 seconds watching, 36–48-second coffee
break, 72-pixel/second independent panorama and music tracks are unchanged.

The final app job `job-fd0b0456aac54654b85b8e21ebb6035a` verified **2700 frames / 90 seconds,
1080p30 H.264 with stereo 48 kHz AAC**. Independent full decoding and comparison of every
output frame passed; all ten sampled travel offsets and both action/two chunk joins matched.
The encoded AAC hash is identical to the baseline. All 360 prepared coffee frames retain exact
RGB and all RGBA outside the final upper-ear region; 332 frames contain localized alpha trims,
with a maximum of 2087 changed pixels. Idle and coffee endpoints remain identical.

Chrome selected the new episode, froze it, estimated storage, queued the export, opened the
verified output, played from 36 through 58 seconds and sought to 41.8 seconds. The
[app screenshot](evidence/t14-calm-upper-ear-app.jpg) and
[rendered before/after close-ups](evidence/t14-calm-upper-ear-comparison.jpg) support review.
The [90-second comparison](assets/clip-tests/Tabi-Calm-Upper-Ear-Comparison-90s-Lo-Fi-Walz-DRAFT.mp4)
and [12-second side-by-side](assets/clip-tests/Tabi-Calm-Upper-Ears-Before-After-12s.mp4) stay local
and untracked. [Exact identities, preservation checks and workflow evidence](evidence/t14-calm-upper-ear-comparison.json)
record the distinction between technical success and remaining visual defects. Original video
and episode hashes still match the selected baseline. No application code changed.

Verification commands: `.venv/bin/python .local/calm-ear-repair-v11/install_candidate.py`
(360-frame preservation audit and shared compiler validation), `verify_export.py` in the same
folder (all 2700 rendered frames, travel/joins and identical AAC), and `compare_video.py`
(360-frame side-by-side). `.venv/bin/python .local/docs-cleanup/check_docs.py` passes for
53 Markdown files, 779 local links, 38 archived tasks, nine planned tasks and 130 target paths;
`git diff --check` passes. The pre-existing staged IDE patch is preserved and zero MP4s are tracked.

The [workflow assessment and strategy](tasks.md#can-the-normal-app-workflow-produce-this-video)
is explicit: current Python services and the app render screen can compose and export this
prepared scene. Cabin separation, matte repair, pose bridges and pack preparation still happen
outside the UI. The target is a reviewed reusable train pack, named calm/idle routines,
compatible scenery selection and duration defaults, followed by preview/export. T43/T44 now
include compatible saved routines; T48 must reproduce this ride and a second scenery/duration
variant in a fresh project without scripts or JSON. T40–T48 remain planned, not implemented.

Residual source-art distortion remains visible through the head turn. Automatic matte trimming
cannot restore already damaged ink or supply missing painted ear lobes. Finish those few
complete source frames from the same character master and review the moving comparison before
promoting a pack. The broader head/neck/arm reconstruction and generated-ear experiments remain
superseded. Music polish and human creative/rights/publication gates stay open.

## P01 — commercial licence review and Colab/Blender trial

5 October 2026. **Diagnostic completed; candidate rejected; overall P01 feasibility open.**
Marco authorized trying an alternative to Meshy with his existing Google/Blender tools and
explicitly required monetization licence checks. He separately approved the Colab first-use
terms and ending the trial runtime. No new purchase, subscription or music upload occurred.

The licence review found that the standard TRELLIS.2 setup includes non-commercial BRIA
RMBG-2.0 weights and NVIDIA nvdiffrast/nvdiffrec rendering components. Its MIT main repository
does not clear those dependencies. That standard route was excluded. A custom replacement
route remains unimplemented; DINOv3 also has separate terms/access requirements. Hunyuan's
territorial terms were unsuitable for the intended unrestricted worldwide publication route.
The [component-by-component review](evidence/p01-character-pipeline.json) preserves official
links, versions, obligations and pending rights. [AGENTS.md](../AGENTS.md) now makes these checks
a standing requirement for every new generator/model/asset version. This is not YouTube
monetization eligibility or source-art/music approval.

One neutral RGBA input was generated with the built-in imagegen tool from the supplied profile
and full-body reference. It remains a draft, with the exact prompt, path and SHA-256 in the
evidence. Existing art was not overwritten. Colab Pro+ supplied an L4 with 22.03 GiB VRAM,
Python 3.11.13 and Torch 2.6.0+cu124. TripoSR code and weights were pinned and reviewed as MIT;
the 1,677,246,742-byte checkpoint was hash-verified before loading. Only DINO's architecture
config was downloaded separately. No background-removal model or NVIDIA research renderer ran.

Setup was not turnkey: notebook quoting, virtualenv bootstrap, a native extension build,
mixed CUDA packages and config lookup required corrections. BSD-licensed scikit-image replaced
the failed torchmcubes build; a non-symmetric ellipsoid checked the mesh axes. One successful
inference took **11.475 seconds**, peaking at **2.323 GiB allocated GPU memory**, and exported a
1,842,928-byte GLB with 46,044 vertices and 92,100 triangles. These figures exclude setup and
downloads. Total hands-on time and consumed Colab compute units were not instrumented; no
claim of cost-free or almost-automatic end-to-end preparation is made.

The downloaded bundle and GLB hashes matched the cloud records. Installed Blender **5.2.2 LTS,
build d13f752e3b9c**, imported the same mesh and rendered eight transparent 640×640 views using
Cycles CPU. Only coordinate orientation, cameras and lighting were set; no mesh/weight/frame
repair, rig or animation was added. Sandbox startup crashed, while a scoped outside-sandbox
Blender run completed. [The actual comparison](evidence/p01-character-comparison.jpg) shows
why this candidate fails: relief-like side depth, soft/merged frill roots, weak face marks and
lost coat detail. A watertight mesh is not acceptance of anatomy or likeness.

Local diagnostic material is in `.local/p01-character-pipeline/`: the input draft,
`tabi-p01-trial-record.ipynb`, result GLB, generation script/patches/configs/package versions,
logs, and `result/blender-review/tabi-triposr-v1-review.blend`. The saved notebook includes failed
setup history and is an execution record, not a Run All production interface. The
[cloud notebook](https://colab.research.google.com/drive/1elmBLvNc05fVgSBeRMXaKIpKfDOaHjNd)
remains saved; final UI showed Reconnect and [no active sessions](evidence/p01-colab-runtime-stopped.jpg).

No breathing/head turn, walk, deep breath, cup contact, second garment, train/café reuse,
restart rehearsal or app integration was performed with the rejected mesh. No 90-second
replacement was generated. P02–P04 stay blocked; T40 is independent engineering. This one
candidate does not prove that every possible 3D route will fail. A further trial must address
depth and detail before moving to a rig, within P01's bounded candidate budget.

Verification: `scripts/verify_character_pipeline.py --report docs/evidence/p01-character-pipeline.json`
under `.venv/bin/python` verifies **32 local artifact identities**, image dimensions, GLB header,
same-master references and the unchanged baseline's **2700 frames / 1080p / 30 fps**. It reports
**no_go**, not creative acceptance. Nine focused verifier tests pass, including rejection of
changed sources, incorrect dimensions, missing gates, unapproved go decisions, different
master hashes, escaping paths and unknown fields/versions. Ruff and `git diff --check` pass.
The preferred video retains SHA-256 `a0d56de1ca30056ba9744c167aa2ae36c7185f1519afa2ce4b3ee1bfd60424e3`.
No MP4 is tracked; unrelated staged IDE files are preserved.

## P01 — no additional paid apps

5 October 2026. Marco prefers to avoid apps with pricing. The standing instructions, product
plan and active tasks now target zero additional software/service spend: no new subscriptions,
paid plugins, licence purchases or credit top-ups. Existing Blender and Google/Colab allowance
remain options; this does not make cloud compute unlimited. The preceding suggestion to use
paid Tripo Studio is superseded. No app behavior, assets or trial evidence were changed.

Preliminary official-source screening found another reason not to rely on a main MIT label:
[TripoSG's NOTICE](https://github.com/VAST-AI-Research/TripoSG/blob/main/NOTICE) names BRIA,
HunyuanDiT and FlashVDM-derived components with their own terms. Its stock route is unqualified.
SPAR3D is the next candidate to audit, not a selected production generator. Its
[official implementation](https://github.com/Stability-AI/stable-point-aware-3d) describes
point-cloud-conditioned reconstruction and experimental Apple Silicon support. Its repository
[licence dated 5 July 2024](https://github.com/Stability-AI/stable-point-aware-3d/blob/main/LICENSE.md)
permits qualifying commercial use without fees below US $1 million annual revenue across
the user/entity and affiliates, requires commercial registration, and specifies distribution
and attribution obligations. Eligibility, exact gated weight terms and full dependencies are
still pending. The public model-card fetch required access; no access gate was bypassed.

This pass used documentation only. No second candidate was generated, no model was installed
or downloaded, no cloud runtime was started, and no service terms were accepted. The original
TripoSR no-go report stays unchanged. Verification is the local documentation/link/history
check and `git diff --check`; application tests are not required for this scope-only update.

## P01 — Colab allowance for 30 monthly videos

5 October 2026. **Account allowance verified; production consumption not yet measured.**
Marco clarified 30 videos of about 90 seconds monthly, with a new combination and some new
assets per video. That is 45 minutes of finished footage, not a cloud-runtime estimate.

Read-only inspection of the signed-in Google One plan-benefits dialog confirmed Google AI
Ultra's **2,000 Colab compute units per month**. Colab's resource monitor showed **2,499.4 units
available**, zero active sessions and no connected runtime. The balance's additional units,
individual expiry dates and next deposit date were not established. No GPU was started,
subscription changed, credit purchased or model downloaded during this check.

[Capacity evidence](evidence/p01-colab-capacity.json) records the observations, public official
sources, private local screenshot hashes, explicit assumptions and missing measurements. The
production plan now proposes a 400-unit reserve and 1,600-unit working budget, about 53.33 units
per episode before subtracting other Colab work. Its 10/25/50/70-unit examples are sensitivity
scenarios, not benchmarks. Final local Blender/video-story rendering would consume no Colab
units; generating new assets, retries and environment setup would consume the cloud budget.

This supports testing the existing-entitlement route without a new paid app, but does not
qualify automatic TABI preparation or guarantee a specific GPU. The next licence-cleared trial
must record the whole session's consumption and separate one-time setup from recurring new
assets. P01 remains open and P02–P04 blocked. The first failed candidate's report, preferred
video and source assets are unchanged. Verification: JSON arithmetic/source-path checks,
local documentation links and `git diff --check`; no application behavior changed.

## P01 — SPAR3D access and measured-trial preparation

5 October 2026. **Prepared, not executed.** Marco confirmed total annual revenue below
US $1 million including affiliates, and completed both Hugging Face access and Stability's
free commercial registration himself. The signed-in model page confirms access. Registration
completion is recorded as Marco's confirmation; no personal form fields enter Git.

[Preflight evidence](evidence/p01-spar3d-preflight.json) pins the official source and model
revisions, model SHA-256 and byte size, the downloaded 4 KB configuration and licence identity.
The exact model licence Git blob matches the reviewed source licence bytes. This clears that
primary licence question under the confirmed conditions; it does not approve source artwork,
all runtime dependencies, generated quality or YouTube eligibility.

The visible tensor inventory includes SPAR3D's own image-estimator and DINO weights. The
prepared runner initializes the existing architectures and requires complete learned-weight
coverage from the single SPAR3D checkpoint. Only the later upstream constant-zero device
sentinel may be absent. No standalone OpenAI CLIP, DINOv2, research-only AlphaCLIP or
background-removal checkpoint is downloaded. This modified loader has not run and may fail;
missing learned weights must stop the trial, never leave random initializations in inference.
The installed dependency closure still needs review before the main weight download.

A separate [Colab notebook](https://colab.research.google.com/drive/1h84XS9vkk3xi1WJSOX_Oj5fdVh_Oakv1?authuser=1)
is saved with L4 / high RAM / runtime 2025.07 selected. The original TripoSR notebook remains
separate. Chrome's initial file-upload restriction was resolved on the subsequent connection;
the uploaded notebook is visibly present. A read-only Hugging Face token is the remaining
user handoff. Browser rules require the user to create the credential; it must be entered
privately in Colab, never in chat, notebook source, reports or Git.

No SPAR3D weights were downloaded, no model installed or generated, no GPU connected and no
new spend incurred. Colab still shows **2,499.4 units, zero active sessions and zero units/hour**.
The notebook uses manual 30-unit / 60-connected-minute trial ceilings; it cannot read or
enforce Google's quota automatically. Actual setup, download, generation and whole-session
costs remain unmeasured. The local Blender review helper is ready for eight unedited mesh
views; it preserves SPAR3D's normal glTF coordinates instead of applying TripoSR's correction.

Verification: all six notebook code cells parse and remain unexecuted with empty outputs;
the runner passes Ruff; synthetic phase records are atomic, retain failure type and omit
exception bodies; configuration/licence Git-blob identities match; the draft input retains
its previous SHA-256. Local prepared scripts, notebook and audit files are hashed in the
preflight evidence and remain under ignored `.local/p01-spar3d/`. No application behavior
changed, so application tests were not rerun. P01 stays open and P02–P04 blocked. The preferred
90-second baseline and first failed candidate are unchanged.

## Next work

P01 remains the production decision: provision the private read token, finish the actual
SPAR3D dependency review and measured trial within existing allowance, then qualify a reusable character through
the required motion, wardrobe, prop and scene-reuse cases before starting P02–P04. The first
candidate is a no-go, not a base for more per-frame repairs. A second bounded candidate requires
the same model/dependency/output licence checks; the standard
TRELLIS.2 setup is not commercially cleared by its main MIT licence alone.

Preserve the calm-window baseline, original art and deferred music work. T40 remains the first
independent application engineering task, but cannot qualify character generation. The
[active index](tasks/INDEX.md) now includes P01–P04 and the updated T40–T48 dependencies.

The complete V1 history is retained separately to avoid confusing completed build steps with
the current queue. Creative gates are summarized in the index and detailed in the acceptance
report; they can proceed independently when the real inputs are available.
