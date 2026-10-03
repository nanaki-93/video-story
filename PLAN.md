# Tabi Story Studio full implementation plan

## Purpose and final outcome

Implement a local production tool for Tabi Eki: original lofi music distributed separately through DistroKid, and YouTube episodes using that music with consistent Tabi animation and visual storytelling. The application turns approved assets plus an authored episode manifest into a reproducible video and a release preparation folder.

Target machine: Marco's Apple Silicon MacBook Pro M5 Pro with 48 GB unified memory. Treat its actual render performance as unmeasured. Development can run elsewhere with synthetic media, but macOS playback, hardware encoding, packaging, and final performance must be verified on that machine or equivalent Apple Silicon hardware.

The first creative milestone is a 90–120-second train pilot. The first completed episode is approximately 5–10 minutes, using enough finished music to justify its length. Longer Stories and Sessions are supported after the short episode and recovery workflow are proven. Do not stretch a short composition to an arbitrary duration.

## Product decisions

| Area | Proposed decision | Reason |
| --- | --- | --- |
| Application identity | Tabi Story Studio; channel identity remains Tabi Eki | Separates production software from the channel |
| Music generation | Outside this project; import Melotrail or DAW WAV exports | Keeps audio composition and video production manageable |
| Core implementation | Python package, typed contracts, CLI | Direct access to media tooling and simple headless operation |
| Renderer | FFmpeg behind a replaceable renderer interface | Suitable for prepared layers and clips |
| Art authoring | Editable layered artwork and authored cutout animation; Fusion optional | Preserves character identity and deliberate motion |
| Desktop | Kotlin/JVM with Compose Multiplatform desktop | Fits the user's Kotlin experience |
| Local service | Python FastAPI, launched and owned by desktop | Same core as CLI, no separate business logic |
| Data | Versioned JSON/YAML documents and local project folders | No account, cloud backend, or database required |
| Generation | Optional local ComfyUI adapter after V1 core | Rendering approved episodes must work offline |
| Scene system | Reusable template capabilities; train first, café second | Supports Tabi beyond travel |
| Preview | Renderer-generated proxy video and still frames | Avoids a second compositor with subtly different output |
| Publishing | Export checklist and release folder; manual upload | Keeps final creative and rights review with Marco |

These are implementation choices, not claims that one stack is universally optimal. Pin compatible Python, JDK, Kotlin, Compose, and FFmpeg versions during the bootstrap spike and record them. Do not hardcode guessed current versions into this plan.

## Scope by release

**Pilot:** one camera angle, seated Tabi, idle breathing and blink, looking outside with clean entry/exit transitions, three exterior depth layers, one scheduled passing landmark, a cabin/window mask, one daylight-to-dusk treatment, original or synthetic demo WAV, 1080p/30 output, basic CLI validation and preview.

**Core beta:** robust asset registry; schema migration; scene and action compilation; deterministic event schedules; full audio timeline; weather/reflections; resumable chunks; cache invalidation; release bundle; automated integration checks; complete short episode.

**V1 desktop:** project browser, asset import/approval, episode setup, story/timeline editor, preview, audio editor, render queue, publishing preparation, settings, basic continuity notebook, macOS installer, backup/recovery, CLI parity. Add a café template as an architectural acceptance test before declaring the engine scene-independent.

**Expansion:** additional outfits and camera packs; sipping, reading and sleeping; more environment packs; richer continuity; local ComfyUI workflow execution; longer Sessions; reusable episode templates; more sophisticated compositor if measured limitations warrant it.

**Deferred:** 3D scenes, general-purpose rig editor, fully automatic depth separation, lip-sync/dialogue, cloud rendering, collaborative editing, accounts, automatic DistroKid uploads, automatic YouTube publishing, social analytics, a browser game, and a reimplementation of Melotrail. These are not needed to complete V1.

## Asset to episode workflow

1. Approve Tabi reference, palette, proportions, and seated camera design.
2. Produce editable character pieces, cabin masks, exterior plates, and sound assets.
3. Export and approve normalized assets; record provenance, versions, and licences.
4. Import finished music and release metadata independently from Melotrail.
5. Author a story outline; map scene beats to musical sections.
6. Compile that outline to an explicit timeline, including transitions and persistent prop states.
7. Validate, render stills and a proxy, then inspect motion and sound.
8. Approve a content-hashed episode snapshot; render resumable sections.
9. Assemble video, mix/mux audio once, and verify the deliverable.
10. Export artwork references, chapters, track list, disclosure notes, and rights report for manual publishing.

