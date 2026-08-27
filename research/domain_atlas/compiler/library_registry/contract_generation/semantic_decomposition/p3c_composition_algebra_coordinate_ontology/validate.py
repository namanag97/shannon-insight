#!/usr/bin/env python3
"""Fail-closed validation for the operator-positioned P3C rebase."""
from __future__ import annotations

import hashlib
import json

from build_composition_algebra_coordinate_ontology import HERE, build, outputs


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

    assert ontology["axis"] == "composition_algebra"
    assert len(ontology["operator_coordinate"]["required_fields"]) == 15
    assert len(ontology["non_collapse_laws"]) >= 16
    archetype_ids = {row["archetype_id"] for row in archetypes}
    assert len(archetypes) == len(archetype_ids) == 28
    assert len(kernels) == len({row["kernel_id"] for row in kernels}) == 41
    assert all(row["operator_archetype_ref"] in archetype_ids for row in kernels)
    assert all(row["applicability"] == "UNRESOLVED_PER_OPERATOR_AND_USE_SITE" for row in kernels)
    assert len(extensions) == 22
    assert len(members) == len({row["library_ref"] for row in members}) == 619
    assert all(row["required_operator_and_use_site_inventory"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_operand_and_result_coordinate_profiles"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_law_and_precondition_profiles"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in members)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in clusters)
    assert all(row["owner_decision"] == "UNRESOLVED" for row in extensions)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in members + clusters + extensions)
    cluster_members = [library_ref for row in clusters for library_ref in row["library_refs"]]
    assert len(cluster_members) == len(set(cluster_members)) == len(members)
    assert set(cluster_members) == {row["library_ref"] for row in members}

    assert summary["target_member_routes"] == 619
    assert summary["routes_with_lexical_discovery_projection"] + summary["routes_with_no_member_operator_evidence"] == 619
    assert summary["operator_use_site_inventories_supplied"] == 0
    assert summary["operator_coordinate_profiles_supplied"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["owner_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        f"PASS P3C composition/algebra coordinate ontology: 619 exact members partition losslessly "
        f"into {summary['research_clusters']} operator-aware clusters; all applicability remains open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
