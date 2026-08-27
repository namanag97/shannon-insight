#!/usr/bin/env python3
"""Build deterministic views for collaboration/privacy/resolution/assurance."""

from __future__ import annotations

import importlib.util

from source_model import SOURCE, source_bytes


HERE = SOURCE.parent
SHARED = HERE.parent / "movement" / "build_bundle.py"
SPEC = importlib.util.spec_from_file_location("shared_cpra_builder", SHARED)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load shared builder: {SHARED}")
shared = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shared)
shared.HERE = HERE
shared.SOURCE = SOURCE
shared.SECTIONS = {
    **shared.SECTIONS,
    "binding_maps": ("product_library_binding_map", "binding_map_id"),
    "binding_gaps": ("product_library_binding_gap", "gap_id"),
    "semantic_gaps": ("semantic_or_conformance_gap", "gap_id"),
    "ddd_dossiers": ("product_ddd_dossier", "dossier_id"),
}
shared.OUTPUTS = {
    **shared.OUTPUTS,
    "binding_maps": "product-library-binding-maps.jsonl",
    "binding_gaps": "product-library-binding-gaps.jsonl",
    "semantic_gaps": "semantic-gaps.jsonl",
    "ddd_dossiers": "product-ddd-dossiers.jsonl",
}
OUTPUTS = shared.OUTPUTS
load_source = shared.load_source
materialize = shared.materialize


if __name__ == "__main__":
    expected = source_bytes()
    check = "--check" in __import__("sys").argv
    if check and (not SOURCE.is_file() or SOURCE.read_bytes() != expected):
        raise SystemExit("STALE source.json")
    if not check:
        SOURCE.write_bytes(expected)
    raise SystemExit(shared.main())
