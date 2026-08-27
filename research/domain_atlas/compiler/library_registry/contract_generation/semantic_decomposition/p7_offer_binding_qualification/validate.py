#!/usr/bin/env python3
"""Validate the P7 qualification-profile tensor and semantic/physical refusal seam."""
from __future__ import annotations

import collections
import hashlib
import json

from build_p7 import (
    CAPABILITY_CLASSES,
    CONTEXTS,
    HERE,
    MAPPINGS,
    OFFERS,
    RECEIPTS,
    SCOPES,
    SOURCE_CLAIMS,
    SUBJECTS,
    TARGETS,
    load_jsonl,
    outputs,
    profile_signature,
)


def main() -> int:
    for name, text in outputs().items():
        path = HERE / name
        assert path.is_file() and path.read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"], name

    summary = json.loads((HERE / "summary.json").read_text())
    profiles = load_jsonl(HERE / "qualification-profile-kernels.jsonl")
    workstreams = load_jsonl(HERE / "conformance-context-workstreams.jsonl")
    templates = load_jsonl(HERE / "implementation-offer-intake-templates.jsonl")
    gates = load_jsonl(HERE / "semantic-physical-binding-gates.jsonl")
    claims = load_jsonl(HERE / "evidence-carrier-source-claims.jsonl")
    provider_summary = json.loads((HERE / "provider-registry-interface-summary.json").read_text())

    assert len(profiles) == summary["qualification_profile_kernels"]
    assert sum(row["scope_count"] for row in profiles) == summary["represented_qualification_scopes"]
    assert sum(row["scope_count"] > 1 for row in profiles) == summary["shared_profile_kernels"]
    assert len(workstreams) == summary["conformance_context_workstreams"]
    assert sum(row["subject_context_occurrence_count"] for row in workstreams) == summary["represented_subject_context_occurrences"]
    assert len(templates) == summary["implementation_offer_intake_templates"]
    assert len(gates) == summary["semantic_physical_binding_gates"]
    assert len(claims) == len(SOURCE_CLAIMS) == 3
    for field in (
        "submitted_implementation_offers", "authorized_semantic_physical_bridges",
        "selected_provider_offers", "qualified_implementations",
    ):
        assert summary[field] == 0
    assert not summary["completion_claim"]

    for claim in summary["input_snapshot"]["files"]:
        path = HERE.parents[6] / claim["path"]
        data = path.read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
        assert len(load_jsonl(path)) == claim["record_count"]

    scopes = {row["scope_id"]: row for row in load_jsonl(SCOPES)}
    subjects = {row["subject_id"]: row for row in load_jsonl(SUBJECTS)}
    contexts = {row["id"]: row for row in load_jsonl(CONTEXTS)}
    assert len(scopes) == summary["represented_qualification_scopes"]
    assert len(subjects) == len(load_jsonl(SUBJECTS))

    profile_by_scope = {}
    represented_scopes = []
    represented_slots = []
    for profile in profiles:
        assert profile["scope_count"] == len(profile["qualification_scope_refs"])
        assert profile["subject_count"] == len(profile["subject_refs"])
        assert profile["implementation_slot_count"] == len(profile["implementation_slot_refs"])
        assert profile["implementation_slot_count"] == 2 * profile["scope_count"]
        for scope_ref in profile["qualification_scope_refs"]:
            scope = scopes[scope_ref]
            assert profile_signature(scope) == profile["signature"]
            profile_by_scope[scope_ref] = profile
        expected_subjects = {ref for scope_ref in profile["qualification_scope_refs"] for ref in scopes[scope_ref]["subject_refs"]}
        expected_slots = {ref for scope_ref in profile["qualification_scope_refs"] for ref in scopes[scope_ref]["implementation_slot_refs"]}
        assert set(profile["subject_refs"]) == expected_subjects
        assert set(profile["implementation_slot_refs"]) == expected_slots
        represented_scopes.extend(profile["qualification_scope_refs"])
        represented_slots.extend(profile["implementation_slot_refs"])
        assert not profile["completion_claim"]
    assert len(represented_scopes) == len(set(represented_scopes)) == len(scopes)
    assert set(represented_scopes) == set(scopes)
    assert len(represented_slots) == len(set(represented_slots)) == 2 * len(scopes)

    workstream_by_context = {row["context_ref"]: row for row in workstreams}
    expected_context_refs = {ref for subject in subjects.values() for ref in subject["required_conformance_context_refs"]}
    assert len(workstream_by_context) == len(workstreams) and set(workstream_by_context) == expected_context_refs
    represented_occurrences = []
    for context_ref, workstream in workstream_by_context.items():
        context = contexts[context_ref]
        expected_subjects = {ref for ref, subject in subjects.items() if context_ref in subject["required_conformance_context_refs"]}
        assert set(workstream["subject_refs"]) == expected_subjects
        assert workstream["subject_context_occurrence_count"] == len(expected_subjects)
        assert workstream["assurance_plane"] == context["assurance_plane"]
        expected_scopes = {scope_ref for scope_ref, scope in scopes.items() if set(scope["subject_refs"]) & expected_subjects}
        assert set(workstream["qualification_scope_refs"]) == expected_scopes
        assert set(workstream["qualification_profile_refs"]) == {profile_by_scope[ref]["profile_id"] for ref in expected_scopes}
        assert workstream["shared_verdict_forbidden"] is True
        represented_occurrences.extend((subject_ref, context_ref) for subject_ref in workstream["subject_refs"])
        assert not workstream["completion_claim"]
    expected_occurrences = {
        (subject_ref, context_ref)
        for subject_ref, subject in subjects.items()
        for context_ref in subject["required_conformance_context_refs"]
    }
    assert len(represented_occurrences) == len(set(represented_occurrences)) == len(expected_occurrences)
    assert set(represented_occurrences) == expected_occurrences

    template_by_slot = {row["implementation_slot_ref"]: row for row in templates}
    gate_by_slot = {row["implementation_slot_ref"]: row for row in gates}
    assert len(template_by_slot) == len(gate_by_slot) == len(represented_slots)
    assert set(template_by_slot) == set(gate_by_slot) == set(represented_slots)
    scope_by_slot = {slot: scope for scope in scopes.values() for slot in scope["implementation_slot_refs"]}
    for slot_ref in represented_slots:
        scope = scope_by_slot[slot_ref]
        profile = profile_by_scope[scope["scope_id"]]
        template = template_by_slot[slot_ref]
        gate = gate_by_slot[slot_ref]
        expected_capabilities = {cap for subject_ref in scope["subject_refs"] for cap in subjects[subject_ref]["provided_capability_refs"]}
        assert template["qualification_scope_ref"] == gate["qualification_scope_ref"] == scope["scope_id"]
        assert template["qualification_profile_ref"] == gate["qualification_profile_ref"] == profile["profile_id"]
        assert set(template["semantic_capability_refs"]) == set(gate["semantic_capability_refs"]) == expected_capabilities
        assert set(template["required_submission_fields"]) == set(template["submission"])
        assert all(value is None for value in template["submission"].values())
        assert template["status"] == "EMPTY_AWAITING_IMPLEMENTATION_OFFER"
        assert gate["offer_intake_template_ref"] == template["template_id"]
        assert gate["declared_physical_requirement_refs"] == []
        assert gate["provider_requirement_offer_mapping_refs"] == []
        assert gate["provider_offer_candidate_refs"] == []
        assert gate["target_occurrence_candidate_refs"] == []
        assert gate["qualification_receipt_refs"] == []
        assert gate["name_matching_forbidden"] is True
        assert gate["status"] == "REFUSE_SEMANTIC_PHYSICAL_BINDING"
        assert not template["completion_claim"] and not gate["completion_claim"]

    capability_classes = load_jsonl(CAPABILITY_CLASSES)
    offers = load_jsonl(OFFERS)
    mappings = load_jsonl(MAPPINGS)
    receipts = load_jsonl(RECEIPTS)
    targets = load_jsonl(TARGETS)
    semantic_caps = {cap for subject in subjects.values() for cap in subject["provided_capability_refs"]}
    physical_caps = {row["capability_class_id"] for row in capability_classes}
    offered_caps = {cap for offer in offers for cap in offer["capability_class_refs"]}
    assert provider_summary["semantic_capability_refs"] == len(semantic_caps)
    assert provider_summary["physical_capability_classes"] == len(physical_caps)
    assert provider_summary["offered_physical_capability_refs"] == len(offered_caps)
    assert provider_summary["semantic_physical_identifier_intersection"] == len(semantic_caps & physical_caps) == 0
    assert provider_summary["provider_requirement_offer_mappings"] == len(mappings)
    assert provider_summary["concrete_provider_offers"] == len(offers)
    assert provider_summary["target_occurrences"] == len(targets)
    assert provider_summary["qualification_assessments"] == len(receipts)
    assert provider_summary["qualified_assessments"] == 0
    assert provider_summary["status"] == "OPEN_NO_SEMANTIC_IMPLEMENTATION_BRIDGES"
    assert not provider_summary["completion_claim"]

    assert {row["claim_id"] for row in claims} == {row["claim_id"] for row in SOURCE_CLAIMS}
    assert all(row["usable_for"] and row["not_authority_for"] and not row["completion_claim"] for row in claims)
    print(
        f"PASS P7 offer binding: {len(scopes)} scopes factor exactly into {len(profiles)} "
        f"qualification profiles and {len(expected_occurrences)} context obligations into "
        f"{len(workstreams)} workstreams; {len(templates)} empty offer contracts preserve "
        "the semantic/implementation/physical seam; all bindings refuse"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
