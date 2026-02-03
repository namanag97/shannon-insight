# Shannon Insight Examples

This directory contains usage examples for Shannon Insight.

## Basic Usage

```python
from shannon_insight import CodebaseAnalyzer

analyzer = CodebaseAnalyzer("/path/to/codebase")
reports = analyzer.analyze()
analyzer.print_report(reports, top_n=10)
```

## Examples

- **basic_usage.py** - Simple analysis and reporting
- **typescript_example.py** - TypeScript/React specific example

## Running Examples

Make sure Shannon Insight is installed:

```bash
pip install shannon-insight
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

Customize output:
```bash
shannon-insight . --top 20 --output my_results.json
```
