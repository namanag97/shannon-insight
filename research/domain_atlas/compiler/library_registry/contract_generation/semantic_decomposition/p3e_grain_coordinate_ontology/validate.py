#!/usr/bin/env python3
"""Fail-closed validation for the operation-positioned P3E grain rebase."""
from __future__ import annotations

import hashlib
import json

from build_grain_coordinate_ontology import HERE, P3E_DOCKETS, build, load_jsonl, outputs


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
    kernels = built["kernels"]
    clusters = built["clusters"]
    routes = built["member_routes"]
    extensions = built["extensions"]
    summary = built["summary"]

    dockets = load_jsonl(P3E_DOCKETS)
    expected_members = {
        library_ref for docket in dockets for library_ref in docket["library_refs"]
    }
    routed_members = {row["library_ref"] for row in routes}
    assert len(dockets) == len(extensions)
    assert len(routes) == len(routed_members) == len(expected_members) == summary["target_member_routes"]
    assert routed_members == expected_members
    assert sum(row["library_count"] for row in clusters) == len(routes)
    assert {row["research_cluster_ref"] for row in routes} == {
        row["cluster_id"] for row in clusters
    }

    assert ontology["discovery_projection_compatibility"]["status"] == "LOSSY_LEXICAL_DISCOVERY_PROJECTION_ONLY"
    assert len(kernels) == 24
    assert len({row["kernel_id"] for row in kernels}) == len(kernels)
    assert all(row["applicability"] == "UNRESOLVED_PER_OPERATION" for row in kernels)
    assert all(row["required_coordinate_profile"] == "OPERATION_POSITIONED_PROFILE_NOT_YET_SUPPLIED" for row in routes)
    assert all(row["required_transformation_composition"] == "NOT_YET_SUPPLIED" for row in routes)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in routes)
    assert all(row["member_applicability"] == row["owner_decision"] == "UNRESOLVED" for row in clusters)
    assert all(row["owner_decision"] == "UNRESOLVED" for row in extensions)
    assert all(row["canonical_gaps_closed"] == 0 and not row["completion_claim"] for row in routes + clusters + extensions)

    assert summary["routes_with_lexical_discovery_projection"] + summary["routes_with_no_member_operation_evidence"] == len(routes)
    assert summary["operation_positioned_profiles_supplied"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["owner_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        "PASS P3E grain coordinate ontology: flat facets remain discovery-only; "
        f"{len(routes)} exact member routes partition into {len(clusters)} lossless research clusters"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
