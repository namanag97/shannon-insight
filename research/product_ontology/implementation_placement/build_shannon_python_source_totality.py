#!/usr/bin/env python3
"""Prove every Python source file is placed or explicitly excluded."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SRC = ROOT / "src" / "shannon_insight"
CROSSWALK = HERE / "shannon-python-module-crosswalk.jsonl"
OUTPUT = HERE / "shannon-python-source-totality.json"

ALLOWED_EXCLUSIONS = {
    "src/shannon_insight/__init__.py": {
        "disposition": "PACKAGE_FACADE_OWNED_BY_APPLICATION_ROOT",
        "owner": "application_product.software_engineering.codebase_intelligence",
        "reason": "The package façade exports application identity/API symbols but is not an independently owned implementation module or reusable library scope.",
    }
}


def sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def main() -> int:
    rows = [
        json.loads(line)
        for line in CROSSWALK.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    represented = {
        source["path"] for row in rows for source in row.get("source_files", [])
    }
    actual = {
        str(path.relative_to(ROOT))
        for path in SRC.rglob("*.py")
        if "__pycache__" not in path.parts
    }
    excluded_paths = actual - represented
    exclusions = []
    for relative in sorted(excluded_paths):
        rule = ALLOWED_EXCLUSIONS.get(relative)
        if rule is None:
            continue
        exclusions.append(
            {
                "path": relative,
                "sha256": sha256(ROOT / relative),
                **rule,
                "semantic_authority": False,
                "implementation_qualified": False,
            }
        )
    classified = represented | {row["path"] for row in exclusions}
    output = {
        "report_id": "shannon_python_source_totality",
        "source_root": "src/shannon_insight",
        "actual_python_source_file_count": len(actual),
        "module_crosswalk_source_file_count": len(represented),
        "explicit_exclusion_count": len(exclusions),
        "explicit_exclusions": exclusions,
        "unclassified_source_files": sorted(actual - classified),
        "stale_crosswalk_source_files": sorted(represented - actual),
        "status": (
            "TOTAL_WITH_EXPLICIT_PACKAGE_FACADE_EXCLUSION"
            if actual == classified and not (represented - actual)
            else "INCOMPLETE"
        ),
        "completion_claim": False,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
