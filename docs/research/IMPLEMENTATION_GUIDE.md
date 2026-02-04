# Implementation Guide: PRIMITIVE_REDESIGN Metrics

## Quick Start

This guide provides concrete implementation steps for the three PRIMITIVE_REDESIGN metrics:
1. **Compression-Based Complexity** (replaces AST entropy)
2. **Identifier-Based Coherence** (replaces import coherence)
3. **Gini-Enhanced Cognitive Load** (improves cognitive load)

---

## File Structure Changes

```
src/shannon_insight/
├── math/
│   ├── __init__.py
│   ├── entropy.py          # Keep (used in other places)
│   ├── statistics.py       # Keep
│   ├── graph.py           # Keep
│   ├── robust.py          # Keep
│   ├── fusion.py          # Keep
│   ├── compression.py      # NEW: Compression complexity
│   ├── identifier.py      # NEW: Identifier token extraction
│   └── gini.py           # NEW: Gini coefficient
├── primitives/
│   ├── __init__.py
│   ├── extractor.py       # MODIFY: Use new metrics
│   ├── detector.py        # Keep
│   ├── fusion.py         # Keep
│   └── recommendations.py # MODIFY: Use new data
├── analyzers/
│   ├── base.py           # MODIFY: Extract function_sizes
│   ├── python_analyzer.py # MODIFY: Extract function_sizes
│   ├── go_analyzer.py    # MODIFY: Extract function_sizes
│   └── typescript_analyzer.py # MODIFY: Extract function_sizes
└── models.py            # MODIFY: Add function_sizes field
```

---

## 1. Compression-Based Complexity

### File: `math/compression.py`

```python
"""Compression-based complexity analysis using Kolmogorov complexity approximation."""

import zlib
from typing import Union


class Compression:
    """Compression-based metrics for code complexity analysis."""
    
    @staticmethod
    def compression_ratio(content: Union[str, bytes], 
                      algorithm: str = "zlib", 
                      level: int = 9) -> float:
        """
        Compute compression ratio as approximation of Kolmogorov complexity.
        
        Formula: ratio = compressed_size / original_size
        
        Lower values indicate high repetition (possible duplication).
        Higher values indicate high informational diversity (complexity).
        
        Args:
            content: Text or bytes to compress
            algorithm: Compression algorithm ('zlib', 'gzip', 'lzma', 'bz2')
            level: Compression level (1-9 for zlib/gzip, 0-9 for others)
        
        Returns:
            Compression ratio in [0, 1]
        
        Calibration:
            < 0.20: Highly repetitive (possible duplication)
            0.20-0.35: Normal code
            0.35-0.45: Moderately complex
            > 0.45: Very dense/complex
            
        Reference:
            Li & Vitányi (2008) - Kolmogorov complexity bounds:
            K(s) ≤ |C(s)| ≤ K(s) + O(1)
        """
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        else:
            content_bytes = content
        
        if len(content_bytes) < 10:
            return 0.0
        
        # Select compressor
        if algorithm == "zlib":
            compressed = zlib.compress(content_bytes, level=level)
        elif algorithm == "gzip":
            import gzip
            compressed = gzip.compress(content_bytes, compresslevel=level)
        elif algorithm == "lzma":
            import lzma
            compressed = lzma.compress(content_bytes, preset=level)
        elif algorithm == "bz2":
            import bz2
            compressed = bz2.compress(content_bytes, compresslevel=level)
        else:
            raise ValueError(f"Unknown compression algorithm: {algorithm}")
        
        return len(compressed) / len(content_bytes)
    
    @staticmethod
    def compute_file_ratio(filepath: str, 
                        algorithm: str = "zlib",
                        level: int = 9) -> float:
        """
        Compute compression ratio for a file.
        
        Args:
            filepath: Path to file
            algorithm: Compression algorithm
            level: Compression level
        
        Returns:
            Compression ratio
        """
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            return Compression.compression_ratio(content, algorithm, level)
        except (IOError, OSError):
            return 0.0


# Test the implementation
if __name__ == "__main__":
    # Simple code (should have low ratio)
    simple_code = """
def add(a, b):
    return a + b

def mul(a, b):
    return a * b
"""
    print(f"Simple code ratio: {Compression.compression_ratio(simple_code):.3f}")
    
    # Complex code (should have higher ratio)
    complex_code = """
def validate_email(email):
    if not email or '@' not in email:
        return False
    if '.' not in email.split('@')[1]:
        return False
    return True

def transform_upper(text):
    return text.upper()

def cache_result(key, value):
    return {key: value}

def log_error(error):
    print(error)
"""
    print(f"Complex code ratio: {Compression.compression_ratio(complex_code):.3f}")
```

