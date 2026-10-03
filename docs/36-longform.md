# Long-form reliability benchmark

T37 runs a complete 45-minute synthetic stress workload on the M5 Pro. This is a technical
Session-length test, not an authored Tabi episode or approved music. Its native 1920×1080
composition repeats explicit ten-second test schedules for acceleration/stops, three scenery
depths, landmarks, body entry/loop/exit, blink, rain, reflection and lighting. The soundtrack
is a newly generated full-duration triangle signal with 129600000 samples; it does not stretch
or loop an original composition. The fixture retains the scaffold's `story` format label.
That label does not change the renderer or the 81000-frame schedule being tested.

Reproduce from a new output directory with the pinned tools:

```sh
.tools/bin/uv run python scripts/benchmark_longform.py \
  --output-root '.local/t37-session-native1080' \
  --config examples/settings.macos.toml \
  --seconds 2700 --design-scale 3 --encoder h264_videotoolbox
```

The runner freezes a snapshot and profile, uses 887-frame chunks (so action/weather phases do
not consistently align with boundaries), and saves a journal before each operation. It exits
its owned worker after two verified chunks and the following chunk-start event, before another
media subprocess is created. A fresh worker recovers the journal, revalidates retained media
and completes the remaining chunks. T20/T21/T33 also test cancellation inside a running owned
subprocess and crashes around final publication.

At one-second intervals the worker records its own RSS, retained live tool RSS, tool count and
open descriptor count. Samples stream to JSONL; completed Popen handles are removed. Project
logical bytes, allocated blocks and inode counts are recorded when verified progress changes.
The final report checks recovery hashes, exact video/sample duration and decoded pixels on
both sides of every chunk boundary against separately rendered exact stills. The lossy test
tolerance is mean absolute RGB error below 3 and 99th-percentile error below 24; it is not an
artistic quality approval. The final output is fully decoded and its fast-start MP4/timestamps
are validated by the same delivery verifier used by the app.

## Resource improvements

The initial journal implementation replayed every full typed job event on every cancellation
poll. A 90-chunk / 181-event journal measured 87.75 ms per read on this Mac. Incremental replay
measured 0.83 ms, about 106× faster. Every event's inode, size, nanosecond modification time and
change time are still checked. Changed history triggers complete hash-chain replay. Atomic
job checkpoints remain rebuildable convenience copies and are never trusted as authority.
Only eight recent journal tails are retained, each with one typed job and file signatures.
Running-time accounting is incremental and still excludes paused intervals.

Curve expressions now select only branches reachable in a render interval and use balanced
conditions for densely keyed intervals. Global frame offsets and analytic integral prefixes
are retained, so a chunk boundary does not reset travel or phase. Real FFmpeg checks exercise
2400-key curves before/within/after key ranges and compare exact values/integrals; existing
motion, fractional-frame-rate opacity and chunk-assembly checks also pass.

Eleven job checks and thirteen focused actual-media checks passed. `make check` passed 285
checks with 59 opt-in media cases skipped, with 64 generated schemas in sync. The scalability
change is committed as `312f693`. `8a0c857` also avoids replaying an unchanged journal for SSE
heartbeats; ten service checks cover idle streaming and delivery of the next committed event.

## Completed 45-minute result

The full run passed on Apple M5 Pro / 48 GiB, macOS 27.0.1, Python 3.11.16 and FFmpeg 9.0.2.
The [report](evidence/t37-longform-report.json), [all boundary comparisons](evidence/t37-boundary-checks.json)
and [resource observations](evidence/t37-resource-summary.json) retain the actual results.

