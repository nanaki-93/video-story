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

## V1 records

All original T01–T38 task bodies, verification and limits are retained in
[V1 task records](../archive/v1-tasks.md). The [chronological log](../archive/v1-progress.md)
retains prior commits, test results and local clip paths. Follow the active table above for new
work rather than historical “next task” instructions.
