#!/usr/bin/env python3
"""Execute the exact-scope LP conformance pilot and retain append-only evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value).encode()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]], key: str) -> None:
    path.write_text("".join(canonical(row) + "\n" for row in sorted(rows, key=lambda row: row[key])), encoding="utf-8")


def uv_command(provider: dict[str, Any], protocol_path: Path) -> list[str]:
    command = ["uv", "run", "--isolated", "--no-project"]
    for pin in provider["declared_dependency_lock"]:
        command.extend(["--with", pin])
    command.extend([
        "python", str(HERE / "provider_adapter.py"),
        "--provider", provider["provider_id"],
        "--protocol", str(protocol_path),
    ])
    return command


def execute_provider(
    provider: dict[str, Any], protocol_path: Path, environment: dict[str, str]
) -> tuple[dict[str, Any], dict[str, str]]:
    started = datetime.now(timezone.utc)
    completed = subprocess.run(
        uv_command(provider, protocol_path),
        cwd=HERE,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    ended = datetime.now(timezone.utc)
    if completed.returncode != 0:
        raise RuntimeError(
            f"provider execution failed for {provider['provider_id']}:\n"
            f"stdout={completed.stdout}\nstderr={completed.stderr}"
        )
    output = json.loads(completed.stdout)
    timing = {
        "started_at": started.isoformat().replace("+00:00", "Z"),
        "ended_at": ended.isoformat().replace("+00:00", "Z"),
    }
    output["runner_stderr"] = completed.stderr
    return output, timing


def expression_value(coefficients: dict[str, float], solution: dict[str, float]) -> float:
    return math.fsum(coefficient * solution[name] for name, coefficient in coefficients.items())


def independently_check_solution(
    model: dict[str, Any], solution: dict[str, float], objective: float, tolerance: float
) -> list[str]:
    failures: list[str] = []
    variables = {row["name"]: row for row in model["variables"]}
    if set(solution) != set(variables):
        return ["solution variable identity mismatch"]
    for name, value in solution.items():
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            failures.append(f"{name}: solution value is non-finite")
            continue
        lower, upper = variables[name]["lower"], variables[name]["upper"]
        if lower is not None and value < lower - tolerance:
            failures.append(f"{name}: lower-bound violation")
        if upper is not None and value > upper + tolerance:
            failures.append(f"{name}: upper-bound violation")
    for constraint in model["constraints"]:
        actual = expression_value(constraint["coefficients"], solution)
        rhs = constraint["rhs"]
        if constraint["sense"] == "<=" and actual > rhs + tolerance:
            failures.append(f"{constraint['name']}: <= violation")
        elif constraint["sense"] == ">=" and actual < rhs - tolerance:
            failures.append(f"{constraint['name']}: >= violation")
        elif constraint["sense"] == "==" and abs(actual - rhs) > tolerance:
            failures.append(f"{constraint['name']}: equality violation")
    recomputed = expression_value(model["objective"]["coefficients"], solution)
    if not math.isclose(recomputed, objective, rel_tol=tolerance, abs_tol=tolerance):
        failures.append("provider objective disagrees with independent recomputation")
    return failures


def evaluate_provider(
    protocol: dict[str, Any], provider_result: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    tolerance = max(
        protocol["scope"]["numeric_policy"]["absolute_tolerance"],
        protocol["scope"]["numeric_policy"]["relative_tolerance"],
    )
    fixtures = {row["fixture_id"]: row for row in protocol["fixtures"]}
    oracle_rows: list[dict[str, Any]] = []
    safe_outcomes: list[bool] = []
    precise_outcomes: list[bool] = []
    for execution in provider_result["results"]:
        fixture = fixtures[execution["fixture_id"]]
        expected = fixture["expected"]
        result = execution["result"]
        observed = result["canonical_status"]
        safe_failures: list[str] = []
        precise_failures: list[str] = []
        if expected["status"] == "invalid_input":
            if observed != "invalid_input" or result.get("provider_invoked") is not False:
                safe_failures.append("invalid input was not refused before provider invocation")
        elif expected["status"] == "optimal":
            if observed != "optimal":
                safe_failures.append(f"expected optimal, observed {observed}")
            elif result.get("solution") is None or result.get("objective") is None:
                safe_failures.append("optimal status lacks solution or objective")
            else:
                safe_failures.extend(
                    independently_check_solution(
                        fixture["model"], result["solution"], result["objective"], tolerance
                    )
                )
                if not math.isclose(
                    result["objective"], expected["objective"], rel_tol=tolerance, abs_tol=tolerance
                ):
                    safe_failures.append("objective differs from independently declared fixture optimum")
        elif expected["status"] == "infeasible":
            if observed not in {"infeasible", "infeasible_or_unbounded"}:
                safe_failures.append(f"unsound infeasibility-family status {observed}")
            if observed != "infeasible":
                precise_failures.append("provider adapter cannot distinguish infeasible from unbounded")
        elif expected["status"] == "unbounded":
            if observed not in {"unbounded", "infeasible_or_unbounded"}:
                safe_failures.append(f"unsound unbounded-family status {observed}")
            if observed != "unbounded":
                precise_failures.append("provider adapter cannot distinguish unbounded from infeasible")
        if safe_failures:
            precise_failures.extend(item for item in safe_failures if item not in precise_failures)
        safe_pass = not safe_failures
        precise_pass = not precise_failures
        safe_outcomes.append(safe_pass)
        precise_outcomes.append(precise_pass)
        oracle_rows.append({
            "fixture_id": fixture["fixture_id"],
            "observed_canonical_status": observed,
            "precise_failures": precise_failures,
            "precise_terminal_oracle": "pass" if precise_pass else "fail",
            "provider_id": provider_result["provider_id"],
            "record_kind": "executed_oracle_result",
            "safe_failures": safe_failures,
            "safe_status_objective_oracle": "pass" if safe_pass else "fail",
        })
    return oracle_rows, {
        "safe": "pass" if all(safe_outcomes) else "fail",
        "precise": "pass" if all(precise_outcomes) else "fail",
    }


def cohabitation_probe(protocol: dict[str, Any], environment: dict[str, str]) -> dict[str, Any]:
    pins = sorted({pin for provider in protocol["providers"] for pin in provider["declared_dependency_lock"]})
    command = ["uv", "run", "--isolated", "--no-project"]
    for pin in pins:
        command.extend(["--with", pin])
    command.extend([
        "python", "-c",
        "import highspy; from ortools.linear_solver import pywraplp; "
        "assert pywraplp.Solver.CreateSolver('GLOP') is not None; print('cohabitation-import-pass')",
    ])
    completed = subprocess.run(
        command, cwd=HERE, env=environment, text=True, capture_output=True, check=False
    )
    stderr_lower = completed.stderr.lower()
    if completed.returncode == 0:
        verdict = "cohabitation_observed_pass_not_generalized"
    elif "symbol not found" in stderr_lower and "libhighs" in stderr_lower:
        verdict = "observed_native_abi_collision_process_isolation_required"
    else:
        verdict = "inconclusive_unclassified_cohabitation_failure"
    return {
        "command_dependency_lock": pins,
        "evidence_digest": digest_value({
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }),
        "process_isolation_requirement": verdict == "observed_native_abi_collision_process_isolation_required",
        "record_kind": "runtime_cohabitation_negative_twin",
        "returncode": completed.returncode,
        "stderr": completed.stderr,
        "stdout": completed.stdout,
        "trial_id": "negative_twin.lp.ortools_highspy.same_python_process",
        "verdict": verdict,
    }


def receipt(
    *,
    run_id: str,
    profile: str,
    provider_result: dict[str, Any],
    timing: dict[str, str],
    verdict: str,
    protocol: dict[str, Any],
) -> dict[str, Any]:
    recorded = datetime.fromisoformat(timing["ended_at"].replace("Z", "+00:00"))
    return {
        "artifact_digest": provider_result["artifact_digest"],
        "configuration_digest": digest_value({
            "adapter_digest": provider_result["adapter_digest"],
            "profile": profile,
            "protocol": protocol,
        }),
        "dependency_lock_digest": provider_result["dependency_lock_digest"],
        "edition": 1,
        "evidence_objects": [
            "protocol.json",
            "provider-results.jsonl",
            "oracle-results.jsonl",
            "cohabitation-negative-twin.json",
        ],
        "execution": {
            "attempts": 1,
            "ended_at": timing["ended_at"],
            "environment_digest": provider_result["environment_digest"],
            "runner": "run_execution.py",
            "started_at": timing["started_at"],
        },
        "independent_appraiser": None,
        "invalidation_triggers": protocol["invalidation_triggers"],
        "limitations": [
            "This is executed-test evidence only; no independent appraisal occurred.",
            "The receipt does not qualify a provider offer, establish portability or prove production fitness.",
            "The scope excludes cancellation, progress, performance, security, licenses and vertical acceptance.",
        ],
        "oracle": {
            "authority": "authority.conformance.lp_protocol_owner",
            "edition": 1,
            "id": f"oracle.lp.{profile}.v1",
        },
        "population": {
            "coverage": [row["fixture_id"] for row in protocol["fixtures"]],
            "definition": "Six declared continuous-LP fixtures including invalid, optimal, degenerate, scaled, infeasible and unbounded cases.",
            "seed_policy": "not_applicable_deterministic_fixtures",
            "size": len(protocol["fixtures"]),
        },
        "receipt_id": f"receipt.{run_id}.{provider_result['adapter']}.{profile}",
        "subject": provider_result["exact_offer_id"],
        "target_occurrence": provider_result["target_occurrence"],
        "validity": {
            "expires_at": (recorded + timedelta(days=30)).isoformat().replace("+00:00", "Z"),
            "recorded_at": timing["ended_at"],
            "revoked": False,
        },
        "verdict": verdict,
        "waiver_ref": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--uv-cache", type=Path, default=Path("/tmp/shannon-qualification-uv-cache"))
    args = parser.parse_args()

    protocol_path = HERE / "protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    output_dir = args.output_dir or HERE / "runs" / args.run_id
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"refusing to overwrite append-only evidence directory {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["UV_CACHE_DIR"] = str(args.uv_cache)
    environment["PYTHONNOUSERSITE"] = "1"

    provider_results: list[dict[str, Any]] = []
    timings: dict[str, dict[str, str]] = {}
    oracle_results: list[dict[str, Any]] = []
    assessments: dict[str, dict[str, str]] = {}
    for provider in protocol["providers"]:
        result, timing = execute_provider(provider, protocol_path, environment)
        provider_results.append(result)
        timings[result["provider_id"]] = timing
        rows, assessment = evaluate_provider(protocol, result)
        oracle_results.extend(rows)
        assessments[result["provider_id"]] = assessment

    cohabitation = cohabitation_probe(protocol, environment)
    receipts: list[dict[str, Any]] = []
    for result in provider_results:
        assessment = assessments[result["provider_id"]]
        receipts.extend([
            receipt(
                run_id=args.run_id,
                profile="safe_status_and_objective",
                provider_result=result,
                timing=timings[result["provider_id"]],
                verdict=assessment["safe"],
                protocol=protocol,
            ),
            receipt(
                run_id=args.run_id,
                profile="precise_terminal_classification",
                provider_result=result,
                timing=timings[result["provider_id"]],
                verdict=assessment["precise"],
                protocol=protocol,
            ),
        ])

    by_provider = {row["provider_id"]: row for row in provider_results}
    left, right = (by_provider[row["provider_id"]] for row in protocol["providers"])
    left_oracles = {row["fixture_id"]: row for row in oracle_results if row["provider_id"] == left["provider_id"]}
    right_oracles = {row["fixture_id"]: row for row in oracle_results if row["provider_id"] == right["provider_id"]}
    objective_agreements = []
    status_differences = []
    for fixture in protocol["fixtures"]:
        fixture_id = fixture["fixture_id"]
        l_exec = next(row for row in left["results"] if row["fixture_id"] == fixture_id)["result"]
        r_exec = next(row for row in right["results"] if row["fixture_id"] == fixture_id)["result"]
        if fixture["expected"]["status"] == "optimal":
            objective_agreements.append({
                "fixture_id": fixture_id,
                "left": l_exec["objective"],
                "right": r_exec["objective"],
                "within_tolerance": math.isclose(
                    l_exec["objective"], r_exec["objective"], rel_tol=1e-7, abs_tol=1e-7
                ),
            })
        if l_exec["canonical_status"] != r_exec["canonical_status"]:
            status_differences.append({
                "fixture_id": fixture_id,
                "left": l_exec["canonical_status"],
                "right": r_exec["canonical_status"],
            })
    safe_agreement = all(
        row["safe_status_objective_oracle"] == "pass"
        for row in list(left_oracles.values()) + list(right_oracles.values())
    ) and all(row["within_tolerance"] for row in objective_agreements)
    precise_agreement = not status_differences and all(
        row["precise_terminal_oracle"] == "pass"
        for row in list(left_oracles.values()) + list(right_oracles.values())
    )
    differential = {
        "differential_id": f"differential.{args.run_id}.ortools_glop__highs",
        "objective_agreements": objective_agreements,
        "precise_scope_agreement": precise_agreement,
        "provider_refs": [left["exact_offer_id"], right["exact_offer_id"]],
        "record_kind": "executed_provider_differential",
        "safe_scope_agreement": safe_agreement,
        "status_differences": status_differences,
        "verdict": (
            "safe_scope_executed_agreement_precise_scope_not_substitutable"
            if safe_agreement and not precise_agreement
            else "inconclusive_or_failed"
        ),
    }
    binding = {
        "assessment_id": f"binding_assessment.{args.run_id}",
        "bindable_offer_refs": [],
        "cohabitation_verdict": cohabitation["verdict"],
        "corpus_corrections": [
            "Replace generic OR-Tools suite identity with exact solver plus API adapter offer identities.",
            "Make runtime cohabitation/process isolation a target-binding decision.",
            "Require a declared status-precision policy before treating GLOP/MPSolver and HiGHS as substitutes.",
            "Retain executed-test receipts below independent appraisal and qualification gates.",
        ],
        "exact_offer_refs": [row["exact_offer_id"] for row in provider_results],
        "independent_appraisal": "not_executed",
        "portable_offer_refs": [],
        "qualification_verdict": "withheld",
        "record_kind": "binding_assessment",
        "structural_generic_offer_trial_verdict": "falsified_offer_identity_too_broad",
        "vertical_acceptance": "not_executed",
    }

    payloads: dict[str, str] = {
        "binding-assessment.json": json.dumps(binding, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        "cohabitation-negative-twin.json": json.dumps(cohabitation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        "differential-verdict.json": json.dumps(differential, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        "oracle-results.jsonl": "".join(canonical(row) + "\n" for row in sorted(oracle_results, key=lambda row: (row["provider_id"], row["fixture_id"]))),
        "provider-results.jsonl": "".join(canonical(row) + "\n" for row in sorted(provider_results, key=lambda row: row["provider_id"])),
        "qualification-receipts.jsonl": "".join(canonical(row) + "\n" for row in sorted(receipts, key=lambda row: row["receipt_id"])),
    }
    for name, content in payloads.items():
        (output_dir / name).write_text(content, encoding="utf-8")
    manifest = {
        "completion_claim": False,
        "counts": {
            "executed_oracle_results": len(oracle_results),
            "executed_test_receipts": len(receipts),
            "provider_results": len(provider_results),
            "qualified_offers": 0,
        },
        "file_sha256": {
            name: hashlib.sha256(content.encode()).hexdigest()
            for name, content in sorted(payloads.items())
        },
        "protocol_digest": "sha256:" + hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        "qualification_status": "withheld",
        "run_id": args.run_id,
        "status": "executed_test_evidence_not_independently_appraised",
    }
    write_json(output_dir / "manifest.json", manifest)
    print(
        f"PASS execution retained at {output_dir}: {len(provider_results)} providers, "
        f"{len(oracle_results)} oracle results, {len(receipts)} receipts, 0 qualified offers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
