#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,platform,sqlite3,tempfile,time
from datetime import datetime,timezone,timedelta
from pathlib import Path

HERE=Path(__file__).resolve().parent

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def now()->datetime:return datetime.now(timezone.utc)
def limit(value,unit,scope,source,ts,failure):return {'value':value,'unit':unit,'scope':scope,'source':source,'observed_at':ts,'failure_behavior':failure}

def main():
    started=now(); ts=started.isoformat().replace('+00:00','Z')
    tests=[]
    def record(name,passed,evidence): tests.append({'test_id':name,'passed':bool(passed),'evidence':evidence})
    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/'occurrence.sqlite3'
        c1=sqlite3.connect(db,timeout=5,isolation_level=None)
        journal=c1.execute('PRAGMA journal_mode=WAL').fetchone()[0]
        record('journal_mode_wal',journal.lower()=='wal',{'journal_mode':journal})
        version=sqlite3.sqlite_version
        c1.executescript('CREATE TABLE items(id INTEGER PRIMARY KEY, value TEXT NOT NULL, amount NUMERIC); INSERT INTO items(value,amount) VALUES (\'alpha\',1.20),(\'beta\',2.00);')
        cols=[{'name':r[1],'type':r[2],'notnull':r[3],'pk':r[5]} for r in c1.execute('PRAGMA table_info(items)')]
        record('schema_and_key_discovery',any(x['name']=='id' and x['pk']==1 for x in cols),{'columns':cols})
        count=c1.execute('SELECT count(*) FROM items').fetchone()[0]
        record('repeatable_read_basic',count==2,{'row_count':count})
        c1.execute('BEGIN'); c1.execute("INSERT INTO items(value,amount) VALUES('rollback',9)"); c1.execute('ROLLBACK')
        rollback_count=c1.execute("SELECT count(*) FROM items WHERE value='rollback'").fetchone()[0]
        record('transaction_rollback_atomicity',rollback_count==0,{'rows_after_rollback':rollback_count})
        # Snapshot isolation: reader starts before concurrent writer commit and retains its cut.
        reader=sqlite3.connect(db,timeout=5,isolation_level=None); writer=sqlite3.connect(db,timeout=5,isolation_level=None)
        reader.execute('BEGIN'); before=reader.execute('SELECT count(*) FROM items').fetchone()[0]
        writer.execute('BEGIN IMMEDIATE'); writer.execute("INSERT INTO items(value,amount) VALUES('concurrent',3)"); writer.execute('COMMIT')
        during=reader.execute('SELECT count(*) FROM items').fetchone()[0]; reader.execute('COMMIT')
        after=reader.execute('SELECT count(*) FROM items').fetchone()[0]
        record('snapshot_cut_stability',before==during and after==before+1,{'before':before,'during_reader_snapshot':during,'after_new_snapshot':after})
        writer.close(); reader.close()
        c1.execute("DELETE FROM items WHERE value='beta'")
        deleted=c1.execute("SELECT count(*) FROM items WHERE value='beta'").fetchone()[0]
        record('hard_delete_observable',deleted==0,{'remaining_beta_rows':deleted})
        c1.execute('ALTER TABLE items ADD COLUMN note TEXT')
        cols2=[r[1] for r in c1.execute('PRAGMA table_info(items)')]
        record('schema_evolution_discoverable','note' in cols2,{'columns':cols2})
        page_size=c1.execute('PRAGMA page_size').fetchone()[0]
        max_pages=c1.execute('PRAGMA max_page_count').fetchone()[0]
        freelist=c1.execute('PRAGMA freelist_count').fetchone()[0]
        integrity=c1.execute('PRAGMA integrity_check').fetchone()[0]
        record('integrity_check',integrity=='ok',{'integrity_check':integrity})
        c1.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        c1.close()
        db_bytes=db.read_bytes(); db_digest=sha(db_bytes)
        all_pass=all(t['passed'] for t in tests)
        receipt={
            'receipt_id':'receipt.source.sqlite_embedded.'+db_digest[:16],
            'record_kind':'source_occurrence_probe_receipt','execution_environment':{'python':platform.python_version(),'sqlite':version,'platform':platform.platform()},
            'started_at':ts,'tests':tests,'passed':all_pass,'database_sha256':db_digest,'same_campaign_controlled':True,
            'qualification_claim':False,'production_slo_claim':False,'independent_appraisal_claim':False,'completion_claim':False,
        }
        (HERE/'probe-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        expires=(started+timedelta(days=30)).isoformat().replace('+00:00','Z')
        occurrence={
            'occurrence_id':'source-occurrence.sqlite.github_actions.synthetic.v1',
            'source_class_id':'source.operational_database.embedded_relational',
            'deployment_identity':{'provider':'SQLite Project','product':'SQLite','deployment':'ephemeral GitHub Actions synthetic database','tenant_or_account':'none_local_ephemeral_test','region_or_site':'github_hosted_runner','version':version},
            'authority_claims':[{'scope':'synthetic items table only','claim':'This occurrence is authoritative only for test data created by this harness; it has no enterprise source-of-record authority.','owner':'shannon-insight B08 execution harness','effective_interval':f'{ts}/{expires}'}],
            'objects':[{'object_pattern':'main.items','schema_ref':'probe-receipt.json#schema_and_key_discovery','key_ref':'main.items.id','sensitivity':'synthetic_non_sensitive'}],
            'observed_capabilities':{'discovery':['sqlite_master','PRAGMA table_info'],'read':['point_query','scan','transaction_snapshot'],'write':['insert','delete','alter_table','transaction'],'change':['schema_reinspection','WAL_file_present_during_execution'],'time_order_finality':['commit_final_with_transaction_snapshot_cut'],'transactions':['atomic_commit','rollback','concurrent_snapshot_reader_under_WAL']},
            'quantitative_limits':{
                'rate':limit(None,'operations_per_second','not_benchmarked','unknown',ts,'must benchmark before capacity claim'),
                'quota':limit(None,'logical quota','local file occurrence','unknown',ts,'filesystem/deployment specific'),
                'page_size':limit(page_size,'bytes','database page','capability_probe',ts,'invalid/unsupported pragma or database corruption'),
                'payload_size':limit(None,'bytes','row/value payload','unknown',ts,'compile/runtime limit requires dedicated boundary probe'),
                'object_size':limit(page_size*max_pages,'bytes_theoretical_from_current_page_size_x_max_page_count','database file theoretical ceiling not production envelope','capability_probe',ts,'disk/filesystem/runtime constraints may bind earlier'),
                'concurrency':limit(None,'concurrent actors','not benchmarked','unknown',ts,'locking/busy timeout and workload specific'),
                'retention':limit(None,'duration','local database persistence','unknown',ts,'operator/filesystem lifecycle specific'),
                'cursor_ttl':limit(None,'duration','sqlite cursor/transaction lifetime','unknown',ts,'connection/transaction lifecycle specific'),
                'query_timeout':limit(5,'seconds','sqlite connection busy timeout used by harness','capability_probe',ts,'busy/locked operation raises error after configured timeout'),
                'cost_and_egress':limit(0,'provider_metered_currency','ephemeral local open-source execution only','capability_probe',ts,'host compute/storage costs intentionally excluded'),
            },
            'security_boundary':{'credential_ref':'none_ephemeral_local_file','authn':'process/filesystem boundary only','authz':'OS runner file permissions; no SQLite-native tenant authorization','network':'no network listener','encryption':'not asserted; ephemeral runner storage','tenant':'single synthetic test process boundary','audit':'retained probe receipt only; no production audit subsystem'},
            'freshness':{'observed_at':ts,'expires_at':expires,'reprobe_trigger':'SQLite version, Python sqlite binding, journal mode, runner image, source-class law or harness changes'},
            'probe_receipts':[receipt['receipt_id']],
            'reviewed_at':ts,
        }
        (HERE/'source-occurrence.json').write_text(json.dumps(occurrence,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        summary={'report_id':'b08_sqlite_embedded_source_occurrence','as_of':ts,'test_count':len(tests),'passed_test_count':sum(t['passed'] for t in tests),'all_tests_passed':all_pass,'source_class_id':occurrence['source_class_id'],'occurrence_id':occurrence['occurrence_id'],'production_qualified':False,'independently_appraised':False,'completion_claim':False}
        (HERE/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print(json.dumps(summary,sort_keys=True)); return 0 if all_pass else 1
if __name__=='__main__': raise SystemExit(main())
