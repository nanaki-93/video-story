# Asset import and review

T05 implements copy/link import, independent media checks, immutable versions, relinking and image proxy records. CLI and API callers use `AssetService`; a missing/changed file cannot be used by `require_valid`. Approval is a recorded human decision bound to the full asset metadata and file hashes. Checking an edited file invalidates its effective approval without rewriting the historical record.

Create a project and a JSON/YAML import request (the `import_request` schema validates it):

```json
{
  "id": "my.cabin",
  "version": "1.0",
  "kind": "still",
  "paths": [{"root_id": "art", "path": "Cabin 東京.png"}],
  "mode": "copy",
  "provenance": {"origin": "user_supplied", "commercial_use": "pending"}
}
```

```sh
.venv/bin/tabi asset import /path/to/project /path/to/import.json --root art=/path/to/art
.venv/bin/tabi asset list /path/to/project
.venv/bin/tabi asset show /path/to/project my.cabin 1.0
.venv/bin/tabi asset check /path/to/project my.cabin 1.0
.venv/bin/tabi asset proxy /path/to/project my.cabin 1.0 --new-version 1.1 --max-edge 640
```

All asset commands return JSON. `check` exits 2 when working media is invalid; command/I/O failures exit 4. Copy import keeps byte-identical source files under a uniquely named `sources/` folder; `source` retains the original selected location. The copied asset remains usable if the original drive disconnects. Link import references the supplied files directly. Register its external root explicitly on every invocation; imported project declarations never grant access. Roots can be remapped to a new mount location while keeping relative identities and exact bytes unchanged.

Image sequences use `kind: sequence`, an explicitly ordered `paths` list and `fps: {"num": 25, "den": 1}` (use the actual authored rate). The importer does not guess fps from names, silently sort frames, alter timing or normalize artwork. Every frame is decoded and must share its canvas, format, color interpretation and alpha. Masks require raw grayscale coverage. Nontrivial EXIF orientation requires an explicitly prepared copy. PNG proxy generation converts tagged images through Pillow/LittleCMS to sRGB; untagged RGB is interpreted as sRGB for that preview only. Original metadata and files stay intact. Working color approval is separate.

For changed paths, create a JSON list of `MediaPath` objects in original sequence order:

```sh
.venv/bin/tabi asset relink /path/to/project my.cabin 1.0 --new-version 1.2 --paths /path/to/paths.json --root art=/new/art/root
```

Every candidate hash and size must match. This creates a draft because paths/version change the reviewed content. Changed content requires a new import version. Existing versions are never overwritten by import/relink/proxy. Only a deliberate approval command changes a draft's review status; it requires the current full `content_sha256` from `check`, an identified reviewer and a note:

```sh
.venv/bin/tabi asset approve /path/to/project my.cabin 1.2 --reviewed-hash ACTUAL_REVIEWED_SHA256 --reviewer 'Reviewer name' --note 'Actual review evidence'
```

Synthetic/unknown provenance and unresolved rights are rejected. This command is a mechanism for recording review, not proof that the operator performed it. No supplied art is automatically approved. Actual media hashes are rechecked; a changed file makes the approval ineffective. Proxy health is reported separately because proxies are disposable and production uses the master files.

Image/font checks use Pillow. PCM WAV import counts actual decoded samples and rejects truncation. Video import uses [ffprobe frame/timestamp reporting](https://ffmpeg.org/ffprobe.html) and a strict FFmpeg decode; variable-rate sources need explicit preparation. Compressed music requires an exported PCM WAV master. PNG color management uses [Pillow ImageCms](https://pillow.readthedocs.io/en/stable/reference/ImageCms.html).

Publication order is verified copies, then atomic registry metadata under the project lock. Failure removes only the new operation's staging directory. A hard crash can leave an unreferenced owned copy for later storage review. Originals and registered media are never generic cache-cleanup targets. This is local application coordination, not an OS sandbox against another process editing the same files.

Evidence: [T05 record](archive/v1-tasks.md#t05), [observed fixture health](evidence/t05-asset-health.json). No actual art approval is implied.
