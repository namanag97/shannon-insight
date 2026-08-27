#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ATLAS=HERE.parent
ROOT=ATLAS.parents[1]
METHODS=ROOT/'research/product_ontology/adjudications/analytical_methods'

def L(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    errors=[]
    queue={r['queue_id']:r for r in L(HERE/'canonical-reference-review-queue.jsonl')}
    ledger=[r for r in L(HERE/'canonical-reference-adjudications.jsonl') if r.get('research_tranche')=='b07.pack_common_operations.2026_08_27']
    gaps={r['gap_id']:r for r in L(HERE/'canonical-reference-extension-gaps.jsonl')}
    evidence={r['evidence_id']:r for r in L(HERE/'canonical-reference-research-evidence.jsonl')}
    ops={r['operation_id'] for r in L(ATLAS/'universes/operations/operation-candidates.jsonl')}
    contexts={r['context_id'] for r in L(ATLAS/'context_map/contexts.jsonl')}
    method_artifacts={r['artifact_id'] for r in L(METHODS/'artifacts.jsonl')}
    method_libraries={r['library_id'] for r in L(METHODS/'library-contracts.jsonl')}
    if len(ledger)!=32: errors.append(f'expected 32 tranche decisions, got {len(ledger)}')
    impact=0
    allowed_relations={
      'rehome_to_domain_semantic_extension','rehome_to_study_method_extension','rehome_to_analytical_method',
      'no_match_underspecified_rehome','rehome_to_intent_context','rehome_to_result_evaluation',
      'rehome_to_method_family','split_required_study_composition','split_required_optimization_composition',
      'split_required_cross_boundary_composition'
    }
    for d in ledger:
        qid=d['queue_id']
        q=queue.get(qid)
        if not q: errors.append(f'{qid}: source queue row missing'); continue
        impact+=q['occurrence_count']
        if q['reference_domain']!='typed_operation' or d['reference_domain']!='typed_operation': errors.append(f'{qid}: domain drift')
        if d['relation'] not in allowed_relations: errors.append(f'{qid}: unexpected relation {d["relation"]}')
        if d.get('completion_claim'): errors.append(f'{qid}: completion claim prohibited')
        if d.get('status')!='research_resolved_candidate_not_ratified': errors.append(f'{qid}: status over/under promotion')
        if not d.get('remaining_gate'): errors.append(f'{qid}: remaining gate required')
        if not d.get('non_collapse_laws'): errors.append(f'{qid}: non-collapse law required')
        if d.get('raw_ref')!=q['raw_ref']: errors.append(f'{qid}: raw ref drift')
        for r in d.get('target_operation_refs',[]):
            if r not in ops: errors.append(f'{qid}: unknown operation {r}')
        for r in d.get('target_context_refs',[]):
            if r not in contexts: errors.append(f'{qid}: unknown context {r}')
        for r in d.get('target_method_refs',[]):
            if r not in method_artifacts and r not in method_libraries: errors.append(f'{qid}: unknown method ref {r}')
        for r in d.get('extension_gap_refs',[]):
            if r not in gaps: errors.append(f'{qid}: unknown extension gap {r}')
        # Rehomes must not make work vanish: there is either a concrete target or typed extension gap.
        if not d.get('candidate_target_refs') and not d.get('extension_gap_refs'): errors.append(f'{qid}: rehome has no replacement obligation')
        for basis in d.get('decision_basis',[]):
            ev=basis.get('evidence_ref')
            if ev and ev not in evidence: errors.append(f'{qid}: unknown research evidence {ev}')
    if impact!=2779: errors.append(f'expected 2779 occurrence impact, got {impact}')
    # Risk/stress evidence must retain bounded use limits and must not become semantic authority.
    for eid in ['evidence.b07.iso31000.risk_management','evidence.b07.nist80030.risk_assessment','evidence.b07.bcbs.stress_testing']:
        ev=evidence.get(eid)
        if not ev: errors.append(f'missing evidence {eid}')
        elif not ev.get('bounded_claim') or not ev.get('use_limit') or ev.get('completion_claim'): errors.append(f'{eid}: evidence posture invalid')
    # Typed gaps are allowed B07 outcomes, never completion claims.
    for gid,g in gaps.items():
        if g.get('completion_claim') or g.get('status')!='OPEN_TYPED_EXTENSION_GAP': errors.append(f'{gid}: invalid extension-gap posture')
        if not g.get('required_resolution') or not g.get('non_collapse_laws'): errors.append(f'{gid}: incomplete gap contract')
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    print(f'PASS B07 pack-common tranche: {len(ledger)} identities / {impact} occurrences dispositioned; all replacement targets/gaps valid; 0 ratifications inferred')
    return 0
if __name__=='__main__': raise SystemExit(main())
