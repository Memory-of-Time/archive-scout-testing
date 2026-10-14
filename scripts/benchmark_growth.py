"""Offline disposable 100k/500k/1m query-scaling benchmark; not download throughput."""
import sys,tempfile,time,json,sqlite3,resource
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from archive_scout.database.connection import open_database
from archive_scout.config import ProjectConfig
from archive_scout.cdx.parameters import cdx_query_signature
from archive_scout.scanning.pending import _pending_rows
from archive_scout.media.downloader import iter_media_download_rows
results=[]
def elapsed(call):
 samples=[]
 for _ in range(3):
  t=time.perf_counter();call();samples.append((time.perf_counter()-t)*1000)
 return round(sorted(samples)[1],4)
with tempfile.TemporaryDirectory() as temp:
 cfg=ProjectConfig(Path(temp),targets=['example.net/*'],keywords=['needle']).normalized();db=open_database(Path(temp));sig=cdx_query_signature(cfg)
 # Bulk fixture construction only: these options do not change application settings.
 db.execute('PRAGMA journal_mode=OFF');db.execute('PRAGMA synchronous=OFF')
 db.execute("INSERT INTO targets(pattern,created_at) VALUES('example.net/*','x')")
 db.execute("INSERT INTO media_targets(pattern,created_at) VALUES('example.net/*','x')")
 previous=0
 for n in (100000,500000,1000000):
  t=time.perf_counter()
  with db:
   db.executemany("INSERT INTO captures(id,original_url,timestamp,target_id,query_signature,mimetype,length,state,created_at,updated_at) VALUES(?,?,'20010101000000',1,?,'text/html',100,'downloaded','x','x')",((i,f'http://example.net/{i}',sig) for i in range(previous+1,n+1)))
   db.executemany("INSERT INTO documents(id,capture_id,path,title,body_text,links_json,content_hash,normalized_hash,size_bytes,created_at,updated_at) VALUES(?,?,'/unused','','needle','[]','h','h',100,'x','x')",((i,i) for i in range(previous+1,n+1)))
   db.executemany("INSERT INTO media_captures(id,original_url,timestamp,target_id,query_signature,media_kind,extension,mimetype,length,state,created_at,updated_at) VALUES(?,?,'20010101000000',1,'growth','image','.jpg','image/jpeg',?,'pending','x','x')",((i,f'http://example.net/{i}.jpg',i) for i in range(previous+1,n+1)))
  seed=time.perf_counter()-t
  with db:db.execute("UPDATE captures SET state='downloaded_unscanned',bytes_saved=100 WHERE id=?",(n,))
  count_query="SELECT COUNT(*) FROM captures c JOIN targets t ON t.id=c.target_id LEFT JOIN documents d ON d.capture_id=c.id WHERE c.state='downloaded_unscanned' AND c.query_signature=? AND t.pattern=?"
  scan_plan=[r[3] for r in db.execute('EXPLAIN QUERY PLAN '+count_query,(sig,'example.net/*'))]
  count_ms=elapsed(lambda:db.execute(count_query,(sig,'example.net/*')).fetchone())
  first_ms=elapsed(lambda:next(_pending_rows(db,cfg),None))
  legacy="SELECT COUNT(*) FROM captures c JOIN targets t ON t.id=c.target_id LEFT JOIN documents d ON d.capture_id=c.id WHERE (c.state='downloaded_unscanned' OR (c.state='downloaded' AND d.id IS NULL)) AND c.query_signature=? AND t.pattern=?"
  old_ms=elapsed(lambda:db.execute(legacy,(sig,'example.net/*')).fetchone())
  started=time.perf_counter();total,rows=iter_media_download_rows(db,['query_signature=?','state=?'],['growth','pending'])
  setup_ms=(time.perf_counter()-started)*1000
  media_query="SELECT mc.id FROM archive_scout_media_queue q JOIN media_captures mc ON mc.id=q.id WHERE (q.length,q.id)>(?,?) ORDER BY q.length,q.id LIMIT 1000"
  media_plan=[r[3] for r in db.execute('EXPLAIN QUERY PLAN '+media_query,(0,0))]
  med={label:elapsed(lambda key=key:db.execute(media_query,(key,key)).fetchall()) for label,key in [('early',0),('middle',n//2),('late',n-1000)]}
  results.append({'history_rows':n,'fixture_seed_seconds':round(seed,3),'scanner_count_ms':count_ms,'scanner_first_pending_ms':first_ms,'legacy_count_ms_same_database':old_ms,'scanner_plan':scan_plan,'media_queue_setup_ms_once':round(setup_ms,3),'media_batch_ms':med,'media_plan':media_plan,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
  print(json.dumps(results[-1]),flush=True)
  with db:db.execute("UPDATE captures SET state='downloaded' WHERE id=?",(n,))
  previous=n
 db.close()
dest=root/'validation';dest.mkdir(exist_ok=True)
(dest/'query-growth.json').write_text(json.dumps(results,indent=2))
