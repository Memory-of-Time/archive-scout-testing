from __future__ import annotations

import sqlite3
from urllib.parse import urlsplit

from ..utils import utc_now


def trace_provenance(database: sqlite3.Connection, stop_event=None) -> int:
    from ..analysis.cache import cached, checkpoint, identity, revision
    from ..events import Stopped
    fingerprint=identity('provenance-v2',revision(database,'documents'),revision(database,'captures'),revision(database,'duplicate_groups'),revision(database,'duplicate_members'))
    old=cached(database,'provenance-generation','all',fingerprint)
    if old is not None:return int(old['count'])
    created=0;group_id=None;source=None
    with database:
        database.execute('DELETE FROM provenance_edges')
        for row in database.execute("""SELECT dg.id AS group_id,dg.method,dm.document_id,dm.similarity,c.original_url,c.timestamp
            FROM duplicate_groups dg JOIN duplicate_members dm ON dm.group_id=dg.id
            JOIN documents d ON d.id=dm.document_id JOIN captures c ON c.id=d.capture_id
            ORDER BY dg.id,c.timestamp,dm.document_id"""):
            if stop_event is not None and stop_event.is_set():raise Stopped
            if row['group_id']!=group_id:
                group_id=row['group_id'];source=row;continue
            source_host=(urlsplit(str(source['original_url'])).hostname or '').casefold()
            mirror_host=(urlsplit(str(row['original_url'])).hostname or '').casefold()
            if source_host==mirror_host and source['original_url']==row['original_url']:continue
            database.execute("""INSERT OR IGNORE INTO provenance_edges(source_document_id,mirror_document_id,method,similarity,source_timestamp,mirror_timestamp,created_at)
                VALUES(?,?,?,?,?,?,?)""",(source['document_id'],row['document_id'],source['method'],float(row['similarity']),source['timestamp'],row['timestamp'],utc_now()))
            created+=1
        checkpoint(database,'provenance-generation','all',fingerprint,{'count':created})
    return created
