#!/usr/bin/env python3
"""Fail-closed validation for the SOTA presentation-semantics extension."""
from __future__ import annotations
import hashlib, json, re
from collections import Counter
from pathlib import Path
from build import HERE, OUTPUTS, bridges, jsonl, summary

ID=re.compile(r"^[a-z][a-z0-9_]*(?:[.-][a-z0-9_]+)+$")

def rows(name):
    return [json.loads(x) for x in (HERE/name).read_text(encoding="utf-8").splitlines() if x.strip()]

def main():
    errors=[]
    req=lambda ok,msg: None if ok else errors.append(msg)
    expected={k:list(v) for k,v in OUTPUTS.items()}
    expected["canonical-bridges.jsonl"]=bridges()
    manifest=json.loads((HERE/"manifest.json").read_text())
    for name,data in expected.items():
        text=jsonl(data)
        req((HERE/name).is_file() and (HERE/name).read_text()==text,f"stale {name}")
        claim=manifest["files"].get(name,{})
        req(claim.get("records")==len(data),f"record count drift {name}")
        req(claim.get("sha256")==hashlib.sha256(text.encode()).hexdigest(),f"digest drift {name}")
    s=summary(expected,expected["canonical-bridges.jsonl"])
    req(json.loads((HERE/"summary.json").read_text())==s,"summary drift")
    req(s["benchmark_products"]>=65,"benchmark saturation floor not met")
    req(s["benchmark_archetypes"]>=18,"archetype saturation floor not met")
    req(s["provider_feature_observations"]>=400,"feature observation floor not met")
    req(s["question_intents"]>=100,"intent floor not met")
    req(s["visual_patterns"]>=170,"visual pattern floor not met")
    req(s["specialist_experiences"]>=20,"specialist floor not met")
    req(s["interaction_contracts"]>=50,"interaction floor not met")
    req(s["candidate_library_seams"]>=60,"library seam floor not met")
    req(s["vertical_acceptance_cases"]>=40 and s["industries"]>=30,"vertical pressure-test floor not met")
    req(s["negative_tests"]>=70,"negative twin floor not met")
    req(s["qualified_providers"]==s["ratified_contracts"]==s["executed_vertical_acceptance_cases"]==0,"fabricated authority")
    srcids={r["source_id"] for r in expected["sources.jsonl"]}
    for r in expected["benchmarks.jsonl"]:
        req(r["evidence_ref"] in srcids,f"missing benchmark evidence {r['benchmark_id']}")
        req(r["semantic_dispatch_allowed"] is False,f"provider dispatch enabled {r['benchmark_id']}")
    visualids={r["visual_pattern_id"] for r in expected["visual-patterns.jsonl"]}
    for r in expected["question-intents.jsonl"]:
        req(bool(r["candidate_visual_refs"]),f"empty intent candidates {r['intent_id']}")
        req(set(r["candidate_visual_refs"])<=visualids,f"unknown visual route {r['intent_id']}")
    for r in expected["interaction-contracts.jsonl"]:
        req(r["business_effect_authority"] is False,f"interaction gained effect authority {r['interaction_id']}")
    for r in expected["canonical-bridges.jsonl"]:
        req(r["compiler_binding"]=="REFUSED_UNTIL_PARENT_RATIFICATION_AND_QUALIFIED_OFFER",f"dishonest bridge {r['bridge_id']}")
    trials=expected["saturation-trials.jsonl"]
    req(trials[-1]["new_root_families"]==0,"late saturation probe still yields root")
    for name,data in expected.items():
        for r in data:
            ident=next((str(v) for k,v in r.items() if k.endswith("_id") and isinstance(v,str)),None)
            if ident: req(bool(ID.fullmatch(ident)),f"invalid id {ident}")
            req(r.get("completion_claim") is False,f"completion claim found {ident or name}")
    if errors:
        print("\n".join("ERROR: "+e for e in errors)); return 1
    print("PASS presentation SOTA semantics: "
          f"{s['sources']} sources; {s['benchmark_products']} products; {s['provider_feature_observations']} features; "
          f"{s['question_intents']} intents; {s['visual_patterns']} patterns; {s['specialist_experiences']} specialists; "
          f"{s['candidate_library_seams']} seams; {s['vertical_acceptance_cases']} vertical cases; "
          "0 ratified contracts/providers/vertical executions")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
