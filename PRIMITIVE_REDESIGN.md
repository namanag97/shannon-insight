# Primitive Redesign — Signal Quality Over Signal Quantity

## The Problem

The 5 current primitives detect *which* files are unusual, but the recommendations they produce are generic platitudes. The root cause isn't the recommendation engine — it's that two of the five primitives are computed from weak signals, so downstream analysis built on them can't be specific.

| Primitive | Current signal | Problem |
|-----------|---------------|---------|
| Structural Entropy | AST node type distribution | Diversity ≠ quality. A file with evenly distributed `if/for/return/function` has high entropy but could be perfectly clean. Also uses language-specific node vocabularies that aren't comparable across languages. |
| Semantic Coherence | TF-IDF on import + export names | Imports are a terrible proxy for what a file *does*. A Python file importing `os, sys, json, logging, re` gets low coherence because those are "diverse" — but that's just a normal Python file. The imports don't reveal that the file mixes validation, transformation, and caching concerns. |
| Cognitive Load | `(functions + structs + interfaces) × complexity × nesting` | Treats all functions as equal. 10 two-line helpers are easier to understand than 3 deeply-nested 50-line functions. The count×complexity formula is too crude. |
| Network Centrality | PageRank on import graph | **Good.** The import graph is real, measurable, and meaningful. Keep as-is. |
| Churn Volatility | File modification time | **Good.** Objective and language-agnostic. Keep as-is. |

Two primitives are solid (centrality, volatility). Three need better signals (entropy, coherence, cognitive load).

---

## Proposed Changes

### 1. Replace Structural Entropy with Compression-Based Complexity

**Current:** Shannon entropy of AST node type Counter (e.g., `{function: 5, if: 12, for: 3, return: 8}`).

**Problem:** This measures diversity of *node types*, not structural complexity. A file with many different node types used evenly gets high entropy, but that might be a well-organized file with a healthy mix of functions, conditionals, and loops. Conversely, a file that's 90% if-statements gets low entropy but is genuinely problematic. The metric measures the wrong thing. Additionally, each language produces a different set of node types (Go has `defer/chan/go`, Python has `yield/with/decorator`, TypeScript has `hook/jsx`), making cross-language comparison impossible.

**Proposed:** Compression ratio as a Kolmogorov complexity approximation.

```python
import zlib

def compression_complexity(content: bytes) -> float:
    """Ratio of compressed size to original size. Higher = more complex/unique."""
    if len(content) < 10:
        return 0.0
    compressed = zlib.compress(content, level=9)
    return len(compressed) / len(content)
```

**Why this is better:**
- **Language-agnostic.** Works identically on Go, Python, TypeScript, Java, Rust, Ruby, C, or any text file. No parser needed.
- **Mathematically grounded.** Compression ratio approximates normalized Kolmogorov complexity — the fundamental measure of information content in a string (Li & Vitanyi, "An Introduction to Kolmogorov Complexity and Its Applications", 2008).
- **Captures what we actually care about.** Repetitive copy-paste code compresses well (low ratio ≈ simple/duplicated). Diverse, dense code compresses poorly (high ratio ≈ genuinely complex). This is what "structural complexity" actually means.
- **Handles the cross-language problem entirely.** No node type vocabulary to standardize.

**Calibration:**
- Typical compression ratios for source code: 0.20–0.45
- Below 0.20: highly repetitive (possible duplication)
- Above 0.45: very dense/complex
- The z-score normalization will handle per-codebase calibration automatically.

**Direction for the registry:** `"both_extreme_bad"` — very low (duplication) and very high (incomprehensible density) are both concerning.

---

### 2. Replace Semantic Coherence with Identifier-Based Responsibility Coherence

**Current:** TF-IDF cosine similarity on import/export names, averaged across all other files.

**Problem:** Imports tell you what *libraries* a file uses, not what *responsibilities* it handles. A file that imports `os, json, re, logging` is using standard libraries — that's normal, not a sign of mixed concerns. Meanwhile, a file whose function names span `validate_email`, `cache_result`, `transform_upper`, `log_middleware` is clearly handling multiple responsibilities — but the current metric can't see that because it only looks at import names.

**Proposed:** TF-IDF on identifier tokens extracted from the file's own content.

```python
import re

def extract_identifier_tokens(content: str) -> List[str]:
    """Extract and split all identifiers from source code into semantic tokens.

    Splits camelCase and snake_case into component words.
    E.g., "validateEmailAddress" → ["validate", "email", "address"]
         "_transform_upper"     → ["transform", "upper"]
    """
    # Extract identifier-like tokens (words, not operators/keywords)
    raw_identifiers = re.findall(r'[a-zA-Z_]\w{2,}', content)

    tokens = []
    for ident in raw_identifiers:
        # Split camelCase: "validateEmail" → ["validate", "Email"]
        parts = re.sub(r'([a-z])([A-Z])', r'\1_\2', ident)
        # Split snake_case and normalize
        for part in parts.split('_'):
            word = part.lower().strip()
            if len(word) >= 3:  # skip short fragments
                tokens.append(word)

    return tokens
```

