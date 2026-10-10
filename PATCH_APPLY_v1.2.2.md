# Apply Archive Scout v1.2.2 patch

1. Back up your existing source repository and any project databases. This patch **does not** change the DB schema.
2. Start from the **complete v1.2.1 repository** (v1.2.0 full ZIP with final v1.2.1 patch overlaid). Do **not** apply this ZIP to original v1.0.5 or to v1.1.x.
3. Extract this overlay at the repository root, preserving paths and replacing the listed files.
4. To validate locally:

   ```bash
   python -m compileall -q archive_scout tests scripts
   python scripts/verify_release.py
   python scripts/run_tests.py --output validation/test-results
   ```

5. Push the changed files to GitHub to run `.github/workflows/tests.yml` on Windows 2022, Ubuntu 22.04, and macOS 15 (Intel/ARM) with Python 3.11 and 3.12. **Local test success is not a claim those hosted jobs passed.**

After installation, open a project and click **Refresh dashboard** to show saved capture and unique matching-page totals. They intentionally do not update during active runs. Activity displays a recent 30-second success rate and a separately labeled whole-pass rate.

The local benchmarks use a loopback server and do not verify the public Wayback service over multi-day runs.
