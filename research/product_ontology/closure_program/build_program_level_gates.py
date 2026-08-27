#!/usr/bin/env python3
"""Build B16-B20 program-level closure gates on top of the B00-B15 qualification spine."""
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def load_jsonl(p:Path): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def dump_jsonl(p:Path, rows): p.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')

def main():
    base=load_jsonl(HERE/'master-batches.jsonl')
    base_ids={r['batch_id'] for r in base}
    required_base={f'B{i:02d}_' for i in range(16)}
    if len(base)!=16 or len(base_ids)!=16:
        raise SystemExit('expected exactly B00-B15 base spine')

    program=[
      {
        'batch_id':'B16_OPEN_WORLD_COVERAGE_NOVELTY',
        'record_kind':'program_level_closure_gate','edition':1,
        'depends_on':['B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE','B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE','B09_DATA_SHAPE_OPERATION_TOTALITY'],
        'question':'Does the discoverable world predominantly compose existing contracts, and do novel concepts fail closed as explicit extension gaps?',
        'scope':['industry and subindustry coverage','profession and business lifecycle coverage','analytical-question coverage','source-system and data-modality coverage','recurring standards/product/paper discovery','held-out industries','novelty testing','structural saturation trend'],
        'required_artifacts':['coverage_sampling_frame','held_out_domain_set','novelty_test_run','new_constructor_or_gap_register','structural_discovery_curve','independent_review_cycle_receipts'],
        'exit_condition':'Two consecutive disjoint discovery cycles over held-out industries/professions/source modalities add no unmodeled core constructor; every novel concept is either composed from existing contracts or retained as a typed extension gap with evidence.',
        'refusals':['held_out_domains_overlap_model_training_set_without_disclosure','new_concept_forced_into_nearby_type','coverage_claim_from_counts_only','single_reviewer_saturation_claim','unbounded_unknown_category_silently_ignored'],
        'status':'OPEN_PROGRAM_GATE','completion_claim':False,
      },
      {
        'batch_id':'B17_INTENT_TO_SOLUTION_COMPOSITION',
        'record_kind':'program_level_closure_gate','edition':1,
        'depends_on':['B10_IMPLEMENTATION_IDENTITY_AND_BUILD','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','B16_OPEN_WORLD_COVERAGE_NOVELTY'],
        'question':'Can governed business intent deterministically or explicitly human-assist into a coherent evidence-backed solution?',
        'scope':['requirement/offer matching','compatibility solving','configuration completeness','authority/policy propagation','logical analytical planning','product/library selection','provider/connector/runtime binding','IR lowering','refusal explanations','alternative plans/tradeoffs','deterministic reproduction','human-governed unresolved decisions'],
        'required_artifacts':['intent_declaration','requirement_set','candidate_solution_plan','compatibility_proof_or_refusal','decision_register','lowered_ir_or_human_plan','selected_offer_bindings','reproduction_manifest'],
        'exit_condition':'Representative intents from unrelated domains either produce the same reproducible solution plan from identical inputs or a typed bounded refusal/human-decision request; no provider or industry detail becomes universal semantics.',
        'refusals':['configuration_incomplete','authority_unresolved','no_compatible_offer','ambiguous_solution_without_governed_decision','non_reproducible_plan','silent_provider_assumption','compiler_claims_decision_it_does_not_own'],
        'status':'OPEN_PROGRAM_GATE','completion_claim':False,
      },
      {
        'batch_id':'B18_APPLICATION_HUMAN_EFFECT_BOUNDARY',
        'record_kind':'program_level_closure_gate','edition':1,
        'depends_on':['B17_INTENT_TO_SOLUTION_COMPOSITION'],
        'question':'Can a complete enterprise application preserve the boundaries among information, recommendation, human judgment, authorization, effect and confirmed outcome?',
        'scope':['workflows and cases','forms and collection','documents and notifications','UI state and interaction','accessibility/localization/device behavior','offline/synchronization','human judgment/review','approval and segregation of duties','irreversible effects/compensation','appeal/correction/recall/disclosure','explanation/evidence presentation'],
        'non_collapse_laws':['analytic_result != recommendation','recommendation != human_decision','human_decision != authorization','authorization != executed_business_effect','executed_business_effect != confirmed_outcome','UI_intent != admitted_command','notification != acknowledgement','draft != durable_fact'],
        'required_artifacts':['journey_or_work_graph','human_decision_points','authority_matrix','effect_boundary_map','compensation_or_recovery_plan','accessibility_equivalence_evidence','offline_conflict_policy','explanation_provenance_binding'],
        'exit_condition':'End-to-end application scenarios preserve every non-collapse law under success, refusal, retry, offline, partial-effect, recall and appeal cases; UI/human layers never mint unauthorized facts or effects.',
        'refusals':['recommendation_auto_promoted_to_decision','authorization_missing','effect_without_idempotency_or_compensation','offline_conflict_unresolved','accessibility_equivalent_task_missing','UI_state_treated_as_business_truth'],
        'status':'OPEN_PROGRAM_GATE','completion_claim':False,
      },
      {
        'batch_id':'B19_MULTI_PRODUCT_SYSTEM_ACCEPTANCE',
        'record_kind':'program_level_closure_gate','edition':1,
        'depends_on':['B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT','B13_PHYSICAL_BINDING_SLO_SECURITY_COST','B18_APPLICATION_HUMAN_EFFECT_BOUNDARY'],
        'question':'Do many individually valid products still compose correctly as one faulted system of systems?',
        'scope':['cross-product time semantics','identity compatibility','transaction-boundary loss','retry amplification','authorization freshness','partial effects','lineage continuity','schema/version skew','cross-product recovery','deletion/recall propagation','backpressure and budget propagation'],
        'required_artifacts':['solution_system_graph','cross_product_contract_matrix','fault_injection_plan','end_to_end_trace_and_lineage','recovery_order','deletion_recall_propagation_receipt','retry_budget_receipt','version_skew_matrix'],
        'exit_condition':'At least two materially different multi-product solutions pass fault-injected end-to-end scenarios with complete evidence tracing, bounded retries, explicit partial-effect handling, compatible identities/time semantics and recoverable deletion/recall propagation.',
        'refusals':['cross_product_identity_ambiguous','time_semantics_incompatible','retry_budget_unbounded','partial_effect_unowned','lineage_break','recovery_order_missing','deletion_or_recall_stops_silently'],
        'status':'OPEN_PROGRAM_GATE','completion_claim':False,
      },
      {
        'batch_id':'B20_CONTINUOUS_VALIDITY_INVALIDATION',
        'record_kind':'program_level_closure_gate','edition':1,
        'depends_on':['B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','B15_TWO_RELEASE_CHANGE_AND_RATIFICATION','B19_MULTI_PRODUCT_SYSTEM_ACCEPTANCE'],
        'question':'Does any material upstream or operational change invalidate every stale conclusion and generate bounded requalification/migration work?',
        'scope':['provider/API version changes','connector deprecation','price/quota changes','security advisories','standards revisions','schema/taxonomy changes','data/behavior drift','evidence expiry','requalification triggers','incidents','supplier failure/exit','product/library decommission'],
        'required_artifacts':['dependency_impact_graph','evidence_validity_intervals','invalidation_rules','change_event_ingestion','affected_scope_query','requalification_work_item','migration_or_exit_plan','decommission_receipt'],
        'exit_condition':'For every seeded material-change class, the system identifies all affected contracts, solutions, deployments and proofs, marks stale verdicts invalid before reuse, and emits bounded requalification, migration, rollback, exit or decommission work.',
        'refusals':['expired_evidence_reused','changed_provider_offer_not_propagated','security_advisory_without_impact_scan','schema_or_taxonomy_change_silently_accepted','supplier_exit_without_portability_path','decommission_leaves_live_dependents'],
        'status':'OPEN_PROGRAM_GATE','completion_claim':False,
      },
    ]
    all_rows=base+program
    ids={r['batch_id'] for r in all_rows}
    for row in all_rows:
        missing=[d for d in row.get('depends_on',[]) if d not in ids]
        if missing: raise SystemExit(f"{row['batch_id']}: missing dependencies {missing}")
    dump_jsonl(HERE/'program-level-gates.jsonl',program)
    dump_jsonl(HERE/'expanded-batches.jsonl',all_rows)
    summary={
      'report_id':'expanded_program_closure_frontier','as_of':'2026-08-27','base_batch_count':len(base),'program_level_gate_count':len(program),'expanded_batch_count':len(all_rows),'program_level_gate_ids':[r['batch_id'] for r in program],
      'application_and_solution_completion_requires':['B16_OPEN_WORLD_COVERAGE_NOVELTY','B17_INTENT_TO_SOLUTION_COMPOSITION','B18_APPLICATION_HUMAN_EFFECT_BOUNDARY','B19_MULTI_PRODUCT_SYSTEM_ACCEPTANCE','B20_CONTINUOUS_VALIDITY_INVALIDATION'],
      'all_program_gates_open':True,'completion_claim':False,
      'status':'EXPANDED_B00_B20_DAG_DEFINED_NO_PROGRAM_COMPLETION_CLAIM'
    }
    (HERE/'expanded-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
