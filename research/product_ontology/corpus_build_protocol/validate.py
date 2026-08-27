#!/usr/bin/env python3
"""Fail-closed validator for the corpus build protocol registry."""
from __future__ import annotations

import json
from pathlib import Path

from build_registry import ROOT, outputs
from source_model import AUTHORITY_CLASSES, PACKAGE_KINDS, REBUILD_POLICIES, WRITE_POLICIES
from validate_m01_io_campaign import main as validate_m01_io_campaign
from validate_m02_io_campaign import main as validate_m02_io_campaign

HERE = Path(__file__).resolve().parent


def load_jsonl(name: str) -> list[dict]:
    return [json.loads(line) for line in (HERE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        path = HERE / name
        assert path.is_file(), f"missing generated protocol artifact {name}"
        assert path.read_text(encoding="utf-8") == text, f"stale generated protocol artifact {name}"

    contracts = load_jsonl("package-contracts.jsonl")
    observed = load_jsonl("observed-package-candidates.jsonl")
    gaps = load_jsonl("migration-gaps.jsonl")
    dockets = load_jsonl("contract-candidate-dockets.jsonl")
    batches = load_jsonl("migration-batches.jsonl")
    by_id = {row["package_id"]: row for row in contracts}
    assert len(by_id) == len(contracts)
    assert sorted(row["topological_order"] for row in contracts) == list(range(1, len(contracts) + 1))

    for row in contracts:
        assert row["package_kind"] in PACKAGE_KINDS
        assert row["authority_class"] in AUTHORITY_CLASSES
        assert row["rebuild_policy"] in REBUILD_POLICIES
        assert row["write_policy"] in WRITE_POLICIES
        assert (ROOT / row["root"]).is_dir(), row["root"]
        assert row["negative_claims"] and row["completion_claim"] is False
        assert row["input_selectors"]
        assert len(row["dependency_refs"]) == len(set(row["dependency_refs"]))
        for dep in row["dependency_refs"]:
            assert dep in by_id
            assert by_id[dep]["topological_order"] < row["topological_order"]
        for command in row["build_commands"] + row["validate_commands"]:
            assert command[0] == "python3", f"unsupported executable in {row['package_id']}"
            assert len(command) == 2, f"arguments require an explicit future command contract: {row['package_id']}"
            assert (ROOT / command[1]).is_file(), command[1]
        if row["package_kind"] == "aggregate_validator":
            assert not row["build_commands"] and row["write_policy"] == "read_only"
        if row["package_kind"] == "fixed_point_projection":
            assert row["rebuild_policy"] == "repository_fixed_point" and row["fixed_point_group"]
        if row["package_kind"] == "historical_snapshot":
            assert not row["build_commands"] and row["rebuild_policy"] == "immutable_never_rebuild"
        if row["execution_enabled"] and row["package_kind"] != "aggregate_validator":
            assert not row["uncontracted_input_surfaces"], f"unsafe execution enabled for {row['package_id']}"

    observed_roots = {row["root"] for row in observed}
    assert len(observed_roots) == len(observed)
    assert all(row["contract_state"] in {"EXPLICIT_CONTRACT", "LEGACY_DISCOVERED_UNCONTRACTED"} for row in observed)
    uncontracted = {row["candidate_id"] for row in observed if row["declared_contract_ref"] is None}
    gap_candidates = {row["package_candidate_ref"] for row in gaps if row["gap_kind"] == "EXPLICIT_PACKAGE_CONTRACT_MISSING"}
    assert uncontracted == gap_candidates
    assert uncontracted == {row["package_candidate_ref"] for row in dockets}
    assert len({row["docket_id"] for row in dockets}) == len(dockets)
    required_axes = {"input_ownership", "output_ownership", "dependency_edges", "package_kind", "authority_class", "determinism", "write_boundary", "fixed_point_membership", "execution_risk"}
    assert all(set(row["decision_axes"]) == required_axes for row in dockets)
    batch_ids = {row["batch_id"] for row in batches}
    assert len(batch_ids) == len(batches) == 9
    assert all(set(row["depends_on"]) <= batch_ids for row in batches)
    docket_refs = {row["package_candidate_ref"] for row in dockets}
    batched_refs = [ref for row in batches for ref in row["package_candidate_refs"]]
    assert len(batched_refs) == len(set(batched_refs)) and set(batched_refs) == docket_refs
    assert all(row["automatic_execution_enabled"] is False and row["completion_claim"] is False for row in batches)
    assert all(row["completion_claim"] is False for row in gaps)

    summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    assert summary["observed_python_package_candidates"] == len(observed)
    assert summary["explicit_package_contracts"] == len(contracts)
    assert summary["uncontracted_observed_packages"] == len(uncontracted)
    assert summary["migration_gap_records"] == len(gaps)
    assert summary["contract_candidate_dockets"] == len(dockets)
    assert summary["migration_batches"] == len(batches)
    assert summary["completion_claim"] is False and summary["world_completion_claim"] is False
    assert validate_m01_io_campaign() == 0
    assert validate_m02_io_campaign() == 0
    print(
        "PASS corpus build protocol: "
        f"{len(contracts)} governed packages form an acyclic executable plan; "
        f"{len(observed)} Python package candidates inventoried; "
        f"{len(uncontracted)} legacy candidates remain explicitly non-executable"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