## Implementation milestones and gates

| Milestone | Work | Exit gate |
| --- | --- | --- |
| M0 Contracts and toolchain | T01–T03 | CLI skeleton, pinned tools, capability report, versioned schemas |
| M1 Asset foundation | T04–T08 | Synthetic test pack plus approved real pilot assets, or explicit art review pending |
| M2 Visual pilot | T09–T14 | 90–120-second preview with correct masks, actions and parallax; user art approval |
| M3 Complete episode | T15–T19 | 5–10-minute authored episode, audio integrated, no discontinuities |
| M4 Reliable headless production | T20–T24 | Resume/cancel/cache tests and final release folder pass |
| M5 Desktop product | T25–T33 | All V1 screens use the same core; packaged application works on Apple Silicon |
| M6 Extension and production readiness | T34–T38 | Café template, optional generation bridge, long-form benchmark, recovery drill |

Tasks marked optional are not required for V1. M2 artistic approval and M3 finished music cannot be claimed through synthetic fixtures. Agents should continue independent infrastructure work while waiting for those inputs.

## Proposed first episode

Working title: The Last Train Home. This is a creative brief, not a promised geographically exact route.

| Segment | Duration share | Story and visual development |
| --- | --- | --- |
| Departure | 0–15% | Quiet station, motion eases in; Tabi listens |
| City | 15–45% | Residential scenery develops; one landmark passes; Tabi looks outside |
| Rain and dusk | 45–80% | Rain grows gently; cabin lighting warms; music changes at an authored boundary |
| Arrival | 80–100% | Motion slows; Tabi settles; closing composition and music resolution |

Use stylized Tokyo-inspired artwork without asserting that impossible combinations are a real rail journey. Platform 7 and clock 11:11 may be recurring brand details where visually appropriate; they are not mandatory for every episode. Preserve Tabi's approved pastel, soft zen identity. Exact colors and anatomy must come from an approved reference, not an agent's memory.

## Dependency and collaboration policy

Work in order until interfaces are stable. Parallel work is optional only when explicitly authorized in a future implementation session. Suitable independent lanes after M0 are asset preparation, core/compiler, and desktop wireframes. Every lane uses shared schemas and task ownership. Do not have two agents edit the same contract without coordination.

Suggested review units: bootstrap, asset registry, timeline/compiler, rendering, audio, recovery, desktop, release, second scene. Each change must name its task, behavior, evidence, and unresolved limitations. No task is done solely because the UI contains a button.

## Effort and cost planning

Do not budget this as a one-prompt build. The critical path is art cleanup and animation transitions, followed by renderer correctness and desktop packaging. Asset approval and target-Mac benchmarking determine the schedule. For each milestone, the implementing agent should report actual effort, remaining art inputs, and measured render speed; only then revise delivery estimates.

Use local approved assets and local rendering by default. Track generation model downloads, commercial asset licences, optional Resolve Studio, optional signing/notarization credentials, disk space, and backups as explicit choices. No paid service or licence purchase is implied by the plan.

## Definition of complete

Marco can install or launch the app, create a project, import his music and approved Tabi assets, author and preview an episode, export a correct MP4, cancel/resume without corruption, and obtain a complete release preparation folder. A second scene template runs without engine-specific train assumptions. Reopening the project preserves edits and asset identities. Documentation covers fresh setup, normal production, missing files, failed renders, backups, and external publishing.

An original finished Tabi episode must be viewed and heard by Marco. No amount of automation guarantees YouTube monetization or distributor acceptance. Software completion, artwork approval, and publication are separate statuses.

## Detailed specifications

- [Assets and production briefs](docs/01-assets.md)
- [Project architecture](docs/02-architecture.md)
- [Data contracts and interfaces](docs/03-contracts.md)
- [Timeline and rendering implementation](docs/04-rendering.md)
- [Desktop pages and interactions](docs/05-desktop.md)
- [Music and publishing handoff](docs/06-publishing.md)
- [Verification and acceptance](docs/07-qa.md)
- [Ordered task backlog](docs/tasks/INDEX.md)
- [Official references and verification status](docs/08-sources.md)
