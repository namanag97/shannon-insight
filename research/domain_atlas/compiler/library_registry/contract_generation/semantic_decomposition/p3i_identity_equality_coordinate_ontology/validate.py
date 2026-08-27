#!/usr/bin/env python3
"""Fail-closed validation for the subject/relation-positioned P3I rebase."""
from __future__ import annotations

import hashlib
import json

from build_identity_equality_coordinate_ontology import HERE, build, outputs


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

    assert ontology["axis"] == "identity_and_equality"
    assert len(ontology["identity_coordinate"]["required_fields"]) == 16
    assert len(ontology["non_collapse_laws"]) >= 20
    archetype_ids = {row["archetype_id"] for row in archetypes}
    assert len(archetypes) == len(archetype_ids) == 24
    assert len(kernels) == len({row["kernel_id"] for row in kernels}) == 42
    assert all(row["identity_bearer_archetype_ref"] in archetype_ids for row in kernels)
    assert all(row["applicability"] == "UNRESOLVED_PER_SUBJECT_RELATION_AND_USE_SITE" for row in kernels)
    assert len(extensions) == 7
    assert len(members) == len({row["library_ref"] for row in members}) == 223
    assert all(row["required_subject_and_identifier_inventory"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_identity_and_equality_relation_profiles"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["required_lifecycle_merge_split_and_alias_contracts"] == "NOT_YET_SUPPLIED" for row in members)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in members)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in clusters)
    assert all(row["owner_decision"] == "UNRESOLVED" for row in extensions)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in members + clusters + extensions)
    cluster_members = [library_ref for row in clusters for library_ref in row["library_refs"]]
    assert len(cluster_members) == len(set(cluster_members)) == len(members)
    assert set(cluster_members) == {row["library_ref"] for row in members}

    assert summary["routes_with_lexical_discovery_projection"] + summary["routes_with_no_member_identity_relation_evidence"] == 223
    assert summary["subject_identity_inventories_supplied"] == 0
    assert summary["identity_equality_relation_profiles_supplied"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["owner_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        f"PASS P3I identity/equality coordinate ontology: 223 exact members partition losslessly "
        f"into {summary['research_clusters']} subject/relation-aware clusters; all applicability remains open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
