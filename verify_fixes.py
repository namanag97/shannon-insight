#!/usr/bin/env python3
"""Verify all bug fixes work correctly."""

from pathlib import Path
import ast

from src.shannon_insight.scanning.factory import ScannerFactory
from src.shannon_insight.config import get_settings
from src.shannon_insight.signals.normalization import _standard_percentile

def test_lines_fix():
    """Test that lines count is accurate."""
    settings = get_settings()
    factory = ScannerFactory(".", settings)
    scanner = factory.create_scanner_for_language("python")

    test_file = Path("src/shannon_insight/signals/models.py")
    metrics = scanner.scan_file(test_file)

    actual_lines = len(test_file.read_text().splitlines())

    print(f"1. LINES FIX:")
    print(f"   Reported: {metrics.lines}")
    print(f"   Actual: {actual_lines}")
    print(f"   Status: {'✅ FIXED' if metrics.lines == actual_lines else '❌ BROKEN'}")
    return metrics.lines == actual_lines

def test_class_count_fix():
    """Test that dataclasses are counted."""
    settings = get_settings()
    factory = ScannerFactory(".", settings)
    scanner = factory.create_scanner_for_language("python")

    test_file = Path("src/shannon_insight/signals/models.py")
    metrics = scanner.scan_file(test_file)

    code = test_file.read_text()
    tree = ast.parse(code)
    actual_classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))

    print(f"\n2. CLASS_COUNT FIX:")
    print(f"   Reported: {metrics.structs}")
    print(f"   Actual: {actual_classes}")
    print(f"   Status: {'✅ FIXED' if metrics.structs == actual_classes else '❌ BROKEN'}")
    return metrics.structs == actual_classes

def test_percentile_fix():
    """Test that percentiles are 0-100, not 0-1."""
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    pctl = _standard_percentile(3.0, values)

    print(f"\n3. PERCENTILE FIX:")
    print(f"   Computed: {pctl}")
    print(f"   Expected: 60.0 (not 0.6)")
    print(f"   Status: {'✅ FIXED' if pctl == 60.0 else '❌ BROKEN'}")
    return pctl == 60.0

def test_frontend_labels():
    """Test that role and percentiles have labels."""
    constants = Path("src/shannon_insight/server/frontend/src/utils/constants.js").read_text()

    has_role = 'role: "File Role' in constants
    has_percentiles = 'percentiles: "Signal Percentile' in constants

    print(f"\n4. FRONTEND LABELS:")
    print(f"   'role' label: {'✅ EXISTS' if has_role else '❌ MISSING'}")
    print(f"   'percentiles' label: {'✅ EXISTS' if has_percentiles else '❌ MISSING'}")
    return has_role and has_percentiles

if __name__ == "__main__":
    print("="*70)
    print("VERIFICATION OF ALL BUG FIXES")
    print("="*70)

    results = [
        test_lines_fix(),
        test_class_count_fix(),
        test_percentile_fix(),
        test_frontend_labels(),
    ]

    print("\n" + "="*70)
    if all(results):
        print("✅ ALL FIXES VERIFIED")
    else:
        print(f"❌ {sum(not r for r in results)} FIXES STILL BROKEN")
    print("="*70)
