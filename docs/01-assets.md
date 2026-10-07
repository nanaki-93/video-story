# Asset production and approval specification

The active scope is the [final reference-assets plan](../PLAN.md) and
[generation contract](39-reference-assets.md). The first reusable train family needs independent
looks, cabins and journeys with breathing, blinks and small gill movement. Advanced actions are
optional later packs, not prerequisites for this milestone.

## Reference and style foundation

The supplied collection has now been inventoried: see [supplied asset audit](09-implementation-review.md) and the per-file [hash inventory](asset-inventory.json). `assets/tabi-character-profile.png` is an actual reference candidate with turnaround, palette and proportions; `assets/scenario/tabi-train-example.png` supplies the seated scene. Their presence does not establish approval. Reuse these originals for comparison and record the exact selected source hash and its review state in each preparation manifest. No replacement Tabi design is needed for technical development.

Obtain the actual approved Tabi reference and channel artwork from Marco or the existing asset collection. Do not assume the channel banner is a layered character master. Preserve an original copy and document its source. Create a contact sheet containing front/side/three-quarter views, approved seated silhouette, head-to-body proportions, frill shapes, headphone design, face states, outline treatment, and palette swatches sampled from the approved art.

Style: preserve the selected reference. The supplied profile depicts a lavender/pink axolotl, pink frills, forehead star, large headphones, a green coat and gold patterned trim. These observed details take precedence over the earlier generic lavender/peach palette brief; approval is still pending. Tabi should remain less human in proportion and appearance, following the reference. Avoid extra musical notes and unnecessary text. Do not add a new outfit or anatomy without art review. Country-influenced casual outfits are later packs, not traditional clothing by default.

Create a style guide with approved and rejected examples. Lock camera, light direction, line weight, texture density, shadow softness and proportions before animation. Hand-drawn/AI-assisted source artwork is allowed; every output still needs cleanup and review.

## Asset inventory

| Pack | Assets for the active train milestone | Source and export |
| --- | --- | --- |
| Character reference | Contact sheet, palette, measurements, neutral expression | Editable source plus PNG contact sheet |
| Seated character | Body, head, eyes, eyelids, frills, arms, headphones; back/front pieces where needed | Layered source; aligned RGBA PNG pieces |
| Gentle motions | Slow breathing cycle, aligned blink states, small gill cycle, compatible rest states | Authored states/settings; aligned RGBA frame sequences in an existing ActionPack |
| Train interior | Cabin background, seat, table foreground, window frame, optional glass highlights, separate interior light mask | Aligned RGBA PNGs plus mask PNGs |
| Window geometry | Exterior visibility mask and optional reflection/light masks | Grayscale PNG, explicit white-is-visible semantics |
| Tokyo journey | Several distinct district views with consistent perspective/light and reviewed joins | Normalized strips with exact wrap padding; optional depth layers |

Cleared music, release artwork, weather/light effects and additional scene families are separate
production or optional extension work. The current acceptance is silent.

Optional action pack: looking/observing, drink, book/page turn, headphone adjustment, sleep entry, sleeping loop, wake exit. Each requires new approved interaction drawings and transitions. A sleep loop must not repeatedly replay the act of falling asleep.

## Production steps for the character

1. Trace or clean the approved seated drawing into separated pieces without changing the silhouette.
2. Reconstruct hidden regions behind the head, arms and props; no unpainted gaps may be exposed by motion.
3. Put all pieces on one agreed canvas with fixed pivots and a seat anchor. Record pivot locations rather than guessing them during compositing.
4. Author slow breathing through local torso/shoulder movement; avoid scaling the entire character. Keep facial parts attached.
5. Author blink shapes and timing; blink is a facial channel and does not restart the body loop.
6. Author a restrained gill motion with matching rest/return states; keep the head fixed for the first pack.
7. Export at the project's frame rate, inspect every frame of transitions, and compare the first/last loop boundary.
8. Inspect alpha edges against black, white, lavender and peach. Correct matte halos and premultiplication errors.
9. Register actions with pose IDs, channels, entry/exit conditions, prop states and their compatible template/camera.
10. User approves the pack; record version, hash and approval note.

