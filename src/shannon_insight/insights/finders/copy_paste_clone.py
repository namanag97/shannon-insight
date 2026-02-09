"""COPY_PASTE_CLONE — file pairs that are near-duplicates.

Scope: FILE_PAIR
Severity: 0.50
Hotspot: NO (structural-only)

Detected via Normalized Compression Distance (NCD) from Phase 3.
NCD < 0.3 means files are highly similar (likely copy-pasted).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Evidence, Finding, compute_confidence

if TYPE_CHECKING:
    from ..store_v2 import AnalysisStore


class CopyPasteCloneFinder:
    """Detects file pairs that are near-duplicates based on NCD."""

    name = "copy_paste_clone"
    api_version = "2.0"
    requires = frozenset({"clone_pairs"})
    error_mode = "skip"
    hotspot_filtered = False  # Structural-only
    tier_minimum = "ABSOLUTE"  # Works in all tiers
    deprecated = False
    deprecation_note = None

    # Thresholds from registry
    NCD_THRESHOLD = 0.3
    BASE_SEVERITY = 0.50

    def find(self, store: AnalysisStore) -> list[Finding]:
        """Detect copy-paste clones from NCD analysis.

        Returns:
            List of findings for clone pairs, sorted by severity desc.
        """
        if not store.clone_pairs.available:
            return []

        clone_pairs = store.clone_pairs.value
        findings: list[Finding] = []

        for pair in clone_pairs:
            # ClonePair dataclass: file_a, file_b, ncd
            file_a = pair.file_a
            file_b = pair.file_b
            ncd_score = pair.ncd

            # Already filtered by Phase 3, but double-check threshold
            if ncd_score >= self.NCD_THRESHOLD:
                continue

            # Lower NCD = more similar = higher severity
            # NCD 0.0 = identical → severity 0.60
            # NCD 0.29 = barely clones → severity 0.50
            severity = self.BASE_SEVERITY + (self.NCD_THRESHOLD - ncd_score) * 0.33

            # Confidence based on how far below threshold
            confidence = compute_confidence(
                [
                    ("ncd_score", ncd_score, self.NCD_THRESHOLD, "high_is_good"),
                ]
            )

            # Sort files for deterministic output
            files_sorted = sorted([file_a, file_b])

            # Build evidence
            evidence = [
                Evidence(
                    signal="ncd_score",
                    value=ncd_score,
                    percentile=0.0,
                    description=f"NCD={ncd_score:.2f} (< {self.NCD_THRESHOLD} = clone)",
                ),
            ]

            findings.append(
                Finding(
                    finding_type=self.name,
                    severity=severity,
                    title=f"Copy-paste clone: {files_sorted[0]} <-> {files_sorted[1]}",
                    files=files_sorted,
                    evidence=evidence,
                    suggestion="Extract shared logic into a common module.",
                    confidence=confidence,
                    effort="MEDIUM",
                    scope="FILE_PAIR",
                )
            )

        return sorted(findings, key=lambda f: f.severity, reverse=True)
