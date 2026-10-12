# Scout 1.2.1 — Operations, Safety and Acquisition Visibility

This **patch-only** update builds on the public Scout 1.2.0 repository, including the Dashboard refresh hotfix and intended 1.5-second CDX default. It does not change the fixed replay request-start spacing (0.125s), normal worker count (10), CDX query pacing or the existing text/media classifier.

## Included changes

- Index and download only (no keyword scans or scan jobs); separate retry failed downloads without scanning; correct index-only scope routing.
- One bounded, fair pass over transient text errors, preventing repeated selection of the same failing batch within a run.
- Cross-process project operation lease, and SQLite WAL-aware safety backup before manual database restoration.
- Import files copied into project-owned capture storage, and one-time rebasing of project-owned document/media paths when a project is moved.
- Consistent media embedded-link filtering: a recognized extension not in Include is rejected, while extensionless tagged candidates remain eligible.
- Manual, on-demand integrity checks include media files and streamed SHA-256 verification; never add these checks to the acquisition hot path.
- Balanced Media page rows and editor headings; additional GUI operation help and validation coverage.
- Passive stall diagnostics report outstanding tasks, waiting Wayback gate workers, probe state and elapsed time since completion/save (only after 30 seconds of no completion).
- **Experimental coordinated host connection recovery is OFF by default**. When explicitly enabled, independent failed connections can trigger a short shared recovery probe using the existing host gate; healthy traffic is not delayed by startup ramp-ups.
- CDX error classification prevents temporary 5xx/429 and host connection outages from generating one-second indexing queries. Broad read timeouts and oversized responses retain bounded/responsible subdivision, but HTTP service failures no longer shrink the saved page size or rotate through one-second checkpoint windows.
- Endpoint fallback logs now include the failure category, elapsed time and next service. No extra network requests or automatic checkpoint reset are introduced.
- Windows/macOS/Linux-facing version metadata and README release links updated for Scout 1.2.1.

## Important limitations and decisions

- **Schema 13 from v1.1.1 is NOT migrated in this patch.** An unverified schema downgrade can destroy historic data; use a tested importer against a real legacy project before claiming support.
- Historical scan-and-discard, scan overlap, manual scan memory/workers and storage compaction controls remain under review. Reintroducing them blindly could alter acquisition correctness or performance.
- No automatic retry gate is enabled by default; the optional host gate has synthetic tests only, not a live long-run proof.
- Existing fragmented CDX plans are not automatically recombined because the historical split cause may be unknown. Incomplete windows remain saved and retryable.
- Project relocation/rebase changes only identifiable internal paths and never synthesizes missing files. Back up and verify very large/legacy projects before moving them.
- A local 90-capture benchmark is not evidence of sustained Internet Archive performance. Hosted cross-platform CI and sustained real Wayback trials are required before public release.
