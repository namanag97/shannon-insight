#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from build_pilot import HERE,build,outputs

def main()->int:
    for n,t in outputs().items():
        p=HERE/n;assert p.is_file() and p.read_text()==t,f"stale {n}"
    m=json.loads((HERE/"manifest.json").read_text())
    for n,c in m["files"].items():
        d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
    b=build();records=b["records"];contracts=b["contracts"]
    assert len(records)==72*16 and len(contracts)==72 and len(b["defaults"])==16 and len(b["per_lib"])==72
    assert len({(x["library_ref"],x["axis"]) for x in records})==72*16
    assert len({x["library_ref"] for x in contracts})==72
    assert all(x["exact_public_type_names"] and x["exact_public_trait_names"] and x["exact_operation_refs"] for x in contracts)
    assert all(x["applicability_decision"]=="UNRESOLVED" and "NOT_AUTHORITY" in x["status"] for x in records)
    assert all("NOT_EXACT_CONTRACT" in x["status"] for x in contracts)
    packages=b["vacancy_packages"]
    assert len({x["axis"] for x in packages})==b["summary"]["vacancy_axes"]==6
    assert len(packages)==b["summary"]["vacancy_work_packages"]
    assert sum(x["library_count"] for x in packages)==b["summary"]["total_axis_evidence_vacancies"]==325
    assert all(x["completion_effect"] and x["status"]=="RESEARCH_AND_OWNER_ADJUDICATION_REQUIRED" for x in packages)
    assert b["summary"]["automatic_owner_decisions"]==b["summary"]["canonical_exact_gaps_closed"]==0
    print(f"PASS method-kernel semantic pilot: 72 source records cover 1,152 axis rows and exact type/trait/operation name candidates; {b['summary']['total_axis_evidence_vacancies']} evidence vacancies and all owner gates remain explicit")
    return 0

if __name__=="__main__":raise SystemExit(main())
