# Archive Scout v1.2.3: final fundamentals implementation

This complete repository starts from the supplied `archive-scout-testing-main(4).zip`, which identified itself as version 1.2.4. The requested final release identity is **Archive Scout 1.2.3**. The numeric release change does not downgrade stored project data. Public GUI/report text, installers, release assets, executable metadata, CLI descriptions and documentation use Archive Scout. Binaries are `ArchiveScout` and `ArchiveScoutCLI`; existing Python imports, project filenames and command aliases remain compatible.

## Acquisition and recovery

Backend recovery reservations are released on every exit, including fallback pacing, Stop, response-size rejection, redirect rejection and disk failures. A reachable response rejected by a local size/redirect policy is not recorded as a failed connection. Queued workers recheck healthy connection methods before waiting on a route that failed while they were queued. Logs include the actual backend exception type and short detail.

Failure classification distinguishes pool exhaustion, connection establishment, read timeouts, TLS failures and response-transfer failures. Explicit transient exceptions remain retryable even when their message does not contain a particular English phrase. Storage-full exceptions propagate immediately from transport/client layers; they do not create repeated network attempts.

Text acquisition retains validated raw bytes, hashes and response evidence before local scanning. A bounded share of admission slots services due retries during the initial pass. Future eligible failures are staged in the same file-backed selection but are not admitted early. Ignored/resolved/permanent errors stay out of autonomous recovery. Unique processed captures and logical attempts are separate progress fields. Fixed healthy request pacing remains unchanged.

## Local scanning

Live scanner queries select `downloaded_unscanned` directly. Historical downloaded-without-document repair is a separate bounded operation with a durable per-signature watermark. Scanner wakes no longer repeat that historical join. SQLite busy/snapshot failures retain finished CPU results and retry the whole write batch in a fresh transaction.

Acquisition checks scanner health before admitting new tasks and at regular completion waits. A failed scanner stops new admission and exposes the error while preserving validated bodies. Individual unexpected parser/write defects retain the affected body and error evidence, rather than claiming successful scan coverage. A repaired scanner can resume locally.

Backpressure applies only to the active target/signature scope when retained pending work reaches 4,096 bodies or 512 MiB. Existing in-flight requests are allowed to finish, so this is an admission threshold with bounded in-flight overshoot, not truncation of evidence. Healthy runs do not wait on this threshold. Local scanning never waits on the network recovery gate. Its worker count follows available CPUs and its existing 64 MiB estimated in-flight budget; exceptionally large individual bodies are accepted singly.

## Indexing

Persistent retries keep exact query bounds, collapse semantics and saved cursors. After repeated stalled resume requests, one durable diagnostic response-size trial uses the same membership query and normal transactional insertion/cursor path. The configured larger page size is restored afterward. A bounded independent-task control prevents one stalled target from immediately blocking every other target; shared service failures do not produce unlimited date-window fragmentation. Diagnostic events record exception, status, connection/read flags, phase, target, bounds, response limit and elapsed time.

The year label now displays multi-year bounds correctly. A 2004–2006 request no longer appears as only 2004.

These changes make failures observable and recovery resumable. **The supplied LiveLeak request has not been tested live**, and its HTTP 503 followed by transfer/TLS failure does not prove a particular root cause. Smaller response limits may not reduce server-side filtering/collapse cost. This implementation does not claim that a different endpoint or response size will always make that site answer.

## Media

Forbidden/excluded indexing responses retain an incomplete exact checkpoint and surface the blocker. They cannot silently produce an empty complete inventory. A full media response without a continuation token gets the same bounded alternate-serialization confirmation as text indexing; contradictory continuation cannot advance its checkpoint. Temporary failures preserve page grouping and collapsed selection. Unsupported-pagination fallback requires relevant evidence; a generic 503 does not establish that paging is unsupported. Server-directed wait-budget exhaustion leaves acquisition retryable and does not set the user Stop event. Transient download failures get durable eligibility and recover automatically while persistent retries are enabled, including after restart and above the ordinary attempt limit. Embedded discovery retries preserve its queue too.

Media files are synced before atomic publication. Full disks hard-stop acquisition while preserving progress. Proven retained text still routes away from media according to the existing policy.

Media selection is materialized once into a file-backed ordered queue, then iterated by an indexed `(length,id)` seek. Unknown/zero lengths remain eligible in their original secondary phase. The queue is `WITHOUT ROWID`; avoiding a competing constant range predicate prevents late batches from rescanning earlier lengths. The additive persistent signature/state/length index also helps selected-inventory construction.

Completed main range inventories are reused only when membership/filter/collapse/selection relationships prove sufficient. Arbitrary text filters and incompatible collapsed ranges require their own media inventory. The requested non-text suffix policy is preserved and tested with every suffix even when CDX reports HTML.

## Analysis and maintenance

Duplicate clustering verifies normalized identity, reduces exact groups to representatives, reuses versioned fingerprints and uses a disk-backed BK tree. Hamming-threshold candidate discovery has no 2,000-entry truncation or four-band recall gap. Group membership/parents stay in SQLite. Publication of a finished duplicate generation is transactional, and completed fingerprints survive interruption. Complete matching can still require substantial CPU on adversarial dense populations; no algorithm is claimed to remove the inherent cost of such workloads. It does not run in ordinary acquisition.

