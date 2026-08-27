#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def jl(name): return [json.loads(x) for x in (HERE/name).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    scopes=jl('semantic-contract-scopes.jsonl'); campaigns=jl('qualification-harness-campaigns.jsonl'); bindings=jl('contract-scope-harness-bindings.jsonl'); summary=json.loads((HERE/'harness-campaign-summary.json').read_text(encoding='utf-8'))
    errors=[]; scope_ids={s['contract_scope_id'] for s in scopes}; binding_ids=[b['contract_scope_ref'] for b in bindings]
    if len(binding_ids)!=len(scope_ids) or set(binding_ids)!=scope_ids: errors.append('every exact semantic contract scope must have exactly one harness binding')
    if len(binding_ids)!=len(set(binding_ids)): errors.append('duplicate scope harness binding')
    campaign_refs={c['harness_archetype_ref'] for c in campaigns}
    if any(b['harness_archetype_ref'] not in campaign_refs for b in bindings): errors.append('binding references unknown harness archetype')
    represented=[]
    for c in campaigns:
        represented.extend(c['contract_scope_refs'])
        if c.get('completion_claim') is not False: errors.append(c['campaign_id']+' completion overclaim')
        if not c.get('mandatory_per_scope_identity') or len(c['mandatory_per_scope_identity'])<10: errors.append(c['campaign_id']+' exact execution identity incomplete')
        if 'verdict may not be reused' not in c.get('reuse_law',''): errors.append(c['campaign_id']+' reuse law weakened')
    if set(represented)!=scope_ids or len(represented)!=len(scope_ids): errors.append('campaign scope partition is not exact')
    if any(b.get('evidence_reuse_authorized') or b.get('semantic_scope_merged') for b in bindings): errors.append('harness factoring must not authorize evidence reuse or merge semantic scopes')
    if summary['semantic_contract_scope_count']!=len(scopes) or summary['assigned_scope_count']!=len(bindings) or summary['harness_campaign_count']!=len(campaigns): errors.append('summary drift')
    if summary['unassigned_scope_count']!=0 or summary['qualification_verdicts_created']!=0 or summary['execution_evidence_reuse_authorized_count']!=0 or summary.get('completion_claim') is not False: errors.append('summary promotion/incompleteness error')
    if errors:
        for e in errors: print('ERROR:',e)
        return 1
    print(f"PASS B10/B11 harness factoring: {len(scopes)} exact scopes -> {len(campaigns)} reusable harness campaigns; exact verdict identity preserved; 0 qualifications/evidence reuse")
    return 0
if __name__=='__main__': raise SystemExit(main())
