# Official references and verification status

Historical reference list retrieved 3 October 2026; links were not re-fetched during the 4 October documentation cleanup. Current implementation results are in [V1 acceptance](38-v1-acceptance.md). Recheck external requirements when doing work that depends on them, especially publication.

| Source | Supports | Status |
| --- | --- | --- |
| [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) | Overlay, masks, crop, scrolling, audio fades/mixing and related filters | Actual rendering, effects and mixing verified by the V1 media gates; see acceptance |
| [FFprobe](https://ffmpeg.org/ffprobe.html) | Stream metadata and decoded frame/timestamp counts | Used in T02's actual media checks |
| [Homebrew FFmpeg](https://formulae.brew.sh/formula/ffmpeg) | External macOS installation | 9.0.2 installed and tested on this M5 Pro; no binaries bundled |
| [ComfyUI server routes](https://docs.comfy.org/development/comfyui-server/comms_routes) | `/prompt`, `/ws`, history and queue routes for optional local workflow integration | Retrieved; adapter must follow installed version |
| [Compose native distribution](https://kotlinlang.org/docs/multiplatform/compose-native-distribution.html) | Original native-client alternative | Historical reference; Kotlin/Compose packaging is deferred by the local web app decision |
| [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/) | Serving the built UI from the local Python service | Local service and bundled frontend implemented and verified in T26/T33 |
| [Starlette file responses](https://starlette.dev/responses/#fileresponse) | Streaming local files and HTTP byte-range responses for proxy seeking | Authenticated artifact/root/range behavior implemented and verified in T26 and subsequent browser gates |
| [File System API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_API) | Browser filesystem access interfaces and compatibility considerations | Checked 3 October 2026; V1 uses the local Python filesystem service, not browser-specific access as a prerequisite |
| [YouTube monetization policies](https://support.google.com/youtube/answer/1311392?hl=en) | Original/authentic content and inauthentic/repetitive content review | Retrieved; no guaranteed outcome |
| [YouTube AI disclosure](https://support.google.com/youtube/answer/14328491?hl=en) | Review of altered/generated content including AI music | Retrieved; apply to actual production facts |
| [YouTube upload encoding](https://support.google.com/youtube/answer/1722171?hl=en) | Delivery settings to consult for export profiles | Retrieved; settings remain configurable |
| [DistroKid help](https://support.distrokid.com/) | Manual place to verify distribution/Content ID rules | Specific relevant articles were inaccessible; details unresolved |

External documentation does not establish distributor pricing, Content ID guarantees or legal eligibility for a release. Project-specific render measurements and their limits live in the [long-form report](36-longform.md); no actual generation-model performance is claimed.
