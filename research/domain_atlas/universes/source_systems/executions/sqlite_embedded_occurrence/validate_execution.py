#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def load_jsonl(p):return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    errors=[]
    receipt=json.loads((HERE/'probe-receipt.json').read_text(encoding='utf-8'))
    occurrence=json.loads((HERE/'source-occurrence.json').read_text(encoding='utf-8'))
    summary=json.loads((HERE/'summary.json').read_text(encoding='utf-8'))
    classes={r['class_id'] for r in load_jsonl(ROOT/'source-classes.jsonl')}
    if occurrence['source_class_id'] not in classes: errors.append('unknown source class')
    required={'deployment_identity','authority_claims','objects','observed_capabilities','quantitative_limits','security_boundary','freshness','probe_receipts','reviewed_at'}
    if not required<=set(occurrence): errors.append('source occurrence required fields missing')
    limit_keys={'rate','quota','page_size','payload_size','object_size','concurrency','retention','cursor_ttl','query_timeout','cost_and_egress'}
    if set(occurrence['quantitative_limits'])!=limit_keys: errors.append('quantitative limit dimensions incomplete')
    required_tests={'journal_mode_wal','schema_and_key_discovery','repeatable_read_basic','transaction_rollback_atomicity','snapshot_cut_stability','hard_delete_observable','schema_evolution_discoverable','integrity_check'}
    tests={r['test_id']:r for r in receipt['tests']}
    if set(tests)!=required_tests or not all(r['passed'] for r in tests.values()): errors.append('probe test suite incomplete or failed')
    if not receipt['passed'] or receipt['qualification_claim'] or receipt['production_slo_claim'] or receipt['independent_appraisal_claim'] or receipt['completion_claim']: errors.append('receipt promotion posture invalid')
    if summary['test_count']!=len(tests) or summary['passed_test_count']!=len(tests) or not summary['all_tests_passed']: errors.append('summary drift')
    if summary['production_qualified'] or summary['independently_appraised'] or summary['completion_claim']: errors.append('summary overclaim')
    if occurrence['authority_claims'][0]['scope']!='synthetic items table only': errors.append('authority scope broadened')
    if occurrence['security_boundary']['network']!='no network listener': errors.append('unexpected network claim')
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    print(f"PASS SQLite source occurrence: {len(tests)} executed probes; exact class bound; synthetic authority only; production qualification/appraisal withheld")
    return 0
if __name__=='__main__': raise SystemExit(main())
