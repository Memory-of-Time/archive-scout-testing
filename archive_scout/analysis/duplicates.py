from __future__ import annotations

import hashlib
import math
import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass

from ..utils import normalize_search, utc_now

TOKEN_PATTERN = re.compile(r"[\w'-]+", re.UNICODE)


@dataclass(slots=True)
class DuplicateSummary:
    exact_groups: int = 0
    near_groups: int = 0
    grouped_documents: int = 0


def _tokens(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(normalize_search(text))


def simhash64(text: str) -> int:
    tokens = _tokens(text)
    if not tokens:
        return 0
    features: list[str] = []
    if len(tokens) < 4:
        features = tokens
    else:
        features = [" ".join(tokens[index:index + 4]) for index in range(len(tokens) - 3)]
    vector = [0] * 64
    counts: dict[str, int] = defaultdict(int)
    for feature in features:
        counts[feature] += 1
    for feature, weight in counts.items():
        digest = hashlib.blake2b(feature.encode("utf-8", "replace"), digest_size=8).digest()
        value = int.from_bytes(digest, "big")
        scaled = 1 + int(math.log2(weight))
        for bit in range(64):
            vector[bit] += scaled if value & (1 << bit) else -scaled
    result = 0
    for bit, score in enumerate(vector):
        if score >= 0:
            result |= 1 << bit
    return result


def hamming_similarity(left: int, right: int) -> float:
    return 1.0 - ((left ^ right).bit_count() / 64.0)


def cluster_duplicates(database: sqlite3.Connection, threshold: float = 0.90,
                       stop_event=None) -> DuplicateSummary:
    """Complete Hamming-threshold clustering with disk-backed exact reduction.

    A BK tree prunes by triangle inequality, with no bucket truncation. Exact
    groups and equal fingerprints enter once; membership stays in SQLite.
    Fingerprints survive interruption; publication is one atomic transaction.
    """
    from .cache import cached, checkpoint, identity, revision
    from ..events import Stopped
    threshold = min(1.0,max(0.5,float(threshold)))
    distance = int(math.floor((1.0-threshold)*64+1e-9))
    fingerprint = identity('duplicates-bktree-v1',threshold,revision(database,'documents'))
    old = cached(database,'duplicate-generation','all',fingerprint)
    if old is not None:
        return DuplicateSummary(**old)
    for table in ('duplicate_work','duplicate_tree','duplicate_exact','duplicate_output'):
        database.execute(f'DROP TABLE IF EXISTS temp.{table}')
    database.execute('CREATE TEMP TABLE duplicate_work(id INTEGER PRIMARY KEY, parent INTEGER NOT NULL, hash TEXT NOT NULL, exact_key TEXT NOT NULL)')
    database.execute('CREATE TEMP TABLE duplicate_tree(id INTEGER PRIMARY KEY, hash TEXT UNIQUE NOT NULL, parent INTEGER, distance INTEGER, UNIQUE(parent,distance))')
    database.execute('CREATE TEMP TABLE duplicate_exact(exact_key TEXT PRIMARY KEY, representative INTEGER NOT NULL) WITHOUT ROWID')
    database.execute('CREATE TEMP TABLE duplicate_output(id INTEGER PRIMARY KEY, root INTEGER NOT NULL)')
    database.execute('CREATE INDEX duplicate_output_root ON duplicate_output(root,id)')
    root_id = None

    def stopped():
        if stop_event is not None and stop_event.is_set():
            raise Stopped

    def find(value):
        path=[]
        while True:
            parent=int(database.execute('SELECT parent FROM duplicate_work WHERE id=?',(value,)).fetchone()[0])
            if parent==value:
                break
            path.append(value);value=parent
        database.executemany('UPDATE duplicate_work SET parent=? WHERE id=?',((value,n) for n in path))
        return value

    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:
            database.execute('UPDATE duplicate_work SET parent=? WHERE id=?',(min(a,b),max(a,b)))

    for index,row in enumerate(database.execute("SELECT id,body_text,normalized_hash,content_hash FROM documents WHERE COALESCE(body_text,'')<>'' ORDER BY id"),1):
        stopped()
        document_id=int(row['id'])
        # Verify actual normalized identity: legacy hashes alone may be stale.
        normalized=normalize_search(str(row['body_text'] or ''))
        exact_key=hashlib.sha256(normalized.encode()).hexdigest()
        exact=database.execute('SELECT representative FROM duplicate_exact WHERE exact_key=?',(exact_key,)).fetchone()
        if exact:
            rep=int(exact[0]);value=database.execute('SELECT hash FROM duplicate_work WHERE id=?',(rep,)).fetchone()[0]
            database.execute('INSERT INTO duplicate_work VALUES(?,?,?,?)',(document_id,rep,value,exact_key))
        else:
            input_hash=identity('simhash64-v1',exact_key)
            output=cached(database,'simhash64',document_id,input_hash)
            value=int(output['value']) if output else simhash64(normalized)
            if output is None:
                checkpoint(database,'simhash64',document_id,input_hash,{'value':str(value)})
            database.execute('INSERT INTO duplicate_work VALUES(?,?,?,?)',(document_id,document_id,str(value),exact_key))
            database.execute('INSERT INTO duplicate_exact VALUES(?,?)',(exact_key,document_id))
            existing=database.execute('SELECT id FROM duplicate_tree WHERE hash=?',(str(value),)).fetchone()
            if existing:
                union(document_id,int(existing[0]))
            elif root_id is None:
                root_id=document_id
                database.execute('INSERT INTO duplicate_tree VALUES(?,?,NULL,NULL)',(document_id,str(value)))
            else:
                stack=[root_id]
                while stack:
                    stopped();node=stack.pop()
                    node_hash=int(database.execute('SELECT hash FROM duplicate_tree WHERE id=?',(node,)).fetchone()[0])
                    delta=(value^node_hash).bit_count()
                    if delta<=distance:
                        union(document_id,node)
                    stack.extend(int(r[0]) for r in database.execute('SELECT id FROM duplicate_tree WHERE parent=? AND distance BETWEEN ? AND ?',
                        (node,max(0,delta-distance),min(64,delta+distance))))
                parent=root_id
                while True:
                    stopped()
                    parent_hash=int(database.execute('SELECT hash FROM duplicate_tree WHERE id=?',(parent,)).fetchone()[0])
                    delta=(value^parent_hash).bit_count()
                    child=database.execute('SELECT id FROM duplicate_tree WHERE parent=? AND distance=?',(parent,delta)).fetchone()
                    if not child:
                        database.execute('INSERT INTO duplicate_tree VALUES(?,?,?,?)',(document_id,str(value),parent,delta));break
                    parent=int(child[0])
        if index%128==0:
            database.commit()
    for row in database.execute('SELECT id FROM duplicate_work ORDER BY id'):
        stopped();value=int(row[0])
        database.execute('INSERT INTO duplicate_output VALUES(?,?)',(value,find(value)))
    database.commit()
    summary=DuplicateSummary()
    with database:
        database.execute('DELETE FROM duplicate_members')
        database.execute('DELETE FROM duplicate_groups')
        for group in database.execute('SELECT root,MIN(id) AS representative,COUNT(*) AS n FROM duplicate_output GROUP BY root HAVING COUNT(*)>1 ORDER BY MIN(id)'):
            stopped();rep=int(group['representative'])
            rep_row=database.execute('SELECT hash,exact_key FROM duplicate_work WHERE id=?',(rep,)).fetchone()
            exact=database.execute('SELECT COUNT(DISTINCT w.exact_key) FROM duplicate_work w JOIN duplicate_output o ON o.id=w.id WHERE o.root=?',(group['root'],)).fetchone()[0]==1
            method='exact' if exact else 'near'
            group_id=database.execute('INSERT INTO duplicate_groups(method,representative_document_id,created_at) VALUES(?,?,?)',(method,rep,utc_now())).lastrowid
            for member in database.execute('SELECT w.id,w.hash,w.exact_key FROM duplicate_output o JOIN duplicate_work w ON w.id=o.id WHERE o.root=? ORDER BY w.id',(group['root'],)):
                similarity=1.0 if member['exact_key']==rep_row['exact_key'] else hamming_similarity(int(member['hash']),int(rep_row['hash']))
                database.execute('INSERT INTO duplicate_members(group_id,document_id,similarity) VALUES(?,?,?)',(group_id,member['id'],similarity))
            if exact:summary.exact_groups+=1
            else:summary.near_groups+=1
            summary.grouped_documents+=int(group['n'])
        checkpoint(database,'duplicate-generation','all',fingerprint,{
            'exact_groups':summary.exact_groups,'near_groups':summary.near_groups,'grouped_documents':summary.grouped_documents})
    return summary
