> Historical baseline audit, before this patch. For implemented behavior and current validation, see V125_COMPLETENESS_IMPLEMENTATION.md.

# Archive Scout v1.2.5: acquisition overhead, retry selection, and completeness audit

**Date:** 23 October 2026. **Scope:** audit and isolated experiments, with no application changes delivered.

**Verdict:** reducing routine acquisition display updates is worthwhile, but the measured results do not establish that GUI overhead explains the live throughput deficit. A reproducible retry-query scaling defect has a much stronger performance case. An existing orphan-recovery defect prevents an unconditional completeness guarantee and blocks larger write batches until recovery evidence is strengthened. The newest activity log shows a separate failure storm that cannot be resolved by making the interface lighter.

This audit deliberately distinguishes verified local behavior, proposed implementation, and evidence that remains unavailable. It does not certify sustained live Wayback performance or declare the application fully optimized.

## 1. Authoritative inputs and boundaries

The baseline is the newly supplied `archive-scout-main(20261023-222935).zip`, SHA-256 `2f52ce18a6fd8be38377dd14cd8eea378f14ee6917f354ccbeb47744e879988c`. Its source, tests, scripts, and configuration match the previously supplied connection/transfer add-on. Earlier local build products are not part of the uploaded source. Public version 1.2.5 and schema 10 remain unchanged.

The actual run evidence comprises `Pasted text(20261023-222001).txt` and the newer, overlapping `Pasted text(20261023-223414).txt`. They are overlapping excerpts of the same activity, not independent benchmark runs. The user's laptop was turned off during the 18:09:05–18:16:55 gap. That interval is excluded from Scout-stall findings and is not evidence of a software freeze.

Experiments used Linux x86-64 and Python 3.12.14, local HTTP fixtures, real streamed files, real filesystem synchronization, SQLite, and the real acquisition/scanning operations. Large historical populations were synthetic metadata. There were not one million historical retained bodies. No native Tk rendering, Windows/macOS workload, power-cut test, or days-long live-service benchmark was performed. No external downloaders were benchmarked in this audit; comparisons with their advertised speeds would not isolate the costs tested here.

## 2. What the actual logs establish

In the earlier excerpt, 6,412 additional retained captures were recorded over 26 minutes 45 seconds. Excluding the known 470-second laptop interruption gives approximately 5.65 saves/second. Reaching 8/s from that sample would require about a 42% throughput increase. The excerpt alone cannot attribute that gap to GUI, CPU, storage, database, network latency, or throttling.

All 4,710 earlier progress records reconcile: satisfied = retained + excluded/routed. The changes also reconcile: 6,412 saves + 411 failed outcomes + 7 exclusions = 6,830 outcomes. Those are attempt outcomes, not a count of unique permanently lost captures.

The newer excerpt materially changes the immediate priority:

| Restart activity | Observed evidence |
|---|---|
| Operation starts | 18:31:59 |
| Local recovery | One existing body is adopted |
| Existing-document check | Finishes at 18:32:06 |
| Queue preparation starts | 18:32:08 |
| First displayed acquisition outcome | 18:32:21; six attempts, six errors, zero saves |
| Last displayed acquisition outcome | 18:34:00; 713 attempts, 711 errors, zero saves |
| Acquisition accounting at the end | 508,325 retained; 12,059 excluded/routed; 795,349 total |

The two non-error outcomes are exclusions/routings, not successful new saves. The increase in retained captures across the restart is consistent with the one adopted local body. It is not a new network save.

Approximately 99.7% of the restart's completed attempts failed. A rate of roughly seven completed outcomes/second in the displayed interval is therefore not useful acquisition throughput. The current log does not supply enough error categories or nested exception details to determine the principal cause. A few messages identify connection-setup failures, but GUI coalescing prevents counting those messages as a complete failure census. There is no explicit 429/503 evidence in these excerpts that justifies diagnosing server throttling.

The 13 seconds between preparation and the first displayed result is not a clean queue-preparation measurement: it also includes initial worker activity and UI handling. Stage timings are required before assigning that interval to database work.

