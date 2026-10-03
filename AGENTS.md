# Agent implementation instructions

This file is intended for the future Tabi Story Studio application repository. The package currently contains planning documents only.

## Read and execute

Read PLAN.md and the linked specifications before implementation. Select the first unblocked task in docs/tasks/INDEX.md. Read its dependencies, implement one coherent behavior, verify it, then update its status with evidence. If an existing repository already contains instructions or code, inspect it before adding or replacing anything; preserve unrelated work.

Use Python for core media orchestration and Kotlin for desktop. Domain/compiler/render logic lives in Python only. CLI and API invoke those same services. The desktop must not recreate timeline semantics or generate FFmpeg commands.

Create the schema layer first. Reject unknown fields and incompatible major versions. Store all times as integer frames and all audio positions as integer samples. Use rational frame rates. Record normalized paths, immutable asset identities, and content hashes.

## Autonomy and boundaries

Complete reversible implementation work and synthetic tests without waiting for optional aesthetic choices. Clearly mark placeholder images/audio as synthetic and not approved for publication. Do not claim the provided character design has been reproduced without comparing to the actual approved reference.

Do not generate a new Tabi design because the reference is unavailable. Do not invent music licences, release identifiers, generation history, or permissions. Do not silently publish, buy assets, upload private music, download unapproved large models, or sign with credentials you have not been given. Manual publishing is outside V1 implementation.

Approved asset versions are immutable; edits create a new version. Draft project files can change atomically. Never erase source artwork when clearing caches. Approval applies to the content hash and is invalidated by edits.

## Engineering rules

Use subprocess argument arrays, never a shell command built from filenames. Separate FFmpeg filter syntax escaping from process argument escaping. Support spaces and Unicode paths. Bind a desktop worker to loopback only; use an ephemeral session token and verify the readiness handshake. Do not connect to or kill an unrelated process found on the same port.

Plan deterministic output at the frame/schedule level. Byte-identical hardware-encoded video is not a requirement. Check job ownership before cancellation. Save outputs to temporary paths and atomically rename only after verification. New schema migrations make backups and never modify approved snapshots in place.

Avoid a database, distributed architecture, or general-purpose creative editor unless a demonstrated requirement demands it. Use small synthetic fixtures rather than checking in large copyrighted assets. No FFmpeg binaries or commercial fonts enter source control without a licence review.

## Review evidence

Each completed task records changed behavior, meaningful verification commands/results, representative screenshots or clip paths where relevant, and target-Mac checks still pending. Unit tests cover substantive time, state and cache behavior. Integration tests render actual media. Art quality requires visual review; tests cannot approve it.

Before merging an implementation milestone, run its acceptance gate, document known limits, and update docs/progress.md. Do not leave TODO buttons, stub jobs, or a mock preview behind a completed task status.
