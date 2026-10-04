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

## Next work

T40 is the first unblocked implementation task: infer safe import parameters from actual media
and explain the remaining choices. T41 exposes that as a simple importer. Scene preparation,
animation binding and a visual builder follow before the wider workflow/navigation work.
See [T40–T48](tasks/INDEX.md) for dependencies and verification commands.

The complete V1 history is retained separately to avoid confusing completed build steps with
the current queue. Creative gates are summarized in the index and detailed in the acceptance
report; they can proceed independently when the real inputs are available.
