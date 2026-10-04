# Masked light, rain and reflection effects

T17 adds three explicit effect kinds to ordered scene-template slots: `tint`, `rain` and `reflection`. Each slot requires a grayscale scene-sized mask, a named strength target and template limits. The template declares `lighting`, `rain` or `reflection` capabilities as applicable. Unknown temporal effects are rejected; trails, motion blur and history-dependent simulation are not silently approximated.

A tint specifies an RGB color and no source asset. The renderer generates a flat color plate whose alpha is controlled by the authored curve and mask. This is a bounded color overlay, not automatic relighting of the character. Put it at the intended point in the template's layer order, with a separate character/interior mask if appropriate.

Rain uses a prepared alpha PNG sequence with explicit loop bounds and episode-matching rational fps. Reflection uses either a prepared alpha still or an explicitly looped PNG sequence. Prepared output, including a declared crop, must match the design canvas. Color/alpha normalization uses the same locked asset pipeline as other layers. Assets and masks can be replaced only through explicit compatible slot assignments; tint color belongs to its immutable template.

Example rain slot inside a reviewed template:

```json
{
  "id": "rain", "z": 20, "kind": "effect",
  "asset": {"id": "rain.prepared", "version": "1.0"},
  "mask": {"id": "train.window-mask", "version": "1.0"},
  "effect": {
    "kind": "rain", "strength_target": "rain_amount",
    "default_strength": 0.0,
    "loop": {"start_frame": 0, "end_frame": 120}
  }
}
```

The corresponding template declares `rain_amount` limits in 0–1. The actual upper bound must come from that asset/style review. The synthetic fixture uses 0.25 rain, 0.20 reflections and 0.22 tint solely as development limits; these are **not approved Tabi palette/effect choices**. Defaults and curve values must fit the limits, and effect curves must use fraction units. Compilation and rendering both enforce the limits. A curve without a supported target cannot silently disappear.

Strength is evaluated at global frames using the shared constant/linear curve semantics and scene-over-episode precedence. Only the alpha plane is scaled, preserving the prepared RGB artwork. The existing source alpha, grayscale mask and slot opacity multiply together. Template layer order places glass effects behind the character and foreground where authored.

`scene.initial_state.weather_phase_frame` is the explicit **global phase origin**, retained as state across cuts. It does not advance with chunks. It must not be later than the scene start when a temporal effect exists. At frame `n`, source selection is `loop.start_frame + (n - origin) mod loop_length`. Fade/buildup is a separate strength curve, so rain may be invisible while its phase continues. Reading a still, seeking or starting a range never resets that origin. Cut/overlap continuity is documented in [story continuity](18-story-continuity.md).

## Reproduction and evidence

```sh
.venv/bin/tabi fixtures --profile effects --output NEW_PROJECT --json
.venv/bin/tabi compile NEW_PROJECT/episodes/episode.synthetic.json --project NEW_PROJECT --purpose synthetic_test
# Use the returned snapshot SHA:
.venv/bin/tabi frame SNAPSHOT_SHA --project NEW_PROJECT --frame 151 --output NEW_FRAME.png
.venv/bin/tabi preview SNAPSHOT_SHA --project NEW_PROJECT --start 0 --end 300 --output NEW_PREVIEW.mp4
```

The effects fixture adds a 12-frame rain sequence, a reflection plate and an interior mask to the existing owned geometry. Its 17 assets and 86 hashed files reproduce byte-for-byte. The compiled episode locks 18 registry inputs, with explicit buildup/fade and dusk curves. No original character art or music changes.

`make check` passes 25 schemas, Ruff and **180 tests**; 26 FFmpeg tests are opt-in. Three new unit cases cover reproducibility, missing masks/capabilities, limit/unit/phase errors, loop overflow, unsupported temporal effects and prior template identity preservation. The two new media cases pass: thirteen stills around curve/loop/action boundaries match independent Pillow composition within three channel values, including protected face/table pixels; complete and split nonzero ranges preserve global rain/light phase. Lossy video comparisons account for BT.709 4:2:0 conversion (99.9% of component errors ≤15 against the independent reference; ≤10 between separately encoded full/split ranges). Existing motion/static media regression checks also passed.

[Frame 151](evidence/t17-effects-frame-151.png) was visually inspected as a synthetic engineering reference. [Compilation](evidence/t17-compilation.json), [frame report](evidence/t17-frame-report.json) and [preview report](evidence/t17-preview-report.json) preserve identities and verification. The ignored clip `.local/t17-effects-verified.mp4` contains 300 frames at 640×360/30 and 480,000 verified stereo AAC samples. The measured render/mix/mux interval was 20.097 seconds on M5 Pro/macOS 27.0.1, Python 3.11.16, FFmpeg 9.0.2. Alpha-only evaluation reduced this from an earlier 42.855-second run, but these runs shared the machine with tests and are not a controlled benchmark.

Effects remain CPU-filtered and substantially slower than the plain fixture. Normalized sequences and masks consume scratch space; 1080p/4K throughput and cache strategy need T22/T37 measurement. Prepared rain/reflection style, real palette limits, real Tabi interaction and Marco's visual approval remain pending. This completes technical behavior against fixtures, not T14/M2 art approval.