**Priority consequence:** identify the failure categories and restore successful acquisition before expecting display optimization to solve this particular restart. Do not add workers or arbitrary sleeps based on these logs.

## 3. End-to-end execution and invariant boundaries

The relevant current path is:

1. `operations.run_project` restores the requested operation and project state, checks indexing coverage, and prepares local scan obligations.
2. `downloads.downloader.download_archive` independently requires text coverage. It classifies/filter-routes inventory, excludes `robots.txt`, and prepares a disk-backed acquisition queue.
3. Bounded network futures stream into capture-specific staging files. Transport completeness, payload routing, and recognizable replay-shell checks precede publication. The file is synchronized and atomically renamed.
4. The acquisition owner commits capture state and raw-byte evidence. A local scanner separately reads retained files, checks available evidence, parses, scores, and commits document coverage.
5. Due transient retries are admitted during fresh work and recovered by persistent operation owners. Local scanning is independent of Wayback admission cooldowns.
6. Scan finalization checks for coverage gaps. Dependent media stages retain their indexing/discovery gates. Reports and operation results must continue to describe unfinished work honestly.

The proposed display cadence belongs outside those durable state transitions. A displayed count must remain a view of committed state. Neither a missing UI update nor a lower repaint frequency may change which captures, scans, retries, or media discoveries execute.

## 4. Display updates every 0.5 or 1 second

**Recommendation:** use 0.5 seconds as the default acquisition display cadence, with 1 second available as a lower-update preference. This is a modest, low-risk efficiency change when confined to presentation. It is not a demonstrated fix for network failures or the entire live throughput deficit.

The current producer constructs progress after each completed attempt, not necessarily after each physical request. The GUI already coalesces events while its consumer is busy. Consequently, it is inaccurate to assume that it always performs exactly eight native repaints per second. It still formats routine producer messages and may repeatedly update the activity widget, status, progress bar, and ETA.

The audit-only sampler retains one newest routine download snapshot. It forwards diagnostics and nonroutine events immediately, provides an idle-timer flush, and forces a final flush. Three deterministic sampler tests verify bounded pending state, exact final counters, timing intervals, and diagnostic bypass; a fourth test reproduces diagnostic loss in the current UI queue. Real-operation tests verify interruption/resume, temporary incomplete-body recovery, redirect refusal, robots/media routing, positive scan coverage, and zero-match rescan coverage at both intervals.

### Controlled acquisition results

Each cell below represents 96 real, streamed, synchronized saves followed by verified scanning. All 864 bodies matched SHA-256 evidence; all 864 had document and score coverage. Modes were run in different orders across stages to reduce simple order effects. Each condition was sampled once, so small differences are not statistically established gains.

The growth benchmark calls the acquisition phase directly. Its assertions cover the newly acquired cohort. Historical documents contain synthetic metadata, not a million verified bodies, full-text index entries, or historical score rows; the benchmark does not execute a million-document prior-history rescan or certify that synthetic project's complete historical coverage. The separate small operation tests do exercise operation completion and rescan.

| Historical metadata rows | Routine updates | 0.5-second display | 1-second display |
|---|---:|---:|---:|
| 10,000 | 8.038 saves/s; 96 updates | 8.056 saves/s; 24 updates | 8.056 saves/s; 13 updates |
| 300,000 | 7.965 saves/s; 96 updates | 7.971 saves/s; 23 updates | 7.970 saves/s; 13 updates |
| 1,000,000 | 7.732 saves/s; 96 updates | 7.762 saves/s; 23 updates | 7.717 saves/s; 13 updates |

Rates include queue preparation, acquisition, and scan drain. Short-window first-to-last commit rates in the raw evidence are not sustainable service capacity; startup and commit bunching can make them exceed the configured eight-request pace.

