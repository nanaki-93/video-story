# Example contracts

The top-level JSON documents pass the strict Python models and published JSON Schemas. `make check` validates them and checks schema drift. They remain illustrative drafts with unresolved media/approvals; successful structural validation does not make them renderable or production-approved.

`workflows/` contains service requests rather than versioned documents. The [operations guide](../docs/37-operations.md)
uses them to import the actual supplied train still with rights pending and create a silent draft.
They are consumed by `asset import` and `author` commands, not `document validate`. No animation,
music or approval is fabricated by that walkthrough.

All root documents explicitly declare `schema_version` and `document_type`. Scene/action/track references use stable asset IDs and versions. Draft hashes may remain null; a compiled snapshot requires resolved hashes for its direct references. T05/T13 must resolve media, transitive dependencies and compatibility before rendering.

Pilot length: 3600 frames at 30/1 fps = 120 seconds. Audio length: 5,760,000 samples at 48 kHz. Body action intervals cover the timeline; entry and exit transitions are 45 frames each. Repeat policies, curve limits and scene transition kinds are explicit. Template layer dimensions/periods are illustrative design values, not measurements or approval of supplied artwork.

`asset.synthetic.json` records the actual SHA-256 and size of `tests/fixtures/synthetic/pixel.ppm`, a two-pixel owned fixture for schema checks. It is labeled synthetic and cannot receive production approval. Other references do not imply that corresponding media files exist. No licence, approval or generation history has been fabricated.

Timing, registry data and provenance for real sources must be populated by import and review; `tabi fixtures --output NEW_DIRECTORY` creates the complete synthetic media pack (T04).

`settings.macos.toml` is a separate developer-settings example for T02. It pins
the externally installed FFmpeg/ffprobe 9.0.2 Cellar paths tested on Apple Silicon;
use it with `tabi --config examples/settings.macos.toml doctor --json`. It is not
a project document and must be adapted if that exact installation is unavailable.