### Integration: Modify `PrimitiveExtractor`

```python
# In src/shannon_insight/primitives/extractor.py

from ..math import Compression, Entropy

class PrimitiveExtractor:
    def __init__(self, files, cache=None, config_hash=""):
        self.files = files
        self.file_map = {f.path: f for f in files}
        # ... existing init code ...
    
    def _compute_structural_entropy(self) -> Dict[str, float]:
        """OLD: Compute normalized entropy of AST node type distribution."""
        entropies = {}
        for file in self.files:
            if not file.ast_node_types or sum(file.ast_node_types.values()) == 0:
                entropies[file.path] = 0.0
                continue
            entropies[file.path] = Entropy.normalized(file.ast_node_types)
        return entropies
    
    def _compute_compression_complexity(self) -> Dict[str, float]:
        """NEW: Compute compression ratio as complexity metric."""
        ratios = {}
        for file in self.files:
            try:
                # Read file content
                filepath = file.path if file.path.startswith('/') else \
                    f"{self.root_dir}/{file.path}"
                ratios[file.path] = Compression.compute_file_ratio(filepath)
            except Exception:
                ratios[file.path] = 0.0
        return ratios
```

### Update Registry

```python
# In src/shannon_insight/primitives/registry.py

PRIMITIVE_REGISTRY = [
    # OLD: Structural entropy
    PrimitiveDefinition(
        name="structural_entropy",
        direction="high_bad",
        weight=0.20,
        interpret=lambda x: interpret_structural_entropy(x),
        deprecated=True,  # Mark as deprecated
        replacement="compression_complexity"
    ),
    
    # NEW: Compression complexity
    PrimitiveDefinition(
        name="compression_complexity",
        direction="both_extreme_bad",  # Both low (duplication) and high (density) are bad
        weight=0.20,
        interpret=lambda x: interpret_compression_complexity(x),
    ),
    
    # ... other primitives ...
]

def interpret_compression_complexity(value: float) -> Interpretation:
    """Interpret compression complexity value."""
    if value < 0.20:
        return Interpretation(
            level="warning",
            message="High code repetition detected. Possible duplication.",
            recommendation="Review for copy-paste patterns; extract common abstractions."
        )
    elif value > 0.45:
        return Interpretation(
            level="warning",
            message="Very high informational density. Code may be difficult to understand.",
            recommendation="Consider breaking into smaller, focused functions."
        )
    else:
        return Interpretation(
            level="info",
            message="Normal structural complexity.",
            recommendation=None
        )
```

---

## 2. Identifier-Based Coherence

### File: `math/identifier.py`

