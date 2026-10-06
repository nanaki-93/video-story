# Active task index

The current implementation queue is **S01–S04** in [the planned-shot workflow](../tasks.md).
Build short shots from clean references and review deliberate camera cuts. Implement and verify
one step, then commit it. The existing assisted handoff and saved videos remain supported.
The archived P/T plans are historical and are not a second implementation queue.

| Task | Outcome | Status |
| --- | --- | --- |
| [S01](../tasks.md#s01--define-compatible-shot-and-reference-contracts) | Define compatible shot contracts | complete |
| [S02](../tasks.md#s02--generate-and-review-bounded-shots-from-clean-references) | Bound fresh shots, prompts and reviewed cuts | complete |
| [S03](../tasks.md#s03--guide-reference-preparation-shot-generation-and-cut-review-in-the-app) | Guide the shot workflow in the app | pending |
| [S04](../tasks.md#s04--verify-complete-shot-assembly-and-document-the-usable-workflow) | Verify full assembly and target-Mac UI | pending |

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
