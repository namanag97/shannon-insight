#!/usr/bin/env python3
"""Build the canonical source-occurrence registry from retained execution packets.

Only source-occurrence documents that have a sibling successful summary and probe receipt are
admitted. This registry is discovery/routing only; it never upgrades production qualification,
independence or source authority beyond the occurrence's own bounded claims.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
EXECUTIONS=HERE/'executions'

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def sha(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->int:
    rows=[]; refused=[]
    for occurrence_path in sorted(EXECUTIONS.glob('*/source-occurrence.json')):
        execution_dir=occurrence_path.parent
        summary_path=execution_dir/'summary.json'; receipt_path=execution_dir/'probe-receipt.json'
        if not summary_path.exists() or not receipt_path.exists():
            refused.append({'path':str(occurrence_path.relative_to(HERE)),'reason':'missing_summary_or_probe_receipt'}); continue
        occurrence=json.loads(occurrence_path.read_text(encoding='utf-8'))
        summary=json.loads(summary_path.read_text(encoding='utf-8'))
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        if not summary.get('all_tests_passed') or not receipt.get('passed'):
            refused.append({'path':str(occurrence_path.relative_to(HERE)),'reason':'execution_not_passed'}); continue
        if summary.get('production_qualified') or summary.get('independently_appraised') or summary.get('completion_claim'):
            refused.append({'path':str(occurrence_path.relative_to(HERE)),'reason':'unsupported_promotion_in_summary'}); continue
        rows.append({
            'record_kind':'source_occurrence_registry_entry',
            'occurrence_id':occurrence['occurrence_id'],
            'source_class_id':occurrence['source_class_id'],
            'deployment_identity':occurrence['deployment_identity'],
            'authority_claims':occurrence['authority_claims'],
            'freshness':occurrence['freshness'],
            'security_boundary':occurrence['security_boundary'],
            'observed_capabilities':occurrence['observed_capabilities'],
            'quantitative_limits':occurrence['quantitative_limits'],
            'execution_packet_ref':str(execution_dir.relative_to(HERE)),
            'occurrence_sha256':sha(occurrence_path),
            'probe_receipt_sha256':sha(receipt_path),
            'summary_sha256':sha(summary_path),
            'production_qualified':False,
            'independently_appraised':False,
            'completion_claim':False,
        })
    rows.sort(key=lambda x:x['occurrence_id'])
    if len({r['occurrence_id'] for r in rows})!=len(rows): raise SystemExit('duplicate occurrence id')
    (HERE/'source-occurrences.jsonl').write_text(''.join(canonical(r)+'\n' for r in rows),encoding='utf-8')
    summary={
        'report_id':'source_system_occurrence_registry',
        'as_of':'2026-08-27',
        'completion_claim':False,
        'retained_occurrence_count':len(rows),
        'source_class_count_with_retained_occurrence':len({r['source_class_id'] for r in rows}),
        'production_qualified_occurrence_count':0,
        'independently_appraised_occurrence_count':0,
        'refused_packet_count':len(refused),
        'refused_packets':refused,
        'status':'POPULATED_RESEARCH_EXECUTION_OCCURRENCES_PRODUCTION_QUALIFICATION_WITHHELD' if rows else 'EMPTY',
    }
    (HERE/'occurrence-registry-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
