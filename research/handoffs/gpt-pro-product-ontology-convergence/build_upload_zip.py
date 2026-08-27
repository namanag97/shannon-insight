#!/usr/bin/env python3
"""Build the deterministic GPT Pro appraisal upload from the current repository state."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "GPT-PRO-PRODUCT-ONTOLOGY-CONVERGENCE-2026-08-27.zip"
FIXED_TIME = (2026, 8, 27, 0, 0, 0)

TREES = [
    ROOT / "research/product_ontology",
    ROOT / "research/domain_atlas/universes",
    ROOT / "research/domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition",
    ROOT / "research/handoffs/gpt-pro-product-ontology-convergence",
]
FILES = [
    path for path in (ROOT / "research/domain_atlas/compiler/library_registry").iterdir()
    if path.is_file()
] + [
    ROOT / "research/domain_atlas/ecosystem/specialists/README.md",
    ROOT / "research/domain_atlas/ecosystem/specialists/inclusion-policy.json",
    ROOT / "research/domain_atlas/ecosystem/specialists/all-experts-registry.jsonl",
    ROOT / "research/domain_atlas/ecosystem/specialists/all-specialist-companies-registry.jsonl",
    ROOT / "research/domain_atlas/ecosystem/specialists/consolidated-registry-summary.json",
]

EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".zip"}


def eligible(path: Path) -> bool:
    return not (set(path.parts) & EXCLUDED_PARTS) and path.suffix not in EXCLUDED_SUFFIXES


def inputs() -> list[Path]:
    paths = set(path for path in FILES if path.exists() and eligible(path))
    for tree in TREES:
        paths.update(path for path in tree.rglob("*") if path.is_file() and eligible(path))
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def main():
    selected = inputs()
    inventory = []
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in selected:
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            info = zipfile.ZipInfo(relative, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
            inventory.append({"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        payload = (json.dumps({
            "archive_role": "GPT Pro independent appraisal and convergence research input",
            "file_count": len(inventory),
            "files": inventory,
        }, indent=2, sort_keys=True) + "\n").encode()
        info = zipfile.ZipInfo("UPLOAD-INVENTORY.json", FIXED_TIME)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(json.dumps({
        "output": str(OUTPUT),
        "files": len(inventory) + 1,
        "bytes": OUTPUT.stat().st_size,
        "sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    }, indent=2))


if __name__ == "__main__":
    main()
