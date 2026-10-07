# Independent cinematic shots without generated joins

## U06a — Refresh rebuilt review media in Chrome

**Status** [x] Verified. Six section/API checks, 383 core checks, 76 actual-media checks (one optional private fixture skipped), eight frontend checks, 68 contracts, Ruff, TypeScript, build and package pass. Real Chrome changes an eight-second Yanaka source to frames 12–192 and loads/plays 7.5 seconds without refreshing the page. [Evidence](evidence/u06a-review-preview.json).

**Behavior** Version selected-video, join and review-image URLs by their content hashes. Reject a stale requested hash while retaining authenticated unversioned links. Preserve original clips, selected ranges, review gates and episode files.

**Verification** Extend the existing section API regression across two ranges, covering distinct URLs/current bytes/stale versions/source preservation/authentication. Run the relevant core and actual-media gates, then repeat the real Chrome section edit without a page refresh before committing U06a.

## U06 — Test the independent plan with real TABI footage

**Status** [ ] Real Flow trial in progress. All twelve real district/camera references are reviewed and imported. Three independent shots (22.5 seconds) are accepted through the app, including one corrected mouth take and one safe source-range adjustment; the fourth shot is generating. Displayed video cost so far: 500 / 1400 existing credits. No final creative or release approval.

**Target files**
- `.local/u06-real-independent/**` (ignored) — preparation/terms, task-owned worker, native references and clips, screenshots, read-only verification and output evidence; no MP4 enters Git.
- `docs/evidence/u06-real-independent.json` (new), `docs/progress.md`, `docs/38-v1-acceptance.md`, `docs/tasks/INDEX.md` — actual attempt/credit/time results, full playback and remaining creative limits.

**Inputs / dependencies**
- U05 and Marco's explicit request on 7 October 2026 to test the workflow with a real TABI video.
- Existing Google Flow Ultra allowance; observed 22849 credits. Recheck hosted commercial/output terms and the exact displayed models before generation. No new purchase, provider, subscription or music upload.

**Trial rules**
- Use the current twelve-shot 90-second independent preset. Prepare and compare each named starting image with the supplied TABI artwork, especially the Tokyo Bay ending, before motion.
- Flow handles reference/video generation; normal video-story UI handles setup, references, saved prompts, imports, whole-clip/ending review, retries, trimming and export. No per-video API, JSON edits or custom assembly.
- Observe costs before each request. Budget up to 1400 existing video credits (twelve 100-credit starts and at most two extra starts if still displayed), with one focused retry per failed shot. Record reference-generation costs separately and keep total use within the same ceiling.
- Stop a repeated quality failure rather than conceal it; preserve attempts and any partial accepted run. Do not weaken visual reviews to claim a finished video.
- Keep all original drafts and the 31 U05-preserved media hashes unchanged. New sources and outputs remain local and immutable.
- Verify exact frames/PTS and source/output hashes, review full normal browser playback and record actual preparation, retries and operator effort. Software checks do not grant Marco's final aesthetic or publication approval.

**Verification**
Read-only independent full decode, timestamp/range/hash checks on the UI-produced export; actual Chrome playback and representative beginning/middle/ending evidence. Run focused software gates only if trial findings require implementation changes; otherwise retain U05's passing engineering gate. Commit the trial evidence with U06 while preserving staged IDE files.

Marco reviewed U04 and explicitly selected independent cinematic shots with deliberate camera
cuts. He does not want repeated attempts to find footage that matches the preceding clip.
U04 improves scenery but still requires six native extensions. U05 removes that dependency
from the next-video preset. Original episodes, clips and approved hashes remain unchanged.

## U05 — Remove Flow extensions from the new Tokyo preset

**Status** [x] Engineering verified: 30 focused, 383 core, 76 actual-media and eight frontend passes, 68 contracts, Ruff/schema/build/package checks and target-Mac embedded-browser observation. One optional private-media test is skipped. Individual generated-shot quality and real preparation/time/credit effort remain unqualified. [Evidence](evidence/u05-independent-flow.json).

**Target files**
- `src/tabi/core/flow/shots.py` — two independent framings per district, twelve 180-frame shots, zero extensions and clear independent-reference instructions.
- `web/src/flow.ts` — explain fixed camera cuts and independent generation, display a single fresh-shot credit estimate for the new preset while keeping saved extension workflows usable.
- `tests/unit/test_flow_shot_runner.py`, `tests/unit/test_flow_shot_api.py`, `tests/unit/test_flow_cli.py` — default plan, refusal to extend an incomplete independent shot, exact fixed cuts, keyed references, cost/clone compatibility and original preservation.
- `tests/integration/test_flow_workflow.py`, `tests/integration/test_flow_shot_workflow.py` — twelve fresh starts, all predetermined 180-frame ranges, retry/reopen, no extension input, exact 90-second media; retain a separate saved six-shot extension regression.
- `tests/fixtures/flow-u04-recipe.json` (new) — immutable six-shot compatibility input copied from U04 evidence, included with source-distribution tests.
- `PLAN.md`, `docs/37-operations.md`, `docs/38-v1-acceptance.md`, `docs/progress.md`, `docs/tasks/INDEX.md`, `docs/evidence/u05-independent-flow.json` (new) — decision, dated official Flow capabilities, verified behavior, trade-offs and remaining production gates.
- `.local/u05-independent-flow/**` (ignored verification artifacts) — synthetic UI fixtures, owned worker helper, screenshots and hash-verified local test media; never commit these or any MP4.

**Inputs / dependencies**
- U04 and Marco's explicit choice in this chat on 7 October 2026. Existing Veo route only; no new model/provider, footage requests, credits, subscription or weights.
- Official Flow documentation confirms eight-second Veo frames-to-video inputs and start/end-frame controls. The Agent supports batch variations; the local app's supported consumer-account bridge remains assisted.

**Implementation rules**
- Keep 2160 frames at 24/1 fps. Each new shot uses an eight-second independent source with a predetermined first 180-frame cut (7.5 seconds); no generated end-to-start match, native Extend, loop, freeze padding or interpolation.
- Two complementary wide/medium images per district create deliberate camera cuts. Preserve the six original district reference keys/framing where possible so an explicitly constructed variation can retain matching U04 references.
- Carry each assigned exterior and quiet rest/watch action. Individual character/scenery quality still needs human review. Do not bypass review or claim zero generative failures.
- Existing saved recipes retain their durations, extensions, credit/history semantics and canonical bytes. Python alone supplies the schedule; no new schema is needed.
- Keep explicit safe-outpoint review; imported originals remain immutable. An undersized new shot stops or restarts, never silently re-enables Extend.
- Explain increased initial reference preparation and fresh-shot costs. No lower total time/credits, unattended batching or 30-video monthly capacity claim without measurements.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml TABI_FLOW_EVIDENCE_DIR=.local/u05-independent-flow .tools/bin/uv run --frozen pytest --run-media tests/unit/test_flow_shot_runner.py tests/unit/test_flow_shot_api.py tests/unit/test_flow_cli.py tests/integration/test_flow_shot_workflow.py`

Run `make check web-check web-build package` and the target-Mac `make test-media` gate, observe the new Setup/reference/cost controls in the embedded browser, compare preserved U03 media hashes, and commit U05 without the unrelated staged IDE files or any MP4.

# Distinct Tokyo views and a calmer production preset

Marco finds the U03 draft interesting but rejects its closing panorama and repetitive exterior,
and worries about lengthy trial and error. New videos should plan distinct window views before
generation, with quiet rest/watch actions. Preserve the real draft and all saved recipes.

## U04 — Bind each Tokyo shot to its own window view

**Status** [x] Engineering verified: 381 core, 75 actual-media and eight frontend passes, 68 contracts, Ruff/schema/build/package checks and target-Mac embedded-browser observation. One optional private-media test is skipped. Real scenery and reduced retry effort need a later trial.

**Target files**
- `src/tabi/core/models/flow.py` — optional hash-compatible shot exterior and consistent shared-reference scenery.
- `src/tabi/core/flow/shots.py` — six distinct illustrated Tokyo views, six 15-second rest/watch shots, assigned reference preparation.
- `src/tabi/core/flow/prompts.py` — carry the assigned exterior through fresh starts and in-shot continuation.
- `src/tabi/core/flow/service.py` — invalidate reference reuse when a shot's exterior changes.
- `src/tabi/core/flow/review.py` — include the planned exterior and window-motion checks in actual clip review.
- `web/src/flow.ts` — editable shot scenery, clear reference titles/counts and scenery confirmation in normal UI.
- `tests/unit/test_flow_shot_contracts.py`, `tests/unit/test_flow_shot_runner.py`, `tests/unit/test_flow_shot_api.py`, `tests/unit/test_flow_cli.py` — reference selection, clone invalidation, fresh/continued prompts, strict inputs and legacy hash checks.
- `tests/integration/test_flow_workflow.py` — exercise six distinct references, per-shot scenery review, native sections and exact 90-second assembly with actual synthetic media.
- `schemas/flow_episode.schema.json`, `schemas/web_flow.schema.json` — generated affected contracts.
- `web/src/generated/flow_episode.ts`, `web/src/generated/web_flow.ts`, `web/src/generated/validators.cjs` — generated browser contracts.
- `PLAN.md`, `docs/37-operations.md`, `docs/38-v1-acceptance.md`, `docs/progress.md`, `docs/tasks/INDEX.md`, `docs/evidence/u04-tokyo-scenery.json` (new) — feedback, implementation evidence, current defaults and remaining creative/throughput gates.

**Inputs / dependencies**
- U03 and Marco's feedback on 7 October 2026. Use the existing local engine and assisted Flow handoff; no new provider, paid app or generation request.
- Marco selected a stylized Tokyo journey with distinct districts. Source district descriptions from the official Tokyo tourism guide; this does not licence photographs or imply actual rail visibility.

**Implementation rules**
- Schema first: optional shot exterior is omitted when absent, preserving existing canonical hashes and immutable approved/saved files. Unknown fields and noninteger timing remain rejected.
- Keep six shots and 2160 frames, each with a distinct starting-image key. Use calm rest/watch actions and at most one extension per shot; saved drinking/breathing plans keep working.
- Prepare each planned exterior in its starting image. Describe window geometry, travel direction and parallax consistently; a fresh camera cut may advance to a new district while continuation stays within that district.
- Display/edit the shot descriptions during Setup and show them during image/clip review. Python supplies all schedules and prompts. A changed exterior requires fresh image reviews through an explicit variation.
- Keep budgets, retry caps, human approval, secure transport and owned exports. Do not claim prompt changes repair the current MP4, eliminate retry needs, or qualify 30 videos/month.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/unit/test_flow_shot_contracts.py tests/unit/test_flow_shot_runner.py tests/unit/test_flow_shot_api.py tests/unit/test_flow_cli.py tests/unit/test_flow_prompts.py tests/integration/test_flow_shot_workflow.py`

