# Archive Scout v1.2.1 — Audit recovery + encoding patch (incremental overlay)

Apply AFTER the consolidated v1.2.1 patch, the two previous cross-platform CI hotfixes, and Archive Scout-v1.2.1-Completeness-First-Audit-Hotfix-Overlay.zip. This ZIP contains only changed/new files relative to the last audit overlay; it is NOT a standalone installation. Extract its folder structure into the repository root, overwriting matching files. Commit and rerun hosted GitHub Actions.

Changes:
- Failure-only partial replay media continuation via validated HTTP Range where supported; never publish .part files or append nonmatching ranges. Prior partial bytes are only reused with reliable identity checks.
- Prevent completed-page status where durable page ledger has a gap.
- Manual/explicit retries include attempt-exhausted pending captures without changing healthy automatic queue pacing.
- Report still-unfinished attempt-exhausted captures and media only at report generation time.
- Decode unexpectedly gzip-wrapped CDX representations and UTF-16 JSON when detected; malformed/oversized encoded bodies are errors, NOT valid empty inventories.
- Targeted tests for encoded CDX, page evidence, partial file recovery.

Validation: local fixture/mock suite 284 tests, 0 failures, 6 skipped; hosted Windows/macOS CI and sustained live Wayback throughput remain unverified.

Caution: CDX query parameter URL-encoding is NOT automatically broken. Parameter encoding is required to transmit special characters correctly. This patch addresses encoded *response bodies*, not hypothetical malformed requests; investigate concrete failing request URLs before changing query serialization.
