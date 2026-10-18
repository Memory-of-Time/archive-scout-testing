# Archive Scout v1.2.4: full-range indexing correction

Baseline: `archive-scout-testing-main(5).zip`, SHA-256 `5312d3fe51ccbb4992e0e35c1f48cb501b32b8556ac4ab217a85649ab26ad52e`.
Public version remains 1.2.4. SQLite schema remains 9. This is a focused correction to the supplied repository, not a claim that all fundamentals/endurance acceptance gates have passed.

## What was wrong

1. Saved projects could retain `text_collapse_scope="year"` indefinitely. The GUI carried that hidden value forward. Choosing automatic/resume indexing did not change date scope: transport strategy and date scope are different settings.
2. The date-label helper incorrectly abbreviated a multi-year January–December range to its first year. Even a real 2005–2008 request could therefore appear as simply `2005`. Multi-year same-month ranges had a related abbreviation error.
3. Direct media indexing unconditionally constructed annual tasks.
4. An entirely untouched inherited range plan could retain multiple annual windows after repeated failures. Existing micro-window repair did not address those plans.
5. Reentering a yielded task added its previously counted completed windows to progress again. This made progress less trustworthy across retry rounds.

The current user report did not include the project database/configuration or a fresh complete HTTP log. The defects above are verified source/fixture findings, not proof of which saved setting produced every request on the user's machine. HTTP 503/504 responses can still prevent a correctly constructed request from obtaining inventory.

## What changed

- Empty, legacy annual projects automatically upgrade to full selected-range mode on load. Read-only database inspection verifies there are no retained captures, completed scopes, committed pages, nonzero seen counts or saved continuation progress before that migration. It does not open/migrate the database through the normal write path.
- A project setting `index_scope_revision=1` records that the scope was chosen under this correction. Save/load preserves an explicit current `range` or `year` choice.
- Settings → Connection and indexing now exposes **Index date scope**. `range` is the default; `year` is the legacy selection mode. GUI and CLI use the persisted project setting.
- Untouched fragmented range plans covering the exact original interval are atomically recombined before the next request. Saved cursors, successful pages, completed windows and known bounded gateway-subdivision plans prevent reassembly.
- New or empty multi-year media indexing uses one full-range task with an independent range checkpoint slot. It retains media's existing safe per-response batch sizing. Completed range work is not reissued on the next run.
- Empty failed annual media plans can be retired when moving to the full-range task; their error history remains. Progressed annual media plans continue from their exact saved cursors.
- Multi-year labels now display their actual date bounds. Logs distinguish full-range traversal, saved partial windows and legacy yearly traversal.
- Repeated task turns no longer double-count completed windows. Waiting for retry eligibility does not consume a request turn.

## What you should see

For a fresh or zero-progress project selecting 2005–2008, text indexing starts with a message resembling:

```text
example.com/* • 2005-01-01–2008-12-31 • full-range resume traversal; seen 0
```

The actual initial text request uses the complete selected `from` and `to`, `limit=100000` at the default batch size, and `showResumeKey=true`. Later batches keep those bounds and use the exact returned `resumeKey`. Custom batch sizes, filters, collapse settings, proxy/backend settings and request pacing remain user-controlled. Fewer returned rows are normal; advertised continuation is still followed.

This is a series of bounded responses over one logical range, not loading the complete archive into memory or sending 100,000 concurrent requests. Explicit paged mode remains supported. Existing bounded recovery subdivision for eligible uncollapsed queries remains supported and is accurately labeled as partial-window work.

## Existing projects with real annual progress

A cursor for a one-year query cannot safely be assigned to a different full-range query. In addition, `collapse=urlkey` across one year can select a different inventory than the same collapse across several years.

Therefore, a project with committed annual captures/pages/cursors is **not silently reset or relabeled as a complete range inventory**. Its legacy scope is preserved and explicitly identified in the log. It can finish/resume in that mode. To intentionally select a different full-range inventory, change **Index date scope** to `range` and save/run the project. Existing history is retained; that selection change can require new indexing and acquisition work and is not an equivalent cursor migration. Existing progressed annual media checkpoints remain resumable in their original scope.

Do not delete project databases, edit `schema_info`, clear progress or copy an annual cursor into a full-range plan. This patch does not convert nonzero annual collapse progress into range completeness by assumption.

## Installation

Use either the complete repository or the patch, not both.

- **Complete repository:** extract the corrected code and start it through the repository's normal launcher/environment. Open the existing project folder.
- **Patch:** extract over the source repository root containing `archive_scout/`, `tests/` and `pyproject.toml`, replacing the included files. The patch contains code/tests/documentation only. Do not extract it into the archive-results/project-data folder.

For an old project that still logs legacy yearly scope, inspect **Settings → Connection and indexing → Index date scope**. The exception above is deliberate protection for existing progress, not an unavailable setting. Empty projects upgrade automatically on normal project load/save; manually constructed Python configurations that explicitly request `year` continue to honor that choice.

## Verification and limits

The package includes `validation/range-indexing-fix.json` with the final canonical suite summary and input/changed-file provenance. The new `tests/unit/test_v124_full_range_indexing.py` covers:

- zero-progress legacy load/save migration, explicit scope round trips and stable defaults across future version numbers;
- opaque/progressed legacy checkpoint preservation;
- actual full-range HTTP parameters, 100,000 default row limit, text Stop/reopen/continuation and completed rerun;
- zero-progress inherited annual-plan repair;
- refusal to combine progressed layouts/cursors or intentional gateway recovery plans;
- repeated 504 rounds across targets without losing their full-range cursors;
- retry-turn progress accounting;
- fresh media full-range batching, exact Stop/reopen recovery and completed rerun;
- empty annual media-plan upgrade and real annual-cursor preservation;
- preservation of media checkpoint identity with target-specific date overrides;
- correct multi-year and single-year/month labels.

Run the standard checks from the source root:

```bash
python scripts/run_tests.py --output validation/test-results
python scripts/verify_release.py
python scripts/benchmark_offline.py --cdx-rows 1000 --result-rows 100 --body-bytes 1024
```

Local checks use Linux/Python 3.12 fixtures. Display-dependent tests remain skipped without a display. Hosted Windows/macOS CI, GUI visual execution, live requests to the user's failing sites and overnight throughput were not verified here. A passing release metadata/workflow check is not a hosted CI run. Upstream unavailability still requires automatic retry/deferral; it must not be called a successful empty inventory.
