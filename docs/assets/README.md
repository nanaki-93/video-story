# Existing Tabi asset library

These are the source references for video-story's planned **Generate from references** workflow.
Preserve the originals. The app will register local folders once, then let you select existing
images for identity, pose, outfit, cabin/layout, style and Tokyo scenery. A reference is not
necessarily an approved or animation-ready asset.

| Location | Available starting material |
| --- | --- |
| This folder | Character profile, banners, icons and signature references |
| `scenario/tabi-train-example.png` | The seated Tabi/train composition used by the successful silent pilot |
| `scenario/tokyo-scenario/` | Six distinct Tokyo panoramas |
| `tabi-assets/outfits/` | 50 outfit/style/scene references |
| `tabi-assets/emotions/` | Eight expression references |
| `tabi-assets/train-actions/` | 12 action stills, six walking poses, 97 breathing and 129 drinking PNG frames |
| `clip-tests/` | Preserved supplied clips and local comparison videos; reference material, not the new generation workflow |

Bulk variants and MP4s are intentionally ignored by Git. They remain at their existing local
paths; a fresh clone will not contain them. Keep a separate backup. The app's future catalog
must scan registered folders, not rely on `git ls-files`. [Local source manifest](../local-source-manifest.json)
records the earlier index-only migration; [original audit](../asset-inventory.json) and
[source findings](../09-implementation-review.md) record source properties and preparation limits.

Generated candidates and prepared packs belong in local project storage as new versions.
Never overwrite these originals or restore bulk media to Git. PNG sequences still need reviewed
fps/anchors/loop bounds and face ownership; outfit references need compatible seated cutouts and
matched motion. [Final plan](../../PLAN.md) and [generation contract](../39-reference-assets.md)
describe the remaining work. Source selection, technical checks and commercial rights are separate.

R01 removes obsolete trial code, plans and local experiment folders outside this library.
Every existing source media file here and the successful L05 pilot is protected by a hash manifest.
All 327 source media files retain their hashes; [cleanup evidence](../evidence/r01-repository-cleanup.json).