```python
"""Identifier token extraction and semantic analysis."""

import re
from typing import List, Set


class IdentifierAnalyzer:
    """Extract and analyze identifier tokens from source code."""
    
    # Combined stop words for all supported languages
    STOP_WORDS = {
        # Python
        'def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif',
        'for', 'while', 'with', 'try', 'except', 'finally', 'raise',
        'pass', 'break', 'continue', 'and', 'or', 'not', 'in', 'is',
        'lambda', 'yield', 'async', 'await', 'global', 'nonlocal',
        'assert', 'del',
        # Go
        'func', 'package', 'import', 'return', 'if', 'else', 'for', 'range',
        'select', 'switch', 'case', 'default', 'defer', 'go', 'chan',
        'var', 'const', 'type', 'struct', 'interface', 'map', 'break',
        'continue', 'fallthrough', 'goto', 'range',
        # TypeScript/JavaScript
        'function', 'const', 'let', 'var', 'return', 'if', 'else',
        'for', 'while', 'switch', 'case', 'default', 'break', 'continue',
        'try', 'catch', 'finally', 'throw', 'new', 'this', 'super',
        'extends', 'implements', 'interface', 'type', 'enum', 'async',
        'await', 'yield', 'class', 'constructor', 'static', 'get', 'set',
        'of', 'in', 'instanceof', 'typeof', 'void', 'null', 'undefined',
        # Java
        'public', 'private', 'protected', 'static', 'final', 'abstract',
        'class', 'interface', 'extends', 'implements', 'throws',
        # Common verbs that appear often but don't reveal domain
        'get', 'set', 'has', 'is', 'to', 'from', 'with', 'by',
        'item', 'data', 'result', 'value', 'key', 'name'
    }
    
    @staticmethod
    def extract_identifiers(content: str) -> List[str]:
        """
        Extract all identifier-like tokens from source code.
        
        Pattern: [a-zA-Z_][a-zA-Z0-9_]{2,}
        - Starts with letter or underscore
        - Followed by 2+ word characters (filters single-letter variables)
        """
        return re.findall(r'[a-zA-Z_]\w{2,}', content)
    
    @staticmethod
    def split_identifier(identifier: str) -> List[str]:
        """
        Split identifier into semantic tokens.
        
        Examples:
            validateEmailAddress -> ['validate', 'email', 'address']
            _transform_upper -> ['transform', 'upper']
            get_full_name -> ['get', 'full', 'name']
            XMLParser -> ['xml', 'parser']
        """
        # Remove leading underscore
        identifier = identifier.lstrip('_')
        
        # Handle consecutive uppercase (XML -> xml)
        # Split before uppercase that follows lowercase
        parts = re.sub(r'([a-z])([A-Z])', r'\1_\2', identifier)
        # Handle consecutive uppercase (XMLParser -> XML_Parser)
        parts = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', parts)
        
        # Split on underscore and lowercase everything
        tokens = [token.lower() for token in parts.split('_') if token]
        
        return tokens
    
    @staticmethod
    def extract_semantic_tokens(content: str) -> List[str]:
        """
        Extract semantic tokens from source code.
        
        Process:
        1. Extract all identifiers
        2. Split each identifier into tokens
        3. Filter out stop words and short fragments
        4. Return semantic tokens
        
        Args:
            content: Source code as string
        
        Returns:
            List of semantic tokens
        """
        identifiers = IdentifierAnalyzer.extract_identifiers(content)
        tokens = []
        
        for ident in identifiers:
            for token in IdentifierAnalyzer.split_identifier(ident):
                # Filter: length >= 3 and not a stop word
                if len(token) >= 3 and token not in IdentifierAnalyzer.STOP_WORDS:
                    tokens.append(token)
        
        return tokens
    
    @staticmethod
    def detect_semantic_clusters(tokens: List[str], 
                               min_cluster_size: int = 3) -> List[dict]:
        """
        Detect semantic clusters (responsibility groups) in tokens.
        
        Uses simple frequency-based clustering:
        1. Count token frequencies
        2. Identify tokens that appear frequently together
        3. Group into clusters
        
        Args:
            tokens: List of semantic tokens
            min_cluster_size: Minimum tokens per cluster
        
        Returns:
            List of clusters with name and tokens
        """
        from collections import Counter
        
        # Count frequencies
        freq = Counter(tokens)
        
        # Simple heuristic: group by prefix or common themes
        # This is a simplified approach; production could use clustering algorithms
        
        # Domain prefixes
        prefixes = ['validate', 'check', 'required',  # validation
                   'transform', 'trim', 'upper', 'lower', 'sanitize',  # transformation
                   'cache', 'middleware', 'metrics', 'log']  # middleware
        
        clusters = []
        used_tokens = set()
        
        for prefix in prefixes:
            cluster_tokens = [t for t in tokens if t.startswith(prefix[:4])]
            if len(cluster_tokens) >= min_cluster_size:
                cluster = {
                    'name': prefix,
                    'tokens': list(set(cluster_tokens)),
                    'count': len(cluster_tokens)
                }
                clusters.append(cluster)
                used_tokens.update(cluster_tokens)
        
        # Add remaining tokens as "other"
        other_tokens = [t for t in tokens if t not in used_tokens]
        if other_tokens:
            clusters.append({
                'name': 'other',
                'tokens': list(set(other_tokens)),
                'count': len(other_tokens)
            })
        
        return clusters


# Test the implementation
if __name__ == "__main__":
    # Test identifier splitting
    examples = [
        'validateEmailAddress',
        '_transform_upper',
        'get_full_name',
        'XMLParser',
        'UserProcessor'
    ]
    
    print("Identifier splitting examples:")
    for example in examples:
        tokens = IdentifierAnalyzer.split_identifier(example)
        print(f"  {example:25s} -> {tokens}")
    
    # Test token extraction
    test_code = """
def validate_email(email: str) -> bool:
    return '@' in email

def cache_result(key: str, value: any) -> dict:
    return {key: value}

def transform_upper(text: str) -> str:
    return text.upper()
"""
    
    tokens = IdentifierAnalyzer.extract_semantic_tokens(test_code)
    print(f"\nSemantic tokens: {tokens}")
    
    clusters = IdentifierAnalyzer.detect_semantic_clusters(tokens)
    print(f"\nDetected clusters:")
    for cluster in clusters:
        print(f"  {cluster['name']:12s}: {cluster['tokens']}")
```