**Verified benefit:** approximately 75–86% fewer delivered routine updates in this fixture. **Unverified benefit:** native GUI CPU savings and live download acceleration. The consumer was headless and inexpensive; actual Tk rendering was not measured. Producer-side message construction remained enabled. These figures cannot support a claim that fewer updates restore 8/s on the user's laptop.

### Required implementation contract

- Use a GUI timer to consume the latest committed snapshot every 0.5/1 second. Do not sleep in acquisition workers or delay database commits.
- Keep errors, storage-full, connection/retry notices, phase transitions, Stop, completion, and incomplete results separate from the replaceable routine slot.
- Flush the latest snapshot before Stop/completion handling and project switching; discard stale snapshots when changing projects.
- Preserve engine callbacks and CLI JSON/JSONL semantics. Some consumers use callbacks for control, and existing tests intentionally trigger Stop from them. Globally suppressing engine events would change behavior.
- Preserve reports-at-any-time behavior and dashboard refresh preferences. Do not rebuild dashboard totals to generate each sampled update.
- Store the cadence as a presentation preference. It must not change indexing identity, acquisition selection, or the meaning of a saved resume request.
- Bound diagnostic delivery too. Do not replace lost messages with an unbounded list or a queue that can indefinitely block acquisition. Persist errors as evidence; aggregate repeated presentation notices with explicit overflow/summary accounting.

## 5. Verified retry-query scaling defect

`download_archive.submit_available` considers a due retry after each block of 16 fresh admissions. Its SQL joins schedules, captures, active scopes/membership, and open retryable download errors, then orders the candidates.

In the unanalysed fixture database, SQLite chose captures by error state, repeatedly searched the broad open-error index, and sorted candidates before returning one. This is more serious than harmless overhead from a single indexed lookup.

| Active due errors | Baseline query | Due-first prototype |
|---|---:|---:|
| 1,000 | 88 ms | 0.211 ms |
| 3,000 | 791 ms | 0.028 ms |
| 10,000 | 8,706 ms | 0.029 ms |

At 10,000 rows the baseline performed approximately 600 million SQLite virtual-machine instructions, versus fewer than a few hundred for the prototype in this layout. Timings include instruction-count instrumentation and are query timings, not full-application speedups. Their exact ratio should not be marketed as an acquisition improvement.

The prototype changes only the probe plan: start from the due-time schedule index, look up captures by primary key, use the capture-specific error index, and order by the schedule's equivalent capture ID. All existing state, deadline, queue exclusion, retryability, operation, scope, and overlapping-target predicates remain intact.

Eligibility checks compare complete returned rows under future deadlines, resolved/ignored/nonretryable errors, non-download errors, queued IDs, downloaded states, differing signatures, overlapping target membership, re-eligibility, and tied deadlines. Interruption/recovery tests run through the real operation path with the prototype. The canonical suite is rerun against the in-memory prototype; see validation evidence for exact results.

### Important limitations and alternatives

Running `ANALYZE` also made the baseline fast in an identical-data control: approximately 8.943 seconds before statistics versus 0.231 ms after statistics. The prototype measured approximately 0.032 ms and 0.113 ms respectively in that control. This is partly a planner-statistics problem. The current normal acquisition path does not regularly refresh those statistics; repair contains an optimize call. Do not add a full analysis pass before every request or retry. Earlier bad-plan runs ranged up to approximately 10.6 seconds; exact timings vary, while the instruction-count finding is stable.

With 10,000 equal deadlines, the analysed baseline still examined/sorted substantially more rows: approximately 12 ms versus 0.025 ms for the prototype. Expressing the equivalent ordering using `sched.capture_id` avoids the unnecessary tie-sort in the tested plan.

The due-first strategy is not constant-time for every project layout. With 300,000 earlier unrelated due errors and no eligible active capture, both strategies walked substantial unrelated history: about 0.09–0.10 seconds for different signatures and about 0.22–0.23 seconds when signatures matched across inactive targets. A signature prefilter eliminated the different-signature work, but did little for same-signature unrelated targets. Signatures do not encode target identity, so replacing exact scope/membership checks with signature equality would be incorrect.

