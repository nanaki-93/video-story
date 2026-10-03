# Renderer preview and exact frame inspection

Choose an episode on Preview, enter the first global frame and exclusive end, then Generate proxy. Python validates and freezes the draft, queues a 960×540 H.264/AAC job and verifies the output before making it playable. Closing a tab leaves it running; refresh reopens the saved selection rather than submitting again. Replacement requests preserve the earlier verified video.

The player reports approximate proxy seconds. Global frame, previous/next and the scrubber request a Python-rendered PNG after 250 ms without further input. The image reports its exact frame and SHA-256; browser timing is never used as proof of frame accuracy. Story and Preview share the selected frame. Seek proxy is only a convenience for approximate playback, including ranges starting after frame zero.

Edits, missing/changed assets or renderer code changes flag the snapshot stale. Refresh/navigation/focus rechecks its compiled inputs. Old videos remain reviewable. Mark selected frame saves a note bound to the snapshot, and notes survive regeneration with earlier-snapshot labels. Notes are not approval.

Stills run in a bounded separate lane. Aborting a superseded request signals only its execution scope; it cannot cancel an export. Responses from older selections are ignored. Sources and snapshots are never removed. Verified stills and their reports remain under `previews/frames/`; source-backed video caching remains in the shared render service.

Verification: `make check` (247 passed), `uv run pytest --run-media tests/unit/test_preview.py tests/integration/test_web_preview.py`, frontend checks/build/tests. The HTTP media check independently verifies 60 frames / 96,000 samples, repeatable frame PNG hashes, byte ranges, immutable WAVs, previous-video retention and expired-media authentication.

On the M5 Pro, Chrome 154 and Safari 27.0.1 played the newly generated 300-frame synthetic story, sought near frame 150 and measured audio RMS around 0.067. Both displayed exact frame-150 PNG `85009c160219ba291d07c775a9e1b2cbea8ae4c2a4c2f109acca9093c8e5a086`. Refresh retained notes/cursor; an edit marked the old snapshot stale; stopping the worker displayed an unavailable message. A native range initially clamped values above 100 until its maximum was assigned; the corrected Story cursor preserved frame 150. Screenshots: [Chrome](evidence/t29-chrome-preview.jpg), [Safari](evidence/t29-safari-frame.jpg), [stale](evidence/t29-stale.jpg).

Local evidence is `.local/t25-browser`; MP4s stay outside Git. Only synthetic art/audio were used. No production approval or listening judgement is implied.
