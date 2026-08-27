#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def rows(name): return [json.loads(x) for x in (HERE/name).read_text().splitlines() if x.strip()]
def main():
    architecture=json.loads((HERE/"architecture.json").read_text()); manifest=json.loads((HERE/"manifest.json").read_text())
    components=rows("components.jsonl"); modes=rows("operating-modes.jsonl"); stages=rows("ir-stages.jsonl"); transforms=rows("ir-transforms.jsonl"); joins=rows("ir-join-rules.jsonl"); planes=rows("data-analytics-planes.jsonl"); python_roles=rows("python-toolchain-roles.jsonl"); artifacts=rows("artifact-classes.jsonl"); policies=rows("build-policies.jsonl"); frontier=rows("compilation-frontier.jsonl"); phases=rows("binding-phases.jsonl"); laws=rows("laws.jsonl"); outcomes=rows("outcomes.jsonl")
    component_ids={r["component_id"] for r in components}; ir_ids={r["ir_id"] for r in stages}
    assert architecture["kind"]=="ARCHITECTURE_PATTERN_NOT_PRODUCT" and architecture["completion_claim"] is False
    assert len(components)==6 and len(component_ids)==6 and all(r["forbidden_ownership"] for r in components)
    assert len(modes)==3 and all(r["primary_component_ref"] in component_ids for r in modes)
    required_ir_suffixes={"business-intent-ir","domain-context-ir","semantic-intent-ir","source-estate-requirement-ir","analytical-design-ir","product-composition-ir","capability-requirement-ir","contract-graph-ir","application-behavior-ir","logical-dataflow-ir","experience-delivery-ir","authority-effect-ir","implementation-offer-ir","qualification-evidence-ir","physical-binding-ir","deployment-blueprint-ir","evidence-acceptance-ir"}
    assert {r["ir_id"].removeprefix("ir.synthesis.") for r in stages}==required_ir_suffixes and all(r["authority"] for r in stages)
    assert len(transforms)>=20 and all(r["input_ir_ref"] in ir_ids and r["output_ir_ref"] in ir_ids and len(r["required_receipt_fields"])==8 for r in transforms)
    assert len(joins)>=8 and all(r["target_ir_ref"] in ir_ids and set(r["required_ir_refs"])<=ir_ids and r["closure_law"] for r in joins)
    adjacency={ref:set() for ref in ir_ids}; indegree={ref:0 for ref in ir_ids}
    for transform in transforms:
        source=transform["input_ir_ref"]; target=transform["output_ir_ref"]
        if target not in adjacency[source]: adjacency[source].add(target); indegree[target]+=1
    ready=sorted(ref for ref,degree in indegree.items() if degree==0); visited=[]
    while ready:
        current=ready.pop(0); visited.append(current)
        for target in sorted(adjacency[current]):
            indegree[target]-=1
            if indegree[target]==0: ready.append(target); ready.sort()
    assert len(visited)==len(ir_ids), "IR transform graph contains a cycle"
    reachable={"ir.synthesis.business-intent-ir"}; frontier_reachable=list(reachable)
    while frontier_reachable:
        current=frontier_reachable.pop()
        for target in adjacency[current]:
            if target not in reachable: reachable.add(target); frontier_reachable.append(target)
    assert reachable==ir_ids, f"IR stages not reachable from business intent: {sorted(ir_ids-reachable)}"
    physical_join=next(r for r in joins if r["target_ir_ref"]=="ir.synthesis.physical-binding-ir")
    assert {"ir.synthesis.implementation-offer-ir","ir.synthesis.qualification-evidence-ir","ir.synthesis.authority-effect-ir"}<=set(physical_join["required_ir_refs"])
    acceptance_join=next(r for r in joins if r["target_ir_ref"]=="ir.synthesis.evidence-acceptance-ir")
    assert "ir.synthesis.deployment-blueprint-ir" in acceptance_join["required_ir_refs"]
    plane_ids={r["plane_id"] for r in planes}
    assert len(planes)>=15 and len(plane_ids)==len(planes)
    assert {"plane.data-analytics.source-acquisition","plane.data-analytics.data-semantics-contracts","plane.data-analytics.movement-transformation","plane.data-analytics.persistence-representation","plane.data-analytics.compute-query-runtime","plane.data-analytics.analytics-methods","plane.data-analytics.experience-presentation","plane.data-analytics.decision-activation"}<=plane_ids
    assert all(r["corpus_prefixes"] and set(r["ir_refs"])<=ir_ids and r["classification_law"]=="coverage_plane_not_automatically_product_context_library_compiler_pass_or_deployment_unit" for r in planes)
    python_role_ids={r["python_role_id"] for r in python_roles}
    assert len(python_roles)>=9 and len(python_role_ids)==len(python_roles) and all(r["semantic_authority"] is False for r in python_roles)
    assert {"python-role.corpus.evidence-collector","python-role.corpus.canonical-builder","python-role.corpus.validator","python-role.corpus.build-orchestrator","python-role.corpus.reference-runtime-implementation"}<=python_role_ids
    artifact_ids={r["artifact_class_id"] for r in artifacts}
    assert len(artifacts)>=11 and len(artifact_ids)==len(artifacts)
    assert {"artifact-class.corpus.raw-evidence-snapshot","artifact-class.corpus.authored-candidate-record","artifact-class.corpus.authority-decision","artifact-class.corpus.derived-projection","artifact-class.corpus.execution-receipt","artifact-class.corpus.qualification-appraisal-receipt","artifact-class.corpus.historical-snapshot"}<=artifact_ids
    assert len(policies)>=8 and any("Historical snapshots validate exact frozen counts" in r["law"] for r in policies) and any("Python is the research/build workbench" in r["law"] for r in policies)
    assert len(frontier)==5 and all(r["owner_component_ref"] in component_ids for r in frontier)
    assert len(phases)==7 and all(r["typical_decisions"] for r in phases)
    assert len(laws)>=12 and {r["statement"] for r in laws}>={"compiler output != business truth or authority","compiled blueprint != applied physical state","product lifecycle owner != sum of required libraries"}
    assert {r["outcome_id"] for r in outcomes}=={"outcome.synthesis.compiled-solution","outcome.synthesis.incomplete-solution"}
    assert all(r["completion_claim"] is False for collection in (components,modes,stages,transforms,joins,planes,python_roles,artifacts,policies,frontier,phases,laws,outcomes) for r in collection)
    for claim in manifest["files"]:
        p=HERE/claim["path"]; assert len(rows(claim["path"]))==claim["records"] and hashlib.sha256(p.read_bytes()).hexdigest()==claim["sha256"]
    print(f"PASS solution-synthesis architecture: {len(components)} bounded mechanisms, {len(modes)} modes, {len(stages)} IR stages, {len(transforms)} typed transforms, {len(joins)} hypergraph joins, {len(planes)} data/analytics planes, {len(python_roles)} Python toolchain roles and {len(artifacts)} artifact classes; compiler remains a kernel and Python remains a governed corpus workbench")
    return 0
if __name__=="__main__": raise SystemExit(main())
