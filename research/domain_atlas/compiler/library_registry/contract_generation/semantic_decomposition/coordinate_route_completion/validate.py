#!/usr/bin/env python3
"""Validate exact supplemental routing while preserving all evidence and decision vacancies."""
import hashlib,json
from build_coordinate_route_completion import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 m=json.loads((HERE/"manifest.json").read_text())
 for n,c in m["files"].items():d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
 b=build();s=b["summary"];routes=b["routes"]
 assert len(routes)==len({(r["library_ref"],r["axis"]) for r in routes})
 assert len(b["axis_rows"])==6 and all(r["combined_member_routes"]==r["expected_member_axis_cells"] and not r["remaining_unrouted_member_refs"] for r in b["axis_rows"])
 assert s["existing_primary_routes"]+s["supplemental_routes"]==s["combined_routes_in_partial_axes"]
 assert s["all_axis_existing_primary_routes"]+s["supplemental_routes"]==s["all_axis_combined_routes"]==s["all_axis_expected_member_cells"]
 assert all(r["source_evidence_binding"]=="UNRESOLVED" and r["coordinate_answers"]=="NOT_SUPPLIED" for r in routes)
 assert s["source_evidence_bindings_supplied"]==s["coordinate_answers_supplied"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
 print(f"PASS coordinate route completion: {len(routes)} structural vacancy routes complete all {s['all_axis_expected_member_cells']} member-axis cells without supplying evidence, answers, applicability, ownership or closure");return 0
if __name__=="__main__":raise SystemExit(main())
