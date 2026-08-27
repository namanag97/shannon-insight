#!/usr/bin/env python3
"""Validate claims, references and deterministic-first laws in the gap audit."""

from __future__ import annotations

import json
from collections import Counter

from build_bundle import HERE, SECTIONS, outputs


def rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text().splitlines() if line.strip()]


def main() -> int:
    errors: list[str] = []
    require = lambda ok, message: None if ok else errors.append(message)
    expected = outputs()
    for path, content in expected.items():
        require(path.is_file() and path.read_bytes() == content, f"stale {path.name}")
    source = json.loads((HERE / "source.json").read_text())
    evidence_rows = rows(SECTIONS["sources"])
    hypotheses = rows(SECTIONS["hypotheses"])
    deferred = rows(SECTIONS["deferred_hypotheses"])
    libraries = rows(SECTIONS["library_hypotheses"])
    collisions = rows(SECTIONS["collision_tests"])
    negatives = rows(SECTIONS["negative_tests"])
    gaps = rows(SECTIONS["blocking_gaps"])
    evidence = {row["source_id"]: row for row in evidence_rows}
    hypothesis_ids = {row["hypothesis_id"] for row in hypotheses}

    require(len(evidence) >= 35, "primary-source floor not met")
    require(len(hypotheses) == 5, "expected five promotion hypotheses")
    require(len(deferred) >= 7, "deferred frontier floor not met")
    require(len(libraries) >= 55, "library decomposition floor not met")
    require(len(negatives) >= 10, "negative-test floor not met")
    require(all(row["blocking_for_ratification"] for row in gaps), "nonblocking gap fabricated")
    require(source["status"].endswith("not_adjudicated_or_ratified"), "audit overclaims adjudication")

    expected_axes = {"user", "job", "adoption", "semantics", "authority", "lifecycle", "operation", "economics", "interface", "market_evidence"}
    for row in hypotheses:
        ident = row["hypothesis_id"]
        require(row["status"] == "candidate_not_ratified", f"{ident}: ratification drift")
        require(row["preliminary_disposition"] == "promote_for_full_adjudication", f"{ident}: unexpected disposition")
        require(set(row["split_scores"]) == expected_axes, f"{ident}: incomplete split scores")
        require(row["score_total"] == sum(row["split_scores"].values()), f"{ident}: score mismatch")
        require(row["score_total"] >= 17, f"{ident}: insufficient preliminary split evidence")
        require(len(row["evidence_refs"]) >= 6, f"{ident}: weak evidence coverage")
        require(all(ref in evidence for ref in row["evidence_refs"]), f"{ident}: unresolved evidence")
        require(len(row["deterministic_core"]) >= 8, f"{ident}: deterministic core underdecomposed")
        require(bool(row["optional_method_bindings"]), f"{ident}: method seam missing")
        require(len(row["lifecycle_states"]) >= 9, f"{ident}: lifecycle underdecomposed")
        modality = row["automation_modality"]
        require(modality["default"] == "DETERMINISTIC_CORE_ONLY", f"{ident}: ambient automation")
        require(set(modality["allowed"]) == {"PROHIBITED", "OPTIONAL", "REQUIRED_BY_INTENT", "UNDETERMINED"}, f"{ident}: modality postures incomplete")
        require("typed proposal" in modality["proposal_law"] and "ground truth" in modality["proposal_law"], f"{ident}: proposal authority law missing")
        require("vocabulary enumeration" in modality["hard_work_law"] and "qualification" in modality["hard_work_law"], f"{ident}: hard-work law missing")

    require({row["hypothesis_ref"] for row in collisions} == hypothesis_ids, "collision-test coverage drift")
    require({row["product_hypothesis_ref"] for row in libraries} == hypothesis_ids, "library-family coverage drift")
    require({row["hypothesis_ref"] for row in gaps} == hypothesis_ids, "blocking-gap coverage drift")
    require(all(len(row["required_surface"]) == 8 for row in libraries), "library DDD/compiler surface incomplete")
    require(Counter(row["family"] for row in evidence_rows) == Counter({
        "self_service_data_preparation": 6,
        "annotation_operations": 8,
        "document_processing_review": 8,
        "visual_inspection_operations": 8,
        "signal_condition_diagnostics": 8,
    }), "evidence-family counts drift")
    negative_ids = {row["negative_test_id"] for row in negatives}
    require({"negative.aoga.ai_prefix", "negative.aoga.agent_research_substitute", "negative.aoga.deterministic_means_closed_form"}.issubset(negative_ids), "critical automation negatives missing")
    manifest = json.loads((HERE / "manifest.json").read_text())
    require(manifest["derived"]["promotion_hypotheses"] == 5, "promotion count drift")
    require(manifest["derived"]["ratified_products"] == 0 and manifest["derived"]["qualified_providers"] == 0, "fabricated ratification or qualification")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "PASS analytical-operations gap audit: "
        f"{len(evidence)} primary sources; {len(hypotheses)} promotion hypotheses; "
        f"{len(deferred)} deferred hypotheses; {len(libraries)} library boundaries; "
        f"{len(collisions)} collision tests; {len(negatives)} negative twins; {len(gaps)} blocking gaps; 0 ratified products"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
