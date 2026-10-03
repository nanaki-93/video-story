# Local release preparation

T24 prepares an immutable local folder from a completed render job. No uploads or platform
API calls are implemented. An engineering export can produce a draft bundle while rights and
creative review remain pending. `--require-ready` refuses those drafts.

Create a `release_preparation` JSON document containing `schema_version: "1.0"`, an `id`,
the completed `job_id`, and a factual `title`. Optional fields are `description`, public
`disclosure_notes`, `chapters` (`start_frame` and `title`), and an approved PNG `thumbnail`
asset reference. All authored positions remain integer frames. Revision starts at zero.

```sh
tabi release save preparation.json --project ROOT
tabi release inspect PREPARATION_ID --project ROOT
tabi release export PREPARATION_ID --bundle-id NEW_BUNDLE_ID --project ROOT
```

Edits use `release save … --expected-revision N`; atomic draft saves and backups use the shared
project store. Existing bundles are never overwritten. A bundle is assembled in owned temporary
storage, its copies and current inputs are checked, and its directory is atomically published
under `ROOT/bundles/NEW_BUNDLE_ID`. Cancellation/failure removes only that new temporary work.
Every exported file is hashed in `manifest.json`. Video and thumbnail are independent copies.

## Public and private content

`public/` contains `video.mp4`, an approved `thumbnail.png` when selected, `title.txt`,
`description.txt`, `tracklist.csv`, valid `chapters.txt` when requested, `rights-summary.json`,
`disclosure-notes.txt`, `release-metadata.json` and a status/blocker `README.txt`. Public JSON
uses an explicit allowlist. It does not contain source filenames, registered roots, licence
evidence paths, generation records, private claim notes or render command paths. Text entered
in the public title/description/disclosure fields is intentionally included and needs review.

`private/` contains the exact frozen snapshot, final render report, independent export
verification, preparation/review record, inspection, locked registry documents and used music
release records. These records can contain local paths and private notes. They must stay private.
Actual private licence documents, credentials and original distribution masters are not copied.
Full project backup/portability is T32; a release bundle is not a source-project backup.

Track entries intersect each music placement with the actual export interval and use exact
clip-relative start/end samples at 48 kHz. Titles, artist, credits, links and IDs come only from
the explicitly linked music release record. Its master hash and sample metadata must match the
locked audio asset. Missing records leave facts null; unknown ISRC/UPC values remain null.
CSV represents null as blank and quotes formula-like text safely. Ambience is not invented as
a released song. All audible/visual source assets still appear in the rights checks.

## Reviews and readiness

Inspection independently hashes and decodes the completed export, checks its final report,
verifies frozen inputs and evaluates current music metadata. Readiness requires a full production
export with approved, non-synthetic assets and confirmed commercial-use records; it also requires
music metadata, credits/explicit-content review, matching audiovisual review and matching public
metadata/disclosure review. Unknown assigned distribution IDs do not block readiness.

Creative review binds `public.video_sha256`; metadata/disclosure review binds the inspection's
`metadata_sha256`. Reviews are explicit human actions, for example after watching the full film
and reviewing all public text:

```sh
tabi release review PREPARATION_ID --kind creative --project ROOT \
  --expected-hash REVIEWED_VIDEO_SHA --expected-revision N \
  --reviewer PERSON --note 'Actual audiovisual review notes'
tabi release review PREPARATION_ID --kind metadata --project ROOT \
  --expected-hash REVIEWED_METADATA_SHA --expected-revision N \
  --reviewer PERSON --note 'Actual metadata and disclosure review notes'
tabi release export PREPARATION_ID --bundle-id NEW_BUNDLE_ID --require-ready --project ROOT
```

Use each newly saved revision. Changed video bytes are rejected outright. Changes to public text,
credits, chapters, thumbnail or other public facts invalidate the metadata review. Rights reverting
to pending blocks readiness even if the video has a matching creative review. Synthetic/preview
exports cannot receive production creative review. Status means only local preparation state;
it never asserts monetization, Content ID eligibility, claim resolution or platform acceptance.

## Chapters

The current [YouTube chapter guidance](https://support.google.com/youtube/answer/9884579?hl=en),
checked 4 October 2026, requires a first marker at 00:00, at least three ascending markers and
chapters lasting at least ten seconds. The app also checks the final chapter against the exact
clip duration. This implementation conservatively accepts only authored frame positions mapping
to whole seconds; fractional markers are not rounded. Invalid layouts produce a warning and
retain the track list without a chapter file. Account feature access remains a manual platform
check; passing these layout rules does not guarantee chapters will appear.

## Evidence

[The retained bundle manifest](evidence/t24-release-bundle.json) describes a real 60-second,
1,800-frame/1080p export with 2,880,000 audio samples copied into a new draft bundle. Chapters
at 00:00/00:20/00:40 are valid. Missing title/artist/ISRC/UPC for its generated signal remain null.
Synthetic assets, missing release metadata and unreviewed content correctly prevent readiness.
The local bundle is `.local/t23-1080-software-lut/bundles/t24-draft/`; its MP4 remains ignored.

`make schemas check` passes 36 schemas and 227 unit checks. The actual-media release integration
test renders a fresh one-second partial clip, verifies its copied bytes and clipped audio interval,
tests pending rights/reviews, revision conflict, stale metadata, existing/traversing destination
rejection, concurrent edits, corrupted export rejection and private sentinel-note isolation.
The original master and the previously published bundle remain unchanged throughout those failures.

Production approval remains pending on finished original music, factual credits/licences,
approved art and Marco's creative/disclosure decisions. No supplied asset was newly approved.
