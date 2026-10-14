> Historical baseline record. For the current v1.2.3 release and schema-10 migration, see [Final fundamentals](FINAL_FUNDAMENTALS_1_2_3.md).

# Archive Scout v1.2.4: full acquisition/indexing audit implementation ledger

Date: October 13, 2026. Source baseline: `ArchiveScout-v1.2.3-Complete-Repository.zip`.
Audit basis: user-supplied `ArchiveScout-Text-Acquisition-Indexing-Audit(1).md`.
This report distinguishes **implemented** safeguards, **partial** mitigation,
**not implemented**, and **unverified** performance. All existing project
schemas remain version 9; additive auxiliary tables are created on opening.

## Each audited recommendation

| Audit item | Status | Implementation and limit |
|---|---|---|
| 1. Durable continuous text recovery | **Implemented, locally tested** | `text_retry_schedule` records eligible time/failure category/counter per capture. Main queue interleaves due transient errors and untouched captures. Recovery is interruptible, restart-safe and continues while `persistent_retries` is enabled. User-configured rate-limit budgets and explicit Stop remain authoritative. |
| 2. Outage backend connection amplification | **Implemented, locally tested** | Maximum two backends per logical request, cooldowns, single-flight recovery probes and shared fallback pacing. Extra redirect hops are not separately admitted to the global start clock. |
| 3. Connection gate | **Partial** | Backend health and failure categories improved. Existing opt-in host gate behavior is preserved; no speculative global host shutdown. No live failure-window threshold tuning has been validated. |
| 4. Disk-full hard stop | **Implemented in v1.2.3** | ENOSPC, SQLITE_FULL, Windows equivalents stop new work without encoding as retryable URL failure. Worker executor may require in-flight tasks to wind down. |
| 5. Keep bodies after local commit errors | **Implemented, locally tested** | Raw content saved atomically with per-capture identity, file hash/size, and DB evidence. If DB commit fails, exact ID-bound saved body is eligible for local adoption and rescanning, not unconditional reacquisition. |
| 6. Streamed retention/local scanning | **Implemented, locally tested** | Disk-stream into `.transfer`, checked preview/classification, hash during stream, publish after completion/fsync. Separate bounded (64 MiB estimate) local scan supervisor with independent DB writer; saves score-zero outcomes. Text streaming deliberately disables unsafe partial Range resumption; media partial resume unchanged. Some backends still buffer bounded response chunks. |
| 7. Explicit nontext routing (76 suffixes) | **Implemented in v1.2.3** | Known non-text suffix overrides misleading MIME before replay and during payload check; audio/descriptor not mislabeled as video. No new generic audio downloader. |
| 8. Existing classification revisions | **Implemented for pending/eligible in v1.2.3; historical intentionally preserved** | Eligible pending inventory refreshes by policy revision; downloaded historical classifications/evidence are not overwritten. |
| 9. Inherited one-second CDX range repair | **Partial in v1.2.3** | Coalesce only untouched compatible windows. Already processed collapsed children with distinct timestamps are untouched pending canonical CDX key-based reconciliation; no silent reindex or deletion. |
| 10. `collapse=urlkey` range split | **Implemented in v1.2.3** | No temporal subdivision for collapsed queries; existing semantic query identity unchanged. Already completed legacy splits cannot be exactly reversed from URL text alone. |
| 11. CDX clean-prefix completeness | **Partial, inherent protocol limit** | Invalid HTML/JSON/truncation rejected; a full page lacking a continuation token receives one different-format confirmation. A syntactically valid shorter prefix with no cursor is not provably incomplete without extra server evidence. |
| 12. Resume vs numbered paging tradeoffs | **Preserved, not auto-overridden** | Keep fast data-bearing resume as default and durable numbered-page ledgers. No unmeasured change to page sizes, secondary-index freshness or capture selection. Adaptive profile switching requires representative live measurements and reconciliation evidence. |
| 13. Memory-backed TEMP queue | **Implemented in v1.2.3** | File-backed SQLite TEMP queue and keyset batch iteration; project-wide Python capture list avoided. |
| 14. CPU/DB/fsync instrumentation | **Partial** | Acquisition/network, fsync-publication and SQLite commit timings exposed in progress. Full connection-pool/TLS/first-byte/WAL breakdown, batched commits and performance-driven worker scaling not implemented without real measurements and crash-proof design. Raw fsync/atomic publish retained. |
| 15. Proxy/backend parity | **Implemented in source, partly unverified across environments** | Auto mode lazy backend availability handling, explicit `trust_environment` propagation to HTTPX/urllib3/curl, urllib3 proxy manager and bypass handling, proxy credentials excluded from logs. SOCKS availability depends on optional dependency; native Windows proxy registry/GPO behavior not verified. |
| 16. Final accounting/diagnostics | **Implemented/partial** | Incomplete unresolved acquisition remains visible, explicit connection vs pool/read errors, event summaries plus bounded details. Diagnostic retention is bounded without removing inventory, checkpoint or persisted per-capture error provenance. More UI breakdown granularity remains optional. |

