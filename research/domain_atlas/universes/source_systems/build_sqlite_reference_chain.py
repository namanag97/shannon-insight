#!/usr/bin/env python3
"""Build the complete seven-stage B08 reference chain from the retained SQLite occurrence.

This is a reference exemplar for identity separation. It does not upgrade the synthetic
occurrence to production qualification and does not claim that a database-file digest is a
logical row-set digest.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXEC=HERE/'executions/sqlite_embedded_occurrence'

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def dump(name,obj): (HERE/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def main():
    occ=load(EXEC/'source-occurrence.json')
    receipt=load(EXEC/'probe-receipt.json')
    ts=receipt['started_at']
    rid=receipt['receipt_id']
    sqlite_version=occ['deployment_identity']['version']
    cls=occ['source_class_id']
    offer={
      'offer_id':'source-offer.sqlite.embedded_relational.current_documented',
      'provider':'SQLite Project','product':'SQLite','edition_or_version_envelope':sqlite_version,
      'source_class_refs':[cls],
      'documented_object_families':['database file','tables','rows','indexes','schema metadata'],
      'documented_access_surface_kinds':['embedded database API','database file'],
      'evidence_refs':['ev.sqlite.isolation'],
      'status':'DOCUMENTED_OFFER_CANDIDATE',
      'non_collapse':['documented SQLite behavior != this GitHub occurrence','SQLite product != embedded-relational source class','SQLite API != connector implementation','documented isolation != executed conformance receipt'],
      'completion_claim':False,
    }
    surface={
      'surface_id':'source-surface.sqlite.github_actions.synthetic.database_api.v1',
      'occurrence_ref':occ['occurrence_id'],'surface_kind':'database','protocol_or_format':'SQLite database API / file format via CPython sqlite3',
      'endpoint_or_locator_class':'ephemeral local database file','object_scope':['main.items'],
      'read_modes':['point_query','scan','transaction_snapshot'],'change_modes':['schema_reinspection','WAL_observation'],
      'authority_scope':'synthetic items table only','observed_limits':occ['quantitative_limits'],'security_requirements':occ['security_boundary'],
      'observed_at':occ['freshness']['observed_at'],'expires_at':occ['freshness']['expires_at'],'evidence_refs':[rid],'status':'OBSERVED',
      'non_collapse':['access surface != SQLite product offer','access surface != source occurrence','access surface != Python connector implementation','observed surface != successful governed acquisition'],
      'completion_claim':False,
    }
    connector={
      'adapter_id':'connector.python_stdlib.sqlite3.github_actions.v1','source_class_ids':[cls],'protocol':'CPython sqlite3 DB-API binding to SQLite',
      'versions':{'protocol':'Python DB-API 2.0 sqlite3 module surface','implementation':f"CPython {receipt['execution_environment']['python']} sqlite3 / SQLite {sqlite_version}",'minimum_source':'not established','maximum_tested_source':sqlite_version},
      'license':{'spdx_or_policy':'Python-2.0 for CPython; SQLite public-domain project posture requires separate legal interpretation','redistribution':'not adjudicated by this receipt','support_status':'test-harness reference adapter only'},
      'operations':{'discovery':['PRAGMA table_info'],'read':['query','scan','transaction snapshot'],'write':['insert','delete','alter table','transaction'],'change':['WAL observation','schema reinspection']},
      'delivery':{'guarantee':'transactional reads/writes for tested scope','ordering_scope':'database transaction / statement order','checkpoint':'transaction snapshot only; no durable CDC checkpoint qualified','resume':'reopen database and new transaction','replay':'query from retained database state only','backfill':'full table scan','deduplication':'caller key/idempotency required','transaction_boundary':'SQLite database transaction'},
      'schema':{'discovery':'PRAGMA table_info','inference':'declared SQLite schema only','drift':'reinspect schema','compatibility':'application-specific and unqualified','unknown_fields':'fail closed in governed mapping','deprecation':'not qualified'},
      'temporal':{'event_time':'not intrinsic','recorded_time':'commit order only','cursor_time':'transaction-local','watermark':'none','late_data':'not intrinsic','revision':'new committed state','tombstone':'hard delete tested; tombstone semantics absent'},
      'security':{'credential_reference_only':True,'authentication':'process/filesystem boundary','authorization':'OS file permission only in this occurrence','encryption':'not asserted','network_boundary':'no network listener','secret_rotation':'not applicable to local synthetic file','audit':'probe receipt only'},
      'limits':{'rate':'not benchmarked','quota':'deployment specific','page':occ['quantitative_limits']['page_size'],'payload':'not benchmarked','concurrency':'not benchmarked','retention':'operator/filesystem specific','query_cost':'not benchmarked'},
      'observability':{'health':'PRAGMA integrity_check','metrics':'probe-local only','logs':'GitHub Actions log','traces':'none','lineage':'receipt + occurrence + chain identities','dead_letter':'none','retry':'typed SQLite exception handling required','runbook':'reference harness only','owner':'shannon-insight B08 research harness'},
      'conformance_receipts':[{'test_id':'verify.sqlite.'+t['test_id'],'result':'pass' if t['passed'] else 'fail','executed_at':ts,'artifact_ref':rid} for t in receipt['tests']],
    }
    plan={
      'plan_id':'acquisition-plan.sqlite.github_actions.synthetic.items.v1','occurrence_ref':occ['occurrence_id'],'access_surface_ref':surface['surface_id'],'connector_ref':connector['adapter_id'],'requested_source_class_refs':[cls],
      'object_selection':{'include':['main.items'],'columns':['id','value','amount','note'],'predicate':'all retained rows after tested mutation sequence'},
      'initial_cut':{'mode':'snapshot','consistency_requirement':'single SQLite read transaction snapshot','boundary_identity':'final retained database state after tested sequence'},
      'change_capture':{'mode':'none_for_governed_cut','cursor_or_position':'none','ordering_scope':'not applicable to sealed snapshot','duplicate_policy':'primary-key uniqueness required','gap_policy':'refuse if snapshot/reconciliation mismatch','retention_expiry_policy':'reprobe/reacquire'},
      'handoff':{'snapshot_to_change_law':'not claimed; no CDC handoff qualified','overlap_policy':'not applicable','gap_detection':'reconciliation required before sealing','unknown_outcome_policy':'do not seal cut'},
      'reconciliation':{'count_or_hash':'database-byte SHA-256 plus final row count','key_coverage':'id primary key discovered','delete_coverage':'hard delete of beta explicitly tested','frequency':'once before sealing synthetic cut','failure_posture':'REFUSE_CUT'},
      'retry_and_idempotency':{'snapshot':'new transaction and full reconciliation','writes':'outside governed acquisition scope'},
      'schema_change':{'discovery':'PRAGMA table_info','compatibility':'exact expected final column set for this cut','unknown_field_policy':'refuse until mapping updated','breaking_change_policy':'new plan/cut edition'},
      'deletion_and_correction':{'hard_delete':'represented in final snapshot','soft_delete':'not intrinsic/untested','correction':'latest committed row state only'},
      'security':{'credential_ref_only':True,'least_privilege':'local file/process boundary only','network_boundary':'no network listener','audit':'retained probe and plan identities'},
      'budgets':{'time':'GitHub Actions job bound','memory':'not benchmarked','concurrency':'one acquisition reader','rate':'not benchmarked','cost':'provider-metered cost excluded'},
      'output_cut_contract':{'governed_cut_required':True,'lineage_required':True,'completeness_state_required':True},
      'refusal_rules':['occurrence evidence expired','schema differs from expected final schema','integrity_check fails','row-count reconciliation fails','source class or access surface identity changes','connector version changes without re-execution'],
      'status':'EXECUTABLE','non_collapse':['acquisition plan != source class','acquisition plan != occurrence','acquisition plan != connector capability','snapshot success != completeness until reconciliation','plan != governed data cut'],'completion_claim':False,
    }
    # The historical harness retained the exact final database bytes and SHA but not a canonical
    # logical row serialization. Therefore the governed cut explicitly uses the database-byte
    # digest as physical population evidence and records the absence of a logical row-set digest.
    final_count=2
    cut={
      'cut_id':'governed-cut.sqlite.github_actions.synthetic.items.v1','occurrence_ref':occ['occurrence_id'],'acquisition_plan_ref':plan['plan_id'],'source_class_refs':[cls],'object_scope':['main.items'],
      'schema_identity':{'schema_digest':'not_separately_retained_historical_harness','compatibility_profile':'exact final schema columns include id,value,amount,note','schema_evidence_ref':rid+'#schema_evolution_discoverable'},
      'time_bounds':{'business_or_event_time':'not intrinsic synthetic rows','recorded_or_commit_time':'bounded by the executed mutation sequence; exact per-row commit timestamps not retained','ingestion_time':ts},
      'position_bounds':{'start':'synthetic database creation','end':'final WAL checkpoint and database byte digest','ordering_scope':'SQLite commit order for this harness','finality':'final retained database bytes after successful integrity check'},
      'record_identity':{'population_digest':receipt['database_sha256'],'population_digest_basis':'PHYSICAL_DATABASE_BYTES_NOT_LOGICAL_ROWSET','logical_rowset_digest':None,'record_count':final_count,'key_coverage':'id INTEGER PRIMARY KEY discovered'},
      'completeness':{'state':'COMPLETE_FOR_DECLARED_SCOPE','reconciliation_receipt_ref':rid,'known_residuals':['logical canonical row-set digest was not retained by historical harness','no CDC handoff qualified','no production source authority']},
      'deletions_and_corrections':{'represented':True,'policy':'final snapshot includes tested hard deletion; no soft-delete/tombstone semantics asserted','residuals':['correction history not retained separately']},
      'authority_refs':['synthetic items table authority only'],'lineage':{'source_occurrence':occ['occurrence_id'],'access_surface':surface['surface_id'],'connector':connector['adapter_id'],'plan':plan['plan_id'],'execution_receipts':[rid]},
      'evidence_refs':[rid,occ['occurrence_id']],'created_at':ts,'status':'SEALED',
      'non_collapse':['governed cut != SQLite occurrence','governed cut != connector run','physical database digest != canonical logical row-set digest','synthetic completeness != production completeness','sealed cut authority is bounded to synthetic items table'],
      'completion_claim':False,
    }
    (HERE/'provider-product-offers.jsonl').write_text(json.dumps(offer,sort_keys=True)+'\n',encoding='utf-8')
    (HERE/'access-surfaces.jsonl').write_text(json.dumps(surface,sort_keys=True)+'\n',encoding='utf-8')
    (HERE/'connector-capabilities.jsonl').write_text(json.dumps(connector,sort_keys=True)+'\n',encoding='utf-8')
    (HERE/'acquisition-plans.jsonl').write_text(json.dumps(plan,sort_keys=True)+'\n',encoding='utf-8')
    (HERE/'governed-data-cuts.jsonl').write_text(json.dumps(cut,sort_keys=True)+'\n',encoding='utf-8')
    summary={'report_id':'sqlite_full_source_acquisition_reference_chain','as_of':'2026-08-27','source_classes':1,'provider_offers':1,'source_occurrences':1,'access_surfaces':1,'connector_implementations':1,'acquisition_plans':1,'governed_data_cuts':1,'production_qualified':False,'independently_appraised':False,'completion_claim':False}
    dump('source-acquisition-reference-summary.json',summary); print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
