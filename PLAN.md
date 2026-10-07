# Tabi Story Studio product plan

Tabi Story Studio makes local lo-fi music videos from reusable illustrated assets. Python owns
asset validation, composition, frame/sample timing, audio, rendering and delivery. A TypeScript
web UI guides scene setup, music selection, preview and export. Music composition and publishing
remain separate.

Marco authorized this refactor on 7 October 2026, including removal of unnecessary old code.
Flow whole-scene generation was rejected for exterior jumps, eye defects and repeated attempts.
Its prompting, credits, retries, clip-chain workflow and separate queue are removed. Earlier
source artwork, music, native clips, project records and exports remain preserved on disk.

## Current workflow

1. Import the master illustration and any prepared masks, scrolling strips, transparent PNG
   animations and finished music into **Asset library**. Keep factual provenance and immutable
   versions. No generator is required by this route.
2. In **Create video**, save a reusable scene: fixed master, rational frame rate, optional window
   mask and scenery layers, optional independent overlay loops. The UI accepts repeat/delay in
   seconds; Python persists exact integer frames. The master determines the canvas.
3. Choose the saved scene, title and ordered music. Set a duration or fit the complete tracks.
   Python compiles an ordinary episode through the same core used by the CLI. It saves the scene
   configuration into a content-addressed template so later recipe edits leave existing videos
   unchanged.
4. Render a short **Preview**, inspect exact frames and loop/mask boundaries, then **Export**
   through the shared frozen-snapshot job service. Adjust music in **Music** as needed.
5. Reuse the scene for subsequent music videos. Prepare a new version only when assets or motion
   need to change. Production approval and manual publishing remain explicit separate steps.

The primary workflow is asset selection and timing, not per-video JSON editing. Existing story,
action-pack, continuity and precise audio tools remain under Advanced where useful. They use the
same renderer and do not introduce a second timeline compiler or general-purpose editor.

## Asset route for the lo-fi channel

<a id="proposed-asset-route-for-the-lo-fi-channel"></a>
Start with one selected TABI/train illustration. Keep TABI, cabin, furniture, gills, hands,
book and cup stable. Prepare a fixed white-visible exterior mask preserving all overlapping
edges. This avoids needing a body rig or changing camera for the first pack. The supplied
1664×936 RGB train reference is a candidate, not an approved layered or native-4K master.

Prepare only the intended motion:

- Small aligned full-canvas RGBA blink sequences, including clean coverage of the open eyes and
  authored intermediate eyelid states. The master is visible during gaps. Existing generated eye
  defects are not repaired merely by looping them.
- Long Tokyo panorama strips with varied interesting districts, a shared horizon/perspective and
  consistent light. They can represent a stylized journey. Their repeated padding must match the
  opening pixels exactly; up to three depth layers share a travel-speed curve.
- Optional restrained rain, reflections or similar prepared overlay loops. Every overlay uses
  independent global-frame timing, so short blinks do not restart the scenery.

The scene recipe supports a still-only composition, up to three cyclic scrolling layers, and up
to eight aligned PNG overlay loops. Source dimensions, fps, alpha, hashes, sequence bounds and
scenery padding are validated. There is no automatic image segmentation, inpainting, blinking,
city generation or district matching. Asset creation happens before reuse.

Chunk boundaries and nonzero render ranges preserve the same global schedule. Arbitrary final
video lengths are not promised to be seamless at the full video's last-to-first join. Review
that join if the whole output will repeat. A prepared cyclic strip can still look repetitive or
have a poorly designed boundary; pixel validation is not artistic approval.

## Production gates

| Input or review | Remaining work |
| --- | --- |
| Approved art | Select the actual master/reference hashes and compare likeness; never create a substitute TABI design because a reference is missing |
| Window mask | Prepare and inspect window edges, character overlaps, props and reflections |
| Eye animation | Prepare clean, aligned authored states and inspect closing/opening, coverage and return to the master |
| Tokyo scenery | Prepare diverse compatible strips; review perspective, pacing, district joins, wrap and repetition |
| Music | Supply original/cleared finished masters, enough material for the requested length, credits and rights evidence |
| Creative pilot | Review full picture and sound, then a representative long-form video using the final assets |
| Release | Recheck commercial terms, source rights, approved hashes, creative review and factual public metadata before manual upload |

Engineering fixtures are synthetic geometry and silence, never approved TABI artwork or music.
A passed test does not approve production art. Monthly throughput and full native-4K long-form
resource demands require measurement with the final pack; previous workload timings apply only
to their recorded fixtures.

## Runtime and storage boundaries

| Area | Decision |
| --- | --- |
| Runtime | Local Python/FastAPI worker with bundled TypeScript UI, authenticated loopback only |
| Ownership | Shared Python compiler/render/audio services for API and CLI; no FFmpeg or timeline semantics in the browser |
| Time | Integer frames/samples and rational fps; music retains complete sample ranges |
| Documents | Strict versioned schemas, stable references, content hashes, atomic draft writes and revision guards |
| Approved content | Immutable approved versions; edits create new versions and invalidate old approval for new content |
| Worker | Registered roots, Host/Origin/CSRF checks, authenticated media, readiness handshake, owned cancellation/recovery |
| Media | Retain source artwork/music separately from disposable caches; never commit MP4 files |
| Delivery | Verified local export, explicit review/public-private bundles and manual publishing |

The target Mac is Apple M5 Pro with 48 GB memory. The app needs externally installed Python and
FFmpeg; Node is a build dependency. No database, cloud rendering, native Kotlin/Compose packaging,
new paid subscription/plugin/licence purchase or credit top-up is introduced.

Before any future generator/model/font/asset is adopted, check official commercial-output terms,
weights, dependencies, hosted terms, attribution and territorial restrictions. Record the exact
version/revision, source links, date and unresolved restrictions. Unknown rights remain pending.
Commercial permission does not establish YouTube Partner Program eligibility. Do not resume old
character-generation experiments or infer unlimited compute from existing Google entitlements.

## Implementation and verification

Follow [AGENTS.md](AGENTS.md) and the [task index](docs/tasks/INDEX.md). Each verified coherent step
has a task-scoped commit and evidence. Run core/schema checks, frontend checks/build, package
verification, actual FFmpeg integrations and normal-browser scene → preview → export acceptance.
Check source hashes and unrelated staged files remain unchanged.

[Operations](docs/37-operations.md) describes the controls. [Progress](docs/progress.md) and
[acceptance](docs/38-v1-acceptance.md) separate current results from creative gates. Earlier Flow
[tasks](docs/archive/flow-tasks.md), [V1 history](docs/archive/v1-progress.md) and
[production trials](docs/archive/production-progress.md) are historical evidence.

Direct Flow control, automatic visual approval, new providers, a body rig editor, automatic image
preparation, native app signing, dialogue/lip-sync, collaboration, analytics and publishing are
outside this refactor.
