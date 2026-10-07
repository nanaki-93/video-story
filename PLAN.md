# Tabi Story Studio — final asset workflow plan

Agreed direction, 8 October 2026. Tabi Story Studio is a local app for producing lo-fi videos
from **reference-generated, reviewed and reusable illustrated assets**. Each video can select a
different Tabi outfit, train interior and stylized Tokyo journey, with two or three gentle motions.
The app owns reference selection, asset generation, preparation, composition, preview and export.
Music creation and manual publishing stay separate. The first acceptance video has no music.

The fixed-scene renderer and silent Tokyo pilot already work. Reference generation, modular
packs and their preparation controls are the planned next implementation phase.

## The workflow Marco will use

1. **Choose references.** Browse the existing `docs/assets/` library, including
   `docs/assets/tabi-assets/`, or import additional images. Select an identity reference, the
   seated pose/layout and any outfit, cabin, scenery or style references needed for this asset.
   Existing local files need registering once, not uploading for every video.
2. **Generate a specific asset.** Choose Outfit, Cabin, Panorama or Targeted correction;
   describe the requested change and the parts to retain. The app submits the actual selected
   images to a local image-editing model. A prompt exporter alone does not complete this feature.
   Generate one candidate by default; another attempt is a deliberate action, never an endless
   retry loop. Reference guidance reduces variation but cannot guarantee likeness or alignment.
3. **Compare and keep.** Compare the result with its source references, including eyes, gills,
   headphones, anatomy, clothing, book and light. Save a kept candidate as a new draft version.
   A region edit can preserve pixels outside its mask through deterministic compositing.
   Keeping a candidate is separate from approving a prepared pack for production.
4. **Prepare a reusable pack.** Guided controls prepare aligned layers, clean hidden regions,
   window masks, scenery strips and short motion cycles. Validate technical compatibility and
   preview their edges and loop joins. Generated RGB images are not automatically cutouts or
   animation-ready layers. Save the reviewed look, cabin or journey once.
5. **Make a video.** Select compatible Look + Cabin + Tokyo journey, two or three gentle motions,
   duration and optional cleared music. Render a short preview, then export using the current
   shared Python renderer. A later video reuses the prepared packs or adds a reviewed new one.

## Existing assets are the starting library

[Source artwork](docs/assets/README.md) includes the character profile, seated train composition,
50 outfit/style images, eight emotion references, 12 train-action stills, six walking poses,
97 breathing and 129 drinking PNG frames, and six distinct Tokyo panoramas. Ignored files must
be discovered on disk too. The original source inventory is evidence, not an exhaustive live
catalog or an approval record. See [source findings](docs/09-implementation-review.md).

Use these references to preserve Tabi's existing design. A whole character profile sheet may
need a selected crop for the intended pose; preserve the original and record the crop. Existing
outfit images can guide clothing changes without replacing Tabi's identity. Existing sequences
need source-fps, anchor, face-channel and loop-boundary review before use; their filenames do not
establish that metadata. They are not automatically compatible with a new outfit or cabin.

All originals in both supplied folders stay unchanged. Register normalized paths and hashes;
put generated candidates, preparation files and immutable versions in local project storage.
A fresh Git clone will not contain the ignored artwork: keep those source folders backed up.

## Generation route and cost boundary

Use local image generation on the M5 Pro/48 GB target Mac, with **no new subscriptions, paid
plugins, model licences or credit top-ups**. The first candidate to qualify is **FLUX.2 klein
4B through MFLUX/MLX**, which documents image editing with multiple references. The 4B model
weights are Apache-2.0 and MFLUX code is MIT; the 9B non-commercial model is excluded.
[Official sources and review limits](docs/08-sources.md).

This is a qualification choice, not an installed or proven backend. Before adoption, pin the
exact model revision, adapter, text encoder, VAE, tokenizer and dependencies; review each set
of terms, notices and regional restrictions; measure real Tabi quality, memory, storage and
latency. Model files are large and require an explicit installation choice with the estimated
size shown. This planning/cleanup task does not download them. Keep the optional backend out
of the basic render installation until qualified.

The qualification has a fixed small attempt budget. If it cannot preserve Tabi or takes too
much operator work, record the failed gate and continue with imported prepared assets while
reporting the missing generator capability. Do not silently switch to a paid provider or mark
an import/prompt workflow as a working generator. Existing app subscriptions do not imply a
third-party image-generation API entitlement. Commercial permission alone does not approve the
source artwork, final output or YouTube monetization.

## Separate assets, stable composition

