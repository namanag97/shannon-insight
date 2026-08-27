#!/usr/bin/env python3
"""Validate the measurement acquisition and calibration corpus."""

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
    libraries, compiler, negatives = rows("library-contracts.jsonl"), rows("compiler-contracts.jsonl"), rows("negative-twins.jsonl")
    lenses, verdicts = rows("boundary-lens-adjudication.jsonl"), rows("boundary-verdicts.jsonl")
    assert len(sources) >= 20 and len(contexts) == 4 and len(libraries) == 5 and len(lenses) == 12
    assert all(x["default"] is None and x["default_law"] == "forbidden" for x in decisions)
    ids = {x["decision_id"] for x in decisions}
    for lib in libraries:
        assert set(lib["decision_refs"]) <= ids
        assert lib["operations"] and lib["oracles"] and lib["error_contracts"] and lib["must_not_own"]
        assert lib["qualification_required"] is False
    offers = [x for x in compiler if x["record_kind"] == "capability_offer"]
    assert len(offers) == len(libraries) and all(not x["portable"] and not x["selectable"] for x in offers)
    assert len(negatives) >= 30 and len(verdicts) >= 3
    print(f"VALIDATION PASS measurement: {len(libraries)} libraries, {len(decisions)} no-default decisions, {sum(len(x['operations']) for x in libraries)} pure operations, {len(lenses)} lenses, {len(negatives)} negative twins, 0 qualified offers")


if __name__ == "__main__":
    main()
