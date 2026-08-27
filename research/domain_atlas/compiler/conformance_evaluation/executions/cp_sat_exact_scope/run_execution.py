#!/usr/bin/env python3
"""Run and retain append-only evidence for the exact CP-SAT Python profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]], key: str) -> None:
    path.write_text("".join(canonical(row) + "\n" for row in sorted(rows, key=lambda row: row[key])), encoding="utf-8")


def expression_value(coefficients: dict[str, int], solution: dict[str, int]) -> int:
    return sum(coefficient * solution[name] for name, coefficient in coefficients.items())


def check_solution(model: dict[str, Any], solution: dict[str, int], objective: float | None) -> list[str]:
    failures: list[str] = []
    variables = {row["name"]: row for row in model["variables"]}
    if set(solution) != set(variables):
        return ["solution variable identity mismatch"]
    for name, value in solution.items():
        row = variables[name]
        if not isinstance(value, int) or isinstance(value, bool):
            failures.append(f"{name}: solution is not an integer")
        elif not row["lower"] <= value <= row["upper"]:
            failures.append(f"{name}: domain violation")
        if row["kind"] == "boolean" and value not in {0, 1}:
            failures.append(f"{name}: Boolean-domain violation")
    intervals = {row["name"]: row for row in model["intervals"]}
    for row in intervals.values():
        if solution[row["end"]] != solution[row["start"]] + row["duration"]:
            failures.append(f"{row['name']}: interval duration violation")
    for index, row in enumerate(model["constraints"]):
        kind = row["type"]
        if kind == "linear":
            value = expression_value(row["coefficients"], solution)
            if row["sense"] == "<=" and value > row["rhs"]:
                failures.append(f"constraint {index}: <= violation")
            elif row["sense"] == ">=" and value < row["rhs"]:
                failures.append(f"constraint {index}: >= violation")
            elif row["sense"] == "==" and value != row["rhs"]:
                failures.append(f"constraint {index}: equality violation")
        elif kind == "all_different":
            values = [solution[name] for name in row["variables"]]
            if len(values) != len(set(values)):
                failures.append(f"constraint {index}: all_different violation")
        elif kind == "exactly_one":
            if sum(solution[name] for name in row["variables"]) != 1:
                failures.append(f"constraint {index}: exactly_one violation")
        elif kind == "precedence":
            if solution[row["first_end"]] > solution[row["second_start"]]:
                failures.append(f"constraint {index}: precedence violation")
        elif kind == "no_overlap":
            selected = [intervals[name] for name in row["intervals"]]
            for left_index, left in enumerate(selected):
                for right in selected[left_index + 1:]:
                    if not (
                        solution[left["end"]] <= solution[right["start"]]
                        or solution[right["end"]] <= solution[left["start"]]
                    ):
                        failures.append(f"constraint {index}: no_overlap violation")
        elif kind == "max_equality":
            if solution[row["target"]] != max(solution[name] for name in row["variables"]):
                failures.append(f"constraint {index}: max_equality violation")
    if model["objective"] is not None and objective is not None:
        recomputed = expression_value(model["objective"]["coefficients"], solution)
        if recomputed != objective:
            failures.append("provider objective differs from independent recomputation")
    return failures


def uv_command(protocol: dict[str, Any]) -> list[str]:
    command = ["uv", "run", "--isolated", "--no-project"]
    for pin in protocol["provider"]["declared_dependency_lock"]:
        command.extend(["--with", pin])
    command.extend(["python", str(HERE / "provider_adapter.py"), "--protocol", str(HERE / "protocol.json")])
    return command


def execute(protocol: dict[str, Any], environment: dict[str, str]) -> tuple[dict[str, Any], dict[str, str]]:
    started = datetime.now(timezone.utc)
    completed = subprocess.run(uv_command(protocol), cwd=HERE, env=environment, text=True, capture_output=True, check=False)
    ended = datetime.now(timezone.utc)
    if completed.returncode != 0:
        raise RuntimeError(f"provider execution failed:\nstdout={completed.stdout}\nstderr={completed.stderr}")
    result = json.loads(completed.stdout)
    result["runner_stderr"] = completed.stderr
    return result, {
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "ended_at": ended.isoformat().replace("+00:00", "Z"),
    }


def evaluate(protocol: dict[str, Any], provider: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    fixtures = {row["fixture_id"]: row for row in protocol["fixtures"]}
    rows: list[dict[str, Any]] = []
    profile_outcomes: dict[str, list[bool]] = {row["profile_id"]: [] for row in protocol["profiles"]}
    for execution in provider["results"]:
        fixture = fixtures[execution["fixture_id"]]
        expected = fixture["expected"]
        result = execution["result"]
        failures: list[str] = []
        if result["canonical_status"] != expected["status"]:
            failures.append(f"expected {expected['status']}, observed {result['canonical_status']}")
        if expected["status"] == "invalid_input":
            if result.get("provider_validator_invoked") or result.get("provider_solver_invoked"):
                failures.append("canonical invalid input reached provider code")
        elif expected["status"] == "model_invalid":
            if result.get("provider_validator_invoked") is not True or result.get("provider_solver_invoked") is not False:
                failures.append("provider model-invalid path did not stop before solve")
        elif expected["status"] == "optimal":
            if result.get("solution") is None:
                failures.append("optimal result lacks solution")
            else:
                failures.extend(check_solution(fixture["model"], result["solution"], result.get("objective")))
            if expected.get("objective") is not None and result.get("objective") != expected["objective"]:
                failures.append("objective differs from independently declared optimum")
            if expected.get("solution_count") is not None:
                if result.get("solution_count") != expected["solution_count"]:
                    failures.append("complete-enumeration count differs")
                solutions = result.get("solutions") or []
                if len({canonical(item) for item in solutions}) != expected["solution_count"]:
                    failures.append("enumerated solutions are incomplete or duplicated")
                for solution in solutions:
                    failures.extend(check_solution(fixture["model"], solution, None))
        elif expected["status"] == "unknown":
            if result["canonical_status"] != "unknown":
                failures.append("limit result was strengthened")
        passed = not failures
        for profile_ref in fixture["profile_refs"]:
            profile_outcomes[profile_ref].append(passed)
        rows.append({
            "fixture_id": fixture["fixture_id"],
            "observed_canonical_status": result["canonical_status"],
            "oracle_failures": failures,
            "oracle_verdict": "pass" if passed else "fail",
            "profile_refs": fixture["profile_refs"],
            "provider_id": provider["provider_id"],
            "record_kind": "executed_oracle_result",
        })
    return rows, {
        profile_ref: "pass" if outcomes and all(outcomes) else "fail"
        for profile_ref, outcomes in profile_outcomes.items()
    }


def receipt(run_id: str, profile: str, verdict: str, protocol: dict[str, Any], provider: dict[str, Any], timing: dict[str, str]) -> dict[str, Any]:
    recorded = datetime.fromisoformat(timing["ended_at"].replace("Z", "+00:00"))
    profile_name = profile.removeprefix("profile.cpsat.")
    return {
        "artifact_digest": provider["artifact_digest"],
        "configuration_digest": digest({"adapter_digest": provider["adapter_digest"], "profile": profile, "protocol": protocol}),
        "dependency_lock_digest": provider["dependency_lock_digest"],
        "edition": 1,
        "evidence_objects": ["protocol.json", "provider-results.jsonl", "oracle-results.jsonl"],
        "execution": {"attempts": 1, "ended_at": timing["ended_at"], "environment_digest": provider["environment_digest"], "runner": "run_execution.py", "started_at": timing["started_at"]},
        "independent_appraiser": None,
        "invalidation_triggers": protocol["invalidation_triggers"],
        "limitations": [
            "This is executed-test evidence only; no independent appraisal occurred.",
            "The receipt does not qualify the offer, establish portability or prove production fitness.",
            "The profile excludes omitted CP-SAT features, parallelism, performance, security, licensing and vertical acceptance."
        ],
        "oracle": {"authority": "authority.conformance.cpsat_protocol_owner", "edition": 1, "id": profile},
        "population": {
            "coverage": [row["fixture_id"] for row in protocol["fixtures"] if profile in row["profile_refs"]],
            "definition": "Exact declared CP-SAT fixture subset for one profile.",
            "seed_policy": "single_worker_fixed_seed_1729",
            "size": sum(profile in row["profile_refs"] for row in protocol["fixtures"]),
        },
        "receipt_id": f"receipt.{run_id}.ortools_cp_sat_python.{profile_name}",
        "subject": provider["exact_offer_id"],
        "target_occurrence": provider["target_occurrence"],
        "validity": {"expires_at": (recorded + timedelta(days=30)).isoformat().replace("+00:00", "Z"), "recorded_at": timing["ended_at"], "revoked": False},
        "verdict": verdict,
        "waiver_ref": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--uv-cache", type=Path, default=Path("/tmp/shannon-qualification-uv-cache"))
    args = parser.parse_args()
    protocol = json.loads((HERE / "protocol.json").read_text(encoding="utf-8"))
    output_dir = args.output_dir or HERE / "runs" / args.run_id
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"refusing to overwrite append-only evidence directory {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["UV_CACHE_DIR"] = str(args.uv_cache)
    environment["PYTHONNOUSERSITE"] = "1"
    provider, timing = execute(protocol, environment)
    oracle_rows, profile_verdicts = evaluate(protocol, provider)
    receipts = [receipt(args.run_id, profile, verdict, protocol, provider, timing) for profile, verdict in sorted(profile_verdicts.items())]
    assessment = {
        "binding_eligible": False,
        "exact_offer_id": provider["exact_offer_id"],
        "profile_verdicts": profile_verdicts,
        "qualification_state": "executed_not_independently_appraised",
        "reason": "Exact-scope executed evidence can narrow candidates but cannot replace independent appraisal, full provider qualification or vertical acceptance.",
        "target_occurrence": provider["target_occurrence"],
    }
    write_jsonl(output_dir / "provider-results.jsonl", [provider], "provider_id")
    write_jsonl(output_dir / "oracle-results.jsonl", oracle_rows, "fixture_id")
    write_jsonl(output_dir / "qualification-receipts.jsonl", receipts, "receipt_id")
    write_json(output_dir / "binding-assessment.json", assessment)
    files = ["binding-assessment.json", "oracle-results.jsonl", "provider-results.jsonl", "qualification-receipts.jsonl"]
    manifest = {
        "completion_claim": False,
        "files": [{"path": name, "sha256": hashlib.sha256((output_dir / name).read_bytes()).hexdigest(), "bytes": (output_dir / name).stat().st_size} for name in files],
        "profile_verdicts": profile_verdicts,
        "protocol_digest": "sha256:" + hashlib.sha256((HERE / "protocol.json").read_bytes()).hexdigest(),
        "qualified_offers": 0,
        "run_id": args.run_id,
        "status": "executed_evidence_not_qualified",
    }
    write_json(output_dir / "manifest.json", manifest)
    print(f"PASS CP-SAT execution retained at {output_dir}; profiles={profile_verdicts}; qualified_offers=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
