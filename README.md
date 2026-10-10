# Archive Scout 1.2.2 — Lean Engine, CDX & Dashboard Fixes

This **patch-updated runnable source repository** starts with the original September 12, 2026 v1.0.5 downloader/indexer/database and selectively restores compatible interface improvements from v1.1.1. Its scope is correctness, fixed pacing, low overhead and stable long-run operation. It is **not** a claim of exact v1.1.1 feature parity or verified sustained live Internet Archive performance.

## v1.2.2 highlights

- CDX's native Timemap format is selected first; valid JSON returned by a text-preferred endpoint is accepted in the same request. Invalid/truncated inventories remain rejected. Global fixed 2.5-second CDX pacing is unchanged.
- The Activity download speed is a **rolling 30-second rate of newly committed saves**, with the whole-pass average separately labeled. Fixed 0.125-second replay pacing remains unchanged.
- The Dashboard is **manual refresh only**: `Saved documents` counts completed text downloads (including locally unscanned bodies), and `Ranked matches` counts unique pages with qualifying keyword matches, not number of hits or repeated scan sets.
- The dark interface's scroll canvases are now themed (no white background), native display DPI scaling is preserved, and Media extension editors are compact. The main editor can expand into the available space.

## Install and launch

Requires Python 3.11 or 3.12 (3.13 source tests also ran), Tk and Internet access for Wayback operations.

```bash
python -m pip install .
archive-scout-gui
```

For CLI and automation:

```bash
archive-scout --help
```

Run the cross-platform test suite and release verification:

```bash
python -m compileall -q archive_scout tests scripts
python scripts/run_tests.py --output validation/test-results
python scripts/verify_release.py
```

Use the root-level `.github/workflows/tests.yml` for Linux, Windows and macOS CI. Windows ZIP / macOS app builders remain in `scripts/`; no executables are bundled with source.

## Architectural commitments

- Original v1.0.5 parallel Timemap page-count / 10-worker paged indexing, with resumable fallback and strict malformed-response rejection.
- **2.5-second shared CDX request-start spacing** and **0.125-second shared replay request-start spacing** by default. These are ceilings on *attempts*, not guarantees of fresh successful saves.
- Ten acquisition workers by default; compact SQLite selection and bounded request staging.
- Entire document source is searched, including content beyond the former 500,000-character cutoff.
- MIME/extension/binary signature checks before accepting downloaded text; originals are saved atomically as bytes with content-hash evidence.
- Automatic continued retries for transient indexing and text replay failures. Actual service Retry-After controls host eligibility; other routine waits are not adaptive global rate controllers.
- Normal scan results, reports, media, backup/repair/diagnostics, AI and Research Intelligence features originally included with v1.0.5 remain available.
- v1.1.1-derived responsive page scrolling, normalized wheel handling, better panel overflow, and a dedicated Reports workspace. Heavy research auto-build is off for *new projects* but existing preferences are respected.

**Important:** The classifier protects strong binary signatures and records metadata/payload routing evidence but is not an exhaustive format decoder. Some ambiguous mislabeled content remains unresolved and needs more fixture coverage. Explicit text/media inclusion/exclusion settings still govern coverage.

## Project compatibility

This code uses **schema 8** (with automatic migrations from supported schema 2–7), not the schema-13 database used by v1.1.1. Back up every project before migrating. Do **not** point this version at a schema-13 project. The original v1.0.5 migration path remains available for earlier projects, subject to its tests.

## v1.1.1 feature parity

The exact v1.1.1 repository was audited. **Not all of its feature-specific database/API changes were ported.** In particular, v1.1.1 Hitlist resume, full operation-specific schema-13 analysis fields, newer FTS model, and operation-scoped evidence tables still require a deliberate compatibility design. Per-file report choice, filtering, sorting, and indexed classification fields are restored in 1.2.1 and refined in 1.2.2. See `docs/FEATURE_PARITY.md` and `docs/LEAN_REBUILD_AUDIT.md`. The v1.1.1 main window cannot be copied wholesale without pulling in its larger engine and schema.

## Verification boundaries

Unit/integration tests are fixture-based. The workflow is provided, but hosted Windows/macOS results and long-running public Wayback throughput must be verified separately. No actual 100k+/million-capture live operation or week-long run is claimed.
