#!/usr/bin/env python3
"""Dependency-free structural and constitutional validator."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_jsonl(name: str) -> list[dict]:
    rows = [json.loads(line) for line in (ROOT / name).read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids)), f"duplicate ID in {name}"
    assert ids == sorted(ids), f"non-canonical order in {name}"
    return rows


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    metamodel = json.loads((ROOT / "architecture-metamodel.json").read_text(encoding="utf-8"))
    files = {
        "sources": "sources.jsonl", "contexts": "contexts.jsonl", "capabilities": "capabilities.jsonl",
        "operations": "operations.jsonl", "decisions": "decision-points.jsonl", "laws": "laws.jsonl",
        "components": "components.jsonl", "ports": "ports.jsonl", "persistence": "persistence-schema-candidates.jsonl",
        "passes": "algorithm-pass-mappings.jsonl", "requirements": "requirements.jsonl", "offers": "offers.jsonl",
        "libraries": "library-boundaries.jsonl", "rust": "rust-applicability.jsonl", "diagnostics": "diagnostics.jsonl",
        "performance": "performance-resource-model.jsonl", "threats": "threat-model.jsonl",
        "innovations": "innovations-2021-2026.jsonl", "examples": "prototype-traces.jsonl",
        "comparisons": "system-comparisons.jsonl", "gaps": "gaps.jsonl",
        "apis": "api-contracts.jsonl", "tests": "conformance-tests.jsonl",
    }
    rows = {key: load_jsonl(filename) for key, filename in files.items()}
    all_ids = {row["id"] for values in rows.values() for row in values}
    source_ids = {row["id"] for row in rows["sources"]}
    context_ids = {row["id"] for row in rows["contexts"]}
    component_ids = {row["id"] for row in rows["components"]}
    requirement_ids = {row["id"] for row in rows["requirements"]}
    library_ids = {row["id"] for row in rows["libraries"]}

    for group, values in rows.items():
        for row in values:
            missing = {"id", "edition", "record_kind", "status"} - row.keys()
            if missing:
                fail(f"schema keys missing in {group}:{missing}")
            if row["edition"] != 1 or not re.fullmatch(r"[a-z][a-z0-9_.-]+", row["id"]):
                fail(f"schema identity violation in {group}:{row.get('id')}")

    thresholds = manifest["thresholds"]
    if len(source_ids) < thresholds["sources"]:
        fail("source threshold")
    if sum(bool(row.get("primary_or_authoritative")) for row in rows["sources"]) < thresholds["sources"]:
        fail("primary/authoritative source threshold")
    if len(context_ids) < thresholds["contexts"]:
        fail("context threshold")
    principal = sum(len(rows[k]) for k in ("capabilities", "operations", "decisions", "laws"))
    if principal < thresholds["principal_records"]:
        fail("principal record threshold")
    if len(library_ids) < thresholds["libraries"]:
        fail("library threshold")
    if len(rows["innovations"]) < thresholds["innovations"]:
        fail("innovation threshold")
    if len(rows["apis"]) < 20 or len(rows["tests"]) < 24:
        fail("API or conformance-test contract threshold")
    if any(not 2021 <= row["year"] <= 2026 or not row["non_llm_core"] for row in rows["innovations"]):
        fail("innovation window or LLM-core violation")

    for group, values in rows.items():
        for row in values:
            for ref in row.get("source_refs", []):
                if ref not in source_ids:
                    fail(f"missing source ref {ref} in {group}:{row['id']}")
            if "context_ref" in row and row["context_ref"] not in context_ids:
                fail(f"missing context ref in {row['id']}")
            if "component_ref" in row and row["component_ref"] not in component_ids:
                fail(f"missing component ref in {row['id']}")
            if "satisfies_requirement_ref" in row and row["satisfies_requirement_ref"] not in requirement_ids:
                fail(f"missing requirement ref in {row['id']}")
            if "library_ref" in row and row["library_ref"] not in library_ids:
                fail(f"missing library ref in {row['id']}")

    if len(rows["components"]) != len(rows["contexts"]):
        fail("one component contract per context required")
    if len(rows["ports"]) != 2 * len(rows["contexts"]):
        fail("input/output port pair per context required")
    if any(row["binding_status"] != "unbound" for row in rows["offers"]):
        fail("research offers must remain unbound")
    if set(metamodel["result_sum_type"]) != {"complete", "partial_with_gaps", "unsat_with_checked_core", "unknown", "refused", "cancelled"}:
        fail("partiality result model changed")
    laws = set(metamodel["constitutional_laws"])
    for required in {
        "unknown meaning fails closed", "no string-based semantic dispatch", "parse != resolve != adjudicate",
        "feasible != preferred != qualified != admitted", "plan != effect authority", "model or agent output is an untrusted proposal",
    }:
        if required not in laws:
            fail(f"missing constitutional law: {required}")

    examples = {row["id"]: row for row in rows["examples"]}
    required_examples = {
        "example.impl.energy-grid-positive", "example.impl.energy-grid-negative-twin",
        "example.impl.bank-sacc-r-positive", "example.impl.bank-sacc-r-negative-twin",
    }
    if not required_examples.issubset(examples):
        fail("positive/negative vertical trace set incomplete")
    if any("agent" not in row["optional_agent_role"] for row in rows["examples"]):
        fail("optional agent seam missing")
    if manifest["completion_claim"] or metamodel["completion_claim"]:
        fail("candidate bundle must not claim completion")
    if not rows["gaps"] or any(row["status"] != "open" for row in rows["gaps"]):
        fail("honest open blockers required")

    for name, expected in manifest["generated_file_sha256"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            fail(f"digest mismatch: {name}")
    if hashlib.sha256((ROOT / "build_bundle.py").read_bytes()).hexdigest() != manifest["generator_sha256"]:
        fail("generator digest mismatch")

    # Regeneration must be byte-identical. The generator writes only within ROOT,
    # so preserve original bytes and compare after a clean deterministic run.
    before = {name: (ROOT / name).read_bytes() for name in [*manifest["generated_file_sha256"], "manifest.json"]}
    subprocess.run([sys.executable, str(ROOT / "build_bundle.py")], cwd=ROOT.parents[3], check=True)
    after = {name: (ROOT / name).read_bytes() for name in before}
    if before != after:
        fail("clean regeneration is not byte-identical")

    print(
        "PASS implementation architecture: "
        f"{len(source_ids)} sources, {len(context_ids)} contexts, {principal} principal records, "
        f"{len(library_ids)} libraries, {len(rows['innovations'])} innovations, {len(rows['gaps'])} blockers"
    )


if __name__ == "__main__":
    main()
