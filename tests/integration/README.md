# Media integration checks

Run `make test-media` (or `pytest --run-media tests/integration`) for actual
FFmpeg rendering, probing and decoding. Ordinary `make check` skips these
explicitly, so missing media tools cannot silently pass the media gate.

T02 checks a ten-second libx264 composite and, on capable Macs, H.264
VideoToolbox with software fallback disabled. Real negative renders break
masking, alpha metadata, entry timing and scrolling speed. Truncation and failed
verification cannot publish a completed artifact. Diagnostics and media live
in pytest temporary directories; use `tabi render-spike --output-dir .local/spikes`
for retained, inspectable artifacts. All inputs are generated and synthetic.

The full episode, browser, audio mixing and resumable job checks remain later
tasks. T03 storage tests use real temporary files and spawned Python processes
under `tests/unit/`; those checks are not media integration tests.