A layout family fixes the camera, canvas, rational fps, character anchor, window geometry,
layer order and scenery period. Compatible variants use one exact existing `SceneTemplate`.
The new pack documents select assets and existing action packs; they do not create another
renderer or animation format.

| Pack | Contents and replacement boundary |
| --- | --- |
| Cabin | Empty cabin/background, white-visible window mask, foreground table/props and compatible lighting; no baked-in duplicate Tabi |
| Look | Seated Tabi in one outfit, matched breathing/gill motion and aligned eye states, with explicit pose and prop constraints |
| Journey | Several visually distinct Tokyo views joined into reviewed strips with a shared horizon, perspective, light and verified wrap padding |
| Recipe | Exact pack versions, selected motions, global frame timing, seed, travel setting, duration and optional music |

A different interior can change upholstery, trim and decoration inside the same layout family.
Moving the window or camera requires another prepared family; arbitrary images are not freely
interchangeable. A new outfit needs matching body motion assets. Face reuse is allowed only
when anchors, lighting and ownership match. Complete the cabin behind the moving character and
retain foreground occlusion so neither the old body nor missing regions become visible.

The Tokyo journey is stylized rather than a claim about a real train route. Reuse and extend
the six supplied districts; avoid visible scenario jumps, abrupt perspective changes and the
same repeated filler between every landmark. Review district joins at the intended speed.

## Motion and rendering

Start with slow **breathing**, sparse **blinks** and an occasional small **gill movement**.
Keep the head still for the first real pack to protect eye registration. A later head movement
requires matching face frames or a motion that owns both body and face for that interval.

Create motion from a few reviewed aligned states and bounded local deformation/compositing.
Do not ask an image model to redraw each video frame. A rigid full-character scale or an
unreviewed eyelid patch is not sufficient proof of natural breathing or a good blink. Use the
existing `ActionPack`/body/face occupancy and entry/exit pose rules. No walking, talking,
lip-sync, 3D reconstruction or clip-end matching belongs in this version.

Python keeps body coverage and independent global-frame phases through chunks and nonzero
previews. All persisted times are integer frames/samples. A seamless repeating *whole video*
requires an explicit compatible duration and matching final-to-first phases; arbitrary export
lengths are not guaranteed seamless. Rendering a longer video reuses assets without generation.

## Architecture and invariants

- Python owns cataloging, generation orchestration, preparation, contracts, composition, jobs,
  timing, audio and FFmpeg. The TypeScript UI calls those same services used by the CLI.
- Use strict versioned schemas and reject unknown fields/incompatible majors. Hash references,
  model manifests and outputs. Seeds support traceability, not a promise of identical GPU pixels.
- Original and approved asset versions are immutable. Changes create new versions; approval
  belongs to a content hash. Draft saves are atomic and revision guarded.
- The worker stays authenticated on loopback, with Host/Origin/CSRF checks, registered roots,
  authenticated media/SSE, readiness checks and owned cancellation. Generation accepts an
  allowlisted backend/configuration, never arbitrary browser commands or executable workflows.
- Bound local generation concurrency and resource use. Persist job state, isolate subprocesses,
  cancel only owned work, and atomically admit verified outputs. No silent network upload or
  download. Failed jobs keep diagnostics without registering partial assets as successful.
- Retain current scenes and snapshots unchanged. Useful shared audio, timeline, cache, release,
  backup and advanced tools remain. No database, general image editor or new timeline engine.
- FFmpeg and optional model files stay external; never commit MP4s or production model weights.

## Delivery order and acceptance

The authoritative ordered tasks are in [docs/tasks.md](docs/tasks.md) and
[the index](docs/tasks/INDEX.md). Start with pack schemas, generation contracts and the reference
catalog. Qualify the model before its live integration; synthetic preparation/composition can
progress while model installation or art review is pending. Then connect API/CLI and the full
UI, finish the book correction, and run the real-assets acceptance.

Completion requires two looks, two cabins and two meaningfully different Tokyo journeys;
inspect all eight combinations, then render one complete 90-second silent video and a
10-minute timing/loop check. Demonstrate a second video made by selecting saved packs without
reconnecting clips, editing JSON or regenerating unchanged assets. Record generation attempts,
operator time and reuse time. A working Generate button, source comparison and real provider
result are required; fixtures alone do not pass the generator gate.

Engineering checks and visual approval are separate. The current successful L05 pilot remains
playable, but its requested book correction is still open. Music rights, final creative review,
Safari, representative long-form/native-4K performance and manual release checks remain explicit
in [acceptance](docs/38-v1-acceptance.md). [Progress](docs/progress.md) distinguishes implemented
features from this next phase.
