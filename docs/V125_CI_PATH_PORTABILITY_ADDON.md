# Archive Scout v1.2.5 CI path-portability add-on

Apply this ZIP over the repository that already contains the Completeness and
Performance patch. Preserve the tests/ and docs/ folders. Replace
tests/unit/test_v125_completeness_patch.py and add this note. No version bump,
database migration, application code change or workflow relaxation is needed.

## Finding

Failed run: https://github.com/Memory-of-Time/archive-scout-testing/actions/runs/40039655380
Revision: f7117c9771ea503e12fabb2740776b498dbf20a0.

All six failed jobs (Windows, macOS ARM and macOS Intel; Python 3.11/3.12)
reported exactly the same two failures. Both Ubuntu jobs passed. The six
uploaded tests.log artifacts were inspected, not just the workflow summaries.
The failing methods were:

- ProofRecovery.test_process_exit_after_receipt_before_publication_recovers_staging
- ProofRecovery.test_process_exit_after_publication_before_sql_recovers_body

The fault injector built its target from an unresolved temporary project path.
The downloader builds its destination from ProjectConfig.normalized().output_dir.
Different spellings of the same path therefore prevented the injected os._exit
from firing. Each subprocess returned 0 instead of the required 71 or 72. macOS
/var aliases and Windows temporary short paths are examples of paths affected
by this faulty comparison. The source comparison and portable reproduction
establish the normalization mismatch; individual runner path aliases were not
logged by the original tests.

## Fix and regression strength

The child now derives its hook destination from cfg.output_dir, exactly as the
downloader does. Every crash case also receives a valid project path containing
an existing directory followed by '..', so the normalization mismatch is
exercised on Linux as well. This avoids depending on incidental host paths.
The same two failures reproduced locally with the alternate spelling before
the hook correction. All 23 focused tests passed after it.

No skips, assertions, exit boundaries, digest checks, staging recovery checks,
SQL evidence checks or receipt-cleanup checks were removed. All three abrupt
exit boundaries still require their specific exit codes and verified recovery.
The application, acquisition cadence, scanning, retry scheduling and saved
project state are unaffected. This add-on does not increase acquisition speed.

## Validation

Final canonical command:
python scripts/run_tests.py --output ../validation/test-results

```json
{
  "version": "1.2.5",
  "generated_utc": "2026-10-23T23:32:44.735032+00:00",
  "platform": "Linux-6.18.55-x86_64-with-glibc2.39",
  "python": "3.12.14 (main, Aug 25 2026, 14:00:49) [Clang 22.1.3 ]",
  "tests_run": 504,
  "failures": 0,
  "errors": 0,
  "skipped": 4,
  "successful": true,
  "test_environment": "Local fixture and mock traffic; live Wayback throughput not tested"
}
```

Release metadata/workflow consistency verification and compilation of the
changed test module also passed. The local environment initially lacked the
socksio dependency required by its configured SOCKS proxy; three unrelated
test setup errors were resolved by installing that dependency before the final
run. No project dependency or application change was made for that local setup.

Native macOS/Windows reruns have not been executed with this add-on. Re-run the
Tests workflow after uploading it. No live-throughput or overnight claim is
made for this test-only correction.
