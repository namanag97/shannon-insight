#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def load_jsonl(path: Path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def main() -> int:
    errors=[]
    readiness=load_jsonl(HERE/'product-readiness.jsonl')
    rows=load_jsonl(HERE/'product-boundary-falsification.jsonl')
    summary=json.loads((HERE/'product-boundary-falsification-summary.json').read_text(encoding='utf-8'))
    by_candidate={r['candidate_id']:r for r in rows}
    expected={r['candidate_id'] for r in readiness}
    if set(by_candidate)!=expected or len(rows)!=len(expected): errors.append('falsification must cover every retained product exactly once')
    required_tests={'MERGE','SPLIT','DEMOTE_TO_CAPABILITY_OR_LIBRARY','REHOME_EXTERNAL_OR_VERTICAL','REJECT_DUPLICATE_OR_NONPRODUCT'}
    for product in readiness:
        row=by_candidate.get(product['candidate_id'])
        if not row: continue
        if row['dossier_ref']!=product['product_specific_ddd']['dossier_ref']: errors.append(f"dossier drift {row['candidate_id']}")
        if not row['sovereign_question'] or not row['negative_mission']: errors.append(f"weak sovereignty {row['candidate_id']}")
        surface=row['owned_structural_surface']
        for key in ('aggregate_roots','commands','domain_events','state_machine_roots','published_language','inside_boundary','outside_boundary'):
            if not surface.get(key): errors.append(f"missing {key} {row['candidate_id']}")
        tests={t['disposition_if_true'] for t in row['falsification_tests']}
        if tests!=required_tests: errors.append(f"incomplete falsification dispositions {row['candidate_id']}")
        if any(not t['falsifier'] or not t['required_evidence'] for t in row['falsification_tests']): errors.append(f"weak falsifier {row['candidate_id']}")
        if row['ratification']!='WITHHELD' or row['completion_claim']: errors.append(f"boundary overclaim {row['candidate_id']}")
        if row['independent_adoption_evidence_state']!='OPEN_PRODUCT_SPECIFIC_EVIDENCE_REQUIRED': errors.append(f"adoption evidence overclaim {row['candidate_id']}")
    if summary['retained_product_count']!=len(readiness) or summary['falsification_contract_count']!=len(rows): errors.append('summary count drift')
    if summary['product_specific_independent_adoption_evidence_complete_count']!=0 or summary['ratified_boundary_count']!=0 or summary['completion_claim']: errors.append('summary overclaim')
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    print(f"PASS product boundary falsification: {len(rows)} retained products each have merge/split/demote/rehome/reject tests; adoption/economic/ratification evidence withheld")
    return 0
if __name__=='__main__': raise SystemExit(main())
