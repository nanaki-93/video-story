# Active task index

The current implementation queue is **U01–U03** in [the app workflow trial](../tasks.md).
Marco permits Flow for generation; setup, trimming, review and export must use video-story.
Implement and verify one step, then commit it. Preserve existing projects and source media.

| Task | Outcome | Status |
| --- | --- | --- |
| U01 | Frame-exact pending clip sections and matching review playback | complete; seven focused checks pass |
| U02 | Normal UI section controls and authenticated preview | complete; API/frontend/build checks pass |
| U02a | Correct accessory/marking identity drift on retry | complete; 17 focused checks pass |
| U02b | Use confirmed cup facts in prop corrections | complete; 21 focused checks pass |
| U02c | Recover from a retry limit while preserving accepted footage and budget | next |
| U03 | Full 90-second real TABI app workflow | active |

S01–S04 planned-shot engineering is complete. Its actual creative limits remain recorded below.

## Previous implementation

| Task | Outcome | Status |
| --- | --- | --- |
| [F00](../tasks.md#f00--qualify-flows-supported-execution-path) | Qualify supported Flow handoff | complete; assisted route |
| [F01](../tasks.md#f01--define-strict-flow-episode-and-execution-contracts) | Define Flow contracts | complete |
| [F02](../tasks.md#f02--persist-resumable-sequences-and-accepted-branches) | Persist accepted branches | complete |
| [F03](../tasks.md#f03--compile-focused-prompts-from-confirmed-state) | Compile focused prompts | complete |
| [F04](../tasks.md#f04--import-native-results-with-measured-timing-and-lineage) | Import native clips | complete |
| [F05](../tasks.md#f05--review-technical-defects-and-visual-continuity-separately) | Review continuity | complete |
| [F06](../tasks.md#f06--advance-the-bounded-generation-and-review-cycle) | Bound retries and progress | complete |
| [F07](../tasks.md#f07--assemble-a-verified-silent-video-from-accepted-footage) | Assemble verified video | complete |
| [F08](../tasks.md#f08--add-one-continuous-local-soundtrack-at-finish) | Add local music | complete |
| [F09](../tasks.md#f09--expose-flow-workflow-services-through-cli-and-authenticated-api) | Expose shared CLI/API | complete |
| [F10](../tasks.md#f10--present-setup-opening-continue-and-finish-as-the-normal-ui) | Guide the app workflow | complete |
| [F11](../tasks.md#f11--prepare-a-youtube-delivery-with-existing-review-rules) | Prepare YouTube delivery | complete |
| [F12](../tasks.md#f12--verify-repeatable-production-and-document-the-remaining-automation-gap) | Verify full production workflow | engineering complete; creative/control gates open |
| [F13](../tasks.md#f13--retire-unused-routes-and-reduce-the-tracked-repository) | Retire obsolete code and untrack preserved bulk media | complete |

## Remaining acceptance

The [planned-shot evidence](../evidence/s04-planned-shots.json) verifies six independent clean
starts, bounded in-shot extensions, camera-cut review, retry/reopen, exact 90-second assembly
and Chrome playback. S01–S04 engineering is complete. The [real TABI camera trial](../evidence/s04-tabi-camera-trial.json)
used five fresh takes and 500 included credits; four full takes failed creative review. It produced
a verified 14-second trimmed camera sample, while the original 24-second and revised 20-second
plans remain incomplete. The short sample does not prove dots eliminated, reliable breathing or
a continuously progressing panorama. Its range imports required the existing API; a simple UI
for retaining a good section is still missing. Full 90-second creative review remains open.

The guided assisted workflow is implemented. [F12 evidence](../evidence/f12-flow-workflow.json)
separates the synthetic 90-second authenticated service run, the short fresh UI journey and
full-length Chrome playback from real creative approval.

The [real Tokyo trial](../evidence/f12-tokyo-real-trial.json) preserves a 90-second recipe
blocked at 22 accepted seconds after a failed correction. A separate 22-second preview is
verified and playable through Finish; real full-length acceptance remains open.

- Review one real 90-second train episode and a fresh setting/outfit variation through the app,
  recording rejects, credits and human effort. Café and walking remain separate trials.
- Qualify source artwork/music, exact provider/model commercial terms, disclosure and the
  final picture/sound before publication. No fixture or old comparison grants that approval.
- Direct unattended Flow control and the target of 30 videos monthly remain unqualified.
  [F00](../evidence/f00-flow-execution.json) establishes only the assisted handoff.

The selected best draft and its mouth/particle defects remain in the
[feedback record](../archive/production-progress.md#p01--flow-baseline-selected-and-repeatable-workflow-review).
The [Tokyo review](../evidence/p01-flow-tokyo-001-review.json) retains the separate timestamp-gap
and invented-prop findings. Neither is a production-ready release.

## Historical work

P01–P04 and T40–T48 in [the retained plan](../tasks.md#retained-production-plan-and-earlier-task-references)
record earlier preparation proposals. They are superseded as the implementation queue by F00–F12;
creative feasibility questions stay open. Rejected Blender/SPAR3D/parts-rig trials remain in
[progress](../progress.md) and the evidence folder. Do not restart them as active tasks.

Original V1 task bodies and checks remain in [V1 tasks](../archive/v1-tasks.md) and
[V1 history](../archive/v1-progress.md). The [acceptance report](../38-v1-acceptance.md)
retains the legacy engineering gates and real-art/music input register. Existing layered projects
remain supported in Advanced.