Then compute coherence as: how tightly clustered are this file's identifier tokens compared to a uniform distribution?

**Two coherence measures:**

**(a) Internal coherence (self-similarity):** How much vocabulary overlap exists within the file? Take the identifier tokens, split into two halves, compute cosine similarity between their TF-IDF vectors. A focused file's first half and second half use the same vocabulary. A God-class file's halves are about different things.

**(b) Cross-file coherence (current approach, better signal):** Replace the TF-IDF document corpus — instead of `imports + exports`, use `extract_identifier_tokens(content)`. Now the similarity between two files reflects whether they're *about the same things* (shared domain vocabulary), not just whether they import the same libraries.

**Why this is better:**
- **Measures actual responsibility mixing.** A file full of `validate_*`, `check_*`, `is_valid_*` functions is coherent. A file with `validate_*`, `cache_*`, `transform_*`, `log_*` is incoherent. Identifiers carry semantic intent.
- **Language-agnostic.** Every language uses identifiers. camelCase/snake_case splitting works everywhere.
- **Enables specific recommendations.** Once you have identifier clusters, you can tell the developer *what* the clusters are: "This file has 3 responsibility groups: validation (validate, check, required, pattern), transformation (transform, trim, upper, sanitize), and caching (cache, key, ttl). Consider splitting along these lines."

**Direction for the registry:** `"both_extreme_bad"` — very low coherence means mixed responsibilities; very high coherence across all files could mean everything is in one module.

---

### 3. Improve Cognitive Load with Function Size Distribution

**Current:** `(functions + structs + interfaces) × complexity_score × (1 + nesting_depth / 10)`

**Problem:** Treats all functions as equal. Consider two files, each with 10 functions:
- File A: 10 functions, each 5 lines, max nesting 2 → easy to understand
- File B: 8 functions of 3 lines + 2 functions of 80 lines with nesting 6 → hard to understand

The current formula gives them similar scores because `functions=10` is the same. But File B's cognitive load is concentrated in those 2 monster functions.

**Proposed:** Incorporate function size variance and max function size.

This requires scanners to extract per-function line counts, not just a total count. The `FileMetrics` model would gain a new field:

```python
@dataclass
class FileMetrics:
    # ... existing fields ...
    function_sizes: List[int]  # line count per function, e.g. [5, 3, 80, 3, 45, ...]
```

Then cognitive load becomes:

```python
def cognitive_load(metrics: FileMetrics) -> float:
    n_concepts = metrics.functions + metrics.structs + metrics.interfaces

    if metrics.function_sizes:
        max_fn_size = max(metrics.function_sizes)
        size_variance = statistics.variance(metrics.function_sizes) if len(metrics.function_sizes) > 1 else 0
        # Gini coefficient of function sizes — measures inequality of code distribution
        gini = gini_coefficient(metrics.function_sizes)
    else:
        max_fn_size = metrics.lines
        size_variance = 0
        gini = 0

    # Base load from concept count and complexity
    base = n_concepts * metrics.complexity_score * (1 + metrics.nesting_depth / 10)

    # Concentration penalty: high Gini means a few functions dominate
    # A file with equal-sized functions (Gini ≈ 0) is easier to understand
    # A file with one 200-line function and ten 3-liners (Gini ≈ 0.8) is harder
    concentration = 1 + gini

    return base * concentration
```

**Why this is better:**
- **Captures the "God function" pattern.** The most common cognitive load problem isn't "too many functions" — it's "one or two functions that are impossibly long and complex." The Gini coefficient detects this.
- **Enables specific recommendations.** With `function_sizes`, you can say: "Function at line 174 is 80 lines (4× the median). Extract the inner loop at line 210 into a helper."
- **Still simple to compute.** Scanners already regex for function definitions. Measuring line span between consecutive function definitions gives approximate function sizes.

**Gini coefficient:** A standard measure of inequality used in economics. 0 = perfect equality (all functions same size), 1 = perfect inequality (one function has all the lines). Well-understood, easy to compute, meaningful to report.

```python
def gini_coefficient(values: List[int]) -> float:
    """Compute Gini coefficient. 0 = equal, 1 = maximally unequal."""
    if not values or all(v == 0 for v in values):
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cumulative = sum((2 * i - n + 1) * v for i, v in enumerate(sorted_vals))
    return cumulative / (n * sum(sorted_vals))
```

---

## What Doesn't Change

