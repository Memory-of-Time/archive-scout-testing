> Historical baseline record. For the current v1.2.3 release and schema-10 migration, see [Final fundamentals](FINAL_FUNDAMENTALS_1_2_3.md).

# Archive Scout v1.2.3 — implementation and verification ledger

Source baseline: the latest `ArchiveScout-v1.2.2-Complete-Repository-Operations-Audited.zip` uploaded in the Library. Scope reference: `ArchiveScout-Text-Acquisition-Indexing-Audit(1).md` (October 13, 2026).

## Implemented and code-tested

1. **Explicit 76-suffix non-text routing:** URL pathname only, case-insensitive and decoded, safe handling of semicolon/ampersand path trailers. Ext overrides a contradictory MIME at inventory and replay boundary. Descriptor/audio/ambiguous decisions keep their provenance and are not forced into an unsupported media downloader. Index-only inventories are preserved; previously saved scan/match history is not deleted.
2. **Storage-full blocker:** intercept ENOSPC/EDQUOT, Windows disk-full equivalents and SQLITE_FULL. Cancel queued tasks and propagate an operation failure, rather than recording an ordinary URL failure. New capture queue admission stops; in-flight requests may need to return before executor shutdown.
3. **Retained-body recovery:** publish validated replay bytes before expensive scoring; on failed document/FTS commit, attempt to mark `downloaded_unscanned`. Independently recover atomically published, exact-ID/URL-bound saved bodies on restart for previously attempted captures, and scan locally. No generic file-presence-only reuse for media.
4. **Safe CDX subdivision:** no temporal splits of server-side collapsed queries in either ordinary split or 504 exploration. Correctness favored over fallback speed. Conservatively coalesce runs of untouched micro-windows when there is no semantic change; never merge active resume keys/numbered page ledgers. For collapsed queries with already completed work, retain the saved plan rather than fabricating equivalent selection.
5. **Transient recovery:** one fair pass over retryable text captures at a time, repeatedly and interruptibly when persistent retries are enabled, with bounded global backoff and local scan opportunities between sweeps. Previously configured acquisition modes and explicit finite retry operations are preserved. This is *not yet* a persisted per-capture `next_eligible_at` scheduler.
6. **Transport:** instantiate only backends actually selected/available; limit alternate requests to two attempts per logical call; respect cooldown before trying a known unhealthy backend. Read timeouts do not cycle stacks. The proxy/trust policy is **not yet identical across all backends**, and per-wire fallback connections are not separately paced.
7. **SQLite temp queue:** use `temp_store=FILE` on new connections before queue creation. Retain existing keyset iterator, project schema and indexed inventory. This targets memory footprint; speed effects need profiling.
8. **Revision-aware classification:** on existing projects, perform a one-time bounded refresh of still-pending/skipped classifications for the new suffix policy. Historical downloaded files, scan outcomes and stronger payload evidence are never overwritten. CDX query signatures do not change.
9. **Operation accounting:** unresolved target-specific download errors/exhausted attempts cause an `incomplete` operation status rather than silently claiming complete. Generated reports are preserved.

## Remaining substantial work

- Identity-bound streaming of full replay bodies with a byte-budgeted scanner *independent* of all network workers, with exact HTTP transfer completion validation.
- Persisted per-capture retry eligibility timestamps, fair retry scheduling while normal untouched downloads continue, backend recovery single-flight probes, and consistent proxy configuration across all three HTTP stacks.
- Stronger CDX terminal page provenance/continuation reconciliation, and collapse-correct repair of already completed legacy split windows (requires selection reconciliation, not blind merging).
- Full historical reclassification beyond eligible unprocessed inventory, and intentional audio/descriptor media handoff.
- Full database/FTS/write/fsync timing breakdown, bounded diagnostic event retention, long-run RSS/CPU/SQLite WAL benchmarks, and native Windows/macOS CI.
- Repeated Merge Project synchronization from an evolving SQLite/WAL source remains unsafe in the pre-existing operations audit. Do not use repeated merge as synchronization.

## Test boundary

Run `python scripts/run_tests.py` and `python scripts/verify_release.py`. For GUI-inclusive pytest in a headless Linux environment, run through `xvfb-run -a`. The regression file `tests/unit/test_v123_acquisition_integrity.py` validates 76 suffixes, inherited-plan conservatism, storage errors, file-backed queues, retained body adoption, and backend construction. No live Wayback or multi-day evidence is provided here. Short local fixture tests cannot establish eight validated saves/s on the production service.