Initial motion timing is chosen from reviewed source states and the selected rational fps.
Separate slow breathing from sparse blinks and occasional gill accents. Do not generate each
frame independently or scale the entire character to substitute for local breathing.

## Environment preparation

Prepare layers individually where possible. A depth mask extracted from a single image leaves hidden areas missing; repaint or inpaint behind foreground objects. Test parallax at maximum approved displacement before accepting a pack.

Start at the resolution needed for the shot. A 1920×1080 scene canvas and exterior strips around 3840×1080 are reasonable pilot proposals; preserve higher-resolution source if available. A strip's displayed height depends on the window crop, not on the whole frame. For final 4K, approve sufficient source detail at the actual displayed scale rather than automatically stretching small PNGs.

Generic depth strips can repeat buildings, vegetation and distant geography. A journey can
include distinct landmarks across a longer reviewed cycle; avoid repeating the same landmark
every few seconds. Review the full route wrap as well as each district join. The existing
advanced renderer also supports one-time landmark sprites. Record period, padding, horizon,
depth, lighting and safe cropping; a stylized journey need not follow a real railway.

Text signage should be authored and checked separately; generated pseudo-Japanese is not accepted signage. Artwork may be Tokyo-inspired without being a precise map. Label geography accordingly.

## Alpha and color contract

Normalize working stills to sRGB RGBA, scene output to SDR BT.709, and masks to grayscale with documented values. Character frames use straight alpha at the interchange boundary; explicitly convert when a source uses premultiplied alpha. Preserve fully transparent pixel behavior and edge colors. Alpha-capable video support must be tested with the installed FFmpeg build; PNG sequences remain a fallback. Never export the final upload with alpha.

Each pack specifies source pixel aspect ratio (normally 1), frame rate, canvas size, origin/pivot, anchor, crop, loop interval, overlap rules, color profile, alpha convention, approval state and compatible scene versions. PNG masks must not be silently gamma-transformed into different opacity values.

## Asset record and provenance

Store stable asset ID, immutable version, original source path, normalized paths, SHA-256 per file or sequence manifest, dimensions, duration/frame count, metadata, approval state (draft/review/approved/rejected), source creator, source/reference IDs, licence evidence, commercial-use status (confirmed/pending/not-permitted), and optional generation model/workflow/seed record.

Keep fonts, sound samples, SFZ libraries, reference images, generation model terms and plugins in the provenance inventory when used. Owning the final recording does not automatically resolve every sample's licence or eligibility for Content ID. Unknown rights do not prevent synthetic development, but block the publish-ready status of affected output.

## Prompt briefs for assisted artwork

Attach the approved reference before using these briefs. They are instructions for still-image preparation; they do not promise exact alpha, layers, animation or seamless tiling from a model.

**Character cleanup:** Preserve the attached Tabi design exactly: proportions, face, frills, headphones and palette. Produce the approved seated three-quarter pose with quiet expression, simple soft shading and clean edges. Keep the full character visible; no text or music symbols. Export a clean cutout if supported. Do not introduce human hands or a new costume. Human cleanup and separation follow.

**Train interior:** Soft pastel zen illustration, fixed three-quarter seated camera, a clear large window, simple seat and foreground table, quiet readable forms, restrained detail. Leave the character area empty. Match the attached reference palette and light direction. No character, no pseudo-text. Generate a flat source; create masks and separate foreground layers in cleanup.

**Environment strip:** Tokyo-inspired residential architecture at the agreed horizon and perspective, restrained palette and texture. Generic repeatable architecture only, no famous landmark or readable text. Request generous horizontal extension; manually inspect and repair both seam and parallax reveal regions.

**Landmark:** One approved recognizable landmark in a compatible stylized perspective and lighting; isolate it with generous transparent padding and no additional scenery. Verify scale and visual placement in the actual scene.

## Acceptance and delivery

Every approved pack contains editable sources, normalized exports, metadata, contact sheets, a loop/transition preview, licence evidence and an approval record. Agent checks dimensions, file existence, frame consistency, alpha presence, loop coverage and state compatibility. Marco reviews likeness, motion, palette and story suitability. Synthetic fixtures stay in a separate directory and never carry approved-real-asset status.
