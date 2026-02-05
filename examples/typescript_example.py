#!/usr/bin/env python3
"""
Example: Analyzing a TypeScript/React codebase
"""

from shannon_insight import InsightKernel

# Analyze a TypeScript/React codebase
kernel = InsightKernel("/path/to/react/app", language="typescript")
result, snapshot = kernel.run(max_findings=10)

# Focus on high-severity findings
high_severity = [f for f in result.findings if f.severity > 0.8]

print(f"\nHigh-severity findings: {len(high_severity)}/{len(result.findings)}")

for finding in high_severity[:5]:
    print(f"\n{finding.title}")
    print(f"  Severity: {finding.severity:.3f}")
    print(f"  Files: {', '.join(finding.files)}")
    print(f"  Suggestion: {finding.suggestion}")
