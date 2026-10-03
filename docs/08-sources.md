# Official references and verification status

Technical and policy references retrieved 3 October 2026. Implementation specifications elsewhere are proposed design choices, unless explicitly attributed below. Recheck time-sensitive requirements at implementation and publication.

| Source | Supports | Status |
| --- | --- | --- |
| [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) | Overlay, masks, crop, scrolling, audio fades/mixing and related filters | Retrieved; exact installed build still needs capability tests |
| [ComfyUI server routes](https://docs.comfy.org/development/comfyui-server/comms_routes) | `/prompt`, `/ws`, history and queue routes for optional local workflow integration | Retrieved; adapter must follow installed version |
| [Compose native distribution](https://kotlinlang.org/docs/multiplatform/compose-native-distribution.html) | Original native-client alternative | Historical reference; Kotlin/Compose packaging is deferred by the local web app decision |
| [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/) | Serving the built UI from the local Python service | Checked 3 October 2026; application integration remains T25/T26 |
| [Starlette file responses](https://starlette.dev/responses/#fileresponse) | Streaming local files and HTTP byte-range responses for proxy seeking | Checked 3 October 2026; authenticated artifact/root checks still need implementation |
| [File System API](https://developer.mozilla.org/en-US/docs/Web/API/File_System_API) | Browser filesystem access interfaces and compatibility considerations | Checked 3 October 2026; V1 uses the local Python filesystem service, not browser-specific access as a prerequisite |
| [YouTube monetization policies](https://support.google.com/youtube/answer/1311392?hl=en) | Original/authentic content and inauthentic/repetitive content review | Retrieved; no guaranteed outcome |
| [YouTube AI disclosure](https://support.google.com/youtube/answer/14328491?hl=en) | Review of altered/generated content including AI music | Retrieved; apply to actual production facts |
| [YouTube upload encoding](https://support.google.com/youtube/answer/1722171?hl=en) | Delivery settings to consult for export profiles | Retrieved; settings remain configurable |
| [DistroKid help](https://support.distrokid.com/) | Manual place to verify distribution/Content ID rules | Specific relevant articles were inaccessible; details unresolved |

No model performance, render speed, distributor pricing, Content ID allowlisting guarantee or legal eligibility is established by this plan. The API/service names, UI tokens, memory budget, frame semantics and repository structure are project specifications to implement and validate.
