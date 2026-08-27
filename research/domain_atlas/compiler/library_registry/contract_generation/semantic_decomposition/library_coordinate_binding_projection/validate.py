#!/usr/bin/env python3
"""Validate exact per-library coordinate requirements and fail-closed lowering dockets."""
import hashlib,json
from build_library_coordinate_binding_projection import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 m=json.loads((HERE/"manifest.json").read_text())
 for n,c in m["files"].items():d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
 b=build();s=b["summary"];req=b["requirements"];d=b["dockets"]
 assert len(req)==len({r["requirement_id"] for r in req})
 assert len(d)==len({r["library_ref"] for r in d}) and all(r["axis_requirement_count"]==16 and r["cross_axis_seam_count"]==20 for r in d)
 assert s["primary_route_requirements"]+s["supplemental_vacancy_requirements"]==len(req)
 assert all(r["required_coordinate_answers"]=="UNRESOLVED" and r["compiler_action"]=="REFUSE_COORDINATE_BINDING" for r in req)
 assert all(r["compiler_binding"]=="REFUSED" and not r["exact_contract_selected"] for r in d)
 assert s["coordinate_answers_supplied"]==s["refusal_precedence_profiles_supplied"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["semantic_seam_appraisals"]==s["exact_contracts_selected"]==s["compiler_bindings_permitted"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
 print(f"PASS library coordinate binding projection: {len(req)} exact axis requirements wire into {len(d)} refusing compiler dockets; no semantic or exact-contract gate is bypassed");return 0
if __name__=="__main__":raise SystemExit(main())
