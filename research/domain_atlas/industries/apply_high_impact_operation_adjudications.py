#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
D={
'refq.typed_operation.098231823f695fa7':{'relation':'split_required_composition','targets':['operation.identity_entity.resolve_composite_identity','operation.temporal.temporal_as_of_join'],'laws':['identity resolution != temporal nearest-match join','dimension equality predicate != as-of ordering predicate'],'evidence':['evidence.b07.duckdb.asof_join'],'gate':'semantic-owner ratification of both component operations and compiler preservation of both refusals'},
'refq.typed_operation.1c48d25187e9c342':{'relation':'rehome_and_split_required','targets':['operation.connector_session.authorize_connector_operation','operation.snapshot_extract.read_consistent_multi_object_snapshot'],'laws':['authorized != acquired','authorized != complete cut','access-control decision cannot mint source facts'],'evidence':['evidence.b07.nist.sp800_162.abac'],'gate':'B08 source-acquisition authority plus access-control authority'},
'refq.typed_operation.38182951decdf811':{'relation':'split_required_method_bound_composition','targets':['operation.statistical_kernel.summarize_uncertainty','operation.output_consumption.attach_uncertainty_to_result'],'laws':['estimator != uncertainty evaluator','confidence interval != credible interval','uncertainty summary != central estimate'],'evidence':['evidence.b07.bipm.jcgm100_uncertainty'],'gate':'method/uncertainty authority must bind estimator and uncertainty relation'},
'refq.typed_operation.c62dcaf6ce05e05e':{'relation':'split_required_cross_boundary_composition','targets':['operation.output_consumption.attach_evidence_to_result','operation.output_consumption.construct_decision_recommendation','operation.output_consumption.publish_output'],'laws':['evidence != recommendation','recommendation != decision authority','decision != authorization','authorization != executed effect'],'evidence':['evidence.b07.w3c.prov_o','evidence.b07.omg.dmn15'],'gate':'output/recommendation authority and application decision/effect boundaries'},
'refq.typed_operation.bf16c19771bb5f9b':{'relation':'split_required_cross_boundary_composition','targets':['operation.output_consumption.record_decision_action','operation.output_consumption.record_outcome_feedback','operation.optimization_simulation.evaluate_realized_decision_outcome'],'laws':['decision action occurrence != outcome observation','outcome observation != causal attribution','evaluation != authorization'],'evidence':['evidence.b07.w3c.prov_o','evidence.b07.omg.dmn15'],'gate':'action/effect/outcome semantic owners and temporal linkage'},
'refq.typed_operation.9347d2fb25cbaf82':{'relation':'split_required_missing_prerequisite','targets':['operation.reconciliation.compare_source_and_target'],'laws':['reconciliation != grain transformation','aggregation/disaggregation != lossless grain alignment','same column names != same grain'],'evidence':['evidence.b07.kimball.grain'],'gate':'B09 must supply grain-change/alignment algebra and loss/refusal laws','dependencies':['gap.context_map.007']},
}
def L(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 queue={r['queue_id']:r for r in L(HERE/'canonical-reference-review-queue.jsonl')}; ledger={r['queue_id']:r for r in L(HERE/'canonical-reference-adjudications.jsonl')}; ops={r['operation_id'] for r in L(HERE.parent/'universes/operations/operation-candidates.jsonl')}; ev={r['evidence_id'] for r in L(HERE/'canonical-reference-research-evidence.jsonl')}; errors=[]; impact=0
 for qid,s in D.items():
  q=queue.get(qid)
  if not q: errors.append(qid+': missing queue'); continue
  impact+=q['occurrence_count']
  for t in s['targets']:
   if t not in ops: errors.append(qid+': unknown '+t)
  for e in s['evidence']:
   if e not in ev: errors.append(qid+': missing evidence '+e)
  ledger[qid]={'queue_id':qid,'record_kind':'canonical_reference_adjudication','edition':1,'reference_domain':'typed_operation','raw_ref':q['raw_ref'],'relation':s['relation'],'candidate_target_refs':s['targets'],'target_operation_refs':s['targets'],'non_collapse_laws':s['laws'],'decision_basis':[{'claim':'High-impact research decomposes the vertical compound without inventing a new sovereign mega-operation.','evidence_ref':e} for e in s['evidence']],'required_dependency_refs':s.get('dependencies',[]),'remaining_gate':s['gate'],'status':'research_resolved_candidate_not_ratified','completion_claim':False,'research_tranche':'b07.high_impact_operations.2026_08_27'}
 if impact!=1296: errors.append(f'expected impact 1296, got {impact}')
 if errors: print('\n'.join('ERROR: '+x for x in errors)); return 1
 rows=sorted(ledger.values(),key=lambda r:r['queue_id']); (HERE/'canonical-reference-adjudications.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows)); print(f'PASS 6 decisions / {impact} occurrences'); return 0
if __name__=='__main__': raise SystemExit(main())
