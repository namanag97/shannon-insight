#!/usr/bin/env python3
"""Validate predictive ML corpus structure, references, quotas and core boundaries."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_jsonl(name: str) -> list[dict]:
    rows = []
    for line_no, line in enumerate((ROOT / name).read_text().splitlines(), 1):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: {exc}") from exc
    return rows


def ids(rows: list[dict], key: str) -> set[str]:
    values = [row[key] for row in rows]
    assert len(values) == len(set(values)), f"duplicate {key}"
    return set(values)


def main() -> int:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    sources = load_jsonl("sources.jsonl")
    models = load_jsonl("model-families.jsonl")
    components = load_jsonl("predictive-components.jsonl")
    component_edges = load_jsonl("component-edges.jsonl")
    evidence_edges = load_jsonl("evidence-edges.jsonl")
    operations = load_jsonl("operations.jsonl")
    decisions = load_jsonl("decision-points.jsonl")
    libraries = load_jsonl("library-boundaries.jsonl")
    mappings = load_jsonl("compiler-mappings.jsonl")
    representations = load_jsonl("representation-input-requirements.jsonl")
    qualifications = load_jsonl("provider-qualification-profiles.jsonl")
    experts = load_jsonl("experts.jsonl")
    expert_edges = load_jsonl("expert-artifact-links.jsonl")
    innovations = load_jsonl("innovations-2021-2026.jsonl")
    verticals = load_jsonl("vertical-examples.jsonl")
    twins = load_jsonl("negative-twins.jsonl")
    gaps = load_jsonl("gaps.jsonl")
    axes = json.loads((ROOT / "classification-axes.json").read_text())

    source_ids = ids(sources, "source_id")
    model_ids = ids(models, "model_family_id")
    component_ids = ids(components, "component_id")
    ids(component_edges, "edge_id")
    ids(evidence_edges, "evidence_edge_id")
    ids(operations, "operation_id")
    ids(decisions, "decision_id")
    library_ids = ids(libraries, "library_id")
    ids(mappings, "mapping_id")
    representation_ids = ids(representations, "requirement_id")
    qualification_ids = ids(qualifications, "qualification_profile_id")
    ids(experts, "expert_id")
    ids(expert_edges, "edge_id")
    ids(innovations, "innovation_id")
    twin_ids = ids(twins, "negative_twin_id")
    ids(gaps, "gap_id")

    expected = {
        "sources": len(sources), "model_families": len(models), "operations": len(operations),
        "decision_points": len(decisions), "library_boundaries": len(libraries), "experts": len(experts),
        "innovations_2021_2026": len(innovations), "predictive_components": len(components),
        "component_edges": len(component_edges), "model_evidence_edges": len(evidence_edges),
    }
    for key, value in expected.items():
        assert manifest["counts"][key] == value, f"manifest count mismatch {key}"
    for key, floor in manifest["minimum_quotas"].items():
        assert manifest["counts"][key] >= floor, f"quota unmet: {key}"

    assert manifest["completion_claim"] is False
    assert manifest["status"] == "researched_candidate_open_world"
    assert len(axes["axes"]) >= 10
    required_axes = {axis["name"] for axis in axes["axes"]}
    assert {"output_geometry", "learning_signal", "data_generating_posture", "epistemic_family", "prediction_timing", "decision_proximity"} <= required_axes

    component_kinds = {"predictive_task", "model_family", "model_structure", "objective_loss", "estimator", "optimization_training_algorithm", "representation", "kernel", "fitted_artifact", "calibration", "evaluator", "decision_rule"}
    by_model = Counter(row["model_family_ref"] for row in components)
    kinds_by_model: dict[str, set[str]] = {}
    for row in components:
        kinds_by_model.setdefault(row["model_family_ref"], set()).add(row["component_kind"])
        assert row["model_family_ref"] in model_ids
        assert set(row["source_refs"]) <= source_ids
    assert all(by_model[mid] == len(component_kinds) for mid in model_ids)
    assert all(kinds_by_model[mid] == component_kinds for mid in model_ids)
    assert all(row["from_ref"] in component_ids and row["to_ref"] in component_ids for row in component_edges)

    operation_counts = Counter(row["model_family_ref"] for row in operations)
    assert all(operation_counts[mid] >= 5 for mid in model_ids)
    for model in models:
        assert model["llm_dependency"] == "none"
        assert len(model["source_refs"]) >= 2 and set(model["source_refs"]) <= source_ids
        assert model["failure_states"] and model["assumptions"] and model["axis_bindings"]
        assert required_axes <= set(model["axis_bindings"])
        forbidden = ("large language model", "prompt chain", "rag pipeline", "agent orchestration")
        assert not any(term in model["name"].lower() for term in forbidden)

    assert all(row["source_ref"] in source_ids and row["subject_ref"] in model_ids for row in evidence_edges)
    assert len(evidence_edges) >= len(models) * 2
    assert all(set(row["artifact_refs"]) <= source_ids and row["artifact_refs"] for row in experts)
    assert all(row["from_ref"].startswith("expert.predictive.") and row["to_ref"] in source_ids for row in expert_edges)

    source_year = {row["source_id"]: row["year"] for row in sources}
    recent_evidenced = 0
    for innovation in innovations:
        assert 2021 <= innovation["year"] <= 2026
        assert innovation["non_llm_core"] is True
        assert set(innovation["source_refs"]) <= source_ids
        if any(source_year[ref] >= 2021 for ref in innovation["source_refs"]):
            recent_evidenced += 1
    assert recent_evidenced >= 30, f"only {recent_evidenced} innovations have 2021-2026 primary/official evidence"

    for example in verticals:
        assert set(example["method_candidates"]) <= model_ids
        assert example["negative_twin_ref"] in twin_ids
    assert len({row["vertical"] for row in verticals}) >= 2
    assert all(row["status"] == "unexecuted_template" for row in qualifications)
    assert {row["library_ref"] for row in qualifications} == library_ids
    assert len(representation_ids) >= 20 and len(qualification_ids) >= 50

    # Exact requested process-research coverage and attribution.
    source_titles = {row["source_id"]: row["title"] for row in sources}
    required_source_fragments = ["HOEG", "Temporal Event Knowledge Graphs", "State-Aware Object-Centric", "Extensible Standard for Object-Centric Event Data"]
    assert all(any(fragment in title for title in source_titles.values()) for fragment in required_source_fragments)
    dirk = next(row for row in experts if row["name"] == "Dirk Fahland")
    assert len(dirk["artifact_refs"]) >= 3

    # Optional full schema pass if jsonschema is available.
    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None
    if jsonschema:
        schema = json.loads((ROOT / "corpus-record.schema.json").read_text())
        files = ["sources.jsonl", "model-families.jsonl", "predictive-components.jsonl", "component-edges.jsonl", "evidence-edges.jsonl", "operations.jsonl", "decision-points.jsonl", "library-boundaries.jsonl", "compiler-mappings.jsonl", "representation-input-requirements.jsonl", "provider-qualification-profiles.jsonl", "experts.jsonl", "expert-artifact-links.jsonl", "innovations-2021-2026.jsonl", "vertical-examples.jsonl", "negative-twins.jsonl", "gaps.jsonl"]
        for name in files:
            for row in load_jsonl(name):
                jsonschema.validate(row, schema)

    print("PASS predictive ML open-world corpus")
    print(json.dumps({"counts": manifest["counts"], "recent_innovations_with_recent_evidence": recent_evidenced, "families": manifest["field_coverage"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
