# Archive Scout v1.2.3 patch installation

1. Stop every running Archive Scout GUI and CLI operation. **Do not overwrite a running source installation.**
2. Back up your current repository and your project directory (including `archive_scout.sqlite3`, any `-wal`/`-shm`, `project.json`, captures, media, reports). Use SQLite's online backup operation if taking a snapshot while a project is active.
3. Extract this patch zip at the **repository root**, preserving `archive_scout/`, `scripts/`, `tests/`, `packaging/`, and `docs/` paths. Replace matching source files. The patch is not a replacement database and should not be extracted into your project output directory.
4. Check `python scripts/verify_release.py` and `python scripts/run_tests.py`. Reopen the existing `project.json` without altering targets, CDX date boundaries, or collapse settings.
5. Optional: use `python scripts/check_project_resume.py "YOUR_PROJECT" --snapshot before.json` before upgrading and `--compare before.json` afterward; do not interpret changed acquisition counters as lost archived captures without reviewing the actual states.

**Target baseline:** complete v1.2.2 *operations-audited* repository. For any older v1.2.2 build, use the full v1.2.3 source release or first apply the intervening operation-audit/rescan fixes; do not assume this incremental patch contains every historical hotfix.

**Known limitations:** see `docs/ARCHIVE_SCOUT_1_2_3_PATCH_VALIDATION.md`. Persistent retry intentionally does not silently stop at a fixed URL attempt ceiling; use Stop to checkpoint manually. Changing suffix policy does not delete historical scan evidence. No schema migration is required (schema 9 retained).
