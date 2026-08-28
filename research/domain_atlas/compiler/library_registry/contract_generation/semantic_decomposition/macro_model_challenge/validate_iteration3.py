#!/usr/bin/env python3
"""Fail-closed validator for macro-model challenge iteration 3."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

from build_iteration3 import outputs, rows
from iteration3_model import (
    ITERATION3_AXES,
    ITERATION3_CHALLENGES,
    ITERATION3_CORRECTIONS,
    ITERATION3_DEEP_CLAIMS,
    ITERATION3_INTERACTIONS,
    ITERATION3_PRIMARY_SOURCES,
)

HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    generated = outputs()
    for name, text in generated.items():
        path = HERE / name
        require(path.is_file(), f"missing iteration-3 artifact: {name}")
        require(path.read_text(encoding="utf-8") == text, f"stale iteration-3 artifact: {name}")

    source_ids = [row["source_id"] for row in ITERATION3_PRIMARY_SOURCES]
    urls = [row["url"] for row in ITERATION3_PRIMARY_SOURCES]
    require(len(ITERATION3_PRIMARY_SOURCES) >= 180, "iteration 3 must preserve >=180 primary/official sources")
    require(len(source_ids) == len(set(source_ids)), "duplicate iteration-3 source id")
    require(len(urls) == len(set(urls)), "duplicate iteration-3 source URL")
    require(all(urlparse(url).scheme == "https" and urlparse(url).netloc for url in urls), "all iteration-3 sources must be absolute HTTPS")
    require(all(row.get("completion_claim") is False for row in ITERATION3_PRIMARY_SOURCES), "source completion promotion detected")
    source_by_id = {row["source_id"]: row for row in ITERATION3_PRIMARY_SOURCES}

    axis_ids = [row["axis"] for row in ITERATION3_AXES]
    require(len(axis_ids) == 8 and len(set(axis_ids)) == 8, "iteration 3 must expose exactly eight candidate axes")
    require("measurement_and_observation" not in axis_ids, "superseded measurement_and_observation axis leaked into iteration 3")
    require("quantity_and_value_semantics" in axis_ids, "quantity/value replacement axis missing")
    require("observation_measurement_and_metrology" in axis_ids, "observation/metrology replacement axis missing")
    require("causal_and_interventional_semantics" in axis_ids, "causal axis regressed")
    require("stochastic_mechanism_and_assignment" in axis_ids, "stochastic axis regressed")

    claims_by_axis: dict[str, list[dict]] = defaultdict(list)
    for claim in ITERATION3_DEEP_CLAIMS:
        require(claim["supports_axis"] in axis_ids, f"deep claim targets unknown axis: {claim['claim_id']}")
        require(set(claim["source_refs"]) <= set(source_by_id), f"unresolved source in claim: {claim['claim_id']}")
        require(bool(claim["bounded_claim"]) and bool(claim["authority_limit"]) and bool(claim["negative_twin"]), f"unbounded claim: {claim['claim_id']}")
        require(claim.get("completion_claim") is False, f"deep claim completion promotion: {claim['claim_id']}")
        claims_by_axis[claim["supports_axis"]].append(claim)
    for axis in ITERATION3_AXES:
        axis_id = axis["axis"]
        require(len(claims_by_axis[axis_id]) >= 5, f"{axis_id}: fewer than five bounded deep claims")
        require(set(axis["evidence_refs"]) <= set(source_by_id), f"{axis_id}: unresolved axis evidence source")
        axis_issuers = {source_by_id[ref]["issuer"] for ref in axis["evidence_refs"]}
        claim_issuers = {source_by_id[ref]["issuer"] for claim in claims_by_axis[axis_id] for ref in claim["source_refs"]}
        require(len(axis["evidence_refs"]) >= 5 and len(axis_issuers) >= 3, f"{axis_id}: insufficient source breadth")
        require(len(claim_issuers) >= 3, f"{axis_id}: insufficient deep-claim issuer diversity")
        require(len(axis["non_collapse"]) >= 4, f"{axis_id}: insufficient non-collapse laws")

    split_challenge = next((row for row in ITERATION3_CHALLENGES if row["challenge_id"] == "macro.measurement-quantity-split"), None)
    require(split_challenge is not None, "measurement/quantity split challenge missing")
    require(split_challenge["verdict"] == "SPLIT_RESEARCH_AXIS", "measurement/quantity split verdict drift")
    require(split_challenge["split_into"] == ["quantity_and_value_semantics", "observation_measurement_and_metrology"], "split lineage drift")

    summary = json.loads(generated["iteration3-summary.json"])
    require(summary["primary_source_count"] >= 180, "summary source breadth regressed")
    require(summary["primary_source_issuer_count"] >= 70, "summary issuer breadth regressed")
    require(summary["base_axis_count"] == 16, "historical base axis count changed")
    require(summary["candidate_axis_count"] == 8, "iteration-3 candidate axis count wrong")
    require(summary["effective_research_axis_count"] == 24, "effective iteration-3 model must expose 24 research axes")
    require(summary["library_count"] == 682 and summary["family_count"] == 24, "library/family population drift")
    require(summary["iteration3_candidate_axis_cells"] == 682 * 8, "iteration-3 cell arithmetic wrong")
    require(summary["effective_research_axis_cells"] == 10912 + (682 * 8), "effective research-cell arithmetic wrong")
    require(summary["candidate_cells"] + summary["unresolved_cells"] == summary["iteration3_candidate_axis_cells"], "candidate/unresolved partition not lossless")
    require(summary["family_axis_review_packages"] == 24 * 8, "family-axis review package count wrong")
    require(summary["targeted_unresolved_library_occurrences"] == summary["unresolved_cells"], "unresolved iteration-3 cells are not fully routed")
    require(summary["replacement_axes"] == ["quantity_and_value_semantics", "observation_measurement_and_metrology"], "summary split lineage drift")
    require(summary["quantity_candidate_cells"] > 0, "quantity/value split produced no candidate cells")
    require(summary["observation_candidate_cells"] > 0, "observation/metrology split produced no candidate cells")
    require(summary["canonical_gaps_closed"] == 0 and summary["owner_decisions"] == 0, "iteration 3 illegally promoted authority/canonical state")
    require(summary["completion_claim"] is False, "iteration 3 may not claim completion")

    axis_deltas = {row["axis"]: row for row in rows(HERE / "iteration3-axis-deltas.jsonl")}
    require(set(axis_deltas) == set(axis_ids), "iteration-3 axis delta population mismatch")
    require(axis_deltas["quantity_and_value_semantics"]["candidate_cells"] == summary["quantity_candidate_cells"], "quantity summary/delta mismatch")
    require(axis_deltas["observation_measurement_and_metrology"]["candidate_cells"] == summary["observation_candidate_cells"], "observation summary/delta mismatch")
    require(axis_deltas["quantity_and_value_semantics"]["independent_issuer_count"] >= 5, "quantity axis lacks issuer breadth")
    require(axis_deltas["observation_measurement_and_metrology"]["independent_issuer_count"] >= 5, "observation axis lacks issuer breadth")
    require("unit_or_currency" in axis_deltas["quantity_and_value_semantics"]["candidate_facet_counts"] or summary["quantity_candidate_cells"] > 0, "quantity axis lacks unit/currency signal")
    require("observation_or_measurement_act" in axis_deltas["observation_measurement_and_metrology"]["candidate_facet_counts"], "observation axis lacks observation-act signal")

    corrections = rows(HERE / "iteration3-correction-receipts.jsonl")
    require(len(corrections) == len(ITERATION3_CORRECTIONS) == 1, "iteration-3 correction receipt population mismatch")
    require(corrections[0]["validation_result"] == "SPLIT_EFFECTIVE", "quantity/observation split did not validate")
    require(corrections[0]["iteration3_quantity_candidate_cells"] > 0 and corrections[0]["iteration3_observation_candidate_cells"] > 0, "split receipt has an empty replacement surface")

    interactions = rows(HERE / "iteration3-cross-axis-interactions.jsonl")
    require(len(interactions) == len(ITERATION3_INTERACTIONS) >= 18, "iteration-3 cross-axis interaction graph incomplete")
    interaction_pairs = {(row["from_axis"], row["to_axis"]) for row in interactions}
    require(("quantity_and_value_semantics", "observation_measurement_and_metrology") in interaction_pairs, "quantity/observation non-collapse relation missing")
    require(("quantity_and_value_semantics", "representation") in interaction_pairs, "quantity/representation relation missing")
    require(("observation_measurement_and_metrology", "provenance_and_derivation") in interaction_pairs, "metrology/provenance relation missing")

    signatures = rows(HERE / "iteration3-signatures.jsonl")
    require(len(signatures) == 682, "iteration-3 signature count mismatch")
    require(all(len(row["axis_selections"]) == 8 for row in signatures), "every library must expose eight iteration-3 axis selections")
    require(all({selection["axis"] for selection in row["axis_selections"]} == set(axis_ids) for row in signatures), "signature axis set drift")
    require(all(row["canonical_mutation_allowed"] is False and row["completion_claim"] is False for row in signatures), "signature authority promotion detected")

    targeted = rows(HERE / "iteration3-targeted-evidence-work-packages.jsonl")
    require(sum(row["unresolved_library_count"] for row in targeted) == summary["unresolved_cells"], "targeted evidence routing not lossless")
    require(all(row["canonical_mutation_allowed"] is False and row["completion_claim"] is False for row in targeted), "targeted evidence work illegally promoted canonical state")

    model = json.loads(generated["iteration3-effective-macro-model.json"])
    require(model["candidate_axis_count"] == 8 and model["effective_research_axis_count"] == 24, "effective model axis counts wrong")
    require(model["split_lineage"] == {"measurement_and_observation": ["quantity_and_value_semantics", "observation_measurement_and_metrology"]}, "effective model split lineage wrong")
    require(model["canonical_mutation_allowed"] is False and model["completion_claim"] is False, "effective model authority promotion detected")

    print(
        "PASS macro iteration 3: "
        f"{summary['primary_source_count']} sources / {summary['primary_source_issuer_count']} issuers; "
        f"24-axis effective research model; quantity={summary['quantity_candidate_cells']} observation={summary['observation_candidate_cells']}; "
        f"all {summary['unresolved_cells']} unresolved new-axis cells routed; zero authority/canonical promotions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
