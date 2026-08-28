#!/usr/bin/env python3
"""Fail-closed validation for sparse B04 exact-evidence dispositions."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from urllib.parse import urlparse
HERE=Path(__file__).resolve().parent
BUILDER=HERE/'build_effective_evidence_governance.py'; BASE=HERE/'organization-family-membership-claims.jsonl'; UP=HERE/'organization-family-evidence-upgrades.jsonl'; OUT=HERE/'effective-evidence-upgrade-dispositions.jsonl'; SUM=HERE/'effective-evidence-governance-summary.json'
def L(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
def validate():
    before={p:p.read_bytes() for p in (OUT,SUM) if p.is_file()}
    if len(before)!=2: raise AssertionError('effective evidence artifacts missing')
    base=L(BASE); up=L(UP); out=L(OUT); summary=json.loads(SUM.read_text())
    if len(base)!=1012: raise AssertionError(f'unexpected base population {len(base)}')
    if len(out)!=len(up): raise AssertionError('sparse disposition count drift')
    by={r['claim_id']:r for r in base}
    if len({r['claim_id'] for r in out})!=len(out): raise AssertionError('duplicate disposition claim')
    for r in out:
        b=by.get(r['claim_id'])
        if not b or (r['organization_id'],r['family_id'])!=(b['organization_id'],b['family_id']): raise AssertionError(f"scope drift {r.get('upgrade_id')}")
        p=urlparse(r['official_locator'])
        if p.scheme!='https' or not p.netloc or not (p.path or '/').strip('/'): raise AssertionError(f"non-exact locator {r['upgrade_id']}")
        if r.get('evidence_strength')!='STRONG_EXACT_OFFICIAL_PRODUCT_DOCUMENTATION': raise AssertionError(f"strength drift {r['upgrade_id']}")
        if r.get('effective_status')!='BOUND_STRONG_EXACT_PRODUCT_EVIDENCE_AUTHORITY_WITHHELD': raise AssertionError(f"status drift {r['upgrade_id']}")
        for k in ('semantic_authority','qualification_claim','completion_claim'):
            if r.get(k) is not False: raise AssertionError(f"illegal {k} {r['upgrade_id']}")
    if summary['strong_exact_product_membership_claim_count']!=len(out) or summary['remaining_weak_membership_claim_count']!=len(base)-len(out): raise AssertionError('summary drift')
    if summary.get('semantic_authority_promotions')!=0 or summary.get('qualification_promotions')!=0 or summary.get('completion_claim') is not False: raise AssertionError('illegal summary promotion')
    run=subprocess.run([sys.executable,str(BUILDER)],cwd=HERE,capture_output=True,text=True)
    if run.returncode: raise AssertionError(run.stdout+run.stderr)
    if before!={p:p.read_bytes() for p in (OUT,SUM)}: raise AssertionError('artifacts stale or nondeterministic')
    return {'base_claim_count':len(base),'upgrade_count':len(out),'remaining_weak_count':len(base)-len(out),'status':'VALID','completion_claim':False}
def main():
    try: print(json.dumps(validate(),sort_keys=True)); return 0
    except Exception as e: print(f'FAIL effective_evidence_governance: {e}',file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
