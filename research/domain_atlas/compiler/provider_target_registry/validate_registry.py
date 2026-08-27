#!/usr/bin/env python3
"""Validate structure, references, evidence scope and physical-binding laws."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema"
REPO_ROOT = ROOT.parents[3]

FILES = {
    "sources": ("sources.jsonl", "source.schema.json", "source_id"),
    "contexts": ("context-candidates.jsonl", "context.schema.json", "context_id"),
    "capabilities": ("capability-classes.jsonl", "capability-class.schema.json", "capability_class_id"),
    "provider_classes": ("provider-classes.jsonl", "provider-class.schema.json", "provider_class_id"),
    "provider_organizations": ("provider-organizations.jsonl", "provider-organization.schema.json", "provider_organization_id"),
    "artifacts": ("implementation-artifacts.jsonl", "implementation-artifact.schema.json", "artifact_id"),
    "offers": ("concrete-offers.jsonl", "concrete-offer.schema.json", "offer_id"),
    "target_profiles": ("target-profiles.jsonl", "target-profile.schema.json", "target_profile_id"),
    "target_occurrences": ("target-occurrences.jsonl", "target-occurrence.schema.json", "target_occurrence_id"),
    "resource_evidence": ("resource-limit-cost-evidence.jsonl", "resource-evidence.schema.json", "resource_evidence_id"),
    "qualification": ("qualification-receipts.jsonl", "qualification-receipt.schema.json", "qualification_receipt_id"),
    "compatibility": ("compatibility-matrix.jsonl", "compatibility.schema.json", "compatibility_id"),
    "decisions": ("decisions.jsonl", "decision.schema.json", "decision_id"),
    "rules": ("refusal-invalidation-rules.jsonl", "rule.schema.json", "rule_id"),
    "mappings": ("compiler-requirement-offer-mappings.jsonl", "compiler-mapping.schema.json", "mapping_id"),
    "boundaries": ("library-adapter-boundaries.jsonl", "library-boundary.schema.json", "boundary_id"),
    "innovations": ("innovations.jsonl", "innovation.schema.json", "innovation_id"),
    "gaps": ("gaps.jsonl", "gap.schema.json", "gap_id"),
}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    for line_no, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path.name}:{line_no}: invalid JSON: {exc}") from exc
    return records


def schema_validate(records: list[dict], schema_path: Path, label: str) -> None:
    try:
        import jsonschema
    except ImportError:
        return
    validator = jsonschema.Draft202012Validator(json.loads(schema_path.read_text()), format_checker=jsonschema.FormatChecker())
    for index, record in enumerate(records, 1):
        errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
        if errors:
            detail = "; ".join(f"{list(error.path)}: {error.message}" for error in errors[:5])
            raise AssertionError(f"{label}:{index}: {detail}")


def ids(records: list[dict], field: str, label: str) -> set[str]:
    values = [record[field] for record in records]
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    assert not duplicates, f"{label}: duplicate {field}: {duplicates}"
    return set(values)


def values(records: list[dict], fields: list[str]) -> set[str]:
    found: set[str] = set()
    for record in records:
        for field in fields:
            value = record.get(field, [])
            if isinstance(value, str):
                found.add(value)
            elif isinstance(value, list):
                found.update(value)
    return found


def file_digests() -> dict[str, str]:
    paths = [ROOT / spec[0] for spec in FILES.values()] + [ROOT / "manifest.json", ROOT / "metamodel.json"] + sorted(SCHEMA.glob("*.json"))
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def main() -> None:
    data: dict[str, list[dict]] = {}
    idsets: dict[str, set[str]] = {}
    for label, (filename, schema_name, id_field) in FILES.items():
        data[label] = load_jsonl(ROOT / filename)
        schema_validate(data[label], SCHEMA / schema_name, label)
        idsets[label] = ids(data[label], id_field, label)

    # Thresholds requested by the work package.
    core_count = sum(len(data[label]) for label in ["capabilities", "offers", "target_profiles", "target_occurrences", "decisions"])
    assert len(data["sources"]) >= 60
    assert len(data["contexts"]) >= 30
    assert core_count >= 180
    assert len(data["innovations"]) >= 20
    assert all(2021 <= record["year"] <= 2026 and record["non_llm"] is True for record in data["innovations"])

    # Sources are primary/official and mutable claims have a retrieval date and explicit scope limit.
    assert all(record["primary_official"] is True for record in data["sources"])
    assert len({record["url"] for record in data["sources"]}) == len(data["sources"])
    assert all(record["retrieved_at"] and record["authority_scope"] and record["limitations"] for record in data["sources"])
    assert all(record["retrieved_at"] == "2026-08-25" for record in data["sources"] if record["mutable"])

    source_ids = idsets["sources"]
    evidence_refs = set()
    for label, fields in {
        "contexts": ["evidence_refs"], "capabilities": ["evidence_refs"], "provider_classes": ["evidence_refs"],
        "provider_organizations": ["evidence_refs"], "artifacts": ["evidence_refs"], "offers": ["evidence_refs"],
        "target_profiles": ["evidence_refs"], "target_occurrences": ["evidence_refs"], "resource_evidence": ["source_refs"],
        "qualification": ["evidence_refs"], "compatibility": ["evidence_refs"], "boundaries": ["evidence_refs"],
        "innovations": ["evidence_refs"], "gaps": ["evidence_refs"],
    }.items():
        evidence_refs.update(values(data[label], fields))
    assert not (evidence_refs - source_ids), f"unknown source refs: {sorted(evidence_refs - source_ids)}"

    capability_ids = idsets["capabilities"]
    capability_refs = set()
    for label, fields in {
        "provider_classes": ["may_offer"], "artifacts": ["capability_class_refs"], "offers": ["capability_class_refs"],
        "qualification": ["capability_class_refs"], "compatibility": ["capability_class_ref"], "mappings": ["capability_class_refs"],
        "innovations": ["affected_capability_refs"],
    }.items():
        capability_refs.update(values(data[label], fields))
    assert not (capability_refs - capability_ids), f"unknown capability refs: {sorted(capability_refs - capability_ids)}"

    assert not (values(data["provider_organizations"], ["provider_class_refs"]) - idsets["provider_classes"])
    assert not ({record["provider_class_ref"] for record in data["offers"]} - idsets["provider_classes"])
    organization_classes = {record["provider_organization_id"]: set(record["provider_class_refs"]) for record in data["provider_organizations"]}
    assert all(record["provider_class_ref"] in organization_classes[record["provider_organization_ref"]] for record in data["offers"]), "offer provider class is not declared by its organization"
    assert not ({record["maintainer_ref"] for record in data["artifacts"]} - idsets["provider_organizations"])
    assert not ({record["provider_organization_ref"] for record in data["offers"] + data["target_occurrences"]} - idsets["provider_organizations"])
    assert not ({record["artifact_ref"] for record in data["offers"]} - idsets["artifacts"])
    assert not (values(data["offers"], ["target_profile_refs"]) - idsets["target_profiles"])
    assert not ({record["target_profile_ref"] for record in data["target_occurrences"]} - idsets["target_profiles"])
    assert not ({record["offer_ref"] for record in data["target_occurrences"]} - idsets["offers"])
    assert not ({record["target_occurrence_ref"] for record in data["qualification"]} - idsets["target_occurrences"])
    assert not ({record["subject_ref"] for record in data["qualification"]} - idsets["offers"])
    assert not (values(data["mappings"], ["offer_candidate_refs"]) - idsets["offers"])
    assert not (values(data["mappings"], ["invalidation_rule_refs"]) - idsets["rules"])

    offer_or_occurrence = idsets["offers"] | idsets["target_occurrences"]
    assert not ({record["subject_ref"] for record in data["resource_evidence"]} - offer_or_occurrence)
    all_registry_ids = set().union(*idsets.values())
    assert not ({record["subject_ref"] for record in data["gaps"]} - all_registry_ids)
    compat_allowed = idsets["offers"] | idsets["artifacts"] | idsets["target_profiles"] | idsets["target_occurrences"]
    assert not ({record["left_ref"] for record in data["compatibility"]} - compat_allowed)
    assert not ({record["right_ref"] for record in data["compatibility"]} - compat_allowed)

    # Identity and evidence distinctions are structural, not prose conventions.
    forbidden_offer_fields = {"semantic_owner", "canonical_semantics", "target_occurrence_id"}
    assert all(not (forbidden_offer_fields & set(record)) for record in data["offers"])
    assert all(record["semantic_ownership_forbidden"] is True for record in data["provider_organizations"])
    assert all(record["non_semantic_owner"] is True for record in data["capabilities"])
    assert {record["library_or_engine_or_service"] for record in data["artifacts"]} >= {"library", "engine", "runtime", "service"}
    assert all("availability_regions" in record and "residency_guarantee" in record for record in data["target_occurrences"])

    # The exact LP pilot uses implementation/interface offers, not provider-project facades.
    offers_by_id = {record["offer_id"]: record for record in data["offers"]}
    ortools_offer_id = "offer.ptr.ortools.glop_mpsolver_python.9_15_6755"
    highs_offer_id = "offer.ptr.highspy.highs.1_15_1"
    cp_sat_offer_id = "offer.ptr.ortools.cp_sat_python.9_15_6755"
    assert {ortools_offer_id, highs_offer_id, cp_sat_offer_id} <= set(offers_by_id)
    precise_capability = "capability.ptr.optimization_solver.precise_infeasible_unbounded_classification"
    assert precise_capability not in offers_by_id[ortools_offer_id]["capability_class_refs"]
    assert precise_capability in offers_by_id[highs_offer_id]["capability_class_refs"]
    assert {
        "capability.ptr.optimization_solver.bounded_integer_cp_sat_execution",
        "capability.ptr.optimization_solver.complete_solution_enumeration",
        "capability.ptr.optimization_solver.unknown_limit_status_preservation",
    } <= set(offers_by_id[cp_sat_offer_id]["capability_class_refs"])

    # Concrete mutable offers are versioned and dated, but documentation snapshots are deliberately not binding eligible.
    for record in data["offers"]:
        assert record["status"] == "candidate"
        assert record["artifact_version"] and record["offer_snapshot"]
        assert record["retrieved_at"] == "2026-08-25" and record["observed_at"] == "2026-08-25"
        assert record["binding_eligible"] is False
        triggers = " ".join(record["validity"]["recheck_triggers"])
        assert all(word in triggers for word in ["version", "configuration", "target"])
        assert any("No universal support" in text for text in record["exclusions"])

    # Every occurrence and mapping carries a non-empty finite budget. Strings are closed constraints, never infinity.
    for record in data["target_occurrences"]:
        assert record["finite_budget"]
        for value in record["finite_budget"].values():
            if isinstance(value, (int, float)):
                assert math.isfinite(value) and value >= 0
            else:
                assert value and not re.search(r"(?i)unbounded|infinite|unlimited", value)
        assert record["binding_eligible"] is False, "documentation occurrence must not masquerade as deployment qualification"
    assert all(record["finite_budget_dimensions"] for record in data["mappings"])
    assert all(record["fallback_law"] in {"refuse", "typed_degradation_only_if_declared"} for record in data["mappings"])

    # Documented/probed limits and list/measured cost are different record kinds with fail-closed evidence status.
    evidence_kinds = {record["evidence_kind"] for record in data["resource_evidence"]}
    assert {"documented_limit", "probed_limit", "list_price", "measured_cost", "quota_observation"} <= evidence_kinds
    for record in data["resource_evidence"]:
        if record["evidence_kind"] in {"list_price", "measured_cost"}:
            assert record["binding_eligible"] is False
        if record["value"] is None:
            assert record["binding_eligible"] is False and record["status"] == "unobserved_gap"

    # Documentation review, executed testing and independent appraisal remain different evidence classes.
    receipt_cache: dict[Path, dict[str, dict]] = {}
    expected_external_subjects = {
        ortools_offer_id: "offer.operations_research.ortools.glop.mpsolver_python.9_15_6755",
        highs_offer_id: "offer.operations_research.highspy.highs.1_15_1",
        cp_sat_offer_id: "offer.operations_research.ortools.cp_sat.python.9_15_6755",
    }
    for record in data["qualification"]:
        assert record["performance_result"] == "not_tested"
        assert record["independent_appraisal"] is False
        triggers = " ".join(record["invalidation_triggers"])
        assert all(word in triggers for word in ["version", "configuration", "target"])
        if record["evidence_class"] == "documentation_review":
            assert record["outcome"] == "inconclusive"
            assert record["semantic_conformance"] == "not_tested"
            assert not record["evidence_object_refs"] and not record["execution_receipt_refs"]
            continue
        assert record["evidence_class"] == "executed_test"
        assert record["evidence_object_refs"] and record["execution_receipt_refs"]
        assert record["subject_ref"] in expected_external_subjects
        assert record["outcome"] == ("rejected" if record["semantic_conformance"] == "fail" else "inconclusive")
        assert record["semantic_conformance"] in {"pass", "fail"}
        for relative in record["evidence_object_refs"]:
            path = REPO_ROOT / relative
            assert path.exists(), f"missing retained execution evidence: {relative}"
            if path not in receipt_cache:
                receipt_cache[path] = {item["receipt_id"]: item for item in load_jsonl(path)}
            for receipt_ref in record["execution_receipt_refs"]:
                assert receipt_ref in receipt_cache[path], f"missing external receipt: {receipt_ref}"
                external = receipt_cache[path][receipt_ref]
                assert external["subject"] == expected_external_subjects[record["subject_ref"]]
                assert external["verdict"] == record["semantic_conformance"]
                assert external["independent_appraiser"] is None

    assert not any(record["outcome"] == "qualified" for record in data["qualification"])
    executed = [record for record in data["qualification"] if record["evidence_class"] == "executed_test"]
    assert len(executed) == 10
    assert sum(record["semantic_conformance"] == "pass" for record in executed) == 8
    assert sum(record["semantic_conformance"] == "fail" for record in executed) == 2
    cp_sat_executed = [record for record in executed if record["subject_ref"] == cp_sat_offer_id]
    assert len(cp_sat_executed) == 6
    assert {record["test_or_oracle"] for record in cp_sat_executed if record["semantic_conformance"] == "pass"} == {
        "profile.cpsat.core", "profile.cpsat.global_constraints", "profile.cpsat.scheduling",
        "profile.cpsat.enumeration", "profile.cpsat.limit_no_strengthening",
    }
    assert [record["test_or_oracle"] for record in cp_sat_executed if record["semantic_conformance"] == "fail"] == [
        "profile.cpsat.enumeration"
    ]

    # Target-scoped native-extension cohabitation evidence is retained without globalizing the result.
    for record in data["compatibility"]:
        for relative in record["evidence_object_refs"]:
            assert (REPO_ROOT / relative).exists(), f"missing compatibility evidence object: {relative}"
    cohabitation = next(record for record in data["compatibility"] if record["compatibility_id"] == "compatibility.ptr.ortools_highspy.same_python_process.local_darwin_arm64_python3_14_7")
    assert cohabitation["result"] == "incompatible"
    assert cohabitation["evidence_object_refs"]
    cp_sat_pre = next(record for record in data["compatibility"] if record["compatibility_id"] == "compatibility.ptr.ortools_cp_sat_python.9_15_6755.pre_enumeration_adapter")
    cp_sat_corrected = next(record for record in data["compatibility"] if record["compatibility_id"] == "compatibility.ptr.ortools_cp_sat_python.9_15_6755.enumeration_adapter_v2")
    assert cp_sat_pre["result"] == "incompatible" and cp_sat_corrected["result"] == "conditional"
    assert cp_sat_pre["left_ref"] == cp_sat_corrected["left_ref"] == cp_sat_offer_id
    assert cp_sat_pre["right_ref"] != cp_sat_corrected["right_ref"], "adapter configurations require distinct occurrences"

    # Refusal and invalidation surfaces must close all dangerous shortcuts.
    rule_text = " ".join(json.dumps(record, sort_keys=True) for record in data["rules"]).lower()
    for phrase in ["vendor", "unbounded", "documented limit", "list-price", "performance", "residency", "degradation", "artifact", "configuration", "target", "price", "quota", "evidence", "callback", "model class"]:
        assert phrase in rule_text, f"missing refusal/invalidation surface: {phrase}"
    assert all(record["default_law"] == "forbidden" for record in data["decisions"])

    # Core records contain no generative dependency. A refusal rule may name the forbidden dependency.
    forbidden = re.compile(r"(?i)\b(prompt|rag|agent[_ -]?memory|large language model|generative model)\b")
    for label in ["capabilities", "provider_classes", "provider_organizations", "artifacts", "offers", "target_profiles", "target_occurrences", "resource_evidence", "qualification", "compatibility", "decisions", "mappings", "boundaries", "innovations"]:
        for index, record in enumerate(data[label], 1):
            assert not forbidden.search(json.dumps(record)), f"{label}:{index}: forbidden generative dependency"

    metamodel = json.loads((ROOT / "metamodel.json").read_text())
    assert metamodel["completion_claim"] is False
    for relative in metamodel["reconciled_contracts"]:
        assert (REPO_ROOT / relative).exists(), f"missing reconciled contract: {relative}"

    manifest = json.loads((ROOT / "manifest.json").read_text())
    expected_counts = {spec[0].removesuffix(".jsonl").replace("-", "_"): len(data[label]) for label, spec in FILES.items()}
    assert manifest["counts"] == expected_counts, "manifest counts are stale"
    assert manifest["capability_offer_target_decision_records"] == core_count
    assert manifest["completion_claim"] is False and manifest["status"] == "candidate"

    # Building twice must be byte-for-byte stable for every generated artifact.
    before = file_digests()
    subprocess.run([sys.executable, str(ROOT / "build_registry.py")], check=True, cwd=ROOT)
    after = file_digests()
    assert before == after, "generator output is not deterministic"

    print(
        "PASS provider-target registry: "
        f"{len(data['sources'])} primary/official sources, {len(data['contexts'])} contexts, "
        f"{len(data['capabilities'])} capability classes, {len(data['provider_classes'])} provider classes, "
        f"{len(data['provider_organizations'])} provider organizations, {len(data['artifacts'])} artifacts, "
        f"{len(data['offers'])} concrete offers, {len(data['target_profiles'])} target profiles, "
        f"{len(data['target_occurrences'])} target occurrences, {len(data['resource_evidence'])} resource/limit/cost evidence records, "
        f"{len(data['qualification'])} qualification receipts, {len(data['compatibility'])} compatibility cells, "
        f"{len(data['decisions'])} decisions, {len(data['rules'])} refusal/invalidation rules, "
        f"{len(data['mappings'])} compiler mappings, {len(data['boundaries'])} library/adapter boundaries, "
        f"{len(data['innovations'])} 2021-2026 non-generative innovations, {len(data['gaps'])} open gaps; "
        f"{core_count} capability/offer/target/decision records"
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
