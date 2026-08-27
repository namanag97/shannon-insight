#!/usr/bin/env python3
"""Validate complete, conservative Wave-0 data-shape boundary adjudication."""

from __future__ import annotations

import hashlib
import json

from build_wave0 import HERE, build, outputs


def main() -> int:
    for name, text in outputs().items():
        path = HERE / name
        assert path.is_file() and path.read_text(encoding="utf-8") == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name
    constitution, decisions, bindings, claims, packages, summary = build()
    assert constitution["status"] == "EVIDENCE_ADJUDICATED_CANDIDATE_PENDING_CANONICAL_RATIFICATION"
    assert len(constitution["layers"]) == 5 and len(constitution["non_collapse_laws"]) >= 8
    assert len(decisions) == 33 and len({row["source_library_ref"] for row in decisions}) == 33
    assert all(row["no_compatibility_alias"] is True for row in decisions)
    assert all(row["canonical_mutation_performed"] is False and row["exact_api_gap_closed"] is False for row in decisions)
    assert sum(row["library_disposition"] == "SPLIT_AND_RENAME_WITHOUT_COMPATIBILITY_ALIAS" for row in decisions) == 32
    assert sum(row["library_disposition"] == "REPLACE_WITH_PROFILE_CONFORMANCE_CONTRACT" for row in decisions) == 1
    gltf = next(row for row in decisions if row["decision_id"] == "decision.wave0.gltf-profile")
    assert gltf["shape_disposition"] == "REPRESENTATION_BINDING_ONLY_NOT_A_NEW_SHAPE"
    assert gltf["broader_shape_ref"] == "candidate.shape.scene_graph"
    assert len(bindings) == 23 and len({row["binding_id"] for row in bindings}) == 23
    assert all(row["qualification_status"] == "NO_IMPLEMENTATION_OR_PROVIDER_QUALIFIED" for row in bindings)
    assert len(claims) == 4 and all(claim["source_authority_limit"] for claim in claims)
    assert len(packages) == 5
    assert sorted(ref for package in packages for ref in package["decision_refs"]) == sorted(row["decision_id"] for row in decisions)
    assert sum(package["candidate_count"] for package in packages) == 33
    assert all(len(package["shared_questions"]) == 5 and len(package["allowed_dispositions"]) == 6 for package in packages)
    assert summary["canonical_mutations"] == summary["canonical_exact_gaps_closed"] == 0
    assert summary["completion_claim"] is False
    print("PASS Wave 0 data-shape boundary adjudication: 33/33 source boundaries grouped into 5 ratification packages; 32 split/rename, one glTF profile-only replacement, 23 independent representation bindings; canonical ratification and exact contracts remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