- **Network centrality (PageRank on import graph).** The import graph is a real, measurable structure. PageRank correctly identifies hub files. The only improvement needed is better import extraction per language (covered by the cross-language scanner work).

- **Churn volatility (file modification time).** Objective, language-agnostic, meaningful. No changes needed. A future enhancement could use `git log` for real commit-based churn, but mtime is a reasonable proxy.

- **The pipeline architecture.** `Scanner → FileMetrics → PrimitiveExtractor → AnomalyDetector → SignalFusion → RecommendationEngine` stays the same. The changes are *within* the extractor (better formulas) and scanners (extract function sizes).

- **The registry system.** PrimitiveDefinition with name, direction, weight, interpret callback. New primitives or modified ones register the same way.

---

## What the Recommendations Become

### Before (current):

```
Root Causes:
  ! Complex file with chaotic organization
  ! High cognitive load: 27 functions, complexity=84, nesting=6

Recommendations:
  -> Reduce nesting depth (currently 6) — flatten deeply nested conditionals
  -> Split file into smaller, focused modules
  -> Extract helper functions to reduce complexity
```

### After (with improved primitives):

```
Root Causes:
  ! High cognitive load concentrated in 2 functions (lines 174-254 and 80-115),
    which account for 60% of complexity (Gini=0.72)
  ! 3 distinct responsibility clusters detected in identifier analysis:
    validation (validate, required, pattern, range, type)
    transformation (transform, trim, upper, sanitize, hash, encode)
    caching/middleware (cache, middleware, metrics, log)

Recommendations:
  -> Extract validation logic (_validate_required, _validate_type,
     _validate_pattern, _validate_range) into a validators module
  -> Extract transformation logic (_transform_trim, _transform_upper,
     _transform_lower, _transform_sanitize, _transform_hash,
     _transform_encode) into a transformers module
  -> Flatten _parse_validators (deepest nesting at 6 levels) using
     a dispatch dict instead of if/elif chain
```

The difference: the first tells you what you already know. The second tells you what to do.

---

## Implementation Sequence

### Step 1: Compression complexity (replaces structural entropy)

- Modify `PrimitiveExtractor._compute_structural_entropy()` → `_compute_compression_complexity()`
- Update registry entry: name stays `structural_entropy` for backward compat, or rename to `compression_complexity`
- No scanner changes needed — just reads `content` from file (already available in scanners, pass raw content through FileMetrics or compute at extraction time)
- Solves cross-language vocabulary problem immediately

**FileMetrics change:** Add `raw_content: Optional[str] = None` field, or compute at extraction time by re-reading files.

### Step 2: Identifier-based coherence (replaces import TF-IDF)

- Modify `PrimitiveExtractor._compute_semantic_coherence()`
- Replace `imports + exports` corpus with `extract_identifier_tokens(content)`
- Same TF-IDF + cosine similarity machinery, better input signal
- Also compute per-file identifier clusters (KMeans or simple prefix grouping) for recommendation engine

**FileMetrics change:** Add `identifier_tokens: List[str] = field(default_factory=list)` or compute at extraction time.

### Step 3: Function size distribution (improves cognitive load)

- Modify scanners to extract function line spans → `function_sizes: List[int]`
- Modify `PrimitiveExtractor._compute_cognitive_load()` to use Gini coefficient
- Update recommendation engine to report specific large functions

**FileMetrics change:** Add `function_sizes: List[int] = field(default_factory=list)`.

### Step 4: Recommendation engine uses new data

- Identifier clusters → "Extract these functions into a X module"
- Function sizes → "Function at line N is X lines, 4× the median"
- Compression ratio extremes → "File is highly repetitive, possible duplication" or "File is extremely dense"

---

## Open Questions

1. **Should `structural_entropy` be renamed?** Changing the primitive name breaks config files that reference `fusion_weights["structural_entropy"]`. Option: keep the name but change the computation. Or: add `compression_complexity` as a new primitive and deprecate `structural_entropy`.

2. **How to get file content into the extractor?** Currently scanners produce `FileMetrics` which doesn't include raw content (just extracted counts). Options: (a) add `raw_content` to FileMetrics, (b) have the extractor re-read files from disk, (c) compute compression ratio in the scanner itself and add it as a FileMetrics field.

3. **Identifier extraction vs. language keywords.** The identifier extractor will pick up language keywords (`def`, `class`, `import`, `function`, `const`). These should be filtered out since they don't carry semantic meaning. Need a stop-word list for common programming keywords across languages.

4. **Function size extraction accuracy.** Regex-based function boundary detection is approximate. For Python (indentation-based), it's especially tricky — where does a function end? Using the "next function definition at the same or lesser indentation" heuristic is imperfect. Tree-sitter (if adopted) solves this perfectly.
