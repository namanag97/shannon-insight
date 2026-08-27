#!/usr/bin/env python3
"""Fail-closed validation for the subject-positioned P3S state/change rebase."""
from __future__ import annotations

import hashlib
import json

from build_state_change_coordinate_ontology import HERE, build, outputs


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
    clusters = built["clusters"]
    members = built["members"]
    extensions = built["extensions"]
    summary = built["summary"]

    assert ontology["discovery_projection_compatibility"]["status"] == "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY"
    assert len(archetypes) == len({row["archetype_id"] for row in archetypes}) == 12
    assert len(kernels) == len({row["kernel_id"] for row in kernels}) == 31
    assert all(row["applicability"] == "UNRESOLVED_PER_TRANSITION" for row in kernels)
    assert len(extensions) == summary["family_extension_candidates"]
    assert len(members) == len({row["library_ref"] for row in members}) == summary["target_member_routes"]
    assert all(row["required_state_subject_profiles"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_lifecycle_editions"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_transition_inventory"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in members)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in clusters)
    assert all(row["owner_decision"] == "UNRESOLVED" for row in extensions)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in members + clusters + extensions)
    cluster_members = [library_ref for row in clusters for library_ref in row["library_refs"]]
    assert len(cluster_members) == len(set(cluster_members)) == len(members)
    assert set(cluster_members) == {row["library_ref"] for row in members}

    assert summary["routes_with_lexical_discovery_projection"] + summary["routes_with_no_member_state_subject_evidence"] == len(members)
    assert summary["state_subject_profiles_supplied"] == 0
    assert summary["transition_inventories_supplied"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["owner_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        f"PASS P3S state/change coordinate ontology: {len(members)} exact members partition losslessly into "
        f"{len(clusters)} bearer-aware research clusters; all lifecycle decisions remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
