#!/usr/bin/env python3
"""Route context-map gaps to their actual closure campaigns without deleting history."""
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROUTES={
'001':('semantic_owner_uniqueness','B02_SEMANTIC_OWNER_UNIQUENESS','authority'),
'002':('shared_kernel_governance','B02_SEMANTIC_OWNER_UNIQUENESS','authority'),
'003':('published_language_compatibility','B12_SECOND_IMPLEMENTATION_PORTABILITY_EXIT','independent_execution'),
'004':('production_residual_totality','B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','production_evidence'),
'005':('identity_map_authority','B02_SEMANTIC_OWNER_UNIQUENESS','authority_and_vertical'),
'006':('bitemporal_translation_laws','B09_DATA_SHAPE_OPERATION_TOTALITY','semantic_and_model_checking'),
'007':('grain_change_algebra','B09_DATA_SHAPE_OPERATION_TOTALITY','semantic_and_conformance'),
'008':('loss_policy_thresholds','B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','domain_authority'),
'009':('foreign_enum_occurrence_monitoring','B08_SOURCE_SYSTEM_AND_OCCURRENCE_CLOSURE','occurrence_evidence'),
'010':('schema_semantic_registry_refusal_precedence','B06_LIBRARY_CONTRACT_AUTHORITY','semantic_authority'),
'011':('cross_region_data_use_translation','B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','jurisdiction_authority'),
'012':('revocation_propagation_latency','B13_PHYSICAL_BINDING_SLO_SECURITY_COST','physical_measurement'),
'013':('source_vs_analytical_finality','B09_DATA_SHAPE_OPERATION_TOTALITY','semantic'),
'014':('historical_mapping_backfill','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','execution'),
'015':('stream_batch_equivalence','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','operator_specific_execution'),
'016':('provider_offer_invalidation','B10_IMPLEMENTATION_IDENTITY_AND_BUILD','provider_freshness'),
'017':('catalog_alias_edition_selection','B06_LIBRARY_CONTRACT_AUTHORITY','semantic_authority'),
'018':('cross_provider_runtime_receipt_profile','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','assurance_profile'),
'019':('independent_appraisal_authority','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','independent_authority'),
'020':('partial_translation_residual_carriers','B09_DATA_SHAPE_OPERATION_TOTALITY','semantic'),
'021':('cyclic_delegation_resolution','B02_SEMANTIC_OWNER_UNIQUENESS','policy_authority'),
'022':('packaging_blast_radius_migration','B15_TWO_RELEASE_CHANGE_AND_RATIFICATION','migration_evidence'),
'023':('clinical_vocab_licensing_editions','B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','vertical_and_legal_authority'),
'024':('legal_entity_agreement_mapping','B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','jurisdiction_authority'),
'025':('industrial_asset_identity_continuity','B14_TWO_VERTICAL_EXECUTED_ACCEPTANCE','vertical_execution'),
'026':('independent_acl_implementations','B11_EXACT_SCOPE_CONFORMANCE_AND_INDEPENDENT_APPRAISAL','independent_execution'),
'027':('http_availability_occurrence_checks','B13_PHYSICAL_BINDING_SLO_SECURITY_COST','physical_measurement'),
'028':('open_world_saturation','B15_TWO_RELEASE_CHANGE_AND_RATIFICATION','independent_review'),
}
def load(): return [json.loads(x) for x in (HERE/'gaps.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    gaps=load(); rows=[]
    for g in gaps:
        suffix=g['gap_id'].rsplit('.',1)[-1]
        campaign,batch,evidence_class=ROUTES[suffix]
        rows.append({'record_kind':'effective_context_map_gap_routing','gap_id':g['gap_id'],'historical_description':g['description'],'blocking_scope':g['blocking_scope'],'campaign':campaign,'owning_batch':batch,'required_evidence_class':evidence_class,'effective_status':'ROUTED_STILL_OPEN','historical_evidence_needed':g['evidence_needed'],'completion_claim':False})
    (HERE/'effective-gap-routing.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    counts={}
    for r in rows:
        counts[r['owning_batch']]=counts.get(r['owning_batch'],0)+1
    summary={'report_id':'context_map_effective_gap_routing','as_of':'2026-08-27','gap_count':len(rows),'routed_gap_count':len(rows),'unrouted_gap_count':0,'end_to_end_closed_count':0,'counts_by_owning_batch':dict(sorted(counts.items())),'completion_claim':False,'status':'ALL_GAPS_ROUTED_NONE_FALSIFIED_CLOSED'}
    (HERE/'effective-gap-routing-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
