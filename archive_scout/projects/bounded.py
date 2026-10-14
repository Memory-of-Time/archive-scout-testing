"""Disposable file-backed collections for exhaustive maintenance operations."""
from __future__ import annotations
import sqlite3
import tempfile
from pathlib import Path


class DiskCollection:
    def __init__(self, unique=False):
        self.folder=tempfile.TemporaryDirectory(prefix='archive-scout-maintenance-')
        self.database=sqlite3.connect(Path(self.folder.name)/'work.sqlite3')
        self.database.execute('PRAGMA journal_mode=OFF')
        self.database.execute('PRAGMA synchronous=OFF')  # disposable, never evidence or checkpoints
        self.database.execute('PRAGMA cache_size=-2048')
        self.database.execute('CREATE TABLE items(id INTEGER PRIMARY KEY,value TEXT'+(' UNIQUE' if unique else '')+')')
    def append(self,value):
        self.database.execute('INSERT OR IGNORE INTO items(value) VALUES(?)',(str(value),))
    add=append
    def __contains__(self,value):
        return self.database.execute('SELECT 1 FROM items WHERE value=? LIMIT 1',(str(value),)).fetchone() is not None
    def __len__(self):
        return int(self.database.execute('SELECT COUNT(*) FROM items').fetchone()[0])
    def __iter__(self):
        return (str(r[0]) for r in self.database.execute('SELECT value FROM items ORDER BY id'))
    def close(self):
        self.database.close();self.folder.cleanup()
