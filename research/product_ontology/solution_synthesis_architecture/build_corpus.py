#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from source_model import (
    ARCHITECTURE,
    ARTIFACT_CLASSES,
    BINDING_PHASES,
    BUILD_POLICIES,
    COMPONENTS,
    DATA_ANALYTICS_PLANES,
    FRONTIER_CLASSES,
    IR_JOIN_RULES,
    IR_STAGES,
    LAWS,
    MODES,
    OUTCOMES,
    PYTHON_TOOLCHAIN_ROLES,
    TRANSFORMS,
)

HERE=Path(__file__).resolve().parent
def dump(name, rows, key):
    text="".join(json.dumps(row,sort_keys=True)+"\n" for row in sorted(rows,key=lambda x:x[key]))
    (HERE/name).write_text(text)
    return {"path":name,"records":len(rows),"sha256":hashlib.sha256(text.encode()).hexdigest()}
def main():
    components=[{"component_id":f"component.synthesis.{i}","name":n,"responsibility":r,"operations":o,"forbidden_ownership":f,"status":"PROPOSED_UNRATIFIED","completion_claim":False} for i,n,r,o,f in COMPONENTS]
    modes=[{"mode_id":f"mode.synthesis.{i}","entry_condition":e,"primary_component_ref":f"component.synthesis.{c}","outcome":o,"completion_claim":False} for i,e,c,o in MODES]
    stages=[{"ir_id":f"ir.synthesis.{i}","name":n,"semantic_content":c,"authority":a,"immutable_edition_required":True,"completion_claim":False} for i,n,c,a in IR_STAGES]
    transforms=[{"transform_id":f"transform.synthesis.{i}","input_ir_ref":f"ir.synthesis.{a}","output_ir_ref":f"ir.synthesis.{b}","mechanism":m,"typed_refusal":r,"required_receipt_fields":["input_edition","output_edition","rule_editions","decisions","information_loss","residuals","evidence_refs","replay_digest"],"completion_claim":False} for i,a,b,m,r in TRANSFORMS]
    joins=[{"join_rule_id":f"join.synthesis.{i}","target_ir_ref":f"ir.synthesis.{target}","required_ir_refs":[f"ir.synthesis.{ref}" for ref in refs],"closure_law":law,"completion_claim":False} for i,target,refs,law in IR_JOIN_RULES]
    frontier=[{"frontier_class_id":f"frontier.synthesis.{i}","definition":d,"owner_component_ref":f"component.synthesis.{c}","completion_claim":False} for i,d,c in FRONTIER_CLASSES]
    phases=[{"binding_phase_id":f"phase.synthesis.{i}","typical_decisions":d,"completion_claim":False} for i,d in BINDING_PHASES]
    laws=[{"law_id":f"law.synthesis.{i}","statement":s,"status":"CONSTITUTIONAL_CANDIDATE","completion_claim":False} for i,s in LAWS]
    outcomes=[{"outcome_id":f"outcome.synthesis.{i}","required_fields":f,"meaning":m,"completion_claim":False} for i,f,m in OUTCOMES]
    planes=[{"plane_id":f"plane.data-analytics.{i}","name":name,"responsibility":responsibility,"corpus_prefixes":prefixes,"ir_refs":[f"ir.synthesis.{ref}" for ref in refs],"classification_law":"coverage_plane_not_automatically_product_context_library_compiler_pass_or_deployment_unit","completion_claim":False} for i,name,responsibility,prefixes,refs in DATA_ANALYTICS_PLANES]
    python_roles=[{"python_role_id":f"python-role.corpus.{i}","responsibility":responsibility,"guardrail":guardrail,"produced_artifact_kinds":artifacts,"semantic_authority":False,"completion_claim":False} for i,responsibility,guardrail,artifacts in PYTHON_TOOLCHAIN_ROLES]
    artifacts=[{"artifact_class_id":f"artifact-class.corpus.{i}","meaning":meaning,"producer_role":producer,"authority_semantics":authority,"mutation_model":mutation,"completion_claim":False} for i,meaning,producer,authority,mutation in ARTIFACT_CLASSES]
    policies=[{"build_policy_id":f"policy.corpus-build.{i}","law":law,"completion_claim":False} for i,law in BUILD_POLICIES]
    files=[dump("components.jsonl",components,"component_id"),dump("operating-modes.jsonl",modes,"mode_id"),dump("ir-stages.jsonl",stages,"ir_id"),dump("ir-transforms.jsonl",transforms,"transform_id"),dump("ir-join-rules.jsonl",joins,"join_rule_id"),dump("data-analytics-planes.jsonl",planes,"plane_id"),dump("python-toolchain-roles.jsonl",python_roles,"python_role_id"),dump("artifact-classes.jsonl",artifacts,"artifact_class_id"),dump("build-policies.jsonl",policies,"build_policy_id"),dump("compilation-frontier.jsonl",frontier,"frontier_class_id"),dump("binding-phases.jsonl",phases,"binding_phase_id"),dump("laws.jsonl",laws,"law_id"),dump("outcomes.jsonl",outcomes,"outcome_id")]
    (HERE/"architecture.json").write_text(json.dumps({**ARCHITECTURE,"component_refs":sorted(r["component_id"] for r in components),"mode_refs":sorted(r["mode_id"] for r in modes),"ir_refs":sorted(r["ir_id"] for r in stages),"completion_claim":False},indent=2,sort_keys=True)+"\n")
    summary={"architecture_patterns":1,"components":len(components),"operating_modes":len(modes),"ir_stages":len(stages),"ir_transforms":len(transforms),"ir_join_rules":len(joins),"data_analytics_planes":len(planes),"python_toolchain_roles":len(python_roles),"artifact_classes":len(artifacts),"build_policies":len(policies),"frontier_classes":len(frontier),"binding_phases":len(phases),"constitutional_laws":len(laws),"outcomes":len(outcomes),"products_promoted":0,"completion_claim":False}
    (HERE/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    (HERE/"manifest.json").write_text(json.dumps({"files":files,"summary":summary},indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))
if __name__=="__main__": main()
