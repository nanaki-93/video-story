# V1 implementation and acceptance

Review date: 4 October 2026 (Asia/Manila). All independently implementable software in
T01–T38 is implemented, including the optional activity packs and local generation adapter.
The local web app replaces Kotlin with the user's authorization. **Creative product acceptance
remains pending:** no original finished Tabi music story or publication approval is claimed.

The final workflow audit added explicit template/action-pack review (`a8baa3f`) and completed
the CLI adapters and operations walkthrough (`d0db033`). The [operations guide](37-operations.md)
walks through setup, normal production, troubleshooting, recovery and private backups. Each
[archived task record](archive/v1-tasks.md) retains its own behavior, checks, output and limits.

## Final engineering gates

[Recorded commands, results and warnings](evidence/t38-test-results.txt).

| Gate | Result / evidence |
| --- | --- |
| `make check` | 296 passed; 61 actual-media cases intentionally skipped by this unit gate. Ruff and 64 schema drift checks pass. |
| `make web-check` | 64 generated browser contracts, TypeScript and formatting pass; all four behavioral frontend tests pass. |
| `make web-build` / `make package` | Static UI build, source archive, wheel and hashed runtime requirements produced successfully. No Node runtime requirement. |
| Full `TABI_CONFIG=examples/settings.macos.toml make test-media` | **61 passed in 231.18 seconds**, including actual rendering, audio, crash/recovery, cache, release, backup and authenticated browser-service media flows. |
| Explicit metadata approval | Current hashes, dependencies, compatibility, concurrent/stale edits, synthetic rejection and immutability tested through core/API/CLI. Actual approved test-only geometry renders 30 frames / 48000 samples in three chunks. |
| CLI audio workflow | Actual 48000-sample audition, frozen compilation, queue progress and a three-chunk 30-frame / 48000-sample verified export. |
| Supplied reference walkthrough | Unchanged source PNG imported with rights pending and draft approval; silent watermarked 1080p/30 output verifies 300 frames / 480000 samples. [Commands and reports](evidence/t38-reference-walkthrough.json). |
| Fresh final installation | Wheel plus 17 locked runtime packages installed outside the checkout, in a Unicode path. No Node on runtime PATH; bundled frontend hashes and `setup-check` pass; installed CLI re-verifies the draft export. [Installation report](evidence/t38-installed-runtime.json). |
| Installed final browser workflow | Chrome plays/seeks the 1080p draft, renders a fresh 300-frame proxy, seeks to five seconds and displays exact frame 150 with PNG SHA-256 `ffab6e9c3b7d90f9142d216c99b5e98fa7f457349d32fd979d4d5e0f62ee872d`. [Observations](evidence/t38-installed-browser.json), [screenshot](evidence/t38-installed-preview.jpg). |
| Repository/distribution audit | Zero tracked MP4s; all five original clips remain local. Wheel source matches all 103 Python modules, with no MP4, font or runtime/media binary bundled. [Audit](evidence/t38-repository-package-audit.json). |

The evidence machine is Apple M5 Pro, 48 GiB unified memory, macOS 27.0.1 arm64;
Python 3.11.16, FFmpeg/ffprobe 9.0.2, uv 0.11.0. Node 25.8.2 and npm 11.14.1 are build tools
only. T33/T29 verified native Safari 27.0.1 and Chrome 154 playback, seek, decoded audio and
exact-frame PNG agreement. T37 proved the full long export in the embedded Chrome player.

Unit tests exercise contracts, time/sample semantics, action/prop state, concurrent writes,
immutable approvals, request/authentication boundaries, caches, portability and recovery.
Media tests render/decode actual files; they are not mocked FFmpeg success responses.
Temporary owned geometry used to exercise positive approval paths is clearly labeled test-only
in its provenance and review notes. Those fixtures cannot establish approval of the supplied art.

## Task and milestone coverage

| Tasks | Implemented and verified | Acceptance still requiring real inputs |
| --- | --- | --- |
| T01–T05 | Locked development setup, strict versioned schemas, safe persistence, toolchain probing, reproducible fixtures and immutable asset registry. | None for their engineering gates. |
| T06–T08 | Original source/hash/visual audit, concrete layered-art requirements, synthetic action/environment packs, source-preserving import and review infrastructure. | Reference selection, editable/separated real artwork, source timing/normalization and artistic review. |
| T09–T13 | Rational/global timeline, deterministic curves/schedules, action/state compiler, window masks, parallax/landmarks, shared CLI previews and frozen snapshots. | Real-art evaluation of the completed engine. |
| T14 | Actual 90-second installed synthetic pilot and review tools; no false Tabi approval. | Approved 90–120-second Tabi visual pilot. |
| T15–T18 | Sample-based music timeline, continuous audio/ambience, weather/light effects, scene transitions, story beats and continuity notebook. | Original-master listening, restrained-effects and story review. |
| T19 | End-to-end short/long render infrastructure and authored story support. | A 5–10-minute finished original-music Tabi episode, viewed and heard by Marco. |
| T20–T24 | Durable owned jobs, crash recovery, verified chunk reuse/assembly, cache/storage controls, export profiles and private/public release preparation. | Production release inputs, credits/licences, creative and disclosure decisions. |
| T25–T33 | All planned local web pages use real Python services; authentication, media ranges/SSE, upload/edit/preview/audio/render/release/backup flows, settings and installed launcher. | Human listening/release decisions remain pending on the relevant screens. |
| T34 | A distinct café template runs through the same renderer/compiler and real export path. | Final café artwork and approval. |
| T35 (optional) | Explicit sip/read/sleep transitions, props, face ownership and compatible outfit switching. | Authored real activity/outfit art. |
| T36 (optional) | Loopback generation adapter, model/workflow/node allowlists, durable prompt reconciliation, bounded draft imports and offline rendering independence. | Validation with a selected actual ComfyUI/model/workflow; no model was downloaded or real inference claimed. |
| T37 | 45-minute native 1080p recovery/resource/boundary gate and native 4K 60-second qualification. | Full-length native 4K and workload-specific real-art performance are unqualified. |
| T38 | Complete operations/CLI workflow, final gate/evidence review and explicit pending-input register. | Marco's final product and creative acceptance. |

