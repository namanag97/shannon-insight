#!/usr/bin/env python3
"""Validate completeness and non-authority of the bulk contract generation program."""

from __future__ import annotations

import hashlib
import json

from build_program import ARCHETYPE_BY_ID, EXACT, HERE, REGISTRY, build, outputs, rows


def unique(records: list[dict], key: str) -> None:
    values = [row[key] for row in records]
    assert len(values) == len(set(values)), f"duplicate {key}"


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        path = HERE / name
        assert path.is_file() and path.read_text(encoding="utf-8") == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name

    archetypes = rows(HERE / "contract-archetypes.jsonl")
    constitutions = rows(HERE / "family-constitutions.jsonl")
    proposals = rows(HERE / "library-instance-proposals.jsonl")
    clusters = rows(HERE / "boundary-falsification-clusters.jsonl")
    collisions = rows(HERE / "cross-owner-collision-candidates.jsonl")
    packages = rows(HERE / "work-packages.jsonl")
    waves = rows(HERE / "execution-waves.jsonl")
    queue = rows(EXACT / "closure-queue.jsonl")
    batches = rows(EXACT / "research-batches.jsonl")
    libraries = {row["library_id"]: row for row in rows(REGISTRY / "library-contributions.jsonl")}

    unique(archetypes, "archetype_id")
    unique(constitutions, "family_id")
    unique(proposals, "proposal_id")
    unique(clusters, "cluster_id")
    unique(collisions, "collision_id")
    unique(packages, "work_package_id")
    unique(waves, "wave_id")
    assert {row["archetype_id"] for row in archetypes} == set(ARCHETYPE_BY_ID)
    assert len(archetypes) >= 18
    assert all(row["status"] == "STRUCTURAL_PATTERN_NOT_DOMAIN_AUTHORITY" for row in archetypes)
    assert all(len(row["owner_authored_slots"]) >= 20 for row in archetypes)
    assert all(row["required_type_roles"] and row["required_operation_roles"] for row in archetypes)
    assert all(row["required_refusal_roles"] and row["required_oracle_roles"] for row in archetypes)

    exact_refs = {row["library_ref"] for row in queue}
    assert len(proposals) == len(exact_refs)
    assert {row["library_ref"] for row in proposals} == exact_refs
    assert all(row["library_ref"] in libraries for row in proposals)
    assert all(row["status"] == "PROPOSAL_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP" for row in proposals)
    assert all(row["boundary_disposition"] == "UNADJUDICATED" for row in proposals)
    assert all(row["primary_archetype_proposal"] in ARCHETYPE_BY_ID for row in proposals)
    assert all(set(row["alternate_archetype_proposals"]) <= set(ARCHETYPE_BY_ID) for row in proposals)
    assert all(row["owner_authored_slots"] and row["currently_missing_dimensions"] for row in proposals)
    assert all("No exact public name" in row["generation_prohibition"] for row in proposals)

    expected_families = {f"constitution.family.{batch['research_family']}" for batch in batches}
    configured_wave_families = {
        f"constitution.family.{family}"
        for wave in waves
        for family in wave["research_families"]
    }
    assert {row["family_id"] for row in constitutions} == expected_families
    assert configured_wave_families == expected_families
    assert all(row["status"] == "OWNER_RESEARCH_AND_ADJUDICATION_REQUIRED" for row in constitutions)
    assert all(len(row["required_truth_planes"]) == 12 for row in constitutions)
    assert all(len(row["required_constitution_sections"]) >= 13 for row in constitutions)
    assert sum(row["open_library_count"] for row in constitutions) == len(proposals)
    assert {row["family_id"] for row in proposals} == expected_families

    clustered_refs = [ref for row in clusters for ref in row["library_refs"]]
    assert len(clustered_refs) == len(set(clustered_refs)) == len(proposals)
    assert set(clustered_refs) == exact_refs
    assert all(len(row["required_tests"]) >= 6 for row in clusters)
    assert all(row["status"] == "UNADJUDICATED" for row in clusters)
    collision_pairs = {(row["left_library_ref"], row["right_library_ref"]) for row in collisions}
    assert len(collision_pairs) == len(collisions)
    assert all(left in exact_refs and right in exact_refs and left < right for left, right in collision_pairs)
    assert all(row["left_owner_refs"] != row["right_owner_refs"] for row in collisions)
    assert all(len(row["shared_responsibility_tokens"]) >= 2 for row in collisions)
    assert all(row["jaccard_similarity"] >= 0.45 for row in collisions)
    assert all(row["status"] == "LEXICAL_SIGNAL_REVIEW_REQUIRED_NOT_DUPLICATE_PROOF" for row in collisions)

    package_proposals = [ref for row in packages for ref in row["library_instance_proposal_refs"]]
    assert len(package_proposals) == len(set(package_proposals)) == len(proposals)
    assert set(package_proposals) == {row["proposal_id"] for row in proposals}
    assert len(packages) == len(batches)
    assert all(len(row["execution_dag"]) == 10 for row in packages)
    assert all(row["status"] == "BOUNDARY_FIRST_THEN_GENERATE" for row in packages)
    waved_packages = [ref for row in waves for ref in row["work_package_refs"]]
    assert len(waves) == 7
    assert len(waved_packages) == len(set(waved_packages)) == len(packages)
    assert set(waved_packages) == {row["work_package_id"] for row in packages}
    wave_positions = {row["wave_id"]: index for index, row in enumerate(waves)}
    assert all(
        all(wave_positions[dependency] < wave_positions[row["wave_id"]] for dependency in row["depends_on_wave_refs"])
        for row in waves
    )
    assert all(len(row["global_entry_gates"]) == 4 and row["status"] == "PLANNED_INCOMPLETE" for row in waves)

    summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    assert summary["completion_claim"] is False and summary["status"] == "ACTIVE_INCOMPLETE"
    assert summary["counts"] == {key: len(value) for key, value in build().items()}
    assert sum(summary["proposal_counts_by_primary_archetype"].values()) == len(proposals)
    assert sum(summary["proposal_counts_by_confidence"].values()) == len(proposals)
    print(
        "PASS bulk contract generation program: "
        f"{len(archetypes)} structural archetypes; {len(constitutions)} family constitutions; "
        f"{len(proposals)} complete non-authoritative proposals; {len(clusters)} owner clusters; "
        f"{len(collisions)} cross-owner collision signals; "
        f"{len(packages)} governed work packages in {len(waves)} dependency waves"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
