from __future__ import annotations

import sqlite3
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from ..content import parse_page
from ..database.repositories import get_or_create_target, upsert_document
from ..events import ProgressEvent, Stopped
from ..analysis.cache import cached, checkpoint, identity
from ..utils import atomic_write_bytes, hash_text, normalize_search, utc_now


def import_text_folder(
    root: Path,
    source_folder: Path,
    database: sqlite3.Connection,
    stop_event,
    callback: Callable[[ProgressEvent], None] | None = None,
) -> int:
    database.execute('DROP TABLE IF EXISTS temp.import_files')
    database.execute('CREATE TEMP TABLE import_files(path TEXT PRIMARY KEY) WITHOUT ROWID')
    batch=[]
    database.execute('DROP TABLE IF EXISTS temp.import_directories')
    database.execute('CREATE TEMP TABLE import_directories(path TEXT PRIMARY KEY,done INTEGER DEFAULT 0) WITHOUT ROWID')
    database.execute('INSERT INTO import_directories(path) VALUES(?)',(str(source_folder),))
    def enumerate_files():
        while True:
            row=database.execute('SELECT path FROM import_directories WHERE done=0 LIMIT 1').fetchone()
            if row is None:return
            with os.scandir(row[0]) as entries:
                for entry in entries:
                    if stop_event.is_set():raise Stopped
                    if entry.is_dir(follow_symlinks=False):
                        database.execute('INSERT OR IGNORE INTO import_directories(path) VALUES(?)',(entry.path,))
                    elif entry.is_file():yield Path(entry.path)
            database.execute('UPDATE import_directories SET done=1 WHERE path=?',(row[0],))
    for path in enumerate_files():
        if stop_event.is_set():
            raise Stopped
        if path.is_file() and path.suffix.lower() in {'.txt','.html','.htm'}:
            batch.append((str(path),))
        if len(batch)>=500:
            database.executemany('INSERT OR IGNORE INTO import_files VALUES(?)',batch);batch.clear()
    if batch:database.executemany('INSERT OR IGNORE INTO import_files VALUES(?)',batch)
    total=int(database.execute('SELECT COUNT(*) FROM import_files').fetchone()[0])
    files=(Path(row[0]) for row in database.execute('SELECT path FROM import_files ORDER BY path'))
    target_id = get_or_create_target(database, f"local-import:{source_folder}")
    imported = 0
    for index, path in enumerate(files, 1):
        if stop_event.is_set():
            raise Stopped
        data = path.read_bytes()
        raw = data.decode("utf-8", errors="replace")
        original = path.resolve().as_uri()
        timestamp = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        stable_id = hashlib.sha256((original + "|" + timestamp + "|" + hashlib.sha256(data).hexdigest()).encode("utf-8", "replace")).hexdigest()[:24]
        destination = root / "captures" / "imported" / f"{stable_id}.txt"
        # Local-import file I/O occurs only during explicit import, never in
        # the Wayback download hot path. Avoid rewriting already identical files.
        if not destination.exists() or destination.read_bytes() != data:
            atomic_write_bytes(destination, data)
        now = utc_now()
        cursor = database.execute(
            """
            INSERT OR IGNORE INTO captures(
                original_url,timestamp,target_id,query_signature,mimetype,state,created_at,updated_at
            ) VALUES(?,?,?,?,?,'downloaded',?,?)
            """,
            (original, timestamp, target_id, "local-import", "text/plain", now, now),
        )
        row = database.execute(
            "SELECT id FROM captures WHERE original_url=? AND timestamp=? AND query_signature='local-import'",
            (original, timestamp),
        ).fetchone()
        capture_id = int(row["id"])
        fingerprint=identity('import-parser-v1',hashlib.sha256(data).hexdigest(),original)
        existing=database.execute('SELECT id,content_hash FROM documents WHERE capture_id=?',(capture_id,)).fetchone()
        if existing and existing['content_hash']==hashlib.sha256(data).hexdigest() and cached(database,'import-document',capture_id,fingerprint) is not None:
            database.commit()
            if callback:callback(ProgressEvent('import',f'Checked {index:,}/{total:,}; unchanged',index,total))
            continue
        title, visible, links = parse_page(raw, original)
        upsert_document(
            database,
            capture_id,
            destination,
            title,
            visible,
            links,
            hashlib.sha256(data).hexdigest(),
            hash_text(normalize_search(visible)),
            len(data),
        )
        checkpoint(database,'import-document',capture_id,fingerprint,{})
        database.commit()
        imported += int(cursor.rowcount > 0)
        if callback:
            callback(ProgressEvent("import", f"Imported {index:,}/{total:,}", index, total))
    return imported
