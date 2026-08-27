#!/usr/bin/env python3
"""Validate the lineage/provenance/evidence universe and deterministic generation."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema"


FILES = {
    "sources": ("sources.jsonl", "source.schema.json", "source_id"),
    "contexts": ("bounded-context-candidates.jsonl", "context.schema.json", "context_id"),
    "entities": ("entity-types.jsonl", "entity-type.schema.json", "entity_type_id"),
    "relations": ("relation-types.jsonl", "relation-type.schema.json", "relation_type_id"),
    "capabilities": ("capability-candidates.jsonl", "capability.schema.json", "capability_id"),
    "rules": ("invariants-refusals.jsonl", "rule.schema.json", "rule_id"),
    "requirements": ("requirements.jsonl", "requirement.schema.json", "requirement_id"),
    "offers": ("offers.jsonl", "offer.schema.json", "offer_id"),
    "mappings": ("compiler-mappings.jsonl", "compiler-mapping.schema.json", "mapping_id"),
    "planes": ("cross-plane-mappings.jsonl", "cross-plane.schema.json", "plane_id"),
    "libraries": ("library-boundaries.jsonl", "library.schema.json", "library_id"),
    "retired_compositions": ("retired-library-compositions.jsonl", "retired-library-composition.schema.json", "decision_id"),
    "innovations": ("innovations.jsonl", "innovation.schema.json", "innovation_id"),
    "gaps": ("gaps.jsonl", "gap.schema.json", "gap_id"),
}


def load_jsonl(name: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{name}:{line_no}: invalid JSON: {exc}") from exc
        assert isinstance(value, dict), f"{name}:{line_no}: JSONL record must be an object"
        records.append(value)
    return records


def unique(records: list[dict[str, Any]], field: str, label: str) -> set[str]:
    values = [record[field] for record in records]
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    assert not duplicates, f"{label}: duplicate {field}: {duplicates}"
    return set(values)


def validate_schema(records: list[dict[str, Any]], schema_name: str, label: str) -> None:
    try:
        import jsonschema
    except ImportError:
        return
    schema = json.loads((SCHEMA / schema_name).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    for index, record in enumerate(records, 1):
        errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
        if errors:
            detail = "; ".join(f"{list(error.path)}: {error.message}" for error in errors[:5])
            raise AssertionError(f"{label}:{index}: {detail}")


def referenced(records: list[dict[str, Any]], fields: list[str]) -> set[str]:
    result: set[str] = set()
    for record in records:
        for field in fields:
            value = record.get(field, [])
            if isinstance(value, str):
                result.add(value)
            elif isinstance(value, list):
                result.update(item for item in value if isinstance(item, str))
    return result


def digest_generated(paths: list[str]) -> dict[str, str]:
    return {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def main() -> None:
    records: dict[str, list[dict[str, Any]]] = {}
    ids: dict[str, set[str]] = {}
    for label, (filename, schema_name, id_field) in FILES.items():
        rows = load_jsonl(filename)
        validate_schema(rows, schema_name, label)
        records[label] = rows
        ids[label] = unique(rows, id_field, label)

    sources = records["sources"]
    contexts = records["contexts"]
    entities = records["entities"]
    relations = records["relations"]
    capabilities = records["capabilities"]
    requirements = records["requirements"]
    offers = records["offers"]
    mappings = records["mappings"]
    planes = records["planes"]
    libraries = records["libraries"]
    innovations = records["innovations"]
    gaps = records["gaps"]

    assert len(sources) >= 45, "at least 45 authoritative primary/official sources required"
    assert len(contexts) >= 35, "at least 35 bounded-context candidates required"
    assert len(capabilities) >= 140, "at least 140 capability/operation/decision/law candidates required"
    assert len(innovations) >= 20, "at least 20 innovations from 2021-2026 required"
    assert len({source["url"] for source in sources}) == len(sources), "source URLs must be unique"
    assert {"W3C", "IETF", "NIST", "OpenLineage"} <= {source["publisher"] for source in sources}
    assert {source["source_kind"] for source in sources} >= {"standard", "official_specification", "regulatory_guidance", "primary_research"}

    # Every generated semantic/research record is explicitly candidate-only. Sources are references.
    for label, rows in records.items():
        if label == "sources":
            assert all(row["status"] == "reference" for row in rows)
        elif label == "retired_compositions":
            assert all(row["status"] == "retired_composition" for row in rows)
        else:
            assert all(row["status"] == "candidate" for row in rows), f"{label}: non-candidate record"

    required_contexts = {
        "prospective-lineage", "retrospective-lineage", "logical-lineage", "physical-lineage",
        "runtime-lineage", "derivation", "activity-execution", "audit-log", "audit-trail",
        "provenance-graph", "provenance-bundle", "evidence-bundle", "claim", "claim-argument",
        "claim-evidence", "attestation", "independent-appraisal", "identity-digest",
        "evidence-freshness", "runtime-receipts", "compiler-receipts", "custody",
        "reproducibility-package", "correction", "retraction", "recall", "deletion-erasure",
        "disclosure", "impact-analysis", "forensic-acquisition", "forensic-preservation",
    }
    assert {f"context.lpe.{name}" for name in required_contexts} <= ids["contexts"], "mandatory distinction context missing"

    # Referential integrity.
    assert not (referenced(contexts, ["neighbor_context_refs"]) - ids["contexts"]), "unknown context neighbor"
    assert not (referenced(entities, ["owner_context_ref"]) - ids["contexts"]), "entity owner context missing"
    assert not (referenced(relations, ["owner_context_ref"]) - ids["contexts"]), "relation owner context missing"
    assert not (referenced(relations, ["source_entity_type_ref", "target_entity_type_ref"]) - ids["entities"]), "relation entity type missing"
    assert not (referenced(capabilities, ["owner_context_ref"]) - ids["contexts"]), "capability owner context missing"
    assert not (referenced(requirements, ["subject_context_ref"]) - ids["contexts"]), "requirement context missing"
    assert not (referenced(requirements, ["operation_ref"]) - ids["capabilities"]), "requirement operation missing"
    assert not (referenced(offers, ["operation_ref"]) - ids["capabilities"]), "offer operation missing"
    assert not (referenced(mappings, ["operation_ref"]) - ids["capabilities"]), "mapping operation missing"
    assert not (referenced(mappings, ["requirement_ref"]) - ids["requirements"]), "mapping requirement missing"
    assert not (referenced(mappings, ["offer_ref"]) - ids["offers"]), "mapping offer missing"
    assert not (referenced(libraries, ["semantic_owner_ref", "contributes_to_context_refs"]) - ids["contexts"]), "library context missing"
    assert not (referenced(libraries, ["operation_refs"]) - ids["capabilities"]), "library operation missing"
    retired = next(row for row in records["retired_compositions"] if row["retired_library_id"] == "library.lpe.prov-core")
    library_by_id = {row["library_id"]: row for row in libraries}
    assert retired["no_compatibility_alias"] is True
    assert "library.lpe.prov-core" not in library_by_id
    assert set(retired["replacement_library_refs"]) == {
        "library.lpe.prov-statement-algebra", "library.lpe.provenance-assertion", "library.lpe.provenance-bundle",
    }
    assert set(retired["operation_partition"]) == set(retired["replacement_library_refs"])
    for ref, expected_owner, expected_trait in [
        ("library.lpe.prov-statement-algebra", "context.lpe.provenance-graph", "ProvStatementAlgebra"),
        ("library.lpe.provenance-assertion", "context.lpe.provenance-assertion", "ProvenanceAssertionAlgebra"),
        ("library.lpe.provenance-bundle", "context.lpe.provenance-bundle", "ProvenanceBundleAlgebra"),
    ]:
        library = library_by_id[ref]
        assert library["semantic_owner_ref"] == expected_owner
        assert library.get("public_traits") == [expected_trait]
        assert len(library.get("operations", [])) >= 4
        assert len(library.get("laws", [])) >= 7 and len(library.get("oracles", [])) >= 5
        assert all(operation.get("input_types") and operation.get("output_type") and operation.get("refusal_types") for operation in library["operations"])
    evidence_bundle = next(row for row in libraries if row["library_id"] == "library.lpe.evidence-bundle")
    assert evidence_bundle.get("public_traits") == ["EvidenceBundleAlgebra"]
    assert len(evidence_bundle.get("public_types", [])) >= 10
    assert len(evidence_bundle.get("operations", [])) == 4
    assert len(evidence_bundle.get("laws", [])) >= 6
    assert len(evidence_bundle.get("oracles", [])) >= 5
    assert "derive_authorized_view" not in {operation["name"] for operation in evidence_bundle["operations"]}
    assert {"disclosure_authorization", "redaction_or_selective_disclosure"} <= set(evidence_bundle["forbidden_responsibilities"])
    assert all(
        operation.get("input_types") and operation.get("output_type")
        and operation.get("refusal_types") and operation.get("purity") == "pure"
        for operation in evidence_bundle["operations"]
    ), "evidence-bundle exact API regressed"
    disclosure = next(row for row in libraries if row["library_id"] == "library.lpe.disclosure-core")
    assert disclosure.get("public_traits") == ["DisclosurePolicyAlgebra", "DisclosureLifecycleReducer"]
    assert len(disclosure.get("public_types", [])) >= 45
    assert len(disclosure.get("operations", [])) == 10
    assert len(disclosure.get("error_contracts", [])) >= 40
    assert len(disclosure.get("laws", [])) >= 14
    assert len(disclosure.get("oracles", [])) >= 12
    assert disclosure["effect_boundary"] == "pure_effect_intents"
    assert {"authorization_issuance", "cryptographic_proof_generation", "delivery", "recipient_acceptance", "source_deletion"} <= set(disclosure["forbidden_responsibilities"])
    disclosure_ops = {operation["name"]: operation for operation in disclosure["operations"]}
    assert disclosure_ops["form_disclosure_delivery_intent"]["effect_intent_type"] == "DisclosureDeliveryIntent"
    assert disclosure_ops["reconcile_disclosure_delivery"]["receipt_type"] == "DisclosureReceiptObservation"
    assert all(
        operation.get("input_types") and operation.get("output_type")
        and operation.get("refusal_types") and operation.get("purity") == "pure"
        for operation in disclosure["operations"]
    ), "disclosure-core exact API regressed"
    runtime_receipt = next(row for row in libraries if row["library_id"] == "library.lpe.runtime-receipt-core")
    assert runtime_receipt.get("public_traits") == ["RuntimeReceiptAlgebra"]
    assert len(runtime_receipt.get("public_types", [])) >= 10
    assert len(runtime_receipt.get("operations", [])) == 5
    assert len(runtime_receipt.get("laws", [])) >= 6
    assert all(
        operation.get("input_types") and operation.get("output_type")
        and operation.get("refusal_types") and operation.get("purity") == "pure"
        for operation in runtime_receipt["operations"]
    ), "runtime-receipt exact API regressed"
    assert not (referenced(planes, ["context_refs"]) - ids["contexts"]), "cross-plane context missing"
    assert not (referenced(planes, ["entity_type_refs"]) - ids["entities"]), "cross-plane entity missing"
    assert not (referenced(planes, ["relation_type_refs"]) - ids["relations"]), "cross-plane relation missing"
    assert not (referenced(planes, ["operation_refs"]) - ids["capabilities"]), "cross-plane operation missing"

    evidence_refs: set[str] = set()
    for rows, fields in [
        (contexts, ["evidence_refs"]), (entities, ["evidence_refs"]), (relations, ["evidence_refs"]),
        (capabilities, ["evidence_refs"]), (records["rules"], ["evidence_refs"]),
        (requirements, ["evidence_refs"]), (offers, ["evidence_refs"]), (mappings, ["evidence_refs"]),
        (libraries, ["evidence_refs"]), (records["retired_compositions"], ["evidence_refs"]),
        (innovations, ["evidence_refs"]), (gaps, ["evidence_refs"]),
    ]:
        evidence_refs.update(referenced(rows, fields))
    model = json.loads((ROOT / "evidence-evaluation-model.json").read_text(encoding="utf-8"))
    evidence_refs.update(model["evidence_refs"])
    assert not (evidence_refs - ids["sources"]), f"unknown source refs: {sorted(evidence_refs - ids['sources'])}"

    kinds = Counter(record["candidate_kind"] for record in capabilities)
    assert kinds["capability"] >= 10 and kinds["operation"] >= 140 and kinds["decision"] >= 20 and kinds["law"] >= 20
    assert all(record["refusal_law"] and record["failure_modes"] for record in capabilities)

    expected_planes = {"sources", "pipelines", "transformations", "semantic_formulas", "models_studies", "decisions_actions", "security", "governance", "quality", "runtime", "compiler"}
    assert ids["planes"] == expected_planes, "cross-plane set is incomplete or unexpected"
    assert all(row["context_refs"] and row["entity_type_refs"] and row["relation_type_refs"] and row["operation_refs"] for row in planes)

    assert len(model["authority_dimensions"]) >= 6 and len(model["strength_dimensions"]) >= 8
    assert len(model["defeater_model"]) >= 8
    assert {"event_time", "recording_time", "valid_from", "valid_until", "appraisal_time", "decision_time"} <= set(model["freshness_model"]["time_fields"])
    assert "No global numeric score" in model["evaluation_output"]["aggregation_law"]

    metamodel = json.loads((ROOT / "metamodel.json").read_text(encoding="utf-8"))
    assert metamodel["status"] == "candidate" and metamodel["completion_claim"] is False
    pairs = {(row["left"], row["right"]) for row in metamodel["distinction_matrix"]}
    assert {
        ("prospective_lineage", "retrospective_lineage"), ("logical_lineage", "physical_lineage"),
        ("physical_lineage", "runtime_lineage"), ("data_derivation", "process_execution"),
        ("audit_log", "provenance_graph"), ("provenance_bundle", "evidence_bundle"),
        ("assertion", "attestation"), ("attestation", "independent_appraisal"),
        ("identity_or_digest", "truth"), ("recording_time", "validity"),
        ("correction", "deletion"), ("retraction", "recall"),
        ("observability_telemetry", "durable_evidence"),
    } <= pairs

    assert all(2021 <= row["year"] <= 2026 and row["non_llm"] is True for row in innovations)
    assert {2021, 2022, 2023, 2024, 2025, 2026} <= {row["year"] for row in innovations}
    forbidden = re.compile(r"(?i)\b(prompt|rag|agent[_ -]?memory|large language model)\b")
    for label in ["capabilities", "requirements", "offers", "mappings", "libraries"]:
        for index, record in enumerate(records[label], 1):
            assert not forbidden.search(json.dumps(record)), f"{label}:{index}: forbidden core dependency"

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    actual_counts = {
        "authoritative_sources": len(sources), "bounded_context_candidates": len(contexts),
        "entity_type_candidates": len(entities), "relation_type_candidates": len(relations),
        "capability_operation_decision_law_candidates": len(capabilities),
        "invariant_refusal_candidates": len(records["rules"]), "requirements": len(requirements),
        "offers": len(offers), "compiler_mappings": len(mappings), "cross_plane_mappings": len(planes),
        "library_boundaries": len(libraries), "innovations_2021_2026": len(innovations),
        "retired_library_compositions": len(records["retired_compositions"]),
        "open_gaps": len(gaps), "schemas": len(list(SCHEMA.glob("*.schema.json"))),
    }
    assert manifest["counts"] == actual_counts, "manifest counts are stale"
    assert manifest["completion_claim"] is False and manifest["status"] == "candidate"

    # A builder rerun must be byte-for-byte stable for every generated artifact.
    generated = manifest["generated_files"] + ["manifest.json"]
    before = digest_generated(generated)
    subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], check=True, cwd=ROOT)
    after = digest_generated(generated)
    assert before == after, "builder output is not deterministic"

    print(
        "PASS lineage-provenance-evidence universe: "
        f"{len(sources)} sources, {len(contexts)} contexts, {len(entities)} entity types, "
        f"{len(relations)} relation types, {len(capabilities)} capability/operation/decision/law candidates "
        f"({kinds['capability']} capabilities, {kinds['operation']} operations, {kinds['decision']} decisions, {kinds['law']} laws), "
        f"{len(records['rules'])} invariants/refusals, {len(requirements)} requirements, {len(offers)} offers, "
        f"{len(mappings)} compiler mappings, {len(planes)} cross-plane mappings, {len(libraries)} library boundaries, "
        f"{len(records['retired_compositions'])} retired compositions, "
        f"{len(innovations)} innovations, {len(gaps)} gaps, {actual_counts['schemas']} schemas; deterministic generation verified"
    )


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
