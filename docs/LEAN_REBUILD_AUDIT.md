# Archive Scout lean rebuild — code comparison and validation audit

**Date:** 2026-10-10. **Candidate:** 1.2.0. **Primary foundation:** the supplied authentic 2026-09-12 v1.0.5 repository, schema 7. **Historical feature source:** the complete supplied v1.1.1 repository, schema 13. The exact source trees were available for this comparison, unlike the earlier historical audit.

## Decision and scope

This is a **complete executable v1.0.5-derived repository**, not a byte-for-byte v1.1.1 transplant. v1.1.1's `ui/main_window.py` alone is ~219 KB versus ~133 KB in v1.0.5 and invokes newer configuration fields, database tables, specialized scanner, report, Hitlist and evidence interfaces not present in schema 7. Copying that window and its dependencies wholesale would restore the larger engine and migrations that the lean rebuild was explicitly intended to avoid. The decision was to preserve the v1.0.5 acquisition, parsing, media, CLI, projects and analysis implementations; port UI components that are independently compatible; and be explicit about unported feature families. See `FEATURE_PARITY.md`.

## Seven required safeguards: source and implementation

| Scope | Verified v1.0.5 behavior | Candidate 1.2.0 change | Validation |
| --- | --- | --- | --- |
| Complete CDX pagination | Timemap page count + ten page workers, bounded page batches, resume fallback; malformed JSON records sometimes skipped | Retained paged strategy and durable window state; both JSON decoders now fail malformed/incomplete rows and retry the page | Existing paging/failure-requeue suite and new malformed-row test |
| Full-source searching | Raw source silently limited to 500,000 characters | Removed source truncation in `scanning/scoring.py` | Match beyond former boundary test |
| Correct text/media classification | Extension could override genuine HTML MIME; text/plain could override PNG bytes | Strong text MIME can override misleading filename; binary structure verified before trusting text MIME; BMP/ID3 false-positive guards | HTML-at-.jpg, mislabeled PNG, BMW-prefix tests |
| Incomplete-response detection | Some parser paths omitted invalid rows | Strict row arity, required timestamp/original, duplicate-header checks | New cross-parser tests; existing CDX text parser malformed checks |
| Atomic file saves | Atomic UTF-8 rewritten `.txt` file | Atomic original-byte write with fsync and rename; hash of exact persisted bytes; text decoding at rescan | Injected replace failure and Windows-1252 replay/rescan hash check |
| Persistent progress | SQLite capture/scan run state and index page checkpoints | Preserved database state and progress; new save telemetry counts only commits; retry selects persisted error captures | Recovery tests, existing integration tests |
| Automatic temporary recovery | Certain network streaks raised `ConnectivityPaused`; transient downloads could remain open errors | Index continues eligible saved work on temporary connection failure until user Stop; temporary replay errors are revisited in bounded DB-selected batches; permanent errors remain terminal | Three-failure-then-success fixture, user-cancellation fixtures and complete suite |

### Request and retry behavior

- **CDX starts:** one process-shared 2.5-second default floor; the configured delay applies across concurrent index workers. Original ten-page-worker and parallel Timemap machinery retained, with resume-key fallback.
- **Replay starts:** one process-shared 0.125-second default floor; workers remain at ten by default.
- **429/503:** actual service `Retry-After` is respected; otherwise a fixed five-second fallback is the default for new projects. There is no escalating application-generated rate-control multiplier.
- **Non-throttle transport failures:** fixed retry waits (not escalating with failure count) happen *only after failures*, not during healthy acquisition. Media indexing likewise recovers automatically instead of requiring manual Resume for temporary transport errors. A persistent outage can leave the application running until the user presses Stop; it must not be treated as a successful complete run.
- **Saved configuration:** earlier values are loaded where explicitly retained. Historical 0.75-second CDX default values are migrated to 2.5 seconds. Older explicit rate-limit budgets may remain in preexisting projects and should be reviewed; they are not a new adaptive controller.

### Latent constraints and risks

