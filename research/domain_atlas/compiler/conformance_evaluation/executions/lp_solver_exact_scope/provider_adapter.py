#!/usr/bin/env python3
"""Execute one exact LP provider adapter in an isolated Python process.

This module must never import both provider packages.  The orchestrator invokes it once per
provider environment because the observed wheels load incompatible libhighs dylibs together.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def distribution_digest(package: str) -> tuple[str, list[dict[str, Any]]]:
    dist = importlib.metadata.distribution(package)
    members: list[dict[str, Any]] = []
    for relative in sorted(dist.files or [], key=str):
        path = Path(dist.locate_file(relative))
        if not path.is_file():
            continue
        members.append({
            "path": str(relative),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size": path.stat().st_size,
        })
    return digest(members), members


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_model(model: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    variables = model.get("variables")
    if not isinstance(variables, list) or not variables:
        return ["variables must be a nonempty list"]
    names = [row.get("name") for row in variables if isinstance(row, dict)]
    if len(names) != len(variables) or any(not isinstance(name, str) or not name for name in names):
        errors.append("every variable requires a nonempty string name")
    if len(set(names)) != len(names):
        errors.append("variable names must be unique")
    for row in variables:
        if not isinstance(row, dict):
            errors.append("variable record must be an object")
            continue
        lower, upper = row.get("lower"), row.get("upper")
        if lower is not None and not finite_number(lower):
            errors.append(f"{row.get('name')}: lower bound is not finite")
        if upper is not None and not finite_number(upper):
            errors.append(f"{row.get('name')}: upper bound is not finite")
        if finite_number(lower) and finite_number(upper) and lower > upper:
            errors.append(f"{row.get('name')}: lower bound exceeds upper bound")
    objective = model.get("objective")
    if not isinstance(objective, dict) or objective.get("sense") not in {"minimize", "maximize"}:
        errors.append("objective sense must be minimize or maximize")
    else:
        for name, coefficient in objective.get("coefficients", {}).items():
            if name not in names or not finite_number(coefficient):
                errors.append(f"objective coefficient for {name!r} is unresolved or non-finite")
    constraints = model.get("constraints")
    if not isinstance(constraints, list):
        errors.append("constraints must be a list")
    else:
        constraint_names: list[str] = []
        for row in constraints:
            if not isinstance(row, dict):
                errors.append("constraint record must be an object")
                continue
            constraint_names.append(row.get("name"))
            if row.get("sense") not in {"<=", ">=", "=="}:
                errors.append(f"{row.get('name')}: unsupported constraint sense")
            if not finite_number(row.get("rhs")):
                errors.append(f"{row.get('name')}: rhs is non-finite")
            for name, coefficient in row.get("coefficients", {}).items():
                if name not in names or not finite_number(coefficient):
                    errors.append(f"{row.get('name')}: coefficient for {name!r} is unresolved or non-finite")
        if any(not isinstance(name, str) or not name for name in constraint_names):
            errors.append("every constraint requires a nonempty string name")
        if len(set(constraint_names)) != len(constraint_names):
            errors.append("constraint names must be unique")
    return errors


def solve_ortools(model: dict[str, Any]) -> dict[str, Any]:
    from ortools.linear_solver import pywraplp

    solver = pywraplp.Solver.CreateSolver("GLOP")
    if solver is None:
        return {"canonical_status": "provider_failure", "raw_status": "backend_unavailable"}
    solver.SetNumThreads(1)
    infinity = solver.infinity()
    variables = {
        row["name"]: solver.NumVar(
            -infinity if row["lower"] is None else row["lower"],
            infinity if row["upper"] is None else row["upper"],
            row["name"],
        )
        for row in model["variables"]
    }
    for row in model["constraints"]:
        expression = solver.Sum(coefficient * variables[name] for name, coefficient in row["coefficients"].items())
        if row["sense"] == "<=":
            solver.Add(expression <= row["rhs"], row["name"])
        elif row["sense"] == ">=":
            solver.Add(expression >= row["rhs"], row["name"])
        else:
            solver.Add(expression == row["rhs"], row["name"])
    objective = solver.Sum(
        coefficient * variables[name] for name, coefficient in model["objective"]["coefficients"].items()
    )
    if model["objective"]["sense"] == "maximize":
        solver.Maximize(objective)
    else:
        solver.Minimize(objective)
    started = time.perf_counter_ns()
    raw_status = solver.Solve()
    elapsed = time.perf_counter_ns() - started
    raw_names = {
        pywraplp.Solver.OPTIMAL: "optimal",
        pywraplp.Solver.FEASIBLE: "feasible",
        pywraplp.Solver.INFEASIBLE: "infeasible",
        pywraplp.Solver.UNBOUNDED: "unbounded",
        pywraplp.Solver.ABNORMAL: "abnormal",
        pywraplp.Solver.MODEL_INVALID: "model_invalid",
        pywraplp.Solver.NOT_SOLVED: "not_solved",
    }
    raw_name = raw_names.get(raw_status, f"unknown_{raw_status}")
    # GLOP's proto adapter intentionally maps INFEASIBLE_OR_UNBOUNDED to MPSolver INFEASIBLE.
    # The safe ACL therefore weakens that status instead of asserting precise infeasibility.
    canonical_status = {
        "optimal": "optimal",
        "feasible": "feasible",
        "infeasible": "infeasible_or_unbounded",
        "unbounded": "unbounded",
        "model_invalid": "invalid_input",
        "abnormal": "numerical_failure",
        "not_solved": "limit_without_incumbent",
    }.get(raw_name, "provider_failure")
    has_solution = raw_status in {pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE}
    return {
        "backend_version": solver.SolverVersion(),
        "canonical_status": canonical_status,
        "elapsed_ns": elapsed,
        "iterations": solver.iterations(),
        "objective": solver.Objective().Value() if has_solution else None,
        "raw_status": raw_name,
        "solution": {name: variable.solution_value() for name, variable in variables.items()} if has_solution else None,
        "status_mapping_note": (
            "MPSolver INFEASIBLE is weakened to infeasible_or_unbounded for GLOP because the "
            "versioned GLOP adapter collapses those internal states."
        ),
        "verify_solution": solver.VerifySolution(1e-7, False) if has_solution else None,
    }


def solve_highspy(model: dict[str, Any]) -> dict[str, Any]:
    import highspy

    solver = highspy.Highs()
    solver.setOptionValue("output_flag", False)
    solver.setOptionValue("threads", 1)
    solver.setOptionValue("time_limit", 10.0)
    infinity = highspy.kHighsInf
    variables = {
        row["name"]: solver.addVariable(
            lb=-infinity if row["lower"] is None else row["lower"],
            ub=infinity if row["upper"] is None else row["upper"],
            name=row["name"],
        )
        for row in model["variables"]
    }
    for row in model["constraints"]:
        expression: Any = 0.0
        for name, coefficient in row["coefficients"].items():
            expression = expression + coefficient * variables[name]
        if row["sense"] == "<=":
            solver.addConstr(expression <= row["rhs"], name=row["name"])
        elif row["sense"] == ">=":
            solver.addConstr(expression >= row["rhs"], name=row["name"])
        else:
            solver.addConstr(expression == row["rhs"], name=row["name"])
    objective: Any = 0.0
    for name, coefficient in model["objective"]["coefficients"].items():
        objective = objective + coefficient * variables[name]
    started = time.perf_counter_ns()
    if model["objective"]["sense"] == "maximize":
        call_status = solver.maximize(objective)
    else:
        call_status = solver.minimize(objective)
    elapsed = time.perf_counter_ns() - started
    status = solver.getModelStatus()
    raw_name = str(status).split(".")[-1]
    canonical_status = {
        "kOptimal": "optimal",
        "kInfeasible": "infeasible",
        "kUnbounded": "unbounded",
        "kUnboundedOrInfeasible": "infeasible_or_unbounded",
        "kTimeLimit": "limit_without_incumbent",
        "kIterationLimit": "limit_without_incumbent",
        "kObjectiveBound": "limit_without_incumbent",
        "kObjectiveTarget": "limit_without_incumbent",
        "kUnknown": "provider_failure",
        "kModelError": "invalid_input",
        "kSolveError": "provider_failure",
        "kPresolveError": "provider_failure",
        "kPostsolveError": "provider_failure",
        "kLoadError": "provider_failure",
    }.get(raw_name, "provider_failure")
    has_solution = canonical_status in {"optimal", "feasible", "limit_with_incumbent"}
    return {
        "backend_version": solver.version(),
        "call_status": str(call_status).split(".")[-1],
        "canonical_status": canonical_status,
        "elapsed_ns": elapsed,
        "objective": solver.getObjectiveValue() if has_solution else None,
        "raw_status": raw_name,
        "raw_status_text": solver.modelStatusToString(status),
        "solution": {name: solver.val(variable) for name, variable in variables.items()} if has_solution else None,
        "status_mapping_note": "HiGHS model status is preserved unless a limit requires separate incumbent inspection.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    provider = next(row for row in protocol["providers"] if row["provider_id"] == args.provider)
    observed_versions = {
        pin.split("==", 1)[0]: importlib.metadata.version(pin.split("==", 1)[0])
        for pin in provider["declared_dependency_lock"]
    }
    expected_versions = {pin.split("==", 1)[0]: pin.split("==", 1)[1] for pin in provider["declared_dependency_lock"]}
    if observed_versions != expected_versions:
        raise SystemExit(f"dependency identity mismatch: {observed_versions!r} != {expected_versions!r}")
    artifact_digest, artifact_members = distribution_digest(provider["package"])
    environment = {
        "machine": platform.machine(),
        "platform": platform.platform(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
    }
    results: list[dict[str, Any]] = []
    for fixture in protocol["fixtures"]:
        validation_errors = validate_model(fixture["model"])
        if validation_errors:
            result = {
                "canonical_status": "invalid_input",
                "provider_invoked": False,
                "refusal_reasons": validation_errors,
            }
        else:
            result = (
                solve_ortools(fixture["model"])
                if provider["adapter"] == "ortools_glop_mpsolver"
                else solve_highspy(fixture["model"])
            )
            result["provider_invoked"] = True
        results.append({
            "expected": fixture["expected"],
            "fixture_id": fixture["fixture_id"],
            "result": result,
        })
    output = {
        "adapter": provider["adapter"],
        "adapter_digest": "sha256:" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "artifact_digest": artifact_digest,
        "artifact_member_count": len(artifact_members),
        "artifact_native_members": [
            row for row in artifact_members
            if row["path"].endswith((".so", ".dylib", ".dll", ".pyd"))
        ],
        "dependency_lock": provider["declared_dependency_lock"],
        "dependency_lock_digest": digest(provider["declared_dependency_lock"]),
        "environment": environment,
        "environment_digest": digest(environment),
        "exact_offer_id": provider["exact_offer_id"],
        "provider_id": provider["provider_id"],
        "provider_version": observed_versions[provider["package"]],
        "record_kind": "provider_execution_result",
        "results": results,
        "target_occurrence": (
            f"target.local.{platform.system().lower()}.{platform.machine().lower()}."
            f"python-{platform.python_version()}.isolated-process"
        ),
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
