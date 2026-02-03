#!/usr/bin/env python3
"""
Example: Analyzing a TypeScript/React codebase
"""

from shannon_insight import CodebaseAnalyzer

# Analyze a TypeScript/React codebase
analyzer = CodebaseAnalyzer("/path/to/react/app", language="typescript")
reports = analyzer.analyze()

# Focus on high-confidence issues only
high_confidence = [r for r in reports if r.confidence > 0.5]

print(f"\nHigh-confidence issues: {len(high_confidence)}/{len(reports)}")

for report in high_confidence[:5]:
    print(f"\n{report.file}")
    print(f"  Score: {report.overall_score:.3f}")
    print(f"  Root causes: {', '.join(report.root_causes)}")
