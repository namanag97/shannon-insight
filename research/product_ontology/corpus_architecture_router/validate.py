#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from build_router import HERE,ROOT,SELF_PREFIX,build,research_files

def rows(name): return [json.loads(x) for x in (HERE/name).read_text().splitlines() if x.strip()]
def main():
    built=build(); manifest=json.loads((HERE/"manifest.json").read_text()); summary=json.loads((HERE/"summary.json").read_text())
    for claim in manifest["files"]:
        p=HERE/claim["path"]; assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==claim["sha256"] and len(rows(claim["path"]))==claim["records"],f"stale {claim['path']}"
    architecture=ROOT/"research/product_ontology/solution_synthesis_architecture"
    components={r["component_id"] for r in rows_from(architecture/"components.jsonl")}; irs={r["ir_id"] for r in rows_from(architecture/"ir-stages.jsonl")}; frontiers={r["frontier_class_id"] for r in rows_from(architecture/"compilation-frontier.jsonl")}; phases={r["binding_phase_id"] for r in rows_from(architecture/"binding-phases.jsonl")}
    rules=built["rules"]; rule_ids={r["rule_id"] for r in rules}
    assert len(rule_ids)==len(rules) and all(r["component_ref"] in components and r["input_ir_ref"] in irs and r["output_ir_ref"] in irs and r["frontier_class_ref"] in frontiers and r["binding_phase_ref"] in phases for r in rules)
    assert all(set(r["dependency_rule_refs"])<=rule_ids for r in rules)
    actual_files={str(p.relative_to(ROOT)) for p in research_files()}; routed={r["path"] for r in built["files"]}
    assert not built["unrouted"] and not built["ambiguities"] and routed==actual_files
    assert len(routed)==len(built["files"]) and len({r["file_route_id"] for r in built["files"]})==len(built["files"])
    assert all(r["rule_id"] in rule_ids and r["route_precision"]=="EXPLICIT_PACKAGE_PREFIX" for r in built["files"])
    file_ids={r["file_route_id"] for r in built["files"]}; assert all(r["file_route_ref"] in file_ids for r in built["records"])
    assert all(r["identity_basis"].startswith("DECLARED_FIELD") for r in built["records"])
    routed_record_count=sum(r["record_count"] for r in built["files"])
    occurrence_only_count=sum(r["occurrence_only_count"] for r in built["files"])
    assert summary["routed_files"]==len(built["files"]) and summary["routed_record_occurrences"]==routed_record_count and summary["declared_identity_routes"]==len(built["records"]) and summary["occurrence_only_records"]==occurrence_only_count and summary["self_hosting_exclusion"]==SELF_PREFIX
    assert all(r["completion_claim"] is False for collection in (rules,built["packages"],built["files"],built["records"],built["identity_findings"],built["parse_findings"]) for r in collection)
    print(f"PASS corpus architecture router: {len(rules)} explicit package rules route all {len(built['files']):,} non-self research files and {routed_record_count:,} JSON/JSONL record occurrences; 0 ambiguous or unrouted files; {len(built['records']):,} declared identity routes and {occurrence_only_count:,} position-addressed occurrences are explicit")
    return 0
def rows_from(path): return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
if __name__=="__main__": raise SystemExit(main())