### Integration: Modify `PrimitiveExtractor`

```python
# In src/shannon_insight/primitives/extractor.py

from ..math import IdentifierAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class PrimitiveExtractor:
    def __init__(self, files, cache=None, config_hash=""):
        self.files = files
        # ... existing init code ...
    
    def _compute_semantic_coherence(self) -> Dict[str, float]:
        """NEW: Compute coherence via identifier-based TF-IDF."""
        
        # Build documents from identifier tokens
        documents = []
        paths = []
        token_map = {}  # Store tokens for each file for clustering
        
        for file in self.files:
            try:
                filepath = self._get_filepath(file.path)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tokens = IdentifierAnalyzer.extract_semantic_tokens(content)
                doc = " ".join(tokens) if tokens else "empty"
                documents.append(doc)
                paths.append(file.path)
                token_map[file.path] = tokens
            except Exception:
                documents.append("empty")
                paths.append(file.path)
                token_map[file.path] = []
        
        if len(documents) < 2:
            return {f.path: 1.0 for f in self.files}
        
        # Compute TF-IDF and cosine similarity
        vectorizer = TfidfVectorizer(min_df=1, max_df=0.8)
        try:
            tfidf_matrix = vectorizer.fit_transform(documents)
        except Exception:
            return {f.path: 1.0 for f in self.files}
        
        similarities = cosine_similarity(tfidf_matrix)
        
        # Compute coherence as mean similarity to other files
        coherences = {}
        n = len(paths)
        for i, path in enumerate(paths):
            if n > 1:
                other_sims = [similarities[i][j] for j in range(n) if j != i]
                coherences[path] = float(np.mean(other_sims))
            else:
                coherences[path] = 1.0
        
        return coherences
    
    def _detect_responsibility_clusters(self, file_path: str) -> List[dict]:
        """NEW: Detect responsibility clusters for a file."""
        if file_path not in self.file_map:
            return []
        
        file = self.file_map[file_path]
        filepath = self._get_filepath(file_path)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tokens = IdentifierAnalyzer.extract_semantic_tokens(content)
            return IdentifierAnalyzer.detect_semantic_clusters(tokens)
        except Exception:
            return []
```

---

