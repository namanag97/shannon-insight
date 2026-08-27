#!/usr/bin/env python3
"""Offline structural and constitutional validator for the binder/solver bundle."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROVIDER_TARGET_ROOT = ROOT.parent / "provider_target_registry"
MODEL_CLASS_ROOT = ROOT.parent / "model_class_adjudication"


def fail(message: str):
    raise AssertionError(message)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(name: str):
    path = ROOT / name
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            fail(f"{name}:{line_number}: {exc}")
    if rows != sorted(rows, key=lambda row: row["id"]):
        fail(f"{name}: records are not sorted by stable identity")
    return rows


def load_external_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def check_record_shape(filename: str, rows: list[dict], all_ids: set[str]):
    for row in rows:
        for key in ("id", "record_kind", "edition", "status"):
            if key not in row:
                fail(f"{filename}:{row.get('id', '?')}: missing {key}")
        if row["edition"] != 1 or row["status"] != "reviewed_candidate":
            fail(f"{filename}:{row['id']}: invalid edition/status")
        if row["id"] in all_ids:
            fail(f"duplicate identity: {row['id']}")
        all_ids.add(row["id"])


def main():
    manifest = load_json(ROOT / "manifest.json")
    metamodel = load_json(ROOT / "metamodel.json")
    if metamodel["completion_claim"] != "candidate_not_complete":
        fail("metamodel must not claim completeness")

    jsonl_files = sorted(path.name for path in ROOT.glob("*.jsonl"))
    tables = {name: load_jsonl(name) for name in jsonl_files}
    all_ids: set[str] = set()
    for name, rows in tables.items():
        check_record_shape(name, rows, all_ids)

    sources = tables["sources.jsonl"]
    if len(sources) < 80:
        fail("fewer than 80 primary/authoritative sources")
    urls = [row["url"] for row in sources]
    if len(urls) != len(set(urls)):
        fail("source URLs must be unique")
    allowed_source_kinds = {
        "standard", "official_documentation", "official_specification", "official_technical_article",
        "reference_checker", "primary_research", "official_rules", "language_specification",
        "recommendation", "specification", "official_algorithm_description", "primary_specification",
        "committee_specification", "official_guidelines", "official_book", "community_specification"
        , "official_release", "official_source"
    }
    for row in sources:
        if row["source_kind"] not in allowed_source_kinds:
            fail(f"unapproved source kind: {row['id']} {row['source_kind']}")
        if not row["url"].startswith("https://"):
            fail(f"non-HTTPS source: {row['id']}")

    phases = tables["binding-phases.jsonl"]
    expected_phase_ids = [
        "phase.bind.structural", "phase.bind.semantic", "phase.bind.constraints",
        "phase.bind.optimization", "phase.bind.qualification", "phase.bind.allocation",
        "phase.bind.runtime"
    ]
    if [row["id"] for row in sorted(phases, key=lambda row: row["ordinal"])] != expected_phase_ids:
        fail("seven non-collapsible phase identities/order changed")
    if metamodel["non_collapsible_phases"] != [
        "structural_matching", "semantic_subsumption", "constraint_solving", "optimization_ranking",
        "qualification", "allocation_admission", "runtime_verification"
    ]:
        fail("metamodel phase law changed")

    # Reference closure for local record relations.
    source_ids = {row["id"] for row in sources}
    phase_ids = {row["id"] for row in phases}
    diagnostic_ids = {row["id"] for row in tables["diagnostics.jsonl"]}
    proof_ids = {row["id"] for row in tables["proof-contracts.jsonl"]}
    gap_ids = {row["id"] for row in tables["gaps.jsonl"]}
    requirement_ids = {row["id"] for row in tables["requirements.jsonl"]}
    offer_ids = {row["id"] for row in tables["offers.jsonl"]}
    example_ids = {row["id"] for row in tables["examples.jsonl"]}

    for name in ("algorithms.jsonl", "compiler-passes.jsonl", "proof-contracts.jsonl"):
        for row in tables[name]:
            if row["phase_ref"] not in phase_ids:
                fail(f"{row['id']}: unknown phase {row['phase_ref']}")
    for row in tables["constraint-kinds.jsonl"]:
        if row["diagnostic"] not in diagnostic_ids:
            fail(f"{row['id']}: unknown diagnostic")
        if row["class_"] in {"identity", "edition", "semantic", "type", "shape", "operation", "law", "authority", "policy", "budget", "evidence"} and row["hardness"] != "hard":
            fail(f"{row['id']}: constitutional constraint was softened")
    for row in tables["requirements.jsonl"]:
        for proof_ref in row["proof_refs"]:
            if proof_ref not in proof_ids:
                fail(f"{row['id']}: unknown proof {proof_ref}")
    for name in ("sources.jsonl", "offers.jsonl", "innovations-2021-2026.jsonl", "examples.jsonl"):
        for row in tables[name]:
            for source_ref in row.get("evidence_refs", []):
                if source_ref not in source_ids:
                    fail(f"{row['id']}: unknown source {source_ref}")

    for row in tables["requirement-offer-evaluations.jsonl"]:
        if row["requirement_ref"] not in requirement_ids or row["offer_ref"] not in offer_ids:
            fail(f"{row['id']}: dangling requirement/offer")
        if row["binding_result"] not in {"typed_gap", "refused"} or not row["gap_refs"]:
            fail(f"{row['id']}: current evaluation must terminate in a typed gap or evidence-backed refusal")
        for gap_ref in row["gap_refs"]:
            if gap_ref not in gap_ids:
                fail(f"{row['id']}: unknown gap {gap_ref}")

    # The provider-target registry is a digest-bound input, and its complete offer set is projected
    # without promotion into the binder snapshot.
    upstream_digests = metamodel.get("upstream_snapshot_digests", {}).get("provider_target_registry", {})
    if not upstream_digests:
        fail("provider-target upstream snapshot digests are absent")
    for name, expected_digest in upstream_digests.items():
        path = PROVIDER_TARGET_ROOT / name
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest:
            fail(f"provider-target input drift: {name}")

    model_class_digests = metamodel.get("upstream_snapshot_digests", {}).get("model_class_adjudication", {})
    if not model_class_digests:
        fail("model-class adjudication upstream snapshot digests are absent")
    for name, expected_digest in model_class_digests.items():
        path = MODEL_CLASS_ROOT / name
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest:
            fail(f"model-class adjudication input drift: {name}")

    model_class_ids = {row["id"] for row in load_external_jsonl(MODEL_CLASS_ROOT / "model-classes.jsonl")}
    model_class_trace_ids = {row["id"] for row in load_external_jsonl(MODEL_CLASS_ROOT / "classification-traces.jsonl")}
    model_class_result_ids = {row["id"] for row in load_external_jsonl(MODEL_CLASS_ROOT / "adjudication-results.jsonl")}
    adjudicated_examples = {
        row["id"]: row for row in tables["examples.jsonl"]
        if row.get("model_class_adjudication_trace_ref") is not None
    }
    for row in adjudicated_examples.values():
        if row.get("model_class_adjudication_trace_ref") not in model_class_trace_ids:
            fail(f"{row['id']}: dangling model-class adjudication trace")
        if row.get("model_class_adjudication_result_ref") not in model_class_result_ids:
            fail(f"{row['id']}: dangling model-class adjudication result")
        if not set(row.get("formal_model_class_refs", [])).issubset(model_class_ids):
            fail(f"{row['id']}: dangling formal model class")

    ptr_offers = load_external_jsonl(PROVIDER_TARGET_ROOT / "concrete-offers.jsonl")
    ptr_occurrences = load_external_jsonl(PROVIDER_TARGET_ROOT / "target-occurrences.jsonl")
    ptr_qualifications = load_external_jsonl(PROVIDER_TARGET_ROOT / "qualification-receipts.jsonl")
    ptr_compatibility = load_external_jsonl(PROVIDER_TARGET_ROOT / "compatibility-matrix.jsonl")
    ptr_offer_by_id = {row["offer_id"]: row for row in ptr_offers}
    ptr_qualifications_by_offer: dict[str, list[dict]] = {}
    for row in ptr_qualifications:
        ptr_qualifications_by_offer.setdefault(row["subject_ref"], []).append(row)
    ptr_occurrences_by_offer: dict[str, list[str]] = {}
    for row in ptr_occurrences:
        ptr_occurrences_by_offer.setdefault(row["offer_ref"], []).append(row["target_occurrence_id"])
    ptr_compatibility_by_offer: dict[str, list[str]] = {}
    for row in ptr_compatibility:
        for endpoint in (row["left_ref"], row["right_ref"]):
            if endpoint.startswith("offer.ptr."):
                ptr_compatibility_by_offer.setdefault(endpoint, []).append(row["compatibility_id"])

    projected = [row for row in tables["offers.jsonl"] if row.get("source_registry") == "san.provider-target-physical-binding-registry"]
    if len(projected) != len(ptr_offers):
        fail(f"provider-target offer projection is incomplete: {len(projected)} != {len(ptr_offers)}")
    if {row["source_offer_ref"] for row in projected} != set(ptr_offer_by_id):
        fail("provider-target offer projection identities differ")
    for row in projected:
        source_offer = ptr_offer_by_id[row["source_offer_ref"]]
        assessments = ptr_qualifications_by_offer.get(source_offer["offer_id"], [])
        expected_assessments = sorted(item["qualification_receipt_id"] for item in assessments)
        expected_execution_receipts = sorted({ref for item in assessments for ref in item.get("execution_receipt_refs", [])})
        expected_compatibility = sorted(ptr_compatibility_by_offer.get(source_offer["offer_id"], []))
        expected_occurrences = sorted(ptr_occurrences_by_offer.get(source_offer["offer_id"], []))
        checks = {
            "source_artifact_ref": source_offer["artifact_ref"],
            "source_provider_organization_ref": source_offer["provider_organization_ref"],
            "offers": source_offer["capability_class_refs"],
            "exact_edition": source_offer["artifact_version"],
            "source_target_profile_refs": source_offer["target_profile_refs"],
            "source_target_occurrence_refs": expected_occurrences,
            "source_compatibility_refs": expected_compatibility,
            "qualification_assessment_refs": expected_assessments,
            "executed_test_receipt_refs": expected_execution_receipts,
            "exclusions": source_offer["exclusions"],
            "upstream_evidence_refs": source_offer["evidence_refs"],
        }
        for field, expected in checks.items():
            if row[field] != expected:
                fail(f"{row['id']}: projection drift in {field}")
        if row["binding_eligible"] or row["qualification_receipts"]:
            fail(f"{row['id']}: projection promoted an unqualified source offer")

    # Candidate documentation and narrow internal execution cannot silently become bindable.
    for row in tables["offers.jsonl"]:
        if row["binding_eligible"]:
            if not row["qualification_receipts"]:
                fail(f"{row['id']}: binding eligible without receipts")
            fail(f"{row['id']}: this candidate corpus should not contain a live bindable offer")
        if row["qualification_receipts"]:
            fail(f"{row['id']}: unexpected qualification receipt in candidate corpus")

    ptr_qualification_by_id = {row["qualification_receipt_id"]: row for row in ptr_qualifications}
    for row in tables["requirement-offer-evaluations.jsonl"]:
        assessment_refs = row.get("source_qualification_assessment_refs", [])
        if not assessment_refs:
            if row.get("source_execution_receipt_refs", []):
                fail(f"{row['id']}: execution receipts lack provider-target assessments")
            continue
        projected_offer = next(item for item in projected if item["id"] == row["offer_ref"])
        supplied_receipts: set[str] = set()
        for assessment_ref in assessment_refs:
            if assessment_ref not in ptr_qualification_by_id:
                fail(f"{row['id']}: unknown provider-target assessment {assessment_ref}")
            assessment = ptr_qualification_by_id[assessment_ref]
            if assessment["subject_ref"] != projected_offer["source_offer_ref"]:
                fail(f"{row['id']}: assessment subject does not match projected offer")
            supplied_receipts.update(assessment.get("execution_receipt_refs", []))
        if not set(row.get("source_execution_receipt_refs", [])) <= supplied_receipts:
            fail(f"{row['id']}: execution receipt was not supplied by the referenced assessments")

    expected_lp_results = {
        "evaluation.bind.lp_safe.ortools_glop_mpsolver_python.9_15_6755": ("typed_gap", "executed_safe_profile_pass"),
        "evaluation.bind.lp_safe.highspy_highs.1_15_1": ("typed_gap", "executed_safe_profile_pass"),
        "evaluation.bind.lp_precise.ortools_glop_mpsolver_python.9_15_6755": ("refused", "executed_precise_profile_fail"),
        "evaluation.bind.lp_precise.highspy_highs.1_15_1": ("typed_gap", "executed_precise_profile_pass"),
    }
    evaluations_by_id = {row["id"]: row for row in tables["requirement-offer-evaluations.jsonl"]}
    for evaluation_id, (result, semantic) in expected_lp_results.items():
        if evaluation_id not in evaluations_by_id:
            fail(f"missing exact LP evaluation: {evaluation_id}")
        if (evaluations_by_id[evaluation_id]["binding_result"], evaluations_by_id[evaluation_id]["semantic"]) != (result, semantic):
            fail(f"{evaluation_id}: exact LP result was strengthened or weakened")
    expected_cp_sat_results = {
        "evaluation.bind.cp_sat_exact.ortools_cp_sat_python.9_15_6755": ("typed_gap", "executed_core_global_scheduling_limit_profiles_pass"),
        "evaluation.bind.cp_sat_enumeration.pre_parameter": ("refused", "executed_enumeration_profile_fail"),
        "evaluation.bind.cp_sat_enumeration.corrected": ("typed_gap", "executed_enumeration_profile_pass"),
    }
    for evaluation_id, (result, semantic) in expected_cp_sat_results.items():
        if evaluation_id not in evaluations_by_id:
            fail(f"missing exact CP-SAT evaluation: {evaluation_id}")
        if (evaluations_by_id[evaluation_id]["binding_result"], evaluations_by_id[evaluation_id]["semantic"]) != (result, semantic):
            fail(f"{evaluation_id}: exact CP-SAT result was strengthened or weakened")

    # Positive examples must stop, negative twins must refuse, and twins must be symmetric.
    by_example = {row["id"]: row for row in tables["examples.jsonl"]}
    verticals = {row["vertical"] for row in by_example.values() if row["polarity"] == "positive"}
    if len(verticals) < 3:
        fail("fewer than three unrelated positive vertical examples")
    for row in by_example.values():
        twin = row["negative_twin_ref"]
        if twin not in example_ids or by_example[twin]["negative_twin_ref"] != row["id"]:
            fail(f"{row['id']}: negative twin relation is not symmetric")
        for gap_ref in row["terminal_gaps"]:
            if gap_ref not in gap_ids:
                fail(f"{row['id']}: unknown terminal gap {gap_ref}")
        if row["polarity"] == "positive":
            if row["terminal_result"] != "partially_bound" or not row["terminal_gaps"]:
                fail(f"{row['id']}: positive example fabricated completion")
        elif row["terminal_result"] != "refused":
            fail(f"{row['id']}: negative twin did not refuse")

    pipeline_positive = by_example.get("example.bind.pipeline_nomination.lp_screening.positive")
    pipeline_negative = by_example.get("example.bind.pipeline_nomination.generic_solver.negative")
    if not pipeline_positive or not pipeline_negative:
        fail("pipeline nomination LP vertical/twin trace is missing")
    energy_cases = {
        row["record_id"]
        for row in load_external_jsonl(ROOT.parents[1] / "industries" / "energy_resources" / "analytics-cases.jsonl")
    }
    if pipeline_positive["upstream_case_ref"] not in energy_cases or pipeline_negative["upstream_case_ref"] not in energy_cases:
        fail("pipeline nomination example does not resolve to the industry corpus")
    if pipeline_positive["required_status_precision"] != "precise_infeasible_vs_unbounded":
        fail("pipeline positive does not require precise terminal classification")
    if pipeline_positive["optional_extension_requirement_refs"] or pipeline_negative["optional_extension_requirement_refs"]:
        fail("pipeline LP path acquired an ambient model/agent dependency")
    if pipeline_positive["automation_modality"] != "deterministic_core_only":
        fail("pipeline LP path is not explicitly deterministic-core only")
    manufacturing_positive = by_example.get("example.bind.manufacturing_schedule.cp_sat.positive")
    manufacturing_negative = by_example.get("example.bind.manufacturing_schedule.generic_optimizer.negative")
    if not manufacturing_positive or not manufacturing_negative:
        fail("manufacturing CP-SAT vertical/twin trace is missing")
    manufacturing_cases = {
        row["record_id"]
        for row in load_external_jsonl(ROOT.parents[1] / "industries" / "manufacturing_industrial" / "analytics-cases.jsonl")
    }
    if manufacturing_positive["upstream_case_ref"] not in manufacturing_cases or manufacturing_negative["upstream_case_ref"] not in manufacturing_cases:
        fail("manufacturing CP-SAT example does not resolve to the industry corpus")
    if set(manufacturing_positive["formal_model_class_refs"]) != {"class.mca.cp_sat_integer", "class.mca.finite_domain_cp"}:
        fail("manufacturing example collapsed or lost its formal-model facets")
    if manufacturing_positive["optional_extension_requirement_refs"] or manufacturing_negative["optional_extension_requirement_refs"]:
        fail("manufacturing CP-SAT path acquired an ambient model/agent dependency")
    if manufacturing_positive["automation_modality"] != "deterministic_core_only":
        fail("manufacturing CP-SAT path is not explicitly deterministic-core only")

    # Non-LLM innovation window and source closure.
    forbidden = ("large language model", "llm", "generative ai", "prompt engineering", "rag")
    for row in tables["innovations-2021-2026.jsonl"]:
        if not 2021 <= row["year"] <= 2026:
            fail(f"{row['id']}: outside requested innovation window")
        body = json.dumps(row).lower()
        if any(term in body for term in forbidden):
            fail(f"{row['id']}: forbidden generative/LLM innovation")

    # Constitutional language must preserve unknown and phase separation.
    laws = "\n".join(metamodel["constitutional_laws"]).lower()
    required_fragments = [
        "structural match is not semantic", "feasibility is not optimality",
        "timeout or unsupported theory is unknown", "unsat core", "resource capacity is not quota",
        "incremental rebinding must equal a clean rebind", "absent offers or receipts terminates in typed gaps"
        , "executed test, independent appraisal", "formal model class must be deterministically adjudicated"
        , "business problem-family name", "model, llm, or agent proposal cannot satisfy"
    ]
    for fragment in required_fragments:
        if fragment not in laws:
            fail(f"missing constitutional law fragment: {fragment}")

    # Upstream inputs are aligned by read-only path and must exist.
    for path in metamodel["upstream_alignment"].values():
        if not (ROOT / path).resolve().exists():
            fail(f"missing upstream alignment target: {path}")

    # Manifest content and digests.
    expected_counts = {"sources": len(sources), "contexts": len(tables["contexts.jsonl"])}
    expected_counts.update({name.removesuffix(".jsonl"): len(rows) for name, rows in tables.items() if name not in {"sources.jsonl", "contexts.jsonl"}})
    if manifest["counts"] != expected_counts:
        fail(f"manifest counts differ: {manifest['counts']} != {expected_counts}")
    for item in manifest["files"]:
        data = (ROOT / item["path"]).read_bytes()
        if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
            fail(f"manifest digest mismatch: {item['path']}")

    # A fresh deterministic generation must be byte-identical.
    tracked = {item["path"]: (ROOT / item["path"]).read_bytes() for item in manifest["files"]}
    old_manifest = (ROOT / "manifest.json").read_bytes()
    subprocess.run([sys.executable, str(ROOT / "build_bundle.py")], check=True)
    for name, before in tracked.items():
        if (ROOT / name).read_bytes() != before:
            fail(f"non-deterministic regeneration: {name}")
    if (ROOT / "manifest.json").read_bytes() != old_manifest:
        fail("non-deterministic manifest regeneration")

    print(
        "PASS binder/solver candidate: "
        f"{len(sources)} sources, {len(phases)} phases, "
        f"{len(tables['constraint-kinds.jsonl'])} constraint kinds, "
        f"{len(tables['proof-contracts.jsonl'])} proof contracts, "
        f"{len(tables['examples.jsonl'])} vertical/twin traces; no bindable offer fabricated"
    )


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
