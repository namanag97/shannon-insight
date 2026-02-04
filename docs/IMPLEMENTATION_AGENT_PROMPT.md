# Implementation Agent Prompt: PRIMITIVE_REDESIGN

## Mission

You are tasked with implementing the PRIMITIVE_REDESIGN changes to the Shannon Insight code analysis system. Your goal is to replace three weak signal primitives with mathematically-grounded alternatives:

1. **Structural Entropy → Compression-Based Complexity**
2. **Semantic Coherence → Identifier-Based Coherence**
3. **Cognitive Load → Gini-Enhanced Cognitive Load**

## Context

The system currently detects *which* files are unusual but produces generic recommendations because it uses weak signals. The root causes are:
- AST node diversity ≠ quality (language-specific vocabularies)
- Imports ≠ actual responsibilities (just show dependencies)
- Total function count hides "God functions" (unequal distribution)

## Research Foundation

You MUST review the research documents before implementing:
- `/Users/namanagarwal/coding/codeanalyser/docs/research/IMPLEMENTATION_GUIDE.md` - Complete implementation code and roadmap
- `/Users/namanagarwal/coding/codeanalyser/docs/research/QUICK_REFERENCE.md` - Calibration data and quick lookup
- `/Users/namanagarwal/coding/codeanalyser/docs/research/MATHEMATICAL_FOUNDATIONS_OF_CODE_QUALITY_ANALYSIS.md` - Theoretical foundations
- `/Users/namanagarwal/coding/codeanalyser/docs/research/EMPIRICAL_VALIDATION.md` - Real-world examples

**Do NOT proceed with implementation until you have read and understood these documents.**

---

## Implementation Scope

You will implement changes in this exact order:

### Phase 1: Core Math Libraries (DO THIS FIRST)

Create three new math classes in `src/shannon_insight/math/`:

#### 1.1 Create `src/shannon_insight/math/compression.py`

```python
"""
Compression-based complexity using Kolmogorov complexity approximation.

Reference: Li & Vitanyi, "An Introduction to Kolmogorov Complexity
and Its Applications", 2008.
"""

import zlib
from typing import Literal


class Compression:
    """Compression-based complexity metrics."""

    MIN_SIZE_THRESHOLD = 512  # bytes below this, compression is unreliable

    @staticmethod
    def compression_ratio(
        content: bytes,
        algorithm: Literal["zlib", "gzip", "bzip2"] = "zlib",
        level: int = 9
    ) -> float:
        """
        Compute compression ratio as Kolmogorov complexity approximation.

        Args:
            content: Raw bytes to compress
            algorithm: Compression algorithm (default: zlib level 9)
            level: Compression level (0-9, default: 9 for maximum)

        Returns:
            Compression ratio = compressed_size / original_size in [0, 1]

        Mathematical Basis:
            K(s) ≈ |C(s)| where C is a compression function
            Ratio = |C(s)| / |s| approximates normalized K(s)

        Calibration:
            < 0.20: Highly repetitive (possible duplication)
            0.20-0.45: Normal source code
            0.45-0.65: Dense, complex
            > 0.65: Very dense or already compressed

        Edge Cases:
            - Empty or tiny files (< MIN_SIZE_THRESHOLD): Return 0.0
            - Compression failure: Return 1.0 (no compression)
        """
        if not content or len(content) < Compression.MIN_SIZE_THRESHOLD:
            return 0.0

        original_size = len(content)

        if algorithm == "zlib":
            compressed = zlib.compress(content, level=level)
        elif algorithm == "gzip":
            import gzip as gzip_module
            compressed = gzip_module.compress(content, compresslevel=level)
        elif algorithm == "bzip2":
            import bz2
            compressed = bz2.compress(content, compresslevel=level)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        compressed_size = len(compressed)

        # Compression can sometimes inflate small/already-compressed files
        if compressed_size >= original_size:
            return 1.0

        return compressed_size / original_size

    @staticmethod
    def compression_complexity(
        content: bytes,
        algorithm: Literal["zlib", "gzip", "bzip2"] = "zlib",
        level: int = 9
    ) -> float:
        """
        Compute compression complexity as inverse of compression ratio.

        Higher value = more complex (less compressible).

        Args:
            content: Raw bytes to compress
            algorithm: Compression algorithm
            level: Compression level

        Returns:
            Complexity score in [0, 1]
        """
        ratio = Compression.compression_ratio(content, algorithm, level)
        return 1.0 - ratio
```

