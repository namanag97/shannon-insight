#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "generated"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    required = {
        "effective-gap-resolutions.jsonl",
        "fixed-point-new-gap-resolutions.jsonl",
        "downstream-revalidation.jsonl",
        "summary.json",
        "manifest.json",
    }
    missing = sorted(name for name in required if not (OUT / name).is_file())
    if missing:
        raise SystemExit(f"missing generated fixed-point outputs: {missing}")

    gaps = load_jsonl(OUT / "effective-gap-resolutions.jsonl")
    new_gaps = load_jsonl(OUT / "fixed-point-new-gap-resolutions.jsonl")
    downstream = load_jsonl(OUT / "downstream-revalidation.jsonl")
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))

    assert len(gaps) == 625
    assert sum(int(row["original_atom_count"]) for row in gaps) == 14_496
    assert len(new_gaps) == summary["new_research_gaps_discovered"] == summary["new_research_gaps_with_effective_resolution"]
    assert summary["p01_families_audited"] == 23
    assert summary["effective_research_vacancies"] == 0
    assert summary["canonical_gaps_closed"] == 0
    assert summary["ratified_decisions"] == 0
    assert summary["invented_implementations"] == 0
    assert summary["invented_qualifications"] == 0
    assert summary["invented_vertical_acceptances"] == 0
    assert summary["completion_claim"] is False
    assert all(row["fixed_point_status"] == "RESEARCH_RESOLVED_TO_PROPOSED_UNRATIFIED_DECISIONS" for row in gaps)
    assert all(row["fixed_point_research_vacancy"] is False for row in gaps)
    assert all(row["fixed_point_completion_claim"] is False for row in gaps)
    assert all(row["fixed_point_status"] == "RESEARCH_RESOLVED_PROPOSED_UNRATIFIED" for row in new_gaps)
    assert all(row["fixed_point_research_vacancy"] is False for row in new_gaps)
    assert all(row["completion_claim"] is False for row in new_gaps)
    assert all(row["fixed_point_completion_claim"] is False for row in downstream)
    assert all(row["fixed_point_ratification_state"] == "PROPOSED_UNRATIFIED_RESEARCH_DECISION" for row in downstream)
    assert {row["fixed_point_revalidation"] for row in downstream} <= {
        "REVALIDATED_WITH_SEMANTIC_MIGRATION",
        "REVALIDATED_WITH_AUTHORITY_ROUTING",
        "REVALIDATED_UNCHANGED",
    }

    for name, claim in manifest["files"].items():
        data = (OUT / name).read_bytes()
        assert len(data) == claim["bytes"]
        assert hashlib.sha256(data).hexdigest() == claim["sha256"]

    print(
        "PASS semantic fixed point: 625/625 original research quotients and "
        f"{len(new_gaps)}/{len(new_gaps)} newly discovered gaps have proposed-unratified effective resolutions; "
        f"{len(downstream)} P02-P05 detail rows revalidated; no canonical, implementation, qualification or acceptance claims invented"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