Also regenerate affected contracts; run `make check web-check web-build package` and the target-Mac `make test-media` gate. Observe Setup and reference guidance in the UI; preserve original draft hashes and staged IDE files. Commit the verified U04 step.

# App-only review and full TABI workflow trial

Make the existing Flow workflow usable without per-video API calls, JSON edits or render
scripts. Keep generation honestly identified as assisted until a supported connector using
the existing entitlement is established; do not substitute a paid API or private endpoint.
The previous S/F/P/T task bodies below remain implementation history.

## U01 — Select and verify a usable clip section

**Status** [x] Seven focused unit/media checks pass, including the complete synthetic 90-second shot workflow. Section rendering, atomic failure recovery, original preservation and continuation safeguards verified.

**Target files**
- `src/tabi/core/flow/review.py` — prepare a frame-exact section preview and fresh evidence atomically for an unreviewed candidate.
- `src/tabi/core/flow/service.py` — verify new range-bound packets while keeping old evidence readable.
- `tests/integration/test_flow_review_media.py` — verify rendered section frames, immutable originals, stale edits, reviewed-clip refusal and recovery after a failed prepare.
- `tests/unit/test_flow_review.py` — range boundary validation where no media is needed.
- `docs/progress.md`, `docs/tasks/INDEX.md` — record the active queue and verified behavior.

**Inputs / dependencies**
- S04 real trial: usable source ranges required the API; the normal player showed excluded footage.

**Implementation rules**
- Python owns integer frame intervals. Only pending candidates in the active branch may change; stale revision/hash requests fail.
- Keep original media and immutable history. Rebuild selected playback, sample images and join together before publishing the draft revision; a failed render leaves the old candidate unchanged.
- Bind new packets to source hash and selected range. Preserve legacy packet compatibility.
- An in-shot continuation cannot discard its opening. An early ending cannot become a native Extend parent unless the selected section finishes the shot/video. Never loop or pad to reach the target.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/unit/test_flow_review.py tests/integration/test_flow_review_media.py tests/integration/test_flow_shot_workflow.py`

## U02 — Expose section review in the normal app

**Status** [x] Seven API/security checks, eight frontend checks, 68 contract drift checks, TypeScript, formatting and production build pass. Target-Mac section playback follows in U03.

**Target files**
- `src/tabi/api/contracts.py`, `src/tabi/api/flow.py` — authenticated section preparation using the U01 service, selected playback and clear source/frame bounds.
- `web/src/flow.ts` — simple optional section controls; the main review player shows the selected footage, and original footage stays available separately.
- `tests/unit/test_flow_shot_api.py` — authenticated range requests, stale/foreign media checks and selected-preview transport.
- `schemas/web_flow.schema.json`, `web/src/generated/web_flow.ts`, `web/src/generated/validators.cjs` — generated affected contracts.
- `docs/progress.md`, `docs/tasks/INDEX.md` — verification evidence.

**Inputs / dependencies**
- U01; reuse local uploads, session security, existing review and Finish services.

**Implementation rules**
- Start with the whole clip. Let the user adjust start/end frames and rebuild the review before accepting. Show seconds as presentation only; Python owns range validity and preview rendering.
- Clear unsaved review confirmations on a range change. Never silently accept, shorten the 90-second target, modify approved clips or reserve extra provider credits for local trimming.
- Keep the source filename/hash and actual provider model attached. No mock generation button or claimed Flow account connection.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_shot_api.py tests/unit/test_web_flow_contracts.py`

Also run `make schemas`, `npm --prefix web run schemas`, `make web-check` and `make web-build` with the local offline uv cache.

## U02a — Correct all character details after an identity rejection

**Status** [x] Seventeen focused prompt/runner checks pass. New identity retries preserve markings, clothing and accessories; existing attempt hashes remain unchanged.

**Target files**
- `src/tabi/core/flow/prompts.py` — identity retry protects markings, clothing and accessories as well as gills and neck.
- `tests/unit/test_flow_prompts.py` — focused correction covers accessories and keeps the current action.
- `docs/progress.md`, `docs/tasks/INDEX.md` — record the first real take's headphone mutation and verification.

**Inputs / dependencies**
- U02; the U03 opening added a yellow star to the reference's plain headphone earcup. The app's existing identity correction covered only gills and neck.

**Implementation rules**
- Keep one focused correction and the same clean starting reference. Protect original appearance without inventing a new inventory or replacing the requested action.
- Existing saved attempt text/hashes remain immutable. Only newly prepared identity retries use the corrected template; same attempt/credit/retry caps.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_prompts.py tests/unit/test_flow_shot_runner.py`

## U02b — Use confirmed cup facts in a prop correction

**Status** [x] Twenty-one focused prompt/runner checks pass. Cup-action corrections use confirmed type/handle/saucer facts and preserve unknowns, unrelated actions and immutable saved prompts.

**Target files**
- `src/tabi/core/flow/prompts.py` — focus cup-action retries on the confirmed cup kind and handle/saucer facts.
- `tests/unit/test_flow_prompts.py` — cover known and unknown facts without repeating the entire inventory or replacing the action.
- `docs/progress.md`, `docs/tasks/INDEX.md` — record the two rejected cup returns and verified correction behavior.

**Inputs / dependencies**
- U02a. At 45 accepted seconds, both return takes changed the handle-free takeaway cup into a handled cup. The generic rigid-object correction omitted facts already confirmed in the app.

**Implementation rules**
- Add only known cup facts for pickup, sip or return corrections. Unknown handle/saucer facts stay unknown; unrelated actions retain the generic prop correction.
- Preserve existing saved prompts, hashes, accepted parents and reviews. No new provider or generation is part of this implementation step.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_prompts.py tests/unit/test_flow_shot_runner.py`

## U02c — Recover from a retry limit without losing accepted footage

**Status** [x] Twenty-one core/API checks, eight frontend checks, 68 contracts, TypeScript, formatting and production build pass. Recovery preserves accepted history and caps; the actual 45-second episode resumes in U03.

**Target files**
- `src/tabi/core/flow/runner.py` — expose and apply an explicit one-step retry-limit increase, within the existing hard maximum and unchanged global caps.
- `src/tabi/api/contracts.py`, `src/tabi/api/flow.py` — typed next-action metadata and revision-guarded authenticated recovery route.
- `web/src/flow.ts` — one recovery button when Python permits it; explain that the credit ceiling remains unchanged.
- `tests/unit/test_flow_runner.py`, `tests/unit/test_flow_shot_api.py` — preserve accepted history and parent identity; refuse stale, unresolved, budget-exhausted and hard-limit changes.
- `schemas/web_flow.schema.json`, `web/src/generated/web_flow.ts`, `web/src/generated/validators.cjs` — regenerated affected transport contracts.
- `docs/progress.md`, `docs/tasks/INDEX.md` — verified recovery and remaining real-media gate.

**Inputs / dependencies**
- U02b. U03 reaches the default one-retry limit with 45 seconds accepted; the current UI offers only backtracking or a new video.

**Implementation rules**
- Increase the configured per-action retry allowance by exactly one, at most three. Keep the episode, recipe, references, accepted footage, immutable attempts, max-attempt limit and credit ceiling.
- Offer recovery only when the next request would otherwise be valid and fit the existing budget. Do not bypass unknown provider results, pending review or paused state.
- Save the changed limit atomically; do not reserve credits or submit a generation. Preparing the next prompt remains a separate explicit action.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_runner.py tests/unit/test_flow_shot_api.py tests/unit/test_web_flow_contracts.py`

Also run `make schemas`, `npm --prefix web run schemas`, `make web-check` and `make web-build` with the local offline uv cache.

## U02d — Keep both hands around a handle-free cup

**Status** [x] Thirty focused prompt/runner checks pass. New handle-free pickup/sip/return prompts use both hands and explicitly preserve the absent handle; known handled and unknown facts retain their previous behavior.

**Target files**
- `src/tabi/core/flow/prompts.py` — make confirmed handle-free pickup/sip/return use both existing hands around the cup body and explicitly keep the cup without a handle.
- `tests/unit/test_flow_prompts.py` — verify the complete two-hand routine while preserving handled and unknown cases.
- `docs/progress.md`, `docs/tasks/INDEX.md` — record Marco's requested correction and verification.

**Inputs / dependencies**
- U02c. Marco explicitly requested both hands and no handle after four returns inherited or introduced a handle from the sip parent.

**Implementation rules**
- Apply the instruction to the whole new cup routine from its clean starting image. Keep existing saved takes and prompts immutable; use known facts only.
- Keep the original action ordering and ending states. Do not reset retry or credit limits.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_prompts.py tests/unit/test_flow_shot_runner.py`

