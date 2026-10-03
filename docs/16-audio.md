# Music masters, waveforms and sample timing

Import a finished mono/stereo PCM WAV through the [asset importer](11-asset-registry.md), using `kind: audio` and explicit copy/link mode. Integer 8/16/24/32-bit and IEEE float 32/64-bit WAV, including standard extensible headers and RF64, are supported. Copy import preserves the original bytes, and both modes record exact source hashes and sample counts. Music generation and distribution masters remain outside the episode mixer.

T15 adds shared audio analysis:

```sh
.venv/bin/tabi audio inspect PROJECT/episodes/EPISODE.json --project PROJECT
.venv/bin/tabi audio waveform ASSET_ID VERSION --project PROJECT --bins 512 --output NEW_WAVEFORM.json
.venv/bin/tabi audio release-import MUSIC_RELEASE.json --project PROJECT
```

Each command emits JSON and accepts explicitly registered external roots through repeated `--root ID=PATH`. `--output NEW_JSON` writes an additional verified, atomic copy and never overwrites an existing output. A waveform is disposable analysis data, identified by asset/content and source-file hashes; it is never a replacement master or an approval. Waveform bins store half-open source-sample ranges and per-channel minimum, maximum and RMS values in full-scale units; float masters may exceed ±1. Exact leading/trailing digital silence and an entirely silent master are reported. Reads use bounded 65,536-sample blocks, independent of source duration.

`audio inspect` orders placements by start sample then ID, validates source duration/channel count and optional release membership, warns about music gaps/overlaps and completely silent masters, and reports necessary sample-rate conversion. Intentional gaps are permitted. Ambience does not conceal missing music coverage. Ordinary `tabi validate` includes these audio warnings after compilation.

## Timeline and fade semantics

The episode audio timeline is always 48,000 samples/second. Trim positions refer to the **prepared 48 kHz source**, including for a differently sampled original master. Its intended prepared length is `round(original_samples * 48000 / original_rate)`, computed rationally with ties-to-even. Resampling writes a separate float64 derivative and trims/pads only to this exact technical length; it never overwrites the original. This convention avoids mixing original-rate positions with timeline positions. Source waveform bins retain the original rate and are labeled accordingly.

Placements use half-open trims and intervals. Mono playback duplicates the channel into stereo without attenuation; stereo preserves left/right. More than two channels require an explicit external downmix. Gain is explicit, from −120 to +24 dB; no automatic normalization, compression or clipping is applied by the sample reader.

A linear fade of N samples includes both endpoints: fade-in index 0 is silent and index N−1 reaches the authored gain. Fade-out is the reverse. A one-sample fade mutes that endpoint. Fade lengths cannot overlap beyond the placement duration. Range reads compute the envelope from the placement's global offset, so changing buffer boundaries never restarts the fade. With no fade, trimmed samples retain their original amplitude except for explicit gain.

## Continuous mix and preview audio (T16)

Compile an episode, then render its saved snapshot to a **new** WAV path:

```sh
.venv/bin/tabi --config examples/settings.macos.toml audio mix SNAPSHOT_SHA --project PROJECT --output NEW_MIX.wav
.venv/bin/tabi --config examples/settings.macos.toml preview SNAPSHOT_SHA --project PROJECT --start 0 --end 300 --output NEW_PREVIEW.mp4
```

The mixer copies and verifies locked sources into owned scratch storage, prepares 48 kHz sources, sums ordered placements in float64 blocks and writes one stereo float32 PCM WAV. The decoded WAV must match every generated PCM byte and the exact sample count before atomic publication. WAV/RF64 packaging is selected by FFmpeg. Scratch work is disposable; source artwork/music is never a cleanup target. Range mixing accepts `--start-sample` and `--end-sample`; its global trim/fade/loop phase equals the same range of the full mix.

Ambience placements may explicitly set `loop_duration_samples` and `loop_crossfade_samples`. Only ambience can loop; music is never stretched automatically. The period is the trimmed source length minus overlap. Each later tail overlaps the next head with a linear crossfade that includes both endpoints. The first pass starts normally. The crossfade is zero for an authored hard seam, or 2 to half the trimmed source length. A hard seam produces a listening warning. Fade/gain automation belongs to the whole placement and never restarts per loop. Inactive loop options are omitted canonically to preserve older snapshot identities.

