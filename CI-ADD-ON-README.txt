Archive Scout v1.2.2 — GitHub Actions compatibility add-on
Root cause: scripts/check_project_resume.py was omitted from the patch-only distribution,
but tests/unit/test_v121_v120_upgrade_compat.py imports compare and snapshot from it.

Installation: extract this ZIP at the root of the repository.
Ensure that scripts/check_project_resume.py exists on GitHub under the scripts folder,
not at the repository root. Do not replace any other source files.

Validation: the 3 affected compatibility tests pass; local Linux Python 3.13.5
canonical suite: 312 tests, 0 failures, 0 errors, 6 skipped.
GitHub CI should be rerun to confirm Windows and macOS.
