#!/usr/bin/env python3
"""Validate representation coordinate ontology and exact member routing."""
import hashlib
import json

from build_representation_coordinate_ontology import HERE, build, outputs


def main() -> int:
    for name, payload in outputs().items():
        assert (HERE / name).is_file(), f"missing {name}"
        assert (HERE / name).read_text() == payload, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
    built = build()
    summary = built["summary"]
    assert len(built["sources"]) == len({row["source_id"] for row in built["sources"]}) == 14
    assert len(built["archetypes"]) == len({row["archetype_id"] for row in built["archetypes"]}) == 48
    assert len(built["kernels"]) == len({row["kernel_id"] for row in built["kernels"]}) == 60
    assert len(built["dockets"]) == len(built["extensions"]) == summary["structural_family_dockets"]
    assert len(built["members"]) == len({row["library_ref"] for row in built["members"]}) == summary["target_member_routes"]
    assert sum(row["library_count"] for row in built["clusters"]) == len(built["members"])
    assert summary["routes_with_lexical_representation_projection"] + summary["routes_with_no_representation_projection"] == len(built["members"])
    assert summary["family_source_evidence_bindings_supplied"] == 0
    assert summary["member_applicability_decisions"] == 0
    assert summary["owner_decisions"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        f"PASS representation coordinate ontology: {len(built['members'])} exact members partition losslessly into "
        f"{summary['research_clusters']} representation-layer clusters; "
        "all evidence bindings and decisions remain open"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
