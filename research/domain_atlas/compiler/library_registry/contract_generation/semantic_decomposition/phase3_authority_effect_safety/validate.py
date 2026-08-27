#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from build_phase3 import HERE,build,outputs

def main()->int:
    for n,t in outputs().items():
        p=HERE/n;assert p.is_file() and p.read_text()==t,f"stale {n}"
    m=json.loads((HERE/"manifest.json").read_text())
    for n,c in m["files"].items():
        d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
    b=build();c=b["constitution"];mods=c["modules"]
    assert [x["axis"] for x in mods]==["authority_and_trust","effect_boundary","privacy_security_safety"]
    assert len(mods[0]["authority_coordinates"])==16 and len(mods[0]["trust_coordinates"])==10
    assert len(mods[1]["effect_coordinates"])==16 and len(mods[1]["boundary_kinds"])==6
    assert len(mods[2]["privacy_coordinates"])==12 and len(mods[2]["security_coordinates"])==12 and len(mods[2]["safety_coordinates"])==10
    assert all(len(x["non_collapse_laws"])>=12 for x in mods)
    ids={x["source_id"] for x in b["sources"]};mids={x["module_id"] for x in mods}
    assert len(ids)==len(b["sources"])==len(b["claims"])==8
    assert all(x["source_ref"] in ids and set(x["supports_module_refs"])<=mids and x["authority_limit"] for x in b["claims"])
    assert len(b["projection"]["required_ir_roles"])>=23 and len(b["projection"]["refusal_roles"])>=19
    assert b["summary"]["completion_claim"] is False and b["summary"]["canonical_exact_gaps_closed"]==0
    print("PASS Phase-3 authority/effect/safety constitution candidate: 3 modules, 8 primary claims, explicit authority/effect/privacy/security/safety coordinates and refusals; owner ratification remains open");return 0

if __name__=="__main__":raise SystemExit(main())
