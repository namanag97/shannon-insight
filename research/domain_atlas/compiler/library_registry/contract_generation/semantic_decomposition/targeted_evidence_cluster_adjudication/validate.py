#!/usr/bin/env python3
"""Validate lossless cluster-first targeted-evidence adjudication work."""
import hashlib
import json

from build_targeted_evidence_cluster_adjudication import HERE, build, outputs


def main() -> int:
    for name, expected in outputs().items():
        path = HERE / name
        assert path.is_file(), f"missing {name}"
        assert path.read_text() == expected, f"stale {name}"
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, claim in manifest["files"].items():
        data = (HERE / name).read_bytes()
        assert len(data) == claim["bytes"] and hashlib.sha256(data).hexdigest() == claim["sha256"]

    built = build()
    summary = built["summary"]
    challenges = built["challenges"]
    occurrences = built["occurrences"]
    assert len(built["axes"]) == len({row["axis"] for row in built["axes"]}) == 6
    assert len(challenges) == len({row["challenge_id"] for row in challenges}) == summary["coordinate_cluster_challenges"]
    assert summary["lexical_hypothesis_clusters"] + summary["no_member_evidence_clusters"] == len(challenges)
    assert len(occurrences) == len({(row["axis"], row["library_ref"]) for row in occurrences}) == summary["member_adjudication_occurrences"]
    assert sum(row["member_occurrence_count"] for row in challenges) == len(occurrences)
    challenge_refs = {row["challenge_id"] for row in challenges}
    assert all(row["cluster_challenge_ref"] in challenge_refs for row in occurrences)
    assert all(row["family_evidence_to_member_binding"] == "UNTESTED" and row["member_applicability"] == "UNRESOLVED" for row in occurrences)
    assert all(row["evidence_to_cluster_binding"] == "UNTESTED" and row["evidence_sufficiency"] == "UNDETERMINED" for row in challenges)
    assert summary["evidence_to_cluster_bindings_adjudicated"] == summary["member_applicability_decisions"] == summary["member_exception_decisions"] == summary["owner_decisions"] == summary["coordinate_answers_supplied"] == summary["canonical_gaps_closed"] == 0
    assert not summary["completion_claim"]
    print(
        f"PASS targeted evidence cluster adjudication: {len(challenges)} reversible challenges cover all {len(occurrences)} exact campaign occurrences; family evidence cannot silently become member applicability"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
