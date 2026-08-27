#!/usr/bin/env python3
"""Propose exact analytical-practice mappings against the current adjudicated method corpus.

This is a second, stricter B07 candidate layer. It does not rewrite the legacy practice
registry and does not authorize compiler substitution. Only exact normalized equality to a
unique semantic_contract or library_contract name/ID in the current analytical-method
adjudication is allowed.
"""
from __future__ import annotations
import hashlib,json,re,unicodedata
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
METHODS=ROOT/'research/product_ontology/adjudications/analytical_methods'

def load_jsonl(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def norm(s):
    s=unicodedata.normalize('NFKC',str(s)).casefold().strip()
    for prefix in ('method.','semantic.','library.'):
        if s.startswith(prefix): s=s[len(prefix):]; break
    s=s.replace('_',' ').replace('-',' ')
    s=re.sub(r'[^a-z0-9]+',' ',s)
    return ' '.join(s.split())

def main():
    queue=load_jsonl(HERE/'canonical-reference-review-queue.jsonl')
    existing=load_jsonl(HERE/'canonical-reference-auto-alias-candidates.jsonl')
    manual=load_jsonl(HERE/'canonical-reference-adjudications.jsonl')
    resolved={r['queue_id'] for r in existing}|{r['queue_id'] for r in manual}
    artifacts=load_jsonl(METHODS/'artifacts.jsonl')
    index=defaultdict(set); meta={}
    for a in artifacts:
        if a.get('kind') not in {'semantic_contract','library_contract'}: continue
        aid=a['artifact_id']; meta[aid]=a
        for v in [aid,a.get('name','')]:
            f=norm(v)
            if f: index[f].add(aid)
    rows=[]
    for q in queue:
        if q['reference_domain']!='analytical_practice' or q['queue_id'] in resolved: continue
        form=norm(q['raw_ref']); targets=sorted(index.get(form,set()))
        if len(targets)!=1: continue
        target=targets[0]; a=meta[target]
        rows.append({'record_kind':'canonical_reference_current_method_identity_candidate','candidate_id':'currentmethod.'+hashlib.sha256(q['queue_id'].encode()).hexdigest()[:16],'edition':1,'queue_id':q['queue_id'],'reference_domain':'analytical_practice','raw_ref':q['raw_ref'],'normalized_form':form,'candidate_target_ref':target,'candidate_target_kind':a['kind'],'candidate_target_name':a.get('name'),'candidate_semantic_owner_ref':a.get('semantic_owner_ref'),'occurrence_count':q['occurrence_count'],'origin_packs':q['origin_packs'],'relation':'exact_current_adjudicated_method_identity_candidate','status':'PROPOSED_NOT_RATIFIED','completion_claim':False,'decision_basis':['unique equality after NFKC/case/punctuation/namespace normalization','target is a current adjudicated semantic_contract or library_contract, not a product/capability/provider'],'prohibited_inferences':['semantic broadening or narrowing','mapping a lifecycle/workbench/product capability as a method','compiler substitution before authority','treating a library implementation as semantic ratification']})
    rows.sort(key=lambda r:r['queue_id'])
    row_ids={r['queue_id'] for r in rows}
    (HERE/'canonical-reference-current-method-candidates.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    summary={'report_id':'industry_current_method_identity_candidates','as_of':'2026-08-27','completion_claim':False,'candidate_records':len(rows),'candidate_occurrences':sum(r['occurrence_count'] for r in rows),'legacy_or_manual_resolved_excluded':len(resolved),'remaining_analytical_practice_rows_after_all_exact_candidate_layers':sum(1 for q in queue if q['reference_domain']=='analytical_practice' and q['queue_id'] not in resolved and q['queue_id'] not in row_ids),'status':'CANDIDATES_ONLY_AUTHORITY_WITHHELD'}
    (HERE/'canonical-reference-current-method-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
