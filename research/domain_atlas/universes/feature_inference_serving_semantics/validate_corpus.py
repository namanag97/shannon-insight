#!/usr/bin/env python3
"""Validate the feature and inference serving semantic corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_corpus


ROOT = Path(__file__).resolve().parent


def load(name: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / name).read_text().splitlines() if line.strip()]


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    data = {name: load(name) for name in build_corpus.FILES}
    for name, rows in data.items():
        assert manifest["files"][name]["records"] == len(rows)
        assert manifest["files"][name]["sha256"] == hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert len(data["sources.jsonl"]) == 28 and all(x["source_kind"] == "primary_or_official" and x["does_not_prove"] for x in data["sources.jsonl"])
    assert len(data["bounded-contexts.jsonl"]) == 4
    methods = {json.loads(x)["method_id"] for x in (ROOT.parents[2] / "product_ontology/boundary_method_ensemble/methods.jsonl").read_text().splitlines() if x.strip()}
    lenses = data["boundary-lens-adjudication.jsonl"]
    assert len(lenses) == 12 and all(set(x["method_refs"]) <= methods for x in lenses)
    decisions = data["decision-points.jsonl"]
    assert len(decisions) == 144 and all(x["default"] is None and x["default_law"] == "forbidden" for x in decisions)
    libraries = {x["library_id"]: x for x in data["library-contracts.jsonl"]}
    assert set(libraries) == {"library.feature.historical_cut.planner", "library.feature.historical_cut.evaluator", "library.feature.materialization.planner", "library.feature.materialization.protocol", "library.feature.online_read.protocol", "library.inference.revision_router", "library.inference.rollout_protocol"}
    expected_ops = {"library.feature.historical_cut.planner": 7, "library.feature.historical_cut.evaluator": 7, "library.feature.materialization.planner": 7, "library.feature.materialization.protocol": 7, "library.feature.online_read.protocol": 7, "library.inference.revision_router": 8, "library.inference.rollout_protocol": 8}
    for lid, lib in libraries.items():
        assert len(lib["operations"]) == expected_ops[lid]
        assert len(lib["public_types"]) >= 30
        assert all(op["purity"] == "pure" and op["output_type"].startswith("Result<") for op in lib["operations"])
        assert lib["gaps"] and not lib["qualification_required"]
    assert libraries["library.inference.rollout_protocol"]["effect_boundary"] == "pure_effect_proposals"
    assert libraries["library.feature.materialization.protocol"]["effect_boundary"] == "pure_effect_intents"
    verdicts = {x["verdict_id"]: x for x in data["boundary-verdicts.jsonl"]}
    assert len(verdicts) == 5
    assert {x.get("supersedes_abstract_ref") for x in verdicts.values() if x.get("supersedes_abstract_ref")} == {"library.model.feature_historical_retrieval", "library.model.feature_materialization", "library.model.feature_online_retrieval", "library.model.inference_routing"}
    laws = " ".join(l for x in libraries.values() for l in x["laws"]).lower()
    for phrase in ["event time, availability time", "latest online state", "materialization is derived cache state", "configured route weights", "traffic shift is not promotion", "model or agent may propose"]: assert phrase in laws
    assert len(data["negative-twins.jsonl"]) == 36
    offers = [x for x in data["compiler-contracts.jsonl"] if x["record_kind"] == "capability_offer"]
    assert len(data["compiler-contracts.jsonl"]) == 21 and len(offers) == 7 and all(not x["portable"] and not x["selectable"] for x in offers)
    assert manifest["completion_claim"] is False and manifest["qualified_implementation_count"] == 0
    print("VALIDATION PASS feature/inference serving: 7 libraries, 144 no-default decisions, 51 pure operations, 12 lenses, 36 negative twins, 0 qualified offers")


if __name__ == "__main__": main()