M0, the synthetic parts of M1–M3, M4's engineering gates, M5 and M6's implemented software are
covered. Real-art M1/M2 and original-music M3 remain open creative gates; their dependent
production-ready release cannot be declared complete through fixtures. No task is marked
complete merely because its UI has a button.

## Measured sustained rendering

These T37 runs used the recorded compiler/renderer fingerprints on this Mac; the reports retain
exact versions and synthetic workload details. T38's changes add review/CLI operations without
changing rendering algorithms; the complete media regression gate checks the final build.

| Workload | Verified output | Wall time / throughput | Peak sampled worker + tools RSS |
| --- | --- | --- | --- |
| Native 1080p, 45 minutes, recovery injected | 81000 frames; 129600000 decoded samples; 184/184 independent frame comparisons | 4022.756 s including restart/recovery and final verification; 20.135 fps | 3.05 GiB |
| Native 4K, 60 seconds | 1800 frames; 2880000 decoded samples; 6/6 quality comparisons | 305.746 s; 5.887 fps | 11.29 GiB |

The 1080p worker retained two verified chunks through an injected crash, with unchanged hashes.
Worker RSS medians across steady thirds were 151.22 / 157.89 / 158.30 MiB. VideoToolbox byte
identity is not required; schedules, presentation times, decoded frame/sample counts, media
integrity and frame tolerances are checked. [Full benchmark evidence and measurement limits](36-longform.md).

## Creative inputs still outstanding

| Input | Exact remaining decision or delivery |
| --- | --- |
| Tabi style/seated reference | Select the original hashes in the [review packet](12-tabi-art-review.md), or identify replacements. The existing profile and train still were inspected and retained unchanged. |
| Character/action masters | Editable aligned pieces, hidden-region repairs, reviewed anchors/pivots, source frame rates/loop intervals, transition endpoints and face/foreground ownership. |
| Train/Tokyo environment | Separated cabin/window/foreground and three prepared depth layers, completed hidden regions, wrap/landmark choices, normalized canvases and day/dusk looks. |
| Music | Finished original WAV masters with enough material for the intended story length; factual titles/credits and rights evidence. Synthetic tones do not satisfy this input. |
| Reviews | Actual alpha/likeness/motion/pilot, full story/audio, effects, thumbnail, rights and public metadata/disclosure review. Every approval binds the reviewed content hash. |
| Optional generation | Operator-selected installed models/workflows with factual versions/hashes, licences and a real integration trial. The adapter's protocol fixture is not proof of generated-art quality. |

The supplied still walkthrough is useful visual evidence of the application, but remains a
silent draft. No new Tabi design, animation, licence, identifier, generation history or
permission was invented. Nothing was published or uploaded to an external service.

## Known limits and deferred work

- One active export is the qualified default. Parallel projects and full 45-minute native 4K
  workloads need their own resource qualification. Conservative storage estimates are not a
  continuously measured peak-disk guarantee.
- Browser playback/seek is approximate. Use renderer-generated PNGs for exact frame review.
  Long outputs can still be reviewed in the app through the verified embedded player.
- The app requires external Python/FFmpeg. No native DMG, signing/notarization, auto-update,
  Windows support or general-purpose rig/animation editor is claimed.
- The generated validator bundle is about 3.07 MB raw / 280 KB gzip. Vite emits a size advisory;
  validators are precompiled and do not require runtime code generation. The Python test client
  emits a Starlette/httpx deprecation warning; tested routes pass.
- Schema 1.0 has no prior schema migration registered. Backups/revision guards and migration
  infrastructure are tested; any future migration needs its own explicit transformation.
- Private backups are directory bundles, not encrypted archives. Public release files do not
  replace private source backups. `.local` projects and all MP4s are intentionally outside Git.
- Native Kotlin/Compose, 3D/automatic depth extraction, dialogue/lip-sync, cloud render/accounts,
  collaboration, analytics and automatic publishing remain out of scope as recorded in PLAN.md.

Software completion is distinct from creative and publication readiness. Final external platform
checks and manual uploads remain with Marco. The application neither guarantees monetization or
distributor acceptance nor infers that an unresolved rights/approval item has been satisfied.
