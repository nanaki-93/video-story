# Active task index

Marco requested a documentation cleanup and a plan before further implementation on
4 October 2026. His priority is **importing existing Tabi images/animation files and building
a scene from them**, with defaults for standard videos. The proposal is in [docs/tasks.md](../tasks.md).
The redesigned app is not implemented yet. Start with T40 when implementation resumes.

| Task | Outcome | Dependencies | Status |
| --- | --- | --- | --- |
| [T39](../progress.md#t39--documentation-cleanup-and-workflow-plan) | Clean docs and prepare the guided workflow plan | Existing V1 records and user clarification | complete |
| [T40](../tasks.md#t40) | Derive safe import choices in Python | Existing asset probe/import services | planned; first unblocked |
| [T41](../tasks.md#t41) | Guide file import with defaults and examples | T40 | planned |
| [T42](../tasks.md#t42) | Build still/layered scene drafts from selected assets | T40 | planned |
| [T43](../tasks.md#t43) | Turn prepared character animation into a compatible scene pack | T42 | planned |
| [T44](../tasks.md#t44) | Add the visual scene builder and reusable scene library | T41, T42, T43 | planned |
| [T45](../tasks.md#t45) | Add standard video defaults and fit duration to music | T42, T43 | planned |
| [T46](../tasks.md#t46) | Connect steps with readiness, context and useful next actions | T41, T44, T45 | planned |
| [T47](../tasks.md#t47) | Simplify preview and export over the existing services | T45, T46 | planned |
| [T48](../tasks.md#t48) | Verify the guided workflow on the target Mac and update operations | T40, T41, T42, T43, T44, T45, T46, T47 | planned |

Dependencies are explicit prerequisites, not authorization to implement in this planning pass.
For each implementation step, update this index and [progress](../progress.md) with behavior,
checks and remaining limits; commit with the task ID as required by [AGENTS.md](../../AGENTS.md).

## Creative gates carried forward

**Current working baseline:** Marco selected
[the calm-window 90-second video](../progress.md#t14--return-to-the-calm-window-baseline)
as the last good result and rejected the direction of later variants. Preserve its original
artwork, poses, timing, scenery and soundtrack; next address only the local ear-edge flicker.
The records below are chronological evidence, not instructions to resume the later rigs or
generated replacement ears. Earlier extra-motion requests are deferred during this repair.
The [bounded upper-ear comparison](../progress.md#t14--bounded-ear-comparison-and-app-workflow-assessment)
is technically verified but remains a review candidate with residual source-art distortion;
it does not promote a new creative baseline.

The [app workflow assessment](../tasks.md#can-the-normal-app-workflow-produce-this-video)
now makes the product gap explicit: the compositor and export jobs work, while raw-art cleanup
and guided pack/scene assembly are not end-to-end UI features. T43/T44 include compatible saved
routines and T48 requires a fresh-project train export followed by a scenery/duration variant
without scripts or hand-written JSON. One-time art preparation remains separately reviewed.

| Original tasks | Remaining input/review |
| --- | --- |
| T06–T08, T10–T11 | Reference selection; separated/matching real art; authored animation timing, loops, transitions and compatibility |
| T14, T16–T19, T30 | Actual Tabi pilot, original music, visual/effects/story and listening review |
| T24, T32, T38 | Real production credits/rights/disclosure/thumbnail and final product/release acceptance |
| T34–T35 | Real café/activity/outfit art if those packs are used |
| T36 (optional) | A selected real ComfyUI/model/workflow trial; independent of this scene-building request |

Use the [acceptance report](../38-v1-acceptance.md) for exact inputs. These gates remain open;
archiving old task files does not mark them complete. Technical implementation and testing can
use clearly labeled synthetic fixtures while the real artwork is prepared.
The [corrected 90-second continuous-train draft](../progress.md#t14--continuous-train-draft-follow-up)
is now available for Marco's visual review; its technical checks do not close the creative gates.
The newer [actions and faster scenery draft](../progress.md#t14--actions-and-faster-scenery-follow-up)
adds breathing/read/sip/look movements, fixes the foreground cup layering and advances through
three exterior views at 72 pixels/second. Marco says the result is almost the desired video,
but reports intermittent TABI disappearance. The [saved review checkpoint](../progress.md#saved-review-checkpoint--4-october-2026)
recorded animation visibility and transition polish as the next creative priority.
The [calmer replacement](../progress.md#t14--calm-window-ride-animation-polish) now uses repaired
foreground alpha, matching poses and a selected sip segment that avoids defective source frames.
TABI watches outside for 78 seconds with one coffee break; all 2700 output frames were checked.
Marco then called the calmer version better, identified remaining ear clipping and requested
continuous breathing with actions at 15/30/45/60/75 seconds. The
[previous timed-action draft](../progress.md#t14--continuous-breathing-and-timed-actions) restores
source ear fringes and adds that authored schedule. All 2700 prepared and final frames were
checked, including ear cores, action/chunk joins and continuous exterior positions. Final visual
acceptance remains pending. Music is unchanged and its polish is deferred. Guided application
work is still planned; T40 remains its first task.

Marco's subsequent review still found ear defects and could not perceive the larger breath.
He selected the window-looking reference for rest and authorized matching generated assets.
The [window-rest/visible-breath draft](../progress.md#t14--window-rest-and-visible-deep-breath)
uses a shared head/frill rig and face-only expressions, stronger normal breathing and an explicit
closed-eye inhale/hold/exhale at 75–85 seconds. All 2700 prepared/final frames and six independent
frill cores per prepared frame were checked. Generated likeness, outlines and rigged gestures
remain human review items. T14's creative gate remains open; T40–T48 are still planned and
music polish remains deferred.

Marco rejected that draft's disconnected neck/collar, incorrect table cup and
duplicated resting/moving arm shapes. The [anatomy review and complete-frame test](../progress.md#t14--anatomy-review-and-complete-character-frames)
records the causes and recommends whole character frames from one coherent master, with
independent scenery. The bounded coffee diagnostic is not a replacement 90-second video;
native ears/matte edges, matching window-rest endpoints and complete breathing/action masters
remain open. T14 is not creatively accepted. No T40–T48 implementation is claimed.

His next review finds ear flicker in the complete-frame coffee diagnostic. The
[ear-stability correction](../progress.md#t14--ear-stability-correction) fits one shared
five-frill master into the same complete-frame 12-second action. Face/prop cores, collar and
lower-body pixels are preserved; the test is rendered and reviewed with continuous scenery.
It is a new draft asset version, not creative acceptance or a 90-second replacement. Review
temporal ear roots/outlines as well as opacity before the remaining action masters.

That candidate is subsequently superseded by Marco's explicit return to the calm-window
baseline above. Its technical checks are retained as evidence and do not override his review.

## V1 records

All original T01–T38 task bodies, verification and limits are retained in
[V1 task records](../archive/v1-tasks.md). The [chronological log](../archive/v1-progress.md)
retains prior commits, test results and local clip paths. Follow the active table above for new
work rather than historical “next task” instructions.
