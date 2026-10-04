# Tabi Story Studio product plan

Tabi Story Studio is a local tool for turning Tabi artwork, prepared animation and finished
music into reviewed videos. Python owns media, timeline and rendering behavior; the TypeScript
web app guides the work. Music composition and external publishing remain separate.

## Current priority

The V1 software is implemented and its engineering gates are recorded in
[V1 acceptance](docs/38-v1-acceptance.md). The interface still exposes too many technical tools
and gives too little guidance between importing media and making a scene.

Marco's 4 October 2026 request takes priority over the original build order: simplify asset
import, help him **assemble scenes from his existing Tabi images and animation files**, and
provide reusable defaults for standard videos. This request is for documentation cleanup and
a plan; the redesigned workflow is not implemented yet.

Read the [guided workflow plan](docs/tasks.md), then select the first unblocked item in the
[active task index](docs/tasks/INDEX.md). Begin with import and scene creation. The guided
application plan does not add artwork generation. Marco separately authorized matching
generated components for the current animation-polish test. The
[documentation guide](docs/README.md) separates current instructions, technical references
and historical records.

The current creative checkpoint is [window rest with a stable ear rig and visible breathing](docs/progress.md#t14--window-rest-and-visible-deep-breath).
Marco still saw ear defects and could not perceive the earlier larger breath. He selected
`06-looking-out-window.png` for rest and explicitly authorized matching new assets. The new rig
keeps one head and six ear-frill shapes throughout, with lowered resting arms, 22-pixel normal
breathing and a clear closed-eye inhale/hold/exhale at 75–85 seconds, reaching 62 pixels of lift.
Window leans at 15/60 seconds, coffee at 30 and music nodding at 45 preserve his cues. All 2700
prepared and final frames were checked. Cabin, continuous three-view scenery and exact music
tracks are unchanged; music polish remains deferred. Generated likeness, gesture quality and
final visual acceptance remain subject to Marco's review. Earlier drafts are saved.
T40 remains the first task when application workflow implementation resumes.

## Product boundaries

| Area | Decision |
| --- | --- |
| Runtime | Local Python/FastAPI service; bundled TypeScript/Vite UI on one authenticated loopback origin |
| Media engine | Shared Python services used by CLI and API; FFmpeg renderer and renderer-generated previews |
| Storage | Versioned local documents and media; atomic draft saves, immutable approved versions, no database |
| Time | Integer frames, integer audio samples and rational frame rates |
| Source art | Preserve supplied originals; never infer approval, missing layers, source timing or licences |
| Normal production | Import prepared media, build/reuse a scene, add finished music, preview and export |
| Defaults | Fill technical settings where evidence permits; keep creative review and unknown source facts explicit |
| Delivery | Verified local video and release preparation folder; manual external upload |
| Optional generation | Existing local ComfyUI adapter remains an advanced utility; no new models or generation workflow required |

Target machine: Marco's Apple Silicon M5 Pro MacBook Pro with 48 GB unified memory. The
[measured long-form checks](docs/36-longform.md) qualify synthetic 45-minute native 1080p
and 60-second native 4K workloads on that machine. They do not qualify every real-art workload.
One active export is the default. Node is required for frontend development/building, not for
running the installed application.

## Creative milestones still open

1. Select the actual character and seated reference hashes in the [review packet](docs/12-tabi-art-review.md).
2. Prepare/review the real character animation, matching foreground, cabin/window and exterior layers.
3. Review a 90–120-second train pilot with the actual assets.
4. Finish an approximately 5–10-minute original-music story and review the full picture and sound.
5. Review rights, credits, thumbnail and release metadata before manual publication.

These remain creative gates, not reasons to block independent interface work using labeled
synthetic fixtures. Standard scene-based videos need not become multi-scene stories, and music
must not be stretched to meet an arbitrary length.

The optional first story brief remains *The Last Train Home*: departure, city, rain/dusk and
arrival. Tokyo-inspired imagery should not claim an exact real route. Tabi's identity comes
from the selected reference; Platform 7 and 11:11 are optional motifs.

## Implementation and verification

Follow [AGENTS.md](AGENTS.md), the active task's dependencies and the applicable
[technical specifications](docs/README.md#technical-reference). Implement one coherent behavior,
run its meaningful checks, record evidence in [progress](docs/progress.md), and commit it with
its task ID. Preserve unrelated staged work. No MP4 enters Git.

The new workflow must preserve existing projects, CLI/API parity, immutable approvals,
authenticated media/SSE, registered filesystem roots, source-preserving cache cleanup and
owned-job recovery. The browser must not implement a second compositor or timeline compiler.
Run the milestone acceptance gate before merging; visual and listening approval remains human.

The original task records and detailed build log are retained in the
[V1 archive](docs/archive/v1-tasks.md) and [implementation history](docs/archive/v1-progress.md).
They are evidence, not the current queue.

## Deferred scope

Native Kotlin/Compose packaging and DMG, signing/notarization, a general animation/rig editor,
automatic layer extraction, 3D, dialogue/lip-sync, cloud rendering, accounts, collaboration,
analytics and automatic publishing remain outside this work. Buy no assets, upload no private
music and download no large models without authorization.
