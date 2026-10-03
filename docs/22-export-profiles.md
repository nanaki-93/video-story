# Export presets and verification

The queue uses explicit SDR H.264 presets. Source frame rate is preserved, including rational
rates such as 30000/1001. Presets accept rates up to 60 fps; they never silently retime an episode.

| Preset | Canvas | Video target at up to 30 fps | Stereo AAC-LC |
| --- | --- | --- | --- |
| `proxy` | 960×540 | 3 Mbit/s | 192 kbit/s |
| `1080p` | 1920×1080 | 8 Mbit/s | 384 kbit/s |
| `4k` | 3840×2160 | 40 Mbit/s | 384 kbit/s |

Rates above 30 fps use 1.5 times the video target. These are configurable encoding targets,
not measured output sizes. The final defaults follow the current SDR resolution ranges,
stereo rate and BT.709 guidance in [YouTube's encoding recommendations](https://support.google.com/youtube/answer/1722171?hl=en),
checked 4 October 2026. Publication requirements should be checked again for an actual release.

```sh
tabi profiles
tabi profiles --encoder h264_videotoolbox --fps-num 30000 --fps-den 1001
tabi jobs submit SNAPSHOT_SHA --project ROOT --preset 1080p \
  --encoder libx264 --output exports/final.mp4
tabi jobs submit SNAPSHOT_SHA --project ROOT --preset 4k \
  --encoder h264_videotoolbox --video-bitrate 45000000 \
  --audio-bitrate 384000 --output exports/final-4k.mp4
tabi jobs estimate JOB_ID --project ROOT
tabi jobs work --project ROOT --once
tabi jobs verify JOB_ID --project ROOT
```

Omitting the preset selects `proxy`. Custom width/height must be supplied together and cannot
be combined with a preset. The old direct `preview` command remains available for a bounded
custom preview; queued presets are the final export workflow. Synthetic and draft snapshots
remain visibly labelled regardless of resolution. Choosing a final-resolution preset does not
approve its artwork, music, rights or snapshot.

Software uses `libx264`; hardware uses explicitly requested `h264_videotoolbox` with software
fallback disabled. Advertised encoder availability is checked before rendering, and actual
encoding must succeed. Both paths select High Profile, progressive 4:2:0, CABAC and closed
GOPs approximately half a second long. Software uses two B frames. Hardware explicitly disables
B-frame reordering: FFmpeg 9.0.2 / VideoToolbox produced clamped decode timestamps and one-tick
sample durations in a short 4K test when reordering was enabled. Invalid output was rejected;
frame times were not altered to conceal it. Chunk encoding and assembly fallback use the same
argument builder. No encoder is silently substituted.

[The rejected hardware trace](evidence/t23-videotoolbox-bframes.json) retains the exact packet
timestamps and durations. Regression checks include 4K clips of 1, 2, 3, 11, 12, 13 and 37
frames at 30000/1001 fps with the corrected hardware policy.

## What verification proves

Before publishing any encoded output, the renderer checks dimensions, H.264 High Profile,
progressive scan, square pixels, YUV420P, limited-range BT.709 tags, exact decoded frame count
and every presentation timestamp. Frame timestamps remain within one stream tick of the
rational schedule; stream/container duration metadata must be within one frame. MP4 movie
timescales can round short non-integral-second durations more coarsely than video timestamps.

A bounded MP4 box scanner verifies that the single `moov` header precedes media payloads.
The encoder and final audio mux use FFmpeg's
[Fast Start option](https://ffmpeg.org/ffmpeg-formats.html#mov_002c-mp4_002c-ismv).
AAC-LC is encoded once at 48 kHz stereo, with exact intended sample timing checked independently
and codec padding reported. FFmpeg's audio trim/priming metadata is retained for sample accuracy.
`jobs verify` checks the completed export hash again, decodes it, verifies format/timing and
returns a strict report; it rejects external changes without overwriting the file. This is
delivery verification, not creative or rights approval.

## Reproducible target-Mac measurements

`scripts/benchmark_exports.py` creates a **new** synthetic project for each run. Its 60-second
stress timeline repeats authored test cycles containing three moving depth layers, landmarks,
body transitions, blinks, rain, reflections and lighting. It creates a full-duration synthetic
triangle signal; no real music is stretched. The default design scale is three, producing a
1920×1080 compositing canvas from the geometric fixture. 4K output from that workload scales
the composition. T37 also measured a native 3840×2160 design with `--design-scale 6`.

```sh
.venv/bin/python scripts/benchmark_exports.py \
  --config examples/settings.macos.toml --output-root .local/bench-1080-software \
  --preset 1080p --encoder libx264
.venv/bin/python scripts/benchmark_exports.py \
  --config examples/settings.macos.toml --output-root .local/bench-4k-hardware \
  --preset 4k --encoder h264_videotoolbox
```

Each invocation records machine/tool versions, the frozen job/profile, source canvas, full
export wall time, CPU time, output size, disk availability, cache provenance and memory.
Memory samples sum this worker's RSS and retained live tool children every 250 ms. Separate
per-process high-water marks are also reported; kernel, unrelated apps and unreported GPU
allocations are outside those measures. No other rendering benchmark should run concurrently.

The first native 1080p attempt was [cancelled through the job service](evidence/t23-pre-lut-cancelled.json)
after 215.8 seconds before its first 900-frame chunk had verified. Its sampled process RSS peak
was 3.53 GiB. This incomplete run is not a completed-export speed measurement. The effects
backend now evaluates opacity once per frame through the shared timeline and applies a
256-value alpha lookup table. Commands are scheduled between frames to avoid timestamp rounding
at rational rates. Pixel checks compare it against the earlier per-pixel expression at linear
and stepped boundaries, including partial ranges; differences remain at most one alpha level.
The existing expression path is retained for unusual custom rates above 1,000 fps, beyond the
timestamp precision needed by the preset workflow.

Six sampled decoded frames are compared with uncompressed renderer frames. RGB mean error,
99th-percentile error and PSNR are retained with the PNG pairs. The synthetic engineering gate
is mean error below 3 and 99th-percentile error below 24 levels; visual inspection still matters.
Simple test artwork cannot establish quality for the pending real Tabi assets.

Both cold video-cache runs completed on Apple M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16
and FFmpeg 9.0.2. Each verified all 1,800 frames and 2,880,000 intended audio samples.

| Export | Whole export wall time | Effective fps | Sampled worker + tools RSS peak | Sampled RGB mean / p99 error |
| --- | --- | --- | --- | --- |
| [1080p software](evidence/t23-1080-software.json) | 94.22 s | 19.10 | 3.58 GiB | 0.56–0.86 / 3–5 |
| [4K VideoToolbox](evidence/t23-4k-hardware.json) | 260.69 s | 6.90 | 3.15 GiB | 0.52–0.90 / 4–6 |

All six sampled frames per export passed. The decoded frame-151 PNGs were visually inspected
at [1080p](evidence/t23-1080-frame-151.png) and [4K](evidence/t23-4k-frame-151.png): the synthetic
labels, masked rain/reflection, occlusion and moving layers remain intact. This geometric
workload compresses well below the target bitrate, particularly with VideoToolbox; the target
is not a constant bitrate or a promise of quality for real art. Measurements include rendering,
assembly, audio and their verification; the later independent quality sampling is outside the
reported export wall time. These two different profiles do not establish an encoder speed comparison.

T37 subsequently passed a full 45-minute native 1080p run with crash/recovery and 184 boundary
comparisons, plus a 60-second native 4K run (305.75 seconds, 5.89 fps, 11.29 GiB sampled RSS).
See [long-form evidence and limits](36-longform.md). MP4s and generated project media are never committed.