## Additional operation-safety repair

- Repeated **Merge Project** now takes a consistent source SQLite backup (including WAL), uses stable source-to-destination IDs for scan runs/notes/extractions, updates existing scores in place, and skips previously copied documents. It incrementally updates FTS instead of rebuilding the destination for every repeat.
- A previously merged source lacking historical ID mappings is **refused for unsafe incremental remerge** until reconciled. Existing data remains untouched. Source raw hashes that changed for an identical capture are refused rather than silently overwriting historical search evidence.
- Duplicate derived text reconstructions are avoided where the original source raw file exists. If original raw bytes are missing, derived evidence is labeled, not claimed to have the original hash.

## Validation and what it does not establish

- Canonical local Linux `scripts/run_tests.py` and GUI-inclusive pytest were executed; exact final counts recorded separately with the release.
- Local HTTP loopback exercises actual network transfer, response hashing, independent scan outcomes, SHA-256 verification, and 30-second-safe fixed request pacing. It is **not a live Wayback service run**.
- CDX terminal-page conflict, proxy trust disabled, invalid saved-body hashes, staged interrupted downloads, interrupted merge/repeated identity, and transient retry timestamps were tested in local fixtures.
- The tests do **not** establish: sustained 8 saves/s overnight, stability after millions of captures, fault behavior on the user's specific proxy/network/antivirus path, or native Windows and macOS CI. Those need dedicated real-environment testing.


## Long-run local scanner/SQLite concurrency regression

The first 900-capture localhost run of the preliminary v1.2.4 build failed:
the download-owner SQLite writer and background scanner's separate WAL
connection encountered `sqlite3.OperationalError: database is locked`.
The short 120-capture smoke test did not surface this issue. The correction
coordinates their **write transactions** with one shared mutex while
retaining independent network and local scanner execution. Scanner analysis
remains CPU-side and outside the writer lock. Ordinary non-concurrent
rescan paths still use their existing database connection. A dedicated
regression test verifies a scanner waits for the other writer and then
commits all outcomes. This is not a claim of lock-freedom against other
processes accessing the same SQLite file.

Post-fix checks on Linux/Python 3.13:

- Canonical local runner: **358 run, 0 failures, 0 errors, 2 skipped**.
- GUI-inclusive pytest (virtual display): **356 passed, 2 skipped,
  88 passing subtests**.
- Actual localhost HTTP, fixed 0.125-second request start spacing:
  **900/900 saved and SHA-256 validated; 900 documents scanned,
  900 scan outcomes persisted; 112.620 seconds, 7.991 validated saves/s**.
- Throughput by save-count third: **7.996 / 7.990 / 7.990 saves/s**; final
  scanner drain: **0.006 seconds**.
- This local fixture deliberately has small, repetitive HTML payloads and no
  real Wayback throttling. It is **not** a multi-day or million-capture run.

## Preservation requirements

No existing project content is erased or reindexed due only to this version upgrade.
Do not start from an empty project when upgrading; maintain your schema-9 DB,
`-wal` / `-shm` safety, capture files, media and historic reports. Existing
text-vs-media policy, 76 explicit excluded suffixes, original URL/timestamp,
user pacing choices, fixed scan selection and GUI/CLI modes are retained.

**Bottom line:** Most of the high-priority audit recommendations are implemented,
but full historical collapsed-CDX reconciliation and live capacity-dependent
scheduler adaptation cannot honestly be certified or automatically completed
without canonical CDX-key evidence and sustained workload measurements.
