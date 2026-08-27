#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    base=load_jsonl(HERE/'master-batches.jsonl')
    program=load_jsonl(HERE/'program-level-gates.jsonl')
    expanded=load_jsonl(HERE/'expanded-batches.jsonl')
    summary=json.loads((HERE/'expanded-summary.json').read_text(encoding='utf-8'))
    errors=[]
    expected=[f'B{i:02d}_' for i in range(21)]
    if len(base)!=16: errors.append(f'expected 16 base batches, got {len(base)}')
    if len(program)!=5: errors.append(f'expected 5 program gates, got {len(program)}')
    if len(expanded)!=21: errors.append(f'expected 21 expanded batches, got {len(expanded)}')
    ids=[r['batch_id'] for r in expanded]
    if len(ids)!=len(set(ids)): errors.append('duplicate batch IDs')
    for i,prefix in enumerate(expected):
        if not ids[i].startswith(prefix): errors.append(f'expanded DAG order mismatch at {i}: {ids[i]}')
    by_id={r['batch_id']:r for r in expanded}
    for row in expanded:
        for dep in row.get('depends_on',[]):
            if dep not in by_id: errors.append(f"{row['batch_id']}: unknown dependency {dep}")
    required={
      'B16_OPEN_WORLD_COVERAGE_NOVELTY':{'B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE','B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE','B09_DATA_SHAPE_OPERATION_TOTALITY'},
      'B17_INTENT_TO_SOLUTION_COMPOSITION':{'B10_IMPLEMENTATION_IDENTITY_AND_BUILD','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','B16_OPEN_WORLD_COVERAGE_NOVELTY'},
      'B18_APPLICATION_HUMAN_EFFECT_BOUNDARY':{'B17_INTENT_TO_SOLUTION_COMPOSITION'},
      'B19_MULTI_PRODUCT_SYSTEM_ACCEPTANCE':{'B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT','B13_PHYSICAL_BINDING_SLO_SECURITY_COST','B18_APPLICATION_HUMAN_EFFECT_BOUNDARY'},
      'B20_CONTINUOUS_VALIDITY_INVALIDATION':{'B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','B15_TWO_RELEASE_CHANGE_AND_RATIFICATION','B19_MULTI_PRODUCT_SYSTEM_ACCEPTANCE'},
    }
    for bid,deps in required.items():
        if set(by_id[bid]['depends_on'])!=deps: errors.append(f'{bid}: dependency law drift')
    b18=by_id['B18_APPLICATION_HUMAN_EFFECT_BOUNDARY']
    required_laws={'analytic_result != recommendation','recommendation != human_decision','human_decision != authorization','authorization != executed_business_effect','executed_business_effect != confirmed_outcome'}
    if not required_laws<=set(b18.get('non_collapse_laws',[])): errors.append('B18 core non-collapse laws incomplete')
    for row in program:
        if row.get('completion_claim') is not False: errors.append(f"{row['batch_id']}: completion claim must remain false")
        if not row.get('required_artifacts'): errors.append(f"{row['batch_id']}: no required artifacts")
        if not row.get('refusals'): errors.append(f"{row['batch_id']}: no refusal catalog")
    if summary.get('expanded_batch_count')!=21 or summary.get('completion_claim') is not False: errors.append('expanded summary invalid')
    if errors:
        for e in errors: print('ERROR:',e)
        return 1
    print('PASS expanded closure DAG: B00-B20, 5 program gates, dependency/non-collapse/refusal laws enforced; no completion promotion')
    return 0
if __name__=='__main__': raise SystemExit(main())
