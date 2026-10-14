# Project migration and compatibility

Archive Scout 1.2.3 uses schema 10. Schema 2–9 projects migrate automatically with a consistent pre-migration SQLite backup. The migration adds pending-work indexes, versioned derived-work checkpoints, media retry eligibility and evidence revision triggers. It preserves capture/document IDs, source files, CDX query signatures, cursors, scan history and settings.

Stop the old program and back up the entire project before upgrading. Open the existing project folder in the new release. Keep targets, date bounds, filters and collapse settings unchanged when checking preserved inventory. Changing pacing does not change semantic query identity.

Schema 13 remains unsupported. Do not edit schema_info to bypass version checks. Older schema-9 releases cannot read an upgraded database; use the consistent backup when rolling back.

The Python module and project database remain archive_scout and archive_scout.sqlite3. New binaries use ArchiveScout / ArchiveScoutCLI; public UI and reports use Archive Scout. Both archive-scout and scout command aliases remain available.
