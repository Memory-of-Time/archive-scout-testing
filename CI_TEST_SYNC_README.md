# Archive Scout v1.2.3 CI test synchronization add-on

Applies to Memory-of-Time/archive-scout-testing after the prior v1.2.3 report/rescan compatibility hotfix.

The Oct 13/14 GitHub Actions run 38487637962 failed two assertions because old tests were still committed:
- `test_multiscan_integration.py` incorrectly expects a **single** Rescan operation to create **two** runs. The user's current specification is one selected keyword set and one new scan run per operation. The replacement checks that behavior and preservation of historical scans.
- `test_v101_audit.py` expected final progress to remain `index`, but an index-only operation now proceeds through an observable `report` stage. The replacement checks the current final stage.

Two other keyword-selection test modules were stale and two operation/rescan finalization regression modules were missing. They are included to match the complete validated v1.2.3 release test suite.

Files: six test modules, **no production code**. Files should be installed at the repository root, preserving `tests/` subdirectories. This package is compatible with the previous report/rescan code hotfix, which must remain installed. It changes no project settings, scan results, downloader, indexer, or database.

Local verification on Linux / CPython 3.13.5:
`python scripts/run_tests.py --output validation/test-results`
358 run, 0 failures, 0 errors, 6 skipped.
Windows and macOS CI are not yet verified for this new add-on.

After applying, commit all six files and trigger GitHub Actions. For an audit of the final repository, compare tracked files against the entire v1.2.3 complete repository, not an older patch archive.
