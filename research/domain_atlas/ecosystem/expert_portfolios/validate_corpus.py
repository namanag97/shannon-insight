#!/usr/bin/env python3
"""Referential, constitutional, breadth, schema, and determinism checks."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GENERATED = [
    "experts.jsonl", "artifacts.jsonl", "families.jsonl", "contribution-edges.jsonl",
    "concept-candidates.jsonl", "compiler-library-mappings.jsonl", "implementation-tool-evidence.jsonl",
    "innovations-2021-2026.jsonl", "review-queue.jsonl", "counterevidence-queue.jsonl", "sources.jsonl",
    "artifact-conversion-candidates.jsonl",
    "coverage-matrix.json", "manifest.json",
]


def rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def index(records: list[dict], key: str) -> dict[str, dict]:
    result = {}
    for record in records:
        assert record[key] not in result, f"duplicate {key}: {record[key]}"
        result[record[key]] = record
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def schema_validate(records: list[dict], schema_name: str) -> None:
    try:
        import jsonschema
    except ImportError:
        return
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for number, record in enumerate(records, 1):
        errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
        assert not errors, f"{schema_name} row {number}: {errors[0].message}"


def main() -> None:
    experts = rows("experts.jsonl")
    artifacts = rows("artifacts.jsonl")
    families = rows("families.jsonl")
    edges = rows("contribution-edges.jsonl")
    mappings = rows("compiler-library-mappings.jsonl")
    reviews = rows("review-queue.jsonl")
    innovations = rows("innovations-2021-2026.jsonl")
    implementations = rows("implementation-tool-evidence.jsonl")
    conversions = rows("artifact-conversion-candidates.jsonl")
    concepts = rows("concept-candidates.jsonl")

    expert_by_id = index(experts, "expert_id")
    artifact_by_id = index(artifacts, "artifact_id")
    family_by_id = index(families, "family_id")
    edge_by_id = index(edges, "edge_id")
    mapping_by_id = index(mappings, "mapping_id")
    review_by_id = index(reviews, "review_id")
    concept_by_id = index(concepts, "concept_id")

    assert len(experts) >= 180, len(experts)
    assert len(artifacts) >= 600, len(artifacts)
    assert len(families) >= 60, len(families)
    assert len(edges) >= 1500, len(edges)
    assert len({row["domain"] for row in experts}) >= 15
    assert len(mappings) == len(families)
    assert len(reviews) == len(experts)
    assert len(implementations) >= 50
    assert len(innovations) >= 100
    assert len(conversions) >= 1000

    for expert in experts:
        assert expert["artifact_refs"], f"expert without exact artifact: {expert['expert_id']}"
        assert all(ref in artifact_by_id for ref in expert["artifact_refs"])
        assert all(ref in family_by_id for ref in expert["family_refs"])
        assert expert["portfolio_state"] != "identity_review_required"
    family_expert_counts = Counter(ref for expert in experts for ref in expert["family_refs"])
    assert min(family_expert_counts.values()) >= 3

    contribution_by_expert = Counter()
    banned_relations = {"invented", "solely_invented", "proved_expertise"}
    for edge in edges:
        assert edge["relation"] not in banned_relations
        assert edge["evidence_refs"]
        assert edge["limitations"]
        if edge["from_id"].startswith("expert."):
            assert edge["from_id"] in expert_by_id
        if edge["to_id"].startswith("artifact."):
            assert edge["to_id"] in artifact_by_id
        elif edge["to_id"].startswith("family."):
            assert edge["to_id"] in family_by_id
        elif edge["to_id"].startswith("concept."):
            assert edge["to_id"] in concept_by_id
        if edge["relation"] == "authored":
            assert edge["claim_state"] in {"bibliographic_verified", "identity_review_required"}
            assert edge["evidence_scope"] == ["registered bibliographic authorship"]
        if edge["from_id"].startswith("expert.") and edge["relation"] in {"authored", "implemented", "developed_methodology", "performed_formal_analysis", "validated", "maintains", "advocated"}:
            contribution_by_expert[edge["from_id"]] += 1
    assert all(contribution_by_expert[eid] >= 1 for eid in expert_by_id)

    banned_title_fragments = ["large language model", "chatgpt", "generative ai", "foundation model"]
    for artifact in artifacts:
        assert artifact["direct_url"].startswith("https://")
        title = artifact["title"].lower()
        assert not any(term in title for term in banned_title_fragments), artifact["title"]
        assert artifact["claim_state"] == "bibliographic_verified"
        assert len(artifact["limitations"]) >= 2
        assert artifact["work_id"].startswith("work.")
        assert artifact["edition_id"].startswith("edition.")
        assert artifact["edition_identity_state"] == "doi_registered_manifestation_not_content_pinned"
        assert artifact["content_digest"] is None

    mapped_families = {row["family_id"] for row in mappings}
    assert mapped_families == set(family_by_id)
    for mapping in mappings:
        assert mapping["mapping_state"] == "candidate_requires_artifact_content_review"
        assert len(mapping["decision_points"]) >= 5
        assert len(mapping["invariants"]) >= 4
        assert "qualification_receipt" in mapping["compiler_targets"]
        assert any("candidate family module" in item for item in mapping["library_boundaries"])
    for item in innovations:
        assert 2021 <= item["year"] <= 2026
        assert item["admission_state"] == "not_admitted_bibliographic_candidate"
    routed = 0
    quarantined = 0
    content_reviewed = 0
    for item in conversions:
        assert item["expert_ref"] in expert_by_id
        assert item["artifact_ref"] in artifact_by_id
        assert item["family_ref"] in family_by_id
        assert item["conversion_state"] in {"artifact_content_candidate_not_compiler_eligible", "bibliographic_only_not_compiler_eligible", "quarantined_identity_or_topic_ambiguous"}
        if item["conversion_state"] == "quarantined_identity_or_topic_ambiguous":
            quarantined += 1
            assert item["admitted_roles"] == []
            assert item["candidate_method_ref"] is None
            assert item["candidate_representation_inputs"] == []
            assert item["candidate_result_outputs"] == []
            assert item["candidate_decision_points"] == []
            assert item["candidate_invariants"] == []
            assert item["candidate_compiler_targets"] == []
            assert item["candidate_library_boundaries"] == []
        else:
            routed += 1
            assert item["candidate_method_ref"] in family_by_id
            assert item["candidate_representation_inputs"]
            assert item["candidate_result_outputs"]
            assert item["candidate_decision_points"]
            assert item["candidate_invariants"]
            if item["conversion_state"] == "artifact_content_candidate_not_compiler_eligible":
                content_reviewed += 1
        assert len(item["conversion_blockers"]) >= 8
    assert routed >= 650, routed
    assert quarantined >= 100, quarantined
    assert content_reviewed >= 15, content_reviewed

    schema_validate(experts, "expert.schema.json")
    schema_validate(artifacts, "artifact.schema.json")
    schema_validate(edges, "contribution-edge.schema.json")
    schema_validate(mappings, "compiler-mapping.schema.json")

    before = {name: digest(ROOT / name) for name in GENERATED}
    subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(ROOT / name) for name in GENERATED}
    assert before == after, "builder is not deterministic"

    print(
        "PASS expert portfolio: "
        f"{len(experts)} people, {len(families)} families, {len(artifacts)} unique artifacts, "
        f"{len(edges)} contribution edges, {len(innovations)} recent candidates, "
        f"{len(mappings)} compiler/library mappings, {len(conversions)} conversion rows "
        f"({routed} routed, {quarantined} quarantined, {content_reviewed} content-reviewed); "
        "all identity/content/replication reviews remain explicit"
    )


if __name__ == "__main__":
    main()
