#!/usr/bin/env python3
"""Build governance-semantics adjudication views using the shared deterministic projection."""

from __future__ import annotations

import importlib.util
import argparse
from pathlib import Path


HERE = Path(__file__).resolve().parent
SHARED = HERE.parent / "movement" / "build_bundle.py"
SPEC = importlib.util.spec_from_file_location("shared_adjudication_builder", SHARED)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load shared builder: {SHARED}")
shared = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shared)
shared.HERE = HERE
shared.SOURCE = HERE / "source.json"

SECTIONS = {
    **shared.SECTIONS,
    "binding_maps": ("product_library_binding_map", "binding_map_id"),
    "binding_gaps": ("product_library_binding_gap", "gap_id"),
    "ddd_dossiers": ("product_ddd_dossier", "dossier_id"),
}
OUTPUTS = {
    **shared.OUTPUTS,
    "binding_maps": "product-library-binding-maps.jsonl",
    "binding_gaps": "product-library-binding-gaps.jsonl",
    "ddd_dossiers": "product-ddd-dossiers.jsonl",
}
load_source = shared.load_source


def materialize(source):
    return shared._materialize(source, SECTIONS, OUTPUTS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payloads, manifest = materialize(load_source())
    changed = []
    for filename, data in sorted(payloads.items()):
        path = HERE / filename
        if not path.exists() or path.read_bytes() != data:
            changed.append(filename)
            if not args.check:
                path.write_bytes(data)
    if args.check and changed:
        print("STALE generated files: " + ", ".join(changed))
        return 1
    print(shared.canonical_json({"counts": manifest["counts"], "derived": manifest["derived"], "status": "PASS"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
