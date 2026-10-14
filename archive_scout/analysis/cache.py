"""Versioned durable derived-work checkpoints; no process-sized body cache."""
from __future__ import annotations
import hashlib
import json
from ..utils import utc_now


def identity(*values) -> str:
    return hashlib.sha256(json.dumps(values,ensure_ascii=False,sort_keys=True,default=str,
        separators=(',',':')).encode()).hexdigest()


def cached(database, feature, key, fingerprint):
    row=database.execute('SELECT input_hash,output_json FROM derived_work WHERE feature=? AND item_key=?',
        (feature,str(key))).fetchone()
    return json.loads(row['output_json']) if row and row['input_hash']==fingerprint else None


def checkpoint(database, feature, key, fingerprint, output):
    database.execute('INSERT OR REPLACE INTO derived_work VALUES(?,?,?,?,?)',
        (feature,str(key),fingerprint,json.dumps(output,ensure_ascii=False),utc_now()))


def revision(database, table):
    row=database.execute('SELECT value FROM project_meta WHERE key=?',('revision:'+table,)).fetchone()
    return str(row[0]) if row else '0'
