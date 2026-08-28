#!/usr/bin/env python3
"""Build a digest-bound manifest for the Python placement corpus."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "manifest.json"

SOURCE_MODELS = [
    "build_shannon_python_placement.py",
    "build_shannon_python_extraction_frontier.py",
    "build_shannon_codebase_intelligence_ddd.py",
]
VALIDATORS = [
    "validate_shannon_python_placement.py",
    "validate_shannon_python_schemas.py",
    "validate_shannon_python_extraction_frontier.py",
    "validate_shannon_codebase_intelligence_ddd.py",
]
SCHEMAS = [
    "shannon-python-placement.schema.json",
    "shannon-python-module-crosswalk.schema.json",
]
GENERATED = [
    "shannon-python-placement.json",
    "shannon-python-module-crosswalk.jsonl",
    "summary.json",
    "shannon-python-extraction-candidates.jsonl",
    "shannon-python-extraction-summary.json",
    "shannon-codebase-intelligence-ddd.json",
    "shannon-codebase-intelligence-ddd-summary.json",
]


def sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def file_record(name: str, role: str) -> dict[str, Any]:
    path = HERE / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return {
        "path": str(path.relative_to(ROOT)),
        "role": role,
        "sha256": sha256(path),
        "byte_count": path.stat().st_size,
    }


def main() -> int:
    placement = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    extraction = json.loads(
        (HERE / "shannon-python-extraction-summary.json").read_text(encoding="utf-8")
    )
    ddd = json.loads(
        (HERE / "shannon-codebase-intelligence-ddd-summary.json").read_text(
            encoding="utf-8"
        )
    )
    files = [file_record(name, "source_model") for name in SOURCE_MODELS]
    files += [file_record(name, "validator") for name in VALIDATORS]
    files += [file_record(name, "schema") for name in SCHEMAS]
    files += [file_record(name, "generated_artifact") for name in GENERATED]
    manifest = {
        "schema_version": "1.0.0",
        "manifest_id": "shannon_python_implementation_placement",
        "application_product_id": "application_product.software_engineering.codebase_intelligence",
        "implementation_id": "implementation.shannon_python.codebase_insight",
        "dependency_order": [
            "Python source tree",
            "module placement projection",
            "application-product DDD",
            "reusable extraction frontier",
            "qualification and vertical-acceptance programs",
        ],
        "projection_links": {
            "placement_digest": placement["projection_digest"],
            "ddd_digest": ddd["ddd_digest"],
            "candidate_count": extraction["candidate_count"],
            "bound_exact_contract_count": extraction[
                "candidates_with_bound_exact_contract"
            ],
            "qualified_candidate_count": extraction["qualified_candidate_count"],
        },
        "files": sorted(files, key=lambda row: row["path"]),
        "claims": {
            "application_boundary_structurally_modeled": True,
            "module_placement_total_for_current_source_tree": True,
            "extraction_candidates_exact_source_scoped": True,
            "semantic_ratified": False,
            "implementation_qualified": False,
            "portable_offer": False,
            "executed_vertical_acceptance": False,
            "build_ready": False,
            "product_ratified": False,
            "overall_completion": False,
        },
    }
    material = json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    manifest["manifest_digest"] = f"sha256:{hashlib.sha256(material).hexdigest()}"
    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "manifest_id": manifest["manifest_id"],
                "file_count": len(files),
                "candidate_count": extraction["candidate_count"],
                "manifest_digest": manifest["manifest_digest"],
                "completion_claim": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
