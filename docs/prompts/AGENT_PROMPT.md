# Shannon Insight — Cross-Language Analysis Redesign

## Your Task

You are working on **Shannon Insight**, a codebase quality analyzer at `/Users/namanagarwal/coding/codeanalyser`. The tool computes 5 quality primitives per source file, detects statistical anomalies, fuses signals, and generates recommendations.

**The core problem:** The tool currently uses hand-written regex scanners per language (Go, Python, TypeScript). This approach has three fatal flaws:

1. **It doesn't scale.** Every new language needs a new 150-line scanner with bespoke regex patterns for imports, exports, functions, classes, complexity, and AST node types. There are 20+ popular languages.

2. **The metrics aren't comparable across languages.** When analyzing a mixed-language codebase (e.g. a Python backend + TypeScript frontend), the z-score normalization pools files from different languages together. But Go's AST node vocabulary (`defer`, `chan`, `go`) differs from Python's (`yield`, `with`, `decorator`) — so structural entropy means different things per language. The `structs` field means Go structs in Go, classes in Python, and React components in TypeScript. Cognitive load computes different things.

3. **The regex parsing is fragile.** It misses edge cases (multiline strings, nested comments, string interpolation), doesn't handle language-specific idioms correctly, and can't adapt to new syntax.

**Your goal:** Redesign the scanning/metric-extraction layer so it works reliably across ALL popular programming languages without needing a per-language plugin. Find a better mathematical or algorithmic approach. Implement it.

---

## Current Architecture

```
src/shannon_insight/
├── analyzers/             # Language-specific scanners (THE PROBLEM)
│   ├── base.py            # BaseScanner ABC
│   ├── go_analyzer.py     # Go regex scanner
│   ├── python_analyzer.py # Python regex scanner
│   └── typescript_analyzer.py
├── primitives/            # Quality primitive computation
│   ├── registry.py        # PrimitiveDefinition registry
│   ├── extractor.py       # Computes 5 primitives from FileMetrics
│   ├── detector.py        # Z-score normalization + anomaly detection
│   ├── fusion.py          # Signal fusion with consistency weighting
│   └── recommendations.py # Context-aware recommendations
├── formatters/            # Output rendering (decoupled from core)
├── core.py                # Pipeline orchestrator
├── models.py              # FileMetrics, Primitives, AnomalyReport, etc.
├── config.py              # pydantic-settings configuration
├── baseline.py            # Diff/PR mode baseline management
└── cli.py                 # Typer CLI
```

### Data Flow

```
Scanner.scan() → List[FileMetrics]
    → PrimitiveExtractor.extract_all() → Dict[str, Primitives]
        → AnomalyDetector.normalize() + detect() → z-scores + flags
            → SignalFusion.fuse() → (score, confidence) per file
                → RecommendationEngine.generate() → List[AnomalyReport]
```

### FileMetrics (the raw input everything depends on)

```python
@dataclass
class FileMetrics:
    path: str
    lines: int
    tokens: int
    imports: List[str]        # dependency edges for network centrality
    exports: List[str]        # public API for semantic coherence (TF-IDF)
    functions: int            # concept count for cognitive load
    interfaces: int           # concept count for cognitive load
    structs: int              # concept count for cognitive load
    complexity_score: float   # cyclomatic complexity estimate
    nesting_depth: int        # deepest nesting level
    ast_node_types: Counter   # distribution for structural entropy
    last_modified: float      # mtime for churn volatility
```

### The 5 Primitives and What They Need

| Primitive | What it measures | Key FileMetrics fields used |
|-----------|-----------------|---------------------------|
| Structural Entropy | Disorder in code organization | `ast_node_types` (Counter) |
| Network Centrality | Importance in dependency graph | `imports` (to build dep graph) |
| Churn Volatility | Change frequency | `last_modified` (filesystem) |
| Semantic Coherence | Conceptual focus | `imports` + `exports` (TF-IDF) |
| Cognitive Load | Mental effort to understand | `functions`, `structs`, `interfaces`, `complexity_score`, `nesting_depth` |

---

