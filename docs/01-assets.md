# Asset production and approval specification

## Reference and style foundation

Obtain the actual approved Tabi reference and channel artwork from Marco or the existing asset collection. Do not assume the channel banner is a layered character master. Preserve an original copy and document its source. Create a contact sheet containing front/side/three-quarter views, approved seated silhouette, head-to-body proportions, frill shapes, headphone design, face states, outline treatment, and palette swatches sampled from the approved art.

Style: quiet, pastel, soft contrast, simple recognizable shapes, restrained lavender/peach or the currently approved zen palette. Tabi should remain less human in proportion and appearance, following the reference. Avoid extra musical notes and unnecessary text. Do not add a new outfit or anatomy without art review. Country-influenced casual outfits are later packs, not traditional clothing by default.

Create a style guide with approved and rejected examples. Lock camera, light direction, line weight, texture density, shadow softness and proportions before animation. Hand-drawn/AI-assisted source artwork is allowed; every output still needs cleanup and review.

## Asset inventory

| Pack | Required V1 assets | Source and export |
| --- | --- | --- |
| Character reference | Contact sheet, palette, measurements, neutral expression | Editable source plus PNG contact sheet |
| Seated character | Body, head, eyes, eyelids, frills, arms, headphones; back/front pieces where needed | Layered source; aligned RGBA PNG pieces |
| Core actions | Idle loop, blink overlay, look entry, observing hold/loop, look exit | Authored animation source; RGBA frame sequence or tested alpha video |
| Train interior | Cabin background, seat, table foreground, window frame, optional glass highlights, separate interior light mask | Aligned RGBA PNGs plus mask PNGs |
| Window geometry | Exterior visibility mask and optional reflection/light masks | Grayscale PNG, explicit white-is-visible semantics |
| Tokyo exterior | Sky, far silhouette, mid buildings, near passers, one distinct scheduled landmark | Separate normalized layers; seamless strips only where needed |
| Weather | Gentle rain animation and glass droplets; approved strength range | Parameterized effect or prepared alpha loop |
| Lighting | Day/dusk/night values and separate cabin/Tabi masks | Named profiles and reference stills |
| Sound | Finished original music, optional owned/licensed ambience | WAV masters; separate ambience stems |
| Release artwork | Thumbnail composition, cover artwork source and exports | Editable source plus export presets |
| Café proof | Interior, window mask, exterior, appropriate seated placement | Independent template using shared engine |

Optional action pack: drink, book/page turn, headphone adjustment, sleep entry, sleeping loop, wake exit. Each requires new approved interaction drawings and transitions. A sleep loop must not repeatedly replay the act of falling asleep.

## Production steps for the character

1. Trace or clean the approved seated drawing into separated pieces without changing the silhouette.
2. Reconstruct hidden regions behind the head, arms and props; no unpainted gaps may be exposed by motion.
3. Put all pieces on one agreed canvas with fixed pivots and a seat anchor. Record pivot locations rather than guessing them during compositing.
4. Author slow breathing through local torso/shoulder movement; avoid scaling the entire character. Keep facial parts attached.
5. Author blink shapes and timing; blink is a facial channel and does not restart the body loop.
6. Author idle-to-observing and observing-to-idle clips, with matching endpoint poses.
7. Export at the project's frame rate, inspect every frame of transitions, and compare the first/last loop boundary.
8. Inspect alpha edges against black, white, lavender and peach. Correct matte halos and premultiplication errors.
9. Register actions with pose IDs, channels, entry/exit conditions, prop states and their compatible template/camera.
10. User approves the pack; record version, hash and approval note.

Suggested starting durations, adjustable after review: idle 8–12 seconds, look transition 1–2 seconds, observing loop 8–15 seconds, blink 4–8 frames at 30 fps. These are animation design proposals, not generative prompts guaranteeing those durations.

## Environment preparation

Prepare layers individually where possible. A depth mask extracted from a single image leaves hidden areas missing; repaint or inpaint behind foreground objects. Test parallax at maximum approved displacement before accepting a pack.

Start at the resolution needed for the shot. A 1920×1080 scene canvas and exterior strips around 3840×1080 are reasonable pilot proposals; preserve higher-resolution source if available. A strip's displayed height depends on the window crop, not on the whole frame. For final 4K, approve sufficient source detail at the actual displayed scale rather than automatically stretching small PNGs.

Seamless strips contain generic buildings, vegetation and distant geography. Landmarks are one-time scheduled sprites with entry/exit times; do not bake a famous tower into a repeating 10-second strip. Record tile period, overlap, transparent edge padding, horizon line, depth coefficient, allowed lighting profiles and safe cropping region.

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
