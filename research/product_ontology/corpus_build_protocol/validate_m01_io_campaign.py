#!/usr/bin/env python3
"""Validate retained M01 I/O observations without promoting them to qualification."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WAVE = "M01_UNIVERSE_AND_EVIDENCE_PRODUCERS"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    rows = load_jsonl(HERE / "m01-io-observations.jsonl")
    summary = json.loads((HERE / "m01-io-campaign-summary.json").read_text(encoding="utf-8"))
    dockets = load_jsonl(HERE / "contract-candidate-dockets.jsonl")
    expected = {row["package_candidate_ref"] for row in dockets if row["migration_wave_ref"] == WAVE}
    assert expected == {row["package_candidate_ref"] for row in rows}
    assert len(rows) == len({row["observation_id"] for row in rows}) == summary["package_observations"]
    assert subprocess.run(["git", "merge-base", "--is-ancestor", summary["subject_commit"], "HEAD"], cwd=ROOT).returncode == 0
    for row in rows:
        root_prefix = row["package_root"].rstrip("/") + "/"
        assert row["same_campaign_controlled"] is True and row["independent_appraisal"] is False
        assert row["execution_authorized_for_canonical_orchestrator"] is False
        assert row["qualification_claim"] is False and row["ratification_claim"] is False and row["completion_claim"] is False
        assert row["all_builders_two_run_stable"] and row["all_builders_exit_zero"] and row["all_writes_package_local"]
        assert row["all_validators_pass"] and row["validators_read_only"]
        for builder in row["builder_observations"]:
            assert hashlib.sha256((ROOT / builder["builder_path"]).read_bytes()).hexdigest() == builder["builder_sha256"]
            assert builder["first_tree_sha256"] == builder["second_tree_sha256"] and builder["two_run_stable"]
            assert builder["exit_codes"] == [0, 0] and not builder["outside_package_write_paths"]
            assert all(path.startswith(root_prefix) for path in builder["repository_write_paths"])
        for validator in row["validator_observations"]:
            assert hashlib.sha256((ROOT / validator["validator_path"]).read_bytes()).hexdigest() == validator["validator_sha256"]
            assert validator["exit_code"] == 0
    payload = (HERE / "m01-io-observations.jsonl").read_bytes()
    assert hashlib.sha256(payload).hexdigest() == summary["observations_sha256"]
    assert summary["stable_packages"] == summary["package_local_write_packages"] == summary["validator_pass_packages"] == len(rows)
    assert summary["independent_appraisals"] == summary["execution_authorizations_created"] == 0
    assert summary["qualification_claim"] is False and summary["ratification_claim"] is False and summary["completion_claim"] is False
    print(f"PASS M01 I/O campaign: {len(rows)} packages rebuilt twice deterministically with package-local writes and passing read-only validators; same-campaign evidence only, execution authorization remains withheld")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

