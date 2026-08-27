#!/usr/bin/env python3
"""Factor all conservative B07 mapping candidates into semantic-owner review batches.

Combines legacy-registry exact candidates with exact candidates against the current adjudicated
method corpus. It creates no semantic decision and no authority receipt.
"""
from __future__ import annotations
import hashlib,json
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
ATLAS=HERE.parent
ROOT=ATLAS.parents[1]
METHODS=ROOT/'research/product_ontology/adjudications/analytical_methods'

def L(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def main():
    legacy=L(HERE/'canonical-reference-auto-alias-candidates.jsonl')
    current=L(HERE/'canonical-reference-current-method-candidates.jsonl') if (HERE/'canonical-reference-current-method-candidates.jsonl').exists() else []
    practices={r['practice_id']:r for r in L(ATLAS/'universes/analytics_types/candidate-practices.jsonl')}
    operations={r['operation_id']:r for r in L(ATLAS/'universes/operations/operation-candidates.jsonl')}
    sources={r['class_id']:r for r in L(ATLAS/'universes/source_systems/source-classes.jsonl')}
    artifacts={r['artifact_id']:r for r in L(METHODS/'artifacts.jsonl')}
    grouped=defaultdict(list)
    for c in legacy:
        d=c['reference_domain']; target=c['candidate_target_ref']
        if d=='analytical_practice': group='legacy_practice_family:'+practices[target]['family_id']
        elif d=='typed_operation': group='operation_family:'+operations[target]['family_id']
        elif d=='source_system_class': group='source_family:'+sources[target]['family_id']
        elif d=='industry_classification': group='industry_classification'
        else: raise ValueError(d)
        grouped[(d,group)].append(c|{'candidate_layer':'legacy_exact_alias'})
    for c in current:
        target=c['candidate_target_ref']; a=artifacts[target]
        group='current_method_owner:'+(a.get('semantic_owner_ref') or 'UNOWNED')
        grouped[('analytical_practice',group)].append(c|{'candidate_layer':'current_method_identity'})
    batches=[]
    for (domain,group),members in sorted(grouped.items()):
        identity=domain+':'+group
        batches.append({'record_kind':'canonical_reference_semantic_review_batch','batch_id':'refbatch.'+hashlib.sha256(identity.encode()).hexdigest()[:16],'edition':2,'reference_domain':domain,'semantic_review_group_ref':group,'candidate_refs':sorted(m['candidate_id'] for m in members),'queue_refs':sorted(m['queue_id'] for m in members),'target_refs':sorted({m['candidate_target_ref'] for m in members}),'candidate_layers':sorted({m['candidate_layer'] for m in members}),'candidate_count':len(members),'occurrence_count':sum(m['occurrence_count'] for m in members),'origin_packs':sorted({p for m in members for p in m['origin_packs']}),'review_protocol':['compare each occurrence intent, input/output, grain, state, time, authority, assumptions and refusals to proposed target','accept exact_alias only if normalization removed representation noise and no semantic qualifier','otherwise record narrower_profile, broader_parent, split_required or no_match','semantic owner ratification remains separate from this machine grouping','compiler substitution remains prohibited until ratification'],'status':'OPEN_MACHINE_FACTORED_SEMANTIC_REVIEW','completion_claim':False})
    (HERE/'canonical-reference-semantic-review-batches.jsonl').write_text(''.join(canon(r)+'\n' for r in batches),encoding='utf-8')
    summary={'report_id':'industry_canonical_reference_semantic_review_batches','as_of':'2026-08-27','legacy_exact_candidates':len(legacy),'current_method_candidates':len(current),'represented_candidate_records':sum(b['candidate_count'] for b in batches),'represented_candidate_occurrences':sum(b['occurrence_count'] for b in batches),'review_batch_count':len(batches),'semantic_decisions_created':0,'authority_receipts_created':0,'completion_claim':False,'status':'MACHINE_FACTORED_REVIEW_FRONTIER_NOT_SEMANTIC_CLOSURE'}
    (HERE/'canonical-reference-semantic-review-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
