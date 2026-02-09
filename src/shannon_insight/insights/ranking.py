"""Percentile computation, severity ranking, and finding deduplication."""

from __future__ import annotations

from bisect import bisect_left
from collections import Counter, defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Finding


def compute_percentiles(values: dict[str, float]) -> dict[str, float]:
    """Given {file: value}, return {file: percentile 0-100}.

    Uses bisect for efficient rank lookup. Ties get the same percentile
    (left-side rank).
    """
    if not values:
        return {}

    sorted_vals = sorted(values.values())
    n = len(sorted_vals)
    if n == 0:
        return {}

    rank_map: dict[str, float] = {}
    for path, val in values.items():
        rank = bisect_left(sorted_vals, val)
        rank_map[path] = (rank / n) * 100

    return rank_map


# ── Finding Deduplication ─────────────────────────────────────────────

# Subsumption rules: parent ⊃ child
# If parent finding exists on same file, suppress child.
SUBSUMPTION_RULES: dict[str, set[str]] = {
    "god_file": {"review_blindspot", "knowledge_silo"},
    "high_risk_hub": {"bug_attractor"},
}


def deduplicate_findings(findings: list[Finding]) -> list[Finding]:
    """Remove redundant findings using subsumption rules.

    If a parent finding (e.g. god_file) exists on a file, suppress
    child findings (e.g. review_blindspot, knowledge_silo) for
    the same file.

    Args:
        findings: List of findings to deduplicate

    Returns:
        Deduplicated list of findings
    """
    if not findings:
        return findings

    # Build lookup: file -> set of finding types present
    file_findings: dict[str, set[str]] = defaultdict(set)
    for f in findings:
        for path in f.files:
            file_findings[path].add(f.finding_type)

    # Apply subsumption rules
    suppressed: set[int] = set()
    for i, finding in enumerate(findings):
        if i in suppressed:
            continue

        for path in finding.files:
            # Check if any parent finding type is present for this file
            for parent_type, child_types in SUBSUMPTION_RULES.items():
                if finding.finding_type in child_types and parent_type in file_findings[path]:
                    suppressed.add(i)
                    break

    return [f for i, f in enumerate(findings) if i not in suppressed]


def count_findings_per_file(findings: list[Finding]) -> dict[str, int]:
    """Count how many findings affect each file.

    Useful for identifying files that are flagged by multiple finders.

    Args:
        findings: List of findings

    Returns:
        Dict mapping file path to finding count
    """
    counts: Counter[str] = Counter()
    for f in findings:
        for path in f.files:
            counts[path] += 1
    return dict(counts)
