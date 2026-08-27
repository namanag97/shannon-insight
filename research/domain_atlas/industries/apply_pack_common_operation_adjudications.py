#!/usr/bin/env python3
"""Merge the high-reuse pack-common typed-operation research tranche into the canonical B07 ledger.

Every row either resolves to existing operation/context/method identities or to an explicit typed
extension gap. Nothing is deleted by rehoming. This script is deterministic and idempotent.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ATLAS=HERE.parent
ROOT=ATLAS.parents[1]
METHODS=ROOT/'research/product_ontology/adjudications/analytical_methods'

# queue_id -> compact normative disposition
# fields: relation, ops, contexts, methods, gaps, evidence, law, gate, replacement_domain
D={
# built / food / environment: 1,305 occurrences
'refq.typed_operation.2bef0ee2d64aa082':('rehome_to_domain_semantic_extension',[],[],[],['gap.b07.risk_management.lifecycle'],['evidence.b07.iso31000.risk_management'],['risk identification != risk analysis or treatment'],'risk semantic-owner/vertical-specialization adjudication','domain_semantics'),
'refq.typed_operation.fbef59af4f82f3c8':('rehome_to_domain_semantic_extension',[],[],[],['gap.b07.risk_management.lifecycle'],['evidence.b07.iso31000.risk_management','evidence.b07.nist80030.risk_assessment'],['risk quantification/analysis != risk identification','risk measure != treatment decision'],'risk semantic-owner/vertical-specialization adjudication','domain_semantics'),
'refq.typed_operation.41a8c932684a2c8b':('rehome_to_study_method_extension',[],['ctx.study.study_design','ctx.study.result_evaluation'],[],['gap.b07.method.stress_testing_profile'],['evidence.b07.bcbs.stress_testing'],['stress testing != generic simulation','stress result != risk treatment decision'],'stress-testing method/profile authority','analytical_practice'),
'refq.typed_operation.760d069a146a84d6':('rehome_to_analytical_method',[],['ctx.study.estimator_method'],['semantic.anomaly_change','library.anomaly_change_core'],[],[],['change-point detection is a method family, not a generic data transform'],'analytical-method authority and exact change-point profile selection','analytical_practice'),
'refq.typed_operation.7ab64ed0620b1cb3':('no_match_underspecified_rehome',[],['ctx.study.estimator_method'],[],['gap.b07.method.generic_decomposition'],[],['unqualified decomposition does not identify an algebra or subject'],'per-occurrence exact decomposition method selection','analytical_practice'),
'refq.typed_operation.185204e072834735':('no_match_underspecified_rehome',[],['ctx.study.estimator_method'],[],['gap.b07.method.generic_segmentation'],[],['segmentation family must be explicit'],'per-occurrence exact segmentation/cohort/partition method selection','analytical_practice'),
'refq.typed_operation.dc3cf25d3bc95e06':('rehome_to_intent_context',[],['ctx.intent.objective_constraint'],[],[],[],['constraint meaning belongs to decision/intent authority before solver representation'],'enterprise-intent owner ratification and later solver lowering','intent_semantics'),
'refq.typed_operation.7ace327b3c51657c':('rehome_to_result_evaluation',[],['ctx.study.result_evaluation'],[],['gap.b07.method.robustness_profile'],[],['robustness protocol != generic check','robustness evidence != decision authority'],'exact robustness protocol selection and result-evaluation authority','analytical_practice'),
'refq.typed_operation.895d37ecf11b3b53':('rehome_to_study_method_extension',[],['ctx.study.estimator_method'],[],['gap.b07.method.model_fit'],[],['fit requires an exact estimator/model/objective'],'exact estimator/method contract','analytical_practice'),
'refq.typed_operation.02739e8677676c7c':('rehome_to_analytical_method',[],['ctx.study.estimator_method'],['semantic.time_series','library.analytics_forecasting.forecast_estimators'],[],[],['forecast method != generic prediction operation','origin/horizon/information set remain method semantics'],'forecast-method authority and exact estimator profile','analytical_practice'),
'refq.typed_operation.879381dda213dc8b':('rehome_to_result_evaluation',[],['ctx.study.result_evaluation'],[],['gap.b07.method.scenario_comparison'],[],['scenario generation != scenario comparison','comparison != authorized choice'],'scenario-comparison method and study authority','analytical_practice'),
'refq.typed_operation.962895ad6907ac7d':('rehome_to_study_method_extension',[],['ctx.study.case_design','ctx.study.estimator_method'],[],['gap.b07.method.bottleneck_localization'],[],['bottleneck subject/model must be explicit','localization != causal attribution'],'exact bottleneck-diagnosis method family','analytical_practice'),
'refq.typed_operation.48c47bf6b6def1a4':('rehome_to_method_family',[],['ctx.study.estimator_method'],['semantic.process_mining','library.analytics_process.process_discovery_methods','library.analytics_process.process_conformance_methods','library.analytics_process.process_performance_methods'],[],['evidence.b07.processmining.methods'],['process mining contains distinct discovery/conformance/performance methods'],'exact process-mining method selection','analytical_practice'),
'refq.typed_operation.9ef716cb84a2161e':('rehome_to_method_family',[],['ctx.study.estimator_method'],['semantic.geospatial_analysis','library.analytics_geospatial.spatial_statistics_methods'],[],[],['geostatistics is a spatial statistical method family, not one atomic transform'],'exact geostatistical estimator/method profile','analytical_practice'),
'refq.typed_operation.644ee2f0b725e64b':('rehome_to_method_family',[],['ctx.study.estimator_method'],['semantic.geospatial_analysis','library.analytics_geospatial.raster_grid_methods','library.analytics_geospatial.spatial_statistics_methods'],[],[],['zonal statistics composes spatial support/raster semantics with a selected statistic'],'exact zonal statistic, zone semantics and raster/support profile','analytical_practice'),
# energy / resources: 1,047 occurrences
'refq.typed_operation.43ec39339ccb37f8':('split_required_study_composition',['operation.reconciliation.compare_source_and_target'],['ctx.study.result_evaluation'],[],[],[],['expected-vs-observed comparison requires both population reconciliation and result-evaluation semantics'],'result-evaluation authority and exact expected/observed relation','study_composition'),
'refq.typed_operation.c39c65191c0e5512':('rehome_to_study_method_extension',[],['ctx.study.result_evaluation','ctx.study.decision_handoff'],[],['gap.b07.method.explanation_ranking'],[],['explanation ranking != causal proof','ranking != adjudication'],'exact explanation/diagnostic ranking method and decision handoff','analytical_practice'),
'refq.typed_operation.95396327f8340057':('rehome_to_study_method_extension',[],['ctx.study.estimator_method'],[],['gap.b07.method.state_reconstruction'],[],['reconstructed state != observed state'],'exact state/observation model and reconstruction method','analytical_practice'),
'refq.typed_operation.ef860c2ca03211f0':('rehome_to_study_method_extension',[],['ctx.study.estimator_method','ctx.study.result_evaluation'],[],['gap.b07.method.model_calibration'],[],['calibration != validation','calibrated parameters != observed truth'],'exact calibration protocol and evaluation authority','analytical_practice'),
'refq.typed_operation.89d6d97ab6483826':('rehome_to_method_family',[],['ctx.study.study_design'],['semantic.simulation_model','library.analytics_simulation.simulation_execution'],[],[],['scenario execution is a simulation/study method family, not generic mutation'],'scenario/simulation model authority and execution profile','analytical_practice'),
'refq.typed_operation.68a78b5cf63fe9b9':('rehome_to_result_evaluation',[],['ctx.study.result_evaluation'],[],['gap.b07.method.sensitivity_uncertainty_profile'],['evidence.b07.bipm.jcgm100_uncertainty'],['sensitivity != uncertainty quantification','uncertainty evidence != robustness verdict'],'exact sensitivity/uncertainty profiles and evaluation authority','analytical_practice'),
'refq.typed_operation.165bab308abccf2a':('rehome_to_domain_semantic_extension',[],[],[],['gap.b07.risk_management.lifecycle'],['evidence.b07.iso31000.risk_management'],['hazard identification != quantified risk','hazard meaning is vertical/safety-context dependent'],'risk/hazard semantic-owner and vertical specialization adjudication','domain_semantics'),
'refq.typed_operation.93186618d4a70b6f':('rehome_to_domain_semantic_extension',[],[],[],['gap.b07.risk_management.lifecycle'],['evidence.b07.iso31000.risk_management','evidence.b07.nist80030.risk_assessment'],['likelihood/consequence model != risk treatment decision'],'risk model/scale and vertical semantic authority','domain_semantics'),
'refq.typed_operation.64c55906a286f874':('rehome_to_domain_semantic_extension',[],['ctx.intent.objective_constraint'],[],['gap.b07.risk_management.lifecycle'],['evidence.b07.iso31000.risk_management'],['risk-reduction ranking != treatment authorization','risk criteria/objectives must be explicit'],'risk-treatment semantics plus decision-intent authority','domain_semantics'),
'refq.typed_operation.714819668d1930c5':('rehome_to_intent_context',[],['ctx.intent.objective_constraint'],[],[],[],['objective/constraint meaning precedes optimization representation'],'enterprise-intent authority and solver lowering','intent_semantics'),
'refq.typed_operation.fb44f6fce5368ef3':('split_required_optimization_composition',['operation.optimization_simulation.solve_exact_model','operation.optimization_simulation.detect_infeasible_model'],['ctx.study.estimator_method'],[],[],[],['solve result != infeasibility proof','solver/configuration must be bound'],'optimization-method authority, exact solver profile and proof/certificate policy','optimization_method'),
'refq.typed_operation.1333e21ad7059378':('split_required_cross_boundary_composition',['operation.optimization_simulation.verify_solution_feasibility'],['ctx.intent.objective_constraint','ctx.study.decision_handoff'],[],[],[],['hard-constraint semantics != solver feasibility check','feasible proposal != authorized decision'],'intent constraint authority, feasibility evidence and decision-handoff authority','study_composition'),
# finance / insurance: 226 occurrences
'refq.typed_operation.bad02a219e0e23cc':('no_match_underspecified_rehome',[],['ctx.study.case_design','ctx.study.estimator_method','ctx.study.result_evaluation'],[],['gap.b07.method.generic_compare_decompose_rank'],[],['slice/decompose/compare omits object, algebra and comparison relation'],'per-occurrence exact analytical method decomposition','analytical_practice'),
'refq.typed_operation.def91567b39d64aa':('rehome_to_method_family',[],['ctx.study.study_design'],['semantic.simulation_model','library.analytics_simulation.simulation_execution'],[],[],['path/event simulation is a simulation-method family; event semantics remain vertical'],'exact stochastic/event simulation profile and finance-domain event semantics','analytical_practice'),
# health / life sciences: 201 occurrences
'refq.typed_operation.22900521cbff2e65':('no_match_underspecified_rehome',[],['ctx.study.case_design','ctx.study.result_evaluation'],[],['gap.b07.method.generic_compare_decompose_rank'],[],['unqualified compare does not identify estimand or comparison relation'],'exact health-study comparison method/estimand','analytical_practice'),
'refq.typed_operation.4e7afc27d66ae29f':('no_match_underspecified_rehome',[],['ctx.study.estimator_method'],[],['gap.b07.method.generic_compare_decompose_rank'],[],['unqualified decompose does not identify decomposition algebra'],'exact health analytical decomposition method','analytical_practice'),
'refq.typed_operation.66050733058b67b7':('no_match_underspecified_rehome',[],['ctx.study.result_evaluation'],[],['gap.b07.method.generic_compare_decompose_rank'],[],['contributor ranking does not imply causal attribution'],'exact contribution/attribution relation and ranking method','analytical_practice'),
}


def L(p:Path): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    queue={r['queue_id']:r for r in L(HERE/'canonical-reference-review-queue.jsonl')}
    ledger=L(HERE/'canonical-reference-adjudications.jsonl')
    existing={r['queue_id']:r for r in ledger}
    gaps={r['gap_id'] for r in L(HERE/'canonical-reference-extension-gaps.jsonl')}
    evidence={r['evidence_id'] for r in L(HERE/'canonical-reference-research-evidence.jsonl')}
    ops={r['operation_id'] for r in L(ATLAS/'universes/operations/operation-candidates.jsonl')}
    contexts={r['context_id'] for r in L(ATLAS/'context_map/contexts.jsonl')}
    method_artifacts={r['artifact_id'] for r in L(METHODS/'artifacts.jsonl')}
    method_libraries={r['library_id'] for r in L(METHODS/'library-contracts.jsonl')}
    errors=[]; impact=0
    for qid,spec in D.items():
        if qid not in queue: errors.append(f'{qid}: missing queue row'); continue
        q=queue[qid]
        if q['reference_domain']!='typed_operation': errors.append(f'{qid}: expected typed_operation')
        relation,oprefs,ctxrefs,mrefs,gaprefs,evrefs,laws,gate,replacement_domain=spec
        impact += q['occurrence_count']
        for r in oprefs:
            if r not in ops: errors.append(f'{qid}: unknown operation {r}')
        for r in ctxrefs:
            if r not in contexts: errors.append(f'{qid}: unknown context {r}')
        for r in mrefs:
            if r not in method_artifacts and r not in method_libraries: errors.append(f'{qid}: unknown method ref {r}')
        for r in gaprefs:
            if r not in gaps: errors.append(f'{qid}: unknown extension gap {r}')
        for r in evrefs:
            if r not in evidence: errors.append(f'{qid}: unknown research evidence {r}')
        existing[qid]={
            'queue_id':qid,'record_kind':'canonical_reference_adjudication','edition':1,
            'reference_domain':'typed_operation','raw_ref':q['raw_ref'],'relation':relation,
            'candidate_target_refs':sorted(oprefs+ctxrefs+mrefs),
            'target_operation_refs':oprefs,'target_context_refs':ctxrefs,'target_method_refs':mrefs,
            'extension_gap_refs':gaprefs,'replacement_reference_domain':replacement_domain,
            'decision_basis':[{'claim':'Pack-common operation research found the vertical label belongs at the recorded operation/context/method/gap boundaries; reuse frequency is evidence of batching leverage, not semantic identity.','evidence_ref':r} for r in evrefs] or [{'claim':'Disposition is grounded in the committed bounded-context/operation/method contracts and preserves an explicit extension gap when the phrase is underspecified.','source_ref':'research/domain_atlas/context_map/contexts.jsonl'}],
            'non_collapse_laws':laws,'remaining_gate':gate,
            'status':'research_resolved_candidate_not_ratified','completion_claim':False,
            'research_tranche':'b07.pack_common_operations.2026_08_27'
        }
    if len(D)!=32: errors.append(f'expected 32 decisions, got {len(D)}')
    if impact!=2779: errors.append(f'expected 2779 occurrence impact, got {impact}')
    if errors:
        for e in errors: print('ERROR: '+e)
        return 1
    rows=sorted(existing.values(),key=lambda r:r['queue_id'])
    (HERE/'canonical-reference-adjudications.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    summary={'report_id':'b07_pack_common_operation_adjudication_tranche','as_of':'2026-08-27','decision_count':len(D),'occurrence_impact':impact,'canonical_ledger_row_count':len(rows),'semantic_ratifications_created':0,'completion_claim':False,'status':'RESEARCH_DISPOSITIONS_MERGED_AUTHORITY_WITHHELD'}
    (HERE/'pack-common-operation-adjudication-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
