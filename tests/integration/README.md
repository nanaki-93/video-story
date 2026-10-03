# Media integration checks

T02 adds the first real FFmpeg render/decode test. T01/T03 do not establish any
rendering, playback, or target-hardware capability. T03 storage tests use real
temporary files and spawned Python processes under `tests/unit/`; those checks
are not media integration tests.
