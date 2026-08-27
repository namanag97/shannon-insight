#!/usr/bin/env python3
"""Validate cross-axis coordinate coverage without converting coverage into closure."""
import hashlib,json
from build_cross_axis_coordinate_audit import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 m=json.loads((HERE/"manifest.json").read_text())
 for n,c in m["files"].items():d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
 b=build();s=b["summary"]
 assert len(b["inventory"])==len({r["axis"] for r in b["inventory"]})==16
 assert len(b["quotient"])==len({r["audit_id"] for r in b["quotient"]})
 assert all(r["lossless_factorization_identity_preserved"] for r in b["quotient"])
 assert sum(r["member_count"] for r in b["quotient"])==s["exact_coordinate_routes"]
 assert s["primary_coordinate_routes"]+s["supplemental_structural_routes"]==s["exact_coordinate_routes"]
 assert s["unrouted_member_axis_cells"]==0
 assert s["full_primary_member_route_packages"]==10 and s["partial_primary_member_route_packages"]==6 and s["full_combined_member_route_packages"]==16
 assert s["fully_routed_quotients"]+s["partially_routed_quotients"]+s["unrouted_quotients"]==len(b["quotient"])
 assert s["cross_axis_seam_obligations"]==s["structural_contradiction_tests_executed"]==20
 assert s["structural_negative_twins_passed"]==120 and s["semantic_contradiction_appraisals_executed"]==0
 assert s["native_normalized_compiler_surface_axes"]==7 and s["projected_normalized_compiler_surface_axes"]==9
 assert s["normalized_compiler_surface_axes"]==16 and s["compiler_surface_normalization_gaps"]==0
 assert s["compiler_lowering_ready_axes"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["canonical_gaps_closed"]==0
 assert not s["completion_claim"]
 print(f"PASS cross-axis coordinate audit: all {s['exact_coordinate_routes']} cells route into 16 normalized compiler surfaces and {s['structural_negative_twins_passed']} seam negative twins fail closed; semantic appraisal and decisions remain open");return 0
if __name__=="__main__":raise SystemExit(main())
