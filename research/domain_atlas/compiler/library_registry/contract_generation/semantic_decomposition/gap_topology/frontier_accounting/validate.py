#!/usr/bin/env python3
"""Fail-closed validation for exhaustive semantic-gap frontier accounting."""
from __future__ import annotations

import collections
import hashlib
import json
from typing import Any

from build_frontier_accounting import (
    GAP_ROOT,
    HERE,
    SHARD_COUNT,
    build_model,
    canonical,
    load_json,
    load_jsonl,
    sha256_text,
)


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    model = build_model()
    manifest = load_json(HERE / "manifest.json")
    summary = load_json(HERE / "summary.json")
    validation_report = load_json(HERE / "validation-report.json")
    taxonomy = load_jsonl(HERE / "disposition-taxonomy.jsonl")
    kernels = load_jsonl(HERE / "decision-kernels.jsonl")
    cluster_rows = load_jsonl(HERE / "cluster-dispositions.jsonl")
    shard_names = [f"atom-dispositions-{index:02d}.jsonl" for index in range(SHARD_COUNT)]
    shard_rows = {name: load_jsonl(HERE / name) for name in shard_names}
    atoms = [row for name in shard_names for row in shard_rows[name]]

    expected_collections = {
        "disposition-taxonomy.jsonl": model["taxonomy"],
        "decision-kernels.jsonl": model["kernels"],
        "cluster-dispositions.jsonl": model["clusters"],
        **model["shards"],
    }
    for name, expected in expected_collections.items():
        actual = load_jsonl(HERE / name)
        if actual != expected:
            fail(f"stale or non-deterministic generated output: {name}")
        if actual != sorted(
            actual,
            key=(
                (lambda row: row["atom_id"])
                if name.startswith("atom-dispositions-")
                else (
                    (lambda row: row["disposition_id"])
                    if name == "disposition-taxonomy.jsonl"
                    else (
                        (lambda row: row["decision_kernel_id"])
                        if name == "decision-kernels.jsonl"
                        else (lambda row: row["source_cluster_ref"])
                    )
                )
            ),
        ):
            fail(f"non-deterministic ordering: {name}")

    if summary != model["summary"]:
        fail("stale summary.json")
    if validation_report != model["validation_report"]:
        fail("stale validation-report.json")

    parent_clusters = load_jsonl(GAP_ROOT / "gap-clusters.jsonl")
    parent_summary = load_json(GAP_ROOT / "summary.json")
    parent_by_id = {row["cluster_id"]: row for row in parent_clusters}
    if len(parent_by_id) != len(parent_clusters):
        fail("duplicate parent gap cluster IDs")

    atom_ids = [row["atom_id"] for row in atoms]
    if len(atom_ids) != len(set(atom_ids)):
        fail("duplicate atom IDs")
    atom_digests = [row["source_atom_digest"] for row in atoms]
    if len(atom_digests) != len(set(atom_digests)):
        fail("duplicate source atom digests")
    kernel_ids = [row["decision_kernel_id"] for row in kernels]
    if len(kernel_ids) != len(set(kernel_ids)):
        fail("duplicate decision kernel IDs")
    cluster_disposition_ids = [row["cluster_disposition_id"] for row in cluster_rows]
    if len(cluster_disposition_ids) != len(set(cluster_disposition_ids)):
        fail("duplicate cluster disposition IDs")

    if {row["source_cluster_ref"] for row in cluster_rows} != set(parent_by_id):
        fail("cluster disposition coverage does not equal parent cluster set")
    if len(cluster_rows) != len(parent_clusters):
        fail("cluster disposition cardinality mismatch")
    if len(atoms) != parent_summary["represented_gap_atoms"]:
        fail("atom cardinality does not equal parent represented_gap_atoms")

    kernels_by_id = {row["decision_kernel_id"]: row for row in kernels}
    cluster_rows_by_ref = {row["source_cluster_ref"]: row for row in cluster_rows}
    atoms_by_cluster: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for atom in atoms:
        cluster_ref = atom["source_cluster_ref"]
        if cluster_ref not in parent_by_id:
            fail(f"atom references unknown cluster: {cluster_ref}")
        if atom["primary_kernel_ref"] not in kernels_by_id:
            fail(f"atom references unknown kernel: {atom['primary_kernel_ref']}")
        if atom["completion_claim"] is not False:
            fail(f"atom claims completion: {atom['atom_id']}")
        if not atom["local_residual"]:
            fail(f"atom loses local residual: {atom['atom_id']}")
        if not atom["local_residual"].get("closure_condition"):
            fail(f"atom lacks closure condition: {atom['atom_id']}")
        if atom["disposition"] == "CLOSED_BY_EXISTING_VALID_EVIDENCE" and not atom["closure_receipt_refs"]:
            fail(f"silent closure without receipt: {atom['atom_id']}")
        if atom["status"] in {
            "IMPLEMENTED",
            "QUALIFIED",
            "ACCEPTED",
            "BUILD_READY",
            "RATIFIED",
            "CLOSED",
        }:
            fail(f"invented completion state: {atom['atom_id']}={atom['status']}")
        atoms_by_cluster[cluster_ref].append(atom)

    for cluster_ref, parent in parent_by_id.items():
        members = sorted(atoms_by_cluster[cluster_ref], key=lambda row: row["atom_id"])
        if len(members) != parent["atom_count"]:
            fail(
                f"{cluster_ref}: projected {len(members)} atoms != parent atom_count "
                f"{parent['atom_count']}"
            )
        row = cluster_rows_by_ref[cluster_ref]
        if row["source_atom_count"] != parent["atom_count"]:
            fail(f"{cluster_ref}: source_atom_count mismatch")
        if row["projected_atom_count"] != len(members):
            fail(f"{cluster_ref}: projected_atom_count mismatch")
        expected_set_digest = sha256_text(
            "".join(
                f"{member['atom_id']}:{member['source_atom_digest']}\n"
                for member in members
            )
        )
        if row["atom_set_sha256"] != expected_set_digest:
            fail(f"{cluster_ref}: atom-set digest mismatch")
        if row["source_cluster_sha256"] != sha256_text(canonical(parent)):
            fail(f"{cluster_ref}: parent cluster digest mismatch")
        if row["primary_kernel_ref"] not in kernels_by_id:
            fail(f"{cluster_ref}: unknown primary kernel")
        if {member["primary_kernel_ref"] for member in members} != {
            row["primary_kernel_ref"]
        }:
            fail(f"{cluster_ref}: atoms do not share cluster primary kernel")
        if row["completion_claim"] is not False:
            fail(f"{cluster_ref}: cluster disposition claims completion")
        if row["disposition"] == "CLOSED_BY_EXISTING_VALID_EVIDENCE" and not row["closure_receipt_refs"]:
            fail(f"{cluster_ref}: cluster silently closes without evidence")

    cluster_kernel_membership: dict[str, int] = collections.Counter()
    represented_atoms_by_kernel = collections.Counter()
    for kernel in kernels:
        if kernel["completion_claim"] is not False:
            fail(f"kernel claims completion: {kernel['decision_kernel_id']}")
        for cluster_ref in kernel["member_cluster_refs"]:
            cluster_kernel_membership[cluster_ref] += 1
            represented_atoms_by_kernel[kernel["decision_kernel_id"]] += parent_by_id[
                cluster_ref
            ]["atom_count"]
        if represented_atoms_by_kernel[kernel["decision_kernel_id"]] != kernel[
            "represented_atom_count"
        ]:
            fail(f"kernel atom count mismatch: {kernel['decision_kernel_id']}")
    if set(cluster_kernel_membership) != set(parent_by_id):
        fail("kernel cluster coverage mismatch")
    if any(count != 1 for count in cluster_kernel_membership.values()):
        fail("one or more clusters have zero or multiple primary kernels")

    disposition_ids = {row["disposition_id"] for row in taxonomy}
    required_dispositions = {
        "CLOSED_BY_EXISTING_VALID_EVIDENCE",
        "COVERED_BY_REUSABLE_KERNEL",
        "SPLIT_INTO_MULTIPLE_DECISIONS",
        "MERGED_WITH_ANOTHER_QUOTIENT",
        "RECLASSIFIED_OR_WRONGLY_FORMULATED",
        "CONTRADICTED_OR_REOPENED",
        "EVIDENCE_VACANCY",
        "IMPLEMENTATION_ONLY",
        "QUALIFICATION_ONLY",
        "OUTSIDE_RESEARCH_SCOPE",
    }
    if disposition_ids != required_dispositions:
        fail("disposition taxonomy is incomplete or contains silent aliases")
    if any(row["completion_claim"] is not False for row in taxonomy):
        fail("taxonomy claims completion")

    actual_dispositions = collections.Counter(row["disposition"] for row in atoms)
    if dict(sorted(actual_dispositions.items())) != summary["disposition_counts"]:
        fail("summary disposition counts mismatch")
    actual_residuals = collections.Counter(
        row["local_residual"]["residual_kind"] for row in atoms
    )
    if dict(sorted(actual_residuals.items())) != summary["residual_counts"]:
        fail("summary residual counts mismatch")
    actual_statuses = collections.Counter(row["status"] for row in atoms)
    if dict(sorted(actual_statuses.items())) != summary["status_counts"]:
        fail("summary status counts mismatch")
    if summary["source_gap_clusters"] != len(parent_clusters):
        fail("summary source_gap_clusters mismatch")
    if summary["source_gap_atoms"] != len(atoms):
        fail("summary source_gap_atoms mismatch")
    if summary["unmapped_clusters"] or summary["unmapped_atoms"] or summary["multiply_mapped_atoms"]:
        fail("summary reports incomplete mapping")
    if summary["closed_by_existing_valid_evidence"] != 0:
        fail("current snapshot cannot claim closed atoms without receipts")
    if parent_summary["canonical_exact_gaps_closed"] != 0:
        fail("parent snapshot closure state changed; disposition policy requires review")
    if summary["implemented_atoms"] or summary["qualified_atoms"] or summary["accepted_atoms"]:
        fail("invented implementation, qualification or acceptance count")
    if summary["completion_claim"] is not False:
        fail("summary claims completion")

    manifest_claims = {row["path"]: row for row in manifest["files"]}
    expected_manifest_paths = set(expected_collections) | {
        "summary.json",
        "validation-report.json",
    }
    if set(manifest_claims) != expected_manifest_paths:
        fail("manifest path set mismatch")
    for path, claim in manifest_claims.items():
        file_path = HERE / path
        data = file_path.read_bytes()
        if hashlib.sha256(data).hexdigest() != claim["sha256"]:
            fail(f"manifest digest mismatch: {path}")
        if len(data) != claim["bytes"]:
            fail(f"manifest byte count mismatch: {path}")
        expected_records = 1 if path.endswith(".json") else len(load_jsonl(file_path))
        if expected_records != claim["records"]:
            fail(f"manifest record count mismatch: {path}")
    if manifest["summary"] != summary:
        fail("manifest summary mismatch")
    if manifest["completion_claim"] is not False:
        fail("manifest claims completion")

    print(
        "PASS exhaustive semantic-gap frontier accounting: "
        f"{len(parent_clusters):,} source clusters -> {len(cluster_rows):,} dispositions; "
        f"{len(atoms):,} exact atoms -> one primary kernel plus one local residual each; "
        f"{len(kernels):,} reusable kernels; 0 unmapped, 0 multiply mapped, "
        "0 invented closures, implementations, qualifications or acceptances"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
