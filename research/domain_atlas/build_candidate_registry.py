#!/usr/bin/env python3
"""Deterministically materialize the context-candidate registry and review queue."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "registry"

PRIORITY = {
    "constitutional-semantics": 100,
    "enterprise-intent-and-outcome": 98,
    "observation-measurement-and-sampling": 97,
    "source-estate": 95,
    "carrier-type-and-admission": 94,
    "data-product-asset-and-publication": 93,
    "connectivity-acquisition-and-movement": 92,
    "analytical-semantics-and-formulas": 91,
    "governance-ownership-and-authority": 90,
    "security-privacy-and-data-use": 89,
    "lineage-provenance-and-evidence": 88,
    "quality-fitness-and-reconciliation": 87,
    "data-modality-algebras": 86,
    "binding-mapping-and-transformation": 85,
    "change-stream-time-and-finality": 84,
    "analytical-study-and-method": 83,
    "analytical-lifecycle-and-result": 82,
    "decision-proposal-and-action": 81,
    "workflow-orchestration-and-build": 80,
    "persistence-catalog-and-serving": 79,
    "query-planning-and-compute": 78,
    "metadata-ontology-and-discovery": 77,
    "platform-runtime-control-and-economics": 76,
    "evolution-migration-and-assurance": 75,
    "client-consumption-and-collaboration": 74,
}

GAPS = [
    "sovereign_question",
    "positive_negative_charter",
    "ubiquitous_language_false_twins",
    "strategic_tactical_ddd",
    "semantic_laws_oracles",
    "authority_time_failure_models",
    "published_contracts_context_map",
    "compiler_runtime_surfaces",
    "primary_incident_implementation_evidence",
    "independent_adjudication",
]

COVERAGE = {
    "research": "none",
    "strategic_ddd": "none",
    "tactical_ddd": "none",
    "semantic_laws": "none",
    "authority_time_failure": "none",
    "contracts_context_map": "none",
    "compiler_runtime": "none",
    "independent_review": "none",
}


def load(name: str) -> dict:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def title(term: str) -> str:
    return " ".join(word.capitalize() for word in term.split("-"))


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    families = load("context-families.json")["families"]
    ambiguity_terms = {item["term"] for item in load("ownership-ambiguities.json")["ambiguities"]}
    program = load("research-program.json")
    phase_for_family = {
        family_id: phase["phase_id"]
        for phase in program["phases"]
        for family_id in phase["families"]
    }

    records: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for family in families:
        family_id = family["family_id"]
        for seed_term in family["seed_contexts"]:
            key = (family_id, seed_term)
            if key in seen:
                raise ValueError(f"duplicate family seed: {key}")
            seen.add(key)
            records.append(
                {
                    "record_id": f"candidate.{family_id}.{seed_term}",
                    "record_kind": "bounded_context_candidate",
                    "edition": 1,
                    "status": "enumerated",
                    "family_id": family_id,
                    "seed_term": seed_term,
                    "name": title(seed_term),
                    "review_priority": PRIORITY[family_id],
                    "ambiguity_status": "declared" if seed_term in ambiguity_terms else "none",
                    "adjudication": "unreviewed",
                    "sovereign_question": None,
                    "coverage": dict(COVERAGE),
                    "gaps": list(GAPS),
                    "deep_spec_ref": None,
                    "evidence_refs": [],
                }
            )

    records.sort(key=lambda item: (-item["review_priority"], item["family_id"], item["seed_term"]))
    REGISTRY.mkdir(parents=True, exist_ok=True)
    registry_path = REGISTRY / "context-candidates.jsonl"
    registry_path.write_text("".join(canonical_json(record) + "\n" for record in records), encoding="utf-8")

    family_queue = []
    for family in sorted(families, key=lambda item: (-PRIORITY[item["family_id"]], item["family_id"])):
        family_id = family["family_id"]
        family_queue.append(
            {
                "family_id": family_id,
                "phase_id": phase_for_family[family_id],
                "priority": PRIORITY[family_id],
                "candidate_occurrences": len(family["seed_contexts"]),
                "review_batches": [
                    family["seed_contexts"][offset : offset + 10]
                    for offset in range(0, len(family["seed_contexts"]), 10)
                ],
                "exit_gate": "Every candidate has an evidence-backed retain/merge/split/rehome/reject disposition.",
            }
        )
    queue = {
        "queue_id": "san.domain-atlas.review-queue",
        "edition": 1,
        "status": "active",
        "record_count": len(records),
        "family_queue": family_queue,
    }
    (ROOT / "review-queue.json").write_text(canonical_json(queue) + "\n", encoding="utf-8")
    print(f"WROTE {len(records)} candidate records and {len(family_queue)} family review items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
