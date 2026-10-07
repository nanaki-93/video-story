# Reference asset generation contract

Planned behavior; not implemented as of 8 October 2026. Product decisions are in [PLAN](../PLAN.md).
This spec complements the existing [asset registry](11-asset-registry.md),
[local service](25-local-service.md) and [activity compatibility](34-activity-packs.md).

## Reference catalog and generation request

Catalog launcher-registered local roots, including the files ignored by Git under `docs/assets/`.
Deduplicate the parent root and nested `tabi-assets` root without hiding their categories. Index
only supported media, resolve paths within allowed roots, and hash readable files. A changed
hash invalidates the cached thumbnail/reference, not the source file. Missing sources have an
actionable relink state. Inspect sequences as a group; do not create hundreds of thumbnails as
if every breathing frame were an unrelated character reference.

A generation request names an output kind (`look`, `cabin`, `panorama`, `correction`), a qualified
backend manifest, ordered hashed image references and their roles (`identity`, `pose`, `outfit`,
`layout`, `style`, `scenery`, `edit_target`), a prompt, integer seed, size and allowlisted options.
Optional crop and edit-mask references are explicit, validated and versioned. Require an identity
source for a character edit, and an edit target for a targeted correction. Respect the qualified
backend's reference count and image-size limits; reject excess inputs rather than silently
ignoring them. Do not claim a single flattened input supplies separate character/cabin layers.

Every output records the original and normalized input hashes, crop/scale/mask operations,
model and dependency revisions, prompt, seed, settings, elapsed time, output hash and factual
rights-review state. One candidate per request is the initial default. Regeneration creates a
new request/version. A kept candidate remains draft until its prepared pack is reviewed.

## Backend qualification and execution

First candidate: FLUX.2 klein 4B through MFLUX/MLX. [Source/terms record](08-sources.md) describes
what has and has not been checked. L16 must record exact code/model commits, weight checksums,
all runtime components, licence texts/notices and unresolved conditions **before execution**.
Keep installation optional and explicit. Rendering existing projects must work without the
backend or model installed. Report unavailable/unsupported dependencies with a useful action.

Qualification uses the actual supplied profile, seated composition, one outfit reference and
Tokyo imagery: one outfit edit, one cabin edit and one panorama variation, with at most one
additional attempt per case (six images maximum). Record human effort, wall time, peak memory,
source preservation and side-by-side visual findings. This is a bounded feasibility check,
not permission to call rejected candidates approved. Marco's review decides whether the quality
and effort meet the channel's needs. If any required asset category fails, state the gap.

Use a persistent typed generation-job record and the existing process/ownership primitives;
render jobs keep their current contract. Initially allow one heavy generation job at a time and
avoid concurrent render/generation overload. Persist start/failure/cancellation/recovery states.
A frozen request determines provenance. Never execute arbitrary commands, download a browser-
provided model URL or resume interrupted GPU work without checking ownership and inputs.
Decode and verify output dimensions/type before atomic registration. A seed is provenance,
not a promise of byte-identical output across machines or model revisions.

## Preparation boundary

Generated or imported candidates enter the same Python preparation service. User-facing tools
are limited to crop/alignment, window/edit masks, layer matte cleanup and loop review. These
are concrete preparation controls, not a general-purpose painting or rigging application.

For region correction, composite the accepted generated region into the source using a reviewed
mask, retaining all pixels outside its coverage. Review edge blending separately. Correcting
an upside-down book still requires valid perspective and hands; a passing pixel-preservation
check cannot approve the art inside the mask.

A cabin pack needs a clean background behind Tabi, window geometry and foreground occlusion.
A look needs alpha, a matching anchor and authored body/face/gill motion. A journey needs aligned
views, visible geographic variety, sensible depth and wrap padding. Explicitly verify source
fps and face ownership when reusing the supplied breath/drink sequences. Never add blinks on
top of a sequence that already controls the eyes.

The preparation manifest records every transform, source/output hash, canvas, rational fps,
anchors, loop ranges, template version and visual-review decision. New revisions cannot mutate
existing approved packs. The compositor only accepts compatible pack versions.

## UI acceptance

`Asset library → Generate from references → Compare → Keep version → Prepare pack → Create video`
must work with a real qualified backend. A user can choose supplied references, see exactly which
images will be used, cancel their own job, inspect a failed job, compare the result, and keep it
without editing files or source JSON. Pack selectors show compatible thumbnails and explain
mismatches. Prompt export and manual import remain useful but cannot pass this generation gate.

Choose outfit, cabin and journey independently; select breathing/blink/gill controls; preview
and export silently or with cleared music. Record all eight 2×2×2 combinations and a second
video that reuses unchanged assets with zero new generation calls. Local generation requires
no new paid app or cloud upload; no quality or monthly throughput guarantee precedes measurement.