## 3. Gini-Enhanced Cognitive Load

### File: `math/gini.py`

```python
"""Gini coefficient calculation for inequality measurement."""

from typing import List


class Gini:
    """Gini coefficient calculations for code distribution analysis."""
    
    @staticmethod
    def gini_coefficient(values: List[float]) -> float:
        """
        Compute Gini coefficient.
        
        Formula: G = (2 × Σ(i × fᵢ)) / (n × Σ fᵢ) - (n + 1) / n
        
        Where:
            fᵢ are values sorted in ascending order
            n is the number of values
        
        Properties:
            G = 0: Perfect equality (all values equal)
            G = 1: Perfect inequality (one value has everything)
        
        Reference:
            Gini, C. (1912) - "Variabilità e Mutabilità"
        
        Args:
            values: List of non-negative values (e.g., function sizes)
        
        Returns:
            Gini coefficient in [0, 1]
        """
        if not values or all(v == 0 for v in values):
            return 0.0
        
        # Sort values in ascending order
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        total = sum(sorted_vals)
        
        if total == 0:
            return 0.0
        
        # Compute Gini using efficient formula
        # G = (2 × Σ(i × fᵢ)) / (n × total) - (n + 1) / n
        cumulative = sum((i + 1) * v for i, v in enumerate(sorted_vals))
        gini = (2 * cumulative) / (n * total) - (n + 1) / n
        
        # Ensure result is in [0, 1]
        return max(0.0, min(1.0, gini))
    
    @staticmethod
    def cognitive_load_multiplier(gini: float) -> float:
        """
        Compute cognitive load multiplier based on Gini coefficient.
        
        Formula: multiplier = 1 + gini
        
        When Gini = 0 (perfect equality): multiplier = 1.0
        When Gini = 1 (perfect inequality): multiplier = 2.0
        
        Args:
            gini: Gini coefficient in [0, 1]
        
        Returns:
            Cognitive load multiplier in [1, 2]
        """
        return 1.0 + gini


# Test the implementation
if __name__ == "__main__":
    # Test cases
    equal_sizes = [10, 10, 10, 10, 10]  # Perfect equality
    unequal_sizes = [2, 3, 5, 10, 30]   # Some inequality
    god_function = [2, 2, 2, 2, 80]     # Extreme inequality
    
    print("Gini coefficient examples:")
    print(f"  Equal sizes:      {Gini.gini_coefficient(equal_sizes):.3f}")
    print(f"  Unequal sizes:    {Gini.gini_coefficient(unequal_sizes):.3f}")
    print(f"  God function:     {Gini.gini_coefficient(god_function):.3f}")
    
    print("\nCognitive load multipliers:")
    print(f"  Equal sizes:      {Gini.cognitive_load_multiplier(Gini.gini_coefficient(equal_sizes)):.3f}")
    print(f"  Unequal sizes:    {Gini.cognitive_load_multiplier(Gini.gini_coefficient(unequal_sizes)):.3f}")
    print(f"  God function:     {Gini.cognitive_load_multiplier(Gini.gini_coefficient(god_function)):.3f}")
```

### Integration: Modify `PrimitiveExtractor`

```python
# In src/shannon_insight/primitives/extractor.py

from ..math import Gini

class PrimitiveExtractor:
    def __init__(self, files, cache=None, config_hash=""):
        self.files = files
        # ... existing init code ...
    
    def _compute_cognitive_load(self) -> Dict[str, float]:
        """NEW: Compute cognitive load with Gini coefficient."""
        loads = {}
        
        for file in self.files:
            # Base load from concepts and complexity
            concepts = file.functions + file.structs + file.interfaces
            base = concepts * file.complexity_score * (1 + file.nesting_depth / 10)
            
            # Gini-based concentration penalty
            if file.function_sizes and len(file.function_sizes) > 0:
                gini = Gini.gini_coefficient(file.function_sizes)
                concentration = Gini.cognitive_load_multiplier(gini)
            else:
                gini = 0.0
                concentration = 1.0
            
            # Cognitive load = base × concentration
            loads[file.path] = base * concentration
        
        # Normalize to [0, 1]
        if loads:
            max_load = max(loads.values())
            if max_load > 0:
                loads = {k: v / max_load for k, v in loads.items()}
        
        return loads
```

