# Example contracts

These JSON files now pass the strict Python models and published JSON Schemas. `make check` validates them and checks schema drift. They remain illustrative drafts with unresolved media/approvals; successful structural validation does not make them renderable or production-approved.

All root documents explicitly declare `schema_version` and `document_type`. Scene/action/track references use stable asset IDs and versions. Draft hashes may remain null; a compiled snapshot requires resolved hashes for its direct references. T05/T13 must resolve media, transitive dependencies and compatibility before rendering.

Pilot length: 3600 frames at 30/1 fps = 120 seconds. Audio length: 5,760,000 samples at 48 kHz. Body action intervals cover the timeline; entry and exit transitions are 45 frames each. Repeat policies, curve limits and scene transition kinds are explicit. Template layer dimensions/periods are illustrative design values, not measurements or approval of supplied artwork.

`asset.synthetic.json` records the actual SHA-256 and size of `tests/fixtures/synthetic/pixel.ppm`, a two-pixel owned fixture for schema checks. It is labeled synthetic and cannot receive production approval. Other references do not imply that corresponding media files exist. No licence, approval or generation history has been fabricated.

Timing, registry data and provenance for real sources must be populated by import and review; T04 will create the complete synthetic media pack.

`settings.macos.toml` is a separate developer-settings example for T02. It pins
the externally installed FFmpeg/ffprobe 9.0.2 Cellar paths tested on Apple Silicon;
use it with `tabi --config examples/settings.macos.toml doctor --json`. It is not
a project document and must be adapted if that exact installation is unavailable.
