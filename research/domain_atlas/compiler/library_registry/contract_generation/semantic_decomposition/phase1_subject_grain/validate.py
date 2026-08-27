#!/usr/bin/env python3
"""Validate the conservative Phase-1 semantic constitution candidate."""

from __future__ import annotations

import hashlib
import json

from build_phase1 import HERE, ROOT, build, outputs


def main() -> int:
    for name, text in outputs().items():
        path = HERE / name
        assert path.is_file() and path.read_text(encoding="utf-8") == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name
    built = build()
    constitution = built["constitution"]
    modules = constitution["modules"]
    assert [row["axis"] for row in modules] == ["semantic_object", "identity_and_equality", "grain_and_cardinality"]
    assert len(modules[1]["equality_stack"]) == 9
    assert len(modules[2]["grain_coordinates"]) == 9
    assert len(modules[2]["cardinality_coordinates"]) == 8
    assert all(len(row["non_collapse_laws"]) >= 8 for row in modules)
    assert constitution["prohibited_new_facades"] == ["universal_object", "universal_id", "universal_record", "universal_collection", "universal_equality", "universal_grain"]
    module_refs = {row["module_id"] for row in modules}
    assert len(built["evidence_claims"]) == 6
    for claim in built["evidence_claims"]:
        source_path = ROOT / claim["source_registry_path"]
        assert source_path.is_file(), source_path
        source_rows = [json.loads(line) for line in source_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        source_ids = {row.get("source_id", row.get("id")) for row in source_rows}
        assert claim["source_ref"] in source_ids
        assert set(claim["supports_module_refs"]) <= module_refs
        assert claim["authority_limit"]
    projection = built["compiler_projection"]
    assert len(projection["required_ir_roles"]) >= 14
    assert len(projection["refusal_roles"]) >= 12
    assert built["summary"]["completion_claim"] is False
    assert built["summary"]["canonical_exact_gaps_closed"] == 0
    print("PASS Phase-1 subject/identity/grain constitution candidate: 3 modules, 6 bounded primary claims, 9 grain coordinates and explicit compiler refusals; owner ratification remains open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
