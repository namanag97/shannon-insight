#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from build_phase4 import HERE,build,outputs

def main()->int:
    for name,text in outputs().items():
        path=HERE/name; assert path.is_file() and path.read_text()==text,f"stale {name}"
    manifest=json.loads((HERE/"manifest.json").read_text())
    for name,contract in manifest["files"].items():
        data=(HERE/name).read_bytes(); assert len(data)==contract["bytes"] and hashlib.sha256(data).hexdigest()==contract["sha256"]
    bundle=build(); constitution=bundle["constitution"]; modules=constitution["modules"]
    assert [x["axis"] for x in modules]==["representation","compatibility_and_evolution"]
    assert len(modules[0]["representation_layers"])==10 and len(modules[0]["binding_coordinates"])==17
    assert len(modules[1]["compatibility_dimensions"])==15 and len(modules[1]["directional_relations"])==8 and len(modules[1]["change_lifecycle"])==15
    assert all(len(x["non_collapse_laws"])>=16 for x in modules)
    source_ids={x["source_id"] for x in bundle["sources"]}; module_ids={x["module_id"] for x in modules}
    assert len(source_ids)==len(bundle["sources"])==len(bundle["claims"])==9
    assert all(x["source_ref"] in source_ids and set(x["supports_module_refs"])<=module_ids and x["authority_limit"] for x in bundle["claims"])
    assert len(bundle["projection"]["required_ir_roles"])>=30 and len(bundle["projection"]["refusal_roles"])>=23
    assert bundle["summary"]["completion_claim"] is False and bundle["summary"]["canonical_exact_gaps_closed"]==0
    print("PASS Phase-4 representation/evolution constitution candidate: 2 modules, 9 primary claims, explicit representation layers, directional compatibility dimensions, migration lifecycle and refusals; owner ratification remains open")
    return 0

if __name__=="__main__": raise SystemExit(main())
