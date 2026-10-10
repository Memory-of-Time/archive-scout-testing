## 1.2.3 (2026-10-10) — Scoped v1.1.1 restoration

- Restored compatible v1.1.1 GUI presentation, editor borders, controlled scrolling, History/Errors details and pagination, report controls, optional dashboard refresh/ETA, and local Search with Hitlist.
- Restored selected-range/resume-first indexing and bounded native JSON paging, with durable per-page and range checkpoints. Existing saved year scope and page layouts are preserved.
- Added archived external redirect download opt-in, hop-by-hop policy checks, destination display/reporting, and deterministic rejection of live redirects without network cooldowns.
- Schema 9 adds checkpoint/search tables to the supplied schema 8; existing routing, payload evidence, media and scored scanning remain unchanged. No adaptive rate limiting or new network pause policy.
- Added restoration, migration, GUI, redirect transport and frozen CLI checks. Local verification does not establish live-service or overnight throughput.

## 1.2.2 (2026-10-10) — CDX response efficiency and GUI/dashboard corrections

- Reinstated v1.1.1's native Timemap endpoint format preference and one-response JSON detection. CDX fallback warnings now report the actual parse fault instead of asserting that every nonmatching response was incomplete.
- Download Activity reports rolling 30-second fresh committed saves/s, with invocation-average speed separately identified; no new database queries in replay workers.
- Dashboard cards refresh only on an explicit Refresh dashboard click. Saved documents counts downloaded and downloaded-unscanned text captures; ranked matches counts distinct pages with qualifying positive keyword matches, excluding zero-score/excluded/incomplete-rule results.
- Fixed unthemed white scrolling canvases in dark mode, preserved OS-native font scaling, reduced unnecessary media editor width, and constrained long media help text.
- Kept database schema 8, fixed 2.5-second CDX and 0.125-second replay request spacing, existing indexing checkpoints and all download/scan routing.
- Added Windows-safe fixture cleanup and regression tests. Local loopback results are not sustained live Wayback claims.

## 1.2.1 (2026-10-10) — Lean acquisition + post-acquisition scanning

- Restored v1.1.1-style automatic index strategy, exclusive keyword set selection, accessible GUI and customizable Reports (candidate improvements).
- Added schema-8 lightweight capture classification and routing evidence, payload overrides, automatic media deferral and classification-aware inventory report fields.
- Moved full keyword/source scanning out of replay workers into a durable bounded local scanner stage; replay pacing unchanged.
- Fixed misleading non-text open errors and expensive every-tick classification aggregation; retained complete source and original bytes.
- Verified 213 tests (three skipped) and 300/300 localhost captures at 8.001 committed fresh saves/s during acquisition; live-service long runs unverified.

# Changelog

## 1.2.1 — Lean feature restoration (candidate)

- Restored v1.1.1's automatic resume-key preference while retaining explicit parallel Timemap paging and completed/in-progress saved page queues. Fixed 2.5-second index request spacing and 0.125-second replay spacing remain unchanged.
- The GUI now selects only the currently active keyword set when using "Use in next scan," eliminating unintended additional scans; older keyword sets and rules are retained.
- Reintroduced report output selection, presets, ordering, field selection and presentation limits using bounded post-operation generation. Disabled outputs are not generated.
- Improved main/sidebar scrolling, visible field boundaries and responsive report access.
- No new work on the replay acquisition hot path; default research auto-build remains disabled.
- Schema 7 and lean text/media classification are unchanged: this candidate does **not** yet restore all v1.1.1 classification/evidence tables, Hitlist resume, report formats, or complete GUI feature parity.
- See `docs/FEATURE_PARITY.md` and `docs/V121_PERFORMANCE.md`. Real Wayback endurance and hosted Windows/macOS workflows remain unverified.

## 1.2.0 — Lean rebuild candidate

- Authentic v1.0.5 source core; selected v1.1.1 GUI widgets and dedicated Reports page.
- Fixed 2.5-second CDX pacing; retained fixed 0.125-second replay pacing, bounded worker pools and paged Timemap indexing.
- Strict CDX JSON row validation, complete source scans, content classification corrections and exact original-byte atomic saves.
- Non-adaptive throttle fallback and automatic recoverable indexing/text download retries; durable retry selection.
- Correct successful-save rate rather than request attempt rate.
- Added cross-platform tests runner and lean-rebuild regressions, CI evidence upload and clean repository identity checks.
- Preserved schema 7, documented missing schema-13 feature parity; **not** safe for newer schema-13 project downgrades.


## 1.0.5

- Changed automatic CDX indexing to the fast Timemap numbered-page pipeline: fixed pageSize=9, ten concurrent page workers, Timemap JSON first, and a rolling queue of up to 1,000 pages. Auto mode forces the reference page grouping even when an older saved queue carried a different numbered-page block value.
- Preserved resume-key traversal as the recovery path for unavailable pagination, repeated slow pages, and explicit resume mode.
- Applied the same parallel Timemap acquisition logic to direct-media indexing.
- Standardized media output to exactly two flat directories: `media/images/` and `media/videos/`.
- Media files now use the original URL filename without timestamp, database-id, host, or path prefixes; raw percent-escaped URL spelling is preserved whenever portable filesystems allow it.
- Media replay fetching now follows the reference downloader's `if_` behavior (`oe_` for SWF), keeps the ten-worker/eight-starts-per-second envelope, uses at least five transient retries, prioritizes known-small files, and skips network work when the exact destination already exists.
- Project merge media copies now honor the same flat images/videos layout.

