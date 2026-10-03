# Distribution contents and third-party notices

The local wheel contains Tabi Python source, generated browser code and the built static UI.
It does not contain Python, Node, Java, FFmpeg/ffprobe, models, media clips, commercial fonts,
private projects, credentials or signed application binaries. This repository does not assign a
new licence to the user's artwork or project; public redistribution needs an explicit owner decision.

The built browser client includes compiled schema validators and runtime helpers from Ajv
8.20.0 and ajv-formats 3.0.1 (MIT). Their dependency notices are also included conservatively:
fast-uri 3.1.8 (BSD-3-Clause), fast-deep-equal 3.1.3, json-schema-traverse 1.0.0 and
require-from-string 2.0.2 (MIT). `make package` copies the exact installed packages' licence texts
to `tabi/web/assets/THIRD-PARTY-NOTICES.txt`; they remain alongside the JS in the wheel/sdist.
No commercial fonts are bundled; the UI uses system fonts.

Python dependencies are installed separately from the locked runtime requirements. Their wheel
metadata and licence files remain with their distributions. The app wheel does not vendor those
packages. Build-only Node tools (Vite, TypeScript, Prettier and schema type generation) are not
shipped as runtime executables. Node is required to build a new frontend, never to run the installed app.

FFmpeg is an external user installation. Codec/FFmpeg build licences are not relicensed by this
package. No media binary is copied into source control or the distribution. Optional models and
generation servers are not installed by packaging. DMG creation, signing, notarization and automatic
updates are outside this local wheel distribution.
