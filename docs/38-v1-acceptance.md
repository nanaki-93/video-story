# Acceptance gates

Updated 8 October 2026. [PLAN](../PLAN.md) is the agreed direction; [progress](progress.md)
distinguishes implemented features from the next phase. Synthetic fixtures are not production art.

## Verified baseline

- Shared Python asset registry, schemas, compiler, timeline, rendering, audio, owned jobs,
  authenticated local API, built TypeScript UI, backups and release preparation are implemented.
- Reusable fixed scenes, masked scenery and independent loops pass the L04 milestone: 298 core
  checks, 62 actual-media integrations, six frontend checks, 63 schemas, build and packaging.
  Chrome creation, playback, export/download and reuse passed. [L04 evidence](evidence/l04-lofi-refactor.json).
  R01 removes obsolete checks and records a fresh post-cleanup gate; historical totals are not
  the current test count.
- The preserved L05 real-art draft is a complete 90-second silent 1080p Tokyo video. Full decode,
  exact timestamps, no audio streams, protected-region stability, next-cycle match and Chrome
  playback passed. [L05 evidence](evidence/l05-tokyo-lofi-pilot.json). It does not prove a reference
  generator, separated outfits/cabins or natural three-motion animation.

R01 planning/cleanup is complete: **289 core, 62 actual-media and six frontend tests pass**,
along with Ruff/formatting, 63 schemas, TypeScript, production web build, wheel and sdist.
Package inspection confirms shared rendering and the obsolete banner's removal. Three tests
initially hit sandbox loopback restrictions, then passed with local-network permission. Existing
validator bundle-size and test-client-deprecation advisories remain. No new visual acceptance
is claimed by this cleanup.

**3,110 obsolete files / 2,187,528,245 bytes removed; all 486 protected source/pilot hashes
unchanged.** Unrelated staged IDE work is preserved and no MP4 is tracked. The
[cleanup evidence](evidence/r01-repository-cleanup.json) records exact scopes, local hash
manifests and verification. Git history and the supplied asset folders were preserved.

## Required for the reference-generator milestone

| Gate | Required evidence | Current status |
| --- | --- | --- |
| Source library | Read-only catalog includes ignored outfit/emotion/action/scenery references; hashes and relinking work | planned L15 |
| Model and terms | Exact backend/model/dependency revisions, licences/notices, source links/date, explicit installation and measured Mac resources | initial candidate only; L16 |
| Real generation | Actual reference-conditioned outfit, cabin and panorama results within the bounded attempt budget, with likeness and effort review | pending L16/L17 |
| Generation jobs | Frozen inputs/provenance, owned cancellation/recovery, one heavy job, verified atomic output; unavailable model leaves rendering usable | planned L17 |
| Prepared assets | Clean background, character alpha, foreground/mask, anchors, panorama joins, compatible look-specific motion and reviewed hashes | planned L08 |
| Compatibility | Same-family exact template/action binding, 2×2×2 independent combinations, useful mismatches and immutable old scenes | planned L07/L09 |
| Three quiet motions | Breathing, blinks and small gill movement; eye registration, coverage/pose/prop ownership and no phase reset | planned L10 |
| Normal UI | Real reference selection → generate → compare → keep → prepare → select → preview/export, with cancel/error states and no JSON edits | planned L11/L12 |
| Current book correction | Correct orientation/perspective, hands/props and protected original pixels; new version, preserved L05 | open L06 |
| Real reuse | Eight reviewed real combinations, 90-second silent export, 10-minute phase check and a second video reusing unchanged packs without generation | pending L13 |

The initial generation qualification is three categories with at most two attempts each, not
unlimited retries. Reject an unqualified dependency or an unsuccessful model rather than
silently adding a paid provider. Record both unattended latency and human correction/retry time.
No preset timing target or monthly throughput promise is established before these measurements.

## Visual and release gates that tests cannot grant

The selected Tabi identity and every final asset version require comparison to the actual supplied
references. Review eyes, frills, headphones, anatomy, outfit, book/hand perspective, layer edges,
lighting, cabin reveal regions, foreground occlusion, district variety and all motion/journey joins.
A technical alpha/padding or fixed-pixel check cannot judge the illustration inside the edited area.

A whole-output loop requires a compatible duration and phase review for every moving layer.
Continuous arbitrary-duration exports are allowed but must not be labeled seamlessly looping.
The existing pilot uses a scaled 1664×936 illustration; upscale dimensions do not establish native
4K detail. Safari and representative final-art long-form/native-4K resource checks remain open.
Prior synthetic workload measurements in [long-form](36-longform.md) apply only to their fixtures.

Supply factual source rights and original/cleared music before a musical release. The current
requested acceptance stays silent. Recheck official commercial terms on provider/version changes
and before release, including weights and runtime dependencies. Unknown rights stay pending;
licence permission does not establish YouTube monetization eligibility. Public metadata must be
factual, and upload/publishing remains manual. No automatic art approval or silent cloud upload.
