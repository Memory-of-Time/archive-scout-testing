# Scout v1.2.4 patch installation

**Exact baseline:** `ArchiveScout-v1.2.3-Complete-Repository.zip`, not an older 1.2.2 repository.

1. Stop all Scout processes. Copy or safely back up your project before upgrading.
   For an open SQLite WAL project, use SQLite's online backup; never copy just
   the main `.sqlite3` file from a running application.
2. Extract this patch ZIP into the **program repository root**, preserving paths
   such as `archive_scout/`, `tests/`, and `docs/`. Overwrite matched program
   files. Do **not** extract these files into the project archive directory.
3. Existing schema-9 projects and query/scan identities are kept. Reopen the
   same project path and preserve its previous target filters/date/collapse
   settings to continue.
4. Run `python scripts/verify_release.py`, then
   `python scripts/run_tests.py --output validation/test-results`.
5. Use the complete v1.2.4 repository ZIP if you are uncertain about the
   intervening v1.2.1–v1.2.3 patches. Do not delete old report folders.

Audit-derived safeguards favor preservation over silently changing old CDX
selection. See `docs/SCOUT_1_2_4_AUDIT_IMPLEMENTATION.md` for still-unverified
behaviors, especially legacy collapse reconciliation and evolving merges.
