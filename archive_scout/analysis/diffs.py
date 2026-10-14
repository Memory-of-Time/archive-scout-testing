from __future__ import annotations

import difflib
import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass

from ..scanning.automaton import LiteralAutomaton
from ..utils import clean_space, utc_now
from .cache import cached, checkpoint, identity


@dataclass(slots=True)
class DiffSummary:
    compared_pairs: int = 0
    changed_pairs: int = 0
    first_appearances: int = 0


def _summary(earlier: str, later: str) -> dict:
    earlier_lines = [value for line in earlier.splitlines() if (value := clean_space(line))]
    later_lines = [value for line in later.splitlines() if (value := clean_space(line))]
    # Strip equal boundaries in linear time before matching changed text.
    prefix=0
    end=min(len(earlier),len(later))
    while prefix<end and earlier[prefix]==later[prefix]:
        prefix+=1
    suffix=0
    while suffix<end-prefix and earlier[len(earlier)-suffix-1]==later[len(later)-suffix-1]:
        suffix+=1
    a=earlier[prefix:len(earlier)-suffix if suffix else len(earlier)]
    b=later[prefix:len(later)-suffix if suffix else len(later)]
    metric='boundary-character-v2'
    if max(len(a),len(b))<=4096:
        matches=sum(block.size for block in difflib.SequenceMatcher(None,a,b,autojunk=False).get_matching_blocks())
    else:
        # Explicit order-insensitive upper bound, never mislabeled as exact diff.
        from collections import Counter
        matches=sum((Counter(a)&Counter(b)).values())
        metric='boundary-character-multiset-upper-bound-v1'
    similarity=1.0 if not earlier and not later else 2*(prefix+suffix+matches)/max(1,len(earlier)+len(later))
    earlier_set = set(earlier_lines)
    later_set = set(later_lines)
    added = sorted(later_set - earlier_set)
    removed = sorted(earlier_set - later_set)
    return {
        "similarity": round(similarity, 6),
        "similarity_metric": metric,
        "similarity_is_upper_bound": metric.endswith("upper-bound-v1"),
        "earlier_chars": len(earlier),
        "later_chars": len(later),
        "added_lines": added[:200],
        "removed_lines": removed[:200],
        "added_count": len(added),
        "removed_count": len(removed),
    }


def compare_snapshots(database: sqlite3.Connection, stop_event=None) -> DiffSummary:
    from ..events import Stopped
    summary=DiffSummary()
    previous=None
    database.execute('DROP TABLE IF EXISTS temp.current_snapshot_pairs')
    database.execute('CREATE TEMP TABLE current_snapshot_pairs(a INTEGER,b INTEGER,summary TEXT,PRIMARY KEY(a,b)) WITHOUT ROWID')
    for row in database.execute("""SELECT c.id AS capture_id,c.original_url,c.timestamp,d.body_text,d.normalized_hash
        FROM captures c JOIN documents d ON d.id=c.document_id WHERE c.state='downloaded'
        ORDER BY c.original_url,c.timestamp,c.id"""):
        if stop_event is not None and stop_event.is_set():
            database.commit()  # completed pair checkpoints, never partial publication
            raise Stopped
        if previous is not None and previous['original_url']==row['original_url']:
            key=f"{previous['capture_id']}:{row['capture_id']}"
            fingerprint=identity('boundary-diff-v2',previous['body_text'],row['body_text'])
            result=cached(database,'snapshot-diff',key,fingerprint)
            if result is None:
                result=_summary(str(previous['body_text'] or ''),str(row['body_text'] or ''))
                checkpoint(database,'snapshot-diff',key,fingerprint,result)
            database.execute('INSERT INTO current_snapshot_pairs VALUES(?,?,?)',
                (previous['capture_id'],row['capture_id'],json.dumps(result,ensure_ascii=False)))
            summary.compared_pairs+=1
            summary.changed_pairs+=int(previous['body_text']!=row['body_text'])
            if summary.compared_pairs%128==0:
                database.commit()
        previous=row
    with database:
        database.execute("DELETE FROM derived_work WHERE feature='snapshot-diff' AND NOT EXISTS(SELECT 1 FROM current_snapshot_pairs p WHERE derived_work.item_key=CAST(p.a AS TEXT)||':'||CAST(p.b AS TEXT))")
        database.execute('DELETE FROM snapshot_diffs')
        database.execute('INSERT INTO snapshot_diffs(earlier_capture_id,later_capture_id,summary_json,created_at) SELECT a,b,summary,? FROM current_snapshot_pairs',(utc_now(),))
    return summary


def build_first_appearances(database: sqlite3.Connection, queries: list[str]) -> int:
    queries = list(dict.fromkeys(value.strip() for value in queries if value.strip()))
    if not queries:
        return 0
    needle_queries: dict[str, list[str]] = {}
    for query in queries:
        needle_queries.setdefault(query.casefold(), []).append(query)
    automaton = LiteralAutomaton(needle_queries)
    count = 0

    def flush(original_url: str | None, matches: dict[str, tuple[sqlite3.Row, sqlite3.Row]]) -> int:
        if original_url is None or not matches:
            return 0
        database.executemany(
            """
            INSERT INTO first_appearances(
                query,original_url,first_capture_id,first_timestamp,last_capture_id,last_timestamp,created_at
            ) VALUES(?,?,?,?,?,?,?)
            """,
            (
                (
                    query,
                    original_url,
                    first["capture_id"],
                    first["timestamp"],
                    last["capture_id"],
                    last["timestamp"],
                    utc_now(),
                )
                for query, (first, last) in matches.items()
            ),
        )
        return len(matches)

    with database:
        database.execute("DELETE FROM first_appearances")
        current_url: str | None = None
        matches: dict[str, tuple[sqlite3.Row, sqlite3.Row]] = {}
        for row in database.execute(
            """
            SELECT c.id AS capture_id,c.original_url,c.timestamp,d.title,d.body_text,d.links_json
            FROM captures c JOIN documents d ON d.id=c.document_id
            ORDER BY c.original_url,c.timestamp,c.id
            """
        ):
            original_url = str(row["original_url"])
            if current_url is not None and original_url != current_url:
                count += flush(current_url, matches)
                matches.clear()
            current_url = original_url
            haystack = " ".join(
                (str(row["title"] or ""), str(row["body_text"] or ""), str(row["links_json"] or ""))
            ).casefold()
            for needle in automaton.find(haystack):
                for query in needle_queries.get(needle, ()):
                    first, _last = matches.get(query, (row, row))
                    matches[query] = (first, row)
        count += flush(current_url, matches)
    return count

