# Official sources and qualification status

## Proposed local reference generator — reviewed 8 October 2026

This is an initial documentation/terms review for planning, **not adoption or a completed
commercial-use clearance**. No model or new dependency was installed. L16 must pin exact source
commits, model revisions/checksums and all components before actual use.

| Component / official source | Observed support and terms | Remaining qualification |
| --- | --- | --- |
| [FLUX.2 klein 4B model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B) | Image generation/editing and multi-reference support; 4B weights published under Apache-2.0 with commercial use described | Pin model revision/weights; retain applicable licence/NOTICE material; inspect all accompanying encoder/VAE/tokenizer components and regional terms |
| [FLUX.2 project](https://github.com/black-forest-labs/flux2) | Official model implementation and model-family licensing | The 9B non-commercial variant is excluded from this production route; a code licence alone does not clear other model weights |
| [MFLUX FLUX.2 documentation](https://github.com/mflux-community/mflux/blob/main/src/mflux/models/flux2/README.md) | Apple MLX implementation; 4B image-conditioned editing using one or more `image_paths`; quantization supported | Pin release/commit, supported Python/MLX versions, reference limits and preprocessing; verify actual M5 Pro performance |
| [MFLUX MIT licence](https://github.com/mflux-community/mflux/blob/main/LICENSE) | MIT code licence, copyright 2026 Filip Strand | Keep copyright/permission notices when distributing code; review dependencies separately |

The linked model/docs pages are mutable; no exact candidate revision was selected in R01.
Consequently the backend remains **pending**, not approved for production. Dependency review
includes MLX, text encoder, VAE, tokenizer, numerical/image libraries, transitive packages,
weight sources, attribution and any additional hosted-download terms. Resolve unknowns before
use and recheck on version/provider changes and before release.

MFLUX documents an approximately 15 GB 4B model download; the chosen quantization/cache layout
may differ. Show the qualified actual size and require an explicit installation action. No
Mac latency, peak memory, output quality or unlimited-compute claim follows from model-card
hardware claims. Qualify a bounded real Tabi outfit/cabin/panorama set and record human effort.
No new subscriptions, paid plugins/licences or credit top-ups; a failed free route stays a
reported gap. Source artwork rights and YouTube eligibility remain separate from model terms.

## Existing runtime and delivery references

These references were recorded during the 3 October 2026 implementation; they were not re-fetched
in R01 unless listed above. Verify changing external requirements when work depends on them.
Project measurements and installed versions are recorded in the linked technical documents.

| Official source | Use and limits |
| --- | --- |
| [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html), [FFprobe](https://ffmpeg.org/ffprobe.html) | Existing compositing/audio and stream/frame validation; actual gates in [acceptance](38-v1-acceptance.md) |
| [Homebrew FFmpeg](https://formulae.brew.sh/formula/ffmpeg) | External macOS tool installation; no FFmpeg binary bundled |
| [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/), [Starlette responses](https://starlette.dev/responses/#fileresponse) | Local UI serving and authenticated media ranges |
| [File System API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_API) | Browser compatibility reference; local Python service owns file access |
| [YouTube monetization policies](https://support.google.com/youtube/answer/1311392?hl=en) | Original/authentic-content requirements; no promised eligibility |
| [YouTube AI disclosure](https://support.google.com/youtube/answer/14328491?hl=en) | Apply to the actual generated/altered content and music |
| [YouTube upload encoding](https://support.google.com/youtube/answer/1722171?hl=en) | Delivery guidance; export settings remain configurable |

External links do not establish project-specific source rights, distribution pricing or Content
ID guarantees. The [long-form measurements](36-longform.md) cover only their recorded fixtures.
