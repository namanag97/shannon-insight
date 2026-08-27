#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from build_phase5 import HERE,build,outputs

def main()->int:
    for n,t in outputs().items():
        p=HERE/n;assert p.is_file() and p.read_text()==t,f"stale {n}"
    m=json.loads((HERE/"manifest.json").read_text())
    for n,c in m["files"].items():
        d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
    b=build();mods=b["constitution"]["modules"]
    assert [x["axis"] for x in mods]==["semantic_role","composition_algebra","resources_and_failure","evidence_and_conformance"]
    assert len(mods[0]["role_kinds"])==14 and len(mods[0]["operation_coordinates"])==15
    assert len(mods[1]["composition_coordinates"])==18 and len(mods[1]["composition_forms"])==10
    assert len(mods[2]["resource_coordinates"])==15 and len(mods[2]["failure_coordinates"])==15
    assert len(mods[3]["evidence_coordinates"])==15 and len(mods[3]["oracle_classes"])==11
    assert all(len(x["non_collapse_laws"])>=16 for x in mods)
    ids={x["source_id"] for x in b["sources"]};mids={x["module_id"] for x in mods}
    assert len(ids)==len(b["sources"])==len(b["claims"])==10
    assert all(x["source_ref"] in ids and set(x["supports_module_refs"])<=mids and x["authority_limit"] for x in b["claims"])
    assert len(b["projection"]["required_ir_roles"])>=32 and len(b["projection"]["refusal_roles"])>=25
    assert b["summary"]["completion_claim"] is False and b["summary"]["canonical_exact_gaps_closed"]==0
    print("PASS Phase-5 behavior/resources/proof constitution candidate: 4 modules, 10 primary claims, explicit roles, composition laws, finite resources, total failures and scoped conformance; owner ratification remains open");return 0

if __name__=="__main__":raise SystemExit(main())
