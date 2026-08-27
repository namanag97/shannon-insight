#!/usr/bin/env python3
"""Validate semantic-axis coverage without promoting discovery candidates to truth."""

from __future__ import annotations

import hashlib
import json

from build_semantic_decomposition import AXES, HERE, build, outputs


def main() -> int:
    for name, text in outputs().items():
        path = HERE / name
        assert path.is_file() and path.read_text(encoding="utf-8") == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name
    built = build()
    signatures = built["signatures"]
    realizations = built["realizations"]
    claims = built["evidence_claims"]
    packages = built["review_packages"]
    queue = built["research_queue"]
    lanes = built["axis_lanes"]
    phases = built["execution_phases"]
    axis_names = {axis["axis"] for axis in AXES}
    assert len(AXES) == len(axis_names) == 16
    assert sum(len(axis["facets"]) for axis in AXES) >= 90
    assert len(realizations) == sum(len(axis["facets"]) for axis in AXES) == 109
    assert len({row["realization_id"] for row in realizations}) == 109
    realization_refs = {row["realization_id"] for row in realizations}
    assert len(signatures) == 674 and len({row["library_ref"] for row in signatures}) == 674
    assert all({row["axis"] for row in signature["axis_selections"]} == axis_names for signature in signatures)
    assert all(len(signature["axis_selections"]) == 16 for signature in signatures)
    for signature in signatures:
        effect = next(row for row in signature["axis_selections"] if row["axis"] == "effect_boundary")
        assert effect["status"] == "EXPLICIT_CANDIDATE_SET_UNRATIFIED"
        assert len(effect["candidate_facets"]) == 1
        assert effect["candidate_facets"][0]["confidence"] == "EXPLICIT_SOURCE_FIELD"
        assert signature["status"] == "DISCOVERY_SIGNATURE_NOT_AUTHORITY_DOES_NOT_CLOSE_GAP"
        assert all(candidate["realization_ref"] in realization_refs for selection in signature["axis_selections"] for candidate in selection["candidate_facets"])
    assert all(row["anti_explosion_law"] for row in realizations)
    assert all(row["status"] == "CANDIDATE_OWNERSHIP_RESOLUTION_NOT_EXACT_CONTRACT" for row in realizations)
    assert len(claims) == 6
    for claim in claims:
        source_path = HERE.parents[5] / claim["source_registry_path"]
        assert source_path.is_file(), source_path
        source_rows = [json.loads(line) for line in source_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        source_ids = {row.get("source_id", row.get("id")) for row in source_rows}
        assert claim["source_ref"] in source_ids, claim["source_ref"]
        assert claim["supports_realization_refs"] and set(claim["supports_realization_refs"]) <= realization_refs
        assert claim["authority_limit"]
    refs = [member["signature_ref"] + "\0" + package["axis"] for package in packages for member in package["member_signatures"]]
    expected = [signature["signature_id"] + "\0" + axis for signature in signatures for axis in axis_names]
    assert sorted(refs) == sorted(expected)
    assert len(queue) == len(packages) == 368
    assert {row["work_package_ref"] for row in queue} == {row["work_package_id"] for row in packages}
    assert [row["rank"] for row in queue] == list(range(1, 369))
    assert [row["priority_score"] for row in queue] == sorted((row["priority_score"] for row in queue), reverse=True)
    assert all(row["unresolved_library_count"] + row["candidate_ratification_count"] == row["library_count"] for row in queue)
    assert len(lanes) == 16 and {row["axis"] for row in lanes} == axis_names
    assert all(row["family_count"] == 23 for row in lanes)
    assert sorted(ref for lane in lanes for ref in lane["family_work_package_refs_in_priority_order"]) == sorted(row["work_package_id"] for row in packages)
    assert len(phases) == 5
    assert len({ref for phase in phases for ref in phase["axis_lane_refs"]}) == 16
    assert phases[0]["depends_on_phase_refs"] == []
    assert all(phase["depends_on_phase_refs"] == [phases[index - 1]["phase_id"]] for index, phase in enumerate(phases) if index > 0)
    assert built["summary"]["completion_claim"] is False
    print(f"PASS semantic-axis decomposition: 674 libraries have complete 16-axis discovery signatures; {len(realizations)} facets have realization dispositions; {len(packages)} ranked family-axis research packages preserve unresolved owner decisions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
