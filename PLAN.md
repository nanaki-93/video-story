# Tabi Story Studio product plan

Tabi Story Studio is a local tool for turning Tabi artwork, prepared animation and finished
music into reviewed videos. Python owns media, timeline and rendering behavior; the TypeScript
web app guides the work. Music composition and external publishing remain separate.

## Current priority

The V1 software is implemented and its engineering gates are recorded in
[V1 acceptance](docs/38-v1-acceptance.md). The interface still exposes too many technical tools
and gives too little guidance between importing media and making a scene.

Marco now requires an **almost entirely automatic, reusable character workflow**, covering
train/café/walking scenes, different interiors/exteriors, real garment changes and actions.
Another isolated ear repair or a simpler importer cannot establish that this works. The
[production plan](docs/tasks.md) makes P01's real-character feasibility proof the current
priority, before integrating preparation through P02–P04. T40 remains independent import
engineering; the redesigned normal workflow is not implemented yet.

Marco's latest cost constraint is **no additional paid apps**. Investigate free tools with
commercial-compatible terms, the installed Blender and existing Google/Colab allowance.
Exclude new subscriptions, paid plugins and credit top-ups from the proposed route. Meshy and
Tripo Studio are outside this route. The second candidate, SPAR3D, has now
[run successfully but failed the character-quality gate](docs/evidence/p01-spar3d-trial.json).
Its actual Blender views show a recognizable front, very shallow side geometry and a visible
tail gap. Exact code/model/dependency checks, private token entry and the measured generation
are complete. Neither tested candidate qualifies as the reusable production character.

The authorized correction round using [eight separate body references and saved prompts](docs/evidence/p01-turnaround-reference-pack.json)
is now complete. The [paired SPAR3D retry](docs/evidence/p01-turnaround-trial.json) compared
the new front image with and without a shape prior derived from all eight views. Neither
variant qualified: the image-only rear is wrong, while the approximate shape prior adds depth
but merges/distorts the gills, headphones, body and tail. All 16 Blender views and both meshes
are preserved. This closes the bounded SPAR3D trial, not the broader workflow decision.

The [next-route source review](docs/evidence/p01-next-route-review.json) recommends a
**TRELLIS 1 mesh-only preflight**. Its official multi-image sampling and native vertex-colour
mesh decoder offer a candidate path, with an Apache-licensed pinned FlexiCubes component.
The stock imports/exporter still include non-commercial components; isolating and verifying
the permitted dependency path is the next checkpoint. No new model/runtime has been run.
Hunyuan3D-2mv is excluded from the proposed worldwide-video route because its current licence
expressly restricts outputs in the EU, UK and South Korea. Full production feasibility remains open.

The current production target is **30 × 90-second videos per month**, with some new assets
and a new combination for each. The [verified account allowance](docs/evidence/p01-colab-capacity.json)
is 2,000 Colab compute units monthly; 2,499.4 were available on 5 October. The
[capacity plan](docs/tasks.md#monthly-production-and-compute-budget) reserves 20% and requires
measured preparation costs before claiming the workload fits. Reuse assets and render locally;
the 45 minutes of monthly finished footage are not 45 minutes of cloud compute.

The authorized **5 October Colab/Blender trial** produced one real TripoSR mesh and eight
local Blender views. [Evidence and licence review](docs/evidence/p01-character-pipeline.json)
record a **no-go for that candidate**: shallow geometry and lost face/frill/outfit detail.
There is no qualified rig or animation. P01 remains open; P02–P04 stay blocked. The standard
TRELLIS.2 setup was excluded because some dependencies have non-commercial terms despite its
MIT main code/weights. No new purchase, subscription or private-music upload occurred.
That runtime is closed and diagnostic files are saved locally. The separate SPAR3D trial also
preserves its model, executed notebook, measurements and eight unedited Blender views locally.
Its [comparison](docs/evidence/p01-spar3d-comparison.jpg) and evidence remain separate from
TripoSR. Runtime release is recorded in the latest progress entry.

Read the [active task index](docs/tasks/INDEX.md) and [documentation guide](docs/README.md).
Check the exact model, weights, dependencies, hosted service and output terms before every
new route/version. Commercial-use terms do not approve source artwork or guarantee YouTube
monetization. This is now a standing rule in [AGENTS.md](AGENTS.md).

The current creative baseline is Marco's selected
[calm-window 90-second video](docs/progress.md#t14--return-to-the-calm-window-baseline),
`docs/assets/clip-tests/Tabi-Calm-Window-Ride-90s-Lo-Fi-Walz-DRAFT.mp4`.
He says its animations are good and later versions are worse. Use episode `tabi-train-calm-90s`,
pack `pack.tabi.calm-ride` at 1.0 and the original `sources/train-polish-v3/` preparation.
Preserve this version's TABI artwork, original ear shapes, poses, cup, timing, 36–48-second
coffee break, calm window holds, continuous 72-pixel/second scenery and existing soundtrack.

This remains the visual comparison baseline. Marco's newer request supersedes the instruction
to keep repairing its ear edges before addressing the production strategy. Do not resume
frame repairs or promote a new design merely to make a rig pass. The separate parts rigs and
replacement-ear experiments remain historical. Music polish is deferred; all originals and
previous versions remain preserved.
The [bounded upper-ear comparison](docs/progress.md#t14--bounded-ear-comparison-and-app-workflow-assessment)
is technically verified but retains source-outline distortion; it does not replace Marco's
selected baseline or close the visual gate.

The [workflow feasibility assessment](docs/tasks.md#can-the-normal-app-workflow-produce-this-video)
distinguishes the working compositor/exporter from the missing guided preparation/binding flow.
The proposed strategy is one persistent master, compatible scene/outfit/action libraries and
automatic Blender preparation, feeding complete-character frames to the existing Python
compositor. This is contingent on P01, including cup contact, walking and a genuinely different
garment. Normal production should use named routines and defaults through the UI, with no
scripts or metadata editing. The failed diagnostic does not establish that handoff.

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
| Character preparation | P01 feasibility open; P02–P04 conditional on a qualified master and almost-automatic operations. Existing ComfyUI adapter remains an advanced utility. |

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
