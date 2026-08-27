#!/usr/bin/env python3
"""Fail-closed validation for the bearer-positioned P3U rebase."""
from __future__ import annotations

import hashlib
import json

from build_partiality_uncertainty_coordinate_ontology import HERE, build, outputs


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

    assert ontology["axis"] == "partiality_and_uncertainty"
    assert len(ontology["uncertainty_coordinate"]["required_fields"]) == 18
    assert len(ontology["non_collapse_laws"]) >= 21
    archetype_ids = {row["archetype_id"] for row in archetypes}
    assert len(archetypes) == len(archetype_ids) == 20
    assert len(kernels) == len({row["kernel_id"] for row in kernels}) == 42
    assert all(row["bearer_archetype_ref"] in archetype_ids for row in kernels)
    assert all(row["applicability"] == "UNRESOLVED_PER_BEARER_POSITION_AND_USE_SITE" for row in kernels)
    assert len(extensions) == 5
    assert len(members) == len({row["library_ref"] for row in members}) == 73
    assert all(row["required_bearer_and_state_lattice_inventory"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_partiality_and_uncertainty_profiles"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_propagation_imputation_and_decision_contracts"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in members)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in clusters)
    assert all(row["owner_decision"] == "UNRESOLVED" for row in extensions)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in members + clusters + extensions)
    cluster_members = [library_ref for row in clusters for library_ref in row["library_refs"]]
    assert len(cluster_members) == len(set(cluster_members)) == len(members)
    assert set(cluster_members) == {row["library_ref"] for row in members}
    assert summary["routes_with_lexical_discovery_projection"] + summary["routes_with_no_member_partiality_uncertainty_evidence"] == 73
    assert summary["bearer_state_lattice_inventories_supplied"] == 0
    assert summary["partiality_uncertainty_profiles_supplied"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["owner_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        f"PASS P3U partiality/uncertainty coordinate ontology: 73 exact members partition losslessly "
        f"into {summary['research_clusters']} bearer-aware clusters; all applicability remains open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
