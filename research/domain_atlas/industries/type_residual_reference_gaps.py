#!/usr/bin/env python3
"""Convert every still-unclassified B07 reference into a typed, evidence-demanding extension gap.

This is the lawful terminal state for references that cannot yet be mapped without semantic
invention. It does not claim the gap is solved; it makes the unresolved obligation exact and
owned so the B07 frontier has no anonymous strings.
"""
from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
from build_unresolved_frontier_profile import campaign_for
HERE=Path(__file__).resolve().parent

def L(p):
 p=Path(p)
 if not p.exists(): return []
 return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
REQUIREMENTS={
 'analytical_practice':{
   'question':'Which exact analytical method, estimand/model family, assumptions, inputs, outputs, uncertainty relation and refusal laws does this vertical phrase denote?',
   'allowed_relations':['exact_alias','narrower_profile','broader_parent','split_required','no_match_new_method_extension'],
   'evidence_needed':['primary methodological/standards evidence where available','foundational or peer-reviewed method evidence','at least one independent implementation/adoption source when implementation behavior matters','vertical source evidence for domain-specific qualifiers'],
   'owning_campaign':'analytical_method_semantic_research'},
 'typed_operation':{
   'question':'Is this an atomic typed operation, a composition of existing operations, a method invocation, or a domain/workflow/decision concern that must be rehomed?',
   'allowed_relations':['exact_alias','narrower_profile','split_required_composition','rehome_to_method_or_domain','no_match_new_operation_extension'],
   'evidence_needed':['committed operation contracts and sovereign-owner map','primary algorithm/standard evidence for operation law','independent implementation evidence for failure/resource behavior','vertical evidence for qualifiers'],
   'owning_campaign':'typed_operation_semantic_research'},
 'source_system_class':{
   'question':'Does this phrase denote a provider-neutral source capability class, a provider/product offer, an access surface, a connector, or a concrete occurrence?',
   'allowed_relations':['exact_source_class','narrower_source_profile','split_multiple_source_classes','rehome_provider_offer_or_occurrence','no_match_new_source_class_extension'],
   'evidence_needed':['official source/provider technical documentation','source-class contract evidence','access/change/schema/time/order/security/limit semantics','representative occurrence or connector evidence when behavior is asserted'],
   'owning_campaign':'source_class_semantic_research'},
 'industry_classification':{
   'question':'Which registered classification/overlay identity and cross-scheme relation defines this vertical coordinate?',
   'allowed_relations':['canonical_local_overlay','equivalent_extent','subset','superset','overlap','composite','unresolved_mapping'],
   'evidence_needed':['classification authority evidence','exact scheme edition and statistical unit','extent/crosswalk evidence and losses','domain/classification review'],
   'owning_campaign':'industry_classification_crosswalk_research'},
}

def main():
 queue=L(HERE/'canonical-reference-review-queue.jsonl'); ledger=L(HERE/'canonical-reference-adjudications.jsonl'); auto=L(HERE/'canonical-reference-auto-alias-candidates.jsonl'); current=L(HERE/'canonical-reference-current-method-candidates.jsonl')
 accounted={r['queue_id'] for r in ledger+auto+current}; existing={r['queue_id']:r for r in ledger}
 residual=[r for r in queue if r['queue_id'] not in accounted]
 gaps=[]; by_domain=Counter(); occ=Counter(); by_campaign=Counter(); campaign_occ=Counter()
 for q in residual:
  domain=q['reference_domain']; spec=REQUIREMENTS[domain]; campaign=campaign_for(q); gid=f"gap.b07.residual.{domain}.{hashlib.sha256(q['queue_id'].encode()).hexdigest()[:16]}"
  gap={'gap_id':gid,'record_kind':'canonical_reference_residual_extension_gap','edition':1,'reference_domain':domain,'queue_id':q['queue_id'],'raw_ref':q['raw_ref'],'occurrence_count':q['occurrence_count'],'origin_packs':q.get('origin_packs',[]),'example_origin_records':q.get('example_origin_records',[]),'research_campaign':campaign,'semantic_question':spec['question'],'allowed_dispositions':spec['allowed_relations'],'evidence_needed':spec['evidence_needed'],'campaign_owner':spec['owning_campaign'],'status':'OPEN_TYPED_EXTENSION_GAP','remaining_gate':'semantic research decision plus accountable canonical-owner/classification review; compiler substitution prohibited until then','completion_claim':False}
  gaps.append(gap); by_domain[domain]+=1; occ[domain]+=q['occurrence_count']; by_campaign[campaign]+=1; campaign_occ[campaign]+=q['occurrence_count']
  existing[q['queue_id']]={'queue_id':q['queue_id'],'record_kind':'canonical_reference_adjudication','edition':1,'reference_domain':domain,'raw_ref':q['raw_ref'],'relation':'typed_extension_gap','candidate_target_refs':[],'extension_gap_refs':[gid],'decision_basis':[{'claim':'No semantics are invented: the unresolved reference is preserved as an exact typed extension obligation with a bounded research question, evidence contract and owner.','source_ref':'research/domain_atlas/industries/canonical-reference-review-queue.jsonl'}],'remaining_gate':gap['remaining_gate'],'status':'typed_extension_gap_open','completion_claim':False,'research_tranche':'b07.residual_gap_typing.2026_08_27'}
 (HERE/'canonical-reference-residual-extension-gaps.jsonl').write_text(''.join(canon(r)+'\n' for r in sorted(gaps,key=lambda r:r['gap_id'])),encoding='utf-8')
 (HERE/'canonical-reference-adjudications.jsonl').write_text(''.join(canon(r)+'\n' for r in sorted(existing.values(),key=lambda r:r['queue_id'])),encoding='utf-8')
 campaigns=[]
 for cid,n in sorted(by_campaign.items(),key=lambda kv:(-campaign_occ[kv[0]],-kv[1],kv[0])):
  campaigns.append({'campaign_id':cid,'record_kind':'b07_residual_research_campaign','gap_count':n,'occurrence_count':campaign_occ[cid],'status':'OPEN_RESEARCH_CAMPAIGN','completion_claim':False})
 (HERE/'canonical-reference-residual-campaigns.jsonl').write_text(''.join(canon(r)+'\n' for r in campaigns),encoding='utf-8')
 summary={'report_id':'b07_residual_reference_gap_typing','as_of':'2026-08-27','raw_queue_records':len(queue),'prior_accounted_records':len(accounted),'typed_residual_gap_count':len(residual),'typed_residual_occurrences':sum(r['occurrence_count'] for r in residual),'residual_gaps_by_domain':dict(sorted(by_domain.items())),'residual_occurrences_by_domain':dict(sorted(occ.items())),'research_campaign_count':len(campaigns),'unclassified_reference_count_after_typing':0,'semantic_ratifications_created':0,'completion_claim':False,'status':'ALL_B07_REFERENCE_ROWS_HAVE_EXPLICIT_DISPOSITION_OR_TYPED_GAP'}
 (HERE/'canonical-reference-residual-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
