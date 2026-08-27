#!/usr/bin/env python3
"""Prioritize weak organization-family claims into evidence-upgrade campaigns."""
from __future__ import annotations
import json
from collections import Counter,defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent

def jl(name): return [json.loads(x) for x in (HERE/name).read_text(encoding='utf-8').splitlines() if x.strip()]
def main():
    claims=jl('organization-family-membership-claims.jsonl'); identities=jl('organization-identity-projection.jsonl')
    ident={r['organization_id']:r for r in identities}; by=defaultdict(list)
    for c in claims: by[c['organization_id']].append(c)
    rows=[]
    for oid,members in by.items():
        i=ident[oid]; families=sorted({m['family_id'] for m in members}); homepage=sum(m['evidence_strength']=='WEAK_HOMEPAGE_ONLY' for m in members)
        score=len(members)*10+homepage*3
        rows.append({'record_kind':'horizontal_evidence_upgrade_campaign','campaign_id':'evidence-upgrade.'+oid,'organization_id':oid,'canonical_name':i['canonical_name'],'canonical_url':i['canonical_url'],'organization_kind':i['organization_kind'],'family_refs':families,'weak_membership_count':len(members),'homepage_only_count':homepage,'priority_score':score,'required_evidence_upgrade':['exact product/project identity','official product/technical/specification/release locator','bounded capability/adoption claim per supported family','edition/version/effective date when applicable','organization-product/project relationship','acquisition/rename/parent identity if applicable'],'promotion_law':'A product page may strengthen only the family claims its exact bounded capability statement supports; organization-wide reputation is never transitive evidence.','status':'OPEN_EVIDENCE_RESEARCH','completion_claim':False})
    rows.sort(key=lambda r:(-r['priority_score'],-r['weak_membership_count'],r['canonical_name']))
    (HERE/'evidence-upgrade-campaigns.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows),encoding='utf-8')
    summary={'report_id':'horizontal_evidence_upgrade_campaigns','as_of':'2026-08-27','organization_campaign_count':len(rows),'weak_membership_count':len(claims),'top_20_campaigns':[{'organization_id':r['organization_id'],'name':r['canonical_name'],'weak_membership_count':r['weak_membership_count'],'priority_score':r['priority_score']} for r in rows[:20]],'strong_memberships_created':0,'completion_claim':False,'status':'PRIORITIZED_EXACT_EVIDENCE_RESEARCH_NOT_UPGRADED'}
    (HERE/'evidence-upgrade-campaign-summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
