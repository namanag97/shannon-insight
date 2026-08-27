#!/usr/bin/env python3
"""Build the missing semantic-implementation-physical binding seam."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
SEM = HERE.parent
P6 = SEM / "p6_implementation_qualification"
QUALIFICATION = REPO / "research/product_ontology/qualification_program"
CONFORMANCE = REPO / "research/domain_atlas/compiler/conformance_evaluation"
PROVIDERS = REPO / "research/domain_atlas/compiler/provider_target_registry"
SCOPES = P6 / "qualification-scope-kernels.jsonl"
DOCKETS = P6 / "subject-dockets.jsonl"
SUBJECTS = QUALIFICATION / "library-qualification-subjects.jsonl"
CONTEXTS = CONFORMANCE / "context-families.jsonl"
CAPABILITY_CLASSES = PROVIDERS / "capability-classes.jsonl"
OFFERS = PROVIDERS / "concrete-offers.jsonl"
MAPPINGS = PROVIDERS / "compiler-requirement-offer-mappings.jsonl"
RECEIPTS = PROVIDERS / "qualification-receipts.jsonl"
TARGETS = PROVIDERS / "target-occurrences.jsonl"
AS_OF = "2026-08-27"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def snapshot() -> dict[str, Any]:
    files = []
    for path in (SCOPES, DOCKETS, SUBJECTS, CONTEXTS, CAPABILITY_CLASSES, OFFERS, MAPPINGS, RECEIPTS, TARGETS):
        data = path.read_bytes()
        files.append({
            "path": str(path.relative_to(REPO)),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "record_count": len(load_jsonl(path)),
        })
    aggregate = hashlib.sha256(canonical(files).encode()).hexdigest()
    return {"snapshot_id": f"snapshot.p7-input.{aggregate[:16]}", "aggregate_sha256": aggregate, "files": files}


def profile_signature(scope: dict[str, Any]) -> dict[str, Any]:
    signature = scope["signature"]
    return {
        "required_conformance_context_refs": sorted(signature["required_conformance_context_refs"]),
        "required_evidence_classes": sorted(signature["required_evidence_classes"]),
        "effect_boundary": signature["effect_boundary"],
    }


SOURCE_CLAIMS = [
    {
        "claim_id": "claim.p7.slsa.provenance.v1-2",
        "source_url": "https://slsa.dev/spec/v1.2/",
        "retrieved_at": AS_OF,
        "bounded_claim": "SLSA defines supply-chain levels/tracks and attestation formats including build provenance.",
        "usable_for": ["build provenance carrier", "build integrity evidence vocabulary"],
        "not_authority_for": ["domain semantics", "implementation conformance", "product acceptance"],
    },
    {
        "claim_id": "claim.p7.in-toto.attestation.v1",
        "source_url": "https://github.com/in-toto/attestation/tree/main/spec/v1",
        "retrieved_at": AS_OF,
        "bounded_claim": "The in-toto Attestation Framework defines a statement and subject/resource descriptors for verifiable claims.",
        "usable_for": ["content-addressed evidence envelope", "predicate and subject binding"],
        "not_authority_for": ["claim truth", "oracle authority", "qualification verdict"],
    },
    {
        "claim_id": "claim.p7.nist.ssdf.1-1",
        "source_url": "https://csrc.nist.gov/pubs/sp/800/218/final",
        "retrieved_at": AS_OF,
        "bounded_claim": "NIST SSDF 1.1 defines high-level secure software development practices usable across SDLC implementations.",
        "usable_for": ["secure-development control vocabulary", "supplier evidence questions"],
        "not_authority_for": ["control execution at an occurrence", "artifact qualification", "semantic correctness"],
    },
]


def build_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    snap = snapshot()
    scopes = load_jsonl(SCOPES)
    dockets = load_jsonl(DOCKETS)
    subjects = {row["subject_id"]: row for row in load_jsonl(SUBJECTS)}
    contexts = {row["id"]: row for row in load_jsonl(CONTEXTS)}
    capability_classes = load_jsonl(CAPABILITY_CLASSES)
    offers = load_jsonl(OFFERS)
    mappings = load_jsonl(MAPPINGS)
    receipts = load_jsonl(RECEIPTS)
    targets = load_jsonl(TARGETS)

    profile_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    profile_signatures: dict[str, dict[str, Any]] = {}
    for scope in scopes:
        signature = profile_signature(scope)
        profile_id = f"profile.p7.qualification.{digest(signature)[:20]}.v1"
        profile_signatures[profile_id] = signature
        profile_groups[profile_id].append(scope)

    profiles = []
    for profile_id, members in sorted(profile_groups.items()):
        signature = profile_signatures[profile_id]
        context_plane_counts = collections.Counter(contexts[ref]["assurance_plane"] for ref in signature["required_conformance_context_refs"])
        subject_refs = sorted({ref for scope in members for ref in scope["subject_refs"]})
        profiles.append({
            "record_kind": "implementation_qualification_profile_kernel",
            "profile_id": profile_id,
            "edition": 1,
            "signature": signature,
            "context_plane_counts": dict(sorted(context_plane_counts.items())),
            "qualification_scope_refs": sorted(scope["scope_id"] for scope in members),
            "subject_refs": subject_refs,
            "implementation_slot_refs": sorted(ref for scope in members for ref in scope["implementation_slot_refs"]),
            "scope_count": len(members),
            "subject_count": len(subject_refs),
            "implementation_slot_count": sum(len(scope["implementation_slot_refs"]) for scope in members),
            "sharing_law": "Share conformance methods, generators and evidence schemas for this exact profile; execute and adjudicate every implementation slot and exact scope separately.",
            "status": "OPEN_PROFILE_EXECUTION_METHOD",
            "completion_claim": False,
        })
    profile_by_scope = {scope_ref: profile for profile in profiles for scope_ref in profile["qualification_scope_refs"]}

    docket_by_subject = {row["subject_ref"]: row for row in dockets}
    context_subjects: dict[str, list[str]] = collections.defaultdict(list)
    for subject_ref, subject in subjects.items():
        for context_ref in subject["required_conformance_context_refs"]:
            context_subjects[context_ref].append(subject_ref)
    workstreams = []
    for context_ref, subject_refs in sorted(context_subjects.items()):
        context = contexts[context_ref]
        local_dockets = [docket_by_subject[ref] for ref in subject_refs]
        scope_refs = sorted({row["qualification_scope_ref"] for row in local_dockets})
        workstreams.append({
            "record_kind": "conformance_context_execution_workstream",
            "workstream_id": f"workstream.p7.{context_ref.removeprefix('context.ce.')}.v1",
            "edition": 1,
            "context_ref": context_ref,
            "assurance_plane": context["assurance_plane"],
            "label": context["label"],
            "inside": context["inside"],
            "outside": context["outside"],
            "qualification_profile_refs": sorted({profile_by_scope[ref]["profile_id"] for ref in scope_refs}),
            "qualification_scope_refs": scope_refs,
            "subject_refs": sorted(subject_refs),
            "subject_context_occurrence_count": len(subject_refs),
            "shared_assets_allowed": ["test method", "generator", "fixture schema", "oracle interface", "evidence schema"],
            "shared_verdict_forbidden": True,
            "status": "OPEN_EXECUTION_WORKSTREAM",
            "completion_claim": False,
        })

    templates = []
    binding_gates = []
    for scope in sorted(scopes, key=lambda row: row["scope_id"]):
        profile = profile_by_scope[scope["scope_id"]]
        semantic_capability_refs = sorted({cap for ref in scope["subject_refs"] for cap in subjects[ref]["provided_capability_refs"]})
        for slot_ref in scope["implementation_slot_refs"]:
            template_id = f"template.p7.offer-intake.{digest(slot_ref)[:20]}.v1"
            templates.append({
                "record_kind": "semantic_implementation_offer_intake_template",
                "template_id": template_id,
                "edition": 1,
                "implementation_slot_ref": slot_ref,
                "qualification_scope_ref": scope["scope_id"],
                "qualification_profile_ref": profile["profile_id"],
                "semantic_capability_refs": semantic_capability_refs,
                "required_submission_fields": [
                    "implementation_offer_id", "implemented_exact_contract_ref", "artifact_identity",
                    "source_digest", "artifact_digest", "dependency_lock_digest", "configuration_digest",
                    "build_provenance_attestation_refs", "sbom_refs", "physical_requirement_refs",
                    "supported_target_profile_refs", "conformance_execution_plan_refs",
                    "invalidation_triggers", "validity_interval", "implementer_authority_ref",
                ],
                "submission": {
                    "implementation_offer_id": None,
                    "implemented_exact_contract_ref": None,
                    "artifact_identity": None,
                    "source_digest": None,
                    "artifact_digest": None,
                    "dependency_lock_digest": None,
                    "configuration_digest": None,
                    "build_provenance_attestation_refs": None,
                    "sbom_refs": None,
                    "physical_requirement_refs": None,
                    "supported_target_profile_refs": None,
                    "conformance_execution_plan_refs": None,
                    "invalidation_triggers": None,
                    "validity_interval": None,
                    "implementer_authority_ref": None,
                },
                "source_claim_refs": [row["claim_id"] for row in SOURCE_CLAIMS],
                "status": "EMPTY_AWAITING_IMPLEMENTATION_OFFER",
                "completion_claim": False,
            })
            binding_gates.append({
                "record_kind": "semantic_implementation_physical_binding_gate",
                "gate_id": f"gate.p7.binding.{digest(slot_ref)[:20]}.v1",
                "edition": 1,
                "implementation_slot_ref": slot_ref,
                "offer_intake_template_ref": template_id,
                "qualification_scope_ref": scope["scope_id"],
                "qualification_profile_ref": profile["profile_id"],
                "semantic_capability_refs": semantic_capability_refs,
                "declared_physical_requirement_refs": [],
                "provider_requirement_offer_mapping_refs": [],
                "provider_offer_candidate_refs": [],
                "target_occurrence_candidate_refs": [],
                "qualification_receipt_refs": [],
                "refusal_codes": [
                    "EXACT_CONTRACT_UNRATIFIED", "NO_IMPLEMENTATION_OFFER_SUBMISSION",
                    "NO_DECLARED_PHYSICAL_REQUIREMENTS", "NO_AUTHORIZED_SEMANTIC_PHYSICAL_BRIDGE",
                    "NO_EXACT_TARGET_OCCURRENCE", "NO_PASSING_EXACT_SCOPE_RECEIPTS",
                ],
                "name_matching_forbidden": True,
                "status": "REFUSE_SEMANTIC_PHYSICAL_BINDING",
                "completion_claim": False,
            })

    semantic_capabilities = {cap for subject in subjects.values() for cap in subject["provided_capability_refs"]}
    physical_catalog_capabilities = {row["capability_class_id"] for row in capability_classes}
    offered_physical_capabilities = {cap for offer in offers for cap in offer["capability_class_refs"]}
    provider_summary = {
        "record_kind": "provider_registry_interface_summary",
        "edition": 1,
        "as_of": AS_OF,
        "semantic_capability_refs": len(semantic_capabilities),
        "physical_capability_classes": len(physical_catalog_capabilities),
        "offered_physical_capability_refs": len(offered_physical_capabilities),
        "semantic_physical_identifier_intersection": len(semantic_capabilities & physical_catalog_capabilities),
        "provider_requirement_offer_mappings": len(mappings),
        "concrete_provider_offers": len(offers),
        "target_occurrences": len(targets),
        "qualification_assessments": len(receipts),
        "qualified_assessments": sum(row.get("outcome") == "pass" and row.get("independent_appraisal") for row in receipts),
        "bridge_law": "A semantic implementation offer declares physical requirements; provider-neutral mappings satisfy those requirements. Semantic and physical capability identifiers are never joined by spelling.",
        "status": "OPEN_NO_SEMANTIC_IMPLEMENTATION_BRIDGES",
        "completion_claim": False,
    }
    return profiles, workstreams, templates, binding_gates, provider_summary, snap


def outputs() -> dict[str, str]:
    profiles, workstreams, templates, gates, provider_summary, snap = build_records()
    summary = {
        "program_id": "program.p7-offer-binding-qualification.v1",
        "edition": 1,
        "as_of": AS_OF,
        "input_snapshot": snap,
        "qualification_profile_kernels": len(profiles),
        "shared_profile_kernels": sum(row["scope_count"] > 1 for row in profiles),
        "represented_qualification_scopes": sum(row["scope_count"] for row in profiles),
        "conformance_context_workstreams": len(workstreams),
        "represented_subject_context_occurrences": sum(row["subject_context_occurrence_count"] for row in workstreams),
        "implementation_offer_intake_templates": len(templates),
        "semantic_physical_binding_gates": len(gates),
        "submitted_implementation_offers": 0,
        "authorized_semantic_physical_bridges": 0,
        "selected_provider_offers": 0,
        "qualified_implementations": 0,
        "completion_claim": False,
    }
    files = {
        "evidence-carrier-source-claims.jsonl": "".join(canonical({"record_kind": "bounded_external_source_claim", "edition": 1, "completion_claim": False, **row}) + "\n" for row in SOURCE_CLAIMS),
        "qualification-profile-kernels.jsonl": "".join(canonical(row) + "\n" for row in profiles),
        "conformance-context-workstreams.jsonl": "".join(canonical(row) + "\n" for row in workstreams),
        "implementation-offer-intake-templates.jsonl": "".join(canonical(row) + "\n" for row in templates),
        "semantic-physical-binding-gates.jsonl": "".join(canonical(row) + "\n" for row in gates),
        "provider-registry-interface-summary.json": json.dumps(provider_summary, sort_keys=True, indent=2) + "\n",
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p7-offer-binding-qualification.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    built = outputs()
    for name, text in built.items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text() != text:
                stale.append(name)
        else:
            path.write_text(text)
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = json.loads(built["summary.json"])
    print(f"{'CHECK' if args.check else 'BUILD'} PASS P7: {summary['represented_qualification_scopes']} scopes factor into {summary['qualification_profile_kernels']} profiles and {summary['represented_subject_context_occurrences']} context obligations into {summary['conformance_context_workstreams']} workstreams; all {summary['semantic_physical_binding_gates']} bindings refuse")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
