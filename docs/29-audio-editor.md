# Audio editing and auditions

Import WAV masters in Assets using the existing bounded upload/copy workflow. In Audio, choose an episode and add imported music or ambience. Trims and positions are integer samples in the prepared 48 kHz stream; original masters retain their own sample rate and exact bytes. Source waveforms display the original sample rate and measured silence.

Edit placements, gain, fades and optional ambience loops. Music does not loop. Move earlier/later requests consecutive music placement in Python; ambience retains its explicit start. Review timing changes shows the proposed intervals and effective end before Apply. Conflicting story duration, trim bounds, linked beats or stale revisions prevent a write. No visual scene/action is silently moved. Undo/redo creates new guarded revisions. Apply fields before navigation; closing with pending edits warns through the browser.

Render audio audition creates a separate verified float32 stereo WAV for a selected range up to 120 seconds. It runs the same mixer as final exports and shows measured LUFS, true peak, sample peak and counts over full scale. Suggested gain is informational. Playback needs an explicit Play gesture; edits mark an existing audition stale. A long episode's complete soundtrack is mixed once by its final render job.

Music release forms build factual track metadata from actual master paths, hashes, rate and sample count. Enter titles, artist, credits, explicit flag and known identifiers. Unknown ISRC/UPC remain null. Ordered track JSON supports additional tracks and optional source/AI notes. Only draft metadata can be edited here; reviewed records require a new draft identity. Synthetic/pending asset rights cannot be promoted by a contradictory release declaration.

Verification: `make check` 248 passed; `uv run pytest --run-media tests/unit/test_audio_editor.py tests/integration/test_web_audio.py` two passed; frontend checks/build and four tests. Two real mixes retain 480,000 samples, differ by the requested 6 dB in their steady portion within 1e-7, and preserve source WAV hashes. Fade sample zero is zero. Metadata rejects unsupported rights and keeps unknown IDs null.

Chrome 154 on the M5 Pro rejected an overlong draft, applied -6 dB and 48,000-sample fades, undid/redid to saved revision 4, drew the waveform and played the entire 10-second audition. Observed result: peak -24.6224 dBFS, true peak -24.62 dBTP, -27.58 LUFS, no samples over full scale. The untouched source hash is `f0acb6b6957870747bc7a78694f4aa117d8796c587ec1950b59098cde15d4f0a`. [Editor](evidence/t30-audio-editor.jpg), [conflict](evidence/t30-duration-conflict.jpg). Outputs remain in `.local/t25-browser/audio/previews/`.

All evidence uses synthetic tones. Original finished masters and Marco's listening review are still required for production approval.
