#!/usr/bin/env python3
"""Validate the Claude provenance/quality integration review without ratifying it."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys

from build_review import HANDOFF, HERE, ROOT, load_jsonl


def main() -> int:
    result = subprocess.run([sys.executable, str(HERE / "build_review.py"), "--check"], capture_output=True)
    assert result.returncode == 0, result.stdout.decode() + result.stderr.decode()
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"], name
    modules = load_jsonl(HERE / "module-integration-review.jsonl")
    merges = load_jsonl(HERE / "merge-candidate-integration-review.jsonl")
    gaps = load_jsonl(HERE / "integration-gaps.jsonl")
    source_modules = load_jsonl(HANDOFF / "semantic-modules.jsonl")
    source_merges = load_jsonl(HANDOFF / "merge-candidates.jsonl")
    assert len(modules) == len({row["module_ref"] for row in modules}) == len(source_modules) == 37
    assert {row["module_ref"] for row in modules} == {row["module_id"] for row in source_modules}
    assert len(merges) == len({row["candidate_ref"] for row in merges}) == len(source_merges) == 12
    assert {row["candidate_ref"] for row in merges} == {row["candidate_id"] for row in source_merges}
    assert sum(row["source_module_kind"] == "GLOBAL_PRIMITIVE_CANDIDATE" for row in modules) == 7
    assert sum(row["source_module_kind"] == "CROSS_FAMILY_MODULE_CANDIDATE" for row in modules) == 7
    assert sum(row["source_module_kind"] == "FAMILY_AXIS_MODULE_CANDIDATE" for row in modules) == 17
    assert sum(row["source_module_kind"] == "LOCAL_REFINEMENT_CANDIDATE" for row in modules) == 6
    assert all(row["source_owner_resolves"] for row in modules)
    assert all(row["constitutional_module_refs"] for row in modules if row["source_module_kind"] != "LOCAL_REFINEMENT_CANDIDATE")
    assert all(not row["constitutional_module_refs"] for row in modules if row["source_module_kind"] == "LOCAL_REFINEMENT_CANDIDATE")
    assert all(row["status"] not in {"RATIFIED", "ACCEPTED"} for row in modules)
    assert all(row["target_exists"] for row in merges)
    assert all(row["precondition_assessment"] == "LIVE_AGGREGATE_SNAPSHOT_BUT_REBIND_TO_TARGET_RECORD_BEFORE_APPLY" for row in merges)
    assert all(row["integration_disposition"] not in {"APPLY", "MERGE", "RATIFY"} for row in merges)
    false_vacancies = {row["candidate_ref"] for row in merges if row["integration_disposition"].startswith("REJECT_FALSE_VACANCY")}
    assert false_vacancies == {"merge.vacancy.disclosure-core", "merge.vacancy.missing-lpe-cores"}
    summary = json.loads((HERE / "summary.json").read_text())
    assert summary["completion_claim"] is False
    assert summary["canonical_mutations_authorized"] == summary["ratified_modules"] == summary["ratified_boundaries"] == 0
    assert summary["omitted_existing_library_count"] == 6
    assert summary["false_vacancy_candidate_count"] == 2
    assert len(gaps) == 5 and all(row["status"] == "OPEN" for row in gaps)
    snapshot = json.loads((HERE / "input-snapshot.json").read_text())
    for item in snapshot["inputs"]:
        path = ROOT / item["path"]
        data = path.read_bytes()
        assert len(data) == item["bytes"] and hashlib.sha256(data).hexdigest() == item["sha256"], item["path"]
    print("PASS Claude provenance/quality integration review: 37 modules and 12 merge candidates routed; 6 omitted existing LPE libraries and 2 false vacancies exposed; zero canonical mutation or ratification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
