# Final validation evidence

`test-results/summary.json` and `tests.log` record the canonical 404-test result (0 failures/errors, 4 display-dependent skips). `release-checks.json` states exactly what was and was not verified.

The localhost JSON files contain actual hash-verified retained saves, scanning coverage and early/middle/late resource samples. `query-growth.json` records 100k/500k/1m SQLite selection fixtures, not real downloads. Its peak RSS includes bulk construction. Media batch timings select IDs; full production rows include more metadata. See `docs/FINAL_FUNDAMENTALS_1_2_3.md` for contracts and limits.

Reproduce after installing the source: `python scripts/run_tests.py --output validation/test-results`, `python scripts/verify_release.py`, `python scripts/benchmark_loopback.py --count 480`, `python scripts/benchmark_loopback.py --count 240 --mixed`, and `python scripts/benchmark_growth.py`. Growth fixture construction disables sync/journaling only in disposable test databases. It requires enough scratch disk for a million-row fixture.

Installed wheel imports were checked outside the source directory with compatible local dependencies. Hosted builds, live service conditions and overnight stability remain unverified.
