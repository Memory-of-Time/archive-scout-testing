# Archive Scout 1.2.3

**Archive Scout** is a cross-platform desktop and command-line workspace for finding, preserving, downloading, searching, and reviewing public Wayback Machine captures.

### Download Archive Scout

| Windows | macOS | Linux |
|---|---|---|
| [**Download for Windows (x64)**](https://github.com/Memory-of-Time/archive-scout/releases/latest/download/ArchiveScout-Windows-x64.zip) | [**Download for macOS (Universal)**](https://github.com/Memory-of-Time/archive-scout/releases/latest/download/ArchiveScout-macOS-Universal.zip) | [**Download for Linux (x64)**](https://github.com/Memory-of-Time/archive-scout/releases/latest/download/ArchiveScout-Linux-x64.tar.gz) |

[All releases](https://github.com/Memory-of-Time/archive-scout/releases) · [Report an issue](https://github.com/Memory-of-Time/archive-scout/issues)

> Release download links work only after the matching assets are published on GitHub. The build workflow defines these filenames; a successful local test does not mean binaries have been published.

## What Archive Scout does

- Index Wayback CDX inventories with restartable resume-key and paged traversal, query compatibility, and durable checkpoints.
- Download eligible captures with fixed request pacing, resilient network transports, and separate local keyword scanning.
- **Index and download only (no scanning)** or retry failed acquisition independently of keyword sets.
- Explain blocked acquisition using passive stall diagnostics, with optional (default-off) coordinated host connection recovery.
- Classify text and media, optionally retrieve images and video, follow approved archived redirects, and discover embedded media.
- Search stored files and indexed URLs using keyword sets and an optional resumable Hitlist; review results and export reports.
- Maintain project databases, diagnostics, backups, integrity tools, analysis, and optional AI research tools.

**Performance:** Archive Scout's healthy replay start clock defaults to 0.125 seconds (nominal eight requests/s), but successful saves depend on network and archive availability. No adaptive request-rate escalation is used. A local benchmark cannot guarantee live Wayback throughput.

## Requirements and installation

Use the linked platform builds once the release is published. On Windows, run `ArchiveScout.exe` inside the extracted `ArchiveScout` folder (or the included `Install Archive Scout.cmd`). On macOS, extract the ZIP and launch `ArchiveScout.app`. On Linux, extract the archive and use its `install.sh` script or launch the contained binary directly. Consult `packaging/` for installation details and checksum verification. Unsigned Windows builds may show SmartScreen prompts; do not disable antivirus protection.

For source installations, Python 3.11 or 3.12 and Tk are recommended:

```bash
python -m pip install .
archive-scout-gui
archive-scout --help
```

The legacy `scout` and `scout-gui` entry points remain available to existing automations. Internally, Python imports remain `archive_scout` to preserve project and integration compatibility; that does not change the public **Archive Scout** name.

## First project

1. Choose a project folder, target URL patterns, date range and operation.
2. Choose **Index and download only** to preserve text without scanning, or use the full index/download/scan workflow with a keyword set.
3. Review results and generate reports. Use **Refresh dashboard** to update the summary counters manually.
4. If a service outage interrupts work, pause and resume in the **same project folder** to preserve checkpoints. Acquisition stalls over 30 seconds now surface worker/host-gate diagnostics in Activity without extra network requests.

Supported schema-9 projects migrate additively to schema 10. Schema-13 projects created by historical releases cannot be opened in this codebase; preserve their backups. Imported files are copied into project-owned storage, and moved schema-9 projects can rebase previously saved internal file paths on opening. See [Migration](docs/MIGRATION.md).

## Development

```bash
python -m pip install .
python scripts/verify_release.py
python scripts/run_tests.py --output validation/test-results
python scripts/benchmark_offline.py --cdx-rows 1000 --result-rows 100 --body-bytes 1024
```

The [test matrix](.github/workflows/tests.yml) covers Python 3.11/3.12 on Windows, Linux, Intel macOS and Apple Silicon macOS. [Build and release](.github/workflows/build-and-release.yml) packages platform executables and uploads matching assets to tagged GitHub releases. Published binaries require those hosted jobs to complete successfully; local tests alone are not proof of cross-platform builds.

Source overview: [`archive_scout/`](archive_scout/) application code; [`tests/`](tests/) regression tests; [`scripts/`](scripts/) benchmarking/build automation; [`packaging/`](packaging/) OS setup; [`docs/`](docs/) operational and developer guides. See [Architecture](docs/ARCHITECTURE.md), [Operations](docs/OPERATIONS.md), [Indexing and recovery](docs/INDEXING_RECOVERY.md), [Privacy](docs/PRIVACY.md), [Contributing](CONTRIBUTING.md) and [Security](SECURITY.md).

## Final fundamentals release

Archive Scout **1.2.3** uses the supplied 1.2.4 testing repository as its baseline. The release number follows the requested final branding; it does not downgrade project data. Python imports, database filenames, settings and the legacy `scout`/`scout-gui` commands remain compatible.

This release fixes exception-safe backend recovery, interleaves due retries, removes repeated historical scanner work, supervises local scans and bounds their retained backlog. Indexing adds saved diagnostic trials without changing query membership. Media retains incomplete blocked indexes, preserves collapse/page semantics during outages and retries transient acquisition automatically. Analysis uses complete disk-backed Hamming candidate matching, versioned derived checkpoints and explicitly labeled bounded snapshot comparisons. Maintenance exports/imports avoid project-sized Python collections.

See [implementation and validation](docs/FINAL_FUNDAMENTALS_1_2_3.md) for contracts, measurements and remaining verification boundaries.

## Upgrade and resume existing projects

Stop the old app, back up the entire project, replace the program, and reopen the same `project.json`. Supported schema 2–9 projects migrate automatically to **schema 10**, adding indexes, retry schedules, derived checkpoints and revision triggers. Existing rows, capture IDs, files, scans, query signatures and cursors are retained. A consistent SQLite backup is created before schema migration. Older schema-9 software cannot reopen the upgraded database; restore its pre-upgrade backup for a rollback. Historical schema-13 projects remain unsupported.

Use `python scripts/check_project_resume.py "PROJECT_FOLDER" --snapshot before.json` before upgrading, then `--compare before.json` afterward. Version differences are expected; capture/scan coverage must remain intact. Never copy only the SQLite file from an active WAL project.

The **Use in next scan** checkbox selects one keyword set. Changing keyword rules creates the appropriate new scan; prior reports and scan history remain available.

MIT-licensed. Archive Scout is an independent research tool, not affiliated with the Internet Archive.