## 1.0.4

- Raised the default replay-download envelope to ten persistent workers with 0.125-second request-start spacing (up to eight starts/second), while retaining coordinated 429/503 host pauses, bounded in-flight work, retries, and resumability.
- Added native `ahocorasick-rs` matching and `selectolax`/Lexbor HTML parsing to the hot scan path, with the existing Python implementations retained as safe fallbacks.
- Removed a duplicate literal-prefilter traversal and reused the already-normalized body when computing document hashes.
- Added legacy text-page extensions `.shtm`, `.dhtm`, `.xhtm`, `.phtm`, and `.dat`; existing `.htm`, `.cgi`, `.php`, and `.txt` support remains.
- Fixed `Index URLs only` so it immediately writes `reports/all_indexed_urls.txt`, `summary.txt`, `errors.txt`, and `site_issues.txt`; report regeneration now also works for index-only projects without a scan run.

## 1.0.3

- Replaced automatic numbered CDX paging with resume-key-first traversal for broad indexes, eliminating the thousands-of-pages failure mode on very large sites.
- Automatically converts unfinished v1.0.2 numbered-page queues to resumable row batches without deleting captures already stored in SQLite.
- Increased the default resumable CDX batch to 100,000 rows while preserving adaptive date-window subdivision, shared request pacing, finite pause budgets, and explicit paged mode for diagnostics.
- Applied the same resume-key-first strategy to direct-media indexing and fixed automatic media paging so `page_blocks=0` can never become `pageSize=1`.
- Reduced embedded-media exact lookups to the minimum CDX data required for earliest/latest policies and parallelized bounded external-asset/media discovery.
- Optimized CDX parsing/ingestion, error lookups, HTML parsing, media URL policy checks, keyword/proximity scoring, duplicate analysis, snapshot analysis, report replacement, and analysis batching.
- Reworked Research Intelligence indexing/search hot paths to reduce N+1 queries, project-sized temporary state, redundant graph rebuilds, and unnecessary entity/vector work.
- Added database indexes for hot review/error/analysis relationships without changing schema version 7.
- Added regression coverage for automatic resume traversal, v1.0.2 queue conversion, 100,000-row continuation, media indexing, URL-key continuation, and compact CDX row semantics.
- Centralized product version reporting in the CLI and AI provider user agents to prevent release metadata drift.

## 1.0.2

- Added project-wide Research Intelligence with local hybrid vector/full-text/entity retrieval, duplicate clustering, evidence relationships, and chronological connection context.
- Added citation-grounded deep AI research over a bounded evidence set while keeping deterministic scores and human review authoritative.
- Added optional FastEmbed local neural embeddings while retaining a dependency-free local-hash backend.
- Replaced the old forced `pageSize=9` broad-CDX default with server-selected large pagination and bounded concurrent large response bodies.
- Added a complete bot/automation CLI with JSON/JSONL progress, stable exit codes, graceful interruption, noninteractive init, and read-only inspection commands.
- Added separate packaged CLI executables on Windows, Linux, and universal macOS.
- Added OpenAI/OpenRouter provider adapters and safe ignored `.env` developer configuration without credential persistence.
- Added schema version 7 and migration coverage for Research Intelligence tables.
- Added agent/automation/provider documentation and expanded release regression coverage.

## 1.0.1

- Resume now re-enters any saved incomplete CDX index queue before downloading, so an interrupted indexing run cannot be mistaken for a complete project.
- Wayback 503 responses now enter the same process-wide coordinated host pause as 429 responses even when Retry-After is absent.
- All archive/index/media clients in one process now share request-start coordination and a host recovery gate, preventing concurrent projects on one machine or VPS from multiplying traffic independently.
- Coordinated pause budgets are finite by default (15 minutes / 8 incidents); legacy zero values normalize to the safety defaults instead of waiting indefinitely.
- Download progress is cumulative across resumes and operation progress is persisted in operation_runs for external integrations.
- Added is_recoverable_pause() as a stable integration contract so bot/front-end wrappers can report saved network pauses separately from failures.
- Added regression coverage for the audit findings.

## 1.0.0

- First official Archive Scout release.
- Added optional OpenAI-powered AI relevance review for completed scan reports.
- Added structured, explainable AI relevance results without replacing deterministic scores or human reviews.
- Added schema version 6 for AI runs/results, persistent external-media discovery, and site-specific Wayback issue tracking.
- Rebuilt external embedded-media discovery around persistent queues, bounded parallel discovery, bounded exact-CDX lookups, host-level policy circuits, and broader modern/legacy embed extraction.
- Preserved the intended external-media workflow: index site → download/scan text → discover external media → resolve archived captures → stream media downloads.
- Added explicit communication for Wayback exclusions, robots.txt restrictions, unavailable captures, access restrictions, invalid replay pages, origin errors, rate limits, timeouts, connection failures, TLS issues, and service errors.
- Retained persistent/resumable CDX work, request pacing, transport fallback, date-window recovery, bulk database insertion, keyset pagination, no-op writes, size-aware scheduling, and direct-to-disk media downloads.
- Retained multi-keyword-set scanning, FTS search, review statuses/notes/tags, report exports, scan comparison, forum reconstruction, legacy embed extraction, provenance, duplicate analysis, first-appearance analysis, project repair, backups, diagnostics, and secure project merging.
- Rebranded product-facing documentation, metadata, startup UI, packaging, and release workflows to the official Archive Scout name and version 1.0.0.
