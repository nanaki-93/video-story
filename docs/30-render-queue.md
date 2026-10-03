# Render queue, local settings and recovery

The Renders page freezes the saved episode revision, then asks Python to prepare a profile,
frame interval, destination beneath the project's `exports/` folder and chunk plan. The storage
estimate does not enqueue anything. Queueing uses that snapshot; later draft edits cannot change
it. Production snapshots require approved inputs and a separate content-hash review. Synthetic
and draft previews remain labeled and cannot acquire production approval.

Progress counts verified frames. While a chunk is running its frames are not yet counted.
The approximate ETA uses completed frames divided by measured running time, excludes paused
intervals, and explicitly excludes the final assembly estimate. The first chunk has no speed
estimate. Diagnostics retain the exact frozen profile, chunk states and failure information.

Pause completes the current video chunk, verifies it and relinquishes the worker lease at the
next boundary. If assembly has already started, it finishes before pausing prior to publication.
Cancel stops this worker's owned process and retains already verified chunks. Resume validates
hashes, toolchain and pipeline, reuses valid chunks, and renders invalid or unfinished chunks
again. A changed renderer requires a new job. Verified outputs can be decoded again from the
queue. The browser can close without cancelling work; restart the launcher and reopen the same
registered project after a worker crash. Recovery never signals an unrelated saved PID.

Settings stores the theme, profile, encoder and managed-cache budget as an atomic revisioned
local document. Tool-path edits back up the exact TOML and use a hash guard against stale writes.
Restart the launcher to apply changed tools; environment overrides still take precedence.
Registered media roots are visible here and set by the launcher. A health check probes actual
local tools. The stop control waits for the current job before exiting.

Cache cleanup first inventories and hashes the managed entries, proposes oldest unprotected
entries until the requested budget is reached, then requires that same inventory when applying.
Source references, snapshots, unknown files and active workers are protected. A zero budget
still does not authorize deletion of protected source media. This is explicit cleanup, not an
unattended eviction service.

CLI parity: `tabi jobs submit ... --dry-run` returns the same conservative storage estimate;
`tabi jobs pause JOB --project PATH`, `resume`, `cancel`, `events`, and `verify` use the same
Python queue. `tabi cache inspect/prune` and `tabi doctor` expose the underlying diagnostics.
