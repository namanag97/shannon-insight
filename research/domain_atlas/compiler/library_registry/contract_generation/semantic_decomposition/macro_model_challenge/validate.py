#!/usr/bin/env python3
"""Fail-closed validation for the primary-source macro-model challenge."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

from build_macro_challenge import outputs, rows
from source_model import DEEP_EVIDENCE_CLAIMS, MACRO_CHALLENGES, PRIMARY_SOURCES, PROPOSED_AXES

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
ALLOWED_SOURCE_CLASSES = {
    "international_standard",
    "standards_body_recommendation",
    "standards_body_catalog",
    "government_standard",
    "internet_standard",
    "official_technical_specification",
    "industry_standard",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    source_ids = [row["source_id"] for row in PRIMARY_SOURCES]
    urls = [row["url"] for row in PRIMARY_SOURCES]
    require(len(PRIMARY_SOURCES) >= 120, "primary-source challenge corpus must contain at least 120 sources")
    require(len(source_ids) == len(set(source_ids)), "duplicate primary source_id")
    require(len(urls) == len(set(urls)), "duplicate primary source URL")
    require(all(urlparse(url).scheme == "https" and urlparse(url).netloc for url in urls), "all challenge sources must use absolute HTTPS URLs")
    require(all(row["source_class"] in ALLOWED_SOURCE_CLASSES for row in PRIMARY_SOURCES), "unexpected source class")
    require(all(row.get("completion_claim") is False for row in PRIMARY_SOURCES), "source records may not claim completion")

    source_by_id = {row["source_id"]: row for row in PRIMARY_SOURCES}
    axis_ids = [row["axis"] for row in PROPOSED_AXES]
    require(len(PROPOSED_AXES) == 5 and len(set(axis_ids)) == 5, "exactly five unique proposed axes are required in iteration 1")
    for axis in PROPOSED_AXES:
        require(len(axis["facets"]) >= 5, f"{axis['axis']}: insufficient facets")
        require(len(axis["non_collapse"]) >= 3, f"{axis['axis']}: insufficient non-collapse laws")
        require(axis["model_verdict"] == "ADD_RESEARCH_AXIS", f"{axis['axis']}: invalid model verdict")
        require(set(axis["evidence_refs"]) <= set(source_by_id), f"{axis['axis']}: unresolved evidence ref")
        issuers = {source_by_id[ref]["issuer"] for ref in axis["evidence_refs"]}
        require(len(axis["evidence_refs"]) >= 5 and len(issuers) >= 3, f"{axis['axis']}: evidence breadth too weak")

    claims_by_axis: dict[str, list[dict]] = defaultdict(list)
    claim_ids = set()
    for claim in DEEP_EVIDENCE_CLAIMS:
        require(claim["claim_id"] not in claim_ids, f"duplicate claim: {claim['claim_id']}")
        claim_ids.add(claim["claim_id"])
        require(claim["supports_axis"] in axis_ids, f"unknown axis in claim: {claim['claim_id']}")
        require(set(claim["source_refs"]) <= set(source_by_id), f"unresolved source in claim: {claim['claim_id']}")
        require(bool(claim["bounded_claim"]), f"missing bounded claim: {claim['claim_id']}")
        require(bool(claim["authority_limit"]), f"missing authority limit: {claim['claim_id']}")
        require(bool(claim["negative_twin"]), f"missing negative twin: {claim['claim_id']}")
        require(claim.get("completion_claim") is False, f"claim illegally promotes completion: {claim['claim_id']}")
        claims_by_axis[claim["supports_axis"]].append(claim)
    for axis_id in axis_ids:
        require(len(claims_by_axis[axis_id]) >= 5, f"{axis_id}: requires at least five deep bounded claims")
        issuers = {
            source_by_id[ref]["issuer"]
            for claim in claims_by_axis[axis_id]
            for ref in claim["source_refs"]
        }
        require(len(issuers) >= 3, f"{axis_id}: deep claims lack issuer independence")

    challenge_ids = [row["challenge_id"] for row in MACRO_CHALLENGES]
    require(len(challenge_ids) == len(set(challenge_ids)), "duplicate macro challenge")
    verdicts = Counter(row["verdict"] for row in MACRO_CHALLENGES)
    require(verdicts["ADD_RESEARCH_AXIS"] == 5, "five positive axis challenges required")
    require(verdicts["REJECT_NEW_AXIS_COMPOSE"] >= 5, "at least five rejected redundant-axis challenges required")
    require({row["candidate"] for row in MACRO_CHALLENGES if row["verdict"] == "ADD_RESEARCH_AXIS"} == set(axis_ids), "positive challenge set != proposed axes")

    base_ontology_path = SEM / "semantic-axis-ontology.json"
    base_ontology = json.loads(base_ontology_path.read_text(encoding="utf-8"))
    base_manifest = json.loads((SEM / "manifest.json").read_text(encoding="utf-8"))
    base_summary = json.loads((SEM / "summary.json").read_text(encoding="utf-8"))
    base_axis_ids = {row["axis"] for row in base_ontology["axes"]}
    require(len(base_axis_ids) == 16, "historical base axis count drift")
    require(not (base_axis_ids & set(axis_ids)), "proposed axis collides with historical axis")
    require(hashlib.sha256(base_ontology_path.read_bytes()).hexdigest() == base_manifest["files"]["semantic-axis-ontology.json"]["sha256"], "historical ontology digest drift")
    require(base_summary["library_signatures"] == 682, "historical library population drift")
    require(base_summary["axis_cells"] == 10912, "historical axis-cell count drift")

    generated = outputs()
    for name, text in generated.items():
        path = HERE / name
        require(path.is_file(), f"missing generated artifact: {name}")
        require(path.read_text(encoding="utf-8") == text, f"stale generated artifact: {name}")

    summary = json.loads(generated["summary.json"])
    require(summary["primary_source_count"] >= 120, "summary source count regressed")
    require(summary["base_axis_count"] == 16, "summary base axis count wrong")
    require(summary["proposed_axis_count"] == 5, "summary proposed axis count wrong")
    require(summary["effective_research_axis_count"] == 21, "effective macro-model must be 21 axes in iteration 1")
    require(summary["library_count"] == 682, "macro projection must cover all 682 libraries")
    require(summary["new_axis_cells"] == 3410, "new-axis review population must be 682 x 5")
    require(summary["effective_research_axis_cells"] == 14322, "effective review population must be 10,912 + 3,410")
    require(summary["new_axis_candidate_cells"] + summary["new_axis_unresolved_cells"] == 3410, "new-axis cell partition is not lossless")
    require(summary["new_family_axis_review_packages"] == 120, "new family-axis package population must be 24 x 5")
    require(summary["canonical_gaps_closed"] == 0 and summary["owner_decisions"] == 0, "research challenge illegally promoted authority")
    require(summary["completion_claim"] is False, "macro challenge may not claim completion")

    model = json.loads(generated["effective-macro-model.json"])
    require(model["canonical_mutation_allowed"] is False, "effective research model may not mutate canonical state")
    require(model["completion_claim"] is False, "effective research model may not claim completion")
    require(model["base_model"]["axis_ids"] == [row["axis"] for row in base_ontology["axes"]], "historical axis ordering changed")

    signatures = [json.loads(line) for line in generated["effective-new-axis-signatures.jsonl"].splitlines() if line]
    require(len(signatures) == 682, "signature population mismatch")
    require(all(len(row["axis_selections"]) == 5 for row in signatures), "each library must expose five new-axis selections")
    require(all(row.get("canonical_mutation_allowed") is False and row.get("completion_claim") is False for row in signatures), "signature promotion detected")
    allowed_selection_status = {"EXPLICIT_CANDIDATE_SET_UNRATIFIED", "UNRESOLVED_OWNER_INPUT_REQUIRED"}
    require(all(selection["status"] in allowed_selection_status for row in signatures for selection in row["axis_selections"]), "invalid selection status")

    print(
        "PASS macro-model challenge: "
        f"{summary['primary_source_count']} primary/official sources, "
        f"{summary['deep_bounded_claim_count']} deep claims, "
        f"{summary['library_count']} libraries x 5 candidate axes = {summary['new_axis_cells']} new review cells; "
        "historical 16-axis corpus unchanged; zero authority/canonical promotions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
