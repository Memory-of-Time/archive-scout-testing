# Archive Scout v1.2.3 CI Compatibility Hotfix

Applies to Memory-of-Time/archive-scout-testing, specifically GitHub Actions run 38487139182.

## Confirmed cause
The repository contains the correct v1.2.3 archive_scout/operations.py but older versions of two related modules. Operations passes `empty_message` to the rescan worker and `progress`, `stop_event`, and `operation` to report exporters; the old function signatures reject these with TypeError. The failures were reproduced in GitHub Actions on Linux, Windows, and macOS.

## Apply
Extract into the REPOSITORY ROOT, preserving paths and replacing both files:
- archive_scout/reports/text.py
- archive_scout/scanning/rescanner.py

Commit both files to GitHub. Run Actions again on the new commit (rerunning the old workflow run without committing changes will not test this fix).

Do not extract the ZIP into an archive_scout subfolder, and do not overwrite your project databases, settings, or saved captures. This hotfix changes no database schema, acquisition, indexing, keyword settings, or text/media classification.

## Verified
- The exact v1.2.3 packaged versions of these modules were compared with the uploaded GitHub branch: both branch files were outdated, while operations.py matched the release file byte-for-byte (Git blob identity).
- Linux CPython 3.13.5 `python scripts/run_tests.py --output ...` in the complete v1.2.3 packaged source: 358 tests, 0 failures, 0 errors, 6 skipped. Proxy environment variables unset for localhost tests.
- Cross-platform GitHub Actions green state must be confirmed with a fresh workflow run after applying this add-on.
