#!/usr/bin/env python3
"""Validate governed executable-recipe artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict]:
    return [json.loads(x) for x in (ROOT / name).read_text(encoding="utf-8").splitlines() if x]


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    for name, meta in manifest["files"].items():
        payload = (ROOT / name).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == meta["sha256"], name
        assert len([x for x in payload.splitlines() if x]) == meta["records"], name
    sources, contexts, decisions = rows("sources.jsonl"), rows("bounded-contexts.jsonl"), rows("decision-points.jsonl")
    libraries, compiler = rows("library-contracts.jsonl"), rows("compiler-contracts.jsonl")
    negatives, lenses, verdicts = rows("negative-twins.jsonl"), rows("boundary-lens-adjudication.jsonl"), rows("boundary-verdicts.jsonl")
    assert len(sources) >= 24 and len(contexts) == 5 and len(libraries) == 6 and len(lenses) == 12
    assert all(x["default"] is None and x["default_law"] == "forbidden" for x in decisions)
    decision_ids = {x["decision_id"] for x in decisions}
    for library in libraries:
        assert set(library["decision_refs"]) <= decision_ids
        assert library["operations"] and library["oracles"] and library["error_contracts"] and library["must_not_own"]
        assert library["qualification_required"] is False
    offers = [x for x in compiler if x["record_kind"] == "capability_offer"]
    assert len(offers) == len(libraries) and all(not x["portable"] and not x["selectable"] for x in offers)
    assert len(negatives) >= 36 and len(verdicts) == 3
    print(f"VALIDATION PASS recipe: {len(libraries)} libraries, {len(decisions)} no-default decisions, {sum(len(x['operations']) for x in libraries)} pure operations, {len(lenses)} lenses, {len(negatives)} negative twins, 0 qualified offers")


if __name__ == "__main__":
    main()