**Recommendation:** harden this hot query and retain operation-compatible index availability, then test queue distributions representative of real projects. Where unrelated due prefixes are substantial, evaluate a scope-aware disk-backed retry workset maintained alongside authoritative failure/resolution transitions. Do not rebuild it every 16 captures, cache eligibility forever, or silently exclude legacy retryable rows lacking schedule records. A workset is a conditional next step, not a verified implementation in this audit.

## 6. Database commits: the measured result changes the recommendation

The acquisition owner and scanner share a write lock. Existing `avg_database_commit_seconds` starts before acquiring that lock, so it includes lock waiting. Calling it pure SQL commit latency is misleading.

An additional 288-save instrumented run separated time inside `save_success` from the existing combined timer:

| Historical metadata | Actual save transaction median | Actual save transaction mean | Combined mean including lock | Estimated aggregate lock wait over 96 saves |
|---|---:|---:|---:|---:|
| 10,000 | 0.610 ms | 0.608 ms | 0.693 ms | 8 ms |
| 300,000 | 0.657 ms | 0.784 ms | 2.196 ms | 136 ms |
| 1,000,000 | 0.667 ms | 0.834 ms | 5.896 ms | 486 ms |

The lock estimate subtracts the instrumented transaction body from the combined timer and includes small measurement overhead. The experiment does not trace every individual lock holder. The scanner's once-per-connection legacy reconciliation is a source-supported candidate for startup contention, not a proven exclusive explanation.

Queue preparation rose from about 0.012 to 0.568 seconds in this run. Large-project startup/reconciliation work therefore deserves separate measurement. These figures do not show actual per-capture SQL transaction time exploding with project size. Nor does half a second of aggregate lock waiting in a short phase explain hours of live slowdown.

**Recommendation:** retain per-capture commits initially. Separate lock-wait, transaction, scanner, and startup timings before changing transaction structure. Remove clearly redundant statements only after verifying their state transitions. Avoid repeatedly recreating pools/scanner connections and repeating historical reconciliation during small retry turns if measured phase churn makes that cost material.

Broad write batching is deferred: there is no demonstrated end-to-end speed benefit here, and recovery currently has the defect below. Deleting integrity checks, raw-byte hashes, synchronization, or completion evidence would violate the requirements.

## 7. Existing completeness blocker: unproven orphan adoption

`scanning.pending.adopt_orphaned_bodies` strongly validates hash and size when payload evidence exists. Without that evidence, it accepts a capture-named file using plausible size, text classification, and a replay-shell preview. It does not establish complete transfer or compare an available selected-capture CDX digest.

The audit reproduces this with a normal text capture containing the full body's valid CDX SHA-1 digest. A local file at the correct capture path is deliberately shortened by 200 bytes, and no payload-evidence row exists. The shortened bytes disagree with the indexed digest.

**Observed result:** adoption returns one, the file becomes saved/unscanned, and the ordinary download operation subsequently scans it and returns `complete` without making a network fetch. The stored document hash describes the shortened body. This is an existing baseline defect; display sampling and the SQL prototype do not introduce it.

This does not prove that the user's adopted file was damaged. It proves that the current acceptance rule cannot establish strict completeness in this recovery case. Passing the reproduction test demonstrates the defect's presence, not correct behavior.

**Required repair before batching:** recovery must have independent evidence for a completed validated transfer. A robust approach records a capture-bound, atomically published validation manifest or equivalent durable journal containing raw hash, size, capture identity, and completed-validation status before allowing the database/publication crash gap to be adopted. Validate the actual file against that evidence on recovery. A trustworthy matching CDX digest can provide another proof path when available and applicable. When proof is absent, preserve the questionable file for inspection and reacquire; never infer completeness from its filename, nonzero size, or readable HTML.

Any manifest design must itself specify crash ordering, incomplete sidecar handling, cleanup, cross-platform atomic publication, and storage-full behavior. It must remain bounded and avoid creating a second acquisition ledger with conflicting completion states. Plain process interruption tests do not certify sudden-power-loss durability; existing WAL/synchronization and filesystem publication behavior require explicit review before making that stronger promise.

