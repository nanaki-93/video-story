# Current progress

Updated 8 October 2026 (Asia/Manila).

## Final direction and R01 cleanup

[PLAN](../PLAN.md) now defines reference-based asset generation inside video-story, using the
existing `docs/assets/` and `docs/assets/tabi-assets/` library. Generated candidates become
reviewed reusable looks, cabins and Tokyo journeys, with breathing, blinking and small gill
motion. The ordered [implementation queue](tasks/INDEX.md) starts with L07 pack contracts after
R01 completion. The generator, modular pack selectors and three-motion preparation are
**planned**, not already available in the app.

FLUX.2 klein 4B via MFLUX/MLX is the first local multi-reference candidate to qualify. Exact
versions/dependency terms, installation and real Tabi quality/performance remain gated; no
model was downloaded and no new paid service was added. [Initial sources](08-sources.md).

R01 removes the obsolete character-pipeline verifier/test, Flow presence banner, superseded
plans, prototype screenshots and rejected Flow/3D/camera/animation trial files. Source artwork,
the successful L05 pilot and useful shared engine/engineering evidence remain. The source
inventory is now [local-source-manifest.json](local-source-manifest.json). Git history is not
rewritten. **3,110 obsolete files / 2,187,528,245 bytes** were removed. All **486 protected
files / 1,920,944,845 bytes** match their baseline hashes, including all 327 supplied media
files and the final pilot. The unrelated IDE index is unchanged; no MP4 is tracked.
[Cleanup evidence](evidence/r01-repository-cleanup.json).

R01 passes **289 core tests, 62 actual-media integrations and six frontend tests**, plus Ruff,
formatting, 63 schemas, TypeScript, production build, wheel and sdist. Package inspection confirms
the retained renderer and removal of the obsolete banner. Three loopback tests were blocked by
the sandbox initially and passed with local-network permission. Existing validator-size and
test-client-deprecation advisories remain. The R01 scope does not claim a new browser/art review.

## Implemented asset-to-video workflow

The app saves fixed illustrations, window masks, up to three scenery strips and independently
timed transparent PNG loops. The normal UI creates, previews and exports ordinary episodes
through shared Python services. API/CLI share the compiler, renderer, audio and owned job
lifecycle. Existing advanced asset/action, audio, release, backup and cache tools remain useful.
Read-only legacy preferences/retirement checks do not execute old generators.

The L04 milestone passed 298 core checks, 62 actual-media integrations, six frontend checks,
63 schemas, TypeScript, build and wheel/sdist verification. Those are historical checkpoint
counts; R01 records the post-cleanup totals. Chrome scene → preview → 1080p export/download →
reuse was verified with synthetic geometry and silence, not approved Tabi artwork/music.
Retained evidence: [scene rendering](evidence/l02-lofi-render.json),
[normal UI](evidence/l03-lofi-ui.json), [complete milestone](evidence/l04-lofi-refactor.json).
The current synthetic regression project remains in `.local/l03-lofi-ui/`.

## Preserved real Tokyo pilot

L05 prepared the original train illustration, window matte, six-district Tokyo strip, closed-eye
sequence and foliage, then rendered **90 seconds / 2,700 frames / 30 fps / 1920×1080 with no audio**.
Full decode, timestamps and fast-start checks passed. Ten inspected source frames had zero
variation across 935,558 protected pixels; the next-cycle frame matched the opening frame.
Chrome played the complete export without media/console errors. [L05 evidence](evidence/l05-tokyo-lofi-pilot.json).

The preserved working project is `.local/tokyo-lofi-pilot-v1/prepared-v3/`; current generated
inputs, request, launcher, deliverable video and project ZIP remain. Earlier aborted/superseded
`prepared-v1/` and `prepared-v2/` were removed in R01.

This remains a draft. **L06 book orientation is not corrected yet.** The correction prompt was
saved after the requested built-in editor was unavailable; recheck availability when doing that
task or use the qualified future backend. Tabi's existing outfit/cabin are baked into the master;
L07–L13 prepare real separated variants rather than pretending those parts are interchangeable.
Foliage repeats at district joins and the 1664×936 source is scaled to 1080p. Final visual review,
source rights, Safari and representative final-art long-form/native-4K checks remain pending.

## Next implementation

L07 adds strict pack/recipe contracts without changing existing scenes. L14/L15 add generation
contracts and the source catalog; L16 qualifies the backend with bounded real tests. Layered
preparation/composition can progress synthetically while model installation or art review waits.
Follow [tasks](tasks.md) one verified step at a time. [Acceptance](38-v1-acceptance.md) defines the
actual generator/UI/creative completion gates; a passing test suite does not approve publication.
