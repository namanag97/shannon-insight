#!/usr/bin/env python3
"""
Example: Basic usage of Shannon Insight as a Python library
"""

from shannon_insight import InsightKernel

# Analyze a codebase
kernel = InsightKernel("/path/to/project", language="python")
result, snapshot = kernel.run(max_findings=10)

# Print findings
for finding in result.findings:
    print(f"{finding.title} (severity: {finding.severity:.2f})")
    for e in finding.evidence:
        print(f"  - {e.description}")
    print(f"  -> {finding.suggestion}")
    print()

print(f"Analysis complete: {len(result.findings)} finding(s) from "
      f"{result.store_summary.total_files} files")