**Requirements:**
- Follow existing code style in `math/` directory (see `entropy.py`, `statistics.py`)
- Include comprehensive docstrings with mathematical basis
- Handle all edge cases (empty, tiny, compression failure)
- Add type hints throughout

**Tests to create:** `tests/test_math_compression.py` with tests for:
- Empty content returns 0.0
- Content below threshold returns 0.0
- Highly repetitive content has low ratio (< 0.2)
- Random content has high ratio (> 0.5)
- Compression inflation returns 1.0

---

#### 1.2 Create `src/shannon_insight/math/identifier.py`

```python
"""
Identifier token extraction and semantic coherence analysis.

Extracts identifiers from source code, splits camelCase/snake_case into
semantic tokens, and analyzes responsibility clustering.
"""

import re
from typing import List, Dict, Set, Tuple
import numpy as np


class IdentifierAnalyzer:
    """Extract and analyze identifier tokens from source code."""

    # Language keywords that don't carry semantic meaning
    STOP_WORDS: Set[str] = frozenset({
        # Python
        "def", "class", "import", "from", "return", "if", "else", "elif",
        "for", "while", "with", "try", "except", "finally", "raise",
        "pass", "break", "continue", "and", "or", "not", "in", "is",
        "lambda", "yield", "async", "await", "global", "nonlocal",
        "assert", "del", "True", "False", "None",

        # Go
        "func", "var", "const", "type", "struct", "interface", "package",
        "import", "return", "if", "else", "for", "range", "go", "chan",
        "select", "defer", "recover", "make", "new", "append", "copy",
        "len", "cap", "close", "nil", "true", "false",

        # TypeScript/JavaScript
        "function", "const", "let", "var", "return", "if", "else",
        "for", "while", "do", "switch", "case", "break", "continue",
        "throw", "try", "catch", "finally", "new", "this", "super",
        "extends", "class", "interface", "type", "enum", "export", "import",
        "from", "default", "async", "await", "yield", "true", "false",
        "null", "undefined",

        # Common generic terms
        "get", "set", "is", "to", "of", "and", "or", "the", "a", "an",
    })

    @staticmethod
    def extract_identifier_tokens(content: str) -> List[str]:
        """
        Extract and split all identifiers into semantic tokens.

        Splits camelCase and snake_case into component words.
        Filters out language keywords and short fragments.

        Examples:
            "validateEmailAddress" → ["validate", "email", "address"]
            "_transform_upper" → ["transform", "upper"]
            "user_email_address" → ["user", "email", "address"]

        Args:
            content: Source code as string

        Returns:
            List of semantic tokens (lowercase, ≥3 chars)

        Mathematical Basis:
            - Identifiers are regular languages (Type-3 in Chomsky hierarchy)
            - Pumping lemma enables efficient regex recognition
            - Tokenization is language-agnostic
        """
        # Extract identifier-like tokens (words, not operators/keywords)
        raw_identifiers = re.findall(r'[a-zA-Z_]\w{2,}', content)

        tokens = []
        for ident in raw_identifiers:
            ident_lower = ident.lower()

            # Skip if it's a stop word (keyword)
            if ident_lower in IdentifierAnalyzer.STOP_WORDS:
                continue

            # Split camelCase: "validateEmail" → ["validate", "email"]
            parts = re.sub(r'([a-z])([A-Z])', r'\1 \2', ident)
            # Split snake_case and normalize
            for part in parts.replace('_', ' ').split():
                word = part.lower().strip()
                # Filter short fragments and numbers-only tokens
                if len(word) >= 3 and not word.isdigit():
                    tokens.append(word)

        return tokens

    @staticmethod
    def detect_semantic_clusters(
        tokens: List[str],
        max_clusters: int = 8,
        min_cluster_size: int = 3
    ) -> List[Dict[str, any]]:
        """
        Detect semantic responsibility clusters using K-means clustering.

        Args:
            tokens: List of semantic tokens
            max_clusters: Maximum number of clusters (default: 8)
            min_cluster_size: Minimum tokens per cluster (default: 3)

        Returns:
            List of cluster dicts with keys:
                - 'tokens': List of tokens in cluster
                - 'top_terms': Top 3 most frequent tokens
                - 'count': Number of tokens in cluster

        Mathematical Basis:
            - TF-IDF vectorization for term weighting
            - K-means objective: minimize Σ_i Σ_{x∈S_i} ||x - μ_i||²
            - Cosine similarity for text data
        """
        if not tokens:
            return []

        # Create simple token frequency map (no sklearn needed for basic version)
        from collections import Counter

        token_counts = Counter(tokens)
        unique_tokens = list(token_counts.keys())

        if len(unique_tokens) < 3:
            return [{
                'tokens': tokens,
                'top_terms': [t for t, _ in token_counts.most_common(3)],
                'count': len(tokens)
            }]

        # Simple clustering by co-occurrence (simpler than K-means)
        # For production, integrate with sklearn KMeans

        # Group by common prefixes (heuristic)
        from itertools import groupby

        sorted_tokens = sorted(unique_tokens)
        clusters_raw = []

        for prefix, group in groupby(sorted_tokens, key=lambda x: x[:3]):
            group_list = list(group)
            total_count = sum(token_counts[t] for t in group_list)

            if total_count >= min_cluster_size:
                clusters_raw.append({
                    'tokens': group_list,
                    'top_terms': sorted(group_list, key=lambda x: -token_counts[x])[:3],
                    'count': total_count
                })

        return clusters_raw

    @staticmethod
    def compute_coherence(tokens: List[str]) -> float:
        """
        Compute coherence score using term clustering.

        Args:
            tokens: List of semantic tokens

        Returns:
            Coherence score in [0, 1]
            Higher = more focused/fewer responsibilities
            Lower = mixed responsibilities

        Mathematical Basis:
            - Fewer clusters with larger groups = high coherence
            - Many small clusters = low coherence
        """
        if not tokens:
            return 0.0

        clusters = IdentifierAnalyzer.detect_semantic_clusters(tokens)

        if len(clusters) <= 1:
            return 1.0  # Single responsibility

        # Coherence = inverse of normalized cluster count
        from collections import Counter

        token_count = len(tokens)
        cluster_entropy = 0.0

        for cluster in clusters:
            p = cluster['count'] / token_count
            import math
            cluster_entropy -= p * math.log2(p)

        max_entropy = math.log2(len(clusters)) if len(clusters) > 1 else 1.0

        return 1.0 - (cluster_entropy / max_entropy) if max_entropy > 0 else 1.0
```

