#!/usr/bin/env python3
"""Validate platform/control product adjudication and compiler projections."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from build_bundle import HERE, OUTPUTS, load_source, materialize
from source_model import SOURCE, AXES, source_bytes
from solution_compiler_enrichment import (
    AUTOMATION,
    BINDER_REGISTRY,
    CENTRAL_REGISTRY,
    CODEGEN_REGISTRY,
    COMPILER_LIBRARIES,
    CONFORMANCE_REGISTRY,
    DDD_FIELDS,
    IMPLEMENTATION_REGISTRY,
    IR_REGISTRY,
    MCA_REGISTRY,
    PRODUCT as COMPILER_PRODUCT,
)
from platform_product_enrichment import (
    AUTOMATION as PRODUCT_AUTOMATION,
    DEVELOPER,
    DEVELOPER_LIBRARIES,
    FINOPS,
    FINOPS_LIBRARIES,
    PRODUCT_LIBRARIES,
    PRODUCTS as ENRICHED_PRODUCTS,
    RUNTIME,
    RUNTIME_LIBRARIES,
)
from platform_estate_enrichment import ESTATE, ESTATE_LIBRARIES


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def identity(row: dict) -> str:
    for key in ("source_id","artifact_id","decision_id","meaning_id","library_id","requirement_id","offer_id","relation_id","legacy_ref","test_id","binding_map_id","gap_id","dossier_id","kind"):
        if key in row:
            return str(row[key])
    return "<missing>"


def main() -> int:
    errors: list[str] = []
    require = lambda ok, msg: None if ok else errors.append(msg)
    require(SOURCE.is_file() and SOURCE.read_bytes()==source_bytes(),"source.json differs from source_model.py")
    source=load_source(); payloads,expected_manifest=materialize(source)
    manifest=json.loads((HERE/"manifest.json").read_text())
    require(manifest==expected_manifest,"manifest projection drift")
    for filename,content in payloads.items(): require((HERE/filename).is_file() and (HERE/filename).read_bytes()==content,f"stale {filename}")
    for filename,digest in manifest.get("file_sha256",{}).items():
        if (HERE/filename).is_file(): require(hashlib.sha256((HERE/filename).read_bytes()).hexdigest()==digest,f"digest mismatch {filename}")
    data={section:rows(HERE/filename) for section,filename in OUTPUTS.items()}
    registry=rows(HERE/"registry.jsonl")
    require(Counter(row["record_kind"] for row in registry)==Counter(manifest["counts"]),"manifest counts differ")
    keys=[(row["record_kind"],identity(row)) for row in registry]; require(len(keys)==len(set(keys)),"duplicate identity")
    evidence={r["source_id"]:r for r in data["sources"]}; artifacts={r["artifact_id"]:r for r in data["artifacts"]}; libraries={r["library_id"]:r for r in data["libraries"]}; nodes=set(artifacts)|set(libraries)
    require(len(evidence)>=35,"source floor not met"); require(all(r.get("claim") and r.get("scope_limit") and r.get("uri","").startswith("https://") for r in evidence.values()),"unscoped evidence")
    for ident,row in artifacts.items():
        require(all(ref in evidence for ref in row.get("evidence_refs",[])),f"bad evidence {ident}")
        owner=row.get("semantic_owner_ref")
        if owner: require(owner in artifacts and artifacts[owner]["kind"]=="semantic_contract",f"bad owner {ident}")
        if row["kind"]=="product": require(row["adoption_unit"] and row["operated"],f"product flags {ident}")
        if row["kind"] in {"suite","architecture_pattern"}: require(owner is None,f"pattern/suite owns meaning {ident}")
    products={i for i,r in artifacts.items() if r["kind"]=="product"}
    require(products=={"product.solution_compiler","product.data_product_developer_platform","product.runtime_resource_control","product.finops_allocation",ESTATE},"product set drift")
    decisions={r["decision_id"]:r for r in data["boundary_decisions"]}; decided=set()
    for ident,row in decisions.items():
        require(row["subject_ref"] in nodes,f"bad subject {ident}"); require(all(ref in evidence for ref in row["evidence_refs"]),f"bad decision evidence {ident}")
        if row["subject_ref"] in products:
            decided.add(row["subject_ref"]); require(set(row["split_test"])==set(AXES),f"split axes {ident}")
            total=sum(cell["score"] for cell in row["split_test"].values()); require(all(cell["score"] in {0,1,2} and cell["evidence_refs"] for cell in row["split_test"].values()),f"split cells {ident}")
            if row["disposition"]=="strong_product_candidate": require(17<=total<=20,f"strong score {ident}:{total}")
            else: require(13<=total<=16,f"presumptive score {ident}:{total}")
    require(decided==products,"unadjudicated product")
    for ident in {"decision.platform.provider_qualification","decision.platform.operations","decision.platform.ai_prefix"}: require(ident in decisions,f"missing decision {ident}")
    graph:dict[str,list[str]]=defaultdict(list)
    for ident,row in libraries.items():
        require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"]=="semantic_contract",f"library owner {ident}")
        for field in ("provides","types","operations","decisions","invariants","refusals"): require(bool(row.get(field)),f"empty {field} {ident}")
        for ref in row["provides"]: require(ref in artifacts and artifacts[ref]["kind"]=="capability",f"bad capability {ident}:{ref}")
        for ref in row["dependencies"]: require(ref in libraries,f"bad dependency {ident}:{ref}"); graph[ident].append(ref)
    visiting:set[str]=set(); visited:set[str]=set()
    def visit(node:str)->None:
        if node in visiting: errors.append(f"library cycle {node}"); return
        if node in visited: return
        visiting.add(node)
        for dep in graph[node]: visit(dep)
        visiting.remove(node); visited.add(node)
    for node in libraries: visit(node)
    for row in data["ownership"]: require(row["owner_ref"] in artifacts and artifacts[row["owner_ref"]]["kind"]=="semantic_contract",f"bad ownership {row['meaning_id']}")
    for row in data["requirements"]: require(row["consumer_ref"] in nodes and row["capability_ref"] in artifacts and row["status"]=="unbound",f"bad requirement {row['requirement_id']}")
    for row in data["offers"]: require(row["provider_ref"] in artifacts and artifacts[row["provider_ref"]]["kind"]=="implementation" and row["qualified_implementation_count"]==0 and row["portable"] is False,f"bad offer {row['offer_id']}")
    for row in data["relations"]: require(row["from_ref"] in nodes and row["to_ref"] in nodes,f"bad relation {row['relation_id']}")
    for row in data["crosswalks"]: require(all(ref in nodes for ref in row["canonical_refs"]),f"bad crosswalk {row['legacy_ref']}")
    repository_root = HERE.parents[3]
    registry_specs = {
        CENTRAL_REGISTRY: "library_id",
        IMPLEMENTATION_REGISTRY: "id",
        IR_REGISTRY: "library_id",
        MCA_REGISTRY: "id",
        BINDER_REGISTRY: "id",
        CONFORMANCE_REGISTRY: "id",
        CODEGEN_REGISTRY: "boundary_id",
    }
    concrete_by_origin: dict[str, set[str]] = {}
    for origin, id_field in registry_specs.items():
        path = repository_root / origin
        require(path.is_file(), f"missing compiler registry {origin}")
        if path.is_file():
            concrete_by_origin[origin] = {str(row[id_field]) for row in rows(path)}
    maps={r["binding_map_id"]:r for r in data["binding_maps"]}; gaps={r["gap_id"]:r for r in data["binding_gaps"]}
    require(len(maps)==len(libraries)==58,"one map per library required"); require({r["abstract_library_ref"] for r in maps.values()}==set(libraries),"map coverage")
    for ident,row in maps.items():
        refs = set(row["concrete_library_refs"])
        origins = row.get("concrete_library_origins", {})
        require(set(origins) == refs, f"compiler origin coverage {ident}")
        for ref, origin in origins.items():
            require(origin in concrete_by_origin, f"unknown compiler registry {ident}:{origin}")
            if origin in concrete_by_origin:
                require(ref in concrete_by_origin[origin], f"unknown compiler library {ident}:{ref}@{origin}")
        if row["compiler_disposition"]=="blocked_typed_gap": require(row.get("gap_ref") in gaps and not row["concrete_library_refs"],f"invalid gap map {ident}")
        else: require(row["compiler_disposition"]=="structurally_projected_unqualified" and row["concrete_library_refs"],f"invalid projected map {ident}")
        require(row["portable_offer"] is False,f"portable map {ident}")
    require(not gaps, "all platform/control structural library gaps must be closed")
    compiler = artifacts[COMPILER_PRODUCT]
    product_truth_fields = {
        "sovereign_question", "users", "harmed_parties", "jobs", "outcomes",
        "negative_mission", "lifecycle_states", "commands", "events", "invariants",
        "refusals", "automation_modality",
    }
    require(all(compiler.get(field) for field in product_truth_fields), "compiler product truth incomplete")
    require(compiler["status"] == "presumptive_product", "compiler product evidence overstated")
    require(compiler.get("automation_modality") == AUTOMATION, "compiler automation doctrine drift")
    compiler_libraries = {ident for ident,row in libraries.items() if COMPILER_PRODUCT in row.get("product_refs", [])}
    require(compiler_libraries == COMPILER_LIBRARIES, "compiler library attribution drift")
    compiler_maps = {row["abstract_library_ref"] for row in maps.values() if COMPILER_PRODUCT in row.get("product_refs", [])}
    require(compiler_maps == COMPILER_LIBRARIES, "compiler binding map attribution drift")
    require(not any(row["abstract_library_ref"] in COMPILER_LIBRARIES for row in gaps.values()), "compiler library has unresolved typed binding gap")
    compiler_requirements = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == COMPILER_PRODUCT}
    compiler_provides = {ref for ident in COMPILER_LIBRARIES for ref in libraries[ident]["provides"]}
    require(compiler_requirements <= compiler_provides, "compiler capability requirement lacks attributed library")
    product_library_expectations = {
        DEVELOPER: DEVELOPER_LIBRARIES,
        RUNTIME: RUNTIME_LIBRARIES,
        FINOPS: FINOPS_LIBRARIES,
        ESTATE: ESTATE_LIBRARIES,
    }
    require(PRODUCT_LIBRARIES == {DEVELOPER: DEVELOPER_LIBRARIES, RUNTIME: RUNTIME_LIBRARIES, FINOPS: FINOPS_LIBRARIES}, "product library constant drift")
    require(ENRICHED_PRODUCTS | {ESTATE} == set(product_library_expectations), "enriched product set drift")
    for product_ref, expected_libraries in product_library_expectations.items():
        product = artifacts[product_ref]
        require(product.get("automation_modality") == PRODUCT_AUTOMATION, f"automation doctrine drift {product_ref}")
        actual_libraries = {ident for ident,row in libraries.items() if product_ref in row.get("product_refs", [])}
        require(actual_libraries == expected_libraries, f"product library attribution drift {product_ref}")
        actual_maps = {row["abstract_library_ref"] for row in maps.values() if product_ref in row.get("product_refs", [])}
        require(actual_maps == expected_libraries, f"product map attribution drift {product_ref}")
        required = {row["capability_ref"] for row in data["requirements"] if row["consumer_ref"] == product_ref}
        provided = {capability for ident in expected_libraries for capability in libraries[ident]["provides"]}
        require(required <= provided, f"product capability requirement lacks attributed library {product_ref}:{sorted(required-provided)}")
    attributed_sets=list(product_library_expectations.values())
    require(all(not (left & right) for index,left in enumerate(attributed_sets) for right in attributed_sets[index+1:]), "product library ownership overlaps")
    require("library.platform.allocation_lease" not in libraries, "collapsed reservation/allocation/lease facade returned")
    require({"library.platform.runtime.reservation_ledger","library.platform.runtime.allocation_ledger","library.platform.runtime.lease_fencing"} <= RUNTIME_LIBRARIES, "reservation allocation lease split missing")
    require("library.platform.cost_normalization" in FINOPS_LIBRARIES, "FinOps normalization seam missing")
    telemetry_map = next((row for row in maps.values() if row["abstract_library_ref"] == "library.platform.telemetry"), None)
    require(telemetry_map is not None and len(telemetry_map.get("concrete_library_refs", [])) == 10, "exact ten-boundary telemetry projection missing")
    require(telemetry_map.get("product_refs") == [] and telemetry_map.get("portable_offer") is False, "cross-cutting telemetry projection must remain unqualified and unattributed")
    focus_map = next((row for row in maps.values() if row["abstract_library_ref"] == "library.platform.cost_normalization"), None)
    require(focus_map is not None and focus_map.get("concrete_library_refs") == ["library.platform-commercial-support.focus-normalization"] and focus_map.get("product_refs") == [FINOPS], "exact FOCUS normalization projection missing")
    dossiers = {row["product_ref"]: row for row in data["ddd_dossiers"]}
    require(set(dossiers) == products, "one DDD dossier per product required")
    for product_ref in products:
        dossier = dossiers.get(product_ref, {})
        require(dossier.get("status") == "candidate_not_ratified", f"DDD status overstated {product_ref}")
        require(set(dossier.get("strategic_and_tactical_ddd", {})) == DDD_FIELDS, f"DDD 29-field coverage drift {product_ref}")
        require(all(dossier.get("strategic_and_tactical_ddd", {}).get(field) for field in DDD_FIELDS), f"DDD contains empty field {product_ref}")
    negatives={r["test_id"] for r in data["negative_tests"]}; require(len(negatives)>=20 and {"negative.ai_prefix","negative.agent_authority","negative.plan_effect","negative.operations_product"}.issubset(negatives),"negative twins missing")
    require({"negative.compiler.domain_owner","negative.compiler.name_binding","negative.compiler.lowering_optimization","negative.compiler.hard_soft","negative.compiler.plan_acceptance","negative.compiler.agent_completion"}.issubset(negatives), "compiler negative twins missing")
    require(manifest["derived"]["qualified_offers"]==0 and manifest["derived"]["portable_offers"]==0,"qualification fabricated")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(f"PASS platform/control adjudication: {len(evidence)} sources; {len(artifacts)} artifacts; {len(products)} product candidates; {len(libraries)} library contracts ({len(DEVELOPER_LIBRARIES)} developer, {len(RUNTIME_LIBRARIES)} runtime, {len(FINOPS_LIBRARIES)} FinOps, {len(ESTATE_LIBRARIES)} estate, {len(COMPILER_LIBRARIES)} compiler); {len(data['requirements'])} unbound requirements; {len(data['offers'])} unqualified offers; {len(maps)} compiler binding maps; 5 complete 29-field product DDDs; {len(gaps)} typed binding gaps; {len(data['crosswalks'])} legacy crosswalks")
    return 0


if __name__=="__main__": raise SystemExit(main())
