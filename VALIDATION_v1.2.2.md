# Archive Scout v1.2.2 — local validation

Scope: ZIP overlay on the authentic complete v1.2.1 repository (v1.2.0 base + final v1.2.1 patch).

- Canonical local test runner: **219 tests, 215 passed, 4 skipped, 0 failed, 0 errors** (Linux Python 3.13.5).
- `python -m compileall -q archive_scout tests scripts`: PASS.
- `python scripts/verify_release.py`: PASS, v1.2.2 schema 8.
- Native Timemap JSON, JSON sniffing, malformed CDX rejection, dashboard page counts, manual-only refresh and Tk canvas theme regression tests: PASS (GUI theme test skipped on headless Linux).
- Headless Xvfb/Tk smoke: Dashboard, Media and Activity load at 1280x720. Scrollable canvases use the dark background. Media requested body width ~811 pixels inside a ~1041-pixel canvas.
- v1.2.1 baseline localhost 90 captures: 8.039 acquisition saves/s; candidate 90 captures: 8.034/s. SHA-256 checked for 90/90 on both.
- Candidate 300 localhost captures (instrumented): **7.999 acquisition saves/s**. Early/middle/late: **8.029 / 7.988 / 7.982 saves/s**. Scan drain 0.452 s. 300/300 hash-verified. This instrumented run completed successfully; the first unattended 300-file invocation timed out in the execution environment without a returned result and was NOT counted as a pass.
- No real Internet Archive request, overnight soak, GitHub-hosted Windows/macOS CI, or million-capture validation executed. Hosting provider throttles may reduce rates below 8/s. No new adaptive pacing or intentional pauses were introduced.
- Tests are source/fixture-based; the supplied GitHub Actions matrix is included for hosted validation after pushing the patch.
