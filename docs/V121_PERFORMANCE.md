# v1.2.1 performance and fidelity gates (2026-10-10)

- Scope: additive GUI, config, and post-operation report changes on v1.2.0's lean acquisition/scanner. Fixed CDX spacing 2.5s and replay spacing 0.125s are unchanged.
- Local localhost 90-capture benchmark (full save/scan/hash, no Internet): v1.2.0 8.036/s, v1.2.1 8.039/s, 90/90 verified both. The ~0.003/s difference is noise, **not evidence of an improvement**. Only 11-second healthy runs.
- 40,000-row offline benchmark (single run each; results subject to cache/scheduler noise): v1.2.0 CDX parse 0.955s, initial upsert 1.507s, repeat no-op 1.328s; v1.2.1 parse 0.961s, initial upsert 1.651s, no-op 1.370s. This suggests a possible 10% initial-upsert regression in this single fixture, **not established**; neither indexing storage nor selection was modified in the patch. Repeat on identical loaded conditions before assigning cause.
- Indexing strategy is performance-sensitive: auto now prefers resume-key traversal as in v1.1.1. It avoids page-count/sparse-page overhead but can serialize dense inventories. Explicit paged mode and unfinished queued page checkpoints remain available. Comparative live Timemap/numbered-page vs resume-key benchmarks were **not run**. Do not imply no indexing regression.
- Report UI configuration and formatting happen only when generating reports, not per downloaded capture. Disabling outputs avoids streaming their result rows. Report generation runtime against equal large projects remains unmeasured.
- GUI smoke tested using Tk/Xvfb at 940×680, 14 pages, constrained sidebar. Native Windows precision touchpad, macOS UI and DPI scaling unverified.
- Local Python unittest suite: 208 tests, zero failures, 3 skips; compilation and release/source identity verification should run before patch release. Actual hosted GitHub Actions matrix not run here.
- v1.1.1 schema-13 capture classification inventory / full evidence routing was not backported: text/media differentiation remains v1.2.0 level; a full feature-parity claim is not warranted.

**Release decision:** candidate only. No demonstrated hot-path slowdown in the short local replay test, but both the unverified dense-indexing risk and slightly slower single-run offline upsert require larger A/B tests and explicit user review before claims of equal sustained performance.

## Final patch revalidation

- 213 local unit/integration tests: 210 passed, three skipped. Source compiles.
- Localhost HTTP 300-capture end-to-end replay: 300/300 saved, committed, locally scanned and SHA-256 checked, zero expected skips. Acquisition to last committed save 37.496 seconds = **8.001 newly saved/s**. Early/middle/late acquisition 8.025 / 7.989 / 7.989. Local scan drain 0.398 seconds; whole-operation 37.894 seconds = 7.917/s.
- Small separate 90-capture run: acquisition 8.034/s, 0.134-second scan drain; whole-operation 7.939/s. A 120-capture comparison produced 8.026 acquisition saves/s.
- Heavy full-source parsing now occurs *after* acquisition, not inside network worker slots. Classification is prepared before downloads, and dashboard classification GROUP BY is rate-limited to once per minute while the GUI is active. Scanner futures are bounded by worker count and estimated in-flight bytes, with oversized single files still allowed.
- Source-matched 1.1.1 strategy preferences and Reports GUI are included; full v1.1.1 indexing, GUI and schema-13 feature parity is **not** claimed. No 100k/1m large-data workload, cross-platform native GUI, remote IA outage, or multi-day live-service run was performed.
