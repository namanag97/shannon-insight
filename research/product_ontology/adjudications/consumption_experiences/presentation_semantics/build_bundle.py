#!/usr/bin/env python3
"""Deterministically build machine-readable presentation-semantics projections."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from source_model import HERE, SOURCE, source, source_bytes


SECTION_SPECS: dict[str, tuple[str, str, str]] = {
    "sources": ("evidence.jsonl", "source_id", "evidence_source"),
    "benchmark_archetypes": ("benchmark-archetypes.jsonl", "archetype_id", "benchmark_archetype"),
    "companies": ("companies.jsonl", "company_id", "benchmark_company"),
    "company_feature_observations": ("company-feature-observations.jsonl", "observation_id", "provider_feature_observation"),
    "analytical_result_kinds": ("analytical-result-kinds.jsonl", "result_kind_id", "analytical_result_kind"),
    "question_intents": ("question-intents.jsonl", "question_intent_id", "question_intent"),
    "visual_patterns": ("visual-patterns.jsonl", "visual_pattern_id", "visual_pattern"),
    "intent_visual_bindings": ("intent-visual-bindings.jsonl", "binding_id", "intent_visual_binding"),
    "visual_fitness_constraints": ("visual-fitness-constraints.jsonl", "fitness_rule_id", "visual_fitness_constraint"),
    "specialist_experiences": ("specialist-experiences.jsonl", "specialist_experience_id", "specialist_experience"),
    "interaction_contracts": ("interaction-contracts.jsonl", "interaction_id", "interaction_contract"),
    "presentation_artifacts": ("presentation-artifacts.jsonl", "presentation_artifact_id", "presentation_artifact"),
    "lifecycle_models": ("lifecycle-models.jsonl", "lifecycle_model_id", "lifecycle_model"),
    "semantic_contracts": ("semantic-contracts.jsonl", "semantic_contract_id", "presentation_semantic_contract"),
    "uncertainty_semantics": ("uncertainty-semantics.jsonl", "uncertainty_kind_id", "uncertainty_semantics"),
    "missingness_semantics": ("missingness-semantics.jsonl", "missingness_kind_id", "missingness_semantics"),
    "accessibility_contracts": ("accessibility-contracts.jsonl", "accessibility_contract_id", "accessibility_contract"),
    "provenance_contracts": ("provenance-contracts.jsonl", "provenance_contract_id", "provenance_contract"),
    "policy_projection_contracts": ("policy-projection-contracts.jsonl", "policy_projection_id", "policy_projection_contract"),
    "resource_budgets": ("resource-budgets.jsonl", "resource_budget_id", "presentation_resource_budget"),
    "library_candidates": ("library-candidates.jsonl", "library_candidate_id", "presentation_library_candidate"),
    "compiler_mappings": ("compiler-mappings.jsonl", "compiler_mapping_id", "presentation_compiler_mapping"),
    "canonical_bridges": ("canonical-bridges.jsonl", "canonical_bridge_id", "canonical_bridge"),
    "vertical_acceptance_cases": ("vertical-acceptance-cases.jsonl", "vertical_acceptance_case_id", "vertical_acceptance_case"),
    "saturation_trials": ("saturation-trials.jsonl", "saturation_trial_id", "saturation_trial"),
    "adoption_plan": ("adoption-plan.jsonl", "adoption_phase_id", "adoption_phase"),
    "non_collapse_laws": ("non-collapse-laws.jsonl", "non_collapse_law_id", "non_collapse_law"),
    "negative_tests": ("negative-tests.jsonl", "negative_test_id", "negative_test"),
}


def _line(row: dict[str, Any]) -> bytes:
    return (json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def materialize(payload: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    outputs: dict[str, bytes] = {}
    registry_rows: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for section, (filename, id_field, record_kind) in SECTION_SPECS.items():
        rows = payload[section]
        ordered = sorted(rows, key=lambda row: str(row[id_field]))
        enriched = []
        for row in ordered:
            item = {"record_kind": record_kind, "edition": payload["edition"], **row}
            enriched.append(item)
            registry_rows.append(item)
        outputs[filename] = b"".join(_line(row) for row in enriched)
        counts[record_kind] = len(enriched)

    registry_rows.sort(key=lambda row: (row["record_kind"], next(
        str(row[field]) for field in payload["metamodel"]["identity_fields"] if field in row
    )))
    outputs["registry.jsonl"] = b"".join(_line(row) for row in registry_rows)
    outputs["metamodel.json"] = (
        json.dumps(payload["metamodel"], ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")

    specialist_patterns = sum(1 for row in payload["visual_patterns"] if row["semantic_level"] == "typed_specialist_view")
    mapped_observations = sum(1 for row in payload["company_feature_observations"] if row["normalized_visual_pattern_refs"])
    industries = sorted({row["industry"] for row in payload["vertical_acceptance_cases"]})
    summary = {
        "contract_id": payload["contract_id"],
        "edition": payload["edition"],
        "status": payload["status"],
        "evidence_cutoff": payload["evidence_cutoff"],
        "sources": len(payload["sources"]),
        "benchmark_archetypes": len(payload["benchmark_archetypes"]),
        "companies": len(payload["companies"]),
        "provider_feature_observations": len(payload["company_feature_observations"]),
        "mapped_provider_feature_observations": mapped_observations,
        "analytical_result_kinds": len(payload["analytical_result_kinds"]),
        "question_intents": len(payload["question_intents"]),
        "visual_patterns": len(payload["visual_patterns"]),
        "typed_specialist_visual_patterns": specialist_patterns,
        "specialist_experiences": len(payload["specialist_experiences"]),
        "interaction_contracts": len(payload["interaction_contracts"]),
        "presentation_artifacts": len(payload["presentation_artifacts"]),
        "semantic_contracts": len(payload["semantic_contracts"]),
        "library_candidates": len(payload["library_candidates"]),
        "compiler_mappings": len(payload["compiler_mappings"]),
        "canonical_existing_bridges": sum(
            1 for row in payload["canonical_bridges"]
            if row["status"] == "projects_to_existing_parent_contract_unqualified"
        ),
        "canonical_candidate_vacancies": sum(
            1 for row in payload["canonical_bridges"]
            if row["status"] == "candidate_vacancy_requires_parent_adjudication"
        ),
        "vertical_acceptance_cases": len(payload["vertical_acceptance_cases"]),
        "vertical_industries": len(industries),
        "saturation_trials": len(payload["saturation_trials"]),
        "trailing_zero_new_root_trials": _trailing_zero_new_root_trials(payload["saturation_trials"]),
        "negative_tests": len(payload["negative_tests"]),
        "qualified_providers": 0,
        "ratified_semantic_contracts": 0,
        "completion_claim": False,
    }
    outputs["summary.json"] = (json.dumps(summary, sort_keys=True, indent=2) + "\n").encode("utf-8")

    file_sha256 = {
        filename: hashlib.sha256(content).hexdigest()
        for filename, content in sorted(outputs.items())
    }
    manifest = {
        "contract_id": payload["contract_id"],
        "edition": payload["edition"],
        "source_sha256": hashlib.sha256(source_bytes()).hexdigest(),
        "counts": counts,
        "file_sha256": file_sha256,
        "derived": summary,
    }
    return outputs, manifest


def _trailing_zero_new_root_trials(rows: list[dict[str, Any]]) -> int:
    count = 0
    for row in reversed(rows):
        if row["new_root_semantics"]:
            break
        count += 1
    return count


def write_all() -> None:
    payload = source()
    SOURCE.write_bytes(source_bytes())
    outputs, manifest = materialize(payload)
    for filename, content in outputs.items():
        (HERE / filename).write_bytes(content)
    (HERE / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


def check_all() -> list[str]:
    errors: list[str] = []
    expected_source = source_bytes()
    if not SOURCE.is_file() or SOURCE.read_bytes() != expected_source:
        errors.append("source.json differs from canonical source_model.py")
    outputs, manifest = materialize(source())
    for filename, content in outputs.items():
        path = HERE / filename
        if not path.is_file() or path.read_bytes() != content:
            errors.append(f"missing or stale {filename}")
    manifest_bytes = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path = HERE / "manifest.json"
    if not path.is_file() or path.read_bytes() != manifest_bytes:
        errors.append("missing or stale manifest.json")
    return errors


def main() -> int:
    if "--check" in sys.argv:
        errors = check_all()
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        print("PASS presentation-semantics generated projection is current")
        return 0
    write_all()
    print("WROTE deterministic presentation-semantics projection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
