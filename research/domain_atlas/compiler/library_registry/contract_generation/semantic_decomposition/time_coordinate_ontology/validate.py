#!/usr/bin/env python3
"""Fail-closed validation for the bearer-positioned all-member time rebase."""
from __future__ import annotations

import hashlib
import json

from build_time_coordinate_ontology import HERE, build, outputs


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        assert (HERE / name).is_file(), f"missing {name}"
        assert (HERE / name).read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    ontology = built["ontology"]
    archetypes = built["archetypes"]
    kernels = built["kernels"]
    dockets = built["dockets"]
    clusters = built["clusters"]
    members = built["members"]
    extensions = built["extensions"]
    summary = built["summary"]

    assert ontology["axis"] == "time"
    assert len(ontology["time_coordinate"]["required_fields"]) == 22
    assert len(ontology["non_collapse_laws"]) >= 22
    archetype_ids = {row["archetype_id"] for row in archetypes}
    assert len(archetypes) == len(archetype_ids) == 25
    assert len(kernels) == len({row["kernel_id"] for row in kernels}) == 48
    assert all(row["temporal_bearer_archetype_ref"] in archetype_ids for row in kernels)
    assert all(row["applicability"] == "UNRESOLVED_PER_TEMPORAL_BEARER_AND_USE_SITE" for row in kernels)
    assert len(dockets) == len(extensions) == summary["structural_family_dockets"]
    assert len(members) == len({row["library_ref"] for row in members}) == summary["target_member_routes"]
    assert all(row["evidence_candidate_refs"] == [] for row in dockets)
    assert all(row["source_evidence_binding"] == "UNRESOLVED_PER_FAMILY_AND_USE_SITE" for row in dockets)
    assert all(row["required_temporal_bearer_and_time_role_inventory"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_time_coordinate_profiles"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_progress_finality_correction_and_replay_contracts"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["family_source_evidence_binding"] == row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in members)
    assert all(row["family_source_evidence_binding"] == row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in clusters)
    assert all(row["source_evidence_binding"] == row["owner_decision"] == "UNRESOLVED" for row in extensions)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in members + clusters + extensions)
    cluster_members = [library_ref for row in clusters for library_ref in row["library_refs"]]
    assert len(cluster_members) == len(set(cluster_members)) == len(members)
    assert set(cluster_members) == {row["library_ref"] for row in members}
    assert summary["routes_with_lexical_discovery_projection"] + summary["routes_with_no_member_temporal_bearer_evidence"] == len(members)
    assert summary["temporal_bearer_inventories_supplied"] == 0
    assert summary["time_coordinate_profiles_supplied"] == 0
    assert summary["family_source_evidence_bindings_supplied"] == 0
    assert summary["member_applicability_decisions"] == summary["owner_decisions"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        f"PASS time coordinate ontology: {len(members)} exact members partition losslessly into "
        f"{summary['research_clusters']} temporal clusters; all evidence bindings and decisions remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