**Requirements:**
- Filter out language-specific keywords
- Handle camelCase and snake_case splitting
- Implement simplified clustering (can integrate sklearn later)
- Add comprehensive docstrings
- Handle empty/single-token edge cases

**Tests to create:** `tests/test_math_identifier.py` with tests for:
- Empty content returns empty list
- Single identifier returns list with semantic tokens
- camelCase splitting works correctly
- snake_case splitting works correctly
- Stop words are filtered
- Coherence is in [0, 1]

---

#### 1.3 Create `src/shannon_insight/math/gini.py`

```python
"""
Gini coefficient for inequality measurement.

The Gini coefficient is a measure of statistical dispersion intended to
represent the income or wealth distribution of a nation's residents.
Here, we apply it to function size distribution to detect
"God functions" (concentrated cognitive load).

Reference: Gini (1912) - Variabilità e Mutabilità
"""

import numpy as np
from typing import List, Union


class Gini:
    """Gini coefficient calculations for inequality measurement."""

    @staticmethod
    def gini_coefficient(
        values: Union[List[float], List[int], np.ndarray],
        bias_correction: bool = True
    ) -> float:
        """
        Compute Gini coefficient.

        Gini measures inequality in a distribution.
        0 = perfect equality (all values identical)
        1 = perfect inequality (one value, rest are zero)

        Args:
            values: Array of non-negative values
            bias_correction: If True, apply n/(n-1) correction for sample data

        Returns:
            Gini coefficient in [0, 1]

        Mathematical Formula:
            Using sorted values x₁ ≤ x₂ ≤ ... ≤ xₙ:

            G = (2 × Σ_{i=1}^{n} i × xᵢ) / (n × Σ_{i=1}^{n} xᵢ) - (n + 1) / n

            Alternative (Lorenz curve):
            G = 1 - 2 × Σ_{i=0}^{n-1} Lᵢ / n

        Calibration for Function Sizes:
            < 0.30: Generally balanced (healthy)
            0.30 - 0.50: Moderate inequality (some large functions)
            0.50 - 0.70: High inequality (likely God functions)
            ≥ 0.70: Severe inequality (definitely needs refactoring)
        """
        values_arr = np.asarray(values, dtype=np.float64)

        # Edge cases
        if len(values_arr) == 0:
            raise ValueError("Cannot compute Gini for empty array")

        if len(values_arr) == 1:
            return 0.0

        # Ensure non-negative
        if np.any(values_arr < 0):
            raise ValueError("Gini requires non-negative values")

        # Handle all zeros
        if np.all(values_arr == 0):
            return 0.0

        # Sort values
        sorted_values = np.sort(values_arr)
        n = len(sorted_values)
        cumulative = np.cumsum(sorted_values)
        total = cumulative[-1]

        # Compute Gini using sorted formulation
        gini = 1.0 - (2.0 / (n * total)) * np.sum(
            (np.arange(1, n + 1) * sorted_values)
        )

        # Bias correction for sample data
        if bias_correction and n > 1:
            gini *= n / (n - 1)

        return max(0.0, min(1.0, gini))
```

