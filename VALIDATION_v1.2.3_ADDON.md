# Archive Scout v1.2.3 GUI/CI add-on validation

Base: the supplied `ArchiveScout-v1.2.3-Patch-Files.zip`, applied **after** the complete v1.2.0 repository, the final v1.2.1 patch, and the v1.2.2 patch. The add-on leaves the application version at **1.2.3**, database schema **9**.

## Changes

- Restrains the navigation sidebar to a readable 224-pixel width rather than allowing long child captions to expand it.
- Makes the Media sites/paths, included extensions and excluded extensions editors share available space equally; places editor labels above their corresponding box.
- Wraps Media options and descriptions to avoid wide clipped content on narrow application windows.
- Adds a subprocess-isolated Tk regression for 940 × 680 and 1280 × 720 layouts, with safe display-dependent skips.
- Runs GUI regressions on a virtual Linux desktop in GitHub Actions in addition to the existing Windows, Linux and macOS test matrix.
- Regenerates the release's source SHA-256 inventory to reflect the already-supplied v1.2.3 tree and the add-on.

## Commands and actual local results

Environment: Linux, Python 3.13.5, Xvfb 1280×800. The work was performed on the **assembled v1.2.3 source**.

- `python -m compileall -q archive_scout tests scripts` — passed.
- `python scripts/verify_release.py --source-only` — passed; v1.2.3.
- `xvfb-run -a -s '-screen 0 1280x800x24' python -m unittest tests.unit.test_v123_ci_layout tests.unit.test_v123_restoration.GuiRestorationTests tests.unit.test_v122_cdx_gui_speed.GUIThemeTests -v` — 3 tests passed.
- `xvfb-run -a -s '-screen 0 1280x800x24' python scripts/run_tests.py --output validation/v123-addon-tests` — **236 tests run, 234 passed, 0 failed, 0 errors, 2 skipped** (optional native accelerator tests were skipped in this environment).
- `python scripts/benchmark_loopback.py --count 120 --output validation/v123-addon-loopback.json` — 120 of 120 bodies validated, SHA-256 verified; **8.028 newly saved captures/s during acquisition**, **7.948/s inclusive of local scan drain**. Early/middle/late acquisition segments were 8.104 / 7.991 / 7.991 saves/s.
- `python scripts/benchmark_offline.py --cdx-rows 1000 --result-rows 100 --body-bytes 1024` — passed before the add-on source change; CDX/acquisition code is unchanged by this add-on.

The add-on does not alter CDX/replay pacing, indexing, transport, database, or scanning behavior. The local speed test is not evidence of multi-day live Wayback performance.

## Still unverified

- Actual GitHub-hosted Windows 2022 and macOS 15 runner outcomes and Windows touchpad behavior.
- Live Internet Archive rate-limit recovery over long runs.
- Performance and memory on million-capture project databases over days.

**GitHub workflow:** `.github/workflows/tests.yml`. It runs the canonical suite on Ubuntu 22.04, Windows 2022, macOS 15 Intel and macOS 15 ARM with Python 3.11/3.12, and an additional Linux Xvfb GUI test step. Results and logs are uploaded as artifacts. Do not describe hosted CI as passing until GitHub reports successful jobs.
