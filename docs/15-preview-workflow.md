# Episode validation, compilation and preview

T13 exposes the shared Python episode service through the CLI. All commands print JSON. Validation checks structure, registry/file identities and compiler semantics; it does not certify visual quality or guarantee that every asset is supported by the renderer.

Generate a new synthetic project, validate it, and save an immutable compilation:

```sh
.venv/bin/tabi fixtures --output ".local/Preview project" --json
.venv/bin/tabi validate ".local/Preview project/episodes/episode.synthetic.json" --project ".local/Preview project" --purpose synthetic_test
.venv/bin/tabi compile ".local/Preview project/episodes/episode.synthetic.json" --project ".local/Preview project" --purpose synthetic_test
```

Copy the returned `snapshot_sha256` into `SNAPSHOT_SHA` below. The saved file is `snapshots/SNAPSHOT_SHA.json` inside the project. An optional `compile --output NEW_JSON` exports an additional canonical copy and refuses to overwrite a file. Recompiling identical inputs returns the same identity. Draft edits create new snapshots; previous snapshots are never rewritten.

```sh
.venv/bin/tabi snapshot show SNAPSHOT_SHA --project ".local/Preview project"
.venv/bin/tabi --config examples/settings.macos.toml frame SNAPSHOT_SHA --project ".local/Preview project" --frame 151 --output ".local/frame-151.png"
.venv/bin/tabi --config examples/settings.macos.toml preview SNAPSHOT_SHA --project ".local/Preview project" --start 84 --end 216 --output ".local/look-preview.mp4"
```

The range is half-open and uses global frames. Stills use the episode canvas by default; previews use 960×540 at the episode's rational frame rate. Supply both `--width` and `--height` to change the canvas. Prepared layers are uniformly fitted according to the scene policy. The same frozen compiler schedule and renderer drive both outputs. Asset locks are checked before and after rendering, and files are published only after full verification. Existing outputs are preserved. Draft and synthetic content carries a permanent visible label.

`--purpose preview` permits valid draft assets. `synthetic_test` requires synthetic inputs. `production` requires approved source records, and rendering additionally requires an explicitly reviewed snapshot. `snapshot show` exposes the full frozen document and its `review_content_sha256`. After an actual review, the following records the review on a **new** immutable snapshot:

```sh
.venv/bin/tabi snapshot review SNAPSHOT_SHA --project PROJECT --reviewed-hash CONTENT_SHA --reviewer NAME --note NOTE
```

The supplied hash must match exactly, locked media is rechecked, and synthetic/preview snapshots cannot receive production approval. This command records the named person's assertion; it cannot perform artistic or rights review. No production review was performed during implementation.

All commands accept repeated `--root ID=PATH` for explicitly trusted external media roots. Imported documents cannot authorize arbitrary filesystem roots. Invalid structure produces a `scope: structure` report; successful parsing followed by compiler checks produces `scope: compile`. Invalid validation exits 2, and workflow/I/O failures exit 4 with JSON diagnostics on stderr.

## Verification and current limits

`make schemas && make check` passes 22 schemas, Ruff and 168 tests. The six focused episode-service/CLI tests also include an actual FFmpeg frame/range render. They check reproducible compilation, immutable prior snapshots after draft edits, no-clobber export, missing inputs, invalid frame requests, snapshot tampering and approval gates.

The [CLI compilation](evidence/t13-compilation.json) freezes 300 frames, eight events and 15 inputs. [Frame 151](evidence/t13-cli-frame-151.png) was visually inspected. The [range report](evidence/t13-preview-report.json) verifies global frames 84–215 as 132 frames/4.4 seconds of 960×540 H.264/30 video, including strict full decode and timestamps. The ignored local clip is `.local/t13-cli/look-range.mp4`. The measured FFmpeg subprocess took 0.999 seconds; that excludes preparation and verification. [Validation](evidence/t13-validation.json) and [still report](evidence/t13-frame-report.json) preserve the remaining evidence.

This step produces video-only previews; audio mixing is T16. Renderer limitations remain documented in [scene rendering](14-renderer.md). Real Tabi pilot approval, browser playback and long-form jobs are separate acceptance gates. The tests used Apple M5 Pro, macOS 27.0.1, Python 3.11.16 and FFmpeg 9.0.2.
