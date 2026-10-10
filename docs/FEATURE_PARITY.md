# v1.1.1 feature parity and compatibility

The complete user-supplied `archive-scout-1.1.1.zip` was inspected. This document distinguishes **working lean features** from features that are **not restored**. Do not interpret the candidate as a drop-in v1.1.1 replacement.

| Feature | Lean candidate | Notes |
| --- | --- | --- |
| Parallel Timemap, page-count, 10 page workers, saved index plans | **Retained from v1.0.5** | Same v1.0.5 scheduler, CDX default spacing changed to 2.5 s |
| Resume-key fallback and error/retry queues | **Retained and adjusted** | Automatic transient recovery; strong durable page progress |
| Primary text download/scanning engine | **v1.0.5 + correctness fixes** | Fast original-byte save, post-download full-source scan, validation; durable unscanned queue |
| Media image/video downloader and embedded discovery | **Retained from v1.0.5** | Not identical to all later v1.1.1 classification rules |
| Project dashboard, targets, keywords, CDX, media, analysis, settings, results, AI, research, scan history, errors, activity | **Retained from v1.0.5** | Already available; not all newer controls or filters restored |
| Scrolling/focus/wheel improvements | **Ported from v1.1.1 widget source** | GUI pages use responsive vertical/horizontal scroll containers |
| Dedicated Reports workspace | **Restored lean text reports** | File/field selection, presets, sorting, output limits, and classification/routing fields; not full schema-13 per-operation fields |
| Indexed-only reports | **Retained from v1.0.5** | Plain inventory/summary/error files |
| Manual AI relevance and local Research Intelligence | **Retained from v1.0.5** | Auto-build off for new projects to remove extra ordinary run work |
| Newer schema-13 classification inventory/evidence tables | **Partially restored** | Lightweight indexed classification plus payload routing in a new schema-8 table; operation-scoped schema-13 evidence not ported |
| 1.1.1 Hitlist resume/cursor and scan detail retention options | **Not ported** | Old rescan/search still available; not equivalent |
| 1.1.1 report field presets and extended report formats | **Partially restored** | Text/index reports now configurable; schema-13 only fields and later report formats remain unported |
| 1.1.1 mode variants such as download-only text without scanning | **Not fully ported** | Original v1.0.5 Download performs scanning; use mode descriptions carefully |
| Later schema-13 FTS/revision/lease implementations | **Not ported** | Current v1.0.5 FTS remains, no database downgrade |
| 1.1.1 revised network/transport fleet | **Not ported** | Simplified v1.0.5 pool and recovery are intentional |

A later full-parity release would need a schema compatibility/migration design, explicit feature-by-feature API mapping, GUI action tests and representative real-project validation before promising exact v1.1.1 parity.
