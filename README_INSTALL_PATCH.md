# Archive Scout v1.2.4 — October 18 Recovery Patch

Exact baseline: `ArchiveScout-v1.2.4-Range-Indexing-Fix-Complete.zip`
SHA-256: `77af8089deb1f6529cdfd4368aa22b438c272b97796aa75d4c556ed5d6a11760`

This ZIP is a **patch**, not a standalone application. From the root of the
repository matching the baseline, extract the `archive_scout/` and `tests/`
folders over the existing source, preserving paths and replacing all six old
files. Add the one new test. Verify with:

    python VERIFY_OCT18_PATCH.py
    python scripts/verify_release.py
    python scripts/run_tests.py --output validation/test-results

Do not upload/commit only some changed files; the old and new revisions must
not be mixed. Push all files, and start a NEW GitHub Actions run against the
new commit. Do not rerun an old commit.

The source is 1.2.4; SQLite remains schema 9. No project migration or data
reset is needed. The accompanying Implementation Ledger lists both corrected
faults and intentionally **unresolved** audit requirements. Hosted CI and live
IA indexing were not verified. Back up existing project data before upgrades.
