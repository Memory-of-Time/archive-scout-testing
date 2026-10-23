# Archive Scout v1.2.5: completeness and acquisition performance patch

This patch applies to `archive-scout-main(20261023-222935).zip`, SHA-256
`2f52ce18a6fd8be38377dd14cd8eea378f14ee6917f354ccbeb47744e879988c`.
Version 1.2.5, schema 10, project identities, existing SQLite tables, and CLI
progress cadence remain unchanged. Apply these files over that repository,
preserving their folders. This builds on the recovery/redirect and connection
add-ons already present in that baseline; it does not replace them with an older
release. The companion baseline audit documents findings before this patch.

## Completion proof and crash recovery

Readable HTML and a capture-shaped filename are insufficient evidence of a
completed transfer. Both production streaming and the compatible memory path
now publish a short-lived capture-bound validation receipt before publishing
the retained body. The receipt records the validated transfer's raw SHA-256,
size, capture ID, original URL, timestamp, and response metadata. The existing
transport checks, payload routing, and archive-shell checks run first. Staging
bytes and receipt bytes are synchronized; the retained-file rename is followed
by directory synchronization on supported POSIX filesystems.

The receipt is deleted only after SQLite commits the raw-byte evidence and
capture state. If a process exits in the publication/commit gap, recovery checks
the entire actual file against that proof. Validated staging bytes can also be
published and recovered after an exit between receipt creation and publication.
An interrupted post-commit cleanup does not lose database proof; later local
scanning also cleans that receipt. Cleanup errors do not undo a committed save.
Receipt storage during ordinary acquisition is limited to in-flight work, not
one permanent metadata file per capture. A process killed during cleanup can
leave a small receipt residue until later scanning or maintenance.

Recovery accepts matching database SHA-256/size evidence, a matching
capture-bound validation receipt, or a valid matching CDX SHA-1 digest for a
legacy file lacking the stronger proof. A database-hash mismatch cannot be
bypassed simply by trusting weaker CDX metadata. A validated newer receipt may
prove a replacement transfer. Missing, altered, malformed, unrelated, or
unprovable files never become successful saves based on a text preview.

Questionable bytes are preserved with an `.unverified-<SHA256>` suffix for
inspection; the capture remains unfinished and eligible for normal automatic
acquisition. Existing unproven saved/unscanned rows are also reconsidered.
Missing/unreadable unproven saved files create explicit scan gaps. Local scanning
checks proof before accepting an unproven retained file. Legacy files without
sufficient evidence may consequently require reacquisition. This preserves
capture identities and historical settings rather than claiming unverified
bytes are complete.

The acquisition owner's local commit-failure rescue now records retained-body
proof/state and its scan error in one transaction. The scanner cannot finish a
body and then have a later error write downgrade it. Successful scanning and
Rescan resolve capture-scoped errors even when those errors were recorded before
a document ID existed. This prevents stale NULL-document errors from stranding
an otherwise correctly recovered operation.

These are process-crash and integrity guarantees under the tested filesystem
conditions. Physical power loss, faulty storage, and native Windows/macOS
durability were not tested. Windows has no POSIX directory-fsync path. Existing
SQLite durability settings were not weakened. Proof that cannot be established
causes unfinished work/reacquisition, never assumed completion.

## Retry selection

One shared owner-only helper selects due text retries from the due-time schedule
index, looks up capture/error evidence using capture-specific indexes, and keeps
the exact active-scope, membership, state, open retryable download-error, queue
exclusion, and deadline predicates. Stable ordering uses the equivalent schedule
capture ID to avoid a redundant tie sort. No lifetime retry ceiling, new adaptive
pause, new request pacing delay, or relaxed indexing gate is introduced.

A regression seeds 10,000 active due errors and limits SQLite VM work. Selection
of the first eligible retry must fit the instruction budget, independent of
machine speed. Inactive prefixes can still require work, as the baseline audit
explains. This is not a universal constant-time claim for every queue layout.

## GUI updates and diagnostic evidence

The Dashboard exposes **Acquisition updates: 0.5 / 1 seconds**, defaulting to
0.5. This is an appearance preference. It does not affect CDX query identity,
project scope, capture selection, saved settings for interrupted acquisition,
network workers, durable commits, or CLI JSON/JSONL callbacks.

Only routine acquisition display snapshots are sampled. There is one newest
pending snapshot, an idle-time flush through the existing UI event pump, and a
forced final snapshot before completion, interruption, deferral, or error
handling. Starting another run resets the presentation slot, not database work.
Indexing/media/scan progress and notices continue to update their existing UI
controls. Error/retry/phase notices cannot be overwritten by routine acquisition
progress. If a busy GUI fills the bounded notice queue, omitted notices are
explicitly counted; the acquisition producer does not block on GUI repainting.
Per-capture error evidence remains in SQLite.

The first occurrence of each acquisition failure category includes a concise
representative exception. Failure streams emit categorized health summaries
approximately every 30 seconds even when requests keep completing unsuccessfully.
Those summaries also enter the existing bounded network incident history with
durable aggregate summaries, independently of GUI consumption. Event-generation
time is attached to GUI events and used by its activity log.

Progress details additionally distinguish shared database-lock waiting from the
`save_success` body/receipt cleanup cost and report retry-probe counts/time. The
legacy combined commit timer remains available for compatible consumers. No
project-wide counter query was added per successful save.

The latest supplied activity log's zero-save failure storm cannot be assigned a
verified root cause from its old generic messages. This patch preserves automatic
recovery and records the evidence needed to distinguish connection, pool,
response, validation, and local commit failures. It does not claim to repair an
unidentified Internet Archive/service/client failure by reducing repainting.

## Preserved behavior and validation

Indexing coverage barriers, text/media suffix routing, pre-acquisition
`robots.txt` exclusion, redirect-off refusal at the first redirect, media
discovery/coverage gates, report generation, keyword coverage including score
zero, retention policy, and operation resume identities remain in place.
Large-project historical data are not cleared or reindexed by this patch.
Temporary failures retain retryable obligations. Storage full remains a hard
blocker. The tests exercise disk-full publication refusal and ordinary
interruptions alongside process exits at three publication/commit boundaries.

The final overlay runs 504 tests with zero failures/errors and four skipped GUI
tests on Linux/Python 3.12. The three older fixture files changed by the patch now
supply real CDX digest evidence; their recovery assertions remain intact.
Additional regressions cover unproven/truncated files, receipt identity/corruption,
staging recovery, local commit failure, stale scan errors, GUI cadence/overflow,
diagnostic persistence, and retry-query scalability.

The accompanying validation report records measured throughput, fixture limits,
installation/release checks, and remaining platform/live-service limits. Local
fixture results do not establish sustained overnight performance against Wayback.
Broad write batching, cache shrinking, worker reductions, and removal of evidence
or scanning obligations were deliberately not used as performance shortcuts.
