# Archive Scout v1.2.1 — patch installation

**Base required:** `ArchiveScout-v1.2.0-Lean-Complete-Repository.zip` (the complete original lean repository). This is a *root-relative overlay*, not a complete source repository and not a patch on v1.1.1 or v1.1.3. It also includes everything from the earlier v1.2.1 candidate patch: **do not apply the candidate separately**.

1. Back up your project folders and existing v1.2.0 source first.
2. Extract the complete v1.2.0 repository.
3. Extract this ZIP **over the repository root**, keeping relative directories and replacing modified files.
4. Commit the changed files to GitHub. The included `.github/workflows/tests.yml` runs the existing CI matrix.
5. Run `python -m compileall -q archive_scout tests scripts`, `python scripts/verify_release.py`, then `python scripts/run_tests.py --output validation/test-results`.

## Changes

- Retains the v1.1.1 automatic resume-key indexing preference, while preserving existing paged Timemap checkpoints and explicit paged mode. CDX admission is fixed at **2.5 seconds/start**.
- Keeps the lean ten-worker, fixed **0.125-second replay admission** acquisition engine, with newly committed fresh-save counters.
- Moves full HTML parsing and keyword matching **out of the network acquisition workers** and into a bounded, durable saved-but-unscanned local stage. Complete body/source matching and original bytes remain intact.
- Adds classification inventory and routing evidence at indexing/preparation time, without requiring a scan of the entire project inside every replay worker. An unexpectedly encountered image/video is **deferred to the media index**, not written as `.txt` or recorded as a network error.
- Adds indexed text/images/videos/audio/media descriptors/other binary/unknown totals, route states and report fields. Expensive aggregate totals are refreshed sparingly, not with each capture save.
- Retains v1.1.1-style exclusive GUI keyword selection, Reports customization, accessible scrolling, input borders and layout fixes.

## Database and evidence compatibility

**New schema version: 8**, up from v1.2.0 schema 7, adding only durable `capture_routing` evidence. Earlier supported schema 2–7 projects auto-upgrade; a safety backup is attempted before upgrading an existing v7 project. This is *not* a migration/downgrade path for v1.1.1/v1.1.3 schema-13 projects. Do not point v1.2.1 at those projects.

All text files remain stored as original replay bytes; keyword source coverage is not truncated. `downloaded_unscanned` bodies remain available for local recovery after interruption. Metadata classification alone is not proof of payload type; conflicting candidates undergo replay validation.

## Performance and validation

- 213 local unit/integration tests, **210 passed**, 3 skipped; compilation and release-identity checks.
- Localhost 90-file baseline: v1.2.0 ~8.036/s, v1.2.1 acquisition ~8.034/s in separate short runs.
- Localhost 300-file run: **8.001 fresh saved/committed captures/s acquisition**, early/middle/late 8.025/7.989/7.989; 300/300 bytes and scan results verified; separate 0.398-second local scan drain. Whole-operation 7.917/s.
- These are **short localhost tests**, not a sustained Internet Archive run. No hosted Windows/macOS CI, actual precision touchpad, million-capture load or overnight live-service soak was executed. Exact 1.1.1 GUI, database feature, and indexing-range-scope parity is **not** complete. See `docs/FEATURE_PARITY.md` and `docs/V121_PERFORMANCE.md`.

The work does not add adaptive pacing, growing application cooldowns, periodic intentional pauses, or extra healthy replay probes. Honor actual service `Retry-After` deadlines.
