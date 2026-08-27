#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    master=load_jsonl(HERE/'master-batches.jsonl')
    base=master[:16]
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
    canonical_tail={r['batch_id']:r for r in master[16:]}
    if [r['batch_id'] for r in program] != [r['batch_id'] for r in master[16:]]:
        errors.append('program gate IDs drift from canonical master frontier')
    for bid,canonical in canonical_tail.items():
        if set(by_id[bid]['depends_on'])!=set(canonical['depends_on']): errors.append(f'{bid}: dependency law drift')
    b18=next(r for r in program if r['batch_id'].startswith('B18_'))
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
