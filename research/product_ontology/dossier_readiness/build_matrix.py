#!/usr/bin/env python3
"""Derive product-specific DDD and compiler-readiness gaps for retained products."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GLOBAL = ROOT / "research/product_ontology/global_boundary_research"
VERTICALS = ROOT / "research/product_ontology/composition_pilots/deterministic_verticals"
QUALIFICATION_SUBJECTS = ROOT / "research/product_ontology/qualification_program/library-qualification-subjects.jsonl"
AS_OF = "2026-08-26"

DDD_FIELDS = [
    "domain_vision_statement",
    "subdomain_classification",
    "bounded_context_boundary",
    "ubiquitous_language_policy",
    "context_map",
    "anti_corruption_layers",
    "published_language",
    "value_objects",
    "entities",
    "aggregates",
    "aggregate_roots",
    "aggregate_invariants",
    "commands",
    "domain_events",
    "refusal_failure_catalog",
    "domain_services",
    "application_services",
    "repositories",
    "factories",
    "specifications",
    "state_machine",
    "policies_and_reactions",
    "sagas_and_process_managers",
    "read_models_and_projections",
    "integration_event_policy",
    "concurrency_and_idempotency",
    "time_model",
    "event_storming_swimlanes",
    "nonfunctional_laws",
]

LOCAL_PRODUCT_FIELDS = [
    "sovereign_question",
    "users",
    "harmed_parties",
    "jobs",
    "outcomes",
    "negative_mission",
    "lifecycle_states",
    "commands",
    "events",
    "invariants",
    "refusals",
    "automation_modality",
]

ADJUDICATION_RE = re.compile(
    r"^research/product_ontology/adjudications/(?P<bundle>[^/]+)/"
    r"boundary-decisions\.jsonl#(?P<decision>.+)$"
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def lines(rows: list[dict[str, Any]]) -> str:
    return "".join(canonical(row) + "\n" for row in rows)


def qualified_offer(row: dict[str, Any]) -> bool:
    status = str(row.get("status", ""))
    return bool(row.get("qualified_implementation_count", 0)) or (
        status.startswith("qualified") and "unqualified" not in status
    )


def portable_offer(row: dict[str, Any]) -> bool:
    return bool(row.get("portable") or row.get("portability_claim"))


def product_ref_matches(row: dict[str, Any], subject_ref: str) -> bool:
    return row.get("product_ref") == subject_ref or subject_ref in row.get("product_refs", [])


def derive() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    candidates = load_jsonl(GLOBAL / "product-archetypes.jsonl")
    retained = [
        row
        for row in candidates
        if row["boundary_evaluation"]["verdict"] in {"strong_product", "presumptive_product"}
    ]
    truth_by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in load_jsonl(GLOBAL / "truth-applicability.jsonl"):
        truth_by_candidate[row["candidate_id"]].append(row)
    global_support = {
        "user_job_outcome": {
            row["candidate_id"] for row in load_jsonl(GLOBAL / "user-jobs-outcomes.jsonl")
        },
        "service_blueprint": {
            row["candidate_id"] for row in load_jsonl(GLOBAL / "service-blueprints.jsonl")
        },
        "lifecycle": {row["candidate_id"] for row in load_jsonl(GLOBAL / "lifecycle.jsonl")},
    }
    vertical_count: Counter[str] = Counter()
    for row in load_jsonl(VERTICALS / "vertical-compositions.jsonl"):
        for candidate_id in row["product_refs"]:
            vertical_count[candidate_id] += 1

    qualification_by_library = {
        row["abstract_library_ref"]: row for row in load_jsonl(QUALIFICATION_SUBJECTS)
    }

    readiness: list[dict[str, Any]] = []
    work: list[dict[str, Any]] = []
    compiler_gap_rebase: list[dict[str, Any]] = []
    for candidate in sorted(retained, key=lambda row: row["record_id"]):
        candidate_id = candidate["record_id"]
        ident = candidate_id.removeprefix("candidate.product.")
        evaluation = candidate["boundary_evaluation"]
        match = ADJUDICATION_RE.match(evaluation["adjudication_ref"])
        if not match:
            raise ValueError(f"{candidate_id}: malformed adjudication_ref")
        bundle = match.group("bundle")
        decision_id = match.group("decision")
        source_path = ROOT / f"research/product_ontology/adjudications/{bundle}/source.json"
        source = json.loads(source_path.read_text(encoding="utf-8"))
        decisions = {row["decision_id"]: row for row in source["boundary_decisions"]}
        decision = decisions[decision_id]
        subject_ref = decision["subject_ref"]
        artifact = next(
            (row for row in source.get("artifacts", []) if row.get("artifact_id") == subject_ref),
            {},
        )
        dossier = next(
            (row for row in source.get("ddd_dossiers", []) if row.get("product_ref") == subject_ref),
            None,
        )
        ddd = dossier.get("strategic_and_tactical_ddd", {}) if dossier else {}
        present_ddd = sorted(field for field in DDD_FIELDS if field in ddd and ddd[field] not in (None, [], {}))
        missing_ddd = sorted(set(DDD_FIELDS) - set(present_ddd))
        present_local = sorted(
            field for field in LOCAL_PRODUCT_FIELDS if artifact.get(field) not in (None, [], {})
        )

        libraries = source.get("libraries", [])
        requirements = source.get("requirements", [])
        maps = source.get("binding_maps", source.get("compiler_library_bindings", []))
        gaps = source.get("binding_gaps", [])
        semantic_gaps = source.get("semantic_gaps", [])
        offers = source.get("offers", [])
        product_libraries = [row for row in libraries if product_ref_matches(row, subject_ref)]
        product_requirements = [row for row in requirements if row.get("consumer_ref") == subject_ref]
        required_capabilities = sorted({row["capability_ref"] for row in product_requirements})
        provided_capabilities = sorted({ref for row in product_libraries for ref in row.get("provides", [])})
        local_artifacts = {row["artifact_id"]: row for row in source.get("artifacts", [])}
        product_owner_ref = artifact.get("semantic_owner_ref")
        internal_required_capabilities = sorted({
            row["capability_ref"]
            for row in product_requirements
            if (
                row["capability_ref"] in provided_capabilities
                or (
                    product_owner_ref is not None
                    and local_artifacts.get(row["capability_ref"], {}).get("semantic_owner_ref")
                    == product_owner_ref
                )
            )
        })
        imported_requirement_refs = sorted({
            row["capability_ref"]
            for row in product_requirements
            if row["capability_ref"] not in internal_required_capabilities
        })
        uncovered_capabilities = sorted(set(internal_required_capabilities) - set(provided_capabilities))
        product_maps = [row for row in maps if product_ref_matches(row, subject_ref)]
        product_gaps = [row for row in gaps if product_ref_matches(row, subject_ref)]
        product_semantic_gaps = [row for row in semantic_gaps if product_ref_matches(row, subject_ref)]
        qualified = sum(qualified_offer(row) for row in offers)
        portable = sum(portable_offer(row) for row in offers)
        structural_verticals = vertical_count[candidate_id]

        product_gap_resolutions = []
        for gap in product_gaps:
            abstract_refs = gap.get("abstract_library_refs") or [gap.get("abstract_library_ref")]
            matches = [qualification_by_library.get(ref) for ref in abstract_refs]
            contract_complete = bool(matches) and all(
                match is not None
                and set(match.get("contract", {}))
                >= {"types", "operations", "decisions", "invariants", "refusals", "dependencies"}
                for match in matches
            )
            if not contract_complete:
                continue
            for abstract_ref, match in zip(abstract_refs, matches):
                resolution = {
                    "record_id": f"rebase.{gap['gap_id']}",
                    "record_kind": "compiler_gap_research_rebase",
                    "source_gap_ref": gap["gap_id"],
                    "product_ref": subject_ref,
                    "abstract_library_ref": abstract_ref,
                    "qualification_subject_ref": match["subject_id"],
                    "contract_surface_present": sorted(match["contract"]),
                    "research_disposition": "EXACT_ABSTRACT_CONTRACT_PRESENT",
                    "remaining_gate": "CONCRETE_IMPLEMENTATION_AND_PROVIDER_QUALIFICATION",
                    "implementation_state": match["implementation_state"],
                    "qualified_implementation_refs": match["qualified_implementation_refs"],
                    "compiler_binding": "REFUSED_NO_QUALIFIED_OFFER",
                    "status": "RESEARCH_RESOLVED_DOWNSTREAM_GATED",
                    "completion_claim": False,
                }
                product_gap_resolutions.append(resolution)
                compiler_gap_rebase.append(resolution)
        unresolved_structural_gaps = {
            gap["gap_id"] for gap in product_gaps
        } - {row["source_gap_ref"] for row in product_gap_resolutions}

        if product_maps:
            mapping_status = "BLOCKED" if unresolved_structural_gaps or uncovered_capabilities else "STRUCTURALLY_MAPPED_UNQUALIFIED"
        else:
            mapping_status = "UNDETERMINED_PRODUCT_ATTRIBUTION"

        record = {
            "record_id": f"readiness.{ident}",
            "record_kind": "product_dossier_readiness",
            "as_of": AS_OF,
            "candidate_id": candidate_id,
            "name": candidate["name"],
            "family": candidate["family"],
            "boundary_verdict": evaluation["verdict"],
            "adjudication_bundle": bundle,
            "adjudication_decision_id": decision_id,
            "local_subject_ref": subject_ref,
            "boundary_adjudication": "PASS_EXACT_TRACE",
            "global_truth_profile": {
                "status": "PASS_STRUCTURAL" if len(truth_by_candidate[candidate_id]) == 110 else "MISSING",
                "truth_dimension_count": len(truth_by_candidate[candidate_id]),
                "warning": "Applicability coverage is not product-specific proof or acceptance.",
            },
            "global_generic_support": {
                name: candidate_id in refs for name, refs in global_support.items()
            },
            "local_product_field_coverage": {
                "present": present_local,
                "missing": sorted(set(LOCAL_PRODUCT_FIELDS) - set(present_local)),
                "present_count": len(present_local),
                "required_count": len(LOCAL_PRODUCT_FIELDS),
            },
            "product_specific_ddd": {
                "status": "COMPLETE_CANDIDATE_DOSSIER" if not missing_ddd else "MISSING_OR_INCOMPLETE",
                "dossier_ref": dossier.get("dossier_id") if dossier else None,
                "present_fields": present_ddd,
                "missing_fields": missing_ddd,
                "present_count": len(present_ddd),
                "required_count": len(DDD_FIELDS),
            },
            "library_and_compiler": {
                "bundle_library_count": len(libraries),
                "bundle_binding_map_count": len(maps),
                "explicit_product_library_count": len(product_libraries),
                "explicit_product_binding_map_count": len(product_maps),
                "explicit_product_binding_gap_count": len(product_gaps),
                "research_resolved_binding_gap_count": len(product_gap_resolutions),
                "open_structural_binding_gap_count": len(unresolved_structural_gaps),
                "implementation_binding_vacancy_count": len(product_gap_resolutions),
                "compiler_gap_rebase_refs": sorted(row["record_id"] for row in product_gap_resolutions),
                "explicit_product_semantic_gap_count": len(product_semantic_gaps),
                "declared_product_requirement_count": len(product_requirements),
                "required_capability_refs": required_capabilities,
                "internally_owned_required_capability_refs": internal_required_capabilities,
                "imported_product_provider_or_resource_requirement_refs": imported_requirement_refs,
                "provided_capability_refs": provided_capabilities,
                "uncovered_required_capability_refs": uncovered_capabilities,
                "uncovered_required_capability_count": len(uncovered_capabilities),
                "mapping_status": mapping_status,
                "attribution_warning": (
                    None
                    if product_libraries
                    else "Bundle-level libraries may exist, but no exact product_ref proves this product's complete decomposition."
                ),
            },
            "provider_readiness": {
                "observed_bundle_offer_count": len(offers),
                "qualified_offer_count": qualified,
                "portable_offer_count": portable,
                "status": "BLOCKED_NO_QUALIFIED_PORTABLE_OFFER" if not qualified or not portable else "EVIDENCED",
            },
            "vertical_proof": {
                "structural_composition_count": structural_verticals,
                "executed_acceptance_count": 0,
                "status": "STRUCTURAL_ONLY" if structural_verticals else "MISSING",
            },
            "ratification": "WITHHELD",
            "build_readiness": "NOT_BUILD_READY",
            "automation_law": {
                "default_posture": candidate["automation_modality"]["default_posture"],
                "deterministic_core_survives_removal": True,
                "generated_proposals_non_authoritative": True,
            },
        }
        readiness.append(record)

        def add_work(kind: str, statement: str, evidence_needed: list[str]) -> None:
            work.append(
                {
                    "record_id": f"work.{ident}.{kind}",
                    "record_kind": "product_closure_work_item",
                    "candidate_id": candidate_id,
                    "work_kind": kind,
                    "blocking": True,
                    "statement": statement,
                    "evidence_needed": evidence_needed,
                    "owner": "UNASSIGNED",
                    "status": "OPEN",
                }
            )

        if missing_ddd:
            add_work(
                "full_ddd_dossier",
                f"Create product-specific strategic/tactical DDD; {len(missing_ddd)} of {len(DDD_FIELDS)} required fields are absent.",
                ["complete 29-field dossier", "domain expert appraisal", "negative-twin review"],
            )
        if not product_libraries:
            add_work(
                "product_library_attribution",
                "Prove the exact product-to-library decomposition instead of relying on bundle-level proximity.",
                ["product_ref on every required library", "complete/non-overlapping ownership review"],
            )
        if not product_maps:
            add_work(
                "compiler_binding_map",
                "Map every product library to an exact compiler registry contract or a named blocking gap.",
                ["one map per product library", "typed gap for every missing exact contract"],
            )
        if unresolved_structural_gaps:
            add_work(
                "compiler_gap_closure",
                f"Close or explicitly retain {len(unresolved_structural_gaps)} exact product-specific compiler binding gaps.",
                ["semantic owner contribution", "law oracles", "independent conformance check"],
            )
        if uncovered_capabilities:
            add_work(
                "capability_decomposition_gap",
                f"Add exact owning libraries or narrow {len(uncovered_capabilities)} internally owned product capability requirements not provided by the attributed library set.",
                ["requirement-to-library coverage", "semantic owner", "invariants and refusals", "compiler map or typed gap"],
            )
        add_work(
            "provider_qualification",
            "Qualify at least one provider for execution and two independent implementations before portability is claimed.",
            ["current qualification receipts", "negative twins", "cross-provider differential", "exit drill"],
        )
        if structural_verticals < 2:
            add_work(
                "unrelated_vertical_generality",
                "Prove unchanged horizontal semantics in at least two unrelated enterprise verticals.",
                ["two structural compositions", "domain-owner acceptance criteria", "semantic diff"],
            )
        add_work(
            "executed_vertical_acceptance",
            "Execute product-specific vertical acceptance; structural composition alone is insufficient.",
            ["accepted source occurrence", "qualified provider", "runtime receipts", "domain-owner verdict"],
        )

    status_counts = Counter(row["product_specific_ddd"]["status"] for row in readiness)
    mapping_counts = Counter(row["library_and_compiler"]["mapping_status"] for row in readiness)
    summary = {
        "report_id": "retained_product_dossier_and_compiler_readiness",
        "as_of": AS_OF,
        "status": "CANDIDATE_GAP_MATRIX",
        "scope": "Every strong or presumptive product in the current finite global corpus.",
        "retained_product_count": len(readiness),
        "full_product_specific_ddd_count": sum(
            row["product_specific_ddd"]["status"] == "COMPLETE_CANDIDATE_DOSSIER"
            for row in readiness
        ),
        "missing_or_incomplete_ddd_count": sum(
            row["product_specific_ddd"]["status"] != "COMPLETE_CANDIDATE_DOSSIER"
            for row in readiness
        ),
        "explicit_product_library_attribution_count": sum(
            row["library_and_compiler"]["explicit_product_library_count"] > 0 for row in readiness
        ),
        "explicit_product_compiler_map_count": sum(
            row["library_and_compiler"]["explicit_product_binding_map_count"] > 0 for row in readiness
        ),
        "product_count_with_uncovered_required_capabilities": sum(
            row["library_and_compiler"]["uncovered_required_capability_count"] > 0
            for row in readiness
        ),
        "qualified_provider_product_count": sum(
            row["provider_readiness"]["qualified_offer_count"] > 0 for row in readiness
        ),
        "portable_provider_product_count": sum(
            row["provider_readiness"]["portable_offer_count"] > 0 for row in readiness
        ),
        "two_vertical_structural_product_count": sum(
            row["vertical_proof"]["structural_composition_count"] >= 2 for row in readiness
        ),
        "executed_vertical_acceptance_product_count": 0,
        "build_ready_product_count": 0,
        "open_work_item_count": len(work),
        "source_compiler_gap_count": sum(row["library_and_compiler"]["explicit_product_binding_gap_count"] for row in readiness),
        "research_resolved_compiler_gap_count": len(compiler_gap_rebase),
        "open_structural_compiler_gap_count": sum(row["library_and_compiler"]["open_structural_binding_gap_count"] for row in readiness),
        "implementation_binding_vacancy_count": len(compiler_gap_rebase),
        "ddd_status_counts": dict(sorted(status_counts.items())),
        "mapping_status_counts": dict(sorted(mapping_counts.items())),
        "laws": [
            "A boundary verdict is not a DDD dossier.",
            "A bundle-level library list is not an exact product decomposition.",
            "A compiler map is not provider qualification.",
            "Structural vertical composition is not executed domain acceptance.",
            "No model or agent may satisfy missing research, semantics, authority, qualification or acceptance evidence.",
        ],
    }
    return readiness, sorted(work, key=lambda row: row["record_id"]), sorted(compiler_gap_rebase, key=lambda row: row["record_id"]), summary


def output_payloads() -> dict[str, str]:
    readiness, work, compiler_gap_rebase, summary = derive()
    payloads = {
        "product-readiness.jsonl": lines(readiness),
        "closure-work-items.jsonl": lines(work),
        "compiler-gap-rebase.jsonl": lines(compiler_gap_rebase),
        "summary.json": json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    manifest = {
        "manifest_id": "retained_product_dossier_readiness_manifest",
        "as_of": AS_OF,
        "files": {
            name: {"sha256": digest(text), "bytes": len(text.encode("utf-8"))}
            for name, text in sorted(payloads.items())
        },
    }
    payloads["manifest.json"] = json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    return payloads


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payloads = output_payloads()
    mismatches = []
    for name, text in payloads.items():
        path = HERE / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                mismatches.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if mismatches:
        print("ERROR stale readiness outputs: " + ", ".join(mismatches))
        return 1
    print(("CHECK" if args.check else "BUILD") + " PASS: 5 deterministic readiness outputs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
