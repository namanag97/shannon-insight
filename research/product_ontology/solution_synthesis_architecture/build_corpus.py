#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from source_model import ARCHITECTURE, COMPONENTS, MODES, IR_STAGES, TRANSFORMS, FRONTIER_CLASSES, BINDING_PHASES, LAWS, OUTCOMES

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
    frontier=[{"frontier_class_id":f"frontier.synthesis.{i}","definition":d,"owner_component_ref":f"component.synthesis.{c}","completion_claim":False} for i,d,c in FRONTIER_CLASSES]
    phases=[{"binding_phase_id":f"phase.synthesis.{i}","typical_decisions":d,"completion_claim":False} for i,d in BINDING_PHASES]
    laws=[{"law_id":f"law.synthesis.{i}","statement":s,"status":"CONSTITUTIONAL_CANDIDATE","completion_claim":False} for i,s in LAWS]
    outcomes=[{"outcome_id":f"outcome.synthesis.{i}","required_fields":f,"meaning":m,"completion_claim":False} for i,f,m in OUTCOMES]
    files=[dump("components.jsonl",components,"component_id"),dump("operating-modes.jsonl",modes,"mode_id"),dump("ir-stages.jsonl",stages,"ir_id"),dump("ir-transforms.jsonl",transforms,"transform_id"),dump("compilation-frontier.jsonl",frontier,"frontier_class_id"),dump("binding-phases.jsonl",phases,"binding_phase_id"),dump("laws.jsonl",laws,"law_id"),dump("outcomes.jsonl",outcomes,"outcome_id")]
    (HERE/"architecture.json").write_text(json.dumps({**ARCHITECTURE,"component_refs":sorted(r["component_id"] for r in components),"mode_refs":sorted(r["mode_id"] for r in modes),"ir_refs":sorted(r["ir_id"] for r in stages),"completion_claim":False},indent=2,sort_keys=True)+"\n")
    summary={"architecture_patterns":1,"components":len(components),"operating_modes":len(modes),"ir_stages":len(stages),"ir_transforms":len(transforms),"frontier_classes":len(frontier),"binding_phases":len(phases),"constitutional_laws":len(laws),"outcomes":len(outcomes),"products_promoted":0,"completion_claim":False}
    (HERE/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    (HERE/"manifest.json").write_text(json.dumps({"files":files,"summary":summary},indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))
if __name__=="__main__": main()