---

## 4. Update FileMetrics Model

```python
# In src/shannon_insight/models.py

from dataclasses import dataclass, field
from collections import Counter
from typing import Dict, List, Optional


@dataclass
class FileMetrics:
    """Raw observations for a single file"""
    
    path: str
    lines: int
    tokens: int
    imports: List[str]
    exports: List[str]
    functions: int
    interfaces: int
    structs: int
    complexity_score: float
    nesting_depth: int
    ast_node_types: Counter
    last_modified: float
    
    # NEW: Function sizes for Gini calculation
    function_sizes: List[int] = field(default_factory=list)
```

---

## 5. Update Scanners

### Example: Python Scanner

```python
# In src/shannon_insight/analyzers/python_analyzer.py

class PythonScanner(BaseScanner):
    def _analyze_file(self, filepath: Path) -> FileMetrics:
        """Extract all metrics from a Python file"""
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            raise FileAccessError(filepath, f"Cannot read file: {e}")
        
        lines = content.split("\n")
        
        # NEW: Extract function sizes
        function_sizes = self._extract_function_sizes(content, lines)
        
        return FileMetrics(
            path=str(filepath.relative_to(self.root_dir)),
            lines=len(lines),
            tokens=self._count_tokens(content),
            imports=self._extract_imports(content),
            exports=self._extract_exports(content),
            functions=self._count_functions(content),
            interfaces=0,  # Python doesn't have interfaces
            structs=self._count_classes(content),
            complexity_score=self._estimate_complexity(content),
            nesting_depth=self._max_nesting_depth_python(content),
            ast_node_types=self._extract_ast_node_types(content),
            last_modified=filepath.stat().st_mtime,
            function_sizes=function_sizes,  # NEW
        )
    
    def _extract_function_sizes(self, content: str, lines: List[str]) -> List[int]:
        """
        Extract line counts for each function.
        
        Approximation: Count lines between consecutive function definitions.
        This is not perfect but works for most cases.
        
        For production, use tree-sitter for accurate function boundaries.
        """
        function_sizes = []
        func_starts = []
        
        # Find all function definition lines
        for i, line in enumerate(lines):
            if re.match(r'^\s*def\s+\w+\s*\(', line):
                func_starts.append(i)
        
        # If no functions, return empty list
        if not func_starts:
            return []
        
        # Calculate sizes
        for i, start in enumerate(func_starts):
            # Next function or end of file
            end = func_starts[i + 1] if i + 1 < len(func_starts) else len(lines)
            size = end - start
            function_sizes.append(size)
        
        return function_sizes
```

---

## 6. Update Recommendations

```python
# In src/shannon_insight/primitives/recommendations.py

def generate_recommendations(file: str, 
                        primitives: Primitives,
                        normalized: Primitives,
                        anomaly_flags: List[str],
                        file_token_clusters: List[dict] = None,
                        file_function_sizes: List[int] = None) -> List[str]:
    """Generate actionable recommendations based on primitive values."""
    
    recommendations = []
    
    # Compression-based recommendations
    if 'high_compression' in anomaly_flags:
        recommendations.append(
            "File has very high informational density. Consider breaking into smaller, "
            "focused modules."
        )
    
    if 'low_compression' in anomaly_flags:
        recommendations.append(
            "File shows high repetition. Check for copy-paste patterns and "
            "extract common abstractions."
        )
    
    # Identifier-based coherence recommendations
    if 'low_coherence' in anomaly_flags and file_token_clusters:
        clusters_text = ", ".join(
            f"{c['name']} ({', '.join(c['tokens'][:3])}{'...' if len(c['tokens']) > 3 else ''})"
            for c in file_token_clusters[:3]
        )
        recommendations.append(
            f"Multiple responsibility clusters detected: {clusters_text}. "
            f"Consider splitting into separate modules."
        )
    
    # Gini-based cognitive load recommendations
    if 'high_cognitive_load' in anomaly_flags and file_function_sizes:
        max_size = max(file_function_sizes)
        median_size = sorted(file_function_sizes)[len(file_function_sizes) // 2]
        
        if max_size > 3 * median_size:
            recommendations.append(
                f"Largest function is {max_size} lines ({max_size // median_size}× the median). "
                f"Extract inner logic into helper functions."
            )
    
    return recommendations
```

