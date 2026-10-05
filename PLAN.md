# Tabi Story Studio product plan

Tabi Story Studio is a local app for making reviewed TABI videos. Python owns prompts,
media, timing, rendering and delivery; the TypeScript interface guides the work. Music
composition and publishing remain separate.

## Current workflow

The normal app starts at **Create video → Setup → Opening → Continue → Finish**. The train /
Tokyo / 90-second preset supplies character, outfit, fixed camera, continuous scenery and a
calm routine. Each step shows the next useful action. Existing scene tools are under Advanced.

Generation uses **Copy prompt → Open Flow → Import native result → Review**. The app saves
reference hashes, prompts, parent lineage, attempts, confirmed prop states, reviews and credit
reservations. Accept continues from the clean reviewed parent; Retry makes one focused
correction. Refresh and an unknown external result do not create another generation request.

Finish assembles only accepted footage at its measured native cadence, trims to an explicitly
reviewed exact ending, and can add one continuous local soundtrack. The verified export can
enter the existing YouTube delivery review and public/private bundle workflow.

[F00–F11](docs/tasks.md) are implemented. [F12 evidence](docs/evidence/f12-flow-workflow.json)
records full-length engineering verification and target-Mac UI observations. A synthetic
90-second video verifies software behavior, not TABI likeness or release approval.

## Remaining production gates

Marco wants almost entirely automatic preparation for 30 × 90-second videos per month, with
new combinations and some new assets each time. That full target remains unqualified:

- No supported external consumer Flow connector, unattended native continuation or enforceable
  account-wide spending cap was established in [F00](docs/evidence/f00-flow-execution.json).
  The installed app does not include this chat's browser automation.
- A real 90-second episode and a fresh setting/outfit variation still need full visual/listening
  review, measured rejected generations, credits and human effort through the guided workflow.
  Café and walking require separate creative trials.
- Source art, original music, exact provider/model commercial terms, disclosure and release
  metadata need current evidence. Commercial output permission does not guarantee YouTube
  monetization.

The selected creative comparison is `docs/assets/clip-tests/TABI-Flow-Train-90s-DRAFT.mp4`.
Marco calls it the best result so far, with a mouth defect near 10 seconds and later particles.
It is preserved with its [review history](docs/progress.md#p01--flow-baseline-selected-and-repeatable-workflow-review).
The earlier calm-window draft and rejected preparation experiments remain historical evidence.
Their passing technical checks do not override Marco's visual feedback.

The existing Tokyo 8/7/7-second native sources import as **528 frames / 22 seconds** without
inheriting the combined scene's one-second timestamp gap. Invented props and particles still
require visual rejection; fixing timestamps does not repair those pixels.

## Cost and tool boundaries

Use existing Google entitlement and local tools. No new subscriptions, paid API, plugins,
licence purchases or credit top-ups are part of the route. Record a freshly observed Flow
allowance and displayed per-attempt cost for each run; included compute is limited.
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
