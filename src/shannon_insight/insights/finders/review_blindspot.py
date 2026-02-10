"""REVIEW_BLINDSPOT — high-centrality, single-author, untested files.

Scope: FILE
Severity: 0.80
Hotspot: YES (temporal)

The most dangerous files:
- High PageRank (central, many dependents)
- Low bus factor (single owner)
- No test file (no safety net)

These are review blindspots - changes here are risky but may not get
adequate review because only one person knows the code and there are no tests.
"""

from __future__ import annotations

import os
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from ..helpers import compute_hotspot_median
from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


def _has_test_file(path: str, all_paths: set[str]) -> bool:
    """Check if a file has an associated test file.

    Language-aware detection:
    - Python: test_bar.py, bar_test.py, tests/test_bar.py
    - Go: bar_test.go (same directory)
    - Java: BarTest.java, BarTests.java
    - TypeScript/JS: bar.test.ts, bar.spec.ts, __tests__/bar.test.ts
    - Ruby: bar_test.rb, test_bar.rb, spec/bar_spec.rb
    - Rust: skip (tests are inline via #[cfg(test)])
    """
    p = PurePosixPath(path)
    stem = p.stem  # filename without extension
    suffix = p.suffix.lower()
    parent = str(p.parent)

    # Rust: skip (inline tests)
    if suffix == ".rs":
        return True  # Assume has tests (inline)

    # Check common test patterns
    test_patterns = []

    if suffix == ".py":
        test_patterns = [
            f"test_{stem}.py",
            f"{stem}_test.py",
            f"tests/test_{stem}.py",
            f"tests/{stem}/test_{stem}.py",
        ]
    elif suffix == ".go":
        test_patterns = [f"{stem}_test.go"]
    elif suffix == ".java":
        test_patterns = [f"{stem}Test.java", f"{stem}Tests.java"]
    elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
        base = stem.replace(".test", "").replace(".spec", "")
        test_patterns = [
            f"{base}.test{suffix}",
            f"{base}.spec{suffix}",
            f"__tests__/{base}.test{suffix}",
        ]
    elif suffix == ".rb":
        test_patterns = [
            f"{stem}_test.rb",
            f"test_{stem}.rb",
            f"spec/{stem}_spec.rb",
        ]

    # Check if any test pattern exists in the codebase
    for pattern in test_patterns:
        # Try in same directory
        test_path = os.path.join(parent, pattern) if parent != "." else pattern
        if test_path in all_paths:
            return True
        # Try at root level
        if pattern in all_paths:
            return True

    return False


class ReviewBlindspotFinder:
    """Detects high-risk files with no tests and single owner."""

    name = "review_blindspot"
    api_version = "2.0"
    requires = frozenset({"signal_field"})
    error_mode = "skip"
    hotspot_filtered = True  # Uses temporal signals
    tier_minimum = "BAYESIAN"  # Needs percentiles
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    BUS_FACTOR_THRESHOLD = 1.5
    PAGERANK_PCTL_THRESHOLD = 0.75
    BASE_SEVERITY = 0.80

    MAX_FINDINGS = 10  # Cap findings for review blindspot

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect review blindspots.

        Returns:
            List of findings sorted by severity desc, capped at MAX_FINDINGS.
        """
        if not store.signal_field.available:
            return []

        field = store.signal_field.value
        tier = field.tier

        # Skip in ABSOLUTE tier (needs percentiles)
        if tier == "ABSOLUTE":
            return []

        # Skip for solo projects — "single owner" is meaningless
        if field.global_signals.team_size <= 1:
            return []

        # Compute hotspot filter median
        median_changes = compute_hotspot_median(field)

        # Get all paths for test detection
        all_paths = set(field.per_file.keys())

        findings: list[Finding] = []

        for path, fs in sorted(field.per_file.items()):
            # Skip test files themselves
            if fs.role == "TEST":
                continue

            # Apply hotspot filter
            if fs.total_changes <= median_changes:
                continue

            # Check bus factor
            if fs.bus_factor > self.BUS_FACTOR_THRESHOLD:
                continue

            # Check pagerank percentile
            pctl_pr = fs.percentiles.get("pagerank", 0.0)
            if pctl_pr <= self.PAGERANK_PCTL_THRESHOLD:
                continue

            # Check for test file
            if _has_test_file(path, all_paths):
                continue  # Has tests

            # Compute confidence
            confidence = compute_confidence(
                [
                    ("pagerank", pctl_pr, self.PAGERANK_PCTL_THRESHOLD, "high_is_bad"),
                    ("bus_factor", fs.bus_factor, self.BUS_FACTOR_THRESHOLD, "high_is_good"),
                ]
            )

            # Build evidence
            evidence = [
                Evidence(
                    signal="pagerank",
                    value=fs.pagerank,
                    percentile=pctl_pr * 100,
                    description=f"Top {(1 - pctl_pr) * 100:.0f}% by centrality",
                ),
                Evidence(
                    signal="bus_factor",
                    value=fs.bus_factor,
                    percentile=fs.percentiles.get("bus_factor", 0.0) * 100,
                    description=f"Bus factor = {fs.bus_factor:.1f} (single owner)",
                ),
                Evidence(
                    signal="has_test",
                    value=0.0,
                    percentile=0.0,
                    description="No test file found",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=self.BASE_SEVERITY,
                    title=f"Review blindspot: {path} (no tests, single owner)",
                    files=[path],
                    evidence=evidence,
                    suggestion="High-centrality code with single owner and no tests. Add tests and reviewer.",
                    confidence=confidence,
                    effort="MEDIUM",
                    scope="FILE",
                )
            )

        findings.sort(key=lambda f: f.severity, reverse=True)
        return findings[: self.MAX_FINDINGS]
