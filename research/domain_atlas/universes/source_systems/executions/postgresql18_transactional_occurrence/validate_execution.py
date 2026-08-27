#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    errors=[]
    receipt=load(HERE/'probe-receipt.json'); occ=load(HERE/'source-occurrence.json'); offer=load(HERE/'provider-offer.json'); surface=load(HERE/'access-surface.json'); connector=load(HERE/'connector-capability.json'); plan=load(HERE/'acquisition-plan.json'); cut=load(HERE/'governed-data-cut.json'); summary=load(HERE/'summary.json')
    classes={r['class_id'] for r in load_jsonl(ROOT/'source-classes.jsonl')}
    expected={'server_identity_and_logical_wal','schema_and_key_discovery','repeatable_snapshot_stability','transaction_rollback_atomicity','logical_slot_identity','wal_position_advances_for_changes','logical_change_visibility','schema_evolution_discoverable','final_reconciliation'}
    tests={t['test_id']:t for t in receipt['tests']}
    if set(tests)!=expected or not all(t['passed'] for t in tests.values()): errors.append('exact PostgreSQL probe suite incomplete or failed')
    if occ['source_class_id']!='source.operational_database.relational_transactional' or occ['source_class_id'] not in classes: errors.append('occurrence class binding invalid')
    cdc='source.event_messaging_cdc.transaction_log_cdc'
    if cdc not in classes: errors.append('canonical CDC class missing')
    if set(offer['source_class_refs'])!={occ['source_class_id'],cdc}: errors.append('offer class set drift')
    if surface['occurrence_ref']!=occ['occurrence_id']: errors.append('surface occurrence mismatch')
    if set(connector['source_class_ids'])!={occ['source_class_id'],cdc}: errors.append('connector class set drift')
    if plan['occurrence_ref']!=occ['occurrence_id'] or plan['access_surface_ref']!=surface['surface_id'] or plan['connector_ref']!=connector['adapter_id']: errors.append('plan chain mismatch')
    if cut['occurrence_ref']!=occ['occurrence_id'] or cut['acquisition_plan_ref']!=plan['plan_id']: errors.append('cut chain mismatch')
    if cut['record_identity']['logical_rowset_digest']!=receipt['logical_rowset_sha256']: errors.append('logical rowset digest drift')
    if cut['record_identity']['record_count']!=3: errors.append('unexpected reconciled row count')
    if cut['completeness']['state']!='COMPLETE_FOR_DECLARED_SCOPE' or not cut['completeness']['known_residuals']: errors.append('bounded completeness posture missing')
    if 'external connector snapshot-to-CDC handoff not qualified' not in cut['completeness']['known_residuals']: errors.append('external CDC handoff residual lost')
    if plan['security']['least_privilege'].startswith('NOT SATISFIED') is False: errors.append('superuser least-privilege debt hidden')
    if summary['external_connector_qualified'] or summary['production_qualified'] or summary['independently_appraised'] or summary['completion_claim']: errors.append('summary promotion overclaim')
    if receipt['qualification_claim'] or receipt['production_slo_claim'] or receipt['independent_appraisal_claim'] or receipt['completion_claim']: errors.append('receipt promotion overclaim')
    # Validate new chain files against canonical schemas when jsonschema is available.
    try:
        import jsonschema
        for row,schema_name in [(occ,'source-occurrence.schema.json'),(offer,'provider-product-offer.schema.json'),(surface,'access-surface.schema.json'),(connector,'connector-capability.schema.json'),(plan,'acquisition-plan.schema.json'),(cut,'governed-data-cut.schema.json')]:
            schema=load(ROOT/schema_name); jsonschema.Draft202012Validator(schema).validate(row)
    except ImportError: pass
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    print(f"PASS PostgreSQL 18 occurrence: {len(tests)} executed tests; transactional snapshot + logical WAL/slot visibility + reconciled logical cut; external connector/production/appraisal withheld")
    return 0
if __name__=='__main__': raise SystemExit(main())
