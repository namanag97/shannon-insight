#!/usr/bin/env python3
"""Build lossless research indexes for experts and specialist companies.

The indexes are navigation artifacts, not rankings, endorsements, or completeness claims.
Every source record remains addressable through its source path and source record ID.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SEMANTIC = ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition"


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def stable(values):
    seen = set()
    result = []
    for value in values:
        marker = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if marker not in seen:
            seen.add(marker)
            result.append(value)
    return sorted(result, key=lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False).casefold())


def strings(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def record_id(record: dict) -> str:
    return record.get("expert_id") or record.get("company_id") or record.get("id") or "unidentified"


def expert_sources() -> list[Path]:
    paths = list(SEMANTIC.glob("*/expert-learning-profiles.jsonl"))
    paths += [
        ROOT / "research/domain_atlas/ecosystem/expert_portfolios/experts.jsonl",
        ROOT / "research/domain_atlas/ecosystem/process_mining_expert_pilot/experts.jsonl",
        ROOT / "research/domain_atlas/ecosystem/specialists/experts.jsonl",
        ROOT / "research/domain_atlas/universes/core_semantic_primitives/experts.jsonl",
        ROOT / "research/domain_atlas/universes/operations_research/experts.jsonl",
        ROOT / "research/domain_atlas/universes/predictive_ml_models/experts.jsonl",
    ]
    return sorted(path for path in paths if path.exists())


def build_experts() -> list[dict]:
    grouped = defaultdict(list)
    for path in expert_sources():
        rel = path.relative_to(ROOT).as_posix()
        for record in rows(path):
            if record.get("name"):
                grouped[record["name"].casefold().strip()].append((rel, record))

    output = []
    learning_fields = (
        "lessons_for_composable_platform", "what_corpus_can_learn", "compiler_learning",
        "what_to_learn", "learn", "learnable_contributions", "study_instruction",
    )
    evidence_fields = ("source_refs", "evidence_refs", "artifact_refs", "contribution_ids")
    domain_fields = ("domain", "family", "family_refs", "practice_refs", "expertise", "expertise_claims")
    for records in grouped.values():
        name = records[0][1]["name"]
        learnings, evidence, domains, limits, source_records = [], [], [], [], []
        for path, record in records:
            source_records.append({"path": path, "record_id": record_id(record)})
            for field in learning_fields:
                learnings += strings(record.get(field))
            for field in evidence_fields:
                evidence += strings(record.get(field))
            for field in domain_fields:
                domains += strings(record.get(field))
            limits += strings(record.get("authority_limit"))
            limits += strings(record.get("limitations"))
            limits += strings(record.get("misuse_warning"))
            limits += strings(record.get("role_warning"))
            limits += strings(record.get("authority_law"))
        output.append({
            "aggregate_expert_id": f"expert.aggregate.{slug(name)}",
            "name": name,
            "domain_and_practice_routes": stable(domains),
            "learnable_contributions": stable(learnings),
            "evidence_refs": stable(evidence),
            "source_records": stable(source_records),
            "authority_limits": stable(limits) or ["A research profile is not semantic ownership, qualification authority, endorsement, or a complete bibliography."],
            "status": "LEARNING_PROFILE_NOT_AUTHORITY",
            "ranking_claim": False,
            "completeness_claim": False,
        })
    return sorted(output, key=lambda record: record["aggregate_expert_id"])


def build_companies() -> list[dict]:
    paths = [
        HERE / "companies.jsonl",
        ROOT / "research/domain_atlas/universes/operations_research/companies.jsonl",
    ]
    grouped = defaultdict(list)
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        for record in rows(path):
            key = (record.get("company_id") or record["name"]).split(".")[-1].casefold()
            grouped[key].append((rel, record))

    output = []
    capability_fields = ("claimed_capabilities", "verified_capabilities", "reusable_ip", "vertical_cases")
    for key, records in grouped.items():
        preferred = next((record for _, record in records if "purity" in record), records[0][1])
        names, categories, practices, products, capabilities, industries = [], [], [], [], [], []
        evidence, limits, delivery, source_records = [], [], [], []
        for path, record in records:
            names += strings(record.get("name"))
            categories += strings(record.get("categories")) + strings(record.get("company_pattern"))
            practices += strings(record.get("practice_refs"))
            products += strings(record.get("products_modules")) + strings(record.get("products_or_services"))
            for field in capability_fields:
                capabilities += strings(record.get(field))
            industries += strings(record.get("industry_scope"))
            evidence += strings(record.get("evidence_refs"))
            limits += strings(record.get("limitations"))
            delivery += strings(record.get("delivery_models")) + strings(record.get("delivery_model"))
            source_records.append({"path": path, "record_id": record_id(record)})
        output.append({
            "aggregate_company_id": f"company.aggregate.{key}",
            "name": preferred["name"],
            "also_named": stable(name for name in names if name != preferred["name"]),
            "categories": stable(categories),
            "practice_routes": stable(practices),
            "products_and_modules": stable(products),
            "capability_and_case_claims": stable(capabilities),
            "industry_routes": stable(industries),
            "delivery_models": stable(delivery),
            "evidence_refs": stable(evidence),
            "source_records": stable(source_records),
            "limitations": stable(limits) or ["Open-world research candidate; capability and operating status require recurring evidence review."],
            "purity": preferred.get("purity", {"tier": preferred.get("specialist_posture", "unclassified")}),
            "non_llm_core": preferred.get("non_llm_core", {"status": preferred.get("llm_core_dependency", "unknown")}),
            "operating_status": preferred.get("operating_status", "requires_current_review"),
            "endorsement_claim": False,
            "completeness_claim": False,
        })
    return sorted(output, key=lambda record: record["aggregate_company_id"])


def write_jsonl(path: Path, records: list[dict]):
    path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in records))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    experts = build_experts()
    companies = build_companies()
    expert_path = HERE / "all-experts-registry.jsonl"
    company_path = HERE / "all-specialist-companies-registry.jsonl"
    write_jsonl(expert_path, experts)
    write_jsonl(company_path, companies)
    summary = {
        "status": "RESEARCH_NAVIGATION_INDEX_NOT_EXHAUSTIVE_CENSUS",
        "expert_source_files": len(expert_sources()),
        "expert_source_records": sum(len(rows(path)) for path in expert_sources()),
        "unique_named_experts": len(experts),
        "company_source_files": 2,
        "company_source_records": len(rows(HERE / "companies.jsonl")) + len(rows(ROOT / "research/domain_atlas/universes/operations_research/companies.jsonl")),
        "unique_specialist_company_records": len(companies),
        "outputs": {
            expert_path.name: digest(expert_path),
            company_path.name: digest(company_path),
        },
        "completeness_claim": False,
    }
    (HERE / "consolidated-registry-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
