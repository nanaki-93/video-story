# Chunk planning, resume and final assembly

T21 extends the durable job service with exact global video ranges, verified chunk reuse, concat/re-encode assembly and one continuous soundtrack. CLI and the forthcoming local API use the same Python implementation.

```sh
tabi jobs submit SNAPSHOT_SHA --project ROOT --output exports/story.mp4 \
  --start 0 --end 18000 --chunk-frames 900 --width 1920 --height 1080
tabi jobs work --project ROOT
tabi jobs resume JOB_ID --project ROOT
tabi jobs work --project ROOT --once
```

The example requires a snapshot at least 18,000 frames long. The generator's synthetic story is only 300 frames; use `--end 300 --chunk-frames 77` for the recorded development case. `resume` validates and requeues; it does not launch a hidden worker.

## Planning and compatibility

The default cap is about 30 seconds, rounded once to an integer frame count. Explicit caps are 1–7,200 frames. Each chunk records a job-relative first frame and exact count; the renderer receives `job.first_frame + chunk.first_frame`. Real scene cuts in the latter half of a full chunk are preferred. A short final remainder is allowed. Splits through overlaps, body/face actions and weather loops retain their original global phases. Supported spatial effects have zero temporal handles; history-dependent effects remain unsupported.

The plan freezes the output-profile hash and core-pipeline fingerprint at submission. The exact local FFmpeg/ffprobe/capability fingerprint is bound at first execution and checked on resume and assembly. Registry/source locks are reverified. A changed profile, pipeline, toolchain, source or range plan requires a new job; old artifacts remain available as historical results. T20 jobs without a plan also require a new submission. No approved snapshot or old journal is migrated in place.

Video chunks contain no audio. Software H.264 uses closed GOPs. Before stream copy, assembly compares codec configuration, frame rate, time base, dimensions, color tags and extradata, and checks that each chunk starts with a keyframe. The concat file references only owned numeric basenames, so spaces, apostrophes and Unicode project names cannot become concat-language commands. Concat timestamps and the full decoded frame schedule are verified. Incompatible configurations or failed stream-copy verification trigger an explicit re-encode fallback with fresh exact timestamps; its reason is retained in the report. Failure of that verification publishes nothing.

After video assembly, the existing sample-accurate mixer prepares one continuous PCM interval. AAC is encoded once in the final mux. Full video decode, frame timestamps, source/chunk hashes and audio sample timing are checked before atomic publication. No independent per-chunk AAC is concatenated.

## Resume and output protection

Resume checks every retained chunk's owned path, hash, report, snapshot/profile compatibility, codec, frame count, timestamps and full decode. Missing, corrupt or incompatible chunks become pending; new attempts use new paths. Valid neighbours keep their existing bytes and paths. Verified assembly can also survive a worker crash and be reused without rerendering video or re-encoding audio.

An export linked just before a worker crash can be adopted only when its exact hash and size match the job's verified assembly. A conflicting existing file is preserved and the job fails with a useful diagnostic. Changing or deleting source artwork is never part of resume or recovery.

## Verification and retained evidence

`make schemas check` passes 27 schemas and 214 unit checks, including thirteen new planner/resume cases. New media checks cover:

- Chunked versus monolithic story and effect ranges at 31 sampled frames around blink, pose, travel, weather and overlap boundaries. Lossy RGB differences stay within a 99.9th-percentile tolerance of 15 levels. Decoded AAC comparison has RMS error below 0.0001 and correlation above 0.9999, with exactly one AAC encode observed in each chunked job.
- Cancellation after two verified chunks, deliberate truncation of the first, and resume that rerenders that chunk while retaining the second's exact hash and modification time.
- 72 frames at `30000/1001` fps with 115,315 intended audio samples, including an injected stream-copy verification rejection followed by a real, verified re-encode.
- Actual worker exits before and after final export publication; safe reuse on restart and preservation of an externally changed conflicting export.

[Resume journal evidence](evidence/t21-resume.json) records the synthetic 300-frame story under `.local/t21-chunks/Marco 東京 project`. It had 154 verified frames when cancelled, 77 after detecting the truncated chunk, and 300 after resume. Three chunks were rendered; the valid neighbour was reused unchanged. The final chunk counts are 77, 77, 77 and 69. [Assembly report](evidence/t21-assembly-report.json) records stream copy and 480,000 AAC samples; [frame 174](evidence/t21-resumed-frame-174.png) was extracted from the resumed MP4 and visually inspected. Resume through final verification and evidence extraction took 6.832 seconds during development checks. MP4 stays local and ignored.

These are M5 Pro / macOS 27.0.1 software-encoder checks with FFmpeg 9.0.2. They do not establish 1080p/4K long-form performance or VideoToolbox concat quality; T23/T37 own those gates. T22 adds cache reuse between distinct jobs, disk estimates and safe pruning. Artistic/music approvals remain pending.