## U02e — Restart a troubled shot from its clean image

**Status** [x] Thirty-five focused core/API checks, eight frontend checks, 68 contracts, TypeScript, Ruff and production build pass. Preserved-history shot restart is available through the normal UI; U03 exercises the actual drink recovery.

**Target files**
- `src/tabi/core/flow/runner.py` — identify and restart the current partial shot through the existing preserved-history branching service.
- `src/tabi/api/contracts.py`, `src/tabi/api/flow.py` — typed recovery availability and revision-guarded route.
- `web/src/flow.ts` — one clearly labelled shot restart control, without browser timeline logic.
- `tests/unit/test_flow_shot_runner.py`, `tests/unit/test_flow_shot_api.py` — verify earlier shots/history/caps survive and unresolved work cannot be bypassed.
- `schemas/web_flow.schema.json`, `web/src/generated/web_flow.ts`, `web/src/generated/validators.cjs` — regenerate the affected transport contract.
- `docs/progress.md`, `docs/tasks/INDEX.md` — verification and target-Mac recovery evidence.

**Inputs / dependencies**
- U02d. The existing attention button backtracks only one clip; restarting the three-part drink shot must be possible through the app without JSON/API shortcuts.

**Implementation rules**
- Keep completed earlier shots, immutable sources/attempts/reviews and the original credit/attempt/retry caps. Remove only the current partial shot from the active branch; do not erase it.
- Python selects the clean-shot boundary. Allow only an idle partial planned shot; block pending provider outcomes, pending review and pauses. A fresh shot still counts as a retry of its existing starting beat.
- Do not prepare or generate automatically. The next ordinary Prepare action uses the same reviewed starting image.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_shot_runner.py tests/unit/test_flow_shot_api.py tests/unit/test_flow_runner.py`

Also regenerate schemas/browser contracts, run `make web-check web-build`, then exercise the actual saved drink-shot restart in U03.

## U02f — Keep the closing breath within the seated outfit

**Status** [x] — 36 focused checks and the full 375-test core/package gate pass; real generated anatomy remains part of U03 review.

**Target files**
- `src/tabi/core/flow/prompts.py` — constrain the breath to a modest seated chest/shoulder rise with unchanged clothing coverage and hand position.
- `docs/progress.md`, `docs/tasks/INDEX.md` — record verification and the remaining real-media check.

**Inputs / dependencies**
- U02e. Two U03 deep-breath takes inflated the torso, opened the closed coat and invented belly/tail markings, including after the identity correction.

**Implementation rules**
- Keep one inhale, pause and complete exhale, with hips seated, the same clothing coverage and current hand position. Avoid suggesting a whole-body expansion or inventing a garment type.
- Change only newly compiled breath prompts; saved attempts, source pixels, schedules and all limits remain unchanged.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_prompts.py tests/unit/test_flow_shot_runner.py`

Also run Ruff and the core/package gates; then review the real correction in U03. Tests cannot qualify generated anatomy.

## U03 — Run the full 90-second journey through the app

**Status** [x] — Real silent 90-second draft exported and downloaded through the normal app; all 2160 frames/PTS and 36 source-range comparisons pass, full Chrome playback reaches the end. Marco's final creative/publication approval remains open. See `docs/evidence/u03-tabi-app-trial.json`.

**Target files**
- `docs/evidence/u03-tabi-app-trial.json` (new) — actual UI steps, verified source/output paths, costs, provider boundaries and unresolved quality findings.
- `docs/evidence/u03-tabi-app-trial.jpg` (new) — target-Mac app screenshot.
- `PLAN.md`, `docs/37-operations.md`, `docs/38-v1-acceptance.md`, `docs/progress.md`, `docs/tasks/INDEX.md` — measured outcome and remaining generation dependency.

**Inputs / dependencies**
- U02–U02f. Marco confirmed: allow Flow for generation; everything else must use video-story.
- Direct generation solely inside video-story is blocked on a supported consumer-Flow connector within the existing allowance. Official Flow Agent documentation does not establish this; Gemini video API pricing is separate. No new purchase is authorized.

**Implementation rules**
- Use normal UI for project/episode setup, references, generation handoff, import, section selection, review and export. Tools may inspect output independently; no per-video API or JSON shortcuts to produce it.
- Keep the full 2160-frame target. A shorter salvage or repeated/padded footage cannot pass this test.
- Check current allowance and hosted-model terms before new generation; preserve exact prompts, source identities, actual model and rejected takes. Silent visual draft; music and publication remain deferred.
- Record a concrete blocker if the required generation mode or creative quality cannot be qualified. Do not mark this task complete just because a synthetic render passed.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml make check web-check web-build package test-media`

Also exercise the target-Mac UI, inspect every accepted clip and join, play the full export,
and independently verify all 2160 decoded frames/PTS and the frozen input ranges.

---

# Planned shots with clean starting references

Active implementation queue: S01–S04. Build a 90-second train story from independently started
shots and short local extension chains. Keep the assisted Flow handoff, reviewed cuts, existing
exports and local soundtrack; this engineering change does not claim to eliminate generated defects.

The simple default uses three reviewed images (wide, medium/table, close), reused across six
shots. Durations are 15 + 15 + 22 + 8 + 15 + 15 seconds; the 22-second drink shot accommodates
separate pickup, sip and return clips. Each camera cut restarts from its assigned clean image.
All reference images are collected before generation, and existing single-shot drafts keep
working without migrations or changed hashes. New generation costs distinguish a fresh shot
from an extension. Technical checks cannot approve appearance or establish output rights.

## S01 — Define compatible shot and reference contracts

**Status** [x] 22 contract/compatibility tests pass; 68 schemas and browser contracts regenerated, drift checked and TypeScript compiled.

**Target files**
- `src/tabi/core/models/flow.py` — strict shots, keyed reference state/review, shot-start attempts, bounded corrections and optional opening cost; omit new defaults from old hashes.
- `tests/unit/test_flow_shot_contracts.py` — invalid schedules/lineage/reference bindings and legacy hash compatibility.
- `schemas/flow_episode.schema.json`, `schemas/flow_attempt.schema.json`, `schemas/flow_export.schema.json`, `schemas/web_flow.schema.json` — generated affected schemas.
- `web/src/generated/flow_episode.ts`, `web/src/generated/flow_attempt.ts`, `web/src/generated/flow_export.ts`, `web/src/generated/web_flow.ts`, `web/src/generated/validators.cjs` — generated affected browser contracts.
- `schemas/web_releases.schema.json`, `web/src/generated/web_releases.ts` — generated delivery contracts containing the same frozen Flow references.
- `docs/progress.md`, `docs/tasks/INDEX.md` — activate and record the shot queue.

**Inputs / dependencies**
- F01–F13 and the preserved F12 real Tokyo trial. No new provider calls or artwork needed.

**Implementation rules**
- Python owns ordered shot duration/beat validation, rational fps, immutable hashes and strict fields.
- Preserve canonical hashes for old recipes, references, attempts and frozen exports; never edit approved snapshots.
- A new shot's previous clip is its editorial predecessor, not its generation input. Explicit `shot_start` mode and shot ID distinguish it from Extend.
- Reject duplicate keys/IDs, missing shot associations, cross-shot Extend and accepted footage that crosses an unreviewed shot boundary.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_contracts.py tests/unit/test_flow_shot_contracts.py tests/unit/test_flow_release_contracts.py`

Also regenerate Python/browser contracts and run their drift checks and TypeScript compilation.

## S02 — Generate and review bounded shots from clean references

**Status** [x] 26 runner/prompt/persistence checks and Ruff pass. Clean-reference starts, reviewed shot cuts, separate costs, retry/extension caps and changed-outfit reference reset are verified.

**Target files**
- `src/tabi/core/flow/shots.py` (new) — shot progress, default plan, reference instructions and clean-cut state compatibility.
- `src/tabi/core/flow/service.py`, `src/tabi/core/flow/runner.py`, `src/tabi/core/flow/prompts.py`, `src/tabi/core/flow/review.py`, `src/tabi/core/flow/media.py` — keyed immutable references, fresh-shot handoff, action/extension limits, motion-only prompts, focused retry corrections and reviewed exact shot trims.
- `tests/unit/test_flow_shot_runner.py` (new), `tests/unit/test_flow_prompts.py`, `tests/unit/test_flow_service.py`, `tests/unit/test_flow_runner.py` — substantive progression, retry/cost/unknown state, backtracking and compatibility tests.
- `docs/progress.md`, `docs/tasks/INDEX.md` — verification evidence.

**Inputs / dependencies**
- S01; reuse existing importer, review packets, assembly and owned worker.

