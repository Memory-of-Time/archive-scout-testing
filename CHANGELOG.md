# Changelog

## Archive Scout 1.2.3 — durable acquisition and audit integration

- Persist per-capture transient-retry eligibility and preserve fair, resumable acquisition during outages; default operation automatically rechecks scheduled work until stopped.
- Stream replay bytes to identity-bound atomic files, keep local scans on a separate bounded worker pipeline, and verify retained SHA-256, response MIME and length before scoring.
- Make repeated project merges WAL-snapshot-consistent and source-ID-mapped, so already merged scan runs, notes and files are not duplicated on subsequent merges; refuse unsafe legacy remerge without ID reconciliation.
- Coordinate one backend recovery probe at a time, rate-limit fallback connections, preserve proxy policy and close streamed redirect responses promptly.
- Retain only bounded granular CDX diagnostic events and aggregate older incident counts; confirm suspicious full terminal CDX pages once before marking complete.
- Distinguish connect, pool and read timeouts, track network/FS/DB hot-path timing, and preserve successful text/media classification and recovery settings.
- Never delete or guess at already completed historical collapsed CDX selections; canonical URL key evidence is required for a true reconciliation.
- Preserve schema-9 databases, existing project state, scan history, and Windows/macOS/Linux source compatibility.
- See `docs/ARCHIVE_SCOUT_1_2_4_AUDIT_IMPLEMENTATION.md` for verification and substantial remaining limitations.

## Archive Scout 1.2.3 — Acquisition/indexing integrity (incremental patch)

- Route the 76 explicitly requested known non-text suffixes away from text acquisition even when Wayback reports `text/html`; retain evidence of MIME contradictions and descriptors/audio provenance.
- Prevent error-recovery subdivision from changing `collapse=urlkey` capture selection; conservatively coalesce untouched inherited one-second windows where semantic scope permits.
- Stop acquisition on disk-full errors instead of recording thousands of retryable URL errors.
- Retain validated raw bodies before local parsing; adopt exact ID-bound complete files after a SQLite/FTS interruption, then rescan locally.
- Fair repeated recovery sweeps for transient text failures in persistent modes, with interruptible shared pauses and scan progress preserved; mark unresolved acquisition states incomplete.
- Construct only requested transport backends, avoid bypassing all backend cooldowns, and limit fallback trials.
- Move the large SQLite TEMP queue to file-backed storage for more predictable memory use.
- Preserve schema-9 databases, historical scans, user pacing, CLI/GUI settings and prior operation audit corrections.
- The full streaming/scanning architecture and live multi-day throughput remain unverified; see `docs/ARCHIVE_SCOUT_1_2_3_PATCH_VALIDATION.md`.

## Archive Scout 1.2.2 — Indexing, scanning and report integrity

- One explicitly selected keyword set per scan/rescan operation, producing one new scan report directory rather than multiple; other sets and past scan history remain available.
- Browsing an unchecked keyword set no longer silently clears the checked "Use in next scan" selection. Legacy projects with multiple checked sets use the first checked set only.
- Includes the previously missing `scripts/check_project_resume.py` and the canonical Windows/macOS path-safe resume compatibility test.
- Scan text inline with downloads; independently recover retained bodies before further network indexing.
- Resume partial scans and backfill missing document outcomes without repeating completed scoring.
- Recover downloaded bodies lacking document records; make scan results and state atomic.
- Preserve incomplete CDX coverage on errors; reduce repeated HTTP 503 and malformed-response churn.
- Respect target-specific CDX signatures in download/retry queues.
- Bound local rescan work and expose genuine zero-hit scans versus unscanned documents.
- Preserve nonempty historical discoveries separately from latest-run exports.
- No database schema or text/media routing change. See `docs/ARCHIVE_SCOUT_1_2_2_INDEX_SCAN_AUDIT.md`.

## Archive Scout 1.2.1 — Operations and reliability (patch)

- Restored index/download-only and acquisition-only retry operations, project safety and import portability.
- Corrected bounded error recovery, embedded media filtering and the Media-page layout.
- Added passive stall diagnostics and a default-off experimental host recovery option.
- On-demand media integrity/hash verification, WAL-safe restoration and project operation leases.
- CDX outages no longer shrink resume windows/page sizes or churn already-fragmented queues; genuine size-pressure recovery retained.
- Endpoint fallback diagnostics now include cause, elapsed time and selected next service.
- Schema-13 migration and retired historical scanning controls remain deferred pending compatibility/performance validation.

## Archive Scout 1.2.0 — New public era

- Rebranded the desktop app, CLI, installers and release packages as Archive Scout.
- Preserved the validated 1.2.3 indexing, resilient acquisition, local scanning, reports and schema-9 project formats.
- Consolidated source repository; removed superseded patches, test output and old audit attachments.
- Added three stable, OS-specific latest-release links backed by the release workflow.
- Retained the `archive_scout` Python import path and legacy CLI aliases to reduce migration risk.

The version reset is a branding decision, not a rewrite of the downloader. See `RELEASE_NOTES.md`.
