#!/usr/bin/env python3
"""Build a lossless closure cockpit and the first ratifier-ready decision batch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REBASE = ROOT / "research/product_ontology/research_convergence_rebase"
GPT = ROOT / "research/handoffs/gpt-pro-product-ontology-convergence/output-2026-08-27"
P1 = (
    ROOT
    / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/p1_authority_symbols"
)


def load(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def write(path, records):
    Path(path).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in records))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def index_unique(rows, key, label):
    indexed = {}
    for row in rows:
        identity = row[key]
        if identity in indexed:
            raise ValueError(f"duplicate {label}: {identity}")
        indexed[identity] = row
    return indexed


def merge_disjoint(primary, supplements, key, label):
    overlap = set(primary) & set(supplements)
    if overlap:
        raise ValueError(f"supplement shadows frozen {label}: {sorted(overlap)}")
    return primary | supplements


def scope_is_covered(scope_ref, decision):
    return scope_ref in decision.get("affected_scope_refs", []) or any(
        scope_ref.startswith(prefix) for prefix in decision.get("affected_scope_prefixes", [])
    )


def main():
    rebase_summary = json.loads((REBASE / "summary.json").read_text(encoding="utf-8"))
    rebased = [
        row
        for row in load(REBASE / "rebased-gap-dispositions.jsonl")
        if row.get("research_addressable") is True
    ]
    physical = load(REBASE / "physical-governance-gate-deltas.jsonl")
    frozen_resolutions = index_unique(
        load(GPT / "source-authority-resolutions.jsonl"),
        "family_ref",
        "frozen source-authority family",
    )
    current_resolutions = index_unique(
        load(HERE / "source-authority-resolution-supplements.jsonl"),
        "family_ref",
        "supplemental source-authority family",
    )
    resolutions = merge_disjoint(
        frozen_resolutions,
        current_resolutions,
        "family_ref",
        "source-authority family",
    )
    packets = index_unique(
        load(P1 / "source-authority-packets.jsonl"),
        "family_id",
        "source-authority packet family",
    )
    frozen_sources = index_unique(
        load(GPT / "source-register.jsonl"),
        "source_id",
        "frozen source",
    )
    current_sources = index_unique(
        load(HERE / "source-authority-source-supplements.jsonl"),
        "source_id",
        "supplemental source",
    )
    current_source_validation = {}
    for source_id, source in sorted(current_sources.items()):
        input_path = ROOT / source["input_source_record_path"]
        input_rows = load(input_path) if input_path.is_file() else []
        matching_input_rows = [row for row in input_rows if row.get("source_id") == source_id]
        input_url = matching_input_rows[0].get("url") if len(matching_input_rows) == 1 else None
        current_source_validation[source_id] = {
            "input_source_record_resolves_exactly_once": len(matching_input_rows) == 1,
            "source_url_identity_matches": input_url == source["url_or_doi"],
            "bounded_claim_present": bool(source.get("exact_bounded_claim_supported")),
            "authority_limit_present": bool(source.get("authority_limit")),
            "negative_twin_present": bool(source.get("counterexample_or_negative_twin")),
            "invalidation_condition_present": bool(source.get("invalidation_condition")),
            "research_status_not_authority": source.get("status") == "RESEARCHED_CANDIDATE",
            "completion_not_claimed": source.get("completion_claim") is False,
        }
        if not all(current_source_validation[source_id].values()):
            raise ValueError(
                f"invalid supplemental source record {source_id}: "
                f"{current_source_validation[source_id]}"
            )
    sources = merge_disjoint(
        frozen_sources,
        current_sources,
        "source_id",
        "source identity",
    )
    rebased_by_id = index_unique(rebased, "rebase_id", "rebased research quotient")
    current_research_decisions = index_unique(
        load(HERE / "current-research-decision-supplements.jsonl"),
        "research_decision_id",
        "current proposed-unratified research decision",
    )
    decision_rebase_owners = {}
    for decision_id, decision in sorted(current_research_decisions.items()):
        evidence_checks = {
            evidence["path"]: sha(ROOT / evidence["path"]) == evidence["sha256"]
            for evidence in decision["input_evidence"]
        }
        checks = {
            "resolved_rebase_ids_present": bool(decision.get("resolved_rebase_ids")),
            "all_rebase_ids_resolve": set(decision["resolved_rebase_ids"]) <= set(rebased_by_id),
            "all_input_evidence_digests_match": all(evidence_checks.values()),
            "all_source_refs_resolve": set(decision["source_refs"]) <= set(sources),
            "bounded_decision_present": bool(decision.get("bounded_decision")),
            "negative_twins_present": bool(decision.get("counterexample_or_negative_twin")),
            "rejected_inferences_present": bool(decision.get("rejected_inferences")),
            "invalidation_condition_present": bool(decision.get("invalidation_condition")),
            "research_status_not_authority": decision.get("status") == "PROPOSED_UNRATIFIED",
            "completion_not_claimed": decision.get("completion_claim") is False,
        }
        if not all(checks.values()):
            raise ValueError(f"invalid current research decision {decision_id}: {checks}")
        for rebase_id in decision["resolved_rebase_ids"]:
            if rebase_id in decision_rebase_owners:
                raise ValueError(f"current research decisions overlap at {rebase_id}")
            base = rebased_by_id[rebase_id]
            if base["gap_kind"] not in decision["gap_kinds"]:
                raise ValueError(f"current research decision gap kind mismatch: {rebase_id}")
            if not all(
                scope_is_covered(scope_ref, decision)
                for scope_ref in base["current_affected_scope_refs"]
            ):
                raise ValueError(f"current research decision scope mismatch: {rebase_id}")
            decision_rebase_owners[rebase_id] = decision_id
    resolution_supplements = index_unique(
        load(HERE / "current-research-resolution-supplements.jsonl")
        + load(HERE / "current-research-resolution-symbol-supplements.jsonl"),
        "rebase_id",
        "current research-resolution supplement",
    )
    source_authority_resolution_ids = index_unique(
        list(current_resolutions.values()),
        "source_authority_resolution_id",
        "supplemental source-authority resolution",
    )
    resolution_ids = source_authority_resolution_ids | current_research_decisions

    effective_resolution_receipts = []
    for rebase_id, supplement in sorted(resolution_supplements.items()):
        if rebase_id not in rebased_by_id:
            raise ValueError(f"supplement references unknown rebase quotient: {rebase_id}")
        base = rebased_by_id[rebase_id]
        resolution_ref = supplement["evidence_resolution_ref"]
        if resolution_ref not in resolution_ids:
            raise ValueError(f"supplement references unknown current resolution: {resolution_ref}")
        resolution = resolution_ids[resolution_ref]
        resolved_atoms = supplement["resolved_research_atoms"]
        if supplement["gap_kind"] != base["gap_kind"]:
            raise ValueError(f"supplement gap kind mismatch: {rebase_id}")
        if resolution_ref in source_authority_resolution_ids:
            if resolution["family_ref"] not in base["current_affected_scope_refs"]:
                raise ValueError(f"supplement resolution scope mismatch: {rebase_id}")
        elif (
            rebase_id not in resolution["resolved_rebase_ids"]
            or decision_rebase_owners.get(rebase_id) != resolution_ref
        ):
            raise ValueError(f"supplement research-decision binding mismatch: {rebase_id}")
        if (
            base.get("research_vacancy") is not True
            or base.get("research_residual_atoms", 0) < resolved_atoms
            or resolved_atoms <= 0
        ):
            raise ValueError(
                f"supplement does not resolve a live bounded research vacancy: {rebase_id}"
            )
        if supplement["canonical_gaps_closed"] != 0 or supplement["completion_claim"] is not False:
            raise ValueError(f"supplement fabricates canonical completion: {rebase_id}")
        effective_resolution_receipts.append(
            {
                "effective_resolution_receipt_id": "receipt.effective."
                + supplement["research_resolution_supplement_id"],
                "research_resolution_supplement_ref": supplement[
                    "research_resolution_supplement_id"
                ],
                "rebase_id": rebase_id,
                "gap_kind": base["gap_kind"],
                "evidence_resolution_ref": resolution_ref,
                "prior_research_residual_atoms": base["research_residual_atoms"],
                "resolved_research_atoms": resolved_atoms,
                "effective_research_residual_atoms": base["research_residual_atoms"]
                - resolved_atoms,
                "effective_research_vacancy": base["research_residual_atoms"] - resolved_atoms > 0,
                "remaining_closure_condition": supplement["remaining_closure_condition"],
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    supplemented_resolution_refs = {
        row["evidence_resolution_ref"] for row in resolution_supplements.values()
    }
    if supplemented_resolution_refs != set(resolution_ids):
        raise ValueError(
            "every current research decision must bind at least one research-resolution supplement"
        )
    for decision_id, decision in current_research_decisions.items():
        bound_rebase_ids = {
            row["rebase_id"]
            for row in resolution_supplements.values()
            if row["evidence_resolution_ref"] == decision_id
        }
        if bound_rebase_ids != set(decision["resolved_rebase_ids"]):
            raise ValueError(f"current research decision coverage mismatch: {decision_id}")

    resolved_atoms_by_rebase = {
        row["rebase_id"]: row["resolved_research_atoms"] for row in effective_resolution_receipts
    }

    order = [
        ("source-authority", "P01", "named source/schema authority ratification"),
        ("researched-symbol-owner", "P02A", "named semantic-owner ratification"),
        (
            "symbol-owner-adjudication-batch",
            "P02B",
            "collision/challenge adjudication and owner ratification",
        ),
        ("family-axis-evidence", "P03", "member applicability appraisal and owner ratification"),
        ("applicability", "P04", "family-axis applicability ratification"),
        ("exact-contract", "P05", "exact public contract ratification"),
        ("implementation", "P06A", "implementation plus executable-oracle receipts"),
        ("qualification", "P06B", "two independent conformance qualifications"),
        ("product-gate", "P07", "product build, offer, appraisal and vertical acceptance receipts"),
    ]
    all_rows = rebased + physical
    tranches = []
    for gap_kind, tranche_id, closure in order:
        rows = [row for row in all_rows if row["gap_kind"] == gap_kind]
        base_residual_quotients = sum(bool(row.get("research_vacancy")) for row in rows)
        base_residual_atoms = sum(row.get("research_residual_atoms", 0) for row in rows)
        supplement_atoms = sum(
            resolved_atoms_by_rebase.get(row.get("rebase_id"), 0) for row in rows
        )
        effective_residual_atoms = base_residual_atoms - supplement_atoms
        effective_residual_quotients = sum(
            row.get("research_residual_atoms", 0)
            - resolved_atoms_by_rebase.get(row.get("rebase_id"), 0)
            > 0
            for row in rows
        )
        tranches.append(
            {
                "tranche_id": tranche_id,
                "gap_kind": gap_kind,
                "quotient_count": len(rows),
                "atom_count": sum(row["current_atom_count"] for row in rows),
                "research_residual_quotient_count_before_current_supplements": base_residual_quotients,
                "research_residual_atom_count_before_current_supplements": base_residual_atoms,
                "current_supplement_resolved_atom_count": supplement_atoms,
                "research_residual_quotient_count": effective_residual_quotients,
                "research_residual_atom_count": effective_residual_atoms,
                "closure_condition": closure,
                "research_only_can_finish": gap_kind
                not in {"implementation", "qualification", "product-gate"},
                "status": "IN_PROGRESS"
                if gap_kind == "source-authority"
                else "BLOCKED_BY_PREDECESSOR",
                "completion_claim": False,
            }
        )

    appraisals = []
    for family, resolution in sorted(resolutions.items()):
        packet = packets[family]
        source_path = ROOT / resolution["input_source_path"]
        unresolved_refs = sorted(set(resolution["source_refs"]) - set(sources))
        checks = {
            "current_source_digest_matches": sha(source_path)
            == resolution["input_source_digest"]
            == packet["source_digest"],
            "packet_identity_matches": resolution["input_packet_ref"] == packet["packet_id"],
            "library_count_matches": resolution["library_count"] == packet["library_count"],
            "all_evidence_refs_resolve": not unresolved_refs,
            "evidence_and_source_refs_match": set(resolution["evidence_refs"])
            == set(resolution["source_refs"]),
            "all_supplemental_evidence_records_valid": all(
                all(current_source_validation[ref].values())
                for ref in resolution["source_refs"]
                if ref in current_source_validation
            ),
            "bounded_rationale_present": bool(resolution["bounded_rationale"]),
            "negative_twin_present": bool(resolution["counterexample_or_negative_twin"]),
            "invalidation_condition_present": bool(resolution["invalidation_condition"]),
            "canonical_completion_not_claimed": resolution["completion_claim"] is False,
        }
        appraisals.append(
            {
                "appraisal_id": "appraisal.precheck." + family.removeprefix("constitution.family."),
                "family_ref": family,
                "packet_ref": packet["packet_id"],
                "proposed_decision": resolution["adoption_decision"],
                "checks": checks,
                "unresolved_evidence_refs": unresolved_refs,
                "ratifier_payload": {
                    "source_digest": resolution["input_source_digest"],
                    "bounded_rationale": resolution["bounded_rationale"],
                    "record_level_rule": resolution["record_level_rule"],
                    "rejected_inferences": resolution["rejected_inferences"],
                    "source_refs": resolution["source_refs"],
                    "invalidation_condition": resolution["invalidation_condition"],
                },
                "status": "READY_FOR_NAMED_RATIFIER_REVIEW"
                if all(checks.values())
                else "PRECHECK_REFUSED",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    write(HERE / "closure-tranches.jsonl", tranches)
    write(HERE / "source-authority-ratification-batch.jsonl", appraisals)
    write(HERE / "effective-research-resolution-receipts.jsonl", effective_resolution_receipts)
    base_residual_quotients = sum(bool(row.get("research_vacancy")) for row in rebased)
    base_residual_atoms = sum(row.get("research_residual_atoms", 0) for row in rebased)
    effective_residual_quotients = sum(row["research_residual_quotient_count"] for row in tranches)
    effective_residual_atoms = sum(row["research_residual_atom_count"] for row in tranches)
    summary = {
        "prior_snapshot_gap_quotients": rebase_summary["prior_gap_quotients"],
        "current_gap_quotients": len(all_rows),
        "current_gap_atoms": sum(row["current_atom_count"] for row in all_rows),
        "research_candidate_quotients": len(rebased),
        "research_residual_quotients_before_current_supplements": base_residual_quotients,
        "research_residual_atoms_before_current_supplements": base_residual_atoms,
        "current_supplement_resolved_quotients": len(effective_resolution_receipts),
        "current_supplement_resolved_atoms": sum(
            row["resolved_research_atoms"] for row in effective_resolution_receipts
        ),
        "research_residual_quotients": effective_residual_quotients,
        "research_residual_atoms": effective_residual_atoms,
        "physical_governance_quotients": len(physical),
        "source_authority_prechecks_complete": sum(
            row["status"] == "READY_FOR_NAMED_RATIFIER_REVIEW" for row in appraisals
        ),
        "source_authority_prechecks_refused": sum(
            row["status"] == "PRECHECK_REFUSED" for row in appraisals
        ),
        "canonical_gaps_closed": 0,
        "source_authority_current_family_count": next(
            row["quotient_count"] for row in tranches if row["gap_kind"] == "source-authority"
        ),
        "source_authority_prepared_payload_count": len(appraisals),
        "source_authority_unprepared_family_count": next(
            row["research_residual_quotient_count"]
            for row in tranches
            if row["gap_kind"] == "source-authority"
        ),
        "next_required_action": "All 29 newly introduced or expanded research quotients now have digest-bound proposed-unratified dispositions. Named semantic authorities must accept, modify, split or reject the 24 source-family payloads, 16-axis application decisions, eight exact application contracts and seven symbol-batch classifications; separate verifiers must attest exact receipts before canonical ingestion. Research preparation is not ratification, implementation, qualification or acceptance.",
        "completion_claim": False,
    }
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
