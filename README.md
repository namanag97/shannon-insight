# Shannon Insight

**Multi-Signal Codebase Quality Analyzer using Mathematical Primitives**

Named after Claude Shannon, the father of information theory, Shannon Insight uses mathematical primitives to detect architectural flaws and quality issues in your codebase.

## 🎯 The Problem

Single metrics fail because they lack context:
- High coupling might be intentional (utility library)
- High complexity might be necessary (compiler parser)
- High churn might mean active development, not instability

**Shannon Insight solves this with multi-signal fusion and consistency weighting.**

## 🔬 The Five Primitives

Shannon Insight analyzes code using five orthogonal mathematical primitives:

1. **Structural Entropy** - `H(AST_nodes)` - Disorder in code organization
2. **Network Centrality** - `PageRank(v)` - Importance in dependency graph
3. **Churn Volatility** - `σ(velocity)` - Instability of change patterns
4. **Semantic Coherence** - Conceptual focus (does file do one thing?)
5. **Cognitive Load** - `concepts × complexity` - Mental effort to understand

### Key Innovation: Consistency-Weighted Fusion

Shannon Insight doesn't just average metrics—it checks if signals agree:
- **High consistency**: Signals converge → Trust the score
- **Low consistency**: Signals contradict → Flag for manual review

This reduces false positives while surfacing true architectural issues.

## 🚀 Quick Start

### Installation

```bash
pip install shannon-insight
```

Or install from source:

```bash
git clone https://github.com/yourusername/shannon-insight.git
cd shannon-insight
pip install -e .
```

### Usage

Analyze any codebase (auto-detects language):

```bash
shannon-insight /path/to/codebase
```

Specify language explicitly:

```bash
shannon-insight /path/to/codebase --language go
shannon-insight /path/to/codebase --language typescript
```

Customize output:

```bash
shannon-insight /path/to/codebase --top 20 --output results.json
```

## 📊 Example Output

```
SHANNON INSIGHT - Multi-Signal Codebase Quality Analyzer
================================================================================

Layer 1: Scanning codebase...
  Found 91 source files

Layer 2: Extracting primitives...
  Extracted 5 primitives for 91 files

Layer 3: Normalizing and detecting anomalies...
  Detected 12 anomalous files

Layer 4: Fusing signals with consistency check...
  Computed consensus scores for 91 files

Layer 5: Generating recommendations...
  Generated 12 actionable reports

================================================================================
TOP 10 FILES REQUIRING ATTENTION
================================================================================

1. core/types.ts
   Overall Score: 0.471 (Confidence: 0.19)

   Raw Primitives:
     • Structural Entropy:  0.856
     • Network Centrality:  0.992
     • Churn Volatility:    0.654
     • Semantic Coherence:  0.234
     • Cognitive Load:      0.487

   Normalized (Z-Scores):
     • Structural Entropy:  +0.63σ
     • Network Centrality:  +8.97σ  ← EXTREME OUTLIER
     • Churn Volatility:    +0.56σ
     • Semantic Coherence:  -1.56σ  ← Low cohesion
     • Cognitive Load:      +0.23σ

   Root Causes:
     ⚠ High coupling - many dependencies
     ⚠ Low cohesion - file handles unrelated concerns

   Recommendations:
     → Implement dependency injection to reduce coupling
     → Extract interface to isolate dependents
     → Separate concerns into different files
     → Group related functions into cohesive modules

--------------------------------------------------------------------------------
```

## 🎓 Supported Languages

- **Go** - Functions, structs, interfaces, goroutines, channels
- **TypeScript/JavaScript** - Classes, functions, React components, hooks
- **More coming soon** - Extensible architecture makes adding languages easy

## 📖 Documentation

- **[Mathematical Foundation](docs/MATHEMATICAL_FOUNDATION.md)** - Deep dive into the math
- **[API Reference](docs/API.md)** - Use as a Python library
- **[Contributing](CONTRIBUTING.md)** - Add new languages or primitives

## 🔧 Use as a Library

```python
from shannon_insight import CodebaseAnalyzer

analyzer = CodebaseAnalyzer("/path/to/codebase", language="go")
reports = analyzer.analyze()

# Print top 10 issues
analyzer.print_report(reports, top_n=10)

# Export JSON
analyzer.export_json(reports, "results.json")
```

## 🧮 Mathematical Properties

- **Independent Primitives** - Low correlation (all |ρ| < 0.35)
- **Normalization Invariance** - Z-scores make files comparable regardless of size
- **Consistency Bounds** - Confidence ∈ [0, 1]
- **Computational Complexity** - O(N² × V) time, practical for ~10K files

## 🎯 Use Cases

- **Pre-merge checks** - Detect quality regressions in PRs
- **Refactoring targets** - Identify high-impact files to improve
- **Technical debt** - Quantify and prioritize architectural issues
- **Code reviews** - Data-driven discussion points
- **Onboarding** - Help new devs understand codebase structure

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding new languages
- Implementing new primitives
- Improving mathematical models
- Bug reports and feature requests

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- Named after **Claude Shannon**, whose information theory (entropy) is fundamental to this tool
- Inspired by research in software metrics, graph theory, and machine learning

## 🔗 Links

- **GitHub**: https://github.com/yourusername/shannon-insight
- **Issues**: https://github.com/yourusername/shannon-insight/issues
- **PyPI**: https://pypi.org/project/shannon-insight/

---

**Built with mathematics. Powered by insight.**
