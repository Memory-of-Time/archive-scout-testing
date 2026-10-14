"""Regression contracts for the final fundamental fixes (offline, no credentials)."""
from __future__ import annotations
import errno
import hashlib
import json
import random
import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from archive_scout.config import ProjectConfig
from archive_scout.database.connection import open_database,DATABASE_NAME
from archive_scout.database.repositories import (get_or_create_target,upsert_captures,upsert_document,
    get_or_create_media_target,upsert_media_captures,get_or_create_keyword_set,start_scan_run)
from archive_scout.network.transports import ResilientTransport
from archive_scout.cdx.client import TransientRequestError,PermanentRequestError,CDXRows,HttpClient
from archive_scout.cdx.indexer import PendingWindow,IndexPlan,window_label,index_archive
from archive_scout.cdx.parameters import cdx_query_signature
from archive_scout.downloads.downloader import download_archive,StorageFullError
from archive_scout.downloads.rate_limit import reset_shared_traffic_state_for_tests,FixedRateLimiter
from archive_scout.scanning.jobs import ScanJob
from archive_scout.scanning.pending import scan_pending_saved,repair_legacy_scan_queue
from archive_scout.media.indexer import index_direct_media,_defer_media_window,media_query_signature
from archive_scout.media.downloader import download_media,iter_media_download_rows
from archive_scout.research.index import build_research_index,_dependency_fingerprint
from archive_scout.projects.importers import import_text_folder
from archive_scout.analysis.duplicates import cluster_duplicates
from archive_scout.analysis.diffs import _summary,compare_snapshots
from archive_scout.analysis.workflow import run_analysis

