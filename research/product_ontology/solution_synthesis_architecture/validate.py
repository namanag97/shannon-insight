#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def rows(name): return [json.loads(x) for x in (HERE/name).read_text().splitlines() if x.strip()]
def main():
    architecture=json.loads((HERE/"architecture.json").read_text()); manifest=json.loads((HERE/"manifest.json").read_text())
    components=rows("components.jsonl"); modes=rows("operating-modes.jsonl"); stages=rows("ir-stages.jsonl"); transforms=rows("ir-transforms.jsonl"); frontier=rows("compilation-frontier.jsonl"); phases=rows("binding-phases.jsonl"); laws=rows("laws.jsonl"); outcomes=rows("outcomes.jsonl")
    component_ids={r["component_id"] for r in components}; ir_ids={r["ir_id"] for r in stages}
    assert architecture["kind"]=="ARCHITECTURE_PATTERN_NOT_PRODUCT" and architecture["completion_claim"] is False
    assert len(components)==6 and len(component_ids)==6 and all(r["forbidden_ownership"] for r in components)
    assert len(modes)==3 and all(r["primary_component_ref"] in component_ids for r in modes)
    assert len(stages)==11 and len(ir_ids)==11 and all(r["authority"] for r in stages)
    assert len(transforms)==11 and all(r["input_ir_ref"] in ir_ids and r["output_ir_ref"] in ir_ids and len(r["required_receipt_fields"])==8 for r in transforms)
    assert len(frontier)==5 and all(r["owner_component_ref"] in component_ids for r in frontier)
    assert len(phases)==7 and all(r["typical_decisions"] for r in phases)
    assert len(laws)>=12 and {r["statement"] for r in laws}>={"compiler output != business truth or authority","compiled blueprint != applied physical state","product lifecycle owner != sum of required libraries"}
    assert {r["outcome_id"] for r in outcomes}=={"outcome.synthesis.compiled-solution","outcome.synthesis.incomplete-solution"}
    assert all(r["completion_claim"] is False for collection in (components,modes,stages,transforms,frontier,phases,laws,outcomes) for r in collection)
    for claim in manifest["files"]:
        p=HERE/claim["path"]; assert len(rows(claim["path"]))==claim["records"] and hashlib.sha256(p.read_bytes()).hexdigest()==claim["sha256"]
    print(f"PASS solution-synthesis architecture: {len(components)} bounded mechanisms, {len(modes)} modes, {len(stages)} IR stages, {len(transforms)} typed transforms, {len(frontier)} compilation-frontier classes, {len(phases)} binding phases and {len(laws)} constitutional laws; compiler remains a kernel, not a universal authority")
    return 0
if __name__=="__main__": raise SystemExit(main())
