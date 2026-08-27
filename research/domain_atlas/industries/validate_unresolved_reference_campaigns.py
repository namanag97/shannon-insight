#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def jl(name): return [json.loads(x) for x in (HERE/name).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    queue=jl('canonical-reference-review-queue.jsonl'); manual=jl('canonical-reference-adjudications.jsonl'); exact=jl('canonical-reference-auto-alias-candidates.jsonl'); current=jl('canonical-reference-current-method-candidates.jsonl') if (HERE/'canonical-reference-current-method-candidates.jsonl').exists() else []
    assignments=jl('canonical-reference-unresolved-campaign-assignments.jsonl'); campaigns=jl('canonical-reference-unresolved-research-campaigns.jsonl'); summary=json.loads((HERE/'canonical-reference-unresolved-campaign-summary.json').read_text(encoding='utf-8'))
    errors=[]; resolved={r['queue_id'] for r in manual+exact+current}; remaining={q['queue_id'] for q in queue if q['queue_id'] not in resolved}; assigned=[r['queue_id'] for r in assignments]
    if set(assigned)!=remaining or len(assigned)!=len(remaining): errors.append('remaining queue must be assigned exactly once')
    if len(assigned)!=len(set(assigned)): errors.append('duplicate campaign assignment')
    cids={c['campaign_id'] for c in campaigns}
    if any(a['research_campaign_ref'] not in cids for a in assignments): errors.append('assignment references missing campaign')
    represented=[q for c in campaigns for q in c['queue_refs']]
    if set(represented)!=remaining or len(represented)!=len(remaining): errors.append('campaigns do not exactly partition remaining queue')
    if any(a.get('canonical_mapping_inferred') for a in assignments): errors.append('campaign routing inferred canonical mapping')
    if any(c.get('completion_claim') is not False for c in campaigns) or any(a.get('completion_claim') is not False for a in assignments): errors.append('completion overclaim')
    required={'exact_alias','narrower_profile','broader_parent','split_required','new_canonical_concept','no_match_or_external_concept'}
    if any(set(c['required_verdicts'])!=required for c in campaigns): errors.append('campaign verdict vocabulary drift')
    if summary['remaining_reference_count']!=len(remaining) or summary['assigned_reference_count']!=len(assignments) or summary['research_campaign_count']!=len(campaigns): errors.append('summary drift')
    if summary['canonical_mappings_inferred']!=0 or summary.get('completion_claim') is not False: errors.append('summary overclaim')
    if errors:
        for e in errors: print('ERROR:',e)
        return 1
    print(f"PASS B07 unresolved factoring: {len(remaining)} refs -> {len(campaigns)} research campaigns; exact per-ref verdict preserved; 0 mappings inferred")
    return 0
if __name__=='__main__': raise SystemExit(main())
