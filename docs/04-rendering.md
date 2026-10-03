# Timeline compiler and rendering design

## First prove a bounded FFmpeg backend

Build a 10-second synthetic scene before real artwork. Use an exterior strip, one grayscale window mask, a cabin foreground, transparent character rectangle and a WAV tone. Prove exterior clipping, alpha overlay, time-dependent scrolling and audio duration with actual FFmpeg output. Then prove changing speed, clip entry/exit and alpha interpretation. If those fail, fix the backend before adding weather or UI.

A renderer must expose capabilities and reject unsupported effects. Keep the first backend restricted to prepared layers, pre-authored character clips, translate/crop/opacity, tested color treatments, masks, simple rain and scheduled sprites. Do not build a rig editor into one filter graph.

## Global-time evaluation

Let frame `n` represent global time `t = n / fps`. Evaluate every continuous parameter from that global frame. A clip beginning at global frame `s` uses clip-local frame `n-s`; a loop phase is `(n-s) mod loop_length`. A weather loop has an explicit phase origin independent of chunk start.

Travel distance is `D(t)=integral(v(u), u=0..t)`. Piecewise constant or linear speed keys yield analytically integrated segments; maintain a prefix-distance table. A layer position is `x(t)=x0-depth_factor*D(t)`, wrapped only for approved tileable layers. Do not use current speed multiplied by elapsed time. Define clamp/zero behavior outside speed key ranges. Support stops and restart without positional jumps; reverse travel is rejected in V1 unless deliberately supported.

Calculate action frames, particles and lighting deterministically at any requested global frame. Effects with history, such as trails or temporal blur, need a warm-up interval and state reconstruction; either implement that explicitly or declare them unsupported in V1.

## Layer ordering and masking

Default train order: background cabin → exterior group clipped by window mask → glass rain/reflections clipped by their masks → rear-seat occlusion if needed → character back/body/front pieces or prepared clip → foreground seat/table → final restrained grade.

Scene templates provide ordered slots; do not hardcode this order into the engine. Foreground table covers character where specified. Exterior masking must not remove the cabin. A character lighting mask changes only the intended area. Rain belongs to glass/exterior, not Tabi's face. Reference stills document all layer boundaries.

For looping scenery, use sufficient duplicated width and modulo crop to ensure both edges are present. Test near-layer reveal regions and strips at zero, normal and maximum travel distance. Landmarks use authored entry frame, world position and exit condition without wrapping.

## Prepared clips and transitions

Compiler expands each body action into entry transition, active hold/loop, and exit transition. Required poses and props are checked before insertion. Respect the exact authored frame count; never loop a one-shot or retime it silently. Body animation and blink overlay have independent approved channels. A prepared body clip that already contains eye animation marks the blink channel unavailable for that interval.

First and last source frames must match the declared poses; loop continuity is inspected, not fixed by an automatic crossfade. Crossfades between whole scenes are optional and require temporal overlap plus an explicit rule for character visibility.

## Render graph strategy

Normalize media outside the final graph and cache those normalized assets. Use explicit fps, scale, pixel format, timestamp reset/offset and color conversion. Write filtergraph text to a UTF-8 file; escape filter parameters deliberately. Pass process arguments without shell interpolation.

The compiler produces a renderer-independent plan first, then the FFmpeg backend emits filtergraphs and media inputs for bounded intervals. Long schedules should not become thousands of parallel open video decoders. Prefer per-shot/per-chunk graphs and prepared sprite/effect caches. Benchmark memory before allowing concurrent renders.

## Audio assembly

Import finished WAV masters without remastering them automatically. Normalize only the technical interchange format where needed, preserving source originals. Keep ordered placements and trims in samples. Musical crossfade is explicit and previews the real overlap; a hard song boundary is valid when authored. Show changes in effective episode duration when overlaps occur.

Optional ambience has its own gain/fade automation and loop seams. Inspect it against the music; no automatic train noise is mandatory. Mix one continuous PCM audio timeline for the whole episode, then encode AAC once during final mux. This avoids repeated AAC priming/rounding at video chunk boundaries.

Report sample peak, true-peak estimate where supported, integrated loudness and clipping. A proposed ceiling of -1 dBTP is a configurable engineering target, not a distributor rule. Do not force every master to a platform loudness number or apply hidden compression. Warn about clipping and allow deliberate user adjustment before final approval.

## Chunks, overlap and assembly

Choose boundaries at scene cuts where feasible, then cap chunks around 30–120 seconds based on benchmark. Record exact first frame and frame count. A job snapshots all source fingerprints. Render to temporary chunk files and verify frame count, timestamps, dimensions, codec and duration before committing completion.

For spatial filters no temporal padding is needed. For approved temporal filters render pre/post handles and trim to exact core frames. Reset chunk presentation timestamps for encoding while passing original global-time offsets into state evaluation. Render a transition only once over its full overlap; chunk cuts through it must be supported and tested or forbidden by the planner.

Use consistent chunk codec, pixel format, color tags, time base and encoder settings with compatible closed GOPs. Attempt concat/remux only after media compatibility checks. If stream-copy produces incorrect boundaries/timestamps, use a documented concat/re-encode fallback. Do not promise stream-copy when filters still need applying. Assemble video first; mux continuous final audio separately.

## Cache and resume

Cache key includes canonical compiled snapshot subset, referenced media hashes, clip/frame ranges, normalization profile, renderer/backend/compiler version, effects, fps, output profile and relevant tool capability fingerprint. Changing a file in place invalidates its content hash even if the path and asset ID are unchanged. Changing ambience need not rerender unchanged video.

Resume skips only verified compatible chunks. Corrupt/missing chunks rerender; stale ones remain available only as old job artifacts. Interrupted jobs never overwrite approved completed exports. Use available-space estimates before starting and track temporary/intermediate usage. Deleting cache cannot delete original media, editable art, rights evidence or frozen release snapshots.

## Export presets and benchmarks

Proposed presets: proxy 960×540/30 H.264; pilot/final 1920×1080/30; optional 3840×2160/30. Final delivery MP4, SDR BT.709, H.264, stereo AAC at 48 kHz, web-friendly metadata placement. Treat output bitrates as configurable and refer to YouTube's current recommended settings rather than permanently freezing them.

Probe software H.264 and available VideoToolbox encoders; verify output quality and actual support on target Mac. Hardware encoding does not guarantee GPU filtering. Benchmark a difficult 60-second shot containing rain, reflections, a landmark, action transition and lighting change. Record frame rate, wall time, CPU, memory, disk, encoder and output quality at 1080p and 4K.

Initial engineering memory budget proposal: keep ordinary single-job rendering below 12 GB resident memory, leaving room for browser/system; revise based on real measurements. Generation and long rendering do not run simultaneously by default. Estimate final output bytes from measured bitrate/duration and intermediate bytes from actual chunk format. Refuse to promise real-time 4K before measurement.
