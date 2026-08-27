#!/usr/bin/env python3
"""Validate one retained exact-scope LP execution without qualifying its offers."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from run_execution import HERE, evaluate_provider


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise AssertionError(f"{path}:{line_number}: blank lines are forbidden")
        row = json.loads(line)
        assert isinstance(row, dict), f"{path}:{line_number}: record must be an object"
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    protocol = json.loads((HERE / "protocol.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    providers = load_jsonl(run_dir / "provider-results.jsonl")
    oracles = load_jsonl(run_dir / "oracle-results.jsonl")
    receipts = load_jsonl(run_dir / "qualification-receipts.jsonl")
    differential = json.loads((run_dir / "differential-verdict.json").read_text(encoding="utf-8"))
    cohabitation = json.loads((run_dir / "cohabitation-negative-twin.json").read_text(encoding="utf-8"))
    binding = json.loads((run_dir / "binding-assessment.json").read_text(encoding="utf-8"))

    assert protocol["completion_claim"] is False
    assert protocol["status"] == "candidate_executable_not_qualified"
    assert manifest["completion_claim"] is False
    assert manifest["qualification_status"] == "withheld"
    assert manifest["counts"]["qualified_offers"] == 0
    assert binding["qualification_verdict"] == "withheld"
    assert binding["bindable_offer_refs"] == [] and binding["portable_offer_refs"] == []
    assert binding["independent_appraisal"] == "not_executed"
    assert binding["vertical_acceptance"] == "not_executed"

    expected_files = {
        "binding-assessment.json",
        "cohabitation-negative-twin.json",
        "differential-verdict.json",
        "oracle-results.jsonl",
        "provider-results.jsonl",
        "qualification-receipts.jsonl",
    }
    assert set(manifest["file_sha256"]) == expected_files
    for name, expected_digest in manifest["file_sha256"].items():
        observed = hashlib.sha256((run_dir / name).read_bytes()).hexdigest()
        assert observed == expected_digest, f"digest mismatch for {name}"
    assert manifest["protocol_digest"] == "sha256:" + hashlib.sha256((HERE / "protocol.json").read_bytes()).hexdigest()

    fixture_ids = {row["fixture_id"] for row in protocol["fixtures"]}
    provider_specs = {row["provider_id"]: row for row in protocol["providers"]}
    assert len(providers) == len(provider_specs) == 2
    assert Counter(row["provider_id"] for row in providers) == Counter(provider_specs.keys())
    for provider in providers:
        spec = provider_specs[provider["provider_id"]]
        assert provider["exact_offer_id"] == spec["exact_offer_id"]
        assert provider["provider_version"] == spec["version"]
        assert provider["dependency_lock"] == spec["declared_dependency_lock"]
        assert provider["artifact_digest"].startswith("sha256:")
        assert provider["dependency_lock_digest"].startswith("sha256:")
        assert provider["environment_digest"].startswith("sha256:")
        assert provider["artifact_member_count"] > 0
        assert provider["artifact_native_members"], f"{provider['provider_id']}: native artifact identity absent"
        assert {row["fixture_id"] for row in provider["results"]} == fixture_ids
        invalid = next(row for row in provider["results"] if row["fixture_id"] == "fixture.lp.invalid_non_finite")
        assert invalid["result"]["canonical_status"] == "invalid_input"
        assert invalid["result"]["provider_invoked"] is False
        recomputed, _ = evaluate_provider(protocol, provider)
        observed = sorted(
            (row["provider_id"], row["fixture_id"], row["safe_status_objective_oracle"], row["precise_terminal_oracle"])
            for row in oracles if row["provider_id"] == provider["provider_id"]
        )
        expected = sorted(
            (row["provider_id"], row["fixture_id"], row["safe_status_objective_oracle"], row["precise_terminal_oracle"])
            for row in recomputed
        )
        assert observed == expected, f"oracle projection drift for {provider['provider_id']}"

    by_adapter = {row["adapter"]: row for row in providers}
    glop = by_adapter["ortools_glop_mpsolver"]
    highs = by_adapter["highspy_highs"]
    glop_statuses = {row["fixture_id"]: row["result"]["canonical_status"] for row in glop["results"]}
    highs_statuses = {row["fixture_id"]: row["result"]["canonical_status"] for row in highs["results"]}
    assert glop_statuses["fixture.lp.infeasible"] == "infeasible_or_unbounded"
    assert glop_statuses["fixture.lp.unbounded"] == "infeasible_or_unbounded"
    assert highs_statuses["fixture.lp.infeasible"] == "infeasible"
    assert highs_statuses["fixture.lp.unbounded"] == "unbounded"

    assert differential["safe_scope_agreement"] is True
    assert differential["precise_scope_agreement"] is False
    assert differential["verdict"] == "safe_scope_executed_agreement_precise_scope_not_substitutable"
    assert {row["fixture_id"] for row in differential["status_differences"]} == {
        "fixture.lp.infeasible", "fixture.lp.unbounded"
    }
    assert all(row["within_tolerance"] for row in differential["objective_agreements"])

    assert cohabitation["record_kind"] == "runtime_cohabitation_negative_twin"
    assert cohabitation["verdict"] == "observed_native_abi_collision_process_isolation_required"
    assert cohabitation["process_isolation_requirement"] is True
    assert cohabitation["returncode"] != 0
    assert "libhighs" in cohabitation["stderr"].lower()
    assert binding["cohabitation_verdict"] == cohabitation["verdict"]
    assert binding["structural_generic_offer_trial_verdict"] == "falsified_offer_identity_too_broad"

    receipt_schema = json.loads(
        (HERE.parents[1] / "qualification-receipt-contract.schema.json").read_text(encoding="utf-8")
    )
    required = set(receipt_schema["required"])
    allowed = set(receipt_schema["properties"])
    assert len(receipts) == 4
    assert len({row["receipt_id"] for row in receipts}) == len(receipts)
    for row in receipts:
        assert required <= set(row), f"{row['receipt_id']}: missing receipt fields"
        assert set(row) <= allowed, f"{row['receipt_id']}: unexpected receipt fields"
        assert row["independent_appraiser"] is None
        assert row["waiver_ref"] is None
        assert row["subject"] in {provider["exact_offer_id"] for provider in providers}
        assert row["artifact_digest"].startswith("sha256:")
        assert row["dependency_lock_digest"].startswith("sha256:")
        assert row["configuration_digest"].startswith("sha256:")
        assert any("executed-test evidence only" in item for item in row["limitations"])
    receipt_verdicts = {
        (row["subject"], row["oracle"]["id"]): row["verdict"] for row in receipts
    }
    assert receipt_verdicts[(glop["exact_offer_id"], "oracle.lp.safe_status_and_objective.v1")] == "pass"
    assert receipt_verdicts[(glop["exact_offer_id"], "oracle.lp.precise_terminal_classification.v1")] == "fail"
    assert receipt_verdicts[(highs["exact_offer_id"], "oracle.lp.safe_status_and_objective.v1")] == "pass"
    assert receipt_verdicts[(highs["exact_offer_id"], "oracle.lp.precise_terminal_classification.v1")] == "pass"

    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    if jsonschema is not None:
        validator = jsonschema.Draft202012Validator(receipt_schema, format_checker=jsonschema.FormatChecker())
        for row in receipts:
            errors = sorted(validator.iter_errors(row), key=lambda error: list(error.path))
            assert not errors, f"{row['receipt_id']}: JSON Schema errors: {[error.message for error in errors]}"

    assert manifest["counts"] == {
        "executed_oracle_results": len(oracles),
        "executed_test_receipts": len(receipts),
        "provider_results": len(providers),
        "qualified_offers": 0,
    }
    print(
        "PASS exact-scope LP execution evidence: 2 isolated providers, 12 oracle results, "
        "4 executed-test receipts, precise substitution refused, 0 qualified offers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
