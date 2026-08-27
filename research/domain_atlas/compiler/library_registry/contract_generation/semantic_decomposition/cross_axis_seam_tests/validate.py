#!/usr/bin/env python3
"""Validate cross-axis fail-closed negative twins and preserve semantic vacancies."""
import hashlib,json
from build_cross_axis_seam_tests import HERE,build,outputs
def main():
 for n,t in outputs().items():assert (HERE/n).is_file(),f"missing {n}";assert (HERE/n).read_text()==t,f"stale {n}"
 m=json.loads((HERE/"manifest.json").read_text())
 for n,c in m["files"].items():d=(HERE/n).read_bytes();assert len(d)==c["bytes"] and hashlib.sha256(d).hexdigest()==c["sha256"]
 b=build();s=b["summary"]
 assert len(b["results"])==len({r["seam_ref"] for r in b["results"]})==20
 assert len(b["cases"])==len({r["test_id"] for r in b["cases"]})==120
 assert all(r["negative_twins_executed"]==r["negative_twins_passed"]==6 for r in b["results"])
 assert all(r["test_result"]=="PASS_FAIL_CLOSED" and not r["semantic_evidence_executed"] and not r["owner_decision_executed"] for r in b["cases"])
 assert s["negative_twins_passed"]==120 and s["structural_contradiction_tests_executed"]==20 and s["structural_contradictions_detected"]==0
 assert s["semantic_seam_profiles_decided"]==s["semantic_contradiction_appraisals_executed"]==s["owner_decisions"]==s["compiler_bindings_permitted"]==s["canonical_gaps_closed"]==0 and not s["completion_claim"]
 print("PASS cross-axis seam tests: 120 negative twins across 20 seams fail closed; semantic contradiction appraisal and binding remain open");return 0
if __name__=="__main__":raise SystemExit(main())
