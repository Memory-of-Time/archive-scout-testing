# Archive Scout 1.2.0 — Lean rebuild candidate

This is a **source-only release candidate** built from the real 2026-09-12 v1.0.5 repository and selectively adapted from the supplied complete v1.1.1 source. See `docs/LEAN_REBUILD_AUDIT.md` for verified differences, tests, and remaining validation needs.

- 2.5 s shared CDX spacing, 0.125 s replay spacing, and v1.0.5 parallel Timemap paging.
- Complete raw-source scanning, strict CDX row validation, better text/media prefix detection, exact-byte atomic saves, and permanent progress tracking.
- Automatic retries of eligible temporary failures, fixed 429 fallback when no Retry-After, and host-directed waits.
- GUI pages scroll vertically and horizontally and offer a Reports workspace based on the existing v1.0.5 report exporter.
- No adaptive global rate controller or extra periodic waits.

**Compatibility warning:** schema 7 is retained. Never open or downgrade v1.1.1/schema-13 projects with this build. The newer GUI/schema-13 features not explicitly restored remain absent.

**Not verified:** Hosted CI, live public Wayback throughput, overnight durability, exact user-configuration compatibility, native Windows touchpad behavior.
