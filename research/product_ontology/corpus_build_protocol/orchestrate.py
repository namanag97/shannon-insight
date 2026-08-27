#!/usr/bin/env python3
"""Plan, verify or execute explicitly contracted corpus packages.

Execution is intentionally unavailable for inferred legacy candidates.  A clean
worktree is required so write-boundary enforcement can be exact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load_contracts() -> dict[str, dict]:
    rows = [json.loads(line) for line in (HERE / "package-contracts.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return {row["package_id"]: row for row in rows}


def selected_plan(target: str, contracts: dict[str, dict]) -> list[dict]:
    if target not in contracts:
        raise SystemExit(f"unknown or uncontracted target: {target}")
    selected: set[str] = set()

    def visit(package_id: str) -> None:
        if package_id in selected:
            return
        for dep in contracts[package_id]["dependency_refs"]:
            visit(dep)
        selected.add(package_id)

    visit(target)
    return sorted((contracts[key] for key in selected), key=lambda row: row["topological_order"])


def run(command: list[str]) -> str:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise SystemExit(f"command failed ({' '.join(command)}):\n{completed.stdout}{completed.stderr}")
    return completed.stdout.strip()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc")):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def dirty_paths() -> set[str]:
    output = run(["git", "status", "--porcelain=v1", "--untracked-files=all"])
    paths = set()
    for line in output.splitlines():
        raw = line[3:]
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.add(raw)
    return paths


def validate_package(row: dict) -> list[str]:
    return [run(command) for command in row["validate_commands"]]


def build_package_twice(row: dict) -> dict:
    if not row["execution_enabled"]:
        raise SystemExit(f"execution refused for not-yet-enabled contract: {row['package_id']}")
    if row["package_kind"] in {"authored_source", "historical_snapshot", "execution_campaign"}:
        raise SystemExit(f"automatic regeneration prohibited for {row['package_kind']}: {row['package_id']}")
    if not row["build_commands"]:
        return {"package_id": row["package_id"], "builds": 0, "stable": True, "validation": validate_package(row)}
    root = ROOT / row["root"]
    first_output = [run(command) for command in row["build_commands"]]
    first_digest = tree_digest(root)
    second_output = [run(command) for command in row["build_commands"]]
    second_digest = tree_digest(root)
    if first_digest != second_digest:
        raise SystemExit(f"non-deterministic package projection: {row['package_id']}")
    return {
        "package_id": row["package_id"],
        "builds": 2,
        "stable": True,
        "tree_sha256": second_digest,
        "build_output": second_output or first_output,
        "validation": validate_package(row),
    }


def execute(plan: list[dict]) -> dict:
    before = dirty_paths()
    if before:
        raise SystemExit("execution requires a clean worktree; commit or discard current changes first")
    receipts = [build_package_twice(row) for row in plan]
    after = dirty_paths()
    allowed_roots = tuple(row["root"].rstrip("/") + "/" for row in plan if row["write_policy"] != "read_only")
    violations = sorted(path for path in after if not path.startswith(allowed_roots))
    if violations:
        raise SystemExit("undeclared write boundary crossed:\n" + "\n".join(violations))
    return {
        "record_kind": "ephemeral_corpus_build_execution_receipt",
        "packages": receipts,
        "changed_paths": sorted(after),
        "write_boundary_violations": [],
        "qualification_claim": False,
        "ratification_claim": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "verify", "execute"))
    parser.add_argument("target", help="exact package.* contract ID")
    args = parser.parse_args()
    contracts = load_contracts()
    plan = selected_plan(args.target, contracts)
    if args.mode == "plan":
        print(json.dumps({"target": args.target, "plan": [row["package_id"] for row in plan]}, indent=2))
        return 0
    if args.mode == "verify":
        results = [{"package_id": row["package_id"], "validation": validate_package(row)} for row in plan]
        print(json.dumps({"target": args.target, "verification": results, "completion_claim": False}, indent=2))
        return 0
    print(json.dumps(execute(plan), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

