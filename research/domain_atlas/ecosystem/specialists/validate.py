#!/usr/bin/env python3
"""Validate specialist ecosystem schemas, references, evidence posture, and research gates."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parents[1]
WINDOW_START = date.fromisoformat("2021-08-25")
WINDOW_END = date.fromisoformat("2026-08-25")


def load_jsonl(name: str) -> list[dict]:
    rows = []
    with (ROOT / name).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise AssertionError(f"{name}:{number}: invalid JSON: {error}") from error
    return rows


def index(rows: list[dict], key: str, label: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        value = row[key]
        assert value not in result, f"duplicate {label} id: {value}"
        result[value] = row
    return result


def refs_exist(values, known, owner, kind):
    missing = sorted(set(values) - set(known))
    assert not missing, f"{owner}: missing {kind}: {missing}"


def optional_schema_validation(file_to_schema: dict[str, str]) -> None:
    try:
        import jsonschema  # type: ignore
    except ModuleNotFoundError:
        return
    for filename, schema_name in file_to_schema.items():
        schema = json.loads((ROOT / "schemas" / schema_name).read_text())
        for line_number, row in enumerate(load_jsonl(filename), 1):
            try:
                jsonschema.Draft202012Validator(schema).validate(row)
            except jsonschema.ValidationError as error:
                raise AssertionError(f"{filename}:{line_number}: schema: {error.message}") from error


def main() -> None:
    policy = json.loads((ROOT / "inclusion-policy.json").read_text())
    gaps = json.loads((ROOT / "coverage-gaps.json").read_text())
    sources = load_jsonl("sources.jsonl")
    companies = load_jsonl("companies.jsonl")
    experts = load_jsonl("experts.jsonl")
    innovations = load_jsonl("innovations.jsonl")
    company_edges = load_jsonl("practice-company-edges.jsonl")
    expert_edges = load_jsonl("expert-practice-edges.jsonl")

    source_by_id = index(sources, "source_id", "source")
    company_by_id = index(companies, "company_id", "company")
    expert_by_id = index(experts, "expert_id", "expert")
    innovation_by_id = index(innovations, "innovation_id", "innovation")
    company_edge_by_id = index(company_edges, "edge_id", "company edge")
    expert_edge_by_id = index(expert_edges, "edge_id", "expert edge")

    practice_path = ATLAS / "universes" / "analytics_types" / "candidate-practices.jsonl"
    practices = {json.loads(line)["practice_id"] for line in practice_path.open()}

    assert policy["completion_claim"] is False
    assert gaps["completion_claim"] is False
    assert len(sources) >= 50, f"authoritative-source gate failed: {len(sources)}"
    authoritative_kinds = {"official_product_docs", "standard", "professional_body", "peer_reviewed_paper", "official_release", "maintained_open_source", "official_profile", "regulator", "customer_primary", "independent_appraisal"}
    assert sum(row["source_kind"] in authoritative_kinds for row in sources) >= 50
    assert len(companies) >= 50, f"company breadth gate failed: {len(companies)}"
    assert len(experts) >= 30, f"expert artifact gate failed: {len(experts)}"
    assert len(innovations) >= 10, f"innovation seed gate failed: {len(innovations)}"
    assert len({row["publisher"] for row in sources}) >= 40, "publisher diversity gate failed"

    for source in sources:
        assert source["url"].startswith("https://"), source["source_id"]
        assert source["supports"], source["source_id"]
        assert source["limitations"], source["source_id"]
        date.fromisoformat(source["accessed_at"])

    eligible_categories = set(policy["eligible_categories"])
    excluded_names = set(policy["excluded_as_primary_examples"])
    company_edge_pairs = {(row["from_id"], row["to_practice_id"]) for row in company_edges}
    expert_edge_pairs = {(row["from_id"], row["to_practice_id"]) for row in expert_edges}

    for company in companies:
        cid = company["company_id"]
        assert company["completeness_claim"] is False, cid
        assert set(company["categories"]) <= eligible_categories, cid
        assert company["name"] not in excluded_names, f"generalist admitted as primary: {cid}"
        assert company["purity"]["primary_record_eligible"] is True, cid
        refs_exist(company["evidence_refs"], source_by_id, cid, "source refs")
        refs_exist(company["practice_refs"], practices, cid, "practice refs")
        assert company["limitations"], cid
        assert company["non_llm_core"]["status"] in {"separable", "partially_separable", "not_applicable", "uncertain"}
        if company["purity"]["tier"] == "quarantined_ai_heavy":
            assert company["non_llm_core"]["quarantined_claims"], f"{cid}: AI-heavy record without quarantine"
        for claim in company["claims"]:
            refs_exist(claim["evidence_refs"], source_by_id, claim["claim_id"], "claim evidence")
            assert claim["limitations"], claim["claim_id"]
        expected = {(cid, practice) for practice in company["practice_refs"]}
        assert expected <= company_edge_pairs, f"{cid}: missing normalized company-practice edge"

    for expert in experts:
        eid = expert["expert_id"]
        assert expert["completeness_claim"] is False and expert["popularity_basis"] is False, eid
        refs_exist(expert["evidence_refs"], source_by_id, eid, "source refs")
        refs_exist(expert["practice_refs"], practices, eid, "practice refs")
        assert expert["what_corpus_can_learn"], eid
        for contribution in expert["contributions"]:
            refs_exist(contribution["evidence_refs"], source_by_id, eid, "contribution evidence")
            assert contribution["artifact"] and contribution["limitations"], eid
        expected = {(eid, practice) for practice in expert["practice_refs"]}
        assert expected <= expert_edge_pairs, f"{eid}: missing normalized expert-practice edge"

    for innovation in innovations:
        iid = innovation["innovation_id"]
        assert innovation["completeness_claim"] is False, iid
        exact = date.fromisoformat(innovation["exact_date"])
        eligible = WINDOW_START <= exact <= WINDOW_END
        assert innovation["window_eligible"] is eligible, f"{iid}: window flag/date mismatch"
        assert eligible, f"{iid}: outside requested five-year window"
        assert innovation["non_llm_status"] in {"none", "quarantined_optional"}, iid
        refs_exist(innovation["evidence_refs"], source_by_id, iid, "source refs")
        refs_exist(innovation["practice_refs"], practices, iid, "practice refs")
        assert innovation["compiler_implications"] and innovation["artifact_refs"], iid
        if innovation["evidence_state"] == "cross_checked":
            publishers = {source_by_id[ref]["publisher"] for ref in innovation["evidence_refs"]}
            assert len(publishers) >= 2 or len(innovation["evidence_refs"]) >= 2, f"{iid}: weak cross-check"

    for edge in company_edges:
        refs_exist([edge["from_id"]], company_by_id, edge["edge_id"], "company")
        refs_exist([edge["to_practice_id"]], practices, edge["edge_id"], "practice")
        refs_exist(edge["evidence_refs"], source_by_id, edge["edge_id"], "evidence")
    for edge in expert_edges:
        refs_exist([edge["from_id"]], expert_by_id, edge["edge_id"], "expert")
        refs_exist([edge["to_practice_id"]], practices, edge["edge_id"], "practice")
        refs_exist(edge["evidence_refs"], source_by_id, edge["edge_id"], "evidence")

    optional_schema_validation({
        "sources.jsonl": "source.schema.json",
        "companies.jsonl": "company.schema.json",
        "experts.jsonl": "expert.schema.json",
        "innovations.jsonl": "innovation.schema.json",
        "practice-company-edges.jsonl": "edge.schema.json",
        "expert-practice-edges.jsonl": "edge.schema.json",
    })

    print(
        "PASS specialist ecosystem: "
        f"{len(sources)} sources / {len({s['publisher'] for s in sources})} publishers, "
        f"{len(company_by_id)} companies/projects, {len(expert_by_id)} experts, "
        f"{len(innovation_by_id)} dated innovations, "
        f"{len(company_edge_by_id) + len(expert_edge_by_id)} practice edges"
    )


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
