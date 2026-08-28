#!/usr/bin/env python3
"""Build sparse effective B04 evidence dispositions over immutable weak base claims."""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse

HERE=Path(__file__).resolve().parent
BASE=HERE/'organization-family-membership-claims.jsonl'
UPGRADES=HERE/'organization-family-evidence-upgrades.jsonl'
OUTPUT=HERE/'effective-evidence-upgrade-dispositions.jsonl'
SUMMARY=HERE/'effective-evidence-governance-summary.json'
REQ={'upgrade_id','claim_id','organization_id','family_id','product_id','product_name','official_locator','bounded_claim','evidence_role','evidence_strength','verified_on','organization_product_relationship','identity_posture','acquisition_or_rename_posture'}

def L(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def home(u): return not (urlparse(u).path or '/').strip('/')

def main():
    base=L(BASE); upgrades=L(UPGRADES); by={r['claim_id']:r for r in base}
    if len(by)!=len(base): raise SystemExit('duplicate base claims')
    seen_u=set(); seen_c=set(); out=[]
    for u in upgrades:
        miss=REQ-u.keys()
        if miss: raise SystemExit(f"{u.get('upgrade_id')}: missing {sorted(miss)}")
        if u['upgrade_id'] in seen_u or u['claim_id'] in seen_c: raise SystemExit('duplicate upgrade or claim target')
        b=by.get(u['claim_id'])
        if not b: raise SystemExit(f"unknown base claim: {u['claim_id']}")
        if (u['organization_id'],u['family_id'])!=(b['organization_id'],b['family_id']): raise SystemExit(f"scope drift: {u['upgrade_id']}")
        p=urlparse(u['official_locator'])
        if p.scheme!='https' or not p.netloc or home(u['official_locator']): raise SystemExit(f"non-exact locator: {u['upgrade_id']}")
        if u['evidence_role']!='product_boundary_evidence' or u['evidence_strength']!='STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION': raise SystemExit(f"invalid evidence posture: {u['upgrade_id']}")
        for k in ('semantic_authority','qualification_claim','completion_claim'):
            if u.get(k) is not False: raise SystemExit(f"illegal promotion {k}: {u['upgrade_id']}")
        seen_u.add(u['upgrade_id']); seen_c.add(u['claim_id'])
        out.append({**u,'base_evidence_locator':b['evidence_locator'],'base_evidence_strength':b['evidence_strength'],'effective_status':'BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_AUTHORITY_WITHHELD'})
    out.sort(key=lambda r:r['claim_id'])
    OUTPUT.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in out),encoding='utf-8')
    orgs=sorted({r['organization_id'] for r in out}); fams=sorted({r['family_id'] for r in out})
    summary={'report_id':'effective_horizontal_evidence_governance','as_of':'2026-08-28','base_membership_claim_count':len(base),'exact_evidence_upgrade_count':len(out),'strong_exact_product_membership_claim_count':len(out),'remaining_weak_membership_claim_count':len(base)-len(out),'organization_count_with_exact_upgrade':len(orgs),'family_count_with_exact_upgrade':len(fams),'upgraded_organization_ids':orgs,'upgraded_family_ids':fams,'semantic_authority_promotions':0,'qualification_promotions':0,'completion_claim':False,'status':'EXACT_EVIDENCE_OVERLAY_ACTIVE_REMAINING_WEAK_CLAIMS_EXPLICIT'}
    SUMMARY.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(summary,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
