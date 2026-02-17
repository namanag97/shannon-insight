#!/usr/bin/env python3
"""Validation harness for Shannon Insight test fixtures.

Compares actual findings against ground truth to compute precision/recall/F1.

Usage:
    python validate_findings.py [fixture_dir]

Example:
    python validate_findings.py tests/fixtures/polyglot_v1_god_file
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GroundTruth:
    """Expected finding from GROUND_TRUTH.md"""

    finding_type: str
    file_path: str
    description: str


@dataclass
class ValidationResult:
    """Result of comparing actual vs expected findings."""

    fixture_name: str
    expected: list[GroundTruth]
    actual_findings: list[dict]
    true_positives: list[GroundTruth]
    false_positives: list[dict]
    false_negatives: list[GroundTruth]

    @property
    def precision(self) -> float:
        """Of findings reported, what % are correct?"""
        if not self.actual_findings:
            return 0.0
        return len(self.true_positives) / len(self.actual_findings)

    @property
    def recall(self) -> float:
        """Of expected findings, what % did we catch?"""
        if not self.expected:
            return 1.0  # No expected = perfect recall
        return len(self.true_positives) / len(self.expected)

    @property
    def f1(self) -> float:
        """Harmonic mean of precision and recall."""
        p, r = self.precision, self.recall
        if p + r == 0:
            return 0.0
        return 2 * p * r / (p + r)


def parse_ground_truth(fixture_dir: Path) -> list[GroundTruth]:
    """Parse GROUND_TRUTH.md to extract expected findings.

    Only reads lines in the "Expected Findings (Parseable Format)" section,
    which is marked by a comment: <!-- Validator parses lines starting with "- FINDING_TYPE: path" -->
    """
    gt_file = fixture_dir / "GROUND_TRUTH.md"
    if not gt_file.exists():
        return []

    expected = []
    content = gt_file.read_text()

    # Only parse lines in the parseable section (after the validator comment)
    in_parseable_section = False
    for line in content.split("\n"):
        stripped = line.strip()

        # Enter parseable section when we see the validator marker comment
        if "Validator parses lines" in stripped:
            in_parseable_section = True
            continue

        if not in_parseable_section:
            continue

        # Parse lines like: "- god_file: python_service/services/god_file.py"
        if stripped.startswith("- ") and ":" in stripped:
            parts = stripped[2:].split(":", 1)
            if len(parts) == 2:
                finding_type = parts[0].strip().lower()
                file_path = parts[1].strip()
                # Skip if finding_type looks like a markdown emphasis or URL
                if finding_type and not finding_type.startswith("*") and "/" not in finding_type:
                    expected.append(
                        GroundTruth(
                            finding_type=finding_type,
                            file_path=file_path,
                            description=stripped,
                        )
                    )

    return expected


def run_analysis(fixture_dir: Path) -> list[dict]:
    """Run shannon-insight on fixture and return findings."""
    result = subprocess.run(
        ["shannon-insight", "-n", "200", "--json", str(fixture_dir)],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"Warning: Analysis failed for {fixture_dir}")
        print(result.stderr[:500])
        return []

    try:
        data = json.loads(result.stdout)
        return data.get("findings", [])
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON from {fixture_dir}")
        return []


def match_finding(expected: GroundTruth, actual: dict) -> bool:
    """Check if an actual finding matches an expected ground truth."""
    # Type must match
    if actual.get("type", "").lower() != expected.finding_type:
        return False

    # File must be in the finding's files list
    actual_files = actual.get("files", [])
    return expected.file_path in actual_files


def validate_fixture(fixture_dir: Path) -> ValidationResult:
    """Validate a single fixture against its ground truth."""
    expected = parse_ground_truth(fixture_dir)
    actual = run_analysis(fixture_dir)

    true_positives = []
    matched_actual_indices = set()

    # Find true positives
    # A FILE_PAIR finding (e.g. hidden_coupling) lists both files and can
    # satisfy multiple expected entries — allow same finding index to match
    # different expected entries if they refer to different files in the pair.
    for gt in expected:
        for i, finding in enumerate(actual):
            if match_finding(gt, finding):
                true_positives.append(gt)
                matched_actual_indices.add(i)
                break

    # False negatives = expected but not found
    false_negatives = [gt for gt in expected if gt not in true_positives]

    # False positives = found but not expected
    # Note: For baseline, everything is a "false positive" in the ground truth sense
    # but we only count as FP if we have a ground truth to compare against
    false_positives = (
        [actual[i] for i in range(len(actual)) if i not in matched_actual_indices]
        if expected
        else []
    )

    return ValidationResult(
        fixture_name=fixture_dir.name,
        expected=expected,
        actual_findings=actual,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


def print_report(result: ValidationResult) -> None:
    """Print validation report for a fixture."""
    print(f"\n{'=' * 60}")
    print(f"FIXTURE: {result.fixture_name}")
    print(f"{'=' * 60}")

    print(f"\nExpected findings: {len(result.expected)}")
    print(f"Actual findings:   {len(result.actual_findings)}")
    print(f"True Positives:    {len(result.true_positives)}")
    print(f"False Positives:   {len(result.false_positives)}")
    print(f"False Negatives:   {len(result.false_negatives)}")

    print(f"\nPrecision: {result.precision:.2%}")
    print(f"Recall:    {result.recall:.2%}")
    print(f"F1 Score:  {result.f1:.2%}")

    if result.true_positives:
        print("\n✓ TRUE POSITIVES (correctly detected):")
        for tp in result.true_positives:
            print(f"  - {tp.finding_type}: {tp.file_path}")

    if result.false_negatives:
        print("\n✗ FALSE NEGATIVES (missed):")
        for fn in result.false_negatives:
            print(f"  - {fn.finding_type}: {fn.file_path}")

    if result.false_positives and len(result.false_positives) <= 10:
        print("\n⚠ FALSE POSITIVES (unexpected findings):")
        for fp in result.false_positives[:10]:
            files = fp.get("files", ["unknown"])
            print(f"  - {fp.get('type')}: {files[0]}")


def main():
    """Run validation on specified fixtures or all fixtures."""
    fixtures_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        # Validate specific fixture
        fixture_path = Path(sys.argv[1])
        if not fixture_path.exists():
            fixture_path = fixtures_dir / sys.argv[1]

        if fixture_path.exists():
            result = validate_fixture(fixture_path)
            print_report(result)
        else:
            print(f"Fixture not found: {sys.argv[1]}")
            sys.exit(1)
    else:
        # Validate all fixtures with GROUND_TRUTH.md
        fixtures = sorted(
            [d for d in fixtures_dir.iterdir() if d.is_dir() and (d / "GROUND_TRUTH.md").exists()]
        )

        if not fixtures:
            print("No fixtures with GROUND_TRUTH.md found.")
            print(f"Looked in: {fixtures_dir}")
            sys.exit(1)

        print("=" * 60)
        print("SHANNON INSIGHT VALIDATION REPORT")
        print("=" * 60)

        all_results = []
        for fixture in fixtures:
            result = validate_fixture(fixture)
            all_results.append(result)
            print_report(result)

        # Summary
        print(f"\n{'=' * 60}")
        print("SUMMARY")
        print(f"{'=' * 60}")

        total_expected = sum(len(r.expected) for r in all_results)
        total_tp = sum(len(r.true_positives) for r in all_results)
        total_fn = sum(len(r.false_negatives) for r in all_results)

        overall_recall = total_tp / total_expected if total_expected else 1.0

        print(f"\nTotal expected findings: {total_expected}")
        print(f"Total caught:            {total_tp}")
        print(f"Total missed:            {total_fn}")
        print(f"\nOverall Recall: {overall_recall:.2%}")


if __name__ == "__main__":
    main()
