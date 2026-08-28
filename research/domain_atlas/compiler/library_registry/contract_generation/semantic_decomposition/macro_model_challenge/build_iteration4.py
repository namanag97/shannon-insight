#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from build_macro_challenge import searchable_text
from iteration4_model import ITERATION3_AXIS_DELTA_BLOB_SHA, ITERATION3_SUMMARY_BLOB_SHA, ITERATION4_AXES, ITERATION4_CHALLENGES, ITERATION4_CORRECTIONS, ITERATION4_DEEP_CLAIMS, ITERATION4_INTERACTIONS, ITERATION4_PRIMARY_SOURCES
HERE=Path(__file__).resolve().parent; SEM=HERE.parent; GENERATION=SEM.parent; REGISTRY=GENERATION.parent; AS_OF='2026-08-28'
def rows(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def canon(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def blobsha(p):
 d=p.read_bytes(); return hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()
def hits(axis,text):
 out=[]
 for facet in axis['facets']:
  ms=[p for p in facet['patterns'] if re.search(p,text,re.I)]
  if ms: out.append({'facet':facet['facet'],'matched_patterns':ms})
 return out
def build():
 if blobsha(HERE/'iteration3-summary.json')!=ITERATION3_SUMMARY_BLOB_SHA: raise ValueError('iteration3 summary drift')
 if blobsha(HERE/'iteration3-axis-deltas.jsonl')!=ITERATION3_AXIS_DELTA_BLOB_SHA: raise ValueError('iteration3 delta drift')
 base=json.loads((SEM/'summary.json').read_text()); i3=json.loads((HERE/'iteration3-summary.json').read_text())
 props=rows(GENERATION/'library-instance-proposals.jsonl'); libs={r['library_id']:r for r in rows(REGISTRY/'library-contributions.jsonl')}
 sources={r['source_id']:r for r in ITERATION4_PRIMARY_SOURCES}; claims=defaultdict(list)
 for c in ITERATION4_DEEP_CLAIMS: claims[c['supports_axis']].append(c)
 sigs=[]; fam=defaultdict(list); fc={a['axis']:Counter() for a in ITERATION4_AXES}; fh={a['axis']:set() for a in ITERATION4_AXES}
 for p in props:
  text=searchable_text(libs[p['library_ref']]); sels=[]
  for a in ITERATION4_AXES:
   hs=hits(a,text); status='EXPLICIT_CANDIDATE_SET_UNRATIFIED' if hs else 'UNRESOLVED_OWNER_INPUT_REQUIRED'
   for h in hs: fc[a['axis']][h['facet']]+=1
   if hs: fh[a['axis']].add(p['family_id'])
   sels.append({'axis':a['axis'],'status':status,'candidate_facets':hs}); fam[(p['family_id'],a['axis'])].append({'library_ref':p['library_ref'],'status':status,'candidate_facets':[h['facet'] for h in hs]})
  sigs.append({'record_kind':'macro_model_iteration4_signature_candidate','signature_id':'signature.macro.iter4.'+p['library_ref'].removeprefix('library.'),'library_ref':p['library_ref'],'family_id':p['family_id'],'source_gap_ref':p['source_gap_ref'],'axis_selections':sels,'status':'DISCOVERY_SIGNATURE_NOT_AUTHORITY','canonical_mutation_allowed':False,'completion_claim':False})
 deltas=[]
 for a in ITERATION4_AXES:
  aid=a['axis']; sels=[s for r in sigs for s in r['axis_selections'] if s['axis']==aid]; refs=set(a['evidence_refs'])
  deltas.append({'record_kind':'macro_model_iteration4_axis_delta','axis':aid,'question':a['question'],'phase':a['phase'],'facet_count':len(a['facets']),'non_collapse_laws':a['non_collapse'],'primary_source_refs':sorted(refs),'independent_issuer_count':len({sources[x]['issuer'] for x in refs}),'deep_claim_refs':[c['claim_id'] for c in claims[aid]],'candidate_cells':sum(bool(s['candidate_facets']) for s in sels),'unresolved_cells':sum(not s['candidate_facets'] for s in sels),'candidate_facet_occurrences':sum(fc[aid].values()),'candidate_facet_counts':dict(sorted(fc[aid].items())),'families_with_candidate_hits':len(fh[aid]),'model_verdict':a['model_verdict'],'status':'EVIDENCE_BACKED_RESEARCH_AXIS_NOT_RATIFIED','canonical_mutation_allowed':False,'completion_claim':False})
 db={r['axis']:r for r in deltas}; packs=[]; targeted=[]
 for n,((fid,aid),members) in enumerate(sorted(fam.items()),1):
  unr=sorted(m['library_ref'] for m in members if m['status']=='UNRESOLVED_OWNER_INPUT_REQUIRED'); counts=Counter(x for m in members for x in m['candidate_facets']); wid=f'work.macro.iter4.{n:04d}'
  packs.append({'record_kind':'macro_model_iteration4_family_axis_review_package','work_package_id':wid,'family_id':fid,'axis':aid,'library_count':len(members),'candidate_library_count':len(members)-len(unr),'unresolved_library_count':len(unr),'unresolved_library_refs':unr,'candidate_facet_counts':dict(sorted(counts.items())),'status':'OWNER_RESEARCH_AND_RATIFICATION_REQUIRED','canonical_mutation_allowed':False,'completion_claim':False})
  if unr:
   a=next(x for x in ITERATION4_AXES if x['axis']==aid); targeted.append({'record_kind':'macro_model_iteration4_targeted_evidence_work_package','targeted_work_package_id':wid.replace('work.macro','targeted.macro'),'review_package_ref':wid,'family_id':fid,'axis':aid,'unresolved_library_count':len(unr),'unresolved_library_refs':unr,'primary_source_refs':sorted(a['evidence_refs']),'deep_claim_refs':[c['claim_id'] for c in claims[aid]],'allowed_outcomes':['REQUIRED','CONDITIONAL','INAPPLICABLE','PROHIBITED','SPLIT_REQUIRED','MISSING_FACET','UNRESOLVED'],'status':'TARGETED_PRIMARY_SOURCE_REVIEW_REQUIRED','canonical_mutation_allowed':False,'completion_claim':False})
 i3src={r['source_id'] for r in rows(HERE/'iteration3-primary-sources.jsonl')}; news=[r for r in ITERATION4_PRIMARY_SOURCES if r['source_id'] not in i3src]
 i3claims={r['claim_id'] for r in rows(HERE/'iteration3-deep-evidence-claims.jsonl')}; newc=[r for r in ITERATION4_DEEP_CLAIMS if r['claim_id'] not in i3claims]
 i3ch={r['challenge_id'] for r in rows(HERE/'iteration3-macro-challenges.jsonl')}; newch=[r for r in ITERATION4_CHALLENGES if r['challenge_id'] not in i3ch]
 cd=db['semantic_constraints_and_validity']; corrections=[{**ITERATION4_CORRECTIONS[0],'candidate_cells':cd['candidate_cells'],'unresolved_cells':cd['unresolved_cells'],'families_with_candidate_hits':cd['families_with_candidate_hits'],'independent_issuer_count':cd['independent_issuer_count'],'validation_result':'NEW_AXIS_SURVIVED_CHALLENGE' if cd['candidate_cells']>0 and cd['independent_issuer_count']>=4 else 'NEW_AXIS_FAILED_CHALLENGE'}]
 cells=len(sigs)*len(ITERATION4_AXES); candidates=sum(bool(s['candidate_facets']) for r in sigs for s in r['axis_selections'])
 summary={'program_id':'program.macro-model-primary-source-challenge.v4','as_of':AS_OF,'iteration3_summary_blob_sha':ITERATION3_SUMMARY_BLOB_SHA,'iteration3_axis_delta_blob_sha':ITERATION3_AXIS_DELTA_BLOB_SHA,'primary_source_count':len(ITERATION4_PRIMARY_SOURCES),'new_primary_source_count':len(news),'primary_source_issuer_count':len({r['issuer'] for r in ITERATION4_PRIMARY_SOURCES}),'deep_bounded_claim_count':len(ITERATION4_DEEP_CLAIMS),'new_deep_bounded_claim_count':len(newc),'macro_challenge_count':len(ITERATION4_CHALLENGES),'new_macro_challenge_count':len(newch),'base_axis_count':base['axes'],'candidate_axis_count':len(ITERATION4_AXES),'effective_research_axis_count':base['axes']+len(ITERATION4_AXES),'library_count':len(sigs),'family_count':len({r['family_id'] for r in props}),'base_axis_cells':base['axis_cells'],'iteration4_candidate_axis_cells':cells,'effective_research_axis_cells':base['axis_cells']+cells,'candidate_cells':candidates,'unresolved_cells':cells-candidates,'family_axis_review_packages':len(packs),'targeted_evidence_work_packages':len(targeted),'targeted_unresolved_library_occurrences':sum(r['unresolved_library_count'] for r in targeted),'constraint_candidate_cells':cd['candidate_cells'],'constraint_candidate_families':cd['families_with_candidate_hits'],'constraint_independent_issuers':cd['independent_issuer_count'],'cross_axis_interactions':len(ITERATION4_INTERACTIONS),'canonical_gaps_closed':0,'owner_decisions':0,'completion_claim':False,'status':'ITERATION_4_MODELED_SATURATION_CHALLENGE_REQUIRED'}
 model={'record_kind':'effective_macro_model_research_candidate_iteration4','model_id':'model.enterprise-data-analytics-semantic-axes.challenge-v4','as_of':AS_OF,'base_axis_count':base['axes'],'candidate_axis_ids':[a['axis'] for a in ITERATION4_AXES],'candidate_axis_count':len(ITERATION4_AXES),'effective_research_axis_count':base['axes']+len(ITERATION4_AXES),'iteration_lineage':['v1 added five candidate axes','v2 corrected population lexical contamination and added causal plus stochastic axes','v3 split quantitative value from observation/metrology','v4 added semantic constraints/validity after proving it is not normativity or conformance evidence'],'status':'ITERATION_4_RESEARCH_CHALLENGE_CANDIDATE_NOT_RATIFIED','canonical_mutation_allowed':False,'completion_claim':False}
 return {'sources':ITERATION4_PRIMARY_SOURCES,'new_sources':news,'claims':ITERATION4_DEEP_CLAIMS,'new_claims':newc,'challenges':ITERATION4_CHALLENGES,'new_challenges':newch,'axis_deltas':deltas,'signatures':sigs,'packages':packs,'targeted':targeted,'interactions':ITERATION4_INTERACTIONS,'corrections':corrections,'model':model,'summary':summary}
def outputs():
 b=build(); files={'iteration4-primary-sources.jsonl':''.join(canon(r)+'\n' for r in b['sources']),'iteration4-new-primary-sources.jsonl':''.join(canon(r)+'\n' for r in b['new_sources']),'iteration4-deep-evidence-claims.jsonl':''.join(canon(r)+'\n' for r in b['claims']),'iteration4-new-deep-claims.jsonl':''.join(canon(r)+'\n' for r in b['new_claims']),'iteration4-macro-challenges.jsonl':''.join(canon(r)+'\n' for r in b['challenges']),'iteration4-new-challenges.jsonl':''.join(canon(r)+'\n' for r in b['new_challenges']),'iteration4-axis-deltas.jsonl':''.join(canon(r)+'\n' for r in b['axis_deltas']),'iteration4-signatures.jsonl':''.join(canon(r)+'\n' for r in b['signatures']),'iteration4-family-axis-review-packages.jsonl':''.join(canon(r)+'\n' for r in b['packages']),'iteration4-targeted-evidence-work-packages.jsonl':''.join(canon(r)+'\n' for r in b['targeted']),'iteration4-cross-axis-interactions.jsonl':''.join(canon(r)+'\n' for r in b['interactions']),'iteration4-correction-receipts.jsonl':''.join(canon(r)+'\n' for r in b['corrections']),'iteration4-effective-macro-model.json':json.dumps(b['model'],sort_keys=True,indent=2)+'\n','iteration4-summary.json':json.dumps(b['summary'],sort_keys=True,indent=2)+'\n'}; mf={n:{'bytes':len(t.encode()),'sha256':hashlib.sha256(t.encode()).hexdigest()} for n,t in files.items()}; files['iteration4-manifest.json']=json.dumps({'manifest_id':'manifest.macro-model-primary-source-challenge.v4','as_of':AS_OF,'files':mf,'completion_claim':False},sort_keys=True,indent=2)+'\n'; return files
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); a=ap.parse_args(); gen=outputs(); stale=[]
 for n,t in gen.items():
  p=HERE/n
  if a.check:
   if not p.is_file() or p.read_text()!=t: stale.append(n)
  else: p.write_text(t)
 if stale: print('STALE '+', '.join(stale)); return 1
 s=json.loads(gen['iteration4-summary.json']); print(f"{'CHECK' if a.check else 'BUILD'} PASS macro iteration 4: {s['primary_source_count']} sources; 16+{s['candidate_axis_count']}={s['effective_research_axis_count']} axes; constraint candidates={s['constraint_candidate_cells']} across {s['constraint_candidate_families']} families; zero authority/canonical promotions"); return 0
if __name__=='__main__': raise SystemExit(main())
