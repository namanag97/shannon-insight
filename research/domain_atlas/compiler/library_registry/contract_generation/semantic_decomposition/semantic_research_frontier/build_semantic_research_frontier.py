#!/usr/bin/env python3
"""Derive the next semantic research frontier over all live axes."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


LANES = {
    "TARGETED_EVIDENCE_REBASE": {
        "lane_id": "lane.semantic-frontier.01.targeted-evidence-rebase",
        "priority": "P0",
        "meaning": "Campaign evidence exists for former generic vacancies; independently adjudicate family/member applicability, exceptions and coordinate laws.",
        "shared_work": [
            "campaign-to-family-axis evidence intake schema",
            "member applicability and negative-twin review protocol",
            "exception-cluster and residual schema",
        ],
        "must_remain_local": [
            "semantic meaning",
            "owner",
            "member applicability",
            "exceptions",
            "exact contract",
            "acceptance",
        ],
    },
    "AMBIGUOUS_MODAL_SPLIT": {
        "lane_id": "lane.semantic-frontier.02.ambiguous-modal-split",
        "priority": "P1",
        "meaning": "Direct structured evidence exists, but at least one family has no unique modal candidate; split or falsify before owner review.",
        "shared_work": [
            "counterexample search protocol",
            "candidate-cluster split test",
            "homonym and owner-collision challenge packet",
        ],
        "must_remain_local": [
            "family split",
            "bounded-context owner",
            "member exception",
            "non-collapse law",
            "ratification",
        ],
    },
    "OWNER_REVIEW_READY": {
        "lane_id": "lane.semantic-frontier.03.owner-review-ready",
        "priority": "P2",
        "meaning": "Direct structured evidence and a review candidate exist for every family; the remaining operation is owner challenge and receipt, not more broad research by default.",
        "shared_work": [
            "owner review packet transport",
            "receipt schema",
            "counterfactual stability and negative-twin checklist",
        ],
        "must_remain_local": [
            "owner decision",
            "family default",
            "member exception",
            "authority receipt",
            "canonical mutation",
        ],
    },
}


def build() -> dict[str, Any]:
    axis_ontology = load_json(SEM / "semantic-axis-ontology.json")
    axes = [row["axis"] for row in axis_ontology["axes"]]
    dockets = load_jsonl(SEM / "p3_applicability_adjudication/family-axis-review-dockets.jsonl")
    campaigns = {
        row["axis"]: row
        for row in load_jsonl(SEM / "targeted_evidence_coverage/campaign-coverage.jsonl")
    }
    by_axis: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in dockets:
        by_axis[row["semantic_axis"]].append(row)
    if set(axes) != set(by_axis):
        raise ValueError(
            f"axis/docket mismatch missing={sorted(set(axes)-set(by_axis))} "
            f"extra={sorted(set(by_axis)-set(axes))}"
        )

    frontier: list[dict[str, Any]] = []
    for axis in axes:
        rows = by_axis[axis]
        blocked = [row for row in rows if row["status"] == "BLOCKED_REQUIRES_EVIDENCE_OR_SPLIT"]
        evidence_counts: Counter[str] = Counter()
        review_counts: Counter[str] = Counter()
        for row in rows:
            evidence_counts.update(row["evidence_state_counts"])
            review_counts[row["review_class"]] += 1
        campaign = campaigns.get(axis)
        if campaign:
            lane_key = "TARGETED_EVIDENCE_REBASE"
            next_operation = "INTAKE_CAMPAIGN_EVIDENCE_THEN_ADJUDICATE_EVERY_TARGET_MEMBER_AND_EXCEPTION"
            research_state = "CAMPAIGN_EVIDENCE_ROUTED_MEMBER_APPLICABILITY_UNRESOLVED"
        elif blocked:
            lane_key = "AMBIGUOUS_MODAL_SPLIT"
            next_operation = "SPLIT_OR_FALSIFY_NON_UNIQUE_MODAL_CLUSTERS_BEFORE_OWNER_REVIEW"
            research_state = "DIRECT_EVIDENCE_PRESENT_NON_UNIQUE_MODAL_SPLIT_REQUIRED"
        else:
            lane_key = "OWNER_REVIEW_READY"
            next_operation = "OWNER_CHALLENGE_RATIFICATION_AND_MEMBER_EXCEPTION_RECEIPTS"
            research_state = "DIRECT_EVIDENCE_PRESENT_OWNER_REVIEW_READY"
        lane = LANES[lane_key]
        frontier.append(
            {
                "record_kind": "semantic_axis_research_frontier",
                "axis": axis,
                "phase": rows[0]["phase"],
                "constitution_ref": rows[0]["constitution_ref"],
                "module_ref": rows[0]["module_ref"],
                "lane_ref": lane["lane_id"],
                "priority": lane["priority"],
                "family_dockets": len(rows),
                "member_axis_cells": sum(row["member_count"] for row in rows),
                "candidate_clusters": sum(len(row["cluster_refs"]) for row in rows),
                "candidate_exception_clusters": sum(
                    len(row["candidate_exception_cluster_refs"]) for row in rows
                ),
                "review_ready_dockets": len(rows) - len(blocked),
                "blocked_dockets": len(blocked),
                "review_class_counts": dict(sorted(review_counts.items())),
                "projection_evidence_state_counts": dict(sorted(evidence_counts.items())),
                "targeted_campaign_ref": campaign["campaign_ref"] if campaign else None,
                "targeted_family_packages": campaign["targeted_work_packages"] if campaign else 0,
                "targeted_library_occurrences": campaign["targeted_library_occurrences"]
                if campaign
                else 0,
                "campaign_evidence_routed": campaign is not None,
                "research_state": research_state,
                "next_closure_operation": next_operation,
                "shared_mechanics_allowed": lane["shared_work"],
                "decisions_that_must_remain_local": lane["must_remain_local"],
                "owner_decisions": 0,
                "member_applicability_decisions": 0,
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    lane_order = {row["lane_id"]: i for i, row in enumerate(LANES.values())}
    frontier.sort(
        key=lambda row: (
            lane_order[row["lane_ref"]],
            -row["targeted_library_occurrences"],
            -row["blocked_dockets"],
            -row["candidate_exception_clusters"],
            row["axis"],
        )
    )
    for rank, row in enumerate(frontier, 1):
        row["frontier_rank"] = rank

    lane_records: list[dict[str, Any]] = []
    for lane_key, lane in LANES.items():
        members = [row for row in frontier if row["lane_ref"] == lane["lane_id"]]
        lane_records.append(
            {
                "record_kind": "semantic_research_lane",
                "lane_id": lane["lane_id"],
                "priority": lane["priority"],
                "meaning": lane["meaning"],
                "axis_refs": [row["axis"] for row in members],
                "axis_count": len(members),
                "family_dockets": sum(row["family_dockets"] for row in members),
                "member_axis_cells": sum(row["member_axis_cells"] for row in members),
                "blocked_dockets": sum(row["blocked_dockets"] for row in members),
                "targeted_family_packages": sum(
                    row["targeted_family_packages"] for row in members
                ),
                "targeted_library_occurrences": sum(
                    row["targeted_library_occurrences"] for row in members
                ),
                "shared_mechanics_allowed": lane["shared_work"],
                "decisions_that_must_remain_local": lane["must_remain_local"],
                "can_execute_concurrently_with_lane_refs": [
                    other["lane_id"]
                    for other_key, other in LANES.items()
                    if other_key != lane_key
                ],
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
        )

    return {
        "frontier": frontier,
        "lanes": lane_records,
        "summary": {
            "program_id": "program.semantic-research-frontier.v1",
            "as_of": AS_OF,
            "semantic_axes": len(frontier),
            "research_lanes": len(lane_records),
            "family_axis_dockets": sum(row["family_dockets"] for row in frontier),
            "member_axis_cells": sum(row["member_axis_cells"] for row in frontier),
            "candidate_clusters": sum(row["candidate_clusters"] for row in frontier),
            "candidate_exception_clusters": sum(
                row["candidate_exception_clusters"] for row in frontier
            ),
            "review_ready_dockets": sum(row["review_ready_dockets"] for row in frontier),
            "blocked_dockets": sum(row["blocked_dockets"] for row in frontier),
            "targeted_axes_with_campaign_routes": sum(
                1 for row in frontier if row["campaign_evidence_routed"]
            ),
            "targeted_family_packages": sum(
                row["targeted_family_packages"] for row in frontier
            ),
            "targeted_library_occurrences": sum(
                row["targeted_library_occurrences"] for row in frontier
            ),
            "owner_decisions": 0,
            "member_applicability_decisions": 0,
            "canonical_gaps_closed": 0,
            "completion_claim": False,
        },
    }


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "axis-frontier.jsonl": "".join(canonical(row) + "\n" for row in built["frontier"]),
        "research-lanes.jsonl": "".join(canonical(row) + "\n" for row in built["lanes"]),
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
            "manifest_id": "manifest.semantic-research-frontier.v1",
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
        "BUILD PASS semantic research frontier: "
        f"{summary['semantic_axes']} axes and {summary['member_axis_cells']} cells factor into "
        f"{summary['research_lanes']} concurrent lanes; zero gaps closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
