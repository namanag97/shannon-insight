# Shannon Insight Examples

This directory contains usage examples for Shannon Insight.

## Basic Usage

```python
from shannon_insight import InsightKernel

kernel = InsightKernel("/path/to/codebase")
result, snapshot = kernel.run(max_findings=10)
for finding in result.findings:
    print(f"{finding.title} (severity: {finding.severity:.2f})")
```

## Examples

- **basic_usage.py** - Simple analysis and reporting
- **typescript_example.py** - TypeScript/React specific example

## Running Examples

Make sure Shannon Insight is installed:

```bash
pip install shannon-codebase-insight
```

Or install from source:

```bash
cd ..
pip install -e .
```

Then run any example:

```bash
python basic_usage.py
python typescript_example.py
```

## CLI Examples

Analyze current directory:
```bash
shannon-insight .
```

Analyze specific project:
```bash
shannon-insight /path/to/project --language go
```

JSON output:
```bash
shannon-insight . --format json
```

Explain a specific file:
```bash
shannon-insight . --explain engine.py
```

Scoped analysis for PRs:
```bash
shannon-insight . --pr --fail-on high
```