---

## Testing Checklist

### Unit Tests

- [ ] `test_compression.py`: Test compression ratio calculation
- [ ] `test_identifier.py`: Test identifier token extraction
- [ ] `test_gini.py`: Test Gini coefficient calculation
- [ ] Test that all metrics produce values in expected ranges

### Integration Tests

- [ ] Test on polyglot codebase (Python + Go + TypeScript)
- [ ] Verify metrics work across all supported languages
- [ ] Check that recommendations are actionable

### Calibration Tests

- [ ] Run on known-good codebase (should have low scores)
- [ ] Run on known-bad codebase (should have high scores)
- [ ] Adjust thresholds based on empirical results

---

## Migration Path

### Phase 1: Add New Metrics (Week 1)
- Implement `Compression` class
- Implement `IdentifierAnalyzer` class
- Implement `Gini` class
- Write unit tests

### Phase 2: Update Scanners (Week 2)
- Add `function_sizes` to `FileMetrics`
- Update all scanners to extract function sizes
- Test on existing codebase

### Phase 3: Update PrimitiveExtractor (Week 2-3)
- Add `_compute_compression_complexity` method
- Update `_compute_semantic_coherence` to use identifiers
- Update `_compute_cognitive_load` to use Gini
- Maintain backward compatibility

### Phase 4: Update Registry and Recommendations (Week 3)
- Add new primitives to registry
- Deprecate old primitives
- Update recommendation engine
- Update documentation

### Phase 5: Testing and Calibration (Week 4)
- Run on multiple codebases
- Calibrate thresholds
- Validate recommendations
- Update user guide

---

## Expected Results

### Before PRIMITIVE_REDESIGN

```
File: complex_processor.py
Anomaly Flags: [high_structural_entropy, high_cognitive_load, low_semantic_coherence]

Recommendations:
  - Reduce structural complexity
  - Reduce cognitive load
  - Improve semantic coherence
```

### After PRIMITIVE_REDESIGN

```
File: complex_processor.py
Anomaly Flags: [high_compression, high_cognitive_load, low_coherence]

Root Causes:
  - High informational density (compression ratio: 0.41)
  - Cognitive load concentrated in 2 functions (Gini: 0.72)
  - 3 distinct responsibility clusters detected:
    * Validation (validate, required, pattern, range)
    * Transformation (transform, trim, upper, sanitize)
    * Caching/middleware (cache, middleware, metrics, log)

Recommendations:
  1. Extract validation logic into validators module:
     - _validate_required, _validate_type, _validate_pattern, _validate_range
     
  2. Extract transformation logic into transformers module:
     - _transform_trim, _transform_upper, _transform_lower, _transform_sanitize
     
  3. Extract caching/middleware logic into middleware module:
     - _middleware_cache, _middleware_metrics, _middleware_log
     
  4. Refactor function at line 174 (80 lines, 4× median):
     - Extract inner loops into separate methods
     - Use early returns to reduce nesting
```

---

## References

1. Li & Vitányi (2008) - *An Introduction to Kolmogorov Complexity and Its Applications*
2. Shannon (1948) - *A Mathematical Theory of Communication*
3. Gini (1912) - *Variabilità e Mutabilità*
4. McCabe (1976) - *A Complexity Measure*
5. Salton et al. (1975) - *A Vector Space Model for Automatic Indexing*

---

**Last Updated:** 2025-02-04  
**Status:** Ready for Implementation
