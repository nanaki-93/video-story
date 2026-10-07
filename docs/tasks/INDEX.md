# Active implementation queue

Read the [final plan](../../PLAN.md) and [task details](../tasks.md). Execute the first unblocked
task below; task identifiers are stable, while this table defines dependency order.

| Order | Task | Outcome | Status / dependencies |
| --- | --- | --- | --- |
| 1 | R01 | Final reference-generation plan and obsolete-trial cleanup | complete; [evidence](../evidence/r01-repository-cleanup.json) |
| 2 | L07 | Strict cabin/look/journey/recipe contracts | next |
| 3 | L14 | Reference generation, provenance and job contracts | L07 |
| 4 | L15 | Catalog existing local references, including ignored assets | L14 |
| 5 | L16 | Qualify the local multi-reference model on real Tabi assets | L15; explicit installation and terms gate |
| 6 | L17 | Owned generation jobs with the qualified backend | L16 |
| 7 | L08 | Guided layered-asset and motion preparation | L07/L14/L15; synthetic work can proceed while L16/L17 wait |
| 8 | L09 | Pack combinations through the shared renderer | L08 |
| 9 | L10 | Breathing, blinks and gills with stable timing | L09 |
| 10 | L11 | Reference/generation/pack API and CLI | L10/L17 |
| 11 | L12 | Full reference-to-video UI | L11 |
| 12 | L06 | Correct the pilot's book as a new version | available editor or L17; may proceed earlier independently |
| 13 | L13 | Real 2×2×2 variants, 90-second silent video and 10-minute check | L06/L12 and real packs |

The existing asset-to-video engine (L01–L04) and silent real Tokyo draft (L05) are implemented.
Their retained evidence is linked from [progress](../progress.md). The new generator and modular
packs are planned, not implemented. [Acceptance](../38-v1-acceptance.md) separates engineering
checks from visual/rights/release gates. Retired experiments are removed, not an alternate queue.
