from __future__ import annotations

import shutil
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ..database.connection import DATABASE_NAME
from ..database.lease import project_lease
from ..utils import utc_now


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_project_backup(root: Path, reason: str = "manual", keep: int = 5) -> Path:
    root = Path(root)
    source = root / DATABASE_NAME
    if not source.exists():
        raise FileNotFoundError(source)
    backup_dir = root / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    destination = backup_dir / f"archive_scout_{_timestamp()}_{reason.replace(' ', '_')}.sqlite3"
    source_db = sqlite3.connect(source)
    destination_db = sqlite3.connect(destination)
    try:
        source_db.backup(destination_db)
    finally:
        destination_db.close()
        source_db.close()
    _record_backup(root, destination, reason)
    prune_backups(root, keep)
    return destination


def _record_backup(root: Path, path: Path, reason: str) -> None:
    database_path = root / DATABASE_NAME
    if not database_path.exists():
        return
    database = sqlite3.connect(database_path)
    try:
        has_table = database.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='project_backups'"
        ).fetchone()
        if has_table:
            database.execute(
                "INSERT OR IGNORE INTO project_backups(path,reason,size_bytes,created_at) VALUES(?,?,?,?)",
                (str(path), reason, path.stat().st_size if path.exists() else 0, utc_now()),
            )
            database.commit()
    except Exception:
        pass
    finally:
        database.close()


def list_project_backups(root: Path) -> list[Path]:
    backup_dir = Path(root) / "backups"
    if not backup_dir.exists():
        return []
    return sorted(backup_dir.glob("archive_scout_*.sqlite3"), key=lambda p: p.stat().st_mtime, reverse=True)


def prune_backups(root: Path, keep: int = 5) -> None:
    keep = max(1, int(keep))
    for path in list_project_backups(root)[keep:]:
        path.unlink(missing_ok=True)


def restore_project_backup(root: Path, backup_path: Path) -> Path:
    """Restore a SQLite snapshot without racing an active Scout operation.

    Project lease is acquired once; full SQLite backup avoids losing committed
    WAL pages. No backup/restore work runs during ordinary acquisition.
    """
    root = Path(root).expanduser().resolve()
    backup_path = Path(backup_path).expanduser().resolve()
    if not backup_path.is_file():
        raise FileNotFoundError(backup_path)
    target = root / DATABASE_NAME
    with project_lease(root):
        # A second process holding a database connection may be a reader, but
        # active WAL writers must not be allowed to modify a replaced file.
        safety = None
        if target.exists():
            safety = create_project_backup(root, reason="before_restore", keep=999999)
            live = sqlite3.connect(target, timeout=2)
            try:
                checkpoint = live.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
                if checkpoint and int(checkpoint[0]):
                    raise RuntimeError("database is busy; close other Scout processes before restoring")
            finally:
                live.close()
        temp = target.with_name(target.name + ".restore.tmp")
        temp.unlink(missing_ok=True)
        # Produce a canonical standalone database even when the provided
        # backup itself has WAL sidecars.
        source = sqlite3.connect(f"file:{backup_path}?mode=ro", uri=True)
        destination = sqlite3.connect(temp)
        try:
            source.backup(destination)
            check = destination.execute("PRAGMA integrity_check").fetchone()
            if not check or str(check[0]).lower() != "ok":
                raise RuntimeError(f"backup failed SQLite integrity check: {check}")
        finally:
            destination.close()
            source.close()
        try:
            for suffix in ("-wal", "-shm"):
                Path(str(target) + suffix).unlink(missing_ok=True)
            os.replace(temp, target)
        finally:
            temp.unlink(missing_ok=True)
        return safety or target
