#!/usr/bin/env python3
"""Validate common compiler-IR normalization without claiming semantic lowering readiness."""
import hashlib,json
from build_coordinate_compiler_ir_normalization import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 m=json.loads((HERE/"manifest.json").read_text())
 for n,c in m["files"].items():d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
 b=build();s=b["summary"];p=b["profiles"]
 assert len(p)==len({r["axis"] for r in p})==16
 assert s["native_common_surface_axes"]==7 and s["axis_native_projection_axes"]==9
 assert s["normalized_coordinate_surfaces"]==s["normalized_total_outcome_surfaces"]==s["normalized_refusal_surfaces"]==16
 assert all(r["required_coordinate_surface"] and r["typed_total_outcomes"] and r["compiler_refusals"] for r in p)
 assert all(not r["compiler_lowering_ready"] and r["refusal_precedence"]=="AXIS_OWNER_MUST_SUPPLY_EXACT_PRECEDENCE_PER_PROFILE" for r in p)
 assert s["refusal_precedence_profiles_supplied"]==s["member_coordinate_answers"]==s["member_applicability_decisions"]==s["owner_decisions"]==s["compiler_lowering_ready_axes"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
 print("PASS coordinate compiler-IR normalization: all 16 axes expose common structural coordinate/outcome/refusal surfaces; precedence, semantic decisions and lowering remain open");return 0
if __name__=="__main__":raise SystemExit(main())