## 8. Error reporting and recovery observability

The current GUI uses one latest-progress slot for all progress stages. A deterministic test inserts an acquisition-stall diagnostic followed by routine progress; only routine progress is returned. Therefore the existing queue can hide useful diagnostic messages. The GUI also assigns log timestamps on consumption, rather than recording event-generation time.

The acquisition watchdog looks for no completed requests. A continuous stream of failures can keep it silent while successful saves remain at zero. The newest log demonstrates why a useful-progress diagnostic is needed in addition to a no-completions diagnostic.

Add bounded periodic summaries of successful saves, fresh failures, retry failures/successes, unique unresolved captures, categorized error counts, physical request attempts, and time since last save. Record nested transport category/status, backend, and a few representative failures separately from routine display text. Preserve durable per-capture errors and retry deadlines. Instrument connection setup, response read, pool acquisition, host/backend admission, queue SQL, write-lock wait, transaction time, file publication, and scanner backlog separately.

A no-success watchdog is primarily diagnostic. Do not automatically introduce broad pauses, mark captures unavailable, or change user-selected recovery/pacing policies merely because it fires. Apply recovery according to classified failures and preserve local scanning eligibility. The current logs do not justify blanket adaptive limiting.

## 9. Scanning, resource use, and work that must remain

Current acquisition futures are bounded, scanning has bounded futures and an approximate 64 MiB in-flight body budget, queues are disk-backed, routine GUI event state is coalesced, the activity widget is capped, and dashboard counts refresh on the configured schedule. These safeguards already exist. Reimplementing them would not constitute a new optimization.

The scanner uses a capped CPU-derived worker count, rather than measuring current memory/storage capacity. It checks retained bytes and records explicit score-zero coverage. It remains independent of network cooldowns, but shares CPU, storage, and the database writer with acquisition. Those dependencies must be measured before adjusting concurrency.

The experiments verified both positive matches and zero-match rescan coverage. They do not establish backlog stability over days or across representative large/complex historical pages. Record saved-unscanned count and age, scan throughput, pending bytes, and final drain time alongside saves/s. A faster download counter with an ever-growing scan backlog is not an acceptable optimization result.

Peak process RSS reached roughly 380 MiB in the large synthetic fixture. It includes constructing historical metadata, SQLite caches/mappings, and cumulative process high-water usage. It is not isolated acquisition memory and does not establish a leak. SQLite's configured 64 MiB page-cache target and 256 MiB mapping ceiling are not equivalent to continuously allocated private memory.

Defer broad resource changes to the requested next phase: measure private/working memory, memory pressure and swapping on the target hardware, CPU, storage queue/latency, WAL growth, thread/socket counts, and bounded cache/queue behavior. Shrinking caches or workers without that evidence can increase disk work or reduce throughput. Removing saved evidence, zero-score coverage, media routing, or recovery state is outside the acceptable optimization space.

## 10. Required implementation order

| Priority | Change | Speed case | Completeness condition |
|---|---|---|---|
| P0 | Diagnose the zero-save restart using categorized durable errors | Current run is not acquiring successfully | Preserve every unfinished capture and eligible retry |
| P0 | Require proof for orphan adoption | Prevent false success and avoid unsafe batching | Wrong/truncated bytes must never complete an obligation |
| P1 | GUI-only 0.5/1-second routine updates; separate notices | Fewer presentation operations verified; native speed gain unverified | Final counters, controls, diagnostics, and CLI consumers remain correct |
| P1 | Harden due-retry SQL and planner behavior | Large query improvement reproduced in bad-plan fixture | Preserve exact scope, state, deadline, membership, and ordering semantics |
| P2 | Remove measured repeated startup/history/SQL work | Startup/lock growth measured; steady commit growth mostly disproven | Retain legacy reconciliation and selection correctness |
| Deferred | Larger write batches or broad scanner/cache changes | No adequate whole-run benefit established | Require corrected recovery proof plus interruption and resource tests |

