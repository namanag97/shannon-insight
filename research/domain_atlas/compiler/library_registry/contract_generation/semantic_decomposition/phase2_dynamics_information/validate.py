#!/usr/bin/env python3
"""Validate Phase-2 dynamics/information constitution candidate."""

from __future__ import annotations
import hashlib, json
from build_phase2 import HERE, build, outputs


def main() -> int:
    for name, text in outputs().items():
        path = HERE / name
        assert path.is_file() and path.read_text(encoding="utf-8") == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes(); assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"]
    built = build(); constitution = built["constitution"]; modules = constitution["modules"]
    assert [row["axis"] for row in modules] == ["state_and_change", "time", "order_and_topology", "partiality_and_uncertainty"]
    assert all(len(row["non_collapse_laws"]) >= 8 for row in modules)
    assert len(modules[0]["coordinates"]) == 12
    assert len(modules[1]["role_coordinates"]) == 11
    assert len(modules[2]["order_coordinates"]) == 7 and len(modules[2]["topology_coordinates"]) == 8
    assert len(modules[3]["information_states"]) == 13 and len(modules[3]["uncertainty_coordinates"]) == 9
    source_ids = {row["source_id"] for row in built["sources"]}; module_ids = {row["module_id"] for row in modules}
    assert len(source_ids) == len(built["sources"]) == len(built["claims"]) == 7
    assert all(claim["source_ref"] in source_ids and set(claim["supports_module_refs"]) <= module_ids and claim["authority_limit"] for claim in built["claims"])
    assert len(built["projection"]["required_ir_roles"]) >= 18 and len(built["projection"]["refusal_roles"]) >= 16
    assert built["summary"]["completion_claim"] is False and built["summary"]["canonical_exact_gaps_closed"] == 0
    print("PASS Phase-2 dynamics/information constitution candidate: 4 modules, 7 primary claims, explicit lifecycle/time/order/partiality coordinates and compiler refusals; owner ratification remains open")
    return 0


if __name__ == "__main__": raise SystemExit(main())