Snapshot comparisons strip equal boundaries before character matching. Large changed remainders use an explicitly labeled, order-insensitive upper bound instead of an unbounded quadratic character comparison. The summary includes `similarity_metric` and `similarity_is_upper_bound`; changed-pair counts compare the actual stored bodies, so an upper bound of 1 does not hide a change. Pair checkpoints are keyed by both inputs and algorithm revision. Completed checkpoints survive cancellation; published diffs are replaced atomically only after pair coverage finishes.

Analysis reuses unchanged document/configuration outcomes. Changed documents replace their own derived records transactionally; completed batches survive restart. Forum aggregate metadata is reconciled after processing. Missing source files fail the operation rather than publishing an empty reconstruction. Previously generated report files remain available until new reports are written successfully. The database can contain committed changed-document results from an interrupted analysis; the run is explicitly interrupted/failed and must be resumed before treating it as a completed generation.

Research caches include dimensions, backend/model revision, excerpt policy, entity policy, text, links and URL. Integer evidence revisions detect relevant in-place changes rather than relying on row counts or second-resolution times alone. Unchanged metadata-only document writes do not trigger needless rebuilds. Disabling entities clears the corresponding derived links when refreshed.

URL export uniqueness and integrity reference/findings collections are file-backed. Integrity also verifies retained unscanned bodies. Import enumeration streams directory entries into bounded disk-backed worklists, and raw-byte/parser checkpoints avoid reparsing unchanged imports. Explicit error retries dispatch bounded 500-capture batches. Provenance streams one member at a time and reuses unchanged generations. Timeline callers can use the streaming iterator or paged list API; the historical full-list API remains available for compatibility.

## Migration

Schema **10** adds indexes, derived-work checkpoints, media retry eligibility and revision triggers. Supported schemas 2–9 migrate automatically. A failed pre-migration backup aborts before changing the old schema. Capture/document IDs, source files, scan history, settings, query identities and checkpoints are preserved. Cache cleanup follows removed documents. No schema-13 migration is claimed.

Stop the old app and back up the entire project before upgrading. Reopen the same project folder. Older schema-9 software cannot read the upgraded database; use the pre-upgrade snapshot for rollback. Do not copy only the database file from an active WAL project.

## Validation

Local environment: Linux x86-64, CPython 3.12.14. The canonical suite ran **404 tests: 0 failures, 0 errors, 4 display-dependent skips**. Canonical test output is under `validation/test-results/`. The final summary records exact tests run, failures, errors and skips. Four display-dependent GUI tests skip here; the included GitHub workflow runs the designated GUI regressions under Xvfb on Linux and includes Windows, Intel macOS and Apple Silicon macOS jobs on Python 3.11/3.12.

Additional regressions cover permit cleanup, storage-full propagation, additive upgrade/failed backup, pending-query plan, legacy watermark, forbidden media completeness, outage semantics, newly due retries, scanner supervision, research invalidation, repeat import, duplicate exact reduction/large-bucket/all-band recall, bounded diff, media ordering/automatic recovery, ignored failures, diagnostic cursor preservation, independent target control, compatible/incompatible range reuse, and all requested non-text suffixes.

Measured fixtures:

| Check | Result |
|---|---|
| 480 small localhost captures | 480 raw hashes, documents and scan outcomes verified; 60.002 s; **8.000 saves/s** |
| Small early/middle/late thirds | **8.022 / 7.990 / 7.989 saves/s**; final local scan drain 0.004 s |
| Small sampled RSS thirds | 29.38–38.84 / 38.71–39.04 / 38.98–39.24 MiB; maximum 15 total threads including fixture infrastructure |
| 240 mixed localhost captures | 4 KiB–1 MiB bodies; all hashes/documents/outcomes verified; 30.034 s; **7.991 saves/s** including final scan drain |
| Mixed early/middle/late thirds | **8.059 / 7.989 / 7.990 saves/s**; final scan drain 0.082 s |
| Mixed sampled RSS thirds | 29.79–45.14 / 43.72–65.82 / 66.13–101.04 MiB; later bodies are deliberately larger |
| One million historical captures | Pending count 0.0073 ms; first pending lookup 0.0234 ms; old count predicate on the same database 370.3719 ms |
| One million media rows | One-time queue construction 367.801 ms; indexed early/middle/late 1,000-ID lookups **0.3219 / 0.4485 / 0.3458 ms** |
| Offline benchmark smoke | 1,000 CDX rows / 100 results / 1 KiB bodies; passed; unchanged CDX writes: 0 |

Million-row results measure SQLite selection, not one million real downloads. Media timings above select IDs; production row materialization includes additional metadata. Fixture construction disables journaling/sync only in disposable benchmark databases, never in app settings. Its peak RSS includes bulk construction and SQLite mapping; it is not a measured overnight acquisition footprint.

Source compilation, release alignment, shell build-script syntax, wheel construction and installed-wheel CLI/asset smoke checks are recorded with final evidence. Hosted CI, actual Windows/macOS executables, native GUI behavior in those environments, live LiveLeak indexing, overnight/multi-day Wayback stability, optional remote AI providers and FastEmbed model execution are **not** locally verified. The test workflow is included; no claim is made that remote jobs have already run.

The changes address demonstrated correctness, recovery and scaling defects. They establish neither a numerical “last 1%” distance from an optimum nor a universal eight-saves/s guarantee under all archive and hardware conditions. Further fundamental changes should follow new reproducible evidence, not speculative rewrites or relaxation of preservation guarantees.
