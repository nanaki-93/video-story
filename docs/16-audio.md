# Music masters, waveforms and sample timing

Import a finished integer PCM WAV through the [asset importer](11-asset-registry.md), using `kind: audio` and explicit copy/link mode. Copy import preserves the original bytes, and both modes record exact source hashes and sample counts. Music generation and distribution masters remain outside the episode mixer.

T15 adds shared audio analysis:

```sh
.venv/bin/tabi audio inspect PROJECT/episodes/EPISODE.json --project PROJECT
.venv/bin/tabi audio waveform ASSET_ID VERSION --project PROJECT --bins 512 --output NEW_WAVEFORM.json
.venv/bin/tabi audio release-import MUSIC_RELEASE.json --project PROJECT
```

Each command emits JSON and accepts explicitly registered external roots through repeated `--root ID=PATH`. `--output NEW_JSON` writes an additional verified, atomic copy and never overwrites an existing output. A waveform is disposable analysis data, identified by asset/content and source-file hashes; it is never a replacement master or an approval. Waveform bins store half-open source-sample ranges and per-channel minimum, maximum and RMS values. Exact leading/trailing digital silence and an entirely silent master are reported. Reads use bounded 65,536-sample blocks, independent of source duration.

`audio inspect` orders placements by start sample then ID, validates source duration/channel count and optional release membership, warns about music gaps/overlaps and completely silent masters, and reports necessary sample-rate conversion. Intentional gaps are permitted. Ambience does not conceal missing music coverage. Ordinary `tabi validate` includes these audio warnings after compilation.

## Timeline and fade semantics

The episode audio timeline is always 48,000 samples/second. Trim positions refer to the **prepared 48 kHz source**, including for a differently sampled original master. Its intended prepared length is `round(original_samples * 48000 / original_rate)`, computed rationally with ties-to-even. Resampling writes a separate derivative in T16. This convention avoids mixing original-rate positions with timeline positions. Source waveform bins retain the original rate and are labeled accordingly.

Placements use half-open trims and intervals. Mono playback duplicates the channel into stereo without attenuation; stereo preserves left/right. More than two channels require an explicit external downmix. Gain is explicit, from −120 to +24 dB; no automatic normalization, compression or clipping is applied by the sample reader.

A linear fade of N samples includes both endpoints: fade-in index 0 is silent and index N−1 reaches the authored gain. Fade-out is the reverse. A one-sample fade mutes that endpoint. Fade lengths cannot overlap beyond the trimmed duration. Range reads compute the envelope from the placement's global offset, so changing buffer boundaries never restarts the fade. With no fade, trimmed samples retain their original amplitude except for explicit gain. T16 adds continuous summing, conversion and final encoding.

## Optional release metadata

Use the strict `release_record` schema as the optional `music-release.json` interchange. Supply a new ID, artist, release title and ordered tracks, each referring to an imported asset/version and master location. Track title, credits, actual sample rate/channels/duration and optional known ISRC, UPC, release link, source-project path and factual AI notes are preserved. Unknown identifiers remain null.

Import accepts a new draft only. Each master must exactly match its asset's bytes and measured metadata; a supplied hash must match. The stored record points to the registry's preserved copy/link and records its actual hash. Rights claims conflicting with pending asset rights are rejected. Import does not confer review or publication status. Edits use the shared revision-checked project store; masters stay immutable.

## Verification and limits

`make schemas check` passed 24 schemas, Ruff and **174 tests**, with 19 FFmpeg tests intentionally skipped. Six new audio cases cover 8/16/24/32-bit PCM signedness, independent trim/fade/gain values, all 25 split points of a small reference, one-sample fades, waveform min/max/RMS, zero-sample silence, gaps/overlaps, invalid trims, rational rate conversion counts, exact copy import and invalid metadata/hash rejection. A 24-bit/44.1 kHz master with a Japanese/apostrophe filename remained byte-identical through import, metadata handling and waveform generation.

Installed CLI evidence: [480,000-sample timeline](evidence/t15-audio-timeline.json) and [64-bin synthetic waveform](evidence/t15-tone-waveform.json). The fixture master hash is `f0acb6b6957870747bc7a78694f4aa117d8796c587ec1950b59098cde15d4f0a`; it remains unchanged. NumPy 2.4.6 is locked for bounded vector operations; its [buffer interpretation](https://numpy.org/doc/stable/reference/generated/numpy.frombuffer.html) documents explicit byte order. Tests ran on the previously recorded M5 Pro/Python 3.11.16.

Current import supports integer PCM WAV; compressed, floating-point WAV and multichannel masters require external preparation. This step does not yet publish a continuous mix or encode AAC. No real finished music or listening approval has been supplied. The synthetic triangle/silence sources are test signals only, never a music release.
