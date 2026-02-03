#!/usr/bin/env python3
"""
Example: Basic usage of Shannon Insight as a Python library
"""

from shannon_insight import CodebaseAnalyzer

# Analyze a Go codebase
analyzer = CodebaseAnalyzer("/path/to/go/project", language="go")
reports = analyzer.analyze()

# Print top 10 files requiring attention
analyzer.print_report(reports, top_n=10)

# Export detailed JSON report
analyzer.export_json(reports, "analysis_results.json")

print("\nAnalysis complete!")
print(f"Found {len(reports)} files with quality issues")
