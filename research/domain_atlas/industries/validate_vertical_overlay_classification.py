#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
FOUND=HERE/'foundation'
PACKS=['built_food_environment','commerce_services','energy_resources','finance_insurance','health_life_sciences','manufacturing_industrial','public_education','telecom_media_tech','transport_logistics']
def L(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
 errors=[]
 queue=[r for r in L(HERE/'canonical-reference-review-queue.jsonl') if r['reference_domain']=='industry_classification']
 nodes=L(FOUND/'vertical-analytical-overlay-nodes.jsonl'); schemes=L(FOUND/'vertical-analytical-overlay-schemes.jsonl')
 ledger={r['queue_id']:r for r in L(HERE/'canonical-reference-adjudications.jsonl')}
 node_by={r['record_id']:r for r in nodes}
 if len(queue)!=398 or len(nodes)!=398: errors.append(f'expected 398 queue/nodes, got {len(queue)}/{len(nodes)}')
 if len(schemes)!=9: errors.append(f'expected 9 overlay schemes, got {len(schemes)}')
 if {s['scheme_id'].split('.')[-2] for s in schemes}!=set(PACKS): errors.append('scheme pack coverage drift')
 cases={}; source_ids={}
 for pack in PACKS:
  cs=L(HERE/pack/'analytics-cases.jsonl'); cases.update({r['record_id']:r for r in cs})
  src=L(HERE/pack/'sources.jsonl'); source_ids[pack]={r.get('source_id',r.get('record_id')) for r in src}
 impact=0; roots=Counter()
 for q in queue:
  d=ledger.get(q['queue_id'])
  if not d: errors.append(q['queue_id']+': missing adjudication'); continue
  if d.get('research_tranche')!='b07.vertical_overlay_classification.2026_08_27': errors.append(q['queue_id']+': wrong tranche')
  if d.get('relation')!='canonical_local_analytical_overlay_identity' or d.get('completion_claim') or d.get('status')!='research_resolved_candidate_not_ratified': errors.append(q['queue_id']+': promotion/relation invalid')
  targets=d.get('target_industry_refs',[])
  if len(targets)!=1 or targets[0] not in node_by: errors.append(q['queue_id']+': target node missing'); continue
  n=node_by[targets[0]]; impact+=q['occurrence_count']; pack=q['origin_packs'][0]
  if n['raw_ref']!=q['raw_ref'] or n['origin_packs']!=[pack]: errors.append(q['queue_id']+': identity drift')
  if n['case_count']!=q['occurrence_count'] or len(n['case_refs'])!=q['occurrence_count']: errors.append(q['queue_id']+': occurrence/case count mismatch')
  for cid in n['case_refs']:
   c=cases.get(cid)
   if not c or not (q['raw_ref']==c.get('industry_id') or q['raw_ref'] in c.get('subindustry_ids',[])): errors.append(q['queue_id']+': invalid case membership '+cid)
  m=n['reference_spine_mapping']
  if m!={'target_scheme_edition_id':'scheme.un.isic.rev5','relation':'unresolved','target_refs':[],'mapping_basis':'local_extension_unmapped','losses':['Collapsing this analytical coordinate to an unreviewed economic-activity code can lose provider/function/regulatory/solution-scope distinctions.','The exact ISIC extent, if any, is not yet reviewed for this local coordinate.'],'transitive_use':'forbidden'}: errors.append(q['queue_id']+': reference-spine mapping posture drift')
  if n.get('completion_claim') or n['status']!='research_candidate_not_ratified' or len(n['non_collapse_laws'])<2: errors.append(q['queue_id']+': node promotion/non-collapse invalid')
  if n['parent_ref'] is None: roots[pack]+=1
  elif n['parent_ref'] not in node_by: errors.append(q['queue_id']+': missing parent')
  if not set(n['evidence_refs']) <= source_ids[pack]: errors.append(q['queue_id']+': node evidence not in owning pack source registry')
 if impact!=5092: errors.append(f'expected 5092 occurrence impact, got {impact}')
 if any(roots[p]!=1 for p in PACKS): errors.append(f'exactly one root per pack required: {dict(roots)}')
 for s in schemes:
  pack=s['scheme_id'].split('.')[-2]
  if s['scheme_kind']!='specialist_activity_overlay' or s['atlas_role']!='specialist_analytical_overlay' or s['status']!='candidate': errors.append(s['scheme_id']+': scheme posture invalid')
  if not set(s['source_refs']) <= source_ids[pack]: errors.append(s['scheme_id']+': source refs not from owning pack')
  if any(x.get('target_scheme_edition_id')!='scheme.un.isic.rev5' or x.get('availability')!='not_found' for x in s.get('official_crosswalks',[])): errors.append(s['scheme_id']+': must not invent ISIC correspondence')
 if errors:
  for e in errors[:100]: print('ERROR: '+e)
  print(f'ERROR COUNT: {len(errors)}')
  return 1
 print('PASS: 9 overlay schemes / 398 canonical local industry identities / 5,092 occurrences; ISIC mapping and ratification withheld')
 return 0
if __name__=='__main__': raise SystemExit(main())