**Requirements:**
- Handle all edge cases (empty, single value, all zeros, negative values)
- Apply bias correction for sample data
- Return value clamped to [0, 1]
- Add comprehensive docstrings with calibration data

**Tests to create:** `tests/test_math_gini.py` with tests for:
- Empty array raises ValueError
- Single value returns 0.0
- All zeros returns 0.0
- Perfect inequality [0, 0, 0, 1] returns ~1.0
- Perfect equality [5, 5, 5, 5] returns 0.0
- Known values produce correct Gini

---

### Phase 2: Update Math Module Exports

**File to modify:** `src/shannon_insight/math/__init__.py`

Add exports for new classes:

```python
from .compression import Compression
from .gini import Gini
from .identifier import IdentifierAnalyzer

# ... existing exports ...
```

---

### Phase 3: Update FileMetrics Model

**File to modify:** `src/shannon_insight/models.py`

Add `function_sizes` field to `FileMetrics` dataclass:

```python
@dataclass
class FileMetrics:
    """Metrics extracted from source code by language scanners."""

    # ... existing fields ...

    function_sizes: List[int] = field(default_factory=list)
    """Line count per function, used for Gini coefficient analysis."""

    # ... rest of class ...
```

**Requirements:**
- Use `field(default_factory=list)` for mutable default
- Add docstring explaining purpose
- Maintain backward compatibility

---

### Phase 4: Update PrimitiveExtractor

**File to modify:** `src/shannon_insight/primitives/extractor.py`

You will replace/extend three compute methods:

#### 4.1 Replace `_compute_structural_entropy`

```python
def _compute_compression_complexity(self) -> Dict[str, float]:
    """Compute compression-based complexity (replaces structural_entropy)."""
    from pathlib import Path

    complexities = {}
    for file in self.files:
        file_path = Path(file.path)

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            ratio = Compression.compression_ratio(content)
            complexities[file.path] = ratio

        except Exception as e:
            logger.warning(f"Failed to compute compression for {file.path}: {e}")
            complexities[file.path] = 0.0

    return complexities
```

**Requirements:**
- Read file in binary mode ('rb')
- Use `Compression.compression_ratio()` from Phase 1
- Handle file read errors gracefully
- Log warnings for failures

#### 4.2 Update `_compute_semantic_coherence`

