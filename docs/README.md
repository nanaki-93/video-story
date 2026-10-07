# Documentation guide

The implemented app makes lo-fi videos from saved illustrations, window scenery and prepared
small loops. The next phase adds reference-based generation and reusable outfit/cabin/journey
packs. The [final plan](../PLAN.md) and [generation contract](39-reference-assets.md) define that
work; [operations](37-operations.md) describes controls available today. Real art/music approval
remains separate from engineering checks.

## Start here

| Need | Document |
| --- | --- |
| Launch/install the app | [Installation](32-installation.md) |
| Make the first 90-second train video | [Reusable scene workflow](37-operations.md#make-a-lo-fi-video) |
| Understand scene reuse and exports | [Current UI](05-webapp.md) |
| Follow implementation and current checks | [Active tasks](tasks/INDEX.md), [progress](progress.md), [acceptance](38-v1-acceptance.md) |
| Read the implementation contract | [Reference asset tasks](tasks.md) |
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
| Interface and planned generation | [Current UI map](05-webapp.md), [reference generator contract](39-reference-assets.md) |
| External reference record | [Sources and verification dates](08-sources.md) |

## Source and verification records

The source [media guide](assets/README.md), [read-only audit](09-implementation-review.md) and
[local source manifest](local-source-manifest.json) preserve supplied-art findings. Ignored
variants stay on disk and need separate backup. [Progress](progress.md) and
[acceptance](38-v1-acceptance.md) link retained evidence for active services and the successful
Tokyo pilot. Superseded plans and rejected experiment files were removed during R01; Git history
was not rewritten. There is one active implementation queue.
