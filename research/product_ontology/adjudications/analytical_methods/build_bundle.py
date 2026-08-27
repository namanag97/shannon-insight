#!/usr/bin/env python3
"""Build analytical-method adjudication views using the shared deterministic projection."""

from __future__ import annotations

import importlib.util
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

# This adjudication also closes its abstract product-facing library groups over
# concrete compiler registries.  Keep these records local to this bundle; the
# shared builder module is loaded under a private module identity for this run.
shared.SECTIONS = {
    **shared.SECTIONS,
    "binding_maps": ("product_library_binding_map", "binding_map_id"),
    "binding_gaps": ("product_library_binding_gap", "gap_id"),
    "ddd_dossiers": ("product_ddd_dossier", "dossier_id"),
}
shared.OUTPUTS = {
    **shared.OUTPUTS,
    "binding_maps": "product-library-binding-maps.jsonl",
    "binding_gaps": "product-library-binding-gaps.jsonl",
    "ddd_dossiers": "product-ddd-dossiers.jsonl",
}

OUTPUTS = shared.OUTPUTS
SECTIONS = shared.SECTIONS
load_source = shared.load_source
materialize = shared.materialize


if __name__ == "__main__":
    raise SystemExit(shared.main())
