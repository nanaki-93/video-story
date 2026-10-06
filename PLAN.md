# Tabi Story Studio product plan

Tabi Story Studio is a local app for making reviewed TABI videos. Python owns prompts,
media, timing, rendering and delivery; the TypeScript interface guides the work. Music
composition and publishing remain separate.

## Current workflow

The normal app starts at **Create video → Setup → References → Shots → Finish**. The train /
Tokyo / 90-second preset uses six short shots and three reviewed starting images (wide, close,
medium/table). Each camera cut begins again from its clean image. A fixed camera within each
shot, ongoing outside travel and a calm routine keep the journey readable. Existing continuous
drafts retain their old workflow; existing scene tools are under Advanced.

Generation uses **Copy prompt → Open Flow → Import native result → Review**. The app saves
reference hashes, prompts, parent lineage, attempts, confirmed prop states, reviews and credit
reservations. Each fresh shot uses Frames to Video with its assigned image. Native Extend stays
inside that shot, normally once and twice for the three-part drink action. The previous shot is
used only to review the editorial cut. Retry uses the same image or in-shot parent with one
selected correction; full rejection notes stay in history. Refresh and an unknown external
result do not create another generation request. This reduces inherited drift; it does not
guarantee clean mouths, stable gills, props or particle-free footage.

Review plays the selected source section, with optional frame controls and the complete original
kept separately. Recovery can raise the per-action retry allowance within the existing maximum
and budget, or restart only the current partial shot from its clean image. Earlier completed
shots and all attempt evidence remain saved. Handle-free cup actions explicitly use both hands
around the same cup body; generated prop consistency still requires visual review.

The default timeline is 0–15s settle, 15–30s watch, 30–52s pickup/sip/return, 52–60s sway,
60–75s watch and 75–90s deep breath. Drink gets three separate clips so the cup returns before
the next camera cut. Every boundary needs completed actions and compatible visible cup/hand
state. Actual native frame counts and an explicitly reviewed outpoint determine the cut.

Finish assembles only accepted footage at its measured native cadence, trims to an explicitly
reviewed exact ending, and can add one continuous local soundtrack. The verified export can
enter the existing YouTube delivery review and public/private bundle workflow.

[S01–S04](docs/tasks.md) add the planned-shot workflow. [F12 evidence](docs/evidence/f12-flow-workflow.json)
records full-length engineering verification and target-Mac UI observations. A synthetic
90-second video verifies software behavior, not TABI likeness or release approval.

The [U03 real app trial](docs/evidence/u03-tabi-app-trial.json) now completes a silent 90-second
TABI Tokyo draft using normal UI for every step except Flow generation. It verifies 2160 real
frames, exact timing and complete Chrome playback. Twelve native clips survived 24 app attempts;
actual usage was 1085 included credits. Two-hand drinking and the closed-coat breath improved,
while acting, cup-print variation and panorama resets still need creative review.

## Remaining production gates

Marco wants almost entirely automatic preparation for 30 × 90-second videos per month, with
new combinations and some new assets each time. That full target remains unqualified:

- No supported external consumer Flow connector, unattended native continuation or enforceable
  account-wide spending cap was established in [F00](docs/evidence/f00-flow-execution.json).
  The installed app does not include this chat's browser automation.
- The real U03 draft still needs Marco's final visual review and later listening review. A fresh
  setting/outfit variation and representative human effort remain unmeasured through the workflow.
  Café and walking require separate creative trials.
- Source art, original music, exact provider/model commercial terms, disclosure and release
  metadata need current evidence. Commercial output permission does not guarantee YouTube
  monetization.

The selected creative comparison is `docs/assets/clip-tests/TABI-Flow-Train-90s-DRAFT.mp4`.
Marco calls it the best result so far, with a mouth defect near 10 seconds and later particles.
It is preserved with its [review history](docs/archive/production-progress.md#p01--flow-baseline-selected-and-repeatable-workflow-review).
The earlier calm-window draft and rejected preparation experiments remain historical evidence.
Their passing technical checks do not override Marco's visual feedback.

The existing Tokyo 8/7/7-second native sources import as **528 frames / 22 seconds** without
inheriting the combined scene's one-second timestamp gap. Invented props and particles still
require visual rejection; fixing timestamps does not repair those pixels.

## Cost and tool boundaries

Use existing Google entitlement and local tools. No new subscriptions, paid API, plugins,
licence purchases or credit top-ups are part of the route. Record a freshly observed Flow
allowance and displayed fresh-shot/extension costs for each run; included compute is limited.
Local reservations cannot prevent independent spending inside Flow.

The earlier Colab/Blender character trials failed their appearance/depth gates. Their exact
model/licence evidence stays in the [historical progress](docs/progress.md); do not resume those
routes or introduce another generator without reviewing its weights, dependencies, hosted
terms and commercial output rights. The earlier monthly Colab estimate is not a Flow capacity
qualification. Thirty production videos per month have not been demonstrated.

## Product boundaries

| Area | Decision |
| --- | --- |
| Runtime | Local Python/FastAPI worker and bundled TypeScript UI on authenticated loopback |
| Engine | Shared Python services for CLI and API; no browser timeline compiler or FFmpeg commands |
| Storage | Versioned local documents/media, atomic drafts and immutable approved hashes; no database |
| Timing | Integer frames/samples and rational frame rates; preserve native clip cadence |
| Review | Automatic technical checks, explicit human appearance/ending-state and release reviews |
| Safety | Registered roots, Host/Origin/CSRF checks, authenticated media, owned cancellation and recovery |
| Media | Original artwork/music remain local; never commit MP4 files or erase masters with cache cleanup |
| Delivery | Verified local export, factual release bundle and manual upload |
| Variations | Fresh opening from stable references; previous reviews do not approve a changed outfit/scene |

The target Mac is Apple M5 Pro with 48 GB unified memory. Existing layered projects remain
supported through Advanced, with the same compositor, audio mixer, owned job services and
release checks. Their [long-form measurements](docs/36-longform.md) remain workload-specific.

## Implementation and verification

Follow [AGENTS.md](AGENTS.md), the [active index](docs/tasks/INDEX.md) and each task's dependencies.
Implement one coherent step, run its required checks, record evidence in
[progress](docs/progress.md), then commit with its task ID. Preserve unrelated staged changes.

Run `make check`, `make web-check`, `make web-build`, `make package` and the target-Mac
`make test-media` milestone gate. Review full real picture/sound separately. No mock preview,
stub generation job or passing fixture may be called a production-ready video.

Use the [operations guide](docs/37-operations.md) for the current guided path, recovery and
Advanced workflows. [V1 acceptance](docs/38-v1-acceptance.md),
[V1 tasks](docs/archive/v1-tasks.md) and [V1 history](docs/archive/v1-progress.md) retain earlier
engineering results. Old plans are evidence, not another active implementation queue.

## Deferred scope

Direct unattended Flow control, automatic visual approval, new providers, a general rig/editor,
native Kotlin/Compose packaging, signing/notarization, dialogue/lip-sync, collaboration,
analytics and automatic publishing remain outside this verified release.