```python
def _compute_semantic_coherence(self) -> Dict[str, float]:
    """Compute semantic coherence via identifier tokens (replaces imports)."""
    from pathlib import Path

    coherences = {}
    for file in self.files:
        file_path = Path(file.path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tokens = IdentifierAnalyzer.extract_identifier_tokens(content)
            coherence = IdentifierAnalyzer.compute_coherence(tokens)
            coherences[file.path] = coherence

        except Exception as e:
            logger.warning(f"Failed to compute coherence for {file.path}: {e}")
            coherences[file.path] = 1.0  # Default to coherent

    return coherences
```

**Requirements:**
- Read file in text mode with UTF-8 encoding
- Use `IdentifierAnalyzer` methods from Phase 1
- Handle file read errors gracefully
- Default to 1.0 (coherent) on failure

#### 4.3 Update `_compute_cognitive_load`

```python
def _compute_cognitive_load(self) -> Dict[str, float]:
    """Compute cognitive load enhanced with Gini coefficient."""
    loads = {}

    for file in self.files:
        concepts = file.functions + file.structs + file.interfaces
        base_load = concepts * file.complexity_score * (1 + file.nesting_depth / 10)

        # Apply Gini coefficient for function size inequality
        if file.function_sizes and len(file.function_sizes) > 1:
            gini = Gini.gini_coefficient(file.function_sizes)
            # Concentration penalty: high Gini means a few functions dominate
            concentration = 1.0 + gini
        else:
            gini = 0.0
            concentration = 1.0

        loads[file.path] = base_load * concentration

    # Normalize to [0, 1] range
    if loads:
        max_load = max(loads.values())
        if max_load > 0:
            loads = {k: v / max_load for k, v in loads.items()}

    return loads
```

**Requirements:**
- Use existing base load calculation
- Add Gini coefficient for function size inequality
- Apply concentration penalty: `load × (1 + gini)`
- Normalize to [0, 1] after computation
- Handle single-function files (Gini = 0)

---

### Phase 5: Update Primitive Registry

**File to modify:** `src/shannon_insight/primitives/registry.py`

You have two options:

**Option A (Recommended):** Create new primitives with deprecation
```python
def _interpret_compression_ratio(v: float) -> str:
    """Interpret compression ratio value."""
    if v < 0.20:
        return "highly repetitive (duplication?)"
    elif v < 0.45:
        return "normal complexity"
    elif v < 0.65:
        return "dense/complex"
    else:
        return "very dense"

def _interpret_identifier_coherence(v: float) -> str:
    """Interpret identifier coherence value."""
    if v < 0.30:
        return "mixed responsibilities"
    elif v < 0.70:
        return "somewhat focused"
    else:
        return "highly focused"

# New primitives
PrimitiveDefinition(
    name="compression_complexity",
    short_name="compression",
    direction="both_extreme_bad",
    weight=0.25,
    interpret=_interpret_compression_ratio
),

PrimitiveDefinition(
    name="identifier_coherence",
    short_name="id_coherence",
    direction="both_extreme_bad",  # Low = mixed concerns, High = one giant module
    weight=0.25,
    interpret=_interpret_identifier_coherence
),

# Keep old structural_entropy for backward compatibility but mark deprecated
PrimitiveDefinition(
    name="structural_entropy",
    short_name="entropy",
    direction="both_extreme_bad",
    weight=0.0,  # Deprecated, zero weight
    interpret=lambda v: "deprecated (use compression_complexity)"
),
```

**Option B:** Replace in-place (breaking change)
- Rename `structural_entropy` → `compression_complexity`
- Rename `semantic_coherence` → `identifier_coherence`
- Update `cognitive_load` computation to use Gini

**Decision:** Use Option A for backward compatibility.

---

### Phase 6: Update AnomalyDetector

**File to modify:** `src/shannon_insight/primitives/detector.py`

Update `_flag_primitives` to handle new primitive names and directions:

