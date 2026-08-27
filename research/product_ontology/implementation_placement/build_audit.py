#!/usr/bin/env python3
"""Build an independent trace audit for the Python placement foundation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "audit.json"

EVIDENCE_FILES = [
    "shannon-python-placement.json",
    "shannon-python-module-crosswalk.jsonl",
    "shannon-python-source-totality.json",
    "shannon-codebase-intelligence-ddd.json",
    "shannon-python-extraction-candidates.jsonl",
    "shannon-python-placement-evidence.jsonl",
    "manifest.json",
]
VALIDATOR_FILES = [
    "validate_shannon_python_placement.py",
    "validate_shannon_python_schemas.py",
    "validate_shannon_python_source_totality.py",
    "validate_shannon_codebase_intelligence_ddd.py",
    "validate_shannon_python_extraction_frontier.py",
    "validate_python_placement_evidence.py",
    "validate_manifest.py",
]


def read_json(name: str) -> dict[str, Any]:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def read_jsonl(name: str) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in (HERE / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256(name: str) -> str:
    return f"sha256:{hashlib.sha256((HERE / name).read_bytes()).hexdigest()}"


def canonical_digest(value: Any) -> str:
    material = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(material).hexdigest()}"


def main() -> int:
    placement = read_json("shannon-python-placement.json")
    placement_summary = read_json("summary.json")
    totality = read_json("shannon-python-source-totality.json")
    ddd = read_json("shannon-codebase-intelligence-ddd.json")
    ddd_summary = read_json("shannon-codebase-intelligence-ddd-summary.json")
    extraction = read_jsonl("shannon-python-extraction-candidates.jsonl")
    extraction_summary = read_json("shannon-python-extraction-summary.json")
    evidence = read_jsonl("shannon-python-placement-evidence.jsonl")
    evidence_summary = read_json("shannon-python-placement-evidence-summary.json")

    requirements = [
        {
            "requirement_id": "placement.application_product_boundary",
            "requirement": "The Python package is assigned to the application-domain plane and is not collapsed into the universal enterprise data/analytics platform.",
            "evidence_refs": ["shannon-python-placement.json", "shannon-codebase-intelligence-ddd.json"],
            "decision": placement["placement_verdict"],
            "validator_refs": ["validate_shannon_python_placement.py", "validate_shannon_codebase_intelligence_ddd.py"],
            "status": "SATISFIED_CANDIDATE_BOUNDARY_NOT_RATIFIED",
            "remaining_gate": "accountable ontology/product authority disposition",
        },
        {
            "requirement_id": "placement.current_source_totality",
            "requirement": "Every current Python source file is represented by a module scope or one explicit digest-bound package-facade exclusion.",
            "evidence_refs": ["shannon-python-module-crosswalk.jsonl", "shannon-python-source-totality.json"],
            "decision": totality["status"],
            "validator_refs": ["validate_shannon_python_source_totality.py"],
            "status": "SATISFIED_FOR_CURRENT_SOURCE_TREE",
            "remaining_gate": "revalidation after every source-tree change",
        },
        {
            "requirement_id": "placement.sovereign_ddd",
            "requirement": "The application has explicit sovereign responsibility, contexts, artifacts, commands, events, states, invariants, refusals, authority, time, concurrency, APIs, dependencies and exit seams.",
            "evidence_refs": ["shannon-codebase-intelligence-ddd.json"],
            "decision": ddd["portfolio_disposition"],
            "validator_refs": ["validate_shannon_codebase_intelligence_ddd.py"],
            "status": "SATISFIED_COMPLETE_CANDIDATE_DDD",
            "remaining_gate": "semantic and product ratification",
        },
        {
            "requirement_id": "placement.reusable_extraction_separation",
            "requirement": "Potential reusable libraries and method kernels are exact-source candidates, not silently promoted platform libraries.",
            "evidence_refs": ["shannon-python-extraction-candidates.jsonl", "shannon-python-extraction-summary.json"],
            "decision": extraction_summary["status"],
            "validator_refs": ["validate_shannon_python_extraction_frontier.py"],
            "status": "SATISFIED_CANDIDATE_SCOPES_GATES_OPEN",
            "remaining_gate": "exact abstract contract, semantic owner, purity proof and qualification per candidate",
        },
        {
            "requirement_id": "placement.primary_evidence",
            "requirement": "The boundary decision is challenged with claim-bound standards, official technical documentation and independently adopted products.",
            "evidence_refs": ["shannon-python-placement-evidence.jsonl"],
            "decision": evidence_summary["status"],
            "validator_refs": ["validate_python_placement_evidence.py"],
            "status": "SATISFIED_RESEARCH_EVIDENCE_NOT_AUTHORITY",
            "remaining_gate": "periodic source freshness and product-identity review",
        },
        {
            "requirement_id": "placement.qualification_separation",
            "requirement": "Research, candidate semantics, implementation identity, qualification, portability, vertical acceptance, build readiness and ratification remain separate gates.",
            "evidence_refs": ["shannon-python-placement.json", "shannon-python-extraction-candidates.jsonl", "shannon-codebase-intelligence-ddd.json"],
            "decision": "NO_DOWNSTREAM_GATE_PROMOTED",
            "validator_refs": ["validate_shannon_python_placement.py", "validate_shannon_python_extraction_frontier.py", "validate_shannon_codebase_intelligence_ddd.py"],
            "status": "SATISFIED_FAIL_CLOSED",
            "remaining_gate": "execute B10-B15 evidence programs rather than changing status fields",
        },
        {
            "requirement_id": "placement.deterministic_traceability",
            "requirement": "Every reported placement claim is traceable through deterministic generated artifacts, source digests and validators.",
            "evidence_refs": EVIDENCE_FILES,
            "decision": "DIGEST_BOUND_GENERATED_CORPUS",
            "validator_refs": VALIDATOR_FILES,
            "status": "SATISFIED_FOR_CURRENT_COMMIT",
            "remaining_gate": "repository-wide validation and future freshness enforcement",
        },
    ]

    artifact_digests = [
        {
            "path": str((HERE / name).relative_to(ROOT)),
            "sha256": sha256(name),
        }
        for name in sorted(set(EVIDENCE_FILES + VALIDATOR_FILES))
    ]
    audit = {
        "schema_version": "1.0.0",
        "audit_id": "shannon_python_implementation_placement_completion_audit",
        "scope": "The checked-in Python application boundary and its relationship to the broader data-engineering and analytics product model.",
        "application_product_id": placement["application_product"]["product_id"],
        "implementation_id": placement["implementation_id"],
        "requirements": requirements,
        "computed_counts": {
            "module_count": placement_summary["module_count"],
            "source_file_count": totality["actual_python_source_file_count"],
            "explicit_source_exclusion_count": totality["explicit_exclusion_count"],
            "bounded_context_count": ddd_summary["bounded_context_count"],
            "owned_artifact_count": ddd_summary["owned_artifact_count"],
            "extraction_candidate_count": len(extraction),
            "bound_exact_contract_count": extraction_summary[
                "candidates_with_bound_exact_contract"
            ],
            "qualified_extraction_candidate_count": extraction_summary[
                "qualified_candidate_count"
            ],
            "claim_bound_primary_source_count": len(evidence),
        },
        "artifact_digests": artifact_digests,
        "remaining_frontier": [
            {
                "gate": "ontology_and_product_authority",
                "count": 1,
                "status": "OPEN_AUTHORITY_REQUIRED",
            },
            {
                "gate": "exact_abstract_contract_binding",
                "count": len(extraction),
                "status": "OPEN_PER_CANDIDATE",
            },
            {
                "gate": "implementation_identity_and_reproducible_build",
                "count": len(extraction) + 1,
                "status": "OPEN_B10",
            },
            {
                "gate": "exact_scope_execution_and_independent_appraisal",
                "count": len(extraction) + 1,
                "status": "OPEN_B11",
            },
            {
                "gate": "second_implementation_portability_exit",
                "count": len(extraction),
                "status": "OPEN_ONLY_WHERE_HORIZONTAL_PORTABILITY_IS_PROPOSED",
            },
            {
                "gate": "physical_binding_security_slo_cost",
                "count": 1,
                "status": "OPEN_B13_FOR_APPLICATION_RELEASE",
            },
            {
                "gate": "executed_acceptance_and_ratification",
                "count": 1,
                "status": "OPEN_APPLICATION_ACCEPTANCE_AND_PRODUCT_AUTHORITY",
            },
        ],
        "verdict": "FOUNDATION_VALIDATED_DOWNSTREAM_AUTHORITY_AND_QUALIFICATION_GATES_OPEN",
        "semantic_ratified": False,
        "implementation_qualified": False,
        "build_ready": False,
        "product_ratified": False,
        "overall_completion_claim": False,
    }
    audit["audit_digest"] = canonical_digest(audit)
    OUTPUT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "audit_id": audit["audit_id"],
                "requirement_count": len(requirements),
                "artifact_digest_count": len(artifact_digests),
                "verdict": audit["verdict"],
                "audit_digest": audit["audit_digest"],
                "completion_claim": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
