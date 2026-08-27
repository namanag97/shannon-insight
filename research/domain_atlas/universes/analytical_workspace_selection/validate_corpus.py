#!/usr/bin/env python3
"""Validate analytical-workspace and selection corpus invariants and drift."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / name).read_text().splitlines() if line.strip()]


def main() -> None:
    before = {p.name: p.read_bytes() for p in ROOT.glob("*.json*")}
    result = subprocess.run([sys.executable, str(ROOT / "build_corpus.py")], capture_output=True, text=True, check=True)
    after = {p.name: p.read_bytes() for p in ROOT.glob("*.json*")}
    assert before == after, "generated outputs drifted; rerun build_corpus.py"
    sources, contexts, decisions = rows("sources.jsonl"), rows("bounded-contexts.jsonl"), rows("decision-points.jsonl")
    libraries, lenses, negatives = rows("library-contracts.jsonl"), rows("boundary-lens-adjudication.jsonl"), rows("negative-twins.jsonl")
    assert len(sources) >= 20 and len(contexts) == 5 and len(libraries) == 5 and len(lenses) == 12 and len(negatives) >= 35
    assert len(decisions) >= 95 and all(d["default"] is None and d["default_law"] == "forbidden" for d in decisions)
    ids = {l["library_id"] for l in libraries}
    assert ids == {"library.analytical_workspace.definition.compiler", "library.analytical_workspace.lifecycle.reducer", "library.selection.predicate.compiler", "library.selection.state.reducer", "library.selection.facet.evaluator"}
    assert all(l["qualification_required"] is False and l["effect_boundary"] == "pure_no_io" for l in libraries)
    assert all(any("model" in law.lower() or "agent" in law.lower() for law in l["laws"]) for l in libraries)
    print(result.stdout.strip())
    print(f"VALIDATION PASS aws: {sum(len(l['operations']) for l in libraries)} operations; no qualified implementations")


if __name__ == "__main__":
    main()
