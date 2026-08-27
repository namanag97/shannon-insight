#!/usr/bin/env python3
"""Validate lossless non-retained product-boundary migration projections."""
import hashlib
import json

from build_boundary_migration_projection import HERE, build, outputs


def main() -> int:
    for name, expected in outputs().items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == expected, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    summary = built["summary"]
    assert summary["global_product_candidates"] == summary["retained_product_candidates"] + summary["nonretained_product_candidates"]
    assert summary["retained_product_candidates"] > 0
    assert len(built["boundaries"]) == len({row["candidate_ref"] for row in built["boundaries"]}) == 13
    assert summary["merge_candidates"] == 9 and summary["deferred_candidates"] == 4
    assert summary["legacy_crosswalks"] == 15 and len(built["reconciliations"]) == 2
    assert len(built["capabilities"]) == len({row["source_import_ref"] for row in built["capabilities"]}) == 39
    assert len(built["solutions"]) == 1 and len(built["work"]) == 13
    assert all(row["crosswalk_count"] >= 1 and row["target_boundary_count"] >= 1 for row in built["boundaries"])
    assert all(row["responsibility_assignment"] == "UNRESOLVED" and not row["compatibility_alias_allowed"] for row in built["capabilities"])
    assert all(row["compiler_action"].startswith("REFUSE_") for row in built["capabilities"] + built["solutions"])
    assert summary["responsibility_assignments_ratified"] == summary["compiler_migrations_permitted"] == summary["compatibility_aliases_allowed"] == 0
    assert not summary["completion_claim"]
    print(
        "PASS product boundary migration projection: all 13 merge/defer candidates factor into exact responsibility work; 39 capability imports and one solution-pack edge remain fail-closed without aliases"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
