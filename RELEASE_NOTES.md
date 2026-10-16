# Archive Scout v1.2.4 — indexing and recovery reliability

This release builds directly on the cleaned Archive Scout v1.2.3 repository while keeping database schema 9, saved project state, acquisition pacing, retained scans, and application paths stable. Key changes are documented in `docs/V124_INDEXING_RECOVERY.md`.

**Validation boundaries:** green local mock/loopback tests do not demonstrate live Wayback multi-day performance. Keep project backups before deployment and verify native Windows/macOS GitHub Actions before distribution.
