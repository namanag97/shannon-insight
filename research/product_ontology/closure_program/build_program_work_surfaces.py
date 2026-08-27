#!/usr/bin/env python3
"""Materialize finite B16-B20 work surfaces from committed corpora.

These are obligations and challenge coordinates, not acceptance results.
"""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def jl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def j(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def write_jl(name,rows): (HERE/name).write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
def hid(s): return hashlib.sha256(s.encode()).hexdigest()[:16]

def main():
    isic=jl(ROOT/'research/domain_atlas/industries/foundation/isic-rev5.nodes.jsonl')
    schemes=j(ROOT/'research/domain_atlas/industries/foundation/classification-schemes.json')
    occupation_ext=jl(ROOT/'research/domain_atlas/industries/foundation/occupation-classification-extension.jsonl')
    sources=j(ROOT/'research/domain_atlas/universes/source_systems/coverage-report.json')
    practices=jl(ROOT/'research/domain_atlas/universes/analytics_types/candidate-practices.jsonl')
    verticals=jl(ROOT/'research/product_ontology/composition_pilots/deterministic_verticals/vertical-compositions.jsonl')

    # B16: open-world sampling frame. No section is declared covered merely because a broad pack exists.
    b16=[]
    for node in isic:
        if node.get('level')!='section': continue
        b16.append({'record_kind':'b16_coverage_coordinate','coordinate_id':'b16.industry.'+hid(node['record_id']),'dimension':'economic_activity','canonical_ref':node['record_id'],'label':node['title'],'scheme_ref':node['scheme_edition_id'],'assessment_state':'UNASSESSED_FOR_NOVELTY','held_out_eligible':True,'completion_claim':False})
    for fam,count in sorted(sources['families'].items()):
        b16.append({'record_kind':'b16_coverage_coordinate','coordinate_id':'b16.source_family.'+fam,'dimension':'source_system_family','canonical_ref':'source-family.'+fam,'label':fam,'class_count':count,'assessment_state':'RESEARCHED_CLASS_UNIVERSE_NOVELTY_NOT_PROVEN','held_out_eligible':True,'completion_claim':False})
    practice_families=Counter(p['family_id'] for p in practices)
    for fam,count in sorted(practice_families.items()):
        b16.append({'record_kind':'b16_coverage_coordinate','coordinate_id':'b16.analytics_family.'+fam.replace('.','_'),'dimension':'analytical_question_family','canonical_ref':fam,'label':fam,'practice_count':count,'assessment_state':'RESEARCHED_CANDIDATE_NOVELTY_NOT_PROVEN','held_out_eligible':True,'completion_claim':False})
    occupation_schemes=[s for s in schemes if s.get('scheme_kind') in {'occupation','profession','work_role'}]
    occupation_schemes += [s for s in occupation_ext if s.get('record_kind')=='classification_scheme_extension' and s.get('scheme_kind') in {'occupation','profession','work_role'}]
    occupation_nodes=[r for r in occupation_ext if r.get('record_kind')=='classification_node_extension' and r.get('level')=='major_group']
    if occupation_schemes:
        for node in sorted(occupation_nodes,key=lambda r:r['scheme_code']):
            b16.append({'record_kind':'b16_coverage_coordinate','coordinate_id':'b16.occupation.'+node['scheme_code'],'dimension':'profession_occupation','canonical_ref':node['record_id'],'label':node['title'],'scheme_ref':node['scheme_edition_id'],'assessment_state':'CANONICAL_FOUNDATION_PRESENT_NOVELTY_NOT_PROVEN','held_out_eligible':True,'non_collapse_laws':['occupation != economic_activity','occupation != job_title','occupation != organizational_role','occupation != skill'],'completion_claim':False})
        if not occupation_nodes:
            b16.append({'record_kind':'b16_foundation_gap','coordinate_id':'b16.foundation.occupation_major_groups','dimension':'profession_occupation','assessment_state':'SCHEME_PRESENT_HIERARCHY_NOT_MATERIALIZED','required_resolution':'Materialize at least the ISCO major-group hierarchy before occupation novelty sampling.','completion_claim':False})
    else:
        b16.append({'record_kind':'b16_foundation_gap','coordinate_id':'b16.foundation.occupation_classification','dimension':'profession_occupation','assessment_state':'MISSING_CANONICAL_FOUNDATION','required_resolution':'Add a primary-source occupation/profession classification foundation and explicit crosswalk policy; economic-activity schemes such as ISIC must not substitute for occupations.','completion_claim':False})

    # B17: reuse every deterministic vertical composition as an intent-to-solution challenge.
    b17=[]
    for v in verticals:
        b17.append({'record_kind':'b17_intent_solution_challenge','challenge_id':'b17.'+v['composition_id'].removeprefix('composition.vertical.'),'composition_ref':v['composition_id'],'industry_ref':v['industry_id'],'actors':v.get('actors',[]),'business_intent':v.get('decision_or_action'),'product_refs':v.get('product_refs',[]),'required_library_refs':v.get('required_library_refs',[]),'source_class_or_need_refs':v.get('source_system_refs',v.get('source_system_need_refs',[])),'data_shape_refs':v.get('data_shape_refs',[]),'method_binding_count':len(v.get('method_bindings',[])),'operation_refs':v.get('operation_refs',[]),'current_compile_phase_verdicts':v.get('compile_phase_verdicts',{}),'required_b17_verdicts':['requirement_offer_matching','compatibility_solution','configuration_completeness','authority_policy_propagation','deterministic_reproduction','typed_refusal_or_governed_human_decision'],'status':'STRUCTURAL_SEED_NOT_B17_ACCEPTED','completion_claim':False})

    # B18: matrix every seeded solution against human/effect non-collapse laws and adversarial modes.
    laws=['analytic_result != recommendation','recommendation != human_decision','human_decision != authorization','authorization != executed_business_effect','executed_business_effect != confirmed_outcome','UI_intent != admitted_command','notification != acknowledgement','draft != durable_fact']
    modes=['success','typed_refusal','retry_duplicate','offline_conflict','partial_effect','recall','appeal_or_correction','stale_authorization']
    b18=[]
    for v in verticals:
        for law in laws:
            for mode in modes:
                b18.append({'record_kind':'b18_human_effect_obligation','obligation_id':'b18.'+hid(v['composition_id']+'|'+law+'|'+mode),'composition_ref':v['composition_id'],'non_collapse_law':law,'scenario_mode':mode,'required_evidence':['pre_state','intent_or_result','authority_state','admitted_command_or_refusal','effect_receipt_if_any','confirmed_outcome_or_residual'],'status':'OPEN_UNEXECUTED','completion_claim':False})

    # B19: system-of-systems faults per composition.
    faults=['time_semantics_mismatch','identity_mismatch','transaction_boundary_loss','retry_amplification','stale_authorization','partial_effect','lineage_break','schema_version_skew','cross_product_recovery_order','deletion_recall_propagation','backpressure_budget_propagation']
    b19=[]
    for v in verticals:
        for fault in faults:
            b19.append({'record_kind':'b19_system_fault_obligation','obligation_id':'b19.'+hid(v['composition_id']+'|'+fault),'composition_ref':v['composition_id'],'fault_class':fault,'product_refs':v.get('product_refs',[]),'required_evidence':['injected_fault_identity','affected_product_edges','bounded_retry_or_refusal','lineage_trace','recovery_or_residual_receipt'],'status':'OPEN_UNEXECUTED','completion_claim':False})

    # B20: invalidation matrix across change classes and proof-bearing artifact categories.
    changes=['provider_api_version_change','connector_deprecation','price_or_quota_change','security_advisory','standard_revision','schema_change','taxonomy_change','data_drift','behavior_drift','evidence_expiry','operational_incident','supplier_failure_or_exit','product_or_library_decommission']
    artifacts=['semantic_contract','library_contract','implementation_artifact','provider_offer','source_occurrence','solution_plan','deployment_binding','qualification_or_acceptance_receipt']
    b20=[]
    for change in changes:
        for artifact in artifacts:
            b20.append({'record_kind':'b20_invalidation_obligation','obligation_id':'b20.'+hid(change+'|'+artifact),'change_class':change,'affected_artifact_class':artifact,'required_behavior':['identify_affected_scope','invalidate_stale_verdict_before_reuse','emit_bounded_requalification_migration_exit_or_decommission_work','retain_invalidation_provenance'],'status':'OPEN_UNEXECUTED','completion_claim':False})

    write_jl('b16-coverage-sampling-frame.jsonl',b16)
    write_jl('b17-intent-solution-challenges.jsonl',b17)
    write_jl('b18-human-effect-obligations.jsonl',b18)
    write_jl('b19-system-fault-obligations.jsonl',b19)
    write_jl('b20-invalidation-obligations.jsonl',b20)
    summary={'report_id':'program_level_gate_work_surfaces','as_of':'2026-08-27','completion_claim':False,'b16_coverage_coordinates':len(b16),'b16_missing_profession_foundation':not bool(occupation_schemes),'b16_occupation_major_group_coordinates':len(occupation_nodes),'b17_seeded_solution_challenges':len(b17),'b18_human_effect_obligations':len(b18),'b19_system_fault_obligations':len(b19),'b20_invalidation_obligations':len(b20),'program_gate_acceptance_results':0,'status':'FINITE_WORK_SURFACES_BUILT_ACCEPTANCE_UNEXECUTED'}
    (HERE/'program-work-surfaces-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
