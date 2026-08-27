#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from build_constitution_coverage import HERE,build,outputs

def main()->int:
    for n,t in outputs().items():
        p=HERE/n;assert p.is_file() and p.read_text()==t,f"stale {n}"
    m=json.loads((HERE/"constitution-coverage-manifest.json").read_text())
    for n,c in m["files"].items():
        d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
    b=build();coverage=b["coverage"];queue=b["inheritance"]
    axes={x["axis"] for x in queue}; families={x["family_id"] for x in queue}
    assert coverage["axis_count"]==len(axes)==16 and coverage["family_count"]==len(families)
    assert coverage["family_axis_matrix_count"]==len(queue)==len(axes)*len(families)
    assert len({(x["axis"],x["family_id"]) for x in queue})==len(queue)
    assert all(x["status"]=="OWNER_APPLICABILITY_AND_EXCEPTION_MATRIX_REQUIRED" and x["closure_effect"] for x in queue)
    assert coverage["completion_claim"] is False and coverage["canonical_gap_effect"]==0
    print(f"PASS semantic constitution coverage: all {len(axes)} axes map exactly once to five candidate constitutions and {len(queue)} family inheritance matrices; owner ratification remains open");return 0

if __name__=="__main__":raise SystemExit(main())