## 11. Acceptance gate for the eventual patch

The production patch must include focused regressions for each changed behavior and pass the canonical suite and supported CI matrix. Cross-platform GUI checks must exercise real rendering, timer lifecycle, project switches, Stop, phase transitions, and final flushing. CLI output and settings round trips must stay compatible.

Performance validation must use identical capture selections, bodies, keyword rules, retention/media settings, request pacing, and comparable service conditions. Record actual network starts/responses, validated saves, scan coverage and backlog, CPU, private memory/pressure, storage/lock latency, database/WAL growth, open handles, and preparation/finalization times. Compare early, middle, and late windows over the full run, not only a peak rolling rate.

Fault injection must cover reset, timeout, 429/503 and Retry-After, incomplete Content-Length/chunks, redirect policy, misclassified payloads, SQLite busy/full, failed publication/commit, Stop/restart, and retained-file alteration. Kill processes at validation/publication/commit/scan boundaries. Verify exactly the same capture identities remain either proven complete, explicitly excluded under policy, or durably unfinished; verify all required score-zero rows and media/discovery obligations. Power-loss claims require separate testing and an explicit durability contract.

The healthy-service target remains sustained near eight validated saves/s, with stable scan coverage and bounded resources. No local fixture can prove that target will hold against live Wayback for days. A candidate may be accepted as a safe overhead reduction without claiming it has closed the entire live throughput gap.

## 12. Validation record and evidence

Machine-readable summaries and raw logs are included in the companion evidence archive.

| Check executed | Result | Qualification |
|---|---|---|
| Canonical suite, unmodified current source | 481 run; 0 failures; 0 errors; 4 skips | Linux/Python 3.12, fixture traffic |
| Canonical suite, final due-first SQL prototype | 481 run; 0 failures; 0 errors; 4 skips | In-memory prototype; production files unchanged |
| Display contract/reproduction suite | 4 run; 0 failures; 0 errors | Three sampler contracts plus one existing diagnostic-loss reproduction |
| Baseline operation/recovery suite | 3 run; 0 failures; 0 errors | Two real-operation scenarios plus one existing orphan-defect reproduction |
| Prototype operation/recovery suite | 3 run; 0 failures; 0 errors | Same scenarios with due-first query |
| Healthy acquisition comparison | 864 saves and scores verified | Nine 96-body conditions, real SHA-256 verification |
| Additional transaction profiling | 288 saves and scores verified | Three 96-body conditions |
| Release metadata verification | Passed | No release published |
| Compile check | Passed | Application, tests, and repository scripts |
| Offline benchmark smoke | Passed | 1,000 CDX rows, 100 result rows, 1,024-byte body parameter |

Defect reproductions intentionally assert unsafe current behavior. Their successful execution is not a completeness or diagnostic-preservation pass.

The initial baseline attempt inherited this environment's SOCKS proxy and produced three initialization errors because `socksio` was unavailable. The clean rerun removes proxy variables only inside the fixture-test subprocess. This does not change the application's proxy settings. Preliminary prototype harness runs required corrections to the module namespace used by test mocks and the working directory used by subprocess imports. The final prototype suite was rerun after those harness fixes. Final results, rather than preliminary harness attempts, are authoritative.

The acquisition comparison contains 864 verified saves; the profiling cohort adds 288, for 1,152 healthy fixture saves. Recovery scenarios add separate files and are not included in those throughput counts. Native GUI checks are skipped without a display. Hosted CI, native Windows/macOS and Python 3.14, sustained live Wayback operation, actual million-body disk histories, and sudden power-loss consistency remain unverified. There is no new release or deployed patch in this deliverable.

**Decision:** implement the presentation sampler and hardened retry selection as focused changes with the stated guards; repair orphan evidence before transaction batching. Treat the current live failure storm as a classified recovery problem first. Proceed to resource reduction using measurements rather than equating smaller memory consumption with higher speed.
