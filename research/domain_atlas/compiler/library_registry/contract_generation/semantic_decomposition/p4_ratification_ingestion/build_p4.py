#!/usr/bin/env python3
"""Ingest externally verified ratification receipts and emit non-mutating delta candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SEM = HERE.parent
P2_TEMPLATES = SEM / "p2_owner_adjudication/owner-ratification-packet-templates.jsonl"
P3_TEMPLATES = SEM / "p3_applicability_adjudication/family-axis-ratification-packet-templates.jsonl"
P5_TEMPLATES = SEM / "p5_exact_contract_adjudication/exact-contract-ratification-packet-templates.jsonl"
P1B_TEMPLATES = SEM / "p1b_foundation_authority_adjudication/ratification-packet-templates.jsonl"
RECEIPTS = HERE / "ratification-receipts.jsonl"
VERIFICATIONS = HERE / "authority-verification-receipts.jsonl"
AS_OF = "2026-08-27"


INGESTION_CONTRACT = {
    "contract_id": "contract.p4.ratification-ingestion.v1",
    "edition": 1,
    "receipt_fields": [
        "record_kind", "receipt_id", "template_ref", "template_kind", "input_snapshot_ref",
        "input_snapshot_sha256", "decision_payload", "decision_payload_digest", "authority_refs",
        "authority_verification_receipt_ref", "attestation_ref", "effective_at", "status",
    ],
    "verification_fields": [
        "record_kind", "verification_receipt_id", "ratification_receipt_ref", "template_ref",
        "authority_refs", "authorized_scope_refs", "decision_payload_digest", "verifier_ref",
        "verified_at", "attestation_digest", "status",
    ],
    "template_kinds": [
        "P1B_SOURCE_AUTHORITY", "P1B_CROSS_OWNER_COLLISION", "P1B_BOUNDED_CONTEXT_BOUNDARY",
        "P1B_FAMILY_CONSTITUTION", "P2_SYMBOL_OWNER", "P3_FAMILY_AXIS_APPLICABILITY",
        "P5_EXACT_LIBRARY_CONTRACT",
    ],
    "laws": [
        "A receipt is accepted only against the exact template snapshot and decision payload digest.",
        "Authority verification is a separate externally issued receipt bound to the same payload and scope.",
        "Blocked upstream templates cannot be ratified by bypassing their challenge package.",
        "P2 occurrence and P3 cluster/member decisions must cover the exact referenced sets.",
        "Accepted receipts emit delta candidates only; this stage never mutates a canonical registry.",
    ],
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def template_ref(row: dict[str, Any]) -> str:
    return row.get("ratification_packet_id") or row["template_id"]


def snapshot() -> dict[str, Any]:
    files = []
    for path in (P1B_TEMPLATES, P2_TEMPLATES, P3_TEMPLATES, P5_TEMPLATES, RECEIPTS, VERIFICATIONS):
        data = path.read_bytes()
        files.append({
            "path": str(path.relative_to(HERE.parents[6])),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "record_count": len(load_jsonl(path)),
        })
    aggregate = digest(files)
    return {"snapshot_id": f"snapshot.p4-input.{aggregate[:16]}", "aggregate_sha256": aggregate, "files": files}


def exact_ref_set(payload: dict[str, Any], field: str, item_ref_field: str) -> set[str] | None:
    value = payload.get(field)
    if not isinstance(value, list) or any(not isinstance(item, dict) or item_ref_field not in item for item in value):
        return None
    refs = [item[item_ref_field] for item in value]
    return set(refs) if len(refs) == len(set(refs)) else None


def refusal(receipt: dict[str, Any], code: str, detail: str) -> dict[str, Any]:
    return {
        "record_kind": "ratification_receipt_refusal",
        "refusal_id": f"refusal.p4.{receipt.get('receipt_id', 'missing')}.{code.lower()}",
        "edition": 1,
        "receipt_ref": receipt.get("receipt_id"),
        "template_ref": receipt.get("template_ref"),
        "code": code,
        "detail": detail,
        "canonical_mutation_allowed": False,
        "canonical_gaps_closed": 0,
        "status": "REFUSED",
        "completion_claim": False,
    }


def adjudicate() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    p2 = load_jsonl(P2_TEMPLATES)
    p3 = load_jsonl(P3_TEMPLATES)
    p5 = load_jsonl(P5_TEMPLATES)
    p1b = load_jsonl(P1B_TEMPLATES)
    templates = {template_ref(row): (row["template_kind"], row) for row in p1b}
    templates.update({template_ref(row): ("P2_SYMBOL_OWNER", row) for row in p2})
    receipts = load_jsonl(RECEIPTS)
    verifications = load_jsonl(VERIFICATIONS)
    templates.update({template_ref(row): ("P3_FAMILY_AXIS_APPLICABILITY", row) for row in p3})
    templates.update({template_ref(row): ("P5_EXACT_LIBRARY_CONTRACT", row) for row in p5})
    if len(templates) != len(p1b) + len(p2) + len(p3) + len(p5):
        raise ValueError("duplicate template reference")
    verification_by_id = {row.get("verification_receipt_id"): row for row in verifications}
    if None in verification_by_id or len(verification_by_id) != len(verifications):
        raise ValueError("missing or duplicate authority verification receipt id")
    receipt_ids = [row.get("receipt_id") for row in receipts]
    if None in receipt_ids or len(receipt_ids) != len(set(receipt_ids)):
        raise ValueError("missing or duplicate ratification receipt id")

    ledger = []
    refusals = []
    deltas = []
    accepted_templates = set()
    for receipt in receipts:
        missing = [field for field in INGESTION_CONTRACT["receipt_fields"] if field not in receipt]
        if missing:
            refusals.append(refusal(receipt, "MISSING_RECEIPT_FIELDS", f"missing {missing}"))
            continue
        pair = templates.get(receipt["template_ref"])
        if pair is None:
            refusals.append(refusal(receipt, "UNKNOWN_TEMPLATE", "template reference does not resolve"))
            continue
        expected_kind, template = pair
        if receipt["template_kind"] != expected_kind:
            refusals.append(refusal(receipt, "TEMPLATE_KIND_MISMATCH", "receipt kind does not match resolved template"))
            continue
        if template["status"] != "READY_FOR_NAMED_AUTHORITY_REVIEW":
            refusals.append(refusal(receipt, "UPSTREAM_TEMPLATE_BLOCKED", "challenge or evidence package remains open"))
            continue
        if receipt["input_snapshot_ref"] != template["input_snapshot_ref"] or receipt["input_snapshot_sha256"] != template["input_snapshot_sha256"]:
            refusals.append(refusal(receipt, "INPUT_SNAPSHOT_MISMATCH", "receipt is not bound to the exact template input"))
            continue
        if digest(receipt["decision_payload"]) != receipt["decision_payload_digest"]:
            refusals.append(refusal(receipt, "DECISION_PAYLOAD_DIGEST_MISMATCH", "decision payload digest does not verify"))
            continue
        required_payload = set(template["required_receipt_fields"]) - {"receipt_id"}
        if not required_payload <= set(receipt["decision_payload"]):
            refusals.append(refusal(receipt, "INCOMPLETE_DECISION_PAYLOAD", f"missing {sorted(required_payload - set(receipt['decision_payload']))}"))
            continue
        verification = verification_by_id.get(receipt["authority_verification_receipt_ref"])
        if verification is None:
            refusals.append(refusal(receipt, "AUTHORITY_VERIFICATION_MISSING", "authority verification receipt does not resolve"))
            continue
        missing_verification = [field for field in INGESTION_CONTRACT["verification_fields"] if field not in verification]
        if missing_verification:
            refusals.append(refusal(receipt, "AUTHORITY_VERIFICATION_INCOMPLETE", f"missing {missing_verification}"))
            continue
        if not (
            verification["status"] == "VERIFIED_BY_EXTERNAL_TRUST_PROVIDER"
            and verification["ratification_receipt_ref"] == receipt["receipt_id"]
            and verification["template_ref"] == receipt["template_ref"]
            and verification["decision_payload_digest"] == receipt["decision_payload_digest"]
            and verification["authority_refs"] == receipt["authority_refs"]
        ):
            refusals.append(refusal(receipt, "AUTHORITY_VERIFICATION_MISMATCH", "verification is not exact for receipt, template, payload and authorities"))
            continue
        required_scope = {template.get("symbol_ref") or template.get("matrix_ref") or template.get("library_ref") or template["subject_ref"]}
        if not required_scope <= set(verification["authorized_scope_refs"]):
            refusals.append(refusal(receipt, "AUTHORITY_SCOPE_INSUFFICIENT", "verified authority does not cover the exact symbol or matrix"))
            continue

        payload = receipt["decision_payload"]
        if expected_kind == "P2_SYMBOL_OWNER":
            actual_refs = exact_ref_set(payload, "complete_occurrence_dispositions", "relation_proposal_ref")
            expected_refs = set(template["occurrence_relation_proposal_refs"])
            delta_payload = {
                "symbol_ref": template["symbol_ref"],
                "chosen_symbol_disposition": payload.get("chosen_symbol_disposition"),
                "semantic_owner_refs_or_complete_local_owner_map": payload.get("semantic_owner_refs_or_complete_local_owner_map"),
                "definition_equality_lifecycle_contract_digest": payload.get("definition_equality_lifecycle_contract_digest"),
                "complete_occurrence_dispositions": payload.get("complete_occurrence_dispositions"),
            }
        elif expected_kind == "P3_FAMILY_AXIS_APPLICABILITY":
            cluster_refs = exact_ref_set(payload, "complete_cluster_decisions", "cluster_ref")
            member_refs = exact_ref_set(payload, "complete_member_exception_decisions", "member_preclassification_ref")
            actual_refs = (cluster_refs, member_refs)
            expected_refs = (set(template["cluster_refs"]), set(template["member_preclassification_refs"]))
            delta_payload = {
                "matrix_ref": template["matrix_ref"],
                "family_ref": template["family_ref"],
                "semantic_axis": template["semantic_axis"],
                "family_default_applicability_decision": payload.get("family_default_applicability_decision"),
                "complete_cluster_decisions": payload.get("complete_cluster_decisions"),
                "complete_member_exception_decisions": payload.get("complete_member_exception_decisions"),
            }
        elif expected_kind == "P5_EXACT_LIBRARY_CONTRACT":
            dimension_payload = payload.get("contract_dimension_payload")
            prerequisite_refs = exact_ref_set(payload, "prerequisite_ratification_receipt_refs", "template_ref")
            actual_refs = prerequisite_refs
            expected_refs = set(template["required_prerequisite_template_refs"])
            if not isinstance(dimension_payload, dict) or set(dimension_payload) != {
                "boundary_and_negative_mission", "semantic_owner_and_context_map",
                "ubiquitous_language_and_public_names", "identity_equality_and_canonicalization",
                "types_traits_operations_and_queries", "commands_events_state_and_time",
                "laws_invariants_and_refusal_precedence", "authority_policy_and_effect_boundary",
                "partiality_uncertainty_and_information_loss", "finite_resources_concurrency_and_cancellation",
                "representation_dto_acl_and_compatibility", "dependencies_features_and_removal_seams",
                "evidence_negative_twins_and_conformance", "platform_supply_chain_and_code_risk",
                "migration_deprecation_and_historical_replay",
            }:
                refusals.append(refusal(receipt, "INCOMPLETE_CONTRACT_DIMENSION_PAYLOAD", "exact contract must cover all fifteen dimensions"))
                continue
            delta_payload = {
                "library_ref": template["library_ref"],
                "exact_api_contract": payload.get("exact_api_contract"),
                "contract_dimension_payload": dimension_payload,
                "source_authority_receipt_ref": payload.get("source_authority_receipt_ref"),
                "boundary_decision_receipt_ref": payload.get("boundary_decision_receipt_ref"),
                "family_constitution_receipt_ref": payload.get("family_constitution_receipt_ref"),
                "prerequisite_ratification_receipt_refs": payload.get("prerequisite_ratification_receipt_refs"),
            }
        else:
            if expected_kind == "P1B_FAMILY_CONSTITUTION":
                actual_refs = exact_ref_set(payload, "prerequisite_ratification_receipt_bindings", "template_ref")
                expected_refs = set(template["required_prerequisite_template_refs"])
                if not isinstance(payload.get("constitution_section_payload"), dict) or not payload["constitution_section_payload"]:
                    refusals.append(refusal(receipt, "INCOMPLETE_FAMILY_CONSTITUTION", "constitution section payload is missing"))
                    continue
            elif expected_kind == "P1B_BOUNDED_CONTEXT_BOUNDARY":
                actual_refs = exact_ref_set(payload, "collision_receipt_bindings", "template_ref")
                expected_refs = set(template["required_prerequisite_template_refs"])
            else:
                actual_refs = set()
                expected_refs = set()
            delta_payload = {
                "template_kind": expected_kind,
                "subject_ref": template["subject_ref"],
                "decision_payload": payload,
            }
        if actual_refs != expected_refs:
            refusals.append(refusal(receipt, "EXACT_DECISION_COVERAGE_MISMATCH", "decision members do not equal the template reference set"))
            continue
        if receipt["template_ref"] in accepted_templates:
            refusals.append(refusal(receipt, "DUPLICATE_TEMPLATE_RATIFICATION", "a verified receipt already binds this template"))
            continue

        accepted_templates.add(receipt["template_ref"])
        ledger.append({
            "record_kind": "verified_ratification_ledger_entry",
            "ledger_entry_id": f"ledger.p4.{receipt['receipt_id']}",
            "edition": 1,
            "receipt_ref": receipt["receipt_id"],
            "verification_receipt_ref": verification["verification_receipt_id"],
            "template_ref": receipt["template_ref"],
            "template_kind": expected_kind,
            "decision_payload_digest": receipt["decision_payload_digest"],
            "authority_refs": receipt["authority_refs"],
            "effective_at": receipt["effective_at"],
            "status": "VERIFIED_RATIFICATION",
            "completion_claim": False,
        })
        deltas.append({
            "record_kind": "canonical_delta_candidate",
            "delta_candidate_id": f"delta-candidate.p4.{receipt['receipt_id']}",
            "edition": 1,
            "template_kind": expected_kind,
            "template_ref": receipt["template_ref"],
            "ratification_ledger_ref": f"ledger.p4.{receipt['receipt_id']}",
            "delta_payload": delta_payload,
            "delta_payload_digest": digest(delta_payload),
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "ELIGIBLE_FOR_SEPARATE_CANONICAL_CHANGE_REVIEW",
            "completion_claim": False,
        })

    blocked = []
    for ref, (kind, template) in sorted(templates.items()):
        if ref in accepted_templates:
            continue
        blocked.append({
            "record_kind": "unratified_template_index",
            "template_ref": ref,
            "template_kind": kind,
            "upstream_status": template["status"],
            "blocker": "UPSTREAM_TEMPLATE_BLOCKED" if template["status"] != "READY_FOR_NAMED_AUTHORITY_REVIEW" else "NO_VERIFIED_RATIFICATION_RECEIPT",
            "canonical_mutation_allowed": False,
            "canonical_gaps_closed": 0,
            "status": "OPEN",
            "completion_claim": False,
        })
    return ledger, refusals, deltas, blocked, snapshot()


def outputs() -> dict[str, str]:
    ledger, refusals, deltas, blocked, snap = adjudicate()
    summary = {
        "program_id": "program.p4-ratification-ingestion.v1",
        "edition": 1,
        "as_of": AS_OF,
        "input_snapshot": snap,
        "total_templates": len(blocked) + len(ledger),
        "submitted_ratification_receipts": len(load_jsonl(RECEIPTS)),
        "authority_verification_receipts": len(load_jsonl(VERIFICATIONS)),
        "verified_ratifications": len(ledger),
        "receipt_refusals": len(refusals),
        "canonical_delta_candidates": len(deltas),
        "unratified_templates": len(blocked),
        "canonical_mutations_allowed": 0,
        "canonical_exact_gaps_closed": 0,
        "completion_claim": False,
    }
    files = {
        "ingestion-contract.json": json.dumps(INGESTION_CONTRACT, sort_keys=True, indent=2) + "\n",
        "verified-ratification-ledger.jsonl": "".join(canonical(row) + "\n" for row in ledger),
        "receipt-refusals.jsonl": "".join(canonical(row) + "\n" for row in refusals),
        "canonical-delta-candidates.jsonl": "".join(canonical(row) + "\n" for row in deltas),
        "unratified-template-index.jsonl": "".join(canonical(row) + "\n" for row in blocked),
        "summary.json": json.dumps(summary, sort_keys=True, indent=2) + "\n",
    }
    manifest = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps({"manifest_id": "manifest.p4-ratification-ingestion.v1", "as_of": AS_OF, "files": manifest, "completion_claim": False}, sort_keys=True, indent=2) + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for name, text in outputs().items():
        path = HERE / name
        if args.check:
            if not path.is_file() or path.read_text() != text:
                stale.append(name)
        else:
            path.write_text(text)
    if stale:
        print("STALE " + ", ".join(stale))
        return 1
    summary = json.loads(outputs()["summary.json"])
    print(f"{'CHECK' if args.check else 'BUILD'} PASS P4: {summary['total_templates']} templates, {summary['verified_ratifications']} verified receipts, {summary['canonical_delta_candidates']} non-mutating delta candidates; zero canonical mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
