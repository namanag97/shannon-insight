#!/usr/bin/env python3
"""Validate retained exact-scope CP-SAT evidence without qualifying the offer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from run_execution import HERE, evaluate


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise AssertionError(f"{path}:{line_number}: blank lines are forbidden")
        row = json.loads(line)
        assert isinstance(row, dict), f"{path}:{line_number}: record must be an object"
        rows.append(row)
    return rows


def validate_protocol(protocol: dict[str, Any]) -> None:
    assert protocol["completion_claim"] is False
    assert protocol["status"] == "candidate_executable_not_qualified"
    assert protocol["scope"]["model_class_refs"] == ["class.mca.cp_sat_integer"]
    assert protocol["scope"]["numeric_policy"]["integer_only"] is True
    assert protocol["scope"]["parameter_policy"] == {
        "num_search_workers": 1,
        "random_seed": 1729,
    }
    assert len(protocol["fixtures"]) == 10
    assert len(protocol["profiles"]) == 5
    fixture_ids = [row["fixture_id"] for row in protocol["fixtures"]]
    profile_ids = [row["profile_id"] for row in protocol["profiles"]]
    source_ids = [row["source_id"] for row in protocol["sources"]]
    assert len(fixture_ids) == len(set(fixture_ids))
    assert len(profile_ids) == len(set(profile_ids))
    assert len(source_ids) == len(set(source_ids))
    assert all(set(row["profile_refs"]) <= set(profile_ids) for row in protocol["fixtures"])
    assert {row["expected"]["status"] for row in protocol["fixtures"]} >= {
        "optimal",
        "infeasible",
        "invalid_input",
        "model_invalid",
        "unknown",
    }
    assert all(
        row["url"].startswith(("https://github.com/google/or-tools/", "https://developers.google.com/optimization/"))
        for row in protocol["sources"]
    )
    provider = protocol["provider"]
    assert provider["version"] == "9.15.6755"
    assert "ortools==9.15.6755" in provider["declared_dependency_lock"]
    assert set(provider["source_refs"]) == set(source_ids)
    assert any("LLM or agent proposal" in law for law in protocol["non_collapse_laws"])

    compiler_dir = HERE.parents[2]
    classes = load_jsonl(compiler_dir / "model_class_adjudication" / "model-classes.jsonl")
    class_by_id = {row["id"]: row for row in classes}
    assert "class.mca.cp_sat_integer" in class_by_id
    requirement_rows = load_jsonl(compiler_dir / "model_class_adjudication" / "provider-requirements.jsonl")
    requirement = next(row for row in requirement_rows if row["class_ref"] == "class.mca.cp_sat_integer")
    assert requirement["binding_status"] == "unbound_no_qualified_offer_asserted"


def validate_run(run_dir: Path, protocol: dict[str, Any], receipt_schema: dict[str, Any]) -> dict[str, str]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    providers = load_jsonl(run_dir / "provider-results.jsonl")
    oracles = load_jsonl(run_dir / "oracle-results.jsonl")
    receipts = load_jsonl(run_dir / "qualification-receipts.jsonl")
    binding = json.loads((run_dir / "binding-assessment.json").read_text(encoding="utf-8"))

    assert manifest["completion_claim"] is False
    assert manifest["status"] == "executed_evidence_not_qualified"
    assert manifest["qualified_offers"] == 0
    assert binding["binding_eligible"] is False
    assert binding["qualification_state"] == "executed_not_independently_appraised"
    assert binding["exact_offer_id"] == protocol["provider"]["exact_offer_id"]
    assert manifest["profile_verdicts"] == binding["profile_verdicts"]

    expected_files = {
        "binding-assessment.json",
        "oracle-results.jsonl",
        "provider-results.jsonl",
        "qualification-receipts.jsonl",
    }
    manifest_files = {row["path"]: row for row in manifest["files"]}
    assert set(manifest_files) == expected_files
    for name, identity in manifest_files.items():
        path = run_dir / name
        assert path.stat().st_size == identity["bytes"], f"byte-count mismatch for {name}"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == identity["sha256"], f"digest mismatch for {name}"
    assert manifest["protocol_digest"] == "sha256:" + hashlib.sha256((HERE / "protocol.json").read_bytes()).hexdigest()

    assert len(providers) == 1
    provider = providers[0]
    spec = protocol["provider"]
    assert provider["provider_id"] == spec["provider_id"]
    assert provider["exact_offer_id"] == spec["exact_offer_id"]
    assert provider["provider_version"] == spec["version"]
    assert provider["dependency_lock"] == spec["declared_dependency_lock"]
    assert provider["artifact_digest"].startswith("sha256:")
    assert provider["adapter_digest"].startswith("sha256:")
    assert provider["dependency_lock_digest"].startswith("sha256:")
    assert provider["environment_digest"].startswith("sha256:")
    assert provider["artifact_member_count"] > 0
    assert provider["artifact_native_members"], "native provider artifact identity absent"
    assert provider["target_occurrence"] == binding["target_occurrence"]
    fixture_ids = {row["fixture_id"] for row in protocol["fixtures"]}
    assert {row["fixture_id"] for row in provider["results"]} == fixture_ids

    recomputed_oracles, recomputed_profiles = evaluate(protocol, provider)
    oracle_projection = lambda rows: sorted(
        (
            row["fixture_id"],
            row["observed_canonical_status"],
            tuple(row["oracle_failures"]),
            row["oracle_verdict"],
            tuple(row["profile_refs"]),
        )
        for row in rows
    )
    assert oracle_projection(oracles) == oracle_projection(recomputed_oracles), "oracle projection drift"
    assert recomputed_profiles == binding["profile_verdicts"] == manifest["profile_verdicts"]
    assert len(oracles) == len(protocol["fixtures"])

    # An observed profile failure is valid retained evidence. The validator checks that the
    # failure was faithfully projected into the oracle and receipts; it does not rewrite a failed
    # execution into a structurally invalid run. Strong fixture assertions apply only after the
    # corresponding profile has passed.
    results = {row["fixture_id"]: row["result"] for row in provider["results"]}
    if recomputed_profiles["profile.cpsat.core"] == "pass":
        for fixture_id in {"fixture.cpsat.invalid_fractional_coefficient", "fixture.cpsat.invalid_domain"}:
            assert results[fixture_id]["canonical_status"] == "invalid_input"
            assert results[fixture_id]["provider_validator_invoked"] is False
            assert results[fixture_id]["provider_solver_invoked"] is False
        invalid = results["fixture.cpsat.provider_overflow_model_invalid"]
        assert invalid["canonical_status"] == "model_invalid"
        assert invalid["provider_validator_invoked"] is True
        assert invalid["provider_solver_invoked"] is False
    if recomputed_profiles["profile.cpsat.limit_no_strengthening"] == "pass":
        assert results["fixture.cpsat.zero_deterministic_budget"]["canonical_status"] == "unknown"
    if recomputed_profiles["profile.cpsat.enumeration"] == "pass":
        enumeration = results["fixture.cpsat.complete_enumeration"]
        assert enumeration["canonical_status"] == "optimal"
        assert enumeration["solution_count"] == 2

    required = set(receipt_schema["required"])
    allowed = set(receipt_schema["properties"])
    profile_ids = {row["profile_id"] for row in protocol["profiles"]}
    assert len(receipts) == len(profile_ids)
    assert len({row["receipt_id"] for row in receipts}) == len(receipts)
    assert {row["oracle"]["id"] for row in receipts} == profile_ids
    for row in receipts:
        assert required <= set(row), f"{row['receipt_id']}: missing receipt fields"
        assert set(row) <= allowed, f"{row['receipt_id']}: unexpected receipt fields"
        assert row["subject"] == spec["exact_offer_id"]
        assert row["target_occurrence"] == provider["target_occurrence"]
        assert row["artifact_digest"] == provider["artifact_digest"]
        assert row["dependency_lock_digest"] == provider["dependency_lock_digest"]
        assert row["independent_appraiser"] is None
        assert row["waiver_ref"] is None
        assert row["verdict"] == recomputed_profiles[row["oracle"]["id"]]
        assert any("executed-test evidence only" in item for item in row["limitations"])

    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    if jsonschema is not None:
        validator = jsonschema.Draft202012Validator(receipt_schema, format_checker=jsonschema.FormatChecker())
        for row in receipts:
            errors = sorted(validator.iter_errors(row), key=lambda error: list(error.path))
            assert not errors, f"{row['receipt_id']}: JSON Schema errors: {[error.message for error in errors]}"

    return recomputed_profiles


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path, nargs="*")
    args = parser.parse_args()
    protocol = json.loads((HERE / "protocol.json").read_text(encoding="utf-8"))
    validate_protocol(protocol)
    receipt_schema = json.loads(
        (HERE.parents[1] / "qualification-receipt-contract.schema.json").read_text(encoding="utf-8")
    )
    run_dirs = [path.resolve() for path in args.run_dir]
    if not run_dirs:
        runs_root = HERE / "runs"
        run_dirs = sorted(path.resolve() for path in runs_root.iterdir() if path.is_dir()) if runs_root.exists() else []
    assert run_dirs, "no retained CP-SAT execution run was supplied or discovered"
    summaries = []
    for run_dir in run_dirs:
        summaries.append((run_dir.name, validate_run(run_dir, protocol, receipt_schema)))
    print(
        "PASS exact-scope CP-SAT evidence: "
        + "; ".join(f"{run_id} profiles={verdicts}" for run_id, verdicts in summaries)
        + "; 0 qualified offers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