```python
def _flag_primitives(self, prims: Primitives, thresh: float) -> List[str]:
    """Use registry direction metadata to flag anomalous primitives."""
    prim_d = self._prim_dict(prims)
    flags: List[str] = []

    for defn in self._registry:
        z = prim_d.get(defn.name, 0.0)

        if defn.name == "compression_complexity":
            # both_extreme_bad: flag both high and low
            if abs(z) > thresh:
                direction = "high" if z > 0 else "low"
                flags.append(f"compression_{direction}")

        elif defn.name == "identifier_coherence":
            # both_extreme_bad: flag both high and low
            if abs(z) > thresh:
                direction = "low" if z < 0 else "high"
                flags.append(f"coherence_{direction}")

        # ... existing flagging logic for other primitives ...
```

---

### Phase 7: Update Test Files

**Files to update:**
- `tests/test_baseline.py` - Update test data with new metrics
- `tests/test_integration.py` - Add integration tests for new metrics
- `tests/test_formatters.py` - Update formatter tests

---

## Testing Requirements

### Unit Tests

For each new math class, create comprehensive unit tests:

```python
# tests/test_math_compression.py
class TestCompressionRatio:
    def test_empty_content(self):
        assert Compression.compression_ratio(b"") == 0.0

    def test_below_threshold(self):
        assert Compression.compression_ratio(b"a" * 100) == 0.0

    def test_repetitive_content(self):
        # Repeated pattern should compress well
        content = b"abc" * 1000
        ratio = Compression.compression_ratio(content)
        assert ratio < 0.3

    def test_random_content(self):
        # Random content shouldn't compress well
        import os
        content = os.urandom(1000)
        ratio = Compression.compression_ratio(content)
        assert ratio > 0.5

    def test_compression_inflation(self):
        # Already compressed content may inflate
        compressed = zlib.compress(b"x" * 1000)
        ratio = Compression.compression_ratio(compressed)
        assert ratio == 1.0


# tests/test_math_identifier.py
class TestIdentifierExtraction:
    def test_empty_content(self):
        assert IdentifierAnalyzer.extract_identifier_tokens("") == []

    def test_camel_case_splitting(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens("validateEmailAddress")
        assert "validate" in tokens
        assert "email" in tokens
        assert "address" in tokens

    def test_snake_case_splitting(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens("user_email_address")
        assert "user" in tokens
        assert "email" in tokens
        assert "address" in tokens

    def test_stop_words_filtered(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens("def return if")
        assert "def" not in tokens
        assert "return" not in tokens
        assert "if" not in tokens


# tests/test_math_gini.py
class TestGiniCoefficient:
    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Gini.gini_coefficient([])

    def test_single_value_zero(self):
        assert Gini.gini_coefficient([42]) == 0.0

    def test_perfect_equality(self):
        assert Gini.gini_coefficient([5, 5, 5, 5]) == 0.0

    def test_perfect_inequality(self):
        # [0, 0, 0, 1] should give Gini ≈ 1
        gini = Gini.gini_coefficient([0, 0, 0, 1])
        assert gini > 0.9

    def test_moderate_inequality(self):
        gini = Gini.gini_coefficient([1, 2, 3, 10])
        assert 0.3 < gini < 0.6
```

### Integration Tests

Create integration test to verify end-to-end behavior:

```python
# tests/test_integration.py
class TestNewPrimitivesIntegration:
    def test_compression_complexity_computed(self, test_codebase):
        """Verify compression_complexity is computed for all files."""
        # Run full pipeline
        # Check compression_complexity values exist
        # Verify values in expected range [0, 1]

    def test_identifier_coherence_computed(self, test_codebase):
        """Verify identifier_coherence is computed for all files."""
        # Run full pipeline
        # Check identifier_coherence values exist
        # Verify values in expected range [0, 1]

    def test_gini_enhanced_cognitive_load(self, test_codebase):
        """Verify cognitive_load uses Gini coefficient."""
        # Create test file with unequal function sizes
        # Verify higher cognitive load than equal-sized equivalent
```

---

## Validation Criteria

Before declaring implementation complete, verify:

### 1. Code Quality
- [ ] All new code follows PEP 8 style
- [ ] All functions have type hints
- [ ] All functions have comprehensive docstrings
- [ ] No TODO or FIXME comments left in code
- [ ] All imports are used and organized