## The Specific Problems With Per-Language Scanners

### Problem 1: AST node types are incomparable

Go scanner produces: `{function, struct, interface, import, export, if, for, range, return, defer, go, chan}`
Python scanner produces: `{function, class, import, export, if, for, while, return, yield, with, try, decorator}`
TypeScript scanner produces: `{function, class, component, hook, import, export, if, for, while, return, jsx}`

Structural entropy = normalized Shannon entropy of this distribution. When you z-score normalize across a mixed Go+Python codebase, you're comparing entropies from different alphabets.

### Problem 2: Semantic field overloading

- TypeScript maps `classes → interfaces` field and `react_components → structs` field
- Python maps `classes → structs` field and hardcodes `interfaces = 0`
- Cognitive load = `(functions + structs + interfaces) × complexity × (1 + nesting/10)`
- This formula computes different things for each language

### Problem 3: Import parsing varies wildly

- Go: `import "github.com/foo/bar"` and grouped `import (...)`
- Python: `import foo`, `from foo import bar`, `from . import baz`
- TypeScript: `import { X } from 'Y'`, `import X from 'Y'`, `require('Y')`
- Java: `import com.foo.Bar;`
- Rust: `use std::collections::HashMap;`
- C/C++: `#include <vector>`, `#include "myfile.h"`
- Ruby: `require 'foo'`, `require_relative 'bar'`

Each needs different regex. And the dependency graph quality depends entirely on how well these are parsed.

---

## Possible Approaches to Explore

You should evaluate these approaches and pick the best one (or combine them). Don't just pick the first one — think about tradeoffs.

### Approach A: Tree-sitter Universal Parsing