The report records source/master identities, resampling counts, output hash, backend/toolchain identity, sample peak, integrated LUFS, true peak, loudness range, over-full-scale samples and a proposed gain. [FFmpeg loudnorm](https://ffmpeg.org/ffmpeg-filters.html#loudnorm) supplies input measurements on a discarded analysis output. The optional suggestion targets −14 LUFS while respecting −1 dBTP; these are review targets, not platform requirements. Nothing applies that suggestion automatically. Silence/very short material may have no measurable integrated loudness.

`audio mix --gain-db VALUE` explicitly changes the exported mix gain. `preview --audio-gain-db VALUE` applies an explicit final soundtrack adjustment and records it. Individual track gains remain authored in the snapshot. Float mixes preserve samples above full scale and report them; AAC preview export refuses such a mix until gain is adjusted. There is no hidden limiter, compressor, music replacement or source-master rewrite.

Preview renders video first, then copies that video while encoding the continuous soundtrack to AAC exactly once. Verification checks the exact container sample duration, start time, stereo/48 kHz format and full decode. AAC may decode up to 1,023 padding samples past the declared container end; that padding is reported separately. No repeated per-video-chunk AAC encodes occur. Chunked final assembly is T21.

## Optional release metadata

Use the strict `release_record` schema as the optional `music-release.json` interchange. Supply a new ID, artist, release title and ordered tracks, each referring to an imported asset/version and master location. Track title, credits, actual sample rate/channels/duration and optional known ISRC, UPC, release link, source-project path and factual AI notes are preserved. Unknown identifiers remain null.

Import accepts a new draft only. Each master must exactly match its asset's bytes and measured metadata; a supplied hash must match. The stored record points to the registry's preserved copy/link and records its actual hash. Rights claims conflicting with pending asset rights are rejected. Import does not confer review or publication status. Edits use the shared revision-checked project store; masters stay immutable.

## Verification and limits

`make schemas check` passed 24 schemas, Ruff and **174 tests**, with 19 FFmpeg tests intentionally skipped. Six new audio cases cover 8/16/24/32-bit PCM signedness, independent trim/fade/gain values, all 25 split points of a small reference, one-sample fades, waveform min/max/RMS, zero-sample silence, gaps/overlaps, invalid trims, rational rate conversion counts, exact copy import and invalid metadata/hash rejection. A 24-bit/44.1 kHz master with a Japanese/apostrophe filename remained byte-identical through import, metadata handling and waveform generation.

Installed CLI evidence: [480,000-sample timeline](evidence/t15-audio-timeline.json) and [64-bin synthetic waveform](evidence/t15-tone-waveform.json). The fixture master hash is `f0acb6b6957870747bc7a78694f4aa117d8796c587ec1950b59098cde15d4f0a`; it remains unchanged. NumPy 2.4.6 is locked for bounded vector operations; its [buffer interpretation](https://numpy.org/doc/stable/reference/generated/numpy.frombuffer.html) documents explicit byte order. Tests ran on the previously recorded M5 Pro/Python 3.11.16.

T16 verification: `make schemas check` passed **25 schemas and 177 tests**, with 24 opt-in media checks skipped. `make test-media` passed **all 24 actual-media tests**. Five new media cases prove byte-exact decoded PCM, global range parity across block boundaries, 44.1→48 kHz RF64/float conversion with preserved master hash and 997 Hz tone frequency, ambience seam bounds, overload reporting/explicit gain, silence and failure cleanup. The preview test observes exactly one AAC encode and compares decoded samples with the global PCM reference (correlation above 0.995; RMS error below 0.003 away from codec edge transients). Unit checks cover every small-loop split and truncated/extensible WAV headers.

The installed CLI produced [compilation](evidence/t16-compilation.json), [mix](evidence/t16-mix-report.json) and [preview](evidence/t16-preview-report.json) reports. Local outputs are `.local/t16-audio/synthetic-mix.wav` and `.local/t16-audio/synthetic-audio-preview.mp4`: ten seconds, 300 frames at 960×540/30, with exactly 480,000 decoded stereo AAC samples. The unchanged test master measured −21.05 LUFS and −18.62 dBTP; authored gain remained 0 dB. The measured render/mix/mux subprocess interval was 2.862 seconds during concurrent test execution, not a production benchmark.

Compressed or multichannel masters and unusual valid-bit/channel-mask layouts require explicit external preparation. Nonfinite float samples are rejected. PCM work uses bounded memory but owned scratch copies and verification files consume disk; storage estimation is T22. Long-form throughput and real-scene quality remain unmeasured. No real finished music or Marco listening approval has been supplied. The synthetic triangle/silence sources are test signals only, never a music release.
