# Archive Scout v1.2.4 fundamentals add-on

**Baseline:** `ArchiveScout-v1.2.4-Complete-Repository.zip`, SHA-256 `253af26b1d22b9b190054b962d929eed9f29b48f2f841c7b7641e0689bdd1d5b` (253-file repository). This patch is **not** for the older v1.2.3 checkout assessed by the October 16 audit. The public version and SQLite schema remain **1.2.4 / 9**.

## Implemented here

- **F1/F7, no-progress indexing recovery:** repeated failing CDX scopes now have exponentially increasing, persisted, per-window eligibility, bounded by the configured `retry_max_seconds` (default 300s). Healthy CDX pacing is unchanged. When all tasks are cooling, the scheduler waits interruptibly instead of tight cycling; it never turns a timeout into complete coverage. **Caveat:** the operation-wide index-before-download barrier is still present, so known inventory may still wait behind a permanently failing index scope.
- **F19, rate-limit deferral:** a finite per-request Wayback 429 wait budget no longer impersonates global user Stop in text or media acquisition. Text failure is recorded for due retry, and unrelated local scanning is unaffected. Media leaves a retryable error, but still needs operation-level automatic due scheduling for complete parity.
- **F20, consistent encoding:** Rescan reads committed `capture_payload_evidence.response_content_type` and uses the same `decode_bytes()` interpretation as acquisition. Hitlist reads saved response content type and its coverage fingerprints now include interpretation version 3. Older interrupted Hitlist version-2 coverage is invalidated and recalculated. Previously *completed* scan runs are not silently rewritten; explicit rescan is needed to refresh older charset-derived matches.
- **F21, immutable acquired evidence:** Rescan refuses to score changed project-owned archival bodies when acquisition SHA-256/size evidence exists, preserves old scan results, and records a local integrity incident. Hitlist likewise counts the body as incomplete and does not treat altered bytes as verified searchable source. Deliberately imported `local-import` files retain their established separate edit semantics. Very old documents without committed raw acquisition evidence remain an unverifiable historical boundary.
- **F22, Wayback shell classification:** avoids rejecting ordinary articles merely because a phrase like `not in archive` occurs somewhere in the body. Strong error titles/headings, Wayback-titled service pages and short first-line plain-text error bodies remain rejected. Ambiguous uncatalogued service templates need further fixture coverage.
- **F23, incremental local scanner discovery:** a SQLite-connection-scoped, one-time reconciliation moves legacy `downloaded` rows without documents into the explicit `downloaded_unscanned` queue. Normal scanner wakeups now use an indexed existence query and keyset scan of explicit pending work, without a whole-history `COUNT`/missing-document join. SQLite busy retries cover the reconciliation write as well as scan commits. The final exact coverage check is preserved.
- **F24, bounded manual retry:** temporary SQLite selection and 256-document/1000-capture batches replace project-sized Python retry ID lists. Stable operation selection remains independent of changing error states. This trades additional setup/network-pool restarts for lower peak memory on unusually large manual retry selections.

## Still open: fundamentals are not certified

- **F1 operation boundary:** while indexing remains incompletely answerable, `run_project` still waits for `index_archive` before downloading known eligible inventory. Fair year/target turns and progressive cooldowns avoid waste but do not solve this barrier. Requires bounded outer orchestration, not a callback hack.
- **F6 collapsed paged selection:** cross-page canonical `urlkey` reducer/grouping evidence is not fully implemented. Retaining old captures and detecting explicit continuation is not a proof of original collapsed selection across arbitrary numbered page boundaries. Do not infer completeness from this mode without protocol verification.
- **F19 media recovery:** a recorded retryable media acquisition error may still require a later media retry operation; it is not yet an equivalent durable automatic due queue.
- **F20 historical scan interpretation:** old completed score coverage isn't automatically versioned/reconciled by charset. Rescan reinterprets bytes correctly when invoked, while legacy results remain preserved.
- **F25 power-loss boundary:** SQLite uses WAL `synchronous=NORMAL` by default, and raw bytes are atomically published with file fsync, but no platform-independent directory fsync/total-power-loss campaign was performed. Do not describe acknowledged saves as power-loss-proof. Using `FULL` or a durable group-commit journal requires dedicated Windows/macOS/slow-storage performance testing; this release does not blindly increase per-save fsyncs to meet a paper guarantee.
- **Acceptance gate L:** no 72-hour live Wayback run, million-row mixed-history endurance, cross-platform hosted CI after this patch, or native sudden-power-cut test has been executed. Local fault fixtures cannot establish remote-service guarantees.

## Measured validation

- Canonical Linux virtual-display suite: **379 tests**, zero failures and errors, two skipped. Run the same `scripts/run_tests.py` matrix in GitHub Actions before distributing binaries.
- Healthy loopback, 240 small HTTP bodies: **240/240** raw saves, documents, scores and SHA-256 checks; **7.984 validated saves/s** overall. Another 900-body run: **900/900** verified, **7.627/s overall**, middle/late thirds **7.990 / 7.991/s**, early third **6.993/s** (startup/shared-machine variation). A separate final 120-body test: **7.742/s overall**, middle/late **7.993 / 7.991/s**. These are local service tests, not live Wayback measurements.
- Synthetic completed-history scanning: **100,000** completed rows, first reconciliation ~45.9ms, next idle checks ~0.52/0.29ms; **500,000** rows, first reconciliation ~278.2ms, next ~2.08/0.33ms. Test setup's sampled peak RSS was ~170MiB and ~387MiB respectively, **not** isolated scanner consumption. In the 900-body benchmark the acquisition process was observed at roughly 120MiB RSS. No million-row mixed-history proof.

## Upgrade instructions

1. Stop Archive Scout, close its project SQLite connections, and back up your project folder independently.
2. Confirm the **application source baseline** matches the named 253-file v1.2.4 ZIP. Do **not** replace your project folder or database.
3. Extract the patch into the repository root, preserving paths and adding the regression test and this document.
4. Run `python scripts/verify_release.py` and `python scripts/run_tests.py`; require the hosted Windows/macOS/Linux workflow to pass before claiming portability.
5. Rescan historical captures with legacy response encodings only if you need to update existing completed match results; the original historical runs are preserved.

**Do not mark the whole fundamentals audit closed based on this patch.** The remaining end-to-end liveness, collapsed selection and durability gates are substantial, and cutting them would misrepresent completeness.
