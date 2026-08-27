#!/usr/bin/env python3
"""Factor exact semantic contract scopes into reusable B10/B11 harness archetypes.

Campaign membership never merges semantic scopes and never authorizes evidence reuse. It only
selects a reusable execution-harness shape. Exact contract, implementation, configuration,
target, oracle, corpus, authority and validity identities remain per-scope proof dimensions.
"""
from __future__ import annotations
import hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def hid(s): return hashlib.sha256(s.encode()).hexdigest()[:16]

def archetype(scope):
    p=scope['semantic_payload']; ref=p['abstract_library_ref'].lower(); ctx=set(p.get('required_conformance_context_refs',[])); effect=p.get('effect_boundary')
    text=' '.join([ref,str(p.get('library_class','')).lower(),str(effect).lower()])
    # Specialized harnesses first. These are test-shape classifications, not semantic identities.
    if 'context.ce.process_mining' in ctx or 'process' in text: return 'process_analytics'
    if 'context.ce.geospatial' in ctx or any(k in text for k in ['geospatial','spatial','coordinate','raster','trajectory','point_cloud']): return 'geospatial_compute'
    if 'context.ce.graph' in ctx or re.search(r'(^|[._])graph([._]|$)',ref): return 'graph_compute'
    if 'context.ce.document' in ctx or any(k in text for k in ['document','ocr','pdf','form_extraction']): return 'document_content'
    if 'context.ce.optimization' in ctx or any(k in text for k in ['optim','solver','constraint','allocation','scheduling']): return 'solver_optimization'
    if {'context.ce.predictive_validation','context.ce.calibration','context.ce.statistical_power'} & ctx or any(k in text for k in ['forecast','predict','statistic','causal','experiment','anomaly','model_']): return 'statistical_model_method'
    if 'context.ce.streaming' in ctx or any(k in text for k in ['stream','cdc','checkpoint','event_log','watermark','change_envelope']): return 'stream_change_dataflow'
    if any(k in text for k in ['query','relational','sql','scan','index','search','olap']): return 'query_index_compute'
    if any(k in text for k in ['catalog','registry','metadata','schema_registry','semantic_registry']): return 'registry_catalog'
    if any(k in text for k in ['storage','persistence','snapshot','commit','table','partition','restore','backup']): return 'storage_persistence'
    if 'context.ce.privacy' in ctx or 'context.ce.threat_abuse' in ctx or any(k in text for k in ['policy','privacy','security','access_control','entitlement','authorization']): return 'policy_security_governance'
    if any(k in text for k in ['presentation','visual','report','dashboard','render','layout','accessib','notification','embed']): return 'presentation_human_experience'
    if any(k in text for k in ['workflow','case_','approval','decision','human','task','work_item']): return 'human_work_state_machine'
    if effect=='pure_no_io': return 'pure_deterministic_semantic'
    if {'context.ce.crash_recovery','context.ce.restore','context.ce.migration'} & ctx: return 'stateful_runtime_recovery'
    return 'generic_effect_bounded_stateful'

REQUIRED_BASE={'context.ce.structural_schema','context.ce.static_type','context.ce.api_surface','context.ce.domain_invariant'}

def main():
    scopes=load_jsonl(HERE/'semantic-contract-scopes.jsonl')
    campaigns=defaultdict(list)
    bindings=[]
    for s in scopes:
        a=archetype(s); campaigns[a].append(s)
        bindings.append({'record_kind':'contract_scope_harness_binding','binding_id':'harnessbinding.'+hid(s['contract_scope_id']+'|'+a),'contract_scope_ref':s['contract_scope_id'],'abstract_library_ref':s['abstract_library_ref'],'harness_archetype_ref':'harness.'+a,'required_conformance_context_refs':s['semantic_payload'].get('required_conformance_context_refs',[]),'effect_boundary':s['semantic_payload'].get('effect_boundary'),'evidence_reuse_authorized':False,'semantic_scope_merged':False,'status':'HARNESS_SHAPE_ASSIGNED_EXACT_VERDICT_STILL_REQUIRED','completion_claim':False})
    rows=[]
    for a,members in sorted(campaigns.items()):
        contexts=Counter(c for s in members for c in s['semantic_payload'].get('required_conformance_context_refs',[]))
        effect_counts=Counter(str(s['semantic_payload'].get('effect_boundary')) for s in members)
        rows.append({'record_kind':'qualification_harness_campaign','campaign_id':'campaign.b10_b11.'+a,'harness_archetype_ref':'harness.'+a,'contract_scope_refs':sorted(s['contract_scope_id'] for s in members),'scope_count':len(members),'effect_boundary_counts':dict(sorted(effect_counts.items())),'conformance_context_union':sorted(contexts),'mandatory_per_scope_identity':['contract_scope_id','implementation_artifact_digest','source_provenance_digest','dependency_lock_digest','toolchain_target_digest','configuration_digest','target_occurrence_id','oracle_edition_digest','population_or_corpus_digest','authority_scope_digest','validity_interval'],'required_campaign_mechanics':['provider_adapter_or_pure_function_adapter','deterministic_fixture_loader','positive_negative_boundary_and_adversarial_oracles','counterexample_retention','resource_and_failure_observation_when_effectful','digest_bound_execution_receipt','independence_metadata'],'reuse_law':'Harness code and fixture infrastructure may be reused across campaign members; a conformance or qualification verdict may not be reused unless the exact per-scope proof identity dimensions also match.','status':'OPEN_EXECUTION_CAMPAIGN','completion_claim':False})
    bindings.sort(key=lambda r:r['contract_scope_ref'])
    (HERE/'qualification-harness-campaigns.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    (HERE/'contract-scope-harness-bindings.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in bindings),encoding='utf-8')
    counts={r['harness_archetype_ref']:r['scope_count'] for r in rows}
    summary={'report_id':'b10_b11_harness_campaign_factoring','as_of':'2026-08-27','semantic_contract_scope_count':len(scopes),'harness_campaign_count':len(rows),'assigned_scope_count':len(bindings),'unassigned_scope_count':len(scopes)-len(bindings),'campaign_scope_counts':dict(sorted(counts.items())),'qualification_verdicts_created':0,'execution_evidence_reuse_authorized_count':0,'completion_claim':False,'status':'ALL_EXACT_SCOPES_FACTORED_INTO_REUSABLE_HARNESS_SHAPES_VERDICTS_OPEN'}
    (HERE/'harness-campaign-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
