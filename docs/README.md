# Documentation guide

Use the current guides below. The original V1 implementation is finished as software; its
remaining art/music reviews are still open. The reusable-character and guided app workflow is
not implemented. Its first Colab/Blender candidate failed the real-art gate; the evidence below
records the result without promoting it to a production asset.

## Start here

| Need | Document |
| --- | --- |
| Launch/install the current app | [Installation](32-installation.md) |
| Import an image and make a first scene today | [First scene walkthrough](37-operations.md#first-scene-from-an-existing-image) |
| Normal production, CLI and troubleshooting | [Operations](37-operations.md) |
| Simpler import, scene builder and default settings proposal | [Guided workflow plan](tasks.md) |
| Actual character-generation trial and commercial-use review | [P01 findings](progress.md#p01--commercial-licence-review-and-colabblender-trial), [comparison](evidence/p01-character-comparison.jpg), [exact evidence/licences](evidence/p01-character-pipeline.json) |
| What to implement next | [Active task index](tasks/INDEX.md) |
| Current status and latest checks | [Progress](progress.md) |
| What passed V1 and what still needs creative input | [V1 acceptance](38-v1-acceptance.md) |
| Supplied artwork and missing preparation | [Source audit](09-implementation-review.md), [reference review](12-tabi-art-review.md) |

## Technical reference

These documents retain contracts, reproducible commands and evidence needed to maintain the
implemented services. Start with the relevant subject rather than reading every file in order.

| Subject | References |
| --- | --- |
| Product and engineering rules | [Product plan](../PLAN.md), [agent instructions](../AGENTS.md) |
| Asset preparation and import | [Art specification](01-assets.md), [registry](11-asset-registry.md), [project/asset UI](26-project-workflows.md) |
| Architecture and contracts | [Ownership and runtime](02-architecture.md), [contracts](03-contracts.md), [local service](25-local-service.md) |
| Timeline and rendering | [Design constraints](04-rendering.md), [time semantics](13-timeline.md), [renderer](14-renderer.md), [effects](17-effects.md) |
| Story and previews | [Continuity](18-story-continuity.md), [editor](27-editor.md), [CLI previews](15-preview-workflow.md), [browser preview](28-preview.md) |
| Audio | [Audio core](16-audio.md), [audio editor](29-audio-editor.md) |
| Jobs and exports | [Jobs](19-jobs.md), [assembly](20-chunk-assembly.md), [cache](21-cache-storage.md), [profiles](22-export-profiles.md), [queue/settings](30-render-queue.md) |
| Release and recovery | [Publishing boundaries](06-publishing.md), [release exporter](23-release-preparation.md), [release/backup UI](31-release-and-backups.md) |
| Scene extensions | [Café](33-cafe-template.md), [activities/outfits](34-activity-packs.md), [optional local generation](35-local-generation.md) |
| Verification | [QA requirements](07-qa.md), [toolchain](10-toolchain.md), [long-form measurements](36-longform.md) |
| Interface reference and history | [Current UI map](05-webapp.md), [original browser spike evidence](24-browser-foundation.md) |
| External reference record | [Sources and verification dates](08-sources.md) |

## Historical records

The 38 individual V1 task files have been consolidated into [V1 task records](archive/v1-tasks.md).
The detailed chronological log is in [V1 implementation history](archive/v1-progress.md).
Historical test totals and “next task” statements describe those earlier checkpoints.
Screenshots, measured reports, source inventories and original artwork remain at their existing
paths so the evidence can still be reproduced.
