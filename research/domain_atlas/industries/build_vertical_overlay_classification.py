#!/usr/bin/env python3
"""Canonicalize B07 local industry/subindustry refs as editioned analytical-overlay coordinates.

This does not equate local vertical coordinates with ISIC. Each node is defined extensionally by
exact committed analytical cases that cite it; mapping to the ISIC Rev.5 reference spine remains
explicitly unresolved unless a separately reviewed crosswalk exists.
"""
from __future__ import annotations
import hashlib,json
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
FOUND=HERE/'foundation'
PACKS=['built_food_environment','commerce_services','energy_resources','finance_insurance','health_life_sciences','manufacturing_industrial','public_education','telecom_media_tech','transport_logistics']

def L(p): return [json.loads(x) for x in Path(p).read_text(encoding='utf-8').splitlines() if x.strip()]
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def node_id(pack,raw): return f"industry.vertical_overlay.{pack}.{hashlib.sha256(raw.encode()).hexdigest()[:16]}"
def scheme_id(pack): return f"scheme.shannon.vertical_overlay.{pack}.e2026_08_27"

def main():
    queue=L(HERE/'canonical-reference-review-queue.jsonl')
    industry=[r for r in queue if r['reference_domain']=='industry_classification']
    if len(industry)!=398: raise SystemExit(f'expected 398 industry queue rows, got {len(industry)}')
    q_by_pack=defaultdict(list)
    for q in industry:
        if len(q.get('origin_packs',[]))!=1: raise SystemExit(f"{q['queue_id']}: expected exactly one owning pack, got {q.get('origin_packs')}")
        q_by_pack[q['origin_packs'][0]].append(q)
    if set(q_by_pack)!=set(PACKS): raise SystemExit(f'pack set drift: {sorted(q_by_pack)}')

    cases_by_pack={}; sources_by_pack={}
    for pack in PACKS:
        cases=L(HERE/pack/'analytics-cases.jsonl'); cases_by_pack[pack]={r['record_id']:r for r in cases}
        sources=L(HERE/pack/'sources.jsonl'); sources_by_pack[pack]={r.get('source_id',r.get('record_id')) for r in sources}

    schemes=[]; nodes=[]; decisions=[]; errors=[]
    existing={r['queue_id']:r for r in L(HERE/'canonical-reference-adjudications.jsonl')}
    for pack in PACKS:
        qs=q_by_pack[pack]
        # The pack-wide coordinate is the row used by the largest number of cases; all nine packs
        # have one such root covering the complete pack case population.
        root=max(qs,key=lambda r:(r['occurrence_count'],r['raw_ref']))
        pack_cases=cases_by_pack[pack]
        root_cases=[c for c in pack_cases.values() if root['raw_ref']==c.get('industry_id') or root['raw_ref'] in c.get('subindustry_ids',[])]
        if len(root_cases)!=len(pack_cases): errors.append(f"{pack}: root {root['raw_ref']} covers {len(root_cases)} / {len(pack_cases)} cases")
        pack_evidence=sorted({e for c in pack_cases.values() for e in c.get('evidence_refs',[])})
        schemes.append({
          'scheme_id':scheme_id(pack),'scheme_series_id':f'scheme.shannon.vertical_overlay.{pack}','record_kind':'classification_scheme','edition':1,'status':'candidate',
          'name':f'Shannon {pack.replace("_"," ").title()} analytical coverage overlay, edition 2026-08-27','custodian':'Shannon Insight research corpus',
          'scheme_kind':'specialist_activity_overlay','concept_classified':'analytical solution coverage coordinate used to scope vertical analytical cases, not principal economic activity',
          'statistical_unit':'analytical case / governed solution scope','geographic_scope':['open_world_unspecified'],
          'temporal_validity':{'edition_label':'2026-08-27','valid_from':'2026-08-27','valid_to':None,'transition_note':'New edition required when case membership, coordinate meaning or crosswalk posture changes.'},
          'hierarchy':{'levels':['pack_root','local_coordinate'],'code_semantics':'Exact raw vertical coordinate strings from the committed pack; hierarchy is pack root plus local analytical coordinates.'},
          'assignment_rules':['A case is a member only when its committed industry_id or subindustry_ids explicitly names the coordinate.','Membership is edition-frozen to the listed case population; lexical similarity does not imply membership.','Economic-activity classification requires a separate reviewed crosswalk to ISIC or another registered scheme.'],
          'atlas_role':'specialist_analytical_overlay','source_refs':pack_evidence or [next(iter(sources_by_pack[pack]))],
          'official_crosswalks':[{'target_scheme_edition_id':'scheme.un.isic.rev5','source_ref':'source.un.isic.rev5.structure','availability':'not_found','notes':'No reviewed row-level mapping for these local analytical coordinates is asserted by this edition.'}],
          'limitations':['This is a research coverage overlay, not an official industry classification.','A local coordinate may overlap, combine or cut across multiple ISIC activities, provider types, functions or regulatory lines.','Provider, product, occupation, business function and economic activity remain orthogonal unless separately crosswalked.']
        })
        root_id=node_id(pack,root['raw_ref'])
        for q in sorted(qs,key=lambda r:r['queue_id']):
            raw=q['raw_ref']; matching=[c for c in pack_cases.values() if raw==c.get('industry_id') or raw in c.get('subindustry_ids',[])]
            refs=sorted(c['record_id'] for c in matching); ev=sorted({e for c in matching for e in c.get('evidence_refs',[])})
            if len(refs)!=q['occurrence_count']: errors.append(f"{q['queue_id']}: queue count {q['occurrence_count']} != extensional case count {len(refs)}")
            if not refs: errors.append(f"{q['queue_id']}: empty case extent")
            nid=node_id(pack,raw); is_root=q['queue_id']==root['queue_id']
            parent=None if is_root else root_id
            ancestors=[] if is_root else [root_id]
            title=raw.replace('_',' ').replace('.',' / ').strip()
            nodes.append({
              'record_id':nid,'record_kind':'vertical_analytical_overlay_node','edition':1,'status':'research_candidate_not_ratified','scheme_edition_id':scheme_id(pack),
              'raw_ref':raw,'title':title,'origin_packs':[pack],'parent_ref':parent,'ancestor_refs':ancestors,
              'semantic_boundary':f"Edition-1 analytical coverage coordinate whose current extent is exactly the {len(refs)} committed analytical case record(s) listed in case_refs that explicitly cite '{raw}'. It is not an economic-activity assignment.",
              'case_refs':refs,'case_count':len(refs),'evidence_refs':ev or pack_evidence,'geographic_scope':['open_world_unspecified'],
              'reference_spine_mapping':{'target_scheme_edition_id':'scheme.un.isic.rev5','relation':'unresolved','target_refs':[],'mapping_basis':'local_extension_unmapped','losses':['Collapsing this analytical coordinate to an unreviewed economic-activity code can lose provider/function/regulatory/solution-scope distinctions.','The exact ISIC extent, if any, is not yet reviewed for this local coordinate.'],'transitive_use':'forbidden'},
              'non_collapse_laws':['local analytical overlay coordinate != economic activity code','case membership != organization principal-activity assignment','provider/function/regulatory role != industry activity unless separately crosswalked'],
              'remaining_gate':'classification and domain reviewers must adjudicate reference-spine relation before cross-scheme compilation','completion_claim':False
            })
            existing[q['queue_id']]={
              'queue_id':q['queue_id'],'record_kind':'canonical_reference_adjudication','edition':1,'reference_domain':'industry_classification','raw_ref':raw,
              'relation':'canonical_local_analytical_overlay_identity','candidate_target_refs':[nid],'target_industry_refs':[nid],
              'decision_basis':[{'claim':'The local vertical coordinate is canonically bound by edition, pack ownership, exact extensional case membership and evidence; no ISIC equivalence is inferred.','source_ref':'research/domain_atlas/industries/foundation/README.md'}],
              'non_collapse_laws':['local overlay != ISIC identity','canonical local identity != ratified cross-scheme mapping'],
              'remaining_gate':'classification/domain review of ISIC relation and residual semantics','status':'research_resolved_candidate_not_ratified','completion_claim':False,
              'research_tranche':'b07.vertical_overlay_classification.2026_08_27'
            }
    if errors:
        print('\n'.join('ERROR: '+e for e in errors)); return 1
    (FOUND/'vertical-analytical-overlay-schemes.jsonl').write_text(''.join(canon(r)+'\n' for r in sorted(schemes,key=lambda r:r['scheme_id'])),encoding='utf-8')
    (FOUND/'vertical-analytical-overlay-nodes.jsonl').write_text(''.join(canon(r)+'\n' for r in sorted(nodes,key=lambda r:r['record_id'])),encoding='utf-8')
    (HERE/'canonical-reference-adjudications.jsonl').write_text(''.join(canon(r)+'\n' for r in sorted(existing.values(),key=lambda r:r['queue_id'])),encoding='utf-8')
    summary={'report_id':'b07_vertical_analytical_overlay_classification','as_of':'2026-08-27','scheme_count':len(schemes),'node_count':len(nodes),'industry_queue_decision_count':len(industry),'represented_occurrences':sum(q['occurrence_count'] for q in industry),'reference_spine_mappings_ratified':0,'semantic_ratifications_created':0,'completion_claim':False,'status':'ALL_LOCAL_INDUSTRY_REFS_CANONICALIZED_AS_EVIDENCE_BOUND_OVERLAYS_ISIC_MAPPING_OPEN'}
    (FOUND/'vertical-analytical-overlay-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
