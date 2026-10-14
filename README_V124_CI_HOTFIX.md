# Archive Scout 1.2.3 CI source synchronization hotfix

For failed GitHub Actions run:
https://github.com/Memory-of-Time/archive-scout-testing/actions/runs/38488398520

## Root cause, confirmed from actual CI artifacts and GitHub's Git tree

The GitHub repository's 83 test files matched the locally validated 1.2.3
release, but FOUR of its 109 application files still had earlier content.
The failed tests correctly detected missing backup, repair, and GUI safety
behavior. The previous test-only fix was therefore insufficient.

This ZIP contains the FOUR complete, exact-byte source files from the fully
tested v1.2.3 complete repository. `cli.py` is included because the full
109-application-file comparison found it mismatched too.

Replace these four repository paths (do not modify the existing project DB):
  - archive_scout/cli.py
  - archive_scout/projects/backups.py
  - archive_scout/projects/repair.py
  - archive_scout/ui/main_window.py


## Apply

1. Extract this ZIP, preserving its archive_scout/ directory tree.
2. Overlay the FOUR Python files on the root of your GitHub checkout.
3. Run: `python VERIFY_V124_CI_HOTFIX.py` in the repository root.
   It must print OK for all four files, or the patch is not installed.
4. Run: `python scripts/run_tests.py --output validation/test-results`.
5. Commit/push all four corrected paths, and start a NEW Actions run.
   Rerunning an old failed workflow uses its previous commit and cannot
   test newly committed files.

The verifier does NOT change repository files. It only compares SHA-256s.
All 83 test files and other application files already matched release.

## Validation boundary

Confirmed in run 38488398520: Ubuntu, macOS, and Windows fail on the same
four underlying test errors. The exact release source, including these four
files, passed 358 tests, zero failures, zero errors locally on Linux.
This does not guarantee a new GitHub Actions run has passed yet.

SHA256SUMS_CI_V124.txt records the four canonical hashes.
