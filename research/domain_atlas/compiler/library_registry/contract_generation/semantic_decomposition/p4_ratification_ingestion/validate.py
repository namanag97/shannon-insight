#!/usr/bin/env python3
"""Validate fail-closed P4 receipt ingestion and non-mutating lowering."""
from __future__ import annotations

import collections
import hashlib
import json

from build_p4 import HERE, P1B_TEMPLATES, P2_TEMPLATES, P3_TEMPLATES, P5_TEMPLATES, load_jsonl, outputs, template_ref


def main() -> int:
    expected = outputs()
    for name, text in expected.items():
        path = HERE / name
        assert path.is_file() and path.read_text() == text, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    assert manifest["completion_claim"] is False
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"], name

    summary = json.loads((HERE / "summary.json").read_text())
    ledger = load_jsonl(HERE / "verified-ratification-ledger.jsonl")
    refusals = load_jsonl(HERE / "receipt-refusals.jsonl")
    deltas = load_jsonl(HERE / "canonical-delta-candidates.jsonl")
    blocked = load_jsonl(HERE / "unratified-template-index.jsonl")
    p2 = load_jsonl(P2_TEMPLATES)
    p3 = load_jsonl(P3_TEMPLATES)
    p5 = load_jsonl(P5_TEMPLATES)
    p1b = load_jsonl(P1B_TEMPLATES)
    templates = {template_ref(row): row for row in p1b + p2 + p3 + p5}

    assert summary["total_templates"] == len(templates) == 1904
    assert summary["submitted_ratification_receipts"] == 0
    assert summary["authority_verification_receipts"] == 0
    assert summary["verified_ratifications"] == len(ledger) == 0
    assert summary["receipt_refusals"] == len(refusals) == 0
    assert summary["canonical_delta_candidates"] == len(deltas) == 0
    assert summary["unratified_templates"] == len(blocked) == 1904
    assert summary["canonical_mutations_allowed"] == summary["canonical_exact_gaps_closed"] == 0
    assert not summary["completion_claim"]

    for claim in summary["input_snapshot"]["files"]:
        path = HERE.parents[6] / claim["path"]
        data = path.read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]
        assert len(load_jsonl(path)) == claim["record_count"]

    assert len({row["template_ref"] for row in blocked}) == len(blocked)
    assert {row["template_ref"] for row in blocked} == set(templates)
    assert collections.Counter(row["template_kind"] for row in blocked) == {
        "P2_SYMBOL_OWNER": 210,
        "P3_FAMILY_AXIS_APPLICABILITY": 368,
        "P5_EXACT_LIBRARY_CONTRACT": 674,
        "P1B_SOURCE_AUTHORITY": 23,
        "P1B_CROSS_OWNER_COLLISION": 146,
        "P1B_BOUNDED_CONTEXT_BOUNDARY": 460,
        "P1B_FAMILY_CONSTITUTION": 23,
    }
    assert collections.Counter(row["blocker"] for row in blocked) == {
        "NO_VERIFIED_RATIFICATION_RECEIPT": 877,
        "UPSTREAM_TEMPLATE_BLOCKED": 1027,
    }
    for row in blocked:
        template = templates[row["template_ref"]]
        expected_blocker = "UPSTREAM_TEMPLATE_BLOCKED" if template["status"] != "READY_FOR_NAMED_AUTHORITY_REVIEW" else "NO_VERIFIED_RATIFICATION_RECEIPT"
        assert row["upstream_status"] == template["status"]
        assert row["blocker"] == expected_blocker
        assert not row["canonical_mutation_allowed"] and row["canonical_gaps_closed"] == 0
        assert not row["completion_claim"]

    print("PASS P4 ratification ingestion: 1,904 exact templates; 877 await verified receipts and 1,027 remain upstream-blocked; 0 verified ratifications, delta candidates, canonical mutations or gaps closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
