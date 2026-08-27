"""Validate the analytics landscape catalogue without third-party dependencies."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "analytics_knowledge_base.json"
EXPERT_LEARNING = ROOT / "expert_learning.json"
MACHINE_REGISTRY = ROOT / "composition" / "horizontal_registry.json"
TYPE_TAXONOMY = ROOT / "analytics_type_taxonomy.json"
DATA_ONTOLOGY = ROOT / "data_ontology.json"
DOMAIN_FIELD_PROFILES = ROOT / "domain_field_profiles.json"


def _ids(items: list[dict[str, Any]], label: str) -> set[str]:
    values = [item["id"] for item in items]
    duplicates = sorted(key for key, count in Counter(values).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate {label} ids: {duplicates}")
    return set(values)


def main() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    domain_ids = _ids(data["domains"], "domain")
    type_ids = _ids(data["analytics_types"], "analytics type")
    company_ids = _ids(data["companies"], "company")
    expert_ids = _ids(data["experts"], "expert")
    innovation_ids = _ids(data["innovations"], "innovation")
    source_ids = _ids(data["sources"], "source")

    learning = json.loads(EXPERT_LEARNING.read_text(encoding="utf-8"))
    registry = json.loads(MACHINE_REGISTRY.read_text(encoding="utf-8"))
    machine_ids = _ids(registry["machines"], "machine")
    lesson_expert_values = [item["expert_id"] for item in learning["expert_lessons"]]
    duplicate_lessons = sorted(
        key for key, count in Counter(lesson_expert_values).items() if count > 1
    )
    if duplicate_lessons:
        raise ValueError(f"experts with duplicate learning records: {duplicate_lessons}")
    lesson_expert_ids = set(lesson_expert_values)
    if missing := sorted(expert_ids - lesson_expert_ids):
        raise ValueError(f"experts without learning records: {missing}")
    if unknown := sorted(lesson_expert_ids - expert_ids):
        raise ValueError(f"learning records reference unknown experts: {unknown}")
    for item in learning["expert_lessons"]:
        if len(item["lessons"]) < 2:
            raise ValueError(f"{item['expert_id']} has fewer than two transferable lessons")
        if not item["platform_implications"]:
            raise ValueError(f"{item['expert_id']} has no platform implications")
        if unknown := sorted(set(item["platform_implications"]) - machine_ids):
            raise ValueError(f"{item['expert_id']} references unknown machines: {unknown}")
        if unknown := sorted(set(item["source_ids"]) - source_ids):
            raise ValueError(f"{item['expert_id']} learning has unknown sources: {unknown}")
        catalog_sources = next(
            expert["source_ids"] for expert in data["experts"] if expert["id"] == item["expert_id"]
        )
        if not set(item["source_ids"]) & set(catalog_sources):
            raise ValueError(f"{item['expert_id']} learning does not cite its expert evidence")

    queue_ids = _ids(learning["expert_research_queue"], "expert research queue")
    principle_ids = _ids(learning["cross_expert_principles"], "cross-expert principle")

    taxonomy = json.loads(TYPE_TAXONOMY.read_text(encoding="utf-8"))
    axes = taxonomy["axes"]
    classification_values = [item["analytics_type_id"] for item in taxonomy["classifications"]]
    duplicate_classifications = sorted(
        key for key, count in Counter(classification_values).items() if count > 1
    )
    if duplicate_classifications:
        raise ValueError(f"duplicate analytics-type classifications: {duplicate_classifications}")
    classified_type_ids = set(classification_values)
    if missing := sorted(type_ids - classified_type_ids):
        raise ValueError(f"analytics types without taxonomy classification: {missing}")
    if unknown := sorted(classified_type_ids - type_ids):
        raise ValueError(f"taxonomy references unknown analytics types: {unknown}")
    expected_keys = set(axes) | {"analytics_type_id"}
    for item in taxonomy["classifications"]:
        actual_keys = set(item)
        if missing_axes := sorted(expected_keys - actual_keys):
            raise ValueError(f"{item['analytics_type_id']} lacks taxonomy axes: {missing_axes}")
        if extra_axes := sorted(actual_keys - expected_keys):
            raise ValueError(f"{item['analytics_type_id']} has unknown taxonomy axes: {extra_axes}")
        for axis_id, axis in axes.items():
            values = item[axis_id]
            if not isinstance(values, list) or not values:
                raise ValueError(f"{item['analytics_type_id']}.{axis_id} must be a non-empty list")
            if len(values) != len(set(values)):
                raise ValueError(f"{item['analytics_type_id']}.{axis_id} has duplicate values")
            if unknown_values := sorted(set(values) - set(axis["values"])):
                raise ValueError(
                    f"{item['analytics_type_id']}.{axis_id} has unknown values: {unknown_values}"
                )

    ontology = json.loads(DATA_ONTOLOGY.read_text(encoding="utf-8"))
    standard_ids = _ids(ontology["standards_sources"], "data-ontology standard")
    stack_ids = _ids(ontology["type_stack"], "type-stack level")
    carrier_ids = _ids(ontology["carrier_types"], "carrier type")
    composite_ids = _ids(ontology["composite_types"], "composite type")
    semantic_ids = _ids(ontology["semantic_value_types"], "semantic value type")
    observation_ids = _ids(ontology["observation_types"], "observation type")
    structure_ids = _ids(ontology["analytical_structures"], "analytical structure")
    typing_rule_ids = _ids(ontology["typing_rules"], "typing rule")
    levels = [item["level"] for item in ontology["type_stack"]]
    if levels != list(range(len(levels))):
        raise ValueError(f"type-stack levels must be contiguous from zero: {levels}")
    for item in ontology["standards_sources"]:
        if not item["url"].startswith("https://"):
            raise ValueError(f"ontology source must use HTTPS: {item['id']}")
    for item in ontology["carrier_types"]:
        if unknown := sorted(set(item["source_ids"]) - standard_ids):
            raise ValueError(f"{item['id']} has unknown standards sources: {unknown}")
    for item in ontology["semantic_value_types"]:
        if unknown := sorted(set(item["allowed_carriers"]) - carrier_ids):
            raise ValueError(f"{item['id']} allows unknown carriers: {unknown}")
        if len(item["required_qualifiers"]) != len(set(item["required_qualifiers"])):
            raise ValueError(f"{item['id']} repeats required qualifiers")
        preferred = item.get("preferred_standard")
        if preferred and preferred not in standard_ids:
            raise ValueError(f"{item['id']} has unknown preferred standard {preferred}")
    for collection_name in ("observation_types", "analytical_structures"):
        for item in ontology[collection_name]:
            preferred = item.get("preferred_standard")
            if preferred and preferred not in standard_ids:
                raise ValueError(f"{item['id']} has unknown preferred standard {preferred}")

    shape_values = set(taxonomy["axes"]["data_shape"]["values"])
    shape_bindings = ontology["taxonomy_shape_bindings"]
    if missing := sorted(shape_values - set(shape_bindings)):
        raise ValueError(f"taxonomy data shapes without ontology bindings: {missing}")
    if unknown := sorted(set(shape_bindings) - shape_values):
        raise ValueError(f"ontology binds unknown taxonomy data shapes: {unknown}")
    if unknown := sorted(set(shape_bindings.values()) - structure_ids):
        raise ValueError(f"data-shape bindings reference unknown structures: {unknown}")

    profile_data = json.loads(DOMAIN_FIELD_PROFILES.read_text(encoding="utf-8"))
    profiles = profile_data["profiles"]
    profile_ids = _ids(profiles, "domain field profile")
    domain_pack_ids = {
        pack["id"]
        for path in (ROOT / "composition" / "domain_packs").glob("*.json")
        for pack in [json.loads(path.read_text(encoding="utf-8"))]
    }
    missingness_values = set(ontology["classification_axes"]["missingness"])
    temporal_values = set(ontology["classification_axes"]["temporality"])
    for profile in profiles:
        if profile["domain_pack_id"] not in domain_pack_ids:
            raise ValueError(f"{profile['id']} has unknown domain pack {profile['domain_pack_id']}")
        if profile["observation_type_id"] not in observation_ids:
            raise ValueError(
                f"{profile['id']} has unknown observation type {profile['observation_type_id']}"
            )
        if unknown := sorted(set(profile.get("source_ids", [])) - standard_ids):
            raise ValueError(f"{profile['id']} has unknown ontology sources: {unknown}")
        field_names = [field["name"] for field in profile["fields"]]
        if duplicates := sorted(
            key for key, count in Counter(field_names).items() if count > 1
        ):
            raise ValueError(f"{profile['id']} has duplicate fields: {duplicates}")
        field_name_set = set(field_names)
        if unknown := sorted(set(profile["primary_key"]) - field_name_set):
            raise ValueError(f"{profile['id']} primary key has unknown fields: {unknown}")
        if unknown := sorted(set(profile["grain_fields"]) - field_name_set):
            raise ValueError(f"{profile['id']} grain has unknown fields: {unknown}")
        temporal_roles = set(profile["temporal_model"]["roles"])
        if unknown := sorted(temporal_roles - temporal_values):
            raise ValueError(f"{profile['id']} has unknown temporal roles: {unknown}")
        represented_roles = {role for field in profile["fields"] for role in field["roles"]}
        if missing := sorted(temporal_roles - represented_roles):
            raise ValueError(f"{profile['id']} lacks fields for temporal roles: {missing}")
        semantic_by_id = {item["id"]: item for item in ontology["semantic_value_types"]}
        for field in profile["fields"]:
            if field["carrier_type_id"] not in carrier_ids:
                raise ValueError(f"{profile['id']}.{field['name']} has unknown carrier")
            if unknown := sorted(set(field.get("composite_type_ids", [])) - composite_ids):
                raise ValueError(
                    f"{profile['id']}.{field['name']} has unknown composite types: {unknown}"
                )
            semantic = semantic_by_id.get(field["semantic_type_id"])
            if semantic is None:
                raise ValueError(f"{profile['id']}.{field['name']} has unknown semantic type")
            if field["carrier_type_id"] not in semantic["allowed_carriers"]:
                raise ValueError(
                    f"{profile['id']}.{field['name']} carrier is invalid for {semantic['id']}"
                )
            if missing := sorted(set(semantic["required_qualifiers"]) - set(field["qualifiers"])):
                raise ValueError(
                    f"{profile['id']}.{field['name']} lacks semantic qualifiers: {missing}"
                )
            if unknown := sorted(set(field["missingness_allowed"]) - missingness_values):
                raise ValueError(
                    f"{profile['id']}.{field['name']} has unknown missingness: {unknown}"
                )
            if not field["nullable"] and set(field["missingness_allowed"]) != {"present"}:
                raise ValueError(
                    f"{profile['id']}.{field['name']} is non-nullable but allows absence"
                )
            if not field.get("provenance_required"):
                raise ValueError(f"{profile['id']}.{field['name']} does not require provenance")

    for item in data["analytics_types"]:
        if item["domain_id"] not in domain_ids:
            raise ValueError(f"{item['id']} has unknown domain {item['domain_id']}")

    for collection_name in ("companies", "experts"):
        for item in data[collection_name]:
            if not item["source_ids"]:
                raise ValueError(f"{item['id']} has no supporting source")
            unknown = set(item["analytics_type_ids"]) - type_ids
            if unknown:
                raise ValueError(f"{item['id']} has unknown analytics types: {sorted(unknown)}")
            unknown_sources = set(item["source_ids"]) - source_ids
            if unknown_sources:
                raise ValueError(f"{item['id']} has unknown sources: {sorted(unknown_sources)}")

    for item in data["innovations"]:
        if not item["source_ids"]:
            raise ValueError(f"{item['id']} has no supporting source")
        unknown_types = set(item["analytics_type_ids"]) - type_ids
        unknown_companies = set(item["company_ids"]) - company_ids
        unknown_experts = set(item["expert_ids"]) - expert_ids
        unknown_sources = set(item["source_ids"]) - source_ids
        if unknown_types:
            raise ValueError(f"{item['id']} has unknown analytics types: {sorted(unknown_types)}")
        if unknown_companies:
            raise ValueError(f"{item['id']} has unknown companies: {sorted(unknown_companies)}")
        if unknown_experts:
            raise ValueError(f"{item['id']} has unknown experts: {sorted(unknown_experts)}")
        if unknown_sources:
            raise ValueError(f"{item['id']} has unknown sources: {sorted(unknown_sources)}")

    for relation in data["relationships"]:
        if relation["company_id"] not in company_ids:
            raise ValueError(f"relationship has unknown company {relation['company_id']}")
        if relation["expert_id"] not in expert_ids:
            raise ValueError(f"relationship has unknown expert {relation['expert_id']}")
        if relation["analytics_type_id"] not in type_ids:
            raise ValueError(
                f"relationship has unknown analytics type {relation['analytics_type_id']}"
            )
        if relation["source_id"] not in source_ids:
            raise ValueError(f"relationship has unknown source {relation['source_id']}")

    deep_days = int(data["review"]["cadence"]["deep_days"])
    stale_before = date.fromisoformat(data["metadata"]["as_of"]) - timedelta(days=deep_days)
    stale_domains = []
    domain_coverage: dict[str, dict[str, int]] = {}
    for domain in data["domains"]:
        domain_type_ids = {
            item["id"] for item in data["analytics_types"] if item["domain_id"] == domain["id"]
        }
        coverage = {
            "analytics_types": len(domain_type_ids),
            "companies": sum(
                bool(set(item["analytics_type_ids"]) & domain_type_ids)
                for item in data["companies"]
            ),
            "experts": sum(
                bool(set(item["analytics_type_ids"]) & domain_type_ids)
                for item in data["experts"]
            ),
            "innovations": sum(
                bool(set(item["analytics_type_ids"]) & domain_type_ids)
                for item in data["innovations"]
            ),
        }
        domain_coverage[domain["id"]] = coverage
        if domain["coverage_status"] == "reviewed":
            if not domain["last_reviewed"]:
                raise ValueError(f"reviewed domain {domain['id']} has no last_reviewed date")
            if coverage["companies"] < 5 or coverage["experts"] < 5:
                raise ValueError(
                    f"reviewed domain {domain['id']} does not meet minimum coverage: {coverage}"
                )
        if domain["last_reviewed"]:
            reviewed_at = date.fromisoformat(domain["last_reviewed"])
            if reviewed_at < stale_before:
                stale_domains.append(domain["id"])

    counts = {
        "domains": len(domain_ids),
        "analytics_types": len(type_ids),
        "companies": len(company_ids),
        "experts": len(expert_ids),
        "innovations": len(innovation_ids),
        "sources": len(source_ids),
        "relationships": len(data["relationships"]),
        "expert_learning_records": len(lesson_expert_ids),
        "cross_expert_principles": len(principle_ids),
        "expert_research_queue": len(queue_ids),
        "classification_axes": len(axes),
        "classified_analytics_types": len(classified_type_ids),
        "type_stack_levels": len(stack_ids),
        "carrier_types": len(carrier_ids),
        "composite_types": len(composite_ids),
        "semantic_value_types": len(semantic_ids),
        "observation_types": len(observation_ids),
        "analytical_structures": len(structure_ids),
        "typing_rules": len(typing_rule_ids),
        "domain_field_profiles": len(profile_ids),
    }
    print("catalog valid")
    print(json.dumps(counts, indent=2, sort_keys=True))
    print("domain coverage")
    print(json.dumps(domain_coverage, indent=2, sort_keys=True))
    if stale_domains:
        print(f"stale by cadence: {', '.join(sorted(stale_domains))}")


if __name__ == "__main__":
    main()
