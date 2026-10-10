# Archive Scout 1.2.3

This release builds on the supplied `archive-scout-testing-main.zip` (v1.2.2). It restores the compatible v1.1.1 interface, indexing behavior, and missing local tools while retaining the supplied repository's text/media classification, acquisition and local scanning engines.

## Changes

- v1.1.1 layout and aesthetic, visible editor borders, controlled wheel scrolling, responsive panels, per-file report controls, read-only evidence details, and paginated History/Errors views with copy/export details.
- Resume-first automatic indexing, full selected-range queries for new projects, native JSON numbered pages when needed, bounded parallel requests, independently committed completed-page checkpoints, and range coverage. Existing projects retain their saved year-collapse behavior and in-progress page sizes.
- Search with Hitlist searches indexed URLs and complete saved text, including downloaded files awaiting scanning. Its separate durable coverage resumes interrupted searches, freezes the inventory boundary, and checks saved-file hashes before reusing coverage. It does not download, create score runs, or change classification.
- Recorded redirect destination in results and optional ranked report fields. Settings can enable archived redirect destinations outside selected sites; this is off by default. Every replay redirect hop is checked before contact, and live-web destinations remain blocked.
- Manual dashboard refresh remains the default. Optional automatic refresh is bounded and coalesced; optional ETA is a display estimate.

The fixed user-selected request spacing, existing automatic connection recovery, service Retry-After handling, text/media rules, original byte validation, existing scored scanner, Media, AI and Research Intelligence remain in place. No adaptive rate limiter is added.

## Apply the patch

Use the extracted repository from the supplied `archive-scout-testing-main.zip` as the base. Keep a backup of that source folder and of existing project folders. Extract the patch ZIP into the repository root (beside `pyproject.toml`) and replace matching files. No repository files need deletion. Do not apply this patch directly to an older v1.1.1/schema-13 source tree.

## Install and launch

Python 3.11 or 3.12 and Tk are required. Wayback operations require Internet access.

```bash
python -m pip install .
archive-scout-gui
archive-scout --help
```

Hitlist is available in Results and search, the Operation menu, and the CLI:

```bash
archive-scout run /path/to/project.json --mode hitlist --format jsonl
```

Set `hitlist_keywords` or `hitlist_file` in the project configuration, or enter them in the GUI. A hitlist file contains one literal search phrase per line; the normal scoring keyword sets remain separate. Outputs are `reports/hitlist_<run-id>/matches.csv` and `summary.txt`.

## Projects and validation

Schema 9 adds Hitlist and indexing checkpoint tables to schema 8. Supported schema 2–8 projects migrate with a safety database backup; payloads and classification tables are retained. Schema-13 v1.1.1 projects are not a supported migration source. New projects use selected-range text collapse; older configurations without that setting retain year collapse. Stored custom settings and current text/media routing remain authoritative.

```bash
python -m pip check
python -m compileall -q archive_scout tests scripts
python scripts/verify_release.py
python scripts/run_tests.py --output validation/test-results
python scripts/benchmark_offline.py --cdx-rows 1000 --result-rows 100 --body-bytes 1024
```

The existing Tests workflow checks Python 3.11/3.12 on Linux, Windows and both macOS architectures and uploads its results. Build All Platforms retains its signing and packaging rules. Run Tests successfully before Build All Platforms; publishing/signing settings are separate from source validation.

Local tests use fixtures, injected faults and localhost HTTP. They do not establish sustained live Wayback throughput near eight validated saves per second, million-capture completeness, overnight consistency, or hosted platform build success. See `docs/V1.2.3_RESTORATION.md` and the separate validation evidence supplied with this patch.
