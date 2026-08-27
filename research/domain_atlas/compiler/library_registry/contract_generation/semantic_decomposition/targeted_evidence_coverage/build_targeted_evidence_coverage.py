#!/usr/bin/env python3
"""Build the fail-closed audit over every targeted semantic-axis campaign."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
TARGETS = SEM / "structured_projection/targeted-evidence-work-packages.jsonl"
AS_OF = "2026-08-27"
sys.path.insert(0, str(SEM))

from axis_evidence_campaign import canonical, digest, load_jsonl  # noqa: E402


CAMPAIGNS = {
    "composition_algebra": "p3c_composition_algebra_evidence",
    "grain_and_cardinality": "p3e_grain_cardinality_evidence",
    "identity_and_equality": "p3i_identity_equality_evidence",
    "order_and_topology": "p3o_order_topology_evidence",
    "partiality_and_uncertainty": "p3u_partiality_uncertainty_evidence",
    "state_and_change": "p3s_state_change_evidence",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def build() -> dict[str, Any]:
    targets = load_jsonl(TARGETS)
    targeted_axes = {row["axis"] for row in targets}
    if targeted_axes != set(CAMPAIGNS):
        raise ValueError(
            "targeted semantic axes differ from registered evidence campaigns: "
            f"unrouted={sorted(targeted_axes - set(CAMPAIGNS))}, "
            f"orphan_campaigns={sorted(set(CAMPAIGNS) - targeted_axes)}"
        )

    records: list[dict[str, Any]] = []
    for axis, directory in sorted(CAMPAIGNS.items()):
        campaign = SEM / directory
        summary = load_json(campaign / "summary.json")
        candidates = load_jsonl(campaign / "evidence-candidates.jsonl")
        dockets = load_jsonl(campaign / "family-evidence-dockets.jsonl")
        axis_targets = sorted(
            (row for row in targets if row["axis"] == axis),
            key=lambda row: row["family_id"],
        )
        target_by_family = {row["family_id"]: row for row in axis_targets}
        docket_by_family = {row["family_ref"]: row for row in dockets}
        candidate_by_family = {row["family_ref"]: row for row in candidates}
        if set(target_by_family) != set(docket_by_family) or set(target_by_family) != set(candidate_by_family):
            raise ValueError(f"{axis}: campaign family coverage differs from live targets")

        for family, target in target_by_family.items():
            docket = docket_by_family[family]
            candidate = candidate_by_family[family]
            if docket["work_package_ref"] != target["work_package_id"]:
                raise ValueError(f"{axis}/{family}: stale work-package reference")
            if docket["work_package_digest"] != digest(target):
                raise ValueError(f"{axis}/{family}: stale work-package digest")
            if docket["library_refs"] != target["library_refs"]:
                raise ValueError(f"{axis}/{family}: library occurrence coverage differs")
            if docket["library_count"] != target["library_count"]:
                raise ValueError(f"{axis}/{family}: library count differs")
            if docket["evidence_candidate_refs"] != [candidate["evidence_candidate_id"]]:
                raise ValueError(f"{axis}/{family}: candidate/docket link differs")

        records.append(
            {
                "record_kind": "targeted_semantic_axis_campaign_coverage",
                "axis": axis,
                "campaign_ref": directory,
                "campaign_program_ref": summary["program_id"],
                "targeted_work_package_refs": [row["work_package_id"] for row in axis_targets],
                "targeted_family_refs": [row["family_id"] for row in axis_targets],
                "targeted_work_packages": len(axis_targets),
                "targeted_library_occurrences": sum(row["library_count"] for row in axis_targets),
                "evidence_candidate_refs": [row["evidence_candidate_id"] for row in candidates],
                "evidence_docket_refs": [row["docket_id"] for row in dockets],
                "campaign_manifest_digest": "sha256:"
                + hashlib.sha256((campaign / "manifest.json").read_bytes()).hexdigest(),
                "owner_decisions": summary["owner_decisions"],
                "member_applicability_decisions": summary["member_applicability_decisions"],
                "canonical_gaps_closed": summary["canonical_gaps_closed"],
                "residual_state": "EVIDENCE_ROUTED; OWNER, MEMBER_APPLICABILITY, EXCEPTIONS, EXACT_CONTRACTS, IMPLEMENTATION_AND_ACCEPTANCE_OPEN",
                "completion_claim": False,
            }
        )

    return {
        "records": records,
        "summary": {
            "program_id": "program.targeted-semantic-axis-campaign-coverage.v1",
            "as_of": AS_OF,
            "targeted_axes": len(records),
            "registered_campaigns": len(CAMPAIGNS),
            "targeted_work_packages": sum(row["targeted_work_packages"] for row in records),
            "targeted_library_occurrences": sum(row["targeted_library_occurrences"] for row in records),
            "routed_work_packages": sum(row["targeted_work_packages"] for row in records),
            "routed_library_occurrences": sum(row["targeted_library_occurrences"] for row in records),
            "unrouted_axes": [],
            "unrouted_work_packages": 0,
            "owner_decisions": sum(row["owner_decisions"] for row in records),
            "member_applicability_decisions": sum(
                row["member_applicability_decisions"] for row in records
            ),
            "canonical_gaps_closed": sum(row["canonical_gaps_closed"] for row in records),
            "completion_claim": False,
        },
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "campaign-coverage.jsonl": "".join(canonical(row) + "\n" for row in built["records"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2)
        + "\n",
    }
    claims = {
        name: {
            "bytes": len(text.encode()),
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
        for name, text in files.items()
    }
    files["manifest.json"] = json.dumps(
        {
            "manifest_id": "manifest.targeted-semantic-axis-campaign-coverage.v1",
            "as_of": AS_OF,
            "files": claims,
            "completion_claim": False,
        },
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS targeted evidence coverage: "
        f"{summary['targeted_axes']} axes, {summary['targeted_work_packages']} packages and "
        f"{summary['targeted_library_occurrences']} occurrences routed; gap closure remains zero"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
