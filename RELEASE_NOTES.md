# Archive Scout v1.2.1 — Lean engine with targeted feature restoration

Patch release against the authentic v1.2.0 lean repository. **Database schema 8** adds lightweight capture classification/routing evidence and safely migrates supported schema 2–7 projects. It **does not open schema-13 projects** from v1.1.1/v1.1.3.

- Original 10-worker lean downloader and 0.125-second fixed replay spacing remain. Full local keyword scanning is now a separate post-acquisition stage. Partial scan backlogs remain durable and resumable; source bytes/hashes are preserved.
- 2.5-second fixed CDX spacing; 1.1.1 automatic resume-key strategy preference; incomplete old parallel page plans remain resumable.
- Preliminary classification before acquisition; payload signature verification; detected media deferred into media selection rather than reported as a failed text download. Media remains subject to enabled image/video and snapshot-selection controls.
- Readable classification counts for text, image, video, audio, descriptor, other binary and unknown; downloadable routing evidence in all-indexed-URLs reports, generated only when requested.
- Exclusive GUI keyword-set selection, customizable Reports tab, scrolling/borders, and responsive sidebar restored in the v1.2.1 candidate are retained.
- Database and GUI classification aggregates are batched / cached and never inserted into each healthy replay slot.

**Local validation:** 213 tests, 210 passed, three skipped; one 300-file localhost acquisition at 8.001 successful committed saves/s, plus 0.398-second independent scan drain, all bytes and matches verified. This does not establish overnight Internet Archive throughput; hosted CI must still run.

**Feature-parity limits:** This is *not* a wholesale transplant of v1.1.1, because that would reinstate its schema-13 processing and network architecture. Several later indexing range-coverage semantics, GUI workspaces, and Hitlist features remain unported. See `docs/FEATURE_PARITY.md`. Keep older installations/projects intact during evaluation.