**Implementation rules**
- Keep old explicit recipes usable; expose a new default planned recipe without silently converting saved episodes.
- Require all three keyed clean reference images and confirmed visible starting facts before new shots begin. Keep reference rights pending.
- Save each attempt before handoff; retries use the same clean reference or same accepted in-shot parent. Unknown remote results block another submission.
- Bound accepted extensions per shot, and keep per-action retry/credit limits. Count actual trimmed frames, not nominal Flow duration.
- At every shot boundary require a completed routine, explicit safe cut when needed, and compatible visible cup/hand state. Preview the editorial cut but never instruct Flow to extend the preceding shot.
- Motion prompts omit repeated appearance inventories and rejection paragraphs; store full review notes separately and compile one selected correction.
- Reuse the verified assembler and continuous audio route. No looping, padded frames, new dependency or automatic visual approval.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_shot_runner.py tests/unit/test_flow_prompts.py tests/unit/test_flow_runner.py tests/unit/test_flow_service.py`

## S03 — Guide reference preparation, shot generation and cut review in the app

**Status** [x] Eight API/CLI checks and eight frontend tests pass; 68 schemas, TypeScript, formatting and production build pass. Target-Mac visual checks follow in S04.

**Target files**
- `src/tabi/api/contracts.py`, `src/tabi/api/flow.py`, `src/tabi/cli/flow.py` — expose the same keyed-reference, shot progress, handoff and review services.
- `web/src/flow.ts`, `web/src/flow-state.ts`, `web/src/style.css`, `web/tests/flow-state.test.mjs` — simple shot overview, reference preparation/upload, explicit Start new shot versus Extend, correction choice and cut confirmation.
- `tests/unit/test_flow_shot_api.py` (new), `tests/unit/test_flow_cli.py` — authenticated API and CLI workflow coverage.
- `schemas/web_flow.schema.json`, `web/src/generated/web_flow.ts`, `web/src/generated/validators.cjs` — regenerated transport contracts.
- `docs/progress.md`, `docs/tasks/INDEX.md` — verification evidence.

**Inputs / dependencies**
- S02. Existing browser session security, registered roots, uploads, output player and release handoff.

**Implementation rules**
- New videos default to the six-shot plan. Existing videos retain their actual next step and old workflow.
- Show one reference/action at a time, a compact shot list and measured progress. Keep state/config details collapsible.
- Supply copyable image-preparation instructions and a download of the exact starting reference for each fresh shot.
- Confirm reference cleanliness and observed starting facts, show both sides of a camera cut, and distinguish shot ending from whole-video ending.
- Collect separate checked Flow costs for fresh shots and extensions; record actual model at import. No account connection, API key or new purchase flow.
- No browser timeline semantics or duplicated FFmpeg logic; Python supplies progress, next action, review bounds and reference selection.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 .tools/bin/uv run --frozen pytest tests/unit/test_flow_shot_api.py tests/unit/test_flow_cli.py tests/unit/test_web_flow_contracts.py`

Also run `make schemas`, `npm --prefix web run schemas`, `make web-check` and `make web-build` with the local offline uv cache.

## S04 — Verify complete shot assembly and document the usable workflow

**Status** [x] Five focused media tests; final 344 core and 74 actual-media passes (one optional private-media case skipped), eight frontend tests, build/package and target-Mac Chrome workflow/playback pass. Real creative/automation gates remain open in the evidence.

**Real-media follow-up, 6 October 2026:** [TABI camera-trial evidence](evidence/s04-tabi-camera-trial.json)
records five fresh Quality takes, four complete-take rejections and 500 included credits.
The app exported a separate 14-second trimmed wide/close/wide sample (336 verified frames and
timestamps, six checked boundary frames, full Chrome playback). The 24-second and 20-second
plans remain incomplete; breathing/identity control and continuous exterior progression failed
qualification. Safe range selection required the existing API and needs a normal UI control.
This follow-up changes the creative findings, not the earlier engineering acceptance.

**Target files**
- `src/tabi/core/flow/prompts.py`, `tests/unit/test_flow_prompts.py` — final review fix: mouth corrections must permit the requested sip, with a regression check.
- `tests/integration/test_flow_shot_workflow.py` (new) — real 90-second synthetic media through authenticated API, independent shot references, retry/reopen, exact cuts, soundtrack and verified export.
- `tests/integration/test_flow_workflow.py` — retain the existing continuous-shot regression with its explicit legacy recipe now that new videos use planned shots.
- `docs/evidence/s04-planned-shots.json` (new), `docs/evidence/s04-shot-workflow.jpg` (new) — bounded target-Mac UI and export evidence.
- `PLAN.md`, `docs/37-operations.md`, `docs/38-v1-acceptance.md`, `docs/progress.md`, `docs/tasks/INDEX.md` — current defaults, operations and remaining real creative/automation gates.

**Inputs / dependencies**
- S03; installed FFmpeg and browser. Use small synthetic fixtures and preserve original Tokyo media.

**Implementation rules**
- Render and strictly verify all 2160 frames, PTS, shot boundaries and continuous soundtrack through the existing app services. No external credits required for engineering acceptance.
- Verify old local Tokyo episode/export documents still load with their hashes; do not mutate them.
- Exercise the new reference/shot/cut UI on the target Mac, reopen saved progress, play a verified output and save a screenshot.
- Keep real TABI wide/close/wide quality, 90-second creative acceptance and unattended Flow control open until actually demonstrated.
- Complete the broader repository gates, preserve unrelated staged changes, and never commit MP4s.

**Verification command**
`UV_CACHE_DIR=.local/uv-cache UV_OFFLINE=1 TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/integration/test_flow_shot_workflow.py tests/integration/test_flow_assembly.py tests/integration/test_flow_release.py`

Final gates: `make check`, `make web-check`, `make web-build`, `make package` and target-Mac `make test-media` with the same offline cache/config environment.

---

The following F/P/T plan is retained implementation history. Its open creative gates are not
additional engineering tasks and do not block S01–S04.

# Flow generation and review workflow in video-story

Plan prepared 6 October 2026. Add a guided, resumable cycle that prepares one Flow prompt,
imports and reviews its result, continues from the accepted parent, and exports the requested
duration with local music and release checks. The loop advances the story; it does not repeat
old footage to fill the duration.

## First working version: one simple train workflow

Marco's priority, confirmed 6 October 2026: **keep it as simple as possible and make the
workflow work from start to finish**. The initial experience opens on the saved TABI train /
Tokyo / 90-second preset, with the existing character references, a fixed camera, continuous
outside travel and the calm action routine below. Reuse those defaults on the next video.

The normal path is **Start video → Copy prompt / Open Flow → Import and review → Export**.
After each accepted clip, prepare the next focused prompt and show the measured progress toward
90 seconds. At review, show one candidate and its join to the previous clip; keep Accept and
Retry clear, with a specific reason if progress needs attention. Save progress automatically.
Show one recommended next action at a time. Advanced parameters remain optional.

Prove import, join playback and export with the existing Tokyo 8/7/7-second clips first, then
complete a fresh 90-second train video through the same app path. The earlier combined scene's
timestamp gap must not reappear; visual defects still require review. Completion means a usable
video produced through the UI, without per-video scripts, JSON edits or manual timeline repair.

Keep the implementation focused on that path. A general recipe editor, preset gallery, custom
Flow Tool, additional provider and automatic visual critic are not prerequisites. New interiors,
outfits, café and walking remain later variations after the train workflow passes. Music stays
optional at Finish; music polishing is deferred. Reuse existing security, media verification
and release checks. The F tasks below describe the supporting work, not extra screens or
settings the user must navigate.

## Flow implementation scope and decision

**Feasible now:** Python can own the recipe, observed prop/pose state, focused prompts,
continuation history, technical checks, bounded retries, measured duration and local export.
The first usable app version has four steps: **Setup → Opening → Continue → Finish**.
Generation initially has an honest **Open Flow / Copy prompt / Import result** handoff.

