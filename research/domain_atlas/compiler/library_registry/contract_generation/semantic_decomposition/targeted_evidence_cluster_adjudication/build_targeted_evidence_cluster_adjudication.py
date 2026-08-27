#!/usr/bin/env python3
"""Factor six targeted evidence campaigns into reversible coordinate-cluster challenges."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
AS_OF = "2026-08-27"

CAMPAIGNS = {
    "composition_algebra": ("p3c_composition_algebra_evidence", "p3c_composition_algebra_coordinate_ontology"),
    "grain_and_cardinality": ("p3e_grain_cardinality_evidence", "p3e_grain_coordinate_ontology"),
    "identity_and_equality": ("p3i_identity_equality_evidence", "p3i_identity_equality_coordinate_ontology"),
    "order_and_topology": ("p3o_order_topology_evidence", "p3o_order_topology_coordinate_ontology"),
    "partiality_and_uncertainty": ("p3u_partiality_uncertainty_evidence", "p3u_partiality_uncertainty_coordinate_ontology"),
    "state_and_change": ("p3s_state_change_evidence", "p3s_state_change_coordinate_ontology"),
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def one_file(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    if len(matches) != 1:
        raise ValueError(f"expected one {pattern} in {directory}, found {len(matches)}")
    return matches[0]


def build() -> dict[str, Any]:
    challenge_rows = []
    occurrence_rows = []
    axis_rows = []
    for axis, (evidence_dir_name, coordinate_dir_name) in sorted(CAMPAIGNS.items()):
        evidence_dir = SEM / evidence_dir_name
        coordinate_dir = SEM / coordinate_dir_name
        candidates = {row["family_ref"]: row for row in load_jsonl(evidence_dir / "evidence-candidates.jsonl")}
        dockets = {row["family_ref"]: row for row in load_jsonl(evidence_dir / "family-evidence-dockets.jsonl")}
        routes = load_jsonl(one_file(coordinate_dir, "member*routes.jsonl"))
        clusters = load_jsonl(one_file(coordinate_dir, "member*clusters.jsonl"))
        route_by_library = {row["library_ref"]: row for row in routes}
        axis_challenges = []
        axis_occurrences = []
        for cluster in sorted(clusters, key=lambda row: row["cluster_id"]):
            family_ref = cluster["family_ref"]
            candidate = candidates[family_ref]
            docket = dockets[family_ref]
            members = sorted(cluster["library_refs"])
            member_routes = [route_by_library[ref] for ref in members]
            if any(route["research_cluster_ref"] != cluster["cluster_id"] for route in member_routes):
                raise ValueError(f"{cluster['cluster_id']}: member route/cluster mismatch")
            no_member_evidence = cluster["research_route"].startswith("NO_MEMBER_")
            priority = "P0" if no_member_evidence or len(members) >= 10 else "P1"
            challenge_id = f"challenge.targeted-evidence-cluster.{slug(cluster['cluster_id'])}.v1"
            occurrence_refs = []
            for route in member_routes:
                occurrence_id = f"occurrence.targeted-evidence-adjudication.{slug(route['route_id'])}.v1"
                occurrence_refs.append(occurrence_id)
                required_inventories = {
                    key: value
                    for key, value in route.items()
                    if key.startswith("required_")
                }
                axis_occurrences.append(
                    {
                        "record_kind": "targeted_evidence_member_adjudication_occurrence",
                        "occurrence_id": occurrence_id,
                        "axis": axis,
                        "library_ref": route["library_ref"],
                        "family_ref": family_ref,
                        "source_gap_ref": route["source_gap_ref"],
                        "coordinate_route_ref": route["route_id"],
                        "coordinate_cluster_ref": cluster["cluster_id"],
                        "cluster_challenge_ref": challenge_id,
                        "family_evidence_candidate_ref": candidate["evidence_candidate_id"],
                        "family_evidence_docket_ref": docket["docket_id"],
                        "route_evidence_class": route["research_route"],
                        "required_use_site_inventories": required_inventories,
                        "family_evidence_to_member_binding": "UNTESTED",
                        "member_applicability": "UNRESOLVED",
                        "member_exception_decision": "UNRESOLVED",
                        "owner_decision": "UNRESOLVED",
                        "coordinate_answers_supplied": False,
                        "compiler_action": "REFUSE_MEMBER_COORDINATE_BINDING",
                        "refusal_reasons": [
                            "FAMILY_EVIDENCE_NOT_ADJUDICATED_AT_MEMBER_USE_SITE",
                            "MEMBER_APPLICABILITY_UNRESOLVED",
                            "MEMBER_EXCEPTION_STATUS_UNRESOLVED",
                            "OWNER_DECISION_UNRATIFIED",
                        ],
                        "canonical_gaps_closed": 0,
                        "completion_claim": False,
                    }
                )
            challenge = {
                "record_kind": "targeted_evidence_coordinate_cluster_challenge",
                "challenge_id": challenge_id,
                "axis": axis,
                "coordinate_package_ref": coordinate_dir_name,
                "coordinate_cluster_ref": cluster["cluster_id"],
                "family_ref": family_ref,
                "family_evidence_candidate_ref": candidate["evidence_candidate_id"],
                "family_evidence_docket_ref": docket["docket_id"],
                "bounded_claim": candidate["bounded_claim"],
                "candidate_coordinate_implications": candidate["candidate_coordinate_implications"],
                "authority_limit": candidate["authority_limit"],
                "negative_twin": candidate["negative_twin"],
                "source": candidate["source"],
                "route_evidence_class": cluster["research_route"],
                "flat_candidate_facets": cluster["flat_candidate_facets"],
                "library_refs": members,
                "library_count": len(members),
                "member_occurrence_refs": occurrence_refs,
                "member_occurrence_count": len(occurrence_refs),
                "evidence_to_cluster_binding": "UNTESTED",
                "evidence_sufficiency": "UNDETERMINED",
                "member_applicability_decisions": 0,
                "member_exception_decisions": 0,
                "owner_decisions": 0,
                "priority": priority,
                "required_challenges": [
                    "prove the bounded source claim addresses this cluster's bearer and use-site rather than only the family name",
                    "inventory the exact subjects, operations, relations, transitions, operands, claims or representations required by the coordinate route",
                    "execute the evidence candidate's negative twin against representative and adversarial members",
                    "decide applicability or prohibition for every member without a family default",
                    "split any member whose coordinate, lifecycle, authority, formalism or refusal law differs",
                    "name and ratify the bounded-context owner before producing coordinate answers",
                ],
                "status": "OPEN_CLUSTER_EVIDENCE_CHALLENGE",
                "canonical_gaps_closed": 0,
                "completion_claim": False,
            }
            axis_challenges.append(challenge)
        challenge_rows.extend(axis_challenges)
        occurrence_rows.extend(axis_occurrences)
        axis_rows.append(
            {
                "record_kind": "targeted_evidence_axis_adjudication_workstream",
                "workstream_id": f"workstream.targeted-evidence-cluster.{axis.replace('_', '-')}.v1",
                "axis": axis,
                "campaign_ref": evidence_dir_name,
                "coordinate_package_ref": coordinate_dir_name,
                "cluster_challenge_refs": [row["challenge_id"] for row in axis_challenges],
                "cluster_challenge_count": len(axis_challenges),
                "member_occurrence_count": len(axis_occurrences),
                "p0_challenge_count": sum(row["priority"] == "P0" for row in axis_challenges),
                "p1_challenge_count": sum(row["priority"] == "P1" for row in axis_challenges),
                "execution_law": "Challenge cluster evidence first, then adjudicate every exact member occurrence; no cluster result becomes a family default.",
                "status": "OPEN_MEMBER_APPLICABILITY_ADJUDICATION",
                "completion_claim": False,
            }
        )

    summary = {
        "program_id": "program.targeted-evidence-cluster-adjudication.v1",
        "as_of": AS_OF,
        "targeted_axes": len(axis_rows),
        "axis_workstreams": len(axis_rows),
        "coordinate_cluster_challenges": len(challenge_rows),
        "lexical_hypothesis_clusters": sum(not row["route_evidence_class"].startswith("NO_MEMBER_") for row in challenge_rows),
        "no_member_evidence_clusters": sum(row["route_evidence_class"].startswith("NO_MEMBER_") for row in challenge_rows),
        "member_adjudication_occurrences": len(occurrence_rows),
        "p0_cluster_challenges": sum(row["priority"] == "P0" for row in challenge_rows),
        "p1_cluster_challenges": sum(row["priority"] == "P1" for row in challenge_rows),
        "evidence_to_cluster_bindings_adjudicated": 0,
        "member_applicability_decisions": 0,
        "member_exception_decisions": 0,
        "owner_decisions": 0,
        "coordinate_answers_supplied": 0,
        "canonical_gaps_closed": 0,
        "completion_claim": False,
    }
    return {"challenges": challenge_rows, "occurrences": occurrence_rows, "axes": axis_rows, "summary": summary}


def outputs() -> dict[str, str]:
    built = build()
    files = {
        "coordinate-cluster-challenges.jsonl": "".join(canonical(row) + "\n" for row in built["challenges"]),
        "member-adjudication-occurrences.jsonl": "".join(canonical(row) + "\n" for row in built["occurrences"]),
        "axis-adjudication-workstreams.jsonl": "".join(canonical(row) + "\n" for row in built["axes"]),
        "summary.json": json.dumps(built["summary"], ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    }
    claims = {name: {"bytes": len(text.encode()), "sha256": hashlib.sha256(text.encode()).hexdigest()} for name, text in files.items()}
    files["manifest.json"] = json.dumps(
        {"manifest_id": "manifest.targeted-evidence-cluster-adjudication.v1", "as_of": AS_OF, "files": claims, "completion_claim": False},
        sort_keys=True,
        indent=2,
    ) + "\n"
    return files


def main() -> int:
    for name, text in outputs().items():
        (HERE / name).write_text(text)
    summary = build()["summary"]
    print(
        "BUILD PASS targeted evidence cluster adjudication: "
        f"{summary['coordinate_cluster_challenges']} quotient challenges preserve "
        f"{summary['member_adjudication_occurrences']} exact member occurrences across "
        f"{summary['targeted_axes']} axes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