1. **No live-service endurance verification:** the v1.0.5 healthy rate is user-observed. This candidate's local fixture performance is not evidence of public Wayback service throughput, long-running congestion, or remote availability policy.
2. **Capture completeness:** old v1.0.5's `collapse=urlkey`, MIME/extension exclusions and status filters still limit the selected inventory. Proper progress does not mean every original archived timestamp is selected.
3. **Classification is conservative, not perfect:** arbitrary binary with no identifiable prefix or embedded media with unknown format may be ambiguous; deeper 1.1.1 classification/evidence state models are not ported.
4. **Text bytes and decoding:** newly downloaded text retains the original payload bytes; rescan recognizes supported encodings. The fallback for uncommon legacy character sets is not exhaustively validated, nor is every importer/old generated file tested with non-UTF8.
5. **Evidence durability:** fsync/atomic replace and SQLite transactions separately protect bytes and metadata. A hard crash between the two can leave an orphaned saved file; a fully transactional file/database journal is not implemented. Project integrity should be used to reconcile orphans.
6. **Automatic retry:** repetitive failed attempts cannot overcome a permanently unavailable remote service. After ordinary retryable errors, the work remains active until recovery or explicit user interruption. Stop responsiveness is bounded by active request I/O timeouts.
7. **Cross-platform:** only Linux source tests and a virtual-display Tk smoke test actually ran here. Windows (including touchpads and file locking), macOS, packaged executables and GitHub Actions CI remain unverified.
8. **No million-row soak:** project-size-dependent costs in analysis, integrity, reports and UI still need profiling at 10k/100k/500k/1m records.
9. **Schema:** old schema 7 only. v1.1.1 schema-13 projects must not be opened/downgraded. A reversible migration is a separate release gate.

## Actual test evidence

| Check | Observed result | Limit |
| --- | --- | --- |
| `python scripts/run_tests.py --output validation/test-results` | **204 run, 201 successful, 3 skipped, 0 failures, 0 errors** | Fixture/mocked source tests on Linux Python 3.13.5 |
| Compile `archive_scout tests scripts` | Passed | Syntax only |
| `python scripts/verify_release.py` | Passed version/package/CI/Windows version assertions | Not a hosted installer |
| Xvfb/Tk application smoke | Passed, 14 tabs, 184px sidebar and scroll owner on each tab | Not native Windows/macOS touchpad/hardware |
| `scripts/benchmark_offline.py --cdx-rows 1000 ...` | Passed | Local database/algorithm microbenchmarks |
| `scripts/benchmark_loopback.py --count 90` | **90/90 saved/scanned/committed and SHA-256 verified; 11.198 s, 8.037/s** | Controlled localhost HTTP; early/middle/late 8.137/7.991/7.990/s; no live Wayback |
| Fault probes | Malformed CDX rejection, three connection failures then success, file publish failure preserving original, byte/hash text rescan | Deterministic synthetic conditions only |

A green local test suite does not certify hosted GitHub Actions. The workflow includes `ubuntu-22.04`, `windows-2022`, `macos-15-intel`, `macos-15` for Python 3.11/3.12, compiled source, version verification, full suite, Linux offline benchmark, and artifact upload on failure. **No remote hosted workflow was run from this environment.**

## Performance/correctness acceptance before calling this production-ready

- Compare same 100k+ diverse capture inventory and filters between the untouched v1.0.5 and candidate; check all selected IDs and source hashes, text/media routing, full-source hits and skipped reasons.
- Repeat mixed-index strategies against compliant real service responses. Detect server-side incomplete bodies, service deadlines and zero-page-but-not-complete cases without silently dropping captures.
- Inject HTTP 429/503, Retry-After, DNS/TLS errors, half-closed pooled connections, incomplete/slow bodies, damaged `.part` files, storage full and SQLite BUSY while verifying no false completion.
- Record 10/60/300-second committed fresh-save rates and bytes/s, queue size, CPU/RSS/disk I/O and open handles early/middle/late in a multi-hour run; record image/video classifications and true body/URL scan counts.
- Test existing schema-7 project restart and project switching under Windows/macOS; verify full CI matrix. Decide separately whether/how to migrate schema-13 projects.
- Restore exact v1.1.1 feature parity only through a planned data/API migration; do not silently reintroduce large analysis, adaptive pacing or network recovery subsystems.

## Conclusion

The seven correctness improvements **do not inherently require** the later 1.1.1 acquisition architecture. A lean v1.0.5 implementation is viable and can approach its fixed replay-admission ceiling under controlled conditions. The **specific v1.1.1 GUI and advanced-feature parity request is not yet fully implemented** because its persisted models and operations are incompatible with the schema-7 foundation. The deliverable is a complete source candidate with known limitations, not a claim of exact final design completion or multi-day service validation.