class FinalFundamentals(unittest.TestCase):
    def setUp(self):
        reset_shared_traffic_state_for_tests()
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.config=ProjectConfig(self.root,targets=['example.net/*'],keywords=['needle'],
            workers=1,download_delay=0,cdx_delay=0,from_year=2001,to_year=2001).normalized()
        self.config.network.trust_environment=False
        self.db=open_database(self.root);self.addCleanup(self.db.close)
    def captures(self,n=1):
        target=get_or_create_target(self.db,'example.net/*')
        with self.db:upsert_captures(self.db,(('20010101000000',f'http://example.net/{i}.html','text/html','200',f'D{i}','100') for i in range(n)),target,cdx_query_signature(self.config))
    def documents(self,texts):
        self.captures(len(texts))
        with self.db:
            for i,text in enumerate(texts,1):
                path=self.root/f'{i}.txt';path.write_text(text)
                upsert_document(self.db,i,path,'Title',text,[],hashlib.sha256(text.encode()).hexdigest(),hashlib.sha256(text.encode()).hexdigest(),len(text))
                self.db.execute("UPDATE captures SET state='downloaded',document_id=? WHERE id=?",(i,i))
    def media(self,n=1):
        self.config.media.enabled=True
        target=get_or_create_media_target(self.db,'example.net/*')
        with self.db:upsert_media_captures(self.db,[(('20010101000000',f'http://example.net/{i}.jpg','image/jpeg','200',f'D{i}',str(100+i)),'image','.jpg') for i in range(n)],target,media_query_signature(self.config))
    def transport(self,method='request',error=None,pacer=None):
        t=ResilientTransport.__new__(ResilientTransport);t.lock=threading.Lock();t.condition=threading.Condition(t.lock)
        t.cooldown_until={'httpx':time.monotonic()-1};t.recovery_probes=set();t.order=['httpx'];t.last_success=None;t.callback=None;t.fallback_pacer=pacer
        class Backend:
            def request(self,*args,**kwargs):raise error or RuntimeError('response exceeds 100 bytes')
            download=request
        t.backends={'httpx':Backend()};return t
    def test_response_rejection_releases_request_probe(self):
        t=self.transport()
        with self.assertRaises(RuntimeError):t.request('https://example.net',{},100,threading.Event())
        self.assertEqual(t.recovery_probes,set());self.assertNotIn('httpx',t.cooldown_until)
    def test_response_rejection_releases_stream_probe(self):
        t=self.transport()
        with self.assertRaises(RuntimeError):t.download('https://example.net',{},self.root/'part',100,threading.Event())
        self.assertEqual(t.recovery_probes,set())
    def test_transport_storage_full_is_not_backend_fallback(self):
        t=self.transport(error=OSError(errno.ENOSPC,'full'))
        with self.assertRaises(OSError) as e:t.download('https://example.net',{},self.root/'part',100,threading.Event())
        self.assertEqual(e.exception.errno,errno.ENOSPC);self.assertFalse(t.recovery_probes)
    def test_client_storage_full_is_not_network_retry(self):
        class Fixture:
            calls=0
            def download(self,*a,**kw):self.calls+=1;raise OSError(errno.ENOSPC,'full')
            def close(self):pass
        t=Fixture();c=HttpClient(FixedRateLimiter(0),3,1,'test',threading.Event(),transport=t)
        self.addCleanup(c.close)
        with self.assertRaises(StorageFullError):c.download_to_path('https://example.net',self.root/'part',100)
        self.assertEqual(t.calls,1)
    def test_schema9_upgrade_preserves_identity_and_payload(self):
        self.captures();self.db.execute('UPDATE schema_info SET version=9');self.db.commit();self.db.close()
        self.db=open_database(self.root);self.addCleanup(self.db.close)
        self.assertEqual(self.db.execute('SELECT version FROM schema_info').fetchone()[0],10)
        self.assertEqual(self.db.execute('SELECT original_url FROM captures').fetchone()[0],'http://example.net/0.html')
        self.assertTrue(list((self.root/'backups').glob('*')))
        self.db.close();self.db=sqlite3.connect(':memory:')  # cleanup callback owns the original connection
    def test_live_scanner_uses_partial_pending_index(self):
        self.documents(['needle']*20)
        with self.db:self.db.execute("UPDATE captures SET state='downloaded_unscanned',bytes_saved=6 WHERE id=20")
        plan=' '.join(str(r[3]) for r in self.db.execute("EXPLAIN QUERY PLAN SELECT id FROM captures WHERE state='downloaded_unscanned' AND query_signature=? AND id>0 ORDER BY id LIMIT 500",(cdx_query_signature(self.config),)))
        self.assertIn('captures_live_scan_idx',plan)
        self.assertNotIn('TEMP B-TREE',plan)
    def test_legacy_repair_has_durable_watermark(self):
        self.captures(3)
        with self.db:self.db.execute("UPDATE captures SET state='downloaded'")
        repair_legacy_scan_queue(self.db,self.config,threading.Event())
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM captures WHERE state='downloaded_unscanned'").fetchone()[0],3)
        before=self.db.total_changes;repair_legacy_scan_queue(self.db,self.config,threading.Event())
        self.assertEqual(self.db.total_changes,before)
    def test_media_forbidden_keeps_incomplete_checkpoint(self):
        self.config.media.enabled=True
        class Fixture:
            def get_cdx_rows_any(self,*a,**kw):raise PermanentRequestError('HTTP 403',status=403,category='wayback_forbidden')
        with self.assertRaises(PermanentRequestError):index_direct_media(self.config,self.db,Fixture(),threading.Event(),None,media_query_signature(self.config),'test')
        row=self.db.execute('SELECT complete,resume_key FROM media_index_state').fetchone()
        self.assertEqual(row['complete'],0);self.assertTrue(row['resume_key'])
    def test_media_503_does_not_shrink_or_rotate_scope(self):
        a=PendingWindow('20010101000000','20011231235959',page_size=100000,strategy='resume')
        b=PendingWindow('20020101000000','20021231235959',page_size=100000,strategy='resume')
        plan=IndexPlan([a,b],0,2);target=get_or_create_media_target(self.db,'example.net/*')
        with patch('archive_scout.media.indexer._wait_seconds',return_value=0):
            _defer_media_window(self.config,self.db,plan,a,target,2001,'test',0,None,'example.net/*','2001',TransientRequestError('HTTP 503',status=503,splittable=True),0,2,threading.Event(),None)
        self.assertEqual(a.page_size,100000);self.assertIs(plan.pending[0],a)
    def test_media_storage_full_is_hard_stop(self):
        self.media()
        with patch('archive_scout.media.downloader.fetch_media',side_effect=OSError(errno.ENOSPC,'full')):
            with self.assertRaises(StorageFullError):download_media(self.config,self.db,threading.Event())
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM media_retry_schedule').fetchone()[0],0)
    def test_newly_due_text_failure_rejoins_current_pass(self):
        self.captures(6);calls=[]
        class Fixture:
            def __init__(self,*a,**kw):pass
            def close(self):pass
            def get(self,url,*a,**kw):
                name=url.rsplit('/',1)[-1];calls.append(name)
                if name=='0.html' and calls.count(name)==1:raise TransientRequestError('connection refused',connection_failed=True)
                return {'data':b'<html>needle</html>','headers':{'content-type':'text/html'},'status':200,'final_url':url}
        def progress(e):
            with self.db:self.db.execute('UPDATE text_retry_schedule SET next_eligible_at=0')
        with patch('archive_scout.downloads.downloader.HttpClient',Fixture):
            download_archive(self.config,self.db,0,threading.Event(),progress,states=('pending','error'),acquire_only=True)
        self.assertEqual(calls.count('0.html'),2)
        self.assertLess(calls.index('0.html',1),calls.index('5.html'))
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM captures WHERE state='downloaded_unscanned'").fetchone()[0],6)
    def test_scanner_failure_stops_new_admission_promptly(self):
        self.captures(12);calls=[];failed=threading.Event()
        class Fixture:
            def __init__(self,*a,**kw):pass
            def close(self):pass
            def get(self,url,*a,**kw):
                failed.wait(1);calls.append(url)
                return {'data':b'<html>needle</html>','headers':{'content-type':'text/html'},'status':200,'final_url':url}
        def fail(*a,**kw):failed.set();raise RuntimeError('injected scanner failure')
        with patch('archive_scout.downloads.downloader.HttpClient',Fixture),patch('archive_scout.scanning.pending.scan_pending_saved',side_effect=fail):
            with self.assertRaisesRegex(RuntimeError,'background scanner failed'):
                download_archive(self.config,self.db,1,threading.Event(),None,scan_jobs=[ScanJob.create(1,'test',['needle'])])
        self.assertLessEqual(len(calls),2)
    def test_research_dimensions_invalidate_checkpoint(self):
        self.documents(['needle']);self.config.research.entity_extraction=False;self.config.research.duplicate_clustering=False
        build_research_index(self.config,self.db,threading.Event());self.config.research.vector_dimensions=512
        result=build_research_index(self.config,self.db,threading.Event())
        self.assertEqual(self.db.execute('SELECT dimensions FROM research_vectors').fetchone()[0],512)
        self.assertEqual(result.indexed,1)
    def test_dependency_revision_detects_in_place_document_change(self):
        self.documents(['needle']);before=_dependency_fingerprint(self.db,'same')
        with self.db:self.db.execute("UPDATE documents SET body_text='changed' WHERE id=1")
        self.assertEqual(before,_dependency_fingerprint(self.db,'same'))  # dependency argument supplied by caller
        from archive_scout.research.index import _document_fingerprint
        fp=_document_fingerprint(self.db)
        with self.db:self.db.execute("UPDATE documents SET body_text='again' WHERE id=1")
        self.assertNotEqual(fp,_document_fingerprint(self.db))
    def test_repeat_import_avoids_parsing_unchanged_bytes(self):
        folder=self.root/'input';folder.mkdir();(folder/'p.txt').write_text('needle')
        from archive_scout.projects import importers
        with patch.object(importers,'parse_page',wraps=importers.parse_page) as parse:
            self.assertEqual(import_text_folder(self.root,folder,self.db,threading.Event()),1)
            self.assertEqual(import_text_folder(self.root,folder,self.db,threading.Event()),0)
            self.assertEqual(parse.call_count,1)
    def test_multi_year_label_displays_both_years(self):
        value=window_label('20040101000000','20061231235959')
        self.assertIn('2004',value);self.assertIn('2006',value)
    def test_exact_group_requires_no_near_pair_work(self):
        self.documents(['same needle']*100)
        from archive_scout.analysis import duplicates
        with patch.object(duplicates,'simhash64',wraps=duplicates.simhash64) as fingerprint,patch.object(duplicates,'hamming_similarity',wraps=duplicates.hamming_similarity) as comparison:
            result=cluster_duplicates(self.db)
        self.assertEqual(result.grouped_documents,100);self.assertEqual(fingerprint.call_count,1);self.assertEqual(comparison.call_count,0)
    def test_near_pair_can_differ_in_all_old_bands(self):
        self.documents(['needle left','needle right'])
        different=sum(1<<n for n in (0,16,32,48))
        with patch('archive_scout.analysis.duplicates.simhash64',side_effect=[0,different]):result=cluster_duplicates(self.db,.9)
        self.assertEqual(result.grouped_documents,2)
    def test_no_2000_bucket_truncation(self):
        self.documents([f'needle unique {i}' for i in range(2001)])
        with patch('archive_scout.analysis.duplicates.simhash64',side_effect=[0]*2000+[1]):result=cluster_duplicates(self.db,.9)
        self.assertEqual(result.grouped_documents,2001)
    def test_hamming_candidate_recall_matches_exhaustive_components(self):
        values=[random.Random(i).getrandbits(64) for i in range(60)]
        values[1]=values[0] ^ sum(1<<n for n in (0,16,32,48));values[3]=values[2]^3
        self.documents([f'needle unique {i}' for i in range(len(values))])
        with patch('archive_scout.analysis.duplicates.simhash64',side_effect=values):cluster_duplicates(self.db,.9)
        groups={}
        for row in self.db.execute('SELECT group_id,document_id FROM duplicate_members'):
            groups.setdefault(row[0],set()).add(row[1]-1)
        for i,a in enumerate(values):
            for j,b in enumerate(values[:i]):
                if (a^b).bit_count()<=6:self.assertTrue(any({i,j}<=g for g in groups.values()))
    def test_repetitive_diff_is_linear_at_equal_boundaries(self):
        start=time.monotonic();result=_summary('a'*8000+'x','a'*8000+'y')
        self.assertLess(time.monotonic()-start,1.0);self.assertEqual(result['similarity_metric'],'boundary-character-v2')
        self.assertEqual(_summary('','')['similarity'],1.0)
    def test_changed_diff_is_not_hidden_by_multiset_upper_bound(self):
        result=_summary('a'*5000+'b'*5000,'b'*5000+'a'*5000)
        self.assertTrue(result['similarity_is_upper_bound'])
    def test_media_queue_keeps_zero_lengths_and_selection_order(self):
        self.media(4)
        with self.db:self.db.execute('UPDATE media_captures SET length=0 WHERE id=2')
        total,rows=iter_media_download_rows(self.db,['state=?'],['pending'],batch_size=1)
        self.assertEqual(total,4);self.assertEqual([r['id'] for r in rows],[1,3,4,2])
    def test_analysis_unchanged_document_is_not_reparsed(self):
        self.documents(['<html>needle</html>'])
        from archive_scout.analysis import workflow
        with patch.object(workflow,'parse_forum_posts',wraps=workflow.parse_forum_posts) as parse:
            run_analysis(self.config,self.db,threading.Event());first=parse.call_count
            run_analysis(self.config,self.db,threading.Event());self.assertEqual(parse.call_count,first)

    def test_media_failure_recovers_without_manual_resume(self):
        self.media(3);calls=[]
        def fetch(row,config,client,destination):
            calls.append(int(row['id']))
            if int(row['id'])==1 and calls.count(1)==1:raise TransientRequestError('temporary disconnect',connection_failed=True)
            destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(b'jpeg')
            return {'id':int(row['id']),'path':destination,'bytes':4,'hash':hashlib.sha256(b'jpeg').hexdigest(),'status':200,'final_url':row['original_url']}
        def progress(e):
            with self.db:self.db.execute('UPDATE media_retry_schedule SET next_eligible_at=0')
        with patch('archive_scout.media.downloader.fetch_media',side_effect=fetch):download_media(self.config,self.db,threading.Event(),progress)
        self.assertEqual(calls.count(1),2);self.assertEqual(self.db.execute("SELECT COUNT(*) FROM media_captures WHERE state='downloaded'").fetchone()[0],3)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM media_retry_schedule').fetchone()[0],0)
    def test_media_future_retry_survives_restart_and_waits_automatically(self):
        self.media();from archive_scout.database.repositories import record_error
        with self.db:
            self.db.execute("UPDATE media_captures SET state='error',download_attempts=99")
            record_error(self.db,'media_download','network','temporary',media_capture_id=1,retryable=True)
            self.db.execute("INSERT INTO media_retry_schedule VALUES(1,?,1,'network',NULL,'x')",(time.time()+.1,))
        def fetch(row,config,client,destination):
            destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(b'jpeg')
            return {'id':1,'path':destination,'bytes':4,'hash':hashlib.sha256(b'jpeg').hexdigest(),'status':200,'final_url':row['original_url']}
        with patch('archive_scout.media.downloader.fetch_media',side_effect=fetch) as calls:
            download_media(self.config,self.db,threading.Event())
        self.assertEqual(calls.call_count,1);self.assertEqual(self.db.execute('SELECT state FROM media_captures').fetchone()[0],'downloaded')
    def test_ignored_media_retry_is_not_readmitted(self):
        self.media();from archive_scout.database.repositories import record_error
        with self.db:
            self.db.execute("UPDATE media_captures SET state='error'")
            record_error(self.db,'media_download','network','temporary',media_capture_id=1,retryable=True)
            self.db.execute('UPDATE errors SET ignored=1')
            self.db.execute("INSERT INTO media_retry_schedule VALUES(1,0,1,'network',NULL,'x')")
        with patch('archive_scout.media.downloader.fetch_media') as fetch:download_media(self.config,self.db,threading.Event())
        self.assertEqual(fetch.call_count,0)
    def test_same_scope_index_diagnostic_commits_members_and_cursor(self):
        self.config.cdx_collapses=['urlkey'];self.config.page_size=100000;calls=[]
        class Fixture:
            def close(self):pass
            def get_cdx_rows_any(inner,endpoints,params,**kw):
                values=dict(params);calls.append(values)
                if len(calls)<=2:raise TransientRequestError('HTTP 503',status=503)
                if len(calls)==3:return CDXRows([('20010101000000','http://example.net/a.html','text/html','200','A','100')],resume_key='cursor')
                return CDXRows([('20010201000000','http://example.net/b.html','text/html','200','B','100')])
        with patch('archive_scout.cdx.indexer._client_for_config',return_value=Fixture()),patch('archive_scout.cdx.indexer.transient_backoff',return_value=0):index_archive(self.config,self.db,threading.Event())
        self.assertEqual(len(calls),4);self.assertEqual(calls[2]['limit'],'1000');self.assertEqual(calls[3]['limit'],'100000')
        self.assertEqual(calls[3]['resumeKey'],'cursor')
        self.assertTrue(all((p['from'],p['to'],p['collapse'])==(calls[0]['from'],calls[0]['to'],calls[0]['collapse']) for p in calls))
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM captures').fetchone()[0],2)
        self.assertEqual(self.db.execute('SELECT complete FROM index_coverage').fetchone()[0],1)
    def test_stalled_index_does_not_starve_independent_target(self):
        self.config.targets=['example.net/*','other.net/*'];calls=[];failures=0
        class Fixture:
            def close(self):pass
            def get_cdx_rows_any(inner,endpoints,params,**kw):
                nonlocal failures
                values=dict(params);calls.append(values['url'])
                if values['url']=='example.net/*' and failures<2:
                    failures+=1;raise TransientRequestError('HTTP 503',status=503)
                return CDXRows([])
        with patch('archive_scout.cdx.indexer._client_for_config',return_value=Fixture()),patch('archive_scout.cdx.indexer.transient_backoff',return_value=0):index_archive(self.config,self.db,threading.Event())
        self.assertEqual(calls[:3],['example.net/*','example.net/*','other.net/*'])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM index_coverage WHERE complete=1').fetchone()[0],2)
    def test_completed_unfiltered_range_is_reused_for_media(self):
        self.config.cdx_collapses=[];self.config.cdx_filters=['statuscode:200'];self.config.media.enabled=True;calls=[]
        class Fixture:
            def close(self):pass
            def get_cdx_rows_any(inner,endpoints,params,**kw):
                calls.append(dict(params));return CDXRows([('20010101000000','http://example.net/a.jpg','image/jpeg','200','D','100')])
        with patch('archive_scout.cdx.indexer._client_for_config',return_value=Fixture()):index_archive(self.config,self.db,threading.Event())
        initial=len(calls);index_direct_media(self.config,self.db,Fixture(),threading.Event(),None,media_query_signature(self.config),'reuse')
        self.assertEqual(len(calls),initial);self.assertEqual(self.db.execute('SELECT COUNT(*) FROM media_captures').fetchone()[0],1)
    def test_filtered_main_range_is_not_false_media_coverage(self):
        self.config.cdx_collapses=[];self.config.cdx_filters=['statuscode:200','mimetype:text/html'];self.config.media.enabled=True;calls=[]
        class Fixture:
            def close(self):pass
            def get_cdx_rows_any(inner,endpoints,params,**kw):calls.append(dict(params));return CDXRows([])
        with patch('archive_scout.cdx.indexer._client_for_config',return_value=Fixture()):index_archive(self.config,self.db,threading.Event())
        initial=len(calls);index_direct_media(self.config,self.db,Fixture(),threading.Event(),None,media_query_signature(self.config),'reuse')
        self.assertGreater(len(calls),initial)
    def test_queued_backend_rechecks_healthy_peer(self):
        t=self.transport();t.order=['httpx','urllib3'];t.cooldown_until={'httpx':time.monotonic()+30}
        self.assertEqual(t._await_backend('httpx',threading.Event()),'urllib3')
    def test_analysis_missing_source_does_not_mark_complete(self):
        self.documents(['needle']);(self.root/'1.txt').unlink()
        with self.assertRaises(FileNotFoundError):run_analysis(self.config,self.db,threading.Event())
        self.assertEqual(self.db.execute('SELECT status FROM analysis_runs ORDER BY id DESC LIMIT 1').fetchone()[0],'failed')
    def test_diff_checkpoint_reused_without_comparison(self):
        self.documents(['old needle','new needle'])
        with self.db:self.db.execute("UPDATE captures SET original_url='http://example.net/shared',timestamp='20020101000000' WHERE id=2")
        compare_snapshots(self.db)
        with patch('archive_scout.analysis.diffs._summary',side_effect=AssertionError('must reuse checkpoint')):compare_snapshots(self.db)
    def test_requested_suffixes_remain_non_text_even_with_html_mime(self):
        from archive_scout.classification import classify_indexed_resource,SUFFIX_NON_TEXT_IMAGES,SUFFIX_NON_TEXT_MEDIA
        for suffix in SUFFIX_NON_TEXT_IMAGES|SUFFIX_NON_TEXT_MEDIA:
            with self.subTest(suffix=suffix):self.assertNotEqual(classify_indexed_resource('http://example.net/file'+suffix,'text/html').resource_class,'text')

    def test_failed_migration_backup_leaves_old_schema_untouched(self):
        with self.db:self.db.execute('UPDATE schema_info SET version=9')
        with patch('archive_scout.projects.backups.create_project_backup',side_effect=OSError(errno.ENOSPC,'full')):
            with self.assertRaises(OSError):open_database(self.root)
        self.assertEqual(self.db.execute('SELECT version FROM schema_info').fetchone()[0],9)
    def test_future_text_retries_are_staged_but_not_initially_admitted(self):
        self.captures(2)
        from archive_scout.database.repositories import record_error
        from archive_scout.downloads.downloader import prepare_download_rows
        with self.db:
            self.db.execute("UPDATE captures SET state='error' WHERE id=1")
            record_error(self.db,'download','connection','temporary',capture_id=1,retryable=True)
            self.db.execute("INSERT INTO text_retry_schedule VALUES(1,?,1,'connection',NULL,'x')",(time.time()+60,))
        count,rows=prepare_download_rows(self.db,self.config,[],states=('pending','error'))
        self.assertEqual(count,1);self.assertEqual([r['id'] for r in rows],[2])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM archive_scout_download_queue').fetchone()[0],2)
    def test_research_entity_toggle_rebuilds_unchanged_content(self):
        self.documents(['needle user@example.net']);self.config.research.entity_extraction=False;self.config.research.duplicate_clustering=False
        build_research_index(self.config,self.db,threading.Event());self.config.research.entity_extraction=True
        summary=build_research_index(self.config,self.db,threading.Event())
        self.assertEqual(summary.indexed,1);self.assertGreater(self.db.execute('SELECT COUNT(*) FROM research_document_entities').fetchone()[0],0)
    def test_timestamp_change_invalidates_graph_dependency(self):
        self.documents(['needle']);from archive_scout.research.index import _document_fingerprint
        before=_document_fingerprint(self.db)
        with self.db:self.db.execute("UPDATE captures SET timestamp='20020101000000' WHERE id=1")
        self.assertNotEqual(before,_document_fingerprint(self.db))
    def test_identical_document_metadata_write_does_not_invalidate_cache(self):
        self.documents(['needle']);from archive_scout.analysis.cache import revision
        before=revision(self.db,'documents')
        with self.db:self.db.execute("UPDATE documents SET updated_at='new-time',path=path WHERE id=1")
        self.assertEqual(before,revision(self.db,'documents'))

    def test_deferred_media_request_does_not_set_user_stop(self):
        self.media();calls=[];stop=threading.Event()
        from archive_scout.cdx.client import RateLimitDeferred
        def fetch(row,config,client,destination):
            calls.append(row['id'])
            if len(calls)==1:raise RateLimitDeferred('server-directed budget exhausted')
            destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(b'jpeg')
            return {'id':1,'path':destination,'bytes':4,'hash':hashlib.sha256(b'jpeg').hexdigest(),'status':200,'final_url':row['original_url']}
        def progress(e):
            with self.db:self.db.execute('UPDATE media_retry_schedule SET next_eligible_at=0')
        with patch('archive_scout.media.downloader.fetch_media',side_effect=fetch):download_media(self.config,self.db,stop,progress)
        self.assertFalse(stop.is_set());self.assertEqual(len(calls),2)
    def test_external_embedded_workflow_retries_saved_lookup_errors(self):
        from archive_scout.media.indexer import _index_embedded_until_current
        calls=[]
        def discovery(config,database,client,stop,callback,signature,**kwargs):
            calls.append(kwargs['external_only'])
            if len(calls)==1:
                with database:database.execute("INSERT INTO media_discovery_queue(query_signature,original_url,source_type,state,created_at,updated_at) VALUES('sig','http://other.net/a.jpg','external_embedded','error','x','x')")
            else:
                with database:database.execute("UPDATE media_discovery_queue SET state='indexed'")
        with patch('archive_scout.media.indexer.index_embedded_media',side_effect=discovery),patch('archive_scout.media.indexer._wait_seconds',return_value=0):
            _index_embedded_until_current(self.config,self.db,None,threading.Event(),None,'sig',external_only=True)
        self.assertEqual(calls,[True,True])

    def test_full_media_page_does_not_complete_with_contradictory_cursor(self):
        from archive_scout.media.indexer import _request_media_resume
        from archive_scout.cdx.client import MalformedCDXResponse
        client=HttpClient.__new__(HttpClient)
        row=('20010101000000','http://example.net/a.jpg','image/jpeg','200','D','100')
        window=PendingWindow('20010101000000','20011231235959',page_size=1,strategy='resume')
        with patch('archive_scout.media.indexer.request_cdx_rows',side_effect=[CDXRows([row]),CDXRows([row],resume_key='more')]) as request:
            with self.assertRaises(MalformedCDXResponse):_request_media_resume(self.config,client,'example.net/*',window,['.jpg'])
        self.assertEqual(request.call_count,2);self.assertIsNone(window.resume_key)
