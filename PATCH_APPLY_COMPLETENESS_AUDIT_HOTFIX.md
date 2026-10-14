# Archive Scout v1.2.1 — Completeness-First Audit Hotfix (Overlay)

**Apply on top of** the current Archive Scout v1.2.1 repository, including its consolidated v1.2.1 patch and existing CI hotfixes. Do **not** replace the repository or use this as a standalone release. Do not apply to v1.2.3/v1.2.3 or a different commit without reconciling source changes first.

This ZIP contains only four replacement source files and three corresponding test files; no version/schema bumps, no changes to default pacing or worker settings. Paths are relative to the repository root.

Changes:
1. Save text and media CDX resume-key progression only in the database transaction that stores the corresponding batch; restore in-memory state if that transaction fails.
2. Check that any previously existing media file truly belongs to the pending capture, via stored SHA-256 and byte count or CDX base32 SHA-1. Preserve conflicting existing contents, disambiguate only collisions, and keep images/videos folders flat.
3. Prevent concurrently queued same-basename media captures from writing to the same destination.
4. Correct false “connection setup” fallback logs for incomplete HTTP transfer and TLS-handling errors.

Validation: baseline 266 local tests passed; overlay 275 tests passed, no failures, six display/environment skips. `scripts/verify_release.py` passed on local Linux Python 3.13. Hosted Windows/macOS and sustained live Wayback performance **not yet verified**. The accompanying full audit is provided separately as a Markdown file.

Local validation after overlay:

```bash
python -m compileall -q archive_scout tests scripts
python scripts/verify_release.py
python scripts/run_tests.py --output validation/test-results
python scripts/benchmark_offline.py --cdx-rows 1000 --result-rows 100 --body-bytes 1024
```

**Keep your existing project database, project.json and capture files.** Stop/exit old Archive Scout processes before changing code. If source in your repository diverged, do not blindly overwrite newer changes.

The hotfix does NOT implement safe HTTP Range continuation or a full coverage/over-attempt dashboard. Those remain listed as next-priority issues in the audit; do not claim the entire program is completeness-certified.