**Separate feasibility gate:** direct, unattended control of Flow from this local application
is unverified. Google's current [Flow Agent](https://support.google.com/flow/answer/17093911?hl=en)
can use project instructions, reference media and generation defaults. Its media consumes Flow
credits; conversational requests have a daily quota. Google also documents
[reusable Tools](https://support.google.com/flow/answer/17104535?hl=en) built inside Flow.
Neither document establishes an external API, native Extend support inside a custom Tool,
reliable parent selection, callback/download integration or an enforceable credit cap.
F00 tests those boundaries before a direct connector is specified. The browser capabilities
available to an assistant in this chat are not automatically part of the installed app.

Read-only account check on 6 October 2026: the selected TABI project exposes an **Agent** switch
(off) and **Tools → My creations → Create new**. The generation controls displayed Video,
720p, 8s and x1. No generation was submitted and no setting was changed. This establishes UI
availability only; native continuation from a Tool and app integration remain untested. Keep
F00 bounded so that this investigation does not delay the assisted import/review/export path.

The official [Veo API pricing](https://ai.google.dev/gemini-api/docs/pricing) lists video
generation on a paid tier. The [API billing model](https://ai.google.dev/gemini-api/docs/billing)
does not establish coverage by Marco's consumer Flow allowance. Do not substitute an API key,
Cloud billing, paid vision reviewer, subscription or top-up for the existing entitlement.
Do not make an undocumented private endpoint or extracted browser credential a product dependency.

F00 qualified the assisted route; F01–F11 are implemented and committed. F12 records
engineering acceptance with real creative/variation and unattended-control gates kept open.
The earlier P/T records are historical and do not form a second active implementation queue.
Each verified change is recorded in `docs/progress.md` and `docs/tasks/INDEX.md`.

### Prompt and state policy

The [Google guidance](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/best-practice),
checked 6 October 2026, recommends one focused moment per short clip and motion-focused prompts
when a source image already supplies appearance. It separately recommends stable identity
descriptions across new scenes. Apply those as different prompt modes, not a single long block:

| Situation | Prompt produced by Python |
| --- | --- |
| New scene from text/references | Stable TABI identity and selected outfit, setting, camera and actual intended props; one opening action |
| Animate an approved opening image | Subject motion and environmental motion; do not redundantly redesign the supplied image |
| Native continuation | Current observed pose/prop state, one next action, ongoing camera/exterior constraints and a compatible ending state |
| Retry | Same clean parent and beat, one targeted correction; never append contradictory old action blocks |

Applying image-to-video motion guidance to native Extend is our design recommendation, not a
Google guarantee. Do not expose a seed or any other control unless the chosen live Flow mode
actually supports it. Preserve the reference hashes and compare each candidate to both the
original reference and the immediate parent; a late frame must not become the new identity.

The accepted opening establishes the actual prop inventory. Desired and observed state are
separate: a requested white cup does not override an observed takeaway cup. An action template
requiring a handle or saucer is incompatible when those objects are absent. During pickup,
the moving hands cannot also be required to stay on the lap. A sip, cup return, music sway and
district transition are separate beats. Gentle breathing and existing scenery motion can
continue under a beat. Requested ending state is only confirmed after reviewing actual footage.

### Default behavior and stop conditions

| Choice | Proposed default |
| --- | --- |
| Episode | 90 seconds, 16:9; train/Tokyo recipe saved for reuse |
| Picture | Native 720p review, preserve measured frame rate; 24/1 only for the tested sources |
| Provider | Eligible eight-second Veo opening and native Lite Extend, subject to current capability/cost checks |
| Routine | Breathing and window rest; look near 15s, cup sequence near 30s, sway near 45s, look near 60s, larger breath near 75s |
| Beat timing | Approximate targets; show actual placement and any shift needed to finish an action |
| Generation | One candidate at a time; one focused retry per failed beat, then Needs attention |
| Review | Technical checks automatic; Accept / Retry / Stop for appearance; no automatic visual approval from passing media checks |
| Credit budget | Required per-run ceiling within a freshly checked remaining allowance; reserve in-flight estimates; no top-ups |
| Sound | Silent visual draft; add the selected local master at Finish when requested |
| Output | Exact approved frame range, H.264 MP4; AAC stereo 48 kHz if audio is selected; preserve native resolution unless scaling is explicitly chosen |

Google's [current feature matrix](https://support.google.com/flow/answer/16352836?hl=en) permits
native extension of eligible eight-second Veo sources using Lite; Omni extension is listed as
coming soon. Record the actual source mode/model instead of inferring it from the current editor
badge. Costs and capabilities are dated observations, not permanent constants.

The measured trial added seven actual seconds per extension. If that remains true, one opening
plus twelve accepted extensions yields 92 seconds, from which a reviewed quiet ending can be
trimmed to 90. This is an estimate, not a fixed clip count or credit promise. Progress is the sum
of accepted, usable frames only. Rejected candidates and nominal eight-second slots do not count.
Stop at the target, budget/retry limit, unknown submission result, lost access or unresolved
continuity. A completed action takes priority over blindly cutting at the duration target.

### Repository boundaries inspected

- `src/tabi/core/assets/probe.py` already counts decoded frames and checks every timestamp;
  it rejects variable/inconsistent schedules. Retain that strict importer. The Tokyo scene
  download requires diagnosed preparation or individual clips, not a relaxed validation rule.
- `src/tabi/core/generation.py` and `src/tabi/api/generation.py` implement a loopback ComfyUI
  still-image adapter. Flow needs its own typed workflow; do not reinterpret this adapter.
- `src/tabi/core/jobs/service.py` and `src/tabi/core/render/assembly.py` are bound to compiled
  layered episodes and verified render chunks. Extract only useful media primitives; introduce
  an explicit complete-scene sequence and export record rather than fabricating an ActionPack.
- `src/tabi/core/publishing.py` currently resolves a layered render job. Add a verified Flow
  export source adapter while retaining its rights, hash-bound review and public/private rules.
- `src/tabi/api/runtime.py` owns one render lane. New local Flow preparation/export work must
  share its ownership/cancellation rules. Waiting for a remote generation must not occupy it.
- `web/src/main.ts` exposes tool pages. The new workflow should have one next action and a
  visible accepted-duration bar; advanced tools remain accessible without dominating the flow.

## F00 — Qualify Flow's supported execution path

**Status** [x] Complete: assisted route qualified by the dated zero-credit review; automatic execution remains unqualified. See `docs/evidence/f00-flow-execution.json`.

**Target files**
- `docs/evidence/f00-flow-execution.json` (new) — dated capabilities, terms, measurements and go/no-go evidence.
- `docs/tasks.md` — record the supported handoff and, only if qualified, specify a connector task.
- `docs/tasks/INDEX.md` — register the Flow queue and its provider dependency at implementation start.
- `docs/progress.md` — record what was actually tested and what remains unavailable.

**Inputs / dependencies**
- Existing Flow account and selected TABI project; no app implementation dependency.
- For any generation, a concrete trial authorization and included-credit ceiling; this plan
  itself does not spend credits. Reuse session authorization when it already covers the test.

**Implementation rules**
- Check availability of native Agent/project instructions/Tools, permitted automation and exact
  provider/output terms. Record review date, displayed model, official URLs, attribution and
  unresolved rights. Reuse existing licence evidence only where its scope still matches.
- Test at most four candidates within the agreed cap: an opening, two serial accepted
  continuations and one rejected attempt. Test explicit parent selection, result identity,
  native download and resume after an interrupted handoff. Do not generate dependent clips
  as independent batch variations.
- Establish whether a Tool can extend the chosen parent and return durable output references.
  UI documentation alone is not success. A credit limit written in a prompt is not an
  enforceable budget. Leave global generation-confirmation settings unchanged in this trial.
- Qualify external control only if its supported interface, authentication, result reconciliation,
  download and spending boundaries are demonstrated. Do not call private endpoints or extract
  cookies. If none qualifies, record assisted handoff as usable and full automation as unresolved.
- Keep account authentication in Flow. No private music upload, public Tool sharing or purchase.
  No model, quota or payment fallback on failure. A zero-credit review may finish with a
  documented unverified capability; it cannot mark automatic execution qualified.

**Verification command**
`.tools/bin/uv run --frozen python -m json.tool docs/evidence/f00-flow-execution.json`

Additionally inspect the actual saved parent/result IDs, source hashes, downloaded frame counts,
observed allowance delta and UI evidence. A valid JSON file is not evidence that the bridge works.

## F01 — Define strict Flow episode and execution contracts

**Status** [x] Complete. Strict contracts and generated browser schemas verified: 73 Python tests, schema drift and web checks pass.

**Target files**
- `src/tabi/core/models/flow.py` (new) — FlowEpisode, FlowAttempt and FlowExport documents with nested recipe, beat, candidate, state, review, limits and frozen export inputs.
- `src/tabi/core/models/__init__.py` — register the new documents without changing existing types.
- `schemas/flow_episode.schema.json` (new), `schemas/flow_attempt.schema.json` (new), `schemas/flow_export.schema.json` (new) — generated schema contracts.
- `web/src/generated/flow_episode.ts` (new), `web/src/generated/flow_attempt.ts` (new), `web/src/generated/flow_export.ts` (new) — generated browser types.
- `web/src/generated/documents.ts`, `web/src/generated/validators.cjs`, `web/src/generated/validators.d.cts` — regenerated registries.
- `tests/unit/test_flow_contracts.py` (new) — substantive invalid-state and compatibility cases.
- `tests/unit/test_contracts.py` — extend the existing closed document-registry assertion.

**Inputs / dependencies**
- Existing Model/DraftDocument/AssetRef/HashedFile/FrameRate/TrackPlacement/OutputProfile contracts.
- No F00 result needed for the assisted route; provider capability remains explicit and unverified.

**Implementation rules**
- Use integer frames and samples, reduced rational fps, content hashes and normalized media paths.
  Reject unknown fields, unsupported versions, cycles, missing parents and invalid intervals.
- Store immutable reference locks, desired recipe, confirmed observed inventory/pose, one beat
  type, prompt/version/hash, provider scene/clip references and exact result association.
  External URLs are context only, never trusted filesystem paths or executable instructions.
- Candidate acceptance binds media hash, parent hash, reviewed frame range and observed ending
  state. Requested state cannot masquerade as observed state. Preserve rejected branches.
- Attempts distinguish prepared, awaiting external action, submitted, unknown, received and
  failed. Exports distinguish queued/running/interrupted/failed/verified and bind immutable
  ordered source trims, audio placements, profile and pipeline/toolchain fingerprints.
- Model safe final trim ranges, unresolved beats, review decisions and reserved/observed credit
  units explicitly. Local technical verification is distinct from creative and release approval.

**Verification command**
`.tools/bin/uv run --frozen pytest tests/unit/test_flow_contracts.py tests/unit/test_contracts.py`

Regenerate with `make schemas` and `npm --prefix web run schemas`; verify with
`.tools/bin/uv run --frozen python scripts/export_schemas.py --check` and `make web-check`.

## F02 — Persist resumable sequences and accepted branches

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/flow/__init__.py` (new), `src/tabi/core/flow/service.py` (new) — shared episode, attempt, branch and frozen-export storage operations.
- `src/tabi/core/persistence.py` — explicit Flow document paths and immutable export-input storage.
- `tests/unit/test_flow_service.py` (new) — revisions, crash boundaries, stale hashes and branch changes.

**Inputs / dependencies**
- F01; ProjectStore atomic writes, locks, backups and immutable asset registry.

**Implementation rules**
- Create/read/save/clone Flow drafts using expected revisions. Clone settings and references,
  never approval, credit receipts or accepted clip state for a different episode.
- Accept only the exact reviewed candidate under its matching active parent. A concurrent edit,
  replaced source or stale review refuses the transition. Keep append-only decision/attempt
  evidence and reconstructible draft state; do not introduce a database or distributed queue.
- Replacing an earlier accepted clip creates a branch. Old descendants remain available but
  are excluded from progress/export until continuity is explicitly reviewed or regenerated.
- Frozen export inputs never follow subsequent recipe edits. Preserve prior snapshots and
  outputs. Add document dispatch without weakening old ProjectStore immutability or migrations.

**Verification command**
`.tools/bin/uv run --frozen pytest tests/unit/test_flow_service.py tests/unit/test_persistence.py`

## F03 — Compile focused prompts from confirmed state

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/flow/prompts.py` (new) — deterministic prompt modes and compatible action templates.
- `src/tabi/core/flow/service.py` — produce the next prompt with its parent/state/template hashes.
- `tests/unit/test_flow_prompts.py` (new) — missing props, contradictory hands, mode selection and carried scenery.

**Inputs / dependencies**
- F01, F02; the prompt/state policy above and confirmed opening inventory.

**Implementation rules**
- Support text/reference opening, approved-image motion and native continuation separately.
  Store the stable identity specification; include detailed appearance where appropriate for a
  new scene, and concise motion/state instructions for conditioned continuation.
- Compile one typed action or district transition. Validate its prerequisites and intended
  postcondition. Breathing and existing exterior travel remain ongoing background behavior.
- Select cup interaction from actual cup type and ownership. Never request a nonexistent
  handle/saucer, reset a held cup to the table, or add hands-on-lap to a reaching/sipping beat.
- Reject incompatible free-text overrides with an explanation; overrides cannot silently
  bypass typed state rules. Do not claim a text linter detects every semantic contradiction.
- Keep the existing district until a transition is scheduled. Store retry reasons and generate
  one targeted correction against the clean parent. No paid LLM or new local weights required.
- Do not silently remove user-requested actions; report an incompatible action or unresolved
  inventory. Editing a prompt after submission creates a new attempt rather than rewriting it.

**Verification command**
`.tools/bin/uv run --frozen pytest tests/unit/test_flow_prompts.py tests/unit/test_flow_service.py`

## F04 — Import native results with measured timing and lineage

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/flow/media.py` (new) — source inspection, bounded preparation and candidate registration.
- `src/tabi/core/flow/service.py` — associate one imported candidate with the exact pending attempt.
- `tests/integration/test_flow_import.py` (new) — actual-media source preservation and timestamp cases.

**Inputs / dependencies**
- F01, F02; AssetService, probe_media, digest_file and registered-root/upload staging boundaries.

**Implementation rules**
- Default to separate native clips. Detect whether an input is a new segment or a cumulative
  scene download; ambiguous cases require an explicit source range/association before progress.
  A filename or download time alone cannot establish the parent or accepted order.
- Fully decode, measure frames/fps/dimensions/PTS and hash before registration. Copy originals
  immutably; distinguish raw source and any prepared derivative with a mapping and recipe hash.
- Retain strict AssetService import. A diagnosed timestamp-gap correction is explicit preparation
  that writes a new version. Do not compress genuine variable-speed footage or discard frozen
  content automatically. Prefer requesting native segments when a combined download is unclear.
- Generate hash-bound first/last and seam review images. Reject partial files, changed sources,
  unexpected fps/aspect or content duplicates presented as a new continuation. Technical import
  never confers creative approval or commercial rights.

**Verification command**
`TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/integration/test_flow_import.py tests/integration/test_asset_import.py`

Use small generated fixtures that reproduce the 192/168/168-frame sequence and missing PTS at
the second join. Do not commit the Tokyo MP4s or use copyrighted media as CI fixtures.

## F05 — Review technical defects and visual continuity separately

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/flow/review.py` (new) — measured diagnostics, review packet and hash-bound decisions.
- `src/tabi/core/flow/service.py` — guarded Accept/Retry transitions and confirmed ending state.
- `tests/unit/test_flow_review.py` (new), `tests/integration/test_flow_review_media.py` (new) — stale review, joins, holds and source-state cases.

**Inputs / dependencies**
- F02, F04; original identity/reference locks and immediate accepted parent.

**Implementation rules**
- Hard-fail corrupt/truncated media and incompatible time/canvas contracts. Flag long repeated
  frames, unexpected cuts and suspicious seam differences as diagnostics with exact frame ranges.
  Distinguish a missing timestamp interval from duplicates already encoded in the video.
- Stillness is not automatically a defect. Use a confirmed window region when evaluating
  exterior motion; missing region or ambiguous motion leaves the result unassessed.
- Present parent ending → candidate beginning, full candidate playback, source reference and
  relevant samples for eyes/mouth/gills, hands/cup, book/bag, camera and scenery continuity.
- Check requested action completion and record actual final pose, hand occupancy and prop
  positions. A model's stated intent or a pass from FFmpeg cannot supply these facts.
- Initially require a human Accept/Retry for appearance. A future vision reviewer must be
  separately qualified for missed ear/prop defects, terms, privacy and available allowance.
  Treat its findings as advisory until measured evidence supports a narrower automatic policy.

**Verification command**
`.tools/bin/uv run --frozen pytest tests/unit/test_flow_review.py tests/unit/test_flow_service.py`

`TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/integration/test_flow_review_media.py`

## F06 — Advance the bounded generation and review cycle

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/flow/runner.py` (new) — next-step decision, progress, retry accounting and recovery.
- `src/tabi/core/flow/service.py` — persisted attempt transitions and idempotent result association.
- `tests/unit/test_flow_runner.py` (new) — target completion, failure recovery, credits and uncertain submissions.

**Inputs / dependencies**
- F02, F03, F04, F05; concrete per-run limits and observed provider capability.
- A direct provider adapter is not assumed. Assisted mode uses externally completed requests.

**Implementation rules**
- Compute progress and next beat in Python from the active accepted branch's usable frames.
  Plan one continuation, then wait for its result and review. Never batch dependent clips.
- Persist an attempt ID and prompt/parent/configuration hash before an external submission.
  Reopening or refreshing resumes the existing attempt; it cannot trigger another generation.
  Unknown outcomes require reconciliation, not an automatic duplicate request.
- Use one focused retry per failed beat by default. Retry from the last accepted parent;
  after exhaustion expose Needs attention with the evidence and simpler-action/stop choices.
  Fix local import/timing failures locally before proposing another credit-consuming generation.
- Reserve estimated credits for in-flight attempts; reconcile observed costs/refunds instead
  of assuming them. Block the next request if the remaining run/account allowance is unknown
  or insufficient. Changing model/cost requires updating the observation before continuation.
- Finish when accepted footage covers the target and all required beats have a reviewed ending.
  Trim only an approved quiet tail; insufficient safe coverage plans another rest continuation
  within limits. No repetition, reversal, speed change or interpolated filler by default.
- Keep Pause/Resume/Stop durable. Pausing local orchestration does not claim to cancel a remote
  generation. Do not turn on recurring background runs or change Flow's global permissions.

**Verification command**
`.tools/bin/uv run --frozen pytest tests/unit/test_flow_runner.py tests/unit/test_flow_service.py`

Test unknown response followed by late import, stale-parent completion, repeated receipt,
rejected branches excluded from duration, 92s to safe 90s trim, unfinished sip, and budget exhaustion.

## F07 — Assemble a verified silent video from accepted footage

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/flow/assembly.py` (new) — frozen complete-scene export preparation and verification.
- `src/tabi/core/render/assembly.py` — extract reusable verified video concat primitives while retaining the existing renderer behavior.
- `src/tabi/core/flow/service.py` — immutable export-input publication and verified output records.
- `tests/integration/test_flow_assembly.py` (new) — exact duration, PTS, trims, failures and source preservation.

**Inputs / dependencies**
- F04, F05, F06; existing OutputProfile, verify_video, run_tool and atomic publication helpers.

**Implementation rules**
- Freeze ordered source hashes, reviewed half-open trims, frame rate, profile and target frames.
  Reject obsolete branches and source changes. Generate video-only prepared chunks with global
  contiguous timestamps, then reuse extracted concat/verification primitives.
- Extract bounded media functions, not a second general timeline engine. Do not construct fake
  layered CompiledSnapshots or expose complete-scene footage as transparent character actions.
- Verify exact frame order/count, rational cadence, every PTS, dimensions and full decode before
  atomic publication. Record re-encoding, scaling and source color preparation explicitly.
- Retain native resolution by default. An explicit 1080p upscale of 720p footage must be labeled
  as scaling, not recovered detail. Keep source rates; do not force 30fps for the YouTube preset.
- Preserve cancellation checkpoints, source hashes, unique output paths, owned temporary files
  and subprocess argument arrays. Keep every MP4 out of Git.

**Verification command**
`TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/integration/test_flow_assembly.py tests/integration/test_chunk_assembly.py`

Include 8+7+7 → 22s without a hold, safe end trim, fractional fps, Unicode paths, altered source,
failed verification and comparison samples on both sides of every join.

## F08 — Add one continuous local soundtrack at Finish

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/audio/mix.py` — extract shared locked-track mixing entry point from layered snapshot orchestration.
- `src/tabi/core/flow/assembly.py` — selected local audio placements, one final AAC mux and verification.
- `tests/integration/test_flow_audio.py` (new) — exact samples, audio joins, source hashes and silent mode.

**Inputs / dependencies**
- F07; existing TrackPlacement, PCM preparation, mixer, loudness diagnostics and mux_aac.

**Implementation rules**
- Refactor only the shared audio-input boundary; keep existing AudioMixer behavior and frozen
  asset validation. Use the Flow export's locked local TrackPlacements and exact sample interval.
- Music is optional during visual work and selected explicitly at Finish. Keep masters local
  and unchanged. Do not infer rights from a file path or upload audio to Flow.
- Show any duration mismatch and require a recorded trim/duration choice. Do not automatically
  stretch or repeat a song, add fades, remaster it or replace it with generated audio.
- Assemble continuous PCM and encode AAC once, not per clip. Verify exact intended samples,
  clipping diagnostics and final A/V duration. A silent draft remains labeled as such.

**Verification command**
`TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/integration/test_flow_audio.py tests/integration/test_audio_mix.py tests/integration/test_chunk_assembly.py`

## F09 — Expose Flow workflow services through CLI and authenticated API

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/api/flow.py` (new), `src/tabi/cli/flow.py` (new) — thin adapters over shared Flow services.
- `src/tabi/api/app.py`, `src/tabi/api/runtime.py`, `src/tabi/api/files.py`, `src/tabi/api/contracts.py`, `src/tabi/cli/main.py` — routing, one owned local work lane and authenticated artifacts.
- `src/tabi/core/flow/service.py`, `src/tabi/core/flow/assembly.py` — shared export discovery, recovery and cancellation ownership.
- `schemas/web_flow.schema.json` (new), `web/src/generated/web_flow.ts` (new) — generated next-step/status DTO.
- `web/src/generated/documents.ts`, `web/src/generated/validators.cjs`, `web/src/generated/validators.d.cts` — regenerated registries.
- `tests/unit/test_web_flow_contracts.py` (new), `tests/unit/test_flow_cli.py` (new), `tests/integration/test_web_flow.py` (new) — parity, security and real-media recovery.

**Inputs / dependencies**
- F01–F08; existing worker, upload, session, filesystem and cancellation contracts.

**Implementation rules**
- Expose create/clone, prompt, import, inspect, review, next-step, pause/resume and export using
  IDs/hashes/revisions. WebFlow returns one recommended action and factual progress; TypeScript
  does not determine the next beat, count usable frames or produce media commands.
- Schedule local inspection/export on the existing owned worker lane with explicit Flow job
  dispatch. Persist current state before work; recover interrupted exports without adopting
  unrelated PIDs or repeating external submissions. Waiting on Flow/review releases the lane.
- Stream hash-verified clip/review/export media through authenticated range endpoints. Preserve
  Host/Origin, CSRF, session expiry, root restrictions, bounded uploads and cancellation ownership.
- Opening Flow is a user-driven link. No arbitrary server-side URL fetch, credential import,
  public callback, wildcard CORS or permission for a Flow Tool to call the local service.
- Add schema drift checks and maintain old CLI/API behavior. Export remains available when Flow
  is offline. Track verified local work separately from external work with unknown progress.

**Verification command**
`.tools/bin/uv run --frozen pytest tests/unit/test_web_flow_contracts.py tests/unit/test_flow_cli.py tests/unit/test_web_service.py`

`TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/integration/test_web_flow.py tests/integration/test_web_worker.py`

## F10 — Present Setup, Opening, Continue and Finish as the normal UI

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `web/src/flow.ts` (new), `web/src/flow-state.ts` (new) — guided pages and request/reconnect state only.
- `web/src/main.ts`, `web/src/wireframes.ts`, `web/src/style.css` — navigation and workflow layout.
- `web/src/session.ts`, `web/src/workspace.ts` — default landing screen and saved-project handoff.
- `docs/evidence/f10-flow-ui.json`, `docs/evidence/f10-flow-finish.jpg`, `docs/evidence/f10-flow-playback.jpg` (new) — target-Mac guided workflow evidence.
- `web/src/contracts.ts` — use the generated Flow DTO in existing validation dispatch.
- `src/tabi/api/flow.py`, `src/tabi/api/contracts.py`, `schemas/web_flow.schema.json`, `web/src/generated/web_flow.ts`, `web/src/generated/validators.cjs` — expose the Python preset and remaining routine for the guided screen.
- `web/tests/flow-state.test.mjs` (new) — stale requests, reconnect and repeated clicks.

**Inputs / dependencies**
- F09; current local app session, chooser/upload and media controls.

**Implementation rules**
- New video opens on the saved train/Tokyo/90s/calm preset and displays its character reference.
  Starting with the defaults does not require choosing a setting, outfit, duration or routine
  again. Put changes behind an optional Edit settings control; fps, codec and IDs stay under
  Advanced. Existing projects remain accessible. A saved variation starts with new reviews
  rather than copying approval.
- Opening shows its actual reference and a compact editable inventory. Continue shows parent,
  next action, accepted duration, remaining beats and one candidate with Accept / Retry / Stop.
  Surface unresolved facts; do not make a screen of technical configuration mandatory.
- Assisted mode explicitly shows Copy prompt, Open Flow and Import result. Display Waiting for
  Flow rather than a fake in-app Generate button. A direct automation control stays absent until
  an F00-qualified connector is implemented and verified.
- Finish offers full playback, optional local music and export. Show retry/credit consumption
  and real job state. Preserve browser refresh recovery and suppress duplicate submissions.
- Plain-language warnings distinguish technical failure, visual retry and pending final review.
  No manual JSON, terminal or per-frame repair is part of the normal journey. Keyboard access,
  focus, clear error recovery and mobile-width layout must remain usable.

**Verification command**
`make web-check` and `make web-build`

On the target Mac, complete the four steps against a running worker with actual synthetic clips,
including stale-tab acceptance, rejected candidate, reconnect and export playback; save UI evidence.

## F11 — Prepare a YouTube delivery with existing review rules

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/models/publishing.py` — explicit Flow/render export source selection preserving legacy serialization.
- `src/tabi/core/publishing.py` — verified Flow source adapter and shared readiness/bundle logic.
- `src/tabi/api/release.py`, `web/src/release.ts`, `web/src/flow.ts`, `web/src/main.ts` — Finish-to-release handoff without expanding advanced navigation.
- `docs/evidence/f11-flow-delivery.json` (new) — current official guidance and target-Mac source handoff evidence.
- `src/tabi/api/contracts.py` — expose verified Flow exports in the shared release chooser.
- `schemas/release_inspection.schema.json`, `schemas/release_bundle_report.schema.json`, `web/src/generated/release_inspection.ts`, `web/src/generated/release_bundle_report.ts` — nested preparation contract regeneration.
- `schemas/release_preparation.schema.json`, `schemas/web_releases.schema.json`, `web/src/generated/release_preparation.ts`, `web/src/generated/web_releases.ts`, `web/src/generated/documents.ts`, `web/src/generated/validators.cjs`, `web/src/generated/validators.d.cts` — regenerated contracts.
- `tests/unit/test_flow_release_contracts.py` (new), `tests/integration/test_flow_release.py` (new) — source verification, hash-bound reviews and private data boundaries.

**Inputs / dependencies**
- F08, F09, F10; existing release inspection/public allowlist/review_status behavior.

**Implementation rules**
- Add a source-kind field defaulting to the current layered render, excluded from serialization
  at that default so existing hashes remain stable. For Flow, resolve a verified FlowExport and
  its immutable inputs instead of fabricating a JobService/CompiledSnapshot record.
- Reuse the same technically verified → creatively reviewed → rights reviewed → ready for
  manual upload progression. Check every used visual/reference/audio dependency, actual model
  and dated commercial-use evidence. Unknown facts remain pending; stale hashes invalidate review.
- Export MP4 and selected local soundtrack, factual metadata/credits, an approved thumbnail if
  supplied and private preparation evidence. Prompt history, credentials and filesystem paths
  cannot leak into public files. Do not invent licences, music IDs or publication permission.
- Match the [YouTube encoding guidance](https://support.google.com/youtube/answer/1722171?hl=en):
  native cadence, progressive H.264/4:2:0, fast-start MP4 and 48kHz stereo AAC when audio is used.
  Report source quality honestly; a 720p export can be uploaded without pretending it is 1080p.
- Commercial-use permission and technical upload readiness do not establish monetization.
  YouTube's [channel policy](https://support.google.com/youtube/answer/1311392?hl=en) evaluates
  originality and substantive variation. Reusing a production tool does not justify releasing
  interchangeable episodes. Keep a distinct episode concept/routine review; do not promise YPP.
- Manual upload remains the final external step. No automatic publishing or monetization badge.

**Verification command**
`.tools/bin/uv run --frozen pytest tests/unit/test_flow_release_contracts.py tests/unit/test_publishing.py`

`TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/integration/test_flow_release.py tests/integration/test_release_export.py tests/integration/test_web_release.py`

Also run `make schemas`, `npm --prefix web run schemas` and `make web-check` after contract changes.

## F12 — Verify repeatable production and document the remaining automation gap

**Status** [x] Engineering implementation and assisted-workflow regression complete.
**Real acceptance** [ ] Train/variation creative review, measured human effort and unattended Flow control remain open; see `docs/evidence/f12-flow-workflow.json`.

The [real Tokyo trial](evidence/f12-tokyo-real-trial.json) reached 22 accepted seconds and
stopped after a failed particle/mouth correction. Its separately shortened, silent preview
was exported and played through the app. The 90-second target is preserved; this trial does
not close full-length or variation acceptance.

**Target files**
- `tests/integration/test_flow_workflow.py` (new) — complete assisted workflow and interruption regression.
- `tests/unit/test_flow_release.py` → `tests/unit/test_flow_release_contracts.py`, `tests/unit/test_web_flow.py` → `tests/unit/test_web_flow_contracts.py`, `pyproject.toml` — avoid unit/integration collection collisions and make repository test helpers importable in the full gate.
- `src/tabi/core/publishing.py` — correct soundtrack lock access exposed by the full-length music-to-delivery regression.
- `docs/evidence/f12-flow-workflow.json` (new) — measured synthetic/real journeys and remaining limits.
- `docs/evidence/f12-flow-finish.jpg`, `docs/evidence/f12-flow-mobile.jpg` (new) — target-Mac full-length playback and narrow-layout observations.
- `docs/37-operations.md`, `docs/38-v1-acceptance.md`, `docs/progress.md`, `docs/tasks/INDEX.md`, `PLAN.md` — verified operations, current queue and honest production status.

**Inputs / dependencies**
- F01–F11. F00's actual outcome determines assisted versus automatically controlled generation;
  an unresolved connector does not block honest assisted-mode engineering acceptance.
- Real creative acceptance uses approved sources and separately authorized Flow allowance.

**Implementation rules**
- From a fresh project, use the UI to import synthetic opening/continuations, review a failure,
  retry, reopen the app, reach exactly 90 seconds, add test audio and export a labeled draft.
  Verify all frames/PTS/samples and every join; assert no synthetic production approval.
- Run the actual Tokyo 8/7/7-second import as local evidence: 528 frames/22s with no inherited
  one-second hold, and the saucer defect still flagged for review. Preserve original files.
- Qualify one real 90-second train episode, then a second with a changed setting/outfit recipe.
  Record review effort, rejected generations, actual credits, time and source rights. The second
  is a fresh opening from stable identity references, not a late drifted frame from the first.
- View the entire output for character/prop/scenery continuity and listen after music is added.
  A passing test suite cannot close this gate. Café and walking require separate visual trials.
- State clearly whether generation was manual, assistant-operated or app-controlled. A human
  clicking Flow successfully does not prove unattended app control. If F00 fails, preserve the
  usable assisted workflow and report the unmet almost-automatic requirement without paid fallback.
- Preserve unrelated staged work and old projects. Commit each verified step using its F-task ID.
  No MP4 enters Git. Update the task index as each behavior actually becomes usable.

**Verification command**
`TABI_CONFIG=examples/settings.macos.toml .tools/bin/uv run --frozen pytest --run-media tests/integration/test_flow_workflow.py`

Final milestone gates: `make check`, `make web-check`, `make web-build`, `make package` and
`TABI_CONFIG=examples/settings.macos.toml make test-media`, followed by the documented target-Mac
journeys and real-art review. Do not claim the almost-automatic production target achieved until
generation control, visual quality and observed human effort all meet it.

## F13 — Retire unused routes and reduce the tracked repository

**Status** [x] Complete. Evidence recorded in `docs/progress.md`.

**Target files**
- `src/tabi/core/generation.py`, `src/tabi/api/generation.py`, `src/tabi/cli/generation.py`, `web/src/generation.ts` — remove the unqualified optional ComfyUI execution bridge.
- `src/tabi/api/app.py`, `src/tabi/cli/main.py`, `web/src/production.ts` — remove its registration and settings controls; retain legacy document schemas/preferences for existing projects.
- `web/src/playback.ts`, `scripts/web_playback_spike.py`, `tests/unit/test_browser_ranges.py` — remove the replaced standalone browser experiment.
- `tests/unit/test_generation.py`, `tests/integration/test_generation_offline.py` — retire tests of the removed bridge; existing shared renderer/worker regressions remain.
- `.gitignore`, `docs/assets/README.md` (new), `docs/evidence/f13-local-media-inventory.json` (new) — local media preservation and scoped index exclusions.
- `docs/assets/tabi-assets/train-actions/breath/`, `docs/assets/tabi-assets/train-actions/drink/`, `docs/assets/tabi-assets/train-actions/walking/`, `docs/assets/tabi-assets/outfits/`, `docs/assets/tabi-assets/emotions/`, `docs/assets/scenario/tokyo-scenario/` — remove from the Git index only; preserve every local byte and record hashes.
- `README.md`, `docs/README.md`, `docs/05-webapp.md`, `docs/24-browser-foundation.md`, `docs/35-local-generation.md`, `docs/37-operations.md`, `docs/38-v1-acceptance.md`, `PLAN.md` — current workflow and retired-route guidance.
- `docs/archive/pre-flow-plan.md`, `docs/archive/production-progress.md`, `docs/archive/local-generation.md` (new), `docs/tasks.md`, `docs/tasks/INDEX.md`, `docs/progress.md` — archive superseded proposals/history, preserve historical link anchors and record this task.
- `docs/evidence/f13-repository-cleanup.json` (new) — tracked-tree size, source preservation, retired routes and final verification.

**Inputs / dependencies**
- F00–F11 and F12's passed engineering gate; the open real-art/control trials remain independent.
- User explicitly authorizes obsolete/legacy removal and asks for a small repository.

**Implementation rules**
- Preserve selected static references, source artwork locally, immutable projects, licences and relevant engineering evidence.
- Do not rewrite Git history or delete artwork. Inventory before untracking and verify all hashes afterward.
- Keep the shared layered renderer/audio/jobs/release services and legacy data-reading contracts.
- Archive historical instructions with a clear superseded notice and valid links; remove retired generation controls rather than leaving dead buttons.
- Preserve unrelated staged IDE files; commit the verified cleanup as its own F13 activity.

**Verification command**
`make check`

Also run `make web-check`, `make web-build`, `make package`, and the target-Mac `make test-media`.
Check all retained local media hashes, zero tracked MP4s, Markdown links, retired CLI/API routes and packaged Python source parity. Report tracked-tree reduction separately from local media and existing Git history.

## F14 — Clean obsolete local test and video artifacts

**Status** [x] Complete. [Evidence](evidence/f14-local-artifact-cleanup.json) records 61 obsolete
run folders, 464 videos and 18.50 GB removed; source/test hashes and the core gate pass.

**Target files**
- Obsolete `.local` synthetic test runs, redundant/superseded train preparation, standalone
  experiment outputs, Python/test/lint/package caches and Finder metadata.
- Three superseded ear-comparison videos in `docs/assets/clip-tests/`.
- `docs/evidence/f14-local-artifact-cleanup.json`, `docs/assets/README.md`, task index and progress.

**Inputs / dependencies**
- F13's source-preservation policy and current workflow/acceptance records.
- Marco explicitly requests cleanup of obsolete tests and video experiments.

**Implementation rules**
- Inventory exact paths and hashes before removing local artifacts. Reject tracked-file cleanup.
- Preserve maintained test sources, original artwork/clips, selected comparison drafts, generation
  archives, immutable durable project sources and the current TABI/Tokyo workflow projects.
- Verify redundant preparation/export copies against durable source hashes. Remove only completed
  test outputs, obsolete derivative experiments and regenerable caches.
- Exclude active render directories; distinguish independently changing runtime/evidence records
  from stable source hashes. Preserve unrelated staged IDE changes and concurrent U03 work.
- Keep the full hash manifest compressed locally; commit only concise cleanup evidence/documentation.
  Do not alter Git history, external projects or application behavior.

**Verification command**
`make check`

Also verify retained source/test hashes, removal-path absence, staged IDE preservation and zero
tracked MP4s. Owned loopback tests require an unsandboxed run on this Mac. No rendering changes
or new creative acceptance are part of this housekeeping step.

## Retained production plan and earlier task references

The previous P01–P04/T40–T48 proposals and trial procedures are retained in the
[archived preparation plan](archive/pre-flow-plan.md). F00–F12 replace that implementation queue;
F13 reduces obsolete code and tracked media. Historical link anchors below preserve earlier references.

<a id="a-bounded-proof-before-more-product-promises"></a>
<a id="build-the-scene-visibly"></a>
<a id="can-the-normal-app-workflow-produce-this-video"></a>
<a id="character-feasibility-proof"></a>
<a id="current-decision-and-scope"></a>
<a id="deferred-checkpoint--trellis-1-mesh-only-preflight"></a>
<a id="historical-checkpoint--native-blender-master"></a>
<a id="how-this-should-appear-in-video-story"></a>
<a id="implementation-conventions"></a>
<a id="monthly-production-and-compute-budget"></a>
<a id="next-checkpoint--google-flow-continuity"></a>
<a id="next-checkpoint--native-blender-master"></a>
<a id="next-checkpoint--trellis-1-mesh-only-preflight"></a>
<a id="p01"></a>
<a id="p01--decide-whether-automatic-character-preparation-meets-the-real-requirements"></a>
<a id="p02"></a>
<a id="p02--define-a-versioned-handoff-from-the-character-library-to-prepared-media"></a>
<a id="p03"></a>
<a id="p03--prepare-complete-character-actions-from-the-same-master-with-blender"></a>
<a id="p04"></a>
<a id="p04--make-preparation-a-durable-application-operation"></a>
<a id="repeatable-flow-production-procedure"></a>
<a id="standard-video-defaults"></a>
<a id="t40"></a>
<a id="t40--derive-safe-import-choices-in-python"></a>
<a id="t41"></a>
<a id="t41--guide-import-with-defaults-and-examples"></a>
<a id="t42"></a>
<a id="t42--build-still-and-layered-scene-drafts-from-assets"></a>
<a id="t43"></a>
<a id="t43--bind-prepared-animation-to-the-scene"></a>
<a id="t44"></a>
<a id="t44--make-scene-building-visual-and-reusable"></a>
<a id="t45"></a>
<a id="t45--apply-standard-defaults-and-let-music-set-the-length"></a>
<a id="t46"></a>
<a id="t46--connect-the-five-steps-with-real-readiness-and-context"></a>
<a id="t47"></a>
<a id="t47--preview-and-export-without-manual-pipeline-setup"></a>
<a id="t48"></a>
<a id="t48--verify-the-complete-guided-workflow-and-update-operations"></a>
<a id="the-proposed-import-experience"></a>
<a id="the-workflow-marco-should-see"></a>
<a id="tools-and-responsibility"></a>
<a id="what-becomes-reusable"></a>
<a id="what-the-repository-explains-about-the-confusion"></a>

Read the [archived preparation plan](archive/pre-flow-plan.md) for these historical sections.
