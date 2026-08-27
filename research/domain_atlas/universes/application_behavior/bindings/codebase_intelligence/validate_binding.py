#!/usr/bin/env python3
"""Fail-closed validation for the code-intelligence application binding."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - fail-closed environment guard
    raise SystemExit("jsonschema is required; refusing schema-less binding validation") from exc

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique(rows: list[dict[str, Any]], key: str) -> None:
    values = [row[key] for row in rows]
    if len(values) != len(set(values)):
        raise AssertionError(f"duplicate {key}")


def validate_definition(schema: dict[str, Any], definition: str, instance: Any) -> None:
    wrapper = {
        "$schema": schema["$schema"],
        "$id": schema["$id"] + f"#{definition}",
        "$defs": schema["$defs"],
        "$ref": f"#/$defs/{definition}",
    }
    jsonschema.validate(instance, wrapper)


def main() -> int:
    result = subprocess.run([sys.executable, str(HERE / "build_binding.py"), "--check"], cwd=HERE, capture_output=True, text=True, check=False)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)

    schema = load_json(HERE / "binding.schema.json")
    product = load_json(HERE / "product-binding.json")
    components = load_jsonl(HERE / "component-bindings.jsonl")
    libraries = load_jsonl(HERE / "library-bindings.jsonl")
    research = load_jsonl(HERE / "research-python-roles.jsonl")
    evidence = load_jsonl(HERE / "evidence.jsonl")
    summary = load_json(HERE / "summary.json")
    manifest = load_json(HERE / "manifest.json")

    validate_definition(schema, "product", product)
    for row in components:
        validate_definition(schema, "component", row)
    for row in libraries:
        validate_definition(schema, "library", row)
    for row in research:
        validate_definition(schema, "researchPython", row)
    for row in evidence:
        validate_definition(schema, "evidence", row)

    unique(components, "component_id")
    unique(components, "path")
    unique(libraries, "library_id")
    unique(research, "path")
    unique(evidence, "evidence_id")

    actual_components = {f"src/shannon_insight/{path.name}" for path in (ROOT / "src" / "shannon_insight").iterdir() if path.name != "__pycache__"}
    bound_components = {row["path"] for row in components}
    assert actual_components == bound_components, f"component drift: missing={sorted(actual_components-bound_components)}, stale={sorted(bound_components-actual_components)}"

    actual_research = {path.relative_to(ROOT).as_posix() for path in (ROOT / "research").rglob("*.py")}
    bound_research = {row["path"] for row in research}
    assert actual_research == bound_research, f"research Python drift: missing={len(actual_research-bound_research)}, stale={len(bound_research-actual_research)}"

    artifact_names = [row["artifact"] for row in product["owned_artifacts"]]
    assert len(artifact_names) == len(set(artifact_names)), "durable artifact has duplicate ownership row"
    assert all(row["owner"] == product["product_id"] for row in product["owned_artifacts"])
    assert all(value is False for value in product["qualification"].values())
    assert all(row["completion_claim"] is False for row in components + libraries + research)
    assert all(row["semantic_authority"] is False for row in research)
    assert all(row["production_runtime"] is False for row in research)
    assert not any(row["semantic_owner"] == product["product_id"] for row in components if row["ownership_kind"] in {"method_implementation", "infrastructure_adapter", "application_runtime", "implementation_support", "implementation_packaging"})

    prohibited_promotions = ("universal data-and-analytics platform", "qualified implementation", "build-ready product", "ratified product")
    serialized = json.dumps({"product": product, "components": components, "research": research}).lower()
    for phrase in prohibited_promotions:
        if phrase in serialized and phrase not in " ".join(product["negative_charter"]).lower():
            raise AssertionError(f"prohibited promotion phrase outside negative charter: {phrase}")

    assert summary["top_level_component_count"] == len(components)
    assert summary["classified_top_level_component_count"] == len(components)
    assert summary["unclassified_top_level_component_count"] == 0
    assert summary["library_binding_count"] == len(libraries)
    assert summary["research_python_file_count"] == len(research)
    assert summary["python_semantic_authority_count"] == 0
    assert summary["qualified_implementation_count"] == 0
    assert summary["build_ready_product_count"] == 0
    assert summary["ratified_product_count"] == 0

    for name, metadata in manifest["files"].items():
        assert sha256(HERE / name) == metadata["sha256"], f"manifest digest mismatch: {name}"
    assert sha256(HERE / "source_model.py") == manifest["inputs"]["source_model.py"]
    assert sha256(ROOT / product["parent_semantic_authority"] / "manifest.json") == manifest["inputs"]["parent_manifest.json"]
    assert sha256(ROOT / "pyproject.toml") == manifest["inputs"]["pyproject.toml"]

    print(json.dumps({"status": "PASS", "components": len(components), "libraries": len(libraries), "research_python_files": len(research), "qualification_promotions": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
