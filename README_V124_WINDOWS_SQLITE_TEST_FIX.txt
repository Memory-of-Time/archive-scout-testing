Archive Scout v1.2.3 — Windows CI SQLite backup test cleanup add-on
==================================================================
Applies to: Memory-of-Time/archive-scout-testing, v1.2.3 (after the previous
source synchronization hotfix).

Changed file:
  tests/unit/test_v122_operation_audit_addon.py

Fix:
  The backup uniqueness test used `with sqlite3.connect(path) as snapshot:`.
  sqlite3.Connection.__exit__ commits/rolls back but does not close the
  connection. On Windows the file handle prevents TemporaryDirectory from
  removing backup SQLite files, raising PermissionError [WinError 32].
  The test now uses `with contextlib.closing(sqlite3.connect(path))` to close
  each snapshot explicitly. Backup implementation and assertions unchanged.

Installation:
  1. Extract this ZIP at the repository root, preserving directory structure.
  2. Overwrite tests/unit/test_v122_operation_audit_addon.py.
  3. Commit and push that single changed Python file.
  4. Trigger a new GitHub Actions run. Re-running an existing SHA is not enough.

Local checks on the patched, complete v1.2.3 repository:
  Targeted backup/operations tests: 9 passed.
  python scripts/run_tests.py: 358 tests, zero failures/errors, six skipped.
  Native Windows runners still need to confirm the fix.

This is a test-only fix; no production source, database, scanning, download,
indexing, reporting or backup routines are changed.
