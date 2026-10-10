ARCHIVE SCOUT v1.0.5: CI + DEFAULT INDEXING SPACING PATCH

BASE: Reconstructed historical September 12, 2026 Archive Scout v1.0.5.
PATCH TYPE: Changed files only, not a full repository. Files use repository-relative paths.

FIXES
1. GitHub Actions Tests workflow: compare installed package version to pyproject.toml,
   instead of the stale hard-coded 1.0.4 check that failed all eight jobs.
2. CDX/indexing default: 2.5 request starts per second (0.4 seconds between starts).
   This is a request-start limit, not a guarantee of responses/snapshots per second.
3. Update GUI new-project spacing setting to 0.4 and clarify its rate label.
4. Preserve already saved/customized CDX delay values (e.g., 0.75 seconds).
5. Update historical assertions for new defaults and add saved-settings tests.

FILES TO COPY INTO YOUR GITHUB REPOSITORY (REPLACE SAME PATHS)
.github/workflows/tests.yml
archive_scout/config.py
archive_scout/ui/main_window.py
tests/unit/test_network_tuning.py
tests/unit/test_v105_release.py

You can upload files preserving directories, or apply the separate .patch with:
  git apply Archive-Scout-v1.0.5-CI-and-2.5rps.patch

VALIDATION ON LOCAL LINUX / PYTHON 3.13.5
- python -m unittest discover -s tests -p 'test_*.py' -v:
  198 run, 195 passed, 3 skipped, 0 failed
- python -m compileall -q archive_scout tests scripts/benchmark_offline.py: PASS
- python scripts/benchmark_offline.py --cdx-rows 1000 --result-rows 100 --body-bytes 1024: PASS
- git apply --check against historical v1.0.5 repository: PASS
- apply and compare five patched files byte-for-byte: PASS

CI LIMITATION: GitHub-hosted Windows/macOS and Python 3.11/3.12 matrix runs were
NOT re-run on this patch, because these patch files have not been uploaded to
GitHub. Passing local tests does not establish live CI success or 2.5 req/s
under service throttling. The observed eight CI failures were solely caused
by the stale 1.0.4 package version assertion before any tests could run.

EXISTING PROJECTS: Saved project.json cdx_delay remains authoritative. To
apply the new pacing to an existing project, manually set the CDX request
spacing field to 0.4 seconds. New project defaults are 0.4 seconds.

No download-rate or version number changes are included.