[tree-sitter](https://tree-sitter.github.io/) provides incremental parsers for 100+ languages with a uniform AST representation. The `tree-sitter` Python binding (`py-tree-sitter` or `tree-sitter-languages`) lets you parse any supported language into a concrete syntax tree.

**How it would work:**
- Auto-detect language from file extension
- Parse with the right tree-sitter grammar
- Walk the CST and map node types to a standard vocabulary
- Extract imports, exports, functions, types from tree queries

**Pros:** Accurate parsing, handles edge cases, 100+ languages for free, uniform AST
**Cons:** Adds a native dependency (tree-sitter grammars are compiled C), slightly heavier install

**Key packages:** `tree-sitter` (core), `tree-sitter-languages` (pre-built grammars for ~20 languages), or individual `tree-sitter-python`, `tree-sitter-javascript`, etc.

### Approach B: Language-Agnostic Statistical Analysis

Instead of parsing language constructs, measure universal statistical properties of source code text:

- **Byte entropy:** Shannon entropy of the raw character distribution. High entropy = diverse character usage = potentially complex. This is truly language-agnostic.
- **Compression ratio:** `len(zlib.compress(content)) / len(content)`. Approximates Kolmogorov complexity. Repetitive code compresses well (low complexity); diverse code doesn't (high complexity). This replaces structural entropy without any parsing.
- **Line-length distribution:** Compute stdev/skewness of line lengths. Deeply nested code has more short lines interspersed with long lines.
- **Indentation statistics:** Mean/max indentation depth works for any language (spaces or tabs). Replaces nesting depth without brace counting or indent parsing.
- **Token entropy:** Split on whitespace + punctuation (universal tokenizer), compute entropy of the token distribution. This approximates structural entropy without knowing what the tokens mean.
- **Halstead metrics:** Count distinct operators and operands (split by non-alphanumeric chars). Compute volume, difficulty, effort. Language-agnostic.

**For dependencies (network centrality):**
- Most languages use keywords for imports: `import`, `include`, `require`, `use`, `using`, `from`. A single regex matching any of these captures 90% of imports across all languages.
- Alternatively: file co-change analysis from git history (files that change together are likely coupled).

**For semantic coherence:**
- Instead of TF-IDF on imports/exports, use TF-IDF on identifier names extracted by splitting camelCase/snake_case tokens. This works for any language.
- Or use normalized compression distance: `NCD(a,b) = (C(ab) - min(C(a),C(b))) / max(C(a),C(b))` where C is compressed size. Files with similar content will compress well together.

**Pros:** Zero language-specific code, works on any text file, mathematically principled (information theory)
**Cons:** Less precise than parsing (can't distinguish a function from a variable), may produce noisier signals

### Approach C: Hybrid (Tree-sitter where available, statistical fallback)

Use tree-sitter for languages that have grammars (Python, JS/TS, Go, Java, Rust, C/C++, Ruby, etc. — covers 95% of real codebases). For exotic languages without a grammar, fall back to statistical analysis.

This gives you accuracy where it matters and coverage everywhere.

### Approach D: Universal Regex with Language Profiles

Define a small JSON/TOML profile per language that maps:
```toml
[go]
extensions = [".go"]
function_pattern = "\\bfunc\\s+\\w+"
class_pattern = "\\btype\\s+\\w+\\s+struct"
interface_pattern = "\\btype\\s+\\w+\\s+interface"
import_pattern = "import\\s+\"([^\"]+)\""
comment_line = "//"
comment_block_start = "/*"
comment_block_end = "*/"
complexity_keywords = ["if", "else", "case", "for", "range", "select", "&&", "||"]
```

**Pros:** Easy to add new languages (just a config file, no code), patterns are declarative
**Cons:** Still regex-based (fragile), still can't handle complex syntax

---

## Key Files to Read

Before making changes, read these files to understand the current implementation:

- `src/shannon_insight/models.py` — FileMetrics dataclass (the contract between scanners and primitives)
- `src/shannon_insight/analyzers/base.py` — BaseScanner ABC (the interface scanners implement)
- `src/shannon_insight/analyzers/go_analyzer.py` — Example scanner (150 lines of regex)
- `src/shannon_insight/analyzers/python_analyzer.py` — Another scanner
- `src/shannon_insight/analyzers/typescript_analyzer.py` — Another scanner
- `src/shannon_insight/primitives/extractor.py` — How FileMetrics → Primitives
- `src/shannon_insight/primitives/detector.py` — How z-scores and anomalies work
- `src/shannon_insight/primitives/fusion.py` — How signals are fused
- `src/shannon_insight/primitives/registry.py` — PrimitiveDefinition registry
- `src/shannon_insight/core.py` — `_get_scanners()` and `analyze()` pipeline
- `src/shannon_insight/config.py` — AnalysisSettings (fusion_weights, thresholds, etc.)
- `tests/test_integration.py` — Existing tests to not break

## Constraints

1. **Don't break existing functionality.** The tool must still work for Go, Python, and TypeScript codebases. Existing tests in `tests/` must pass.
2. **The output format doesn't change.** `AnomalyReport` with `Primitives` (5 named fields) is the public API. Formatters, CLI, baseline/diff mode — all stay the same.
3. **`pyproject.toml` dependencies.** If you add tree-sitter or other deps, add them to `pyproject.toml` under `[project.dependencies]`. Prefer packages that are pip-installable without system-level compilation if possible.
4. **Performance.** The tool should analyze a 500-file codebase in under 30 seconds. Don't add anything that makes per-file analysis slow (no LLM calls, no network requests).
5. **The primitive registry is extensible.** New primitives can be added by registering a `PrimitiveDefinition` and a compute method. Don't break this.

## What "Done" Looks Like

1. Running `shannon-insight .` on a mixed-language repo (Go + Python + TypeScript + Java + Rust + Ruby + C) produces meaningful, comparable results.
2. Structural entropy values are computed from a consistent vocabulary across all languages.
3. Network centrality correctly identifies hub files regardless of language.
4. Cognitive load is semantically equivalent across languages (a complex Java file and a complex Python file get comparable scores).
5. Adding support for a new language requires minimal effort (ideally zero code, or at most a small config entry).
6. `python3 -m pytest tests/` passes.

## Decision Record

Document your chosen approach and reasoning before implementing. Explain:
- Which approach (A/B/C/D/other) you chose and why
- What tradeoffs you accepted
- How you ensure cross-language comparability for each primitive
- How new languages get added in your design
