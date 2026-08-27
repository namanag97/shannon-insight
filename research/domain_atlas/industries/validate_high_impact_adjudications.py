#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ATLAS=HERE.parent
ROOT=ATLAS.parents[1]
TARGETS={
 'refq.typed_operation.098231823f695fa7',
 'refq.typed_operation.1c48d25187e9c342',
 'refq.typed_operation.38182951decdf811',
 'refq.typed_operation.c62dcaf6ce05e05e',
 'refq.typed_operation.bf16c19771bb5f9b',
 'refq.typed_operation.9347d2fb25cbaf82',
}
ALLOWED_RELATIONS={
 'split_required_composition','rehome_and_split_required','split_required_method_bound_composition',
 'split_required_cross_boundary_composition','split_required_missing_prerequisite'
}
def L(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 errors=[]
 queue={r['queue_id']:r for r in L(HERE/'canonical-reference-review-queue.jsonl')}
 decisions={r['queue_id']:r for r in L(HERE/'canonical-reference-adjudications.jsonl')}
 evidence={r['evidence_id']:r for r in L(HERE/'canonical-reference-research-evidence.jsonl')}
 operations={r['operation_id'] for r in L(ATLAS/'universes/operations/operation-candidates.jsonl')}
 context_gaps={r['gap_id'] for r in L(ATLAS/'context_map/gaps.jsonl')}
 if not TARGETS <= decisions.keys(): errors.append('six high-impact decisions not all present')
 impact=0
 for qid in sorted(TARGETS):
  if qid not in queue: errors.append(f'{qid}: queue row missing'); continue
  d=decisions[qid]; impact+=queue[qid]['occurrence_count']
  if d.get('completion_claim'): errors.append(f'{qid}: completion claim prohibited')
  if d.get('status')!='research_resolved_candidate_not_ratified': errors.append(f'{qid}: invalid research status')
  if d.get('relation') not in ALLOWED_RELATIONS: errors.append(f'{qid}: unexpected relation {d.get("relation")}')
  if not d.get('remaining_gate'): errors.append(f'{qid}: remaining gate required')
  if not d.get('non_collapse_laws'): errors.append(f'{qid}: non-collapse laws required')
  for ref in d.get('candidate_target_refs',[]):
   if ref not in operations: errors.append(f'{qid}: unknown operation target {ref}')
  for basis in d.get('decision_basis',[]):
   ev=basis.get('evidence_ref')
   if ev and ev.startswith('evidence.b07.') and ev not in evidence: errors.append(f'{qid}: missing evidence {ev}')
 if impact!=1296: errors.append(f'expected 1296 occurrence impact, got {impact}')
 grain=decisions['refq.typed_operation.9347d2fb25cbaf82']
 if 'gap.context_map.007' not in grain.get('required_dependency_refs',[]): errors.append('grain reconciliation must retain gap.context_map.007 dependency')
 if 'gap.context_map.007' not in context_gaps: errors.append('grain dependency does not exist in context gap ledger')
 cut=decisions['refq.typed_operation.1c48d25187e9c342']
 for rel in cut.get('required_dependency_refs',[]):
  if rel.startswith('research/') and not (ROOT/rel).exists(): errors.append(f'authorized source cut dependency missing: {rel}')
 # Evidence roles are bounded and none may claim universal semantic authority.
 for ev in evidence.values():
  if ev.get('completion_claim'): errors.append(f"{ev['evidence_id']}: completion claim prohibited")
  if not ev.get('bounded_claim') or not ev.get('use_limit'): errors.append(f"{ev['evidence_id']}: bounded claim/use limit required")
 if errors:
  for e in errors: print('ERROR: '+e)
  return 1
 print(f'PASS B07 high-impact adjudications: {len(TARGETS)} identities / {impact} occurrences research-resolved; authority and downstream dependencies retained')
 return 0
if __name__=='__main__': raise SystemExit(main())