### 2. Mathematical Correctness
- [ ] Compression ratio is in [0, 1]
- [ ] Gini coefficient is in [0, 1]
- [ ] Coherence is in [0, 1]
- [ ] Edge cases handled (empty, single value, all zeros)
- [ ] Negative values rejected with appropriate errors

### 3. Integration
- [ ] New math classes imported in `__init__.py`
- [ ] `FileMetrics` has `function_sizes` field
- [ ] `PrimitiveExtractor` methods read files correctly
- [ ] Registry entries created for new primitives
- [ ] Old primitives deprecated with weight=0

### 4. Testing
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Test coverage > 90% for new code
- [ ] Edge cases tested explicitly

### 5. Backward Compatibility
- [ ] Existing API unchanged where possible
- [ ] Deprecation warnings issued for old metrics
- [ ] Existing test suites still pass

---

## Error Handling Requirements

For all file operations:

```python
try:
    with open(file_path, 'rb') as f:
        content = f.read()
    # Compute metric
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    return default_value
except PermissionError:
    logger.error(f"Permission denied: {file_path}")
    return default_value
except UnicodeDecodeError:
    logger.warning(f"Unicode decode error: {file_path}, trying latin-1")
    with open(file_path, 'r', encoding='latin-1') as f:
        content = f.read()
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return default_value
```

---

## Performance Considerations

1. **Compression:**
   - Reading entire file into memory is necessary
   - For very large files (>10MB), consider streaming compression
   - Caching: Cache compression ratio per file hash

2. **Identifier Analysis:**
   - Regex tokenization is O(n) where n = file size
   - For large codebases, parallelize per-file processing

3. **Gini Coefficient:**
   - Sorting is O(n log n) where n = number of functions
   - Typically n < 100, so performance is negligible

---

## Documentation Updates

After implementation, update:

1. **README.md** - Add new primitives to feature list
2. **CHANGELOG.md** - Document breaking changes and deprecations
3. **API docs** - Document new classes and methods

---

## Common Mistakes to Avoid

❌ **Do NOT:**
- Forget to handle empty files
- Return values outside expected ranges [0, 1]
- Ignore Unicode encoding issues
- Create breaking changes without deprecation warnings
- Skip unit tests for edge cases
- Use `eval()` or similar unsafe functions
- Hardcode file paths (use `Path` and configuration)

✅ **Do:**
- Handle all edge cases explicitly
- Log warnings for non-fatal errors
- Return sensible defaults on failure
- Write comprehensive docstrings
- Test with real code (Python, Go, TypeScript)
- Follow existing code patterns in the codebase

---

## Sequence of Operations

Follow this exact sequence:

1. **STOP** - Read all research documents first
2. **Phase 1** - Create three math classes with full tests
3. **Phase 2** - Update `math/__init__.py` exports
4. **Phase 3** - Update `FileMetrics` model
5. **Phase 4** - Update `PrimitiveExtractor` methods
6. **Phase 5** - Update `registry.py` (Option A: deprecate)
7. **Phase 6** - Update `detector.py` flagging logic
8. **Phase 7** - Update existing tests
9. **Validation** - Run all tests, check code quality
10. **Documentation** - Update README, CHANGELOG

---

## Success Criteria

Implementation is successful when:

- ✅ All three new math classes implemented and tested
- ✅ FileMetrics includes `function_sizes`
- ✅ PrimitiveExtractor computes new metrics
- ✅ Registry updated with new primitives
- ✅ All existing tests pass
- ✅ New tests have >90% coverage
- ✅ Code passes linting and type checking
- ✅ Documentation updated
- ✅ System can analyze real codebases without errors

---

## Final Instructions

1. **Read first:** Before writing any code, read all research documents
2. **Test early:** Write tests alongside implementation (TDD)
3. **Verify math:** Double-check formulas against research documents
4. **Handle errors:** Graceful degradation, not crashes
5. **Maintain compatibility:** Don't break existing APIs without warning
6. **Log everything:** Use logger for warnings and errors
7. **Review your work:** Before finalizing, re-read and verify

**Good luck! You have all the research, code examples, and instructions needed to implement PRIMITIVE_REDESIGN correctly.**
