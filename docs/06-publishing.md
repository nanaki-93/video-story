# Music handoff and release preparation

## Independent music and visual products

Melotrail or the DAW exports finished original WAV masters and optional metadata. Tabi Story Studio consumes them without calling Melotrail's internal services. Music can be released independently through DistroKid; the episode uses those recordings as its soundtrack.

Define an optional `music-release.json` interchange: artist, release title, track titles, order, writers/credits, master filenames/hashes, explicit content flags, source-project references, known ISRC/UPC, rights records and AI-generation notes. Unknown assigned identifiers remain null. Do not invent DistroKid identifiers or expect an upload API.

Preserve distribution masters untouched. Render audio mixes and ambience separately from those masters. If a music arrangement changes materially, export a new master/version and update the episode lock; do not overwrite the approved WAV in place.

## Human publishing sequence

1. Finalize original recordings; inspect samples, instruments and model/asset licences.
2. Prepare music artwork, credits, artist spelling and release metadata.
3. Upload through DistroKid manually and record actual assigned IDs/links when available.
4. Finish the Tabi episode with an authored concept and approve its audiovisual result.
5. Prepare thumbnail, description, track list, chapters where applicable, credits and disclosure notes.
6. Upload video privately/unlisted if the chosen publication process allows; inspect processing and claims.
7. If Content ID is enabled, verify current service eligibility, handling of your own videos and any available claim-release procedure in the authenticated distributor workflow.
8. Publish deliberately and record actual URLs and dates.

DistroKid documentation could not be retrieved during preparation of this plan. Its current Content ID eligibility, allowlisting scope, prices, AI rules and any claim procedure are therefore unresolved checks, not implementation assumptions. The release page provides editable notes and links; it must not claim that an entire channel is allowlisted or a claim is resolved without evidence.

## YouTube guidance integrated into the workflow

YouTube's monetization guidance describes original/authentic content and warns about mass-produced or repetitive output. A recurring Tabi design, visual variation or 4K export does not guarantee approval. Keep individual episode concepts and musical contribution clear; do not implement a cosmetic city/tint swap as the originality strategy.

The current disclosure guidance includes AI-created music when music is the main focus. Store factual generation/editing notes and prompt a publishing review against the current guidance. Do not automatically claim that any AI-assisted repair requires the same disclosure as music generation. Disclosure is a publishing decision, not a fabricated badge in the rendered image.

Keeping some melody recognizable is an artistic goal from the Melotrail project; it is not asserted here as a YouTube rule. Distinguish commercial-use rights from eligibility for Content ID and from copyright ownership. Where uncertain, record pending status instead of a legal conclusion.

## Release folder

Produce `video.mp4`, `thumbnail.png` if approved, `title.txt`, `description.txt`, `tracklist.csv`, `chapters.txt` when appropriate, `episode-snapshot.json`, `render-report.json`, `rights-summary.json`, `disclosure-notes.txt`, `release-metadata.json`, and a `README.txt` listing unresolved checks. No credentials or private licence documents are copied into a public bundle. Offer a separate private archive of source/rights evidence.

Track list includes episode start/end, title, artist, asset version, actual release link and known ISRC. Chapter rules must be checked against current YouTube requirements before presenting them as upload-ready. Unsupported chapter layouts remain a simple track list.

## Publishing status

Statuses: draft → technically verified → creatively reviewed → rights reviewed → ready for manual upload → uploaded → published. The app cannot infer platform monetization approval from any of these states. Missing rights, unreviewed AI disclosure or placeholder art blocks the ready-for-upload label while allowing development previews and draft exports.
