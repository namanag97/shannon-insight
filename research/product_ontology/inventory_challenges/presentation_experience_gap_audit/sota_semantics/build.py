#!/usr/bin/env python3
"""Build deterministic SOTA presentation-semantics projections nested under the canonical presentation audit."""
from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path
from typing import Any

from sources import SOURCES
from benchmarks import BENCHMARKS
from catalog import RESULT_KINDS, VISUAL_PATTERNS, SPECIALISTS
from intents import INTENTS
from contracts import INTERACTIONS, LIBRARY_SEAMS
from assurance import VERTICAL_CASES, NEGATIVE_TESTS, SATURATION_TRIALS

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
ROOT = HERE.parents[4]

OUTPUTS = {
    "sources.jsonl": SOURCES,
    "benchmarks.jsonl": BENCHMARKS,
    "analytical-result-kinds.jsonl": RESULT_KINDS,
    "question-intents.jsonl": INTENTS,
    "visual-patterns.jsonl": VISUAL_PATTERNS,
    "specialist-experiences.jsonl": SPECIALISTS,
    "interaction-contracts.jsonl": INTERACTIONS,
    "library-seams.jsonl": LIBRARY_SEAMS,
    "vertical-acceptance-cases.jsonl": VERTICAL_CASES,
    "negative-tests.jsonl": NEGATIVE_TESTS,
    "saturation-trials.jsonl": SATURATION_TRIALS,
}

def canonical(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(canonical(r) + "\n" for r in rows)

def load_parent_source():
    path=PARENT/"source_model.py"
    spec=importlib.util.spec_from_file_location("presentation_parent_source", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def bridges() -> list[dict[str, Any]]:
    parent=load_parent_source()
    parent_names={row[0]: row for row in parent.LIBRARY_CANDIDATES}
    aliases={
        "result_presentation_binding":"analytical_result_binding",
        "statistical_visual_grammar":"visual_encoding",
        "visual_fitness_constraints":"visual_encoding_fitness",
        "view_state_bookmark":"bookmark_view_state",
        "table_grid_model":"table_model",
        "report_snapshot":"report_snapshot_reducer",
        "export_delivery":"export_delivery_port",
        "localization_format":"localization_format",
        "renderer_adapter":"renderer_adapter",
        "presentation_resource_budget":"presentation_resource_budget",
        "presentation_usage_evidence":"presentation_usage_evidence",
        "embed_entitlement_projection":"embed_entitlement_projection",
        "accessibility_semantics":"accessibility_semantics",
        "accessible_task_equivalent":"accessible_task_equivalent",
        "uncertainty_encoding":"uncertainty_encoding",
        "missingness_encoding":"missingness_encoding",
        "provenance_disclosure":"provenance_disclosure",
        "annotation_collaboration":"annotation_collaboration",
        "selection_algebra":"selection_algebra",
        "drill_navigation":"drill_navigation",
        "composition_layout":"composition_layout",
        "responsive_layout":"responsive_layout",
        "interaction_state":"interaction_state",
        "presentation_intent":"presentation_intent",
        "presentation_ir":"presentation_ir",
        "dashboard_runtime":"dashboard_runtime",
        "report_definition":"report_definition",
        "report_run":"report_run",
        "pagination_layout":"pagination_layout",
        "publication_lifecycle":"publication_lifecycle",
        "embedded_bridge":"embedded_bridge",
        "export_plan":"export_plan",
        "export_encoder":"export_encoder",
    }
    rows=[]
    for seam in LIBRARY_SEAMS:
        name=seam["name"]; parent_name=aliases.get(name, name)
        p=parent_names.get(parent_name)
        rows.append({
            "bridge_id":f"bridge.presentation_sota.{name}",
            "extension_library_ref":seam["library_candidate_id"],
            "parent_library_hypothesis_ref":f"library-hypothesis.presentation.{parent_name}" if p else None,
            "parent_exact_existing_library_ref":None if not p or p[1]=="new" else p[1],
            "disposition":"PROJECT_TO_PARENT_CANDIDATE" if p else "PARENT_ADJUDICATION_REQUIRED",
            "compiler_binding":"REFUSED_UNTIL_PARENT_RATIFICATION_AND_QUALIFIED_OFFER",
            "completion_claim":False,
        })
    return rows

def summary(rows: dict[str,list[dict[str,Any]]], bridge_rows:list[dict[str,Any]]) -> dict[str,Any]:
    archetypes={x["archetype"] for x in rows["benchmarks.jsonl"]}
    industries={x["industry"] for x in rows["vertical-acceptance-cases.jsonl"]}
    observed_features=sum(len(x["observed_features"]) for x in rows["benchmarks.jsonl"])
    return {
        "program_id":"program.presentation-sota-semantics.v1",
        "as_of":"2026-08-27",
        "status":"EVIDENCE_BACKED_SOTA_EXTENSION_UNRATIFIED",
        "sources":len(rows["sources.jsonl"]),
        "benchmark_archetypes":len(archetypes),
        "benchmark_products":len(rows["benchmarks.jsonl"]),
        "provider_feature_observations":observed_features,
        "analytical_result_kinds":len(rows["analytical-result-kinds.jsonl"]),
        "question_intents":len(rows["question-intents.jsonl"]),
        "visual_patterns":len(rows["visual-patterns.jsonl"]),
        "specialist_experiences":len(rows["specialist-experiences.jsonl"]),
        "interaction_contracts":len(rows["interaction-contracts.jsonl"]),
        "candidate_library_seams":len(rows["library-seams.jsonl"]),
        "canonical_bridges":len(bridge_rows),
        "vertical_acceptance_cases":len(rows["vertical-acceptance-cases.jsonl"]),
        "industries":len(industries),
        "saturation_trials":len(rows["saturation-trials.jsonl"]),
        "negative_tests":len(rows["negative-tests.jsonl"]),
        "qualified_providers":0,
        "ratified_contracts":0,
        "executed_vertical_acceptance_cases":0,
        "completion_claim":False,
    }

def build() -> None:
    rows={k:list(v) for k,v in OUTPUTS.items()}
    bridge_rows=bridges()
    rows["canonical-bridges.jsonl"]=bridge_rows
    manifest_files={}
    for name,data in sorted(rows.items()):
        text=jsonl(data); (HERE/name).write_text(text, encoding="utf-8")
        manifest_files[name]={"records":len(data),"bytes":len(text.encode()),"sha256":hashlib.sha256(text.encode()).hexdigest()}
    s=summary(rows,bridge_rows)
    stext=json.dumps(s,indent=2,sort_keys=True)+"\n"; (HERE/"summary.json").write_text(stext,encoding="utf-8")
    manifest={"manifest_id":"manifest.presentation-sota-semantics.v1","as_of":"2026-08-27","completion_claim":False,
              "files":manifest_files,"summary_sha256":hashlib.sha256(stext.encode()).hexdigest()}
    (HERE/"manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(s,indent=2,sort_keys=True))

if __name__=="__main__":
    build()
