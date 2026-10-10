# Archive Scout v1.2.3 cross-platform CI hotfix (add-on)

**Apply this ZIP after** `ArchiveScout-v1.2.3-Validated-Patch-Files.zip` (or after the original v1.2.3 patch plus the v1.2.3 CI & GUI add-on). This archive is **not** a complete repository or replacement for the earlier patch.

## Actual GitHub Actions failure

Source: `Memory-of-Time/archive-scout-testing` run `38085544339`, failing job `114311184489` and corresponding other Windows/macOS jobs, 10 October 2026.

Six matrix jobs failed on exactly one assertion in `tests/unit/test_v123_restoration.py::HitlistRestorationTests.test_existing_imported_source_outside_project_remains_searchable_in_place`.

- Windows compared `C:\\Users\\RUNNER~1\\...` with `C:\\Users\\runneradmin\\...`.
- macOS compared `/var/folders/...` with `/private/var/folders/...`.

These are valid alternative paths to the same underlying file. The old test required their text representations to match. The updated test uses `os.path.samefile(stored_path, path)`, which verifies file identity while accepting Windows 8.3 aliases and macOS `/var` symlinks.

The application code is unchanged. This add-on changes only the test, the source checksum inventory and this explanatory note. It does not modify data handling, import behavior, Hitlist code, network access, CDX scheduling, scan operations or dashboard performance.

## Install

Extract the ZIP at the root of the existing v1.2.3 repository, **preserving paths** and replacing the matching existing files. Commit and push. The existing GitHub Actions workflow will run automatically on a push to `main`.

The modified test is at `tests/unit/test_v123_restoration.py`.

## Checks actually performed

- Retrieved the failed Windows 3.12 workflow logs and the uploaded test log; retrieved Windows 3.11 and macOS Intel/ARM Python 3.12 artifacts; all contained the same failing assertion. All six Windows/macOS jobs in the run reported one failure, zero errors, zero skips; the two Ubuntu jobs passed.
- Targeted Hitlist test: passed locally under Linux Python 3.13.5.
- `python -m compileall -q archive_scout tests scripts`: passed.
- `python scripts/verify_release.py`: passed (v1.2.3).
- `xvfb-run -a -s '-screen 0 1280x800x24' python scripts/run_tests.py --output validation/v123-cross-platform-hotfix-tests`: **236 tests, 0 failures, 0 errors, 2 skips**. Display-dependent tests ran on Xvfb.
- Confirmed all original inventory hashes other than the intended modified test stayed unchanged; updated `SOURCE_SHA256SUMS.txt` accordingly.

**Not run:** Native Windows/macOS local tests or hosted GitHub Actions after applying this hotfix. The corrected assertion is directly grounded in the actual failures, but the hosted CI result remains to be confirmed by the next push. No live Wayback or performance benchmarks were needed for this test-only change.
