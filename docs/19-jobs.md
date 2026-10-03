# Durable jobs and cancellation

The shared Python `JobService` queues frozen snapshots, runs one owned worker per project, records verified progress and exposes cancellation/recovery to both CLI and the future API. A queued job fixes its global range, profile, renderer fingerprint and source snapshot. It never follows edits to the draft episode.

```sh
tabi jobs submit SNAPSHOT_SHA --project ROOT --output exports/story-preview.mp4 \
  --start 0 --end 300 --width 640 --height 360
tabi jobs list --project ROOT
tabi jobs work --project ROOT --once
tabi jobs status JOB_ID --project ROOT
tabi jobs events JOB_ID --project ROOT
tabi jobs cancel JOB_ID --project ROOT
tabi jobs recover --project ROOT
```

Commands return structured JSON. Submission queues work; `work` drains the queue in submission order, or executes at most one job with `--once`. The CLI worker stays in the foreground. The later local service owns its background lifecycle. `work` returns 4 for failed/interrupted results, 5 for cancellation and 130 for an operator interrupt. Status/recovery reads do not imply a job succeeded.

## Persistence and ownership

Each event is an immutable, atomically published JSON file under `jobs/.journals/JOB_ID/`, linked to its predecessor's content hash. The event is the commit point. `jobs/JOB_ID.json` is an atomic current-state checkpoint and can be rebuilt after a crash between event and checkpoint publication. The shared short project lock serializes cancellation and state changes. Metadata symlinks, malformed identities, missing events and altered history fail explicitly. No database is used.

The distinct `.tabi-worker.lock` lease prevents a second worker or recovery operation from interfering with live work. A recovered running job becomes `interrupted`; already verified chunks and reports remain on disk. Recovery never adopts or signals a stored PID. An OS-killed worker may leave temporary files or its already launched encoder to finish; those are not promoted to verified output. T22 provides explicit safe cleanup of owned intermediates.

Cancellation of queued work is immediate. Cancellation of running work sets a durable request, checked during media preparation, audio blocks and subprocess waits. The calling execution scope retains the exact `Popen` child, sends termination only to that child, waits and escalates to kill if necessary. It never matches process names or sends process-group signals. Other execution scopes and projects are unaffected. A completed job stays verified if a cancellation arrives after its final publication transaction.

The media backend renders into an owned temporary directory, decodes and verifies the result, then publishes a chunk without replacing an existing file. Its report and hash are committed before verified progress advances. Final export publication and completion are serialized against cancellation. An interruption between export publication and its event can leave a valid unclaimed export; it is never overwritten. Original art/audio and previously verified exports remain untouched.

Progress means **verified frames**, not an estimated encoding percentage. The T20 checkpoint ran one bounded chunk (up to 7,200 frames) and supported new output paths only under the project's `exports/`. The current [T21 workflow](20-chunk-assembly.md) adds planning, resume, video-only chunks and continuous final audio assembly. Legacy unplanned T20 jobs remain historical artifacts and require a new submission; their old journals are preserved.

## Target-Mac evidence

`make check` passes 27 schemas, Ruff and 201 unit checks. Eight new unit checks exercise queue ordering, event/checkpoint failure, journal tampering, process leases, cancellation isolation, path safety, actual worker exit and changed input rejection. Three actual-media tests exercise the CLI global-range render, an OS-exited worker after chunk verification, and cancellation during a real FFmpeg graph with an unrelated live process.

[Job/event evidence](evidence/t20-jobs.json) captures four runs under `.local/t20-jobs/Marco 東京 project`: a verified 300-frame story, an injected encoder termination with a useful failure record, a cancelled render, and a worker exited before final publication with 46 verified frames retained after recovery. The original WAV hash is unchanged. [Preview report](evidence/t20-preview-report.json) verifies 300 frames and 480,000 AAC samples; measured render/mix/mux time was 4.871 seconds during concurrent checks. MP4s and job artifacts remain ignored local data.

Machine: M5 Pro / 48 GiB, macOS 27.0.1 arm64; Python 3.11.16; FFmpeg/ffprobe 9.0.2. Packaged worker lifecycle and browser reconnect tests belong to T26/T33. Real-art and music approvals remain pending independently of job reliability.
