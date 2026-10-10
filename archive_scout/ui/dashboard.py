from __future__ import annotations

import sqlite3
from pathlib import Path


EMPTY_DASHBOARD = {
    "captures": 0,
    "documents": 0,
    "matches": 0,
    "errors": 0,
    "text": 0,"image":0,"video":0,"audio":0,"media_descriptor":0,
    "other_binary":0,"unknown":0,"deferred":0,"skipped":0,"failed":0,
}


def read_dashboard_counts(database_path: Path, *, include_classification: bool = True) -> dict[str, int]:
    """Explicit-refresh snapshot of persisted project totals.

    Documents counts *completed text downloads*, including those pending a
    local scan. Matches counts unique pages with qualifying positive keyword
    results, never the number of hits or repeated scan-set rows. No polling.
    """
    if not database_path.exists():
        return dict(EMPTY_DASHBOARD)
    database = sqlite3.connect(database_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=0.25)
    try:
        database.execute("PRAGMA query_only=ON")
        database.execute("PRAGMA busy_timeout=250")
        row = database.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM captures),
                (SELECT COUNT(*) FROM captures WHERE state IN ('downloaded', 'downloaded_unscanned')),
                (SELECT COUNT(DISTINCT document_id) FROM document_matches
                 WHERE score > 0 AND excluded=0 AND required_missing=0),
                (SELECT COUNT(*) FROM errors WHERE resolved=0 AND ignored=0)
            """
        ).fetchone()
        if row is None:
            return dict(EMPTY_DASHBOARD)
        result = {
            "captures": int(row[0] or 0),
            "documents": int(row[1] or 0),
            "matches": int(row[2] or 0),
            "errors": int(row[3] or 0),
        }
        if not include_classification:
            return result
        try:
            from ..database.classification import classification_counts
            counts=classification_counts(database)
            for kind in ("text","image","video","audio","media_descriptor","other_binary","unknown"):
                result[kind]=counts.get(kind,0)
            result["deferred"]=counts.get("route_deferred_to_media",0)
            result["skipped"]=counts.get("route_skipped_non_text",0)+counts.get("route_skipped_url_filter",0)
            result["failed"]=counts.get("route_failed",0)
        except sqlite3.OperationalError:
            pass
        return result
    finally:
        database.close()
