#!/usr/bin/env python3
"""Execute the exact OR-Tools CP-SAT Python surface in an isolated process."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path
from typing import Any


INT_MIN = -(2**63)
INT_MAX = 2**63 - 1


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and INT_MIN <= value <= INT_MAX


def distribution_digest(package: str) -> tuple[str, list[dict[str, Any]]]:
    dist = importlib.metadata.distribution(package)
    members: list[dict[str, Any]] = []
    for relative in sorted(dist.files or [], key=str):
        path = Path(dist.locate_file(relative))
        if path.is_file():
            members.append({
                "path": str(relative),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size": path.stat().st_size,
            })
    return digest(members), members


def validate_model(model: dict[str, Any], enumerate_all: bool) -> list[str]:
    errors: list[str] = []
    variables = model.get("variables")
    if not isinstance(variables, list) or not variables:
        return ["variables must be a nonempty list"]
    names: list[str] = []
    kinds: dict[str, str] = {}
    for row in variables:
        if not isinstance(row, dict):
            errors.append("variable record must be an object")
            continue
        name = row.get("name")
        if not isinstance(name, str) or not name:
            errors.append("every variable requires a nonempty string name")
            continue
        names.append(name)
        kind = row.get("kind")
        kinds[name] = kind
        if kind not in {"integer", "boolean"}:
            errors.append(f"{name}: unsupported variable kind")
        lower, upper = row.get("lower"), row.get("upper")
        if not is_int(lower) or not is_int(upper):
            errors.append(f"{name}: bounds must be signed int64")
        elif lower > upper:
            errors.append(f"{name}: lower bound exceeds upper bound")
        if kind == "boolean" and (lower, upper) != (0, 1):
            errors.append(f"{name}: Boolean bounds must be exactly 0..1")
    if len(names) != len(set(names)):
        errors.append("variable names must be unique")
    name_set = set(names)

    objective = model.get("objective")
    if objective is not None:
        if not isinstance(objective, dict) or objective.get("sense") not in {"minimize", "maximize"}:
            errors.append("objective must be null or a minimize/maximize object")
        else:
            coefficients = objective.get("coefficients")
            if not isinstance(coefficients, dict) or not coefficients:
                errors.append("objective coefficients must be a nonempty object")
            else:
                for name, coefficient in coefficients.items():
                    if name not in name_set or not is_int(coefficient):
                        errors.append(f"objective coefficient for {name!r} is unresolved or noninteger")
        if enumerate_all:
            errors.append("complete enumeration profile forbids an objective")

    intervals = model.get("intervals")
    interval_names: list[str] = []
    if not isinstance(intervals, list):
        errors.append("intervals must be a list")
    else:
        for row in intervals:
            if not isinstance(row, dict):
                errors.append("interval record must be an object")
                continue
            name = row.get("name")
            if not isinstance(name, str) or not name:
                errors.append("every interval requires a nonempty string name")
                continue
            interval_names.append(name)
            if row.get("start") not in name_set or row.get("end") not in name_set:
                errors.append(f"{name}: start/end variable is unresolved")
            if not is_int(row.get("duration")) or row["duration"] <= 0:
                errors.append(f"{name}: duration must be a positive int64")
        if len(interval_names) != len(set(interval_names)):
            errors.append("interval names must be unique")
    interval_set = set(interval_names)

    constraints = model.get("constraints")
    if not isinstance(constraints, list):
        return errors + ["constraints must be a list"]
    for index, row in enumerate(constraints):
        if not isinstance(row, dict):
            errors.append(f"constraint {index}: record must be an object")
            continue
        kind = row.get("type")
        if kind == "linear":
            if row.get("sense") not in {"<=", ">=", "=="} or not is_int(row.get("rhs")):
                errors.append(f"constraint {index}: invalid linear sense or rhs")
            coefficients = row.get("coefficients")
            if not isinstance(coefficients, dict) or not coefficients:
                errors.append(f"constraint {index}: coefficients must be a nonempty object")
            else:
                for name, coefficient in coefficients.items():
                    if name not in name_set or not is_int(coefficient):
                        errors.append(f"constraint {index}: coefficient for {name!r} is unresolved or noninteger")
        elif kind in {"all_different", "exactly_one"}:
            refs = row.get("variables")
            if not isinstance(refs, list) or len(refs) < 2 or not set(refs).issubset(name_set):
                errors.append(f"constraint {index}: unresolved {kind} variables")
            if kind == "exactly_one" and any(kinds.get(ref) != "boolean" for ref in refs or []):
                errors.append(f"constraint {index}: exactly_one requires Boolean variables")
        elif kind == "precedence":
            if row.get("first_end") not in name_set or row.get("second_start") not in name_set:
                errors.append(f"constraint {index}: unresolved precedence endpoint")
        elif kind == "no_overlap":
            refs = row.get("intervals")
            if not isinstance(refs, list) or len(refs) < 2 or not set(refs).issubset(interval_set):
                errors.append(f"constraint {index}: unresolved no_overlap intervals")
        elif kind == "max_equality":
            refs = row.get("variables")
            if row.get("target") not in name_set or not isinstance(refs, list) or not refs or not set(refs).issubset(name_set):
                errors.append(f"constraint {index}: unresolved max_equality variables")
        else:
            errors.append(f"constraint {index}: unsupported type {kind!r}")
    return errors


def safe_stat(solver: Any, name: str) -> Any:
    value = getattr(solver, name, None)
    if callable(value):
        try:
            return value()
        except TypeError:
            return None
    return value


def execute_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    from ortools.sat.python import cp_model

    enumerate_all = bool(fixture.get("enumerate_all_solutions", False))
    validation_errors = validate_model(fixture["model"], enumerate_all)
    if validation_errors:
        return {
            "canonical_status": "invalid_input",
            "provider_solver_invoked": False,
            "provider_validator_invoked": False,
            "refusal_reasons": validation_errors,
        }

    canonical = fixture["model"]
    model = cp_model.CpModel()
    variables: dict[str, Any] = {}
    for row in canonical["variables"]:
        if row["kind"] == "boolean":
            variables[row["name"]] = model.new_bool_var(row["name"])
        else:
            variables[row["name"]] = model.new_int_var(row["lower"], row["upper"], row["name"])

    intervals: dict[str, Any] = {}
    for row in canonical["intervals"]:
        intervals[row["name"]] = model.new_interval_var(
            variables[row["start"]], row["duration"], variables[row["end"]], row["name"]
        )

    for row in canonical["constraints"]:
        kind = row["type"]
        if kind == "linear":
            expression = sum(coefficient * variables[name] for name, coefficient in row["coefficients"].items())
            if row["sense"] == "<=":
                model.add(expression <= row["rhs"])
            elif row["sense"] == ">=":
                model.add(expression >= row["rhs"])
            else:
                model.add(expression == row["rhs"])
        elif kind == "all_different":
            model.add_all_different([variables[name] for name in row["variables"]])
        elif kind == "exactly_one":
            model.add_exactly_one([variables[name] for name in row["variables"]])
        elif kind == "precedence":
            model.add(variables[row["first_end"]] <= variables[row["second_start"]])
        elif kind == "no_overlap":
            model.add_no_overlap([intervals[name] for name in row["intervals"]])
        elif kind == "max_equality":
            model.add_max_equality(variables[row["target"]], [variables[name] for name in row["variables"]])

    objective = canonical["objective"]
    if objective is not None:
        expression = sum(coefficient * variables[name] for name, coefficient in objective["coefficients"].items())
        if objective["sense"] == "maximize":
            model.maximize(expression)
        else:
            model.minimize(expression)

    provider_validation = model.validate()
    if provider_validation:
        return {
            "canonical_status": "model_invalid",
            "provider_model_validation": provider_validation,
            "provider_solver_invoked": False,
            "provider_validator_invoked": True,
        }

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 1729
    solver.parameters.log_search_progress = False
    # A callback alone observes solutions but does not request exhaustive search.
    # The enumeration intent must be carried into the provider parameter surface.
    solver.parameters.enumerate_all_solutions = enumerate_all
    for name, value in fixture.get("parameters", {}).items():
        setattr(solver.parameters, name, value)

    class Collector(cp_model.CpSolverSolutionCallback):
        def __init__(self) -> None:
            super().__init__()
            self.count = 0
            self.assignments: list[dict[str, int]] = []

        def on_solution_callback(self) -> None:
            self.count += 1
            self.assignments.append({name: self.value(variable) for name, variable in variables.items()})

    collector = Collector() if enumerate_all else None
    raw_status = solver.solve(model, collector) if collector else solver.solve(model)
    raw_names = {
        cp_model.UNKNOWN: "UNKNOWN",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.OPTIMAL: "OPTIMAL",
    }
    raw_name = raw_names.get(raw_status, f"UNRECOGNIZED_{raw_status}")
    canonical_status = {
        "UNKNOWN": "unknown",
        "MODEL_INVALID": "model_invalid",
        "FEASIBLE": "feasible",
        "INFEASIBLE": "infeasible",
        "OPTIMAL": "optimal",
    }.get(raw_name, "provider_failure")
    has_solution = raw_name in {"FEASIBLE", "OPTIMAL"}
    solution = {name: solver.value(variable) for name, variable in variables.items()} if has_solution else None
    return {
        "best_objective_bound": solver.best_objective_bound if objective is not None and has_solution else None,
        "canonical_status": canonical_status,
        "num_booleans": safe_stat(solver, "num_booleans"),
        "num_branches": safe_stat(solver, "num_branches"),
        "num_conflicts": safe_stat(solver, "num_conflicts"),
        "objective": solver.objective_value if objective is not None and has_solution else None,
        "provider_solver_invoked": True,
        "provider_validator_invoked": True,
        "raw_status": raw_name,
        "response_stats": solver.response_stats(),
        "solution": solution,
        "solution_count": collector.count if collector else None,
        "solutions": collector.assignments if collector else None,
        "wall_time": safe_stat(solver, "wall_time"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    provider = protocol["provider"]
    observed_versions = {
        pin.split("==", 1)[0]: importlib.metadata.version(pin.split("==", 1)[0])
        for pin in provider["declared_dependency_lock"]
    }
    expected_versions = {
        pin.split("==", 1)[0]: pin.split("==", 1)[1]
        for pin in provider["declared_dependency_lock"]
    }
    if observed_versions != expected_versions:
        raise SystemExit(f"dependency identity mismatch: {observed_versions!r} != {expected_versions!r}")

    artifact_digest, artifact_members = distribution_digest(provider["package"])
    environment = {
        "machine": platform.machine(),
        "platform": platform.platform(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
    }
    output = {
        "adapter": provider["adapter"],
        "adapter_digest": "sha256:" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "artifact_digest": artifact_digest,
        "artifact_member_count": len(artifact_members),
        "artifact_native_members": [row for row in artifact_members if row["path"].endswith((".so", ".dylib", ".dll", ".pyd"))],
        "dependency_lock": provider["declared_dependency_lock"],
        "dependency_lock_digest": digest(provider["declared_dependency_lock"]),
        "environment": environment,
        "environment_digest": digest(environment),
        "exact_offer_id": provider["exact_offer_id"],
        "provider_id": provider["provider_id"],
        "provider_version": observed_versions[provider["package"]],
        "record_kind": "provider_execution_result",
        "results": [
            {"expected": fixture["expected"], "fixture_id": fixture["fixture_id"], "result": execute_fixture(fixture)}
            for fixture in protocol["fixtures"]
        ],
        "target_occurrence": (
            "target.occurrence.cpsat.local."
            f"{environment['platform'].lower().replace(' ', '_')}."
            f"python{environment['python_version'].replace('.', '_')}.isolated"
        ),
    }
    json.dump(output, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
