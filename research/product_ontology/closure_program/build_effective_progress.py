#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent

def J(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def L(p): return [json.loads(x) for x in (ROOT/p).read_text(encoding='utf-8').splitlines() if x.strip()]
def exists(p): return (ROOT/p).exists()
def main():
    master=L('research/product_ontology/closure_program/master-batches.jsonl')
    q=J('research/product_ontology/qualification_program/effective-summary.json')
    b04=J('research/analytics_landscape/product_families/evidence-governance-summary.json')
    b05=J('research/product_ontology/dossier_readiness/product-boundary-falsification-summary.json')
    b06=J('research/product_ontology/qualification_program/contract-scope-summary.json')
    b07=J('research/domain_atlas/industries/canonical-reference-auto-alias-summary.json')
    occ=J('research/domain_atlas/universes/source_systems/occurrence-registry-summary.json')
    dsg=J('research/domain_atlas/universes/data_shapes/effective-gap-summary.json')
    ctx=J('research/domain_atlas/context_map/manifest.json')
    readiness=J('research/product_ontology/dossier_readiness/summary.json')
    statuses={}
    statuses['B00_TRUTH_CONVERGENCE']={'state':'STRUCTURALLY_DONE_MONITOR','remaining':'freshness/digest enforcement for future generated corpora','machine_addressable':True}
    statuses['B01_SOURCE_AUTHORITY']={'state':'AUTHORITY_BLOCKED','remaining':23,'machine_addressable':False}
    statuses['B02_SEMANTIC_OWNER_UNIQUENESS']={'state':'PARTIAL_RESEARCH_AUTHORITY_BLOCKED','remaining':'8 legacy decisions researched; global uniqueness + ratification remain','machine_addressable':True}
    statuses['B03_CONTEXT_MAP_RATIFICATION']={'state':'PARTIAL_RESEARCH_AUTHORITY_BLOCKED','remaining':ctx['counts']['gaps'],'machine_addressable':True}
    statuses['B04_HORIZONTAL_EVIDENCE_GOVERNANCE']={'state':'MACHINE_ACTIVE','remaining':{'weak_memberships':b04['weak_membership_claim_count'],'organization_identity_graphs':b04['unique_organization_count']-b04['identity_relationships_fully_adjudicated_count']},'machine_addressable':True}
    statuses['B05_PRODUCT_BOUNDARY_FALSIFICATION']={'state':'STRUCTURAL_FALSIFICATION_DONE_EXTERNAL_EVIDENCE_OPEN','remaining':{'independent_adoption':b05['retained_product_count']-b05['product_specific_independent_adoption_evidence_complete_count'],'economic_exit':b05['retained_product_count']-b05['product_specific_economic_exit_evidence_complete_count'],'ratification':b05['retained_product_count']-b05['ratified_boundary_count']},'machine_addressable':True}
    statuses['B06_LIBRARY_CONTRACT_AUTHORITY']={'state':'STRUCTURAL_SCOPE_DONE_AUTHORITY_BLOCKED','remaining':{'semantic_scopes':b06['semantic_contract_scope_count'],'ratified':b06['ratified_contract_scope_count']},'machine_addressable':False}
    statuses['B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE']={'state':'MACHINE_ACTIVE','remaining':b07['remaining_without_manual_or_machine_exact_candidate'],'machine_addressable':True}
    statuses['B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE']={'state':'MACHINE_ACTIVE','remaining':{'source_classes_without_retained_occurrence':171-occ['source_class_count_with_retained_occurrence'],'representative_family_breadth_open':True},'machine_addressable':True}
    statuses['B09_DATA_SHAPE_OPERATION_TOTALITY']={'state':'MACHINE_ACTIVE','remaining':{'historical_gaps':dsg['historical_gap_count'],'end_to_end_closed':dsg['end_to_end_closed_gap_count']},'machine_addressable':True}
    for bid in ['B10_IMPLEMENTATION_IDENTITY_AND_BUILD','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT','B13_PHYSICAL_BINDING_SLO_SECURITY_COST','B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','B15_TWO_RELEASE_CHANGE_AND_RATIFICATION']:
        statuses[bid]={'state':'DOWNSTREAM_EVIDENCE_BLOCKED','remaining':'see qualification effective vacancies / provider and vertical acceptance ledgers','machine_addressable':bid in {'B10_IMPLEMENTATION_IDENTITY_AND_BUILD','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL'}}
    rows=[]
    for b in master:
        s=statuses[b['batch_id']]
        rows.append({'batch_id':b['batch_id'],'depends_on':b['depends_on'],'effective_state':s['state'],'remaining':s['remaining'],'machine_addressable_now':s['machine_addressable'],'exit_condition':b['exit_condition'],'completion_claim':False})
    (HERE/'effective-batch-progress.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    summary={'report_id':'effective_batched_closure_progress','as_of':'2026-08-27','batch_count':16,'structurally_done_or_done_monitor_count':sum('DONE' in r['effective_state'] for r in rows),'machine_active_count':sum(r['effective_state']=='MACHINE_ACTIVE' for r in rows),'authority_blocked_count':sum('AUTHORITY_BLOCKED' in r['effective_state'] for r in rows),'downstream_evidence_blocked_count':sum(r['effective_state']=='DOWNSTREAM_EVIDENCE_BLOCKED' for r in rows),'effective_qualification_vacancies':q['effective_evidence_vacancy_count'],'largest_machine_queue':{'batch_id':'B07_INDUSTRY_CANONICAL_REFERENCE_CLOSURE','count':b07['remaining_without_manual_or_machine_exact_candidate']},'retained_source_occurrences':occ['retained_occurrence_count'],'completion_claim':False}
    (HERE/'effective-progress-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
