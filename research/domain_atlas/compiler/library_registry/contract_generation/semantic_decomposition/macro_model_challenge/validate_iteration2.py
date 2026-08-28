#!/usr/bin/env python3
"""Fail-closed validator for macro-model challenge iteration 2."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

from build_iteration2 import outputs, rows
from iteration2_model import (
    CROSS_AXIS_INTERACTIONS,
    ITERATION2_AXES,
    ITERATION2_CHALLENGES,
    ITERATION2_CORRECTIONS,
    ITERATION2_DEEP_CLAIMS,
    ITERATION2_PRIMARY_SOURCES,
)

HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    generated = outputs()
    for name, text in generated.items():
        path = HERE / name
        require(path.is_file(), f"missing iteration-2 artifact: {name}")
        require(path.read_text(encoding="utf-8") == text, f"stale iteration-2 artifact: {name}")

    source_ids = [row["source_id"] for row in ITERATION2_PRIMARY_SOURCES]
    urls = [row["url"] for row in ITERATION2_PRIMARY_SOURCES]
    require(len(ITERATION2_PRIMARY_SOURCES) >= 170, "iteration 2 must retain >100-source breadth and causal/stochastic additions")
    require(len(source_ids) == len(set(source_ids)), "duplicate iteration-2 source id")
    require(len(urls) == len(set(urls)), "duplicate iteration-2 source URL")
    require(all(urlparse(url).scheme == "https" and urlparse(url).netloc for url in urls), "all iteration-2 sources must be absolute HTTPS")
    require(all(row.get("completion_claim") is False for row in ITERATION2_PRIMARY_SOURCES), "source completion promotion detected")
    source_by_id = {row["source_id"]: row for row in ITERATION2_PRIMARY_SOURCES}

    axis_ids = [row["axis"] for row in ITERATION2_AXES]
    require(len(axis_ids) == 7 and len(set(axis_ids)) == 7, "iteration 2 must expose exactly seven candidate axes")
    require("causal_and_interventional_semantics" in axis_ids, "causal axis missing")
    require("stochastic_mechanism_and_assignment" in axis_ids, "stochastic mechanism axis missing")

    claims_by_axis: dict[str, list[dict]] = defaultdict(list)
    for claim in ITERATION2_DEEP_CLAIMS:
        require(claim["supports_axis"] in axis_ids, f"deep claim targets unknown iteration-2 axis: {claim['claim_id']}")
        require(set(claim["source_refs"]) <= set(source_by_id), f"unresolved deep-claim source: {claim['claim_id']}")
        require(bool(claim["bounded_claim"]) and bool(claim["authority_limit"]) and bool(claim["negative_twin"]), f"unbounded deep claim: {claim['claim_id']}")
        require(claim.get("completion_claim") is False, f"deep claim completion promotion: {claim['claim_id']}")
        claims_by_axis[claim["supports_axis"]].append(claim)
    for axis in ITERATION2_AXES:
        axis_id = axis["axis"]
        require(len(claims_by_axis[axis_id]) >= 5, f"{axis_id}: fewer than five bounded deep claims")
        require(set(axis["evidence_refs"]) <= set(source_by_id), f"{axis_id}: unresolved axis evidence source")
        evidence_issuers = {source_by_id[ref]["issuer"] for ref in axis["evidence_refs"]}
        claim_issuers = {source_by_id[ref]["issuer"] for claim in claims_by_axis[axis_id] for ref in claim["source_refs"]}
        require(len(axis["evidence_refs"]) >= 5 and len(evidence_issuers) >= 3, f"{axis_id}: axis evidence lacks breadth")
        require(len(claim_issuers) >= 3, f"{axis_id}: deep claims lack issuer diversity")
        require(len(axis["non_collapse"]) >= 4, f"{axis_id}: insufficient non-collapse laws")

    challenge_by_id = {row["challenge_id"]: row for row in ITERATION2_CHALLENGES}
    require("macro.causal-interventional" in challenge_by_id, "causal challenge absent")
    require("macro.stochastic-mechanism" in challenge_by_id, "stochastic challenge absent")
    require(challenge_by_id["macro.causal-interventional"]["verdict"] == "ADD_RESEARCH_AXIS", "causal challenge not promoted to research axis")
    require(challenge_by_id["macro.stochastic-mechanism"]["verdict"] == "ADD_RESEARCH_AXIS", "stochastic challenge not promoted to research axis")
    require(challenge_by_id["macro.objective-preference"]["verdict"] == "REJECT_NEW_AXIS_COMPOSE", "objective/preference challenge must remain composed rather than duplicate sovereign intent semantics")
    require(sum(row["verdict"] == "ADD_RESEARCH_AXIS" for row in ITERATION2_CHALLENGES) == 7, "iteration 2 positive-axis challenge count drift")
    require(sum(row["verdict"] == "REJECT_NEW_AXIS_COMPOSE" for row in ITERATION2_CHALLENGES) >= 6, "insufficient rejected redundant-axis challenges")

    summary = json.loads(generated["iteration2-summary.json"])
    require(summary["primary_source_count"] >= 170, "summary source breadth regressed")
    require(summary["base_axis_count"] == 16, "historical base axis count changed")
    require(summary["candidate_axis_count"] == 7, "iteration-2 candidate axis count wrong")
    require(summary["effective_research_axis_count"] == 23, "effective iteration-2 model must expose 23 research axes")
    require(summary["library_count"] == 682 and summary["family_count"] == 24, "library/family population drift")
    require(summary["iteration2_candidate_axis_cells"] == 682 * 7, "iteration-2 cell arithmetic wrong")
    require(summary["effective_research_axis_cells"] == 10912 + (682 * 7), "effective research-cell arithmetic wrong")
    require(summary["candidate_cells"] + summary["unresolved_cells"] == summary["iteration2_candidate_axis_cells"], "candidate/unresolved partition not lossless")
    require(summary["family_axis_review_packages"] == 24 * 7, "family-axis package population wrong")
    require(summary["targeted_unresolved_library_occurrences"] == summary["unresolved_cells"], "unresolved cells are not fully routed to targeted evidence")
    require(summary["canonical_gaps_closed"] == 0 and summary["owner_decisions"] == 0, "iteration 2 illegally promoted authority/canonical state")
    require(summary["completion_claim"] is False, "iteration 2 may not claim completion")

    axis_deltas = {row["axis"]: row for row in rows(HERE / "iteration2-axis-deltas.jsonl")}
    require(axis_deltas["scope_population_and_eligibility"]["candidate_cells"] <= 100, "scope/population correction did not remove generic lexical contamination")
    require(summary["scope_candidate_cell_reduction"] >= 250, "scope/population false-positive reduction is not material")
    require("contextual_constraint" not in axis_deltas["scope_population_and_eligibility"]["candidate_facet_counts"], "iteration-1 generic contextual constraint leaked into iteration 2")
    require(axis_deltas["scope_population_and_eligibility"]["candidate_facet_counts"].get("population_applicability_predicate", 0) <= 20, "refined population applicability matcher is still over-broad")
    require(axis_deltas["causal_and_interventional_semantics"]["candidate_cells"] >= 40, "causal axis lacks cross-library discovery support")
    require(axis_deltas["causal_and_interventional_semantics"]["families_with_candidate_hits"] >= 10, "causal axis lacks cross-family discovery support")
    require(axis_deltas["stochastic_mechanism_and_assignment"]["candidate_cells"] >= 1, "stochastic axis has no direct discovery candidates")
    require(axis_deltas["stochastic_mechanism_and_assignment"]["unresolved_cells"] > axis_deltas["stochastic_mechanism_and_assignment"]["candidate_cells"], "stochastic axis unexpectedly treated lexical discovery as universal applicability")

    corrections = rows(HERE / "iteration2-correction-receipts.jsonl")
    require(len(corrections) == len(ITERATION2_CORRECTIONS), "correction receipt population mismatch")
    require(all(row["validation_result"] in {"FALSE_POSITIVE_SURFACE_REDUCED", "SEPARATE_CAUSAL_AXIS_PRESENT"} for row in corrections), "iteration-2 correction failed")

    interactions = rows(HERE / "iteration2-cross-axis-interactions.jsonl")
    require(len(interactions) == len(CROSS_AXIS_INTERACTIONS) >= 12, "cross-axis interaction graph incomplete")
    interaction_pairs = {(row["from_axis"], row["to_axis"]) for row in interactions}
    require(("causal_and_interventional_semantics", "order_and_topology") in interaction_pairs, "causal/topology non-collapse missing")
    require(("stochastic_mechanism_and_assignment", "partiality_and_uncertainty") in interaction_pairs, "stochastic/uncertainty non-collapse missing")
    require(("normativity_and_obligation", "authority_and_trust") in interaction_pairs, "normativity/authority non-collapse missing")
    require(("provenance_and_derivation", "authority_and_trust") in interaction_pairs, "provenance/authority non-collapse missing")

    signatures = rows(HERE / "iteration2-signatures.jsonl")
    require(len(signatures) == 682, "iteration-2 signature count mismatch")
    require(all(len(row["axis_selections"]) == 7 for row in signatures), "every library must expose seven iteration-2 axis selections")
    allowed_statuses = {"EXPLICIT_CANDIDATE_SET_UNRATIFIED", "UNRESOLVED_OWNER_INPUT_REQUIRED"}
    require(all(selection["status"] in allowed_statuses for row in signatures for selection in row["axis_selections"]), "invalid iteration-2 selection status")
    require(all(row["canonical_mutation_allowed"] is False and row["completion_claim"] is False for row in signatures), "signature authority promotion detected")

    target_rows = rows(HERE / "iteration2-targeted-evidence-work-packages.jsonl")
    require(sum(row["unresolved_library_count"] for row in target_rows) == summary["unresolved_cells"], "targeted evidence routing not lossless")
    require(all(row["canonical_mutation_allowed"] is False and row["completion_claim"] is False for row in target_rows), "targeted evidence work illegally promotes canonical state")

    print(
        "PASS macro iteration 2: "
        f"{summary['primary_source_count']} sources / {summary['primary_source_issuer_count']} issuers; "
        f"23-axis effective research model; scope candidates {summary['scope_iteration1_candidate_cells']}->{summary['scope_iteration2_candidate_cells']}; "
        f"causal={summary['causal_candidate_cells']} stochastic={summary['stochastic_candidate_cells']}; "
        f"all {summary['unresolved_cells']} unresolved new-axis cells routed; zero authority/canonical promotions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
