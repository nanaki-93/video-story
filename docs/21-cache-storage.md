# Verified caches and storage planning

The project owns disposable caches under `.cache/tabi-v1/normalized_image/KEY/` and
`.cache/tabi-v1/video_chunk/KEY/`. Each entry contains a fixed payload name and a strict,
content-addressed descriptor. This V1 project-local layout keeps rendering, recovery and
pruning on the same volume. The early developer setting `cache_root` is reserved; it does
not redirect project media or authorize deleting an arbitrary folder.

Normalized PNG keys bind the original file hash, probe, alpha/color interpretation, crop,
render purpose, normalization code and Pillow/codec versions. Cache reads check bytes and
decode the expected image format/dimensions. Draft color warnings survive reuse. A production
render cannot reuse normalization performed under draft assumptions. Original inputs and
frozen registry locks are validated even when every requested pixel is cached.

Video keys bind the relevant scenes, scheduled actions, curves, visual asset locks, global
frame interval, purpose/badge, compiler, pipeline/backend, toolchain and video profile.
Soundtrack placements, music asset locks, output names and audio gain are excluded. Changing
only the soundtrack therefore reuses verified frames but mixes and encodes the new continuous
soundtrack. Keys conservatively include all visual dependencies of active scenes; editing a
curve may invalidate more chunks than the minimum necessary.

Cache storage owns independent video bytes. Reuse copies those bytes into a new job artifact
and independently verifies stream properties, every presentation timestamp and full decode.
Reports identify the current snapshot and the originating snapshot/cache key. Editing an old
job artifact cannot corrupt the cache through a hard link. A missing, corrupt or incompatible
entry is rerendered. Normalized PNG scratch links are read-only renderer inputs; pruning their
cache names cannot erase the linked working copy.

## Inspect and prune

```sh
tabi cache inspect --project ROOT
tabi cache prune --project ROOT --all
# After inspecting the returned inventory:
tabi cache prune --project ROOT --key KEY --inventory INVENTORY_SHA --apply
# Or remove all entries not referenced as authored sources:
tabi cache prune --project ROOT --all --inventory INVENTORY_SHA --apply
make clean-cache PROJECT="ROOT"
```

Inspection and the default prune command do not delete anything. Applying a selection requires
the observed inventory hash. The core rereads it while holding the worker lease, project writer
lock and cache lock; stale inventories and active workers fail before removal. It removes only
the fixed payload and entry metadata for the selected keys. Unknown files, malformed entries,
symlinks, source artwork, registry documents, snapshots, job artifacts and exports are preserved.
Any cache payload explicitly referenced by source/rights metadata becomes protected. Removed
byte counts describe logical payload sizes, not guaranteed physical space freed from linked files.

Pruning does not scan arbitrary `.tabi-*` directories or delete interrupted job scratch data.
Those files have no persisted ownership manifest proving that a live process has released them.
Retain them for recovery/manual inspection with the worker stopped; they are never adopted as
verified chunks or promoted automatically.

## Disk estimates

```sh
tabi jobs estimate JOB_ID --project ROOT
```

The typed estimate reports additional normalization, video, audio and reserve bytes against
the project's available disk space. A worker runs the same check before starting media work.
It accounts for independent chunk/cache copies, assembly/fallback/mux, source audio copies,
resampled PCM and continuous audio buffers. Verified cached images avoid another persistent
normalization copy. Video size uses the configured bitrate or a conservative pixel-rate estimate
with 50% headroom; a reserve adds at least 256 MiB or 10%. Compression and other processes make
this an estimate, not a space guarantee. Insufficient space fails the job with a useful diagnostic;
existing sources, verified artifacts and final exports remain available. Resume after freeing space.

## Verification

Eight new unit cases cover normalized image reuse/repair, audio versus visual key changes,
version/profile changes, explicit pruning, stale inventories, worker contention, protection of
authored sources, symlinks, cross-volume copy failure and low-space preflight. The actual-media
case changes audio gain and measures the resulting AAC samples while proving zero new video
graphs; then it corrupts one cache payload and verifies exactly one rerender. A motion edit
invalidates both video chunks. T21's cancellation test now restores a damaged owned chunk from
the independent valid cache and retains its verified neighbour.

[Retained evidence](evidence/t22-cache.json) records a 300-frame synthetic story with 4 video
graphs initially, 0 after changing audio gain, and 1 after corrupting one cached video chunk.
Each run encoded AAC exactly once. Pruning removed 29 entries while all 54 checked source,
snapshot and export files retained their hashes. `make check` passes 31 schemas and 222 unit
checks; the full media suite passes all 39 cases, with the expanded content-change case rerun.
All generated clips are visibly synthetic and remain ignored local files. This is technical
cache verification, not art, soundtrack or publication approval.
