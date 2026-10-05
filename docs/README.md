# Documentation guide

The current normal workflow is the guided assisted Flow path. Python prepares prompts,
checks native imports and joins, saves reviews/progress, exports exact footage with local music,
and prepares YouTube delivery. Real art/music and the almost-automatic production target still
need acceptance. Existing layered tools remain under Advanced.

## Start here

| Need | Document |
| --- | --- |
| Launch/install the app | [Installation](32-installation.md) |
| Make the first 90-second train video | [Guided Flow workflow](37-operations.md#make-a-90-second-train-video) |
| Understand the four steps | [Current UI](05-webapp.md) |
| Follow implementation and current checks | [Active tasks](tasks/INDEX.md), [progress](progress.md), [acceptance](38-v1-acceptance.md) |
| Read the implementation contract | [Flow task plan](tasks.md) |
| Find artwork and preserved local variants | [Media guide](assets/README.md), [source audit](09-implementation-review.md) |
| Use existing layered projects / troubleshoot | [Advanced operations](37-operations.md#produce-an-advanced-layered-episode), [recovery](37-operations.md#troubleshooting-and-recovery) |

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
| Scene extensions | [Café](33-cafe-template.md), [activities/outfits](34-activity-packs.md) |
| Verification | [QA requirements](07-qa.md), [toolchain](10-toolchain.md), [long-form measurements](36-longform.md) |
| Interface reference and history | [Current UI map](05-webapp.md), [original browser spike evidence](24-browser-foundation.md) |
| External reference record | [Sources and verification dates](08-sources.md) |

## Historical records

The 38 individual V1 task files have been consolidated into [V1 task records](archive/v1-tasks.md).
The detailed chronological log is in [V1 implementation history](archive/v1-progress.md).
Historical test totals and “next task” statements describe those earlier checkpoints.
Superseded proposals are in [the preparation archive](archive/pre-flow-plan.md); character trials,
licences, hashes and creative feedback are in [production history](archive/production-progress.md).
The unused [ComfyUI bridge](35-local-generation.md) and playback prototype have been retired.
Bulk source variants remain locally with recorded hashes rather than in the tracked tree; keep
those files backed up separately. No source artwork or Git history was erased.
