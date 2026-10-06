# Active task index

The **U01–U03** [app workflow trial](../tasks.md) is complete as a real silent draft.
Marco's final creative approval and the production gates below remain open.
Marco permits Flow for generation; setup, trimming, review and export must use video-story.
Implement and verify one step, then commit it. Preserve existing projects and source media.

| Task | Outcome | Status |
| --- | --- | --- |
| U01 | Frame-exact pending clip sections and matching review playback | complete; seven focused checks pass |
| U02 | Normal UI section controls and authenticated preview | complete; API/frontend/build checks pass |
| U02a | Correct accessory/marking identity drift on retry | complete; 17 focused checks pass |
| U02b | Use confirmed cup facts in prop corrections | complete; 21 focused checks pass |
| U02c | Recover from a retry limit while preserving accepted footage and budget | complete; core/API/frontend/build checks pass |
| U02d | Keep both hands around the confirmed handle-free cup | complete; 30 focused checks pass |
| U02e | Restart only the current partial shot from its clean image | complete; 35 focused checks and frontend/build pass |
| U02f | Keep the closing breath seated with unchanged clothing coverage | complete; 36 focused checks and core/package pass |
| U03 | Full 90-second real TABI app workflow | complete draft; 2160 real frames and full playback verified |

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
| [F14](../tasks.md#f14--clean-obsolete-local-test-and-video-artifacts) | Remove obsolete local test runs, preparation copies and video comparisons | complete; 18.50 GB removed, protected hashes and core checks pass |

## Remaining acceptance

The [U03 real app trial](../evidence/u03-tabi-app-trial.json) completed a 90-second silent
train draft through Setup, References, Shots, Finish and Download. Twelve native clips are
active; 24 app attempts include ten rejections and two superseded accepted takes. Actual Flow
usage was 1085 included credits (1070 app ledger plus 15 earlier duplicate submissions).
No custom assembly, looping, padding, new subscription or credit purchase was used. Exact
frames/PTS, all hashes and 36 source-range comparisons pass; full Chrome playback reaches 90 seconds.
The app now exposes source-section controls, bounded retry recovery and partial-shot restart.
The real trial used complete native ranges; partial trimming has separate actual-media tests.

Remaining creative limits include broad facial/body acting, minor cup-print changes, two
visibly distinct framings instead of three, and exterior resets at fresh camera cuts. The
closed-coat breath and corrected handle-free drinking are draft evidence, not deterministic
generation quality. Marco's final visual approval and a fresh setting/outfit trial remain open.

The [planned-shot evidence](../evidence/s04-planned-shots.json) verifies six independent clean
starts, bounded in-shot extensions, camera-cut review, retry/reopen, exact 90-second assembly
and Chrome playback. S01–S04 engineering is complete. The [real TABI camera trial](../evidence/s04-tabi-camera-trial.json)
used five fresh takes and 500 included credits; four full takes failed creative review. It produced
a verified 14-second trimmed camera sample, while the original 24-second and revised 20-second
plans remain incomplete. The short sample does not prove dots eliminated, reliable breathing or
a continuously progressing panorama. Its historical range imports required the API; U01/U02
subsequently added ordinary UI controls. U03 above supersedes its incomplete full-length trial.

The guided assisted workflow is implemented. [F12 evidence](../evidence/f12-flow-workflow.json)
separates the synthetic 90-second authenticated service run, the short fresh UI journey and
full-length Chrome playback from real creative approval.

The [real Tokyo trial](../evidence/f12-tokyo-real-trial.json) preserves a 90-second recipe
blocked at 22 accepted seconds after a failed correction. A separate 22-second preview is
verified and playable through Finish; real full-length acceptance remains open.

- Obtain Marco's creative review of the real U03 train draft; run a fresh setting/outfit
  variation and measure representative human effort. Café and walking remain separate trials.
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
