#!/usr/bin/env python3
"""Structural, referential, coverage, and constitutional validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_jsonl(name: str) -> list[dict]:
    rows = []
    for line_no, line in enumerate((ROOT / name).read_text().splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{name}:{line_no}: invalid JSON: {exc}") from exc
    return rows


FILES = [
    "works.jsonl", "editions.jsonl", "venue-occurrences.jsonl", "artifacts.jsonl",
    "people.jsonl", "institutions.jsonl", "contributions.jsonl",
    "sources.jsonl", "evidence.jsonl", "concepts.jsonl", "formalisms.jsonl",
    "research-types.jsonl", "claims.jsonl", "methods.jsonl", "models.jsonl",
    "estimators.jsonl", "guarantees.jsonl",
    "algorithms.jsonl", "implementations.jsonl", "benchmarks.jsonl", "relations.jsonl",
    "evaluations.jsonl", "supplementary-artifacts.jsonl", "limitations-threats.jsonl",
    "replications.jsonl", "contradictions-supersessions.jsonl",
    "relation-ontology.jsonl", "compiler-library-mappings.jsonl", "conversion-rules.jsonl",
    "conflict-replication.jsonl", "review-queue.jsonl", "gaps.jsonl",
]


def digest_outputs() -> str:
    h = hashlib.sha256()
    for name in sorted(FILES + ["manifest.json", "metamodel.json"]):
        h.update(name.encode())
        h.update((ROOT / name).read_bytes())
    return h.hexdigest()


def validate(rebuild: bool = False) -> None:
    before = digest_outputs()
    if rebuild:
        subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], check=True)
        after = digest_outputs()
        assert before == after, "generator is not deterministic or generated files were stale"

    data = {name: load_jsonl(name) for name in FILES}
    artifacts = data["artifacts.jsonl"]
    assert len(artifacts) >= 120, "at least 120 candidate artifacts required"
    assert sum(a["year"] <= 2020 for a in artifacts) >= 35, "at least 35 foundational artifacts required"
    assert sum(2021 <= a["year"] <= 2026 for a in artifacts) >= 35, "at least 35 recent artifacts required"
    assert all(a["non_llm"] is True for a in artifacts), "LLM artifacts are excluded from this corpus"
    categories = Counter(a["category"] for a in artifacts)
    required_categories = {
        "database_query_transaction", "distributed_streaming", "compression_storage",
        "programming_languages_compilers", "information_retrieval", "visualization_hci",
        "statistics_ml_predictive", "process_mining", "graph_spatial_scientific",
        "optimization_control", "security_privacy", "quality_governance_provenance",
    }
    assert required_categories <= categories.keys(), required_categories - categories.keys()
    assert all(categories[c] >= 8 for c in required_categories), categories

    all_rows = [r for rows in data.values() for r in rows]
    ids = [r["id"] for r in all_rows]
    duplicate_ids = [k for k, n in Counter(ids).items() if n > 1]
    assert not duplicate_ids, f"duplicate IDs: {duplicate_ids[:10]}"
    index = {r["id"]: r for r in all_rows}

    artifact_ids = {a["id"] for a in artifacts}
    work_ids = {w["id"] for w in data["works.jsonl"]}
    edition_ids = {e["id"] for e in data["editions.jsonl"]}
    occurrence_ids = {o["id"] for o in data["venue-occurrences.jsonl"]}
    source_ids = {s["id"] for s in data["sources.jsonl"]}
    evidence_ids = {e["id"] for e in data["evidence.jsonl"]}
    person_ids = {p["id"] for p in data["people.jsonl"]}
    review_artifacts = {r["artifact_id"] for r in data["review-queue.jsonl"] if "artifact_id" in r}
    mapping_artifacts = {m["artifact_id"] for m in data["compiler-library-mappings.jsonl"]}

    assert len(source_ids) == len(artifacts), "one primary source occurrence per candidate artifact required"
    assert len(evidence_ids) == len(artifacts), "one evidence scope per candidate artifact required"
    assert len(work_ids) == len(artifacts) == len(edition_ids) == len(occurrence_ids)
    for edition in data["editions.jsonl"]:
        assert edition["work_id"] in work_ids
    for occurrence in data["venue-occurrences.jsonl"]:
        assert occurrence["edition_id"] in edition_ids
    for source in data["sources.jsonl"]:
        assert source["artifact_id"] in artifact_ids
        assert source["url"].startswith("https://")
    for ev in data["evidence.jsonl"]:
        assert ev["artifact_id"] in artifact_ids
        assert ev["source_id"] in source_ids
        assert ev["excludes"], f"unbounded evidence scope: {ev['id']}"

    by_artifact = defaultdict(list)
    for c in data["contributions.jsonl"]:
        assert c["artifact_id"] in artifact_ids
        assert c["person_id"] in person_ids
        assert c["does_not_establish"], c["id"]
        by_artifact[c["artifact_id"]].append(c)
    assert set(by_artifact) == artifact_ids, "every artifact needs contributor credit records"
    for aid, rows in by_artifact.items():
        ordinals = sorted(r["ordinal"] for r in rows)
        assert ordinals == list(range(1, len(rows) + 1)), f"noncontiguous credit order: {aid}"

    for artifact in artifacts:
        assert artifact["identity_basis"] == "title+year+primary_url+edition"
        assert artifact["work_id"] in work_ids
        assert artifact["edition_id"] in edition_ids
        assert artifact["venue_occurrence_id"] in occurrence_ids
        assert artifact["do_not_infer"], artifact["id"]
        if artifact["extraction_status"] == "metadata_only":
            assert artifact["id"] in review_artifacts, f"metadata-only artifact not queued: {artifact['id']}"
        else:
            assert artifact["id"] in mapping_artifacts, f"deep artifact missing compiler mapping: {artifact['id']}"

    relation_types = {r["label"] for r in data["relation-ontology.jsonl"]}
    for rel in data["relations.jsonl"]:
        assert rel["relation_type"] in relation_types, rel["id"]
        assert rel["from_id"] in index, f"missing from ref: {rel['id']}"
        assert rel["to_id"] in index, f"missing to ref: {rel['id']}"
        assert rel["evidence_id"] in evidence_ids, f"missing evidence ref: {rel['id']}"

    for claim in data["claims.jsonl"]:
        assert claim["artifact_id"] in artifact_ids
        assert claim["assumptions"] and claim["limitations"]
        assert set(claim["evidence_ids"]) <= evidence_ids
    for mapping in data["compiler-library-mappings.jsonl"]:
        assert mapping["binding_status"] == "research_candidate_not_bindable"
        assert mapping["proof_obligations"]
    supplement_ids = {s["id"] for s in data["supplementary-artifacts.jsonl"]}
    for supplement in data["supplementary-artifacts.jsonl"]:
        assert supplement["research_artifact_id"] in artifact_ids
        assert supplement["version_or_digest"] and supplement["license"]
    benchmark_ids = {b["id"] for b in data["benchmarks.jsonl"]}
    for evaluation in data["evaluations.jsonl"]:
        assert evaluation["artifact_id"] in artifact_ids
        assert "effect_size" in evaluation and "uncertainty" in evaluation
        assert evaluation["threats"] and evaluation["qualification_status"]
        assert set(evaluation["data_or_benchmark_ids"]) <= supplement_ids | benchmark_ids
    for limitation in data["limitations-threats.jsonl"]:
        assert limitation["artifact_id"] in artifact_ids
    for replication in data["replications.jsonl"]:
        if replication["subject_artifact_id"] is not None:
            assert replication["subject_artifact_id"] in artifact_ids
        if replication["replicating_artifact_id"] is not None:
            assert replication["replicating_artifact_id"] in artifact_ids
    for adjudication in data["contradictions-supersessions.jsonl"]:
        assert set(adjudication["subject_ids"]) <= artifact_ids
        assert adjudication["contradiction_status"] and adjudication["supersession_status"]
    for name in ["formalisms.jsonl", "research-types.jsonl", "models.jsonl", "estimators.jsonl", "guarantees.jsonl"]:
        for row in data[name]:
            assert set(row["artifact_ids"]) <= artifact_ids, f"bad artifact ref: {row['id']}"

    laws = {r["id"] for r in data["conversion-rules.jsonl"]}
    required_laws = {
        "conversion_rule.publication_not_concept", "conversion_rule.claim_not_law",
        "conversion_rule.method_algorithm_implementation_split", "conversion_rule.benchmark_not_qualification",
        "conversion_rule.author_not_inventor", "conversion_rule.predictive_model_contract",
        "conversion_rule.process_state_contract", "conversion_rule.event_transform_contract",
    }
    assert required_laws <= laws, required_laws - laws

    conflict_cases = {c["id"] for c in data["conflict-replication.jsonl"]}
    assert "case.fahland_attribution" in conflict_cases
    assert "case.ocel_oced_tekg" in conflict_cases
    assert any(g["id"] == "gap.cs_saturation" for g in data["gaps.jsonl"])

    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["coverage"]["artifacts_total"] == len(artifacts)
    assert manifest["coverage"]["recent_2021_2026"] >= 35
    assert manifest["coverage"]["foundational_le_2020"] >= 35
    assert manifest["constitutional_posture"] == "open_world_governed_extension"

    print(
        "PASS research artifact graph: "
        f"{len(artifacts)} artifacts, {len(categories)} fields, "
        f"{len(data['people.jsonl'])} contributor identities, "
        f"{len(data['claims.jsonl'])} deep claims, "
        f"{len(data['compiler-library-mappings.jsonl'])} compiler mappings, "
        f"{len(data['review-queue.jsonl'])} review items"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="rebuild and verify byte-for-byte determinism")
    validate(parser.parse_args().rebuild)