| Measurement | Observed result |
| --- | --- |
| Native design and output | 1920×1080, 30/1 fps, H.264 VideoToolbox, BT.709 limited range |
| Complete output | 81000 frames, 2700.000 seconds, 422776362 bytes |
| Continuous audio | 48 kHz stereo AAC; intended and decoded samples both 129600000; zero padding |
| Render, assembly, delivery verification and crash/recovery | 4022.756 seconds (67 minutes 3 seconds); 20.135 frames/second overall |
| Chunk count | 92, including a shorter final chunk |
| Crash recovery | First 1774 frames / two verified chunks retained unchanged |
| Boundary comparisons | 184/184 pass; maximum mean RGB error 1.432, maximum p99 error 9 |
| Worker + live media tools RSS peak | 3273080832 bytes (3.05 GiB) |
| Worker median RSS across steady thirds | 151.22 / 157.89 / 158.30 MiB |
| Retained live tools / worker descriptors | Maximum one tool / ten descriptors |
| Resource samples | 3916, with no sampling errors |

The reported elapsed time comes from the durable first `started` and final `verified` UTC
journal events, including the injected crash and recovery. It excludes parent startup before
the first event, fixture preparation, the independent delivery recheck and boundary review.
Future runs also persist a parent monotonic-clock receipt before post-render review. The
initial flat 184-term frame-selection expression exceeded FFmpeg's parser depth; balancing
that expression selected all 184 frames in an actual 81000-frame, 2×2 FFmpeg check. The saved
verified export was then reviewed successfully without rerendering it. Review-only recovery
requires the unchanged core pipeline:

```sh
.tools/bin/uv run python scripts/benchmark_longform.py \
  --output-root '.local/t37-session-native1080' \
  --config examples/settings.macos.toml --review-existing
```

The final output SHA-256 is
`c422cf5351d85aea3f7fd387fe402a3e2602b0a09578bd6f026f60965389c38c`.
The ignored local video is `.local/t37-session-native1080/exports/session.mp4`.
Representative decoded [first](evidence/t37-first-frame.png),
[middle](evidence/t37-middle-frame.png) and [last](evidence/t37-last-frame.png) frames were viewed.
These demonstrate synthetic geometry, masking and state; they do not approve Tabi artwork.

Project allocated blocks grew from 0.49 GiB before rendering to 1.18 GiB at the final verified
video chunk. A separate observation during final frame counting measured 2.87 GiB while
assembly temporaries existed. After review, the retained tree used 1.60 GiB in allocated
blocks, including boundary PNGs. Hard-linked bytes are counted once. Disk observations occur
at progress changes plus the recorded assembly observation; they are not a continuous peak
measurement. The original free-disk value was not retained and is explicitly null in this
recovered report. The [assembly observation](evidence/t37-assembly-storage.json) preserves its scope.

The web app keeps one export job active across its open projects. Keep that default. CLI
ownership is per project; starting separate CLI workers for different projects adds concurrency
outside that UI limit. This run does not qualify parallel exports. RSS measurements exclude
other apps, kernel and unreported GPU allocations. Complex real artwork and different tools
need their own measurements; do not multiply this synthetic result into a promised production SLA.

## Browser review

`2f863b5` adds an embedded verified-export player to Renders, including an approximate seconds
seek control. Only a selected export receives a media source. Switching exports or leaving the
page pauses and releases it. Settings links select the project and open its render queue.
This avoids the target Chrome session's raw-MP4 page navigation block while retaining the same
authenticated, hash-checked byte-range endpoint.

Actual Chrome playback sought to 2650 seconds and advanced to 2665.71 with no media error;
the final build also sought to 2695 seconds, with duration 2700 and readyState 4. Navigation
removed the video element. See [observations](evidence/t37-browser-seek.json) and
[screenshot](evidence/t37-longform-seek.jpg). Frontend typecheck, four tests and production build
pass. This is a decoding/seeking check, not musical listening approval.

## Native 4K gate

T23 tested 4K output from a 1920×1080 design. A separate native 3840×2160, 60-second effects
workload is running for T37 with `--design-scale 6`. Its measurements and six reference-frame
comparisons will be recorded before completing this task.
