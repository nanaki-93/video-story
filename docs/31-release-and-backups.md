# Release preparation and private backups

Release uses a verified saved render, editable public title/description/disclosure, authored
integer-frame chapters and an approved thumbnail. Save the draft and inspect it to run the
shared Python technical and rights checks. The public JSON preview exposes exactly the
metadata being reviewed. Review records bind the exported video or public metadata hash;
editing it makes that review stale. A synthetic preview cannot gain production creative review.

Draft bundles are allowed while blockers remain. Requiring ready for manual upload rejects
missing rights, original music, creative review, metadata/disclosure review and other recorded
issues. Bundle export copies and verifies the video; `public/` contains the shareable files,
while `private/` retains source and review records. Authenticated file links expose only the
public files from the bundle manifest. The app does not upload, query platform status or
infer claim resolution. Recorded URLs and claim notes remain private factual notes.

For a private project backup, first pause or finish queued/running jobs and choose a new folder
outside the source project. The service streams independent file copies, retains drafts,
revision backups, approved snapshots, source artwork, music, private evidence, job artifacts
and exports, and skips disposable caches, unfinished upload staging and process locks.
Referenced render media is included even if it lives in an otherwise disposable location.
Unavailable historical source references are explicitly listed as warnings; missing required
render media fails the backup.

Linked external media is copied below `.portable-media/<root-id>/`. A strict local mapping
contains root IDs only and can point only inside that project's copy. Asset documents and
snapshot hashes stay byte-identical, so moving a project does not rewrite its approvals.
The original absolute paths recorded as historical evidence are not rewritten.

Restore checks the exact manifest inventory, hashes, project identity, media, snapshots and job
journals before atomically publishing a new folder. It never overwrites an existing project,
follows archive symlinks or unpacks arbitrary ZIP paths. The directory bundle is deliberately
uncompressed and private; move the complete backup folder between disks. It is not an encrypted
archive. Use Projects → Relink for an existing project moved to a new registered location.

The CLI invokes the same core:

```sh
tabi backup export '/path/to/project' '/other/disk/private-backup' --root 'music=/path/to/masters'
tabi backup inspect '/other/disk/private-backup'
tabi backup restore '/other/disk/private-backup' '/path/to/restored-project'
```

After restore, the registered original external disk is unnecessary for copied render media.
Paused jobs still require compatible renderer/tool fingerprints before resume. A new renderer
version requires a new export; verified old videos and their reports remain accessible.
