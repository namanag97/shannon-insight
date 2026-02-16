"""Concept extraction with 3-tier approach.

Tier 1 (<3 functions): Single concept from role
Tier 2 (3-9 functions): Keyword frequency top-3
Tier 3 (10+ functions, 20+ identifiers): TF-IDF + Louvain

Two-pass architecture:
- Pass 1: Extract identifiers from all files, build corpus IDF
- Pass 2: Compute per-file TF-IDF vectors, run Louvain for Tier 3

Path-based concept enrichment:
- Extract tokens from directory path for every file
- This ensures even single-function files get meaningful concepts
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from .models import Concept, Role

if TYPE_CHECKING:
    from ..scanning.syntax import FileSyntax


# Common stopwords to exclude from concepts
STOPWORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "dare",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "and",
        "or",
        "but",
        "if",
        "then",
        "else",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "also",
        "now",
        "here",
        "there",
        "self",
        "this",
        "that",
        "these",
        "those",
        "what",
        "which",
        "who",
        "none",
        "true",
        "false",
        "null",
        "nil",
        "return",
        "def",
        "class",
        "func",
        "function",
        "var",
        "let",
        "const",
        "import",
        "export",
        "public",
        "private",
        "protected",
        "static",
        "final",
        "abstract",
        "get",
        "set",
        "new",
        "init",
        "main",
        "args",
        "kwargs",
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "tuple",
        "type",
        "any",
        "object",
        "value",
        "key",
        "item",
        "data",
        "result",
        "output",
        "input",
        "name",
        "path",
        "file",
        "dir",
        "config",
        "options",
        "settings",
        "error",
        "exception",
        "test",
        "tests",
        "spec",
        "mock",
        "stub",
    }
)


def extract_identifiers(syntax: FileSyntax) -> list[str]:
    """Extract all identifiers from a file.

    Includes function names, class names, parameter names.
    Splits camelCase and snake_case into tokens.
    """
    identifiers: list[str] = []

    # Function names and parameters
    for fn in syntax.functions:
        identifiers.extend(split_identifier(fn.name))
        for param in fn.params:
            identifiers.extend(split_identifier(param))

    # Class names and fields
    for cls in syntax.classes:
        identifiers.extend(split_identifier(cls.name))
        for field in cls.fields:
            identifiers.extend(split_identifier(field))
        for method in cls.methods:
            identifiers.extend(split_identifier(method.name))
            for param in method.params:
                identifiers.extend(split_identifier(param))

    # Filter stopwords and short tokens
    return [tok for tok in identifiers if tok.lower() not in STOPWORDS and len(tok) > 2]


def split_identifier(name: str) -> list[str]:
    """Split camelCase and snake_case into tokens."""
    # Handle snake_case
    if "_" in name:
        parts = name.split("_")
    else:
        # Handle camelCase/PascalCase
        parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", name)

    return [p.lower() for p in parts if p]


def extract_path_concepts(path: str) -> list[str]:
    """Extract concept tokens from the file's directory path.

    signals/plugins/centrality.py → ["signal", "plugin", "centrality"]
    """
    parts = PurePosixPath(path).parts
    tokens: list[str] = []
    skip_parts = {"src", "__pycache__", ".", "..", "__init__"}
    for part in parts:
        stem = PurePosixPath(part).stem
        if stem in skip_parts:
            continue
        tokens.extend(split_identifier(stem))
    return [t for t in tokens if t.lower() not in STOPWORDS and len(t) > 2]


def determine_tier(syntax: FileSyntax, identifiers: list[str]) -> int:
    """Determine which extraction tier to use.

    Tier 1: <3 functions
    Tier 2: 3-9 functions
    Tier 3: 10+ functions AND 20+ unique identifiers
    """
    func_count = syntax.function_count
    unique_ids = len(set(identifiers))

    if func_count < 3:
        return 1
    elif func_count < 10 or unique_ids < 20:
        return 2
    else:
        return 3


def extract_concepts_tier1(role: Role) -> tuple[list[Concept], float]:
    """Tier 1: Single concept from role.

    Returns:
        (concepts, entropy) where entropy is always 0.0
    """
    concept = Concept(topic=role.value, weight=1.0, keywords=[role.value])
    return [concept], 0.0


def extract_concepts_tier2(identifiers: list[str]) -> tuple[list[Concept], float]:
    """Tier 2: Keyword frequency top-3.

    Returns:
        (concepts, entropy)
    """
    if not identifiers:
        return [], 0.0

    # Count token frequency
    counter = Counter(identifiers)
    total = sum(counter.values())

    # Get top 3 tokens
    top_tokens = counter.most_common(3)

    concepts = []
    weights = []
    for token, count in top_tokens:
        weight = count / total
        concepts.append(Concept(topic=token, weight=weight, keywords=[token]))
        weights.append(weight)

    # Normalize weights to sum to 1
    weight_sum = sum(weights)
    if weight_sum > 0:
        for i, concept in enumerate(concepts):
            concept.weight = weights[i] / weight_sum

    entropy = compute_entropy([c.weight for c in concepts])
    return concepts, entropy


def extract_concepts_tier3(
    identifiers: list[str],
    idf: dict[str, float],
) -> tuple[list[Concept], float]:
    """Tier 3: TF-IDF + Louvain clustering.

    Args:
        identifiers: Tokens from this file
        idf: Corpus-wide IDF values

    Returns:
        (concepts, entropy)
    """
    if not identifiers:
        return [], 0.0

    # Compute TF for this file
    counter = Counter(identifiers)
    total = sum(counter.values())
    tf = {token: count / total for token, count in counter.items()}

    # Compute TF-IDF
    tfidf = {}
    for token, tf_val in tf.items():
        idf_val = idf.get(token, 0.0)
        tfidf[token] = tf_val * idf_val

    if not tfidf:
        return [], 0.0

    # Build co-occurrence graph for Louvain
    # (simplified: tokens that appear together have edges)
    communities = louvain_communities(identifiers, tfidf)

    # Convert communities to concepts
    concepts = []
    total_weight = sum(tfidf.values())

    for community_tokens in communities:
        if not community_tokens:
            continue

        # Community weight is sum of TF-IDF scores
        weight = sum(tfidf.get(t, 0) for t in community_tokens)
        if total_weight > 0:
            weight /= total_weight

        # Label is the highest TF-IDF token in community
        label = max(community_tokens, key=lambda t: tfidf.get(t, 0))

        # Top keywords by TF-IDF
        keywords = sorted(community_tokens, key=lambda t: tfidf.get(t, 0), reverse=True)[:5]

        concepts.append(Concept(topic=label, weight=weight, keywords=keywords))

    # Sort by weight
    concepts.sort(key=lambda c: c.weight, reverse=True)

    # Normalize weights
    weight_sum = sum(c.weight for c in concepts)
    if weight_sum > 0:
        for c in concepts:
            c.weight /= weight_sum

    entropy = compute_entropy([c.weight for c in concepts])
    return concepts, entropy


def louvain_communities(identifiers: list[str], tfidf: dict[str, float]) -> list[list[str]]:
    """Simple Louvain-inspired community detection.

    Uses co-occurrence to group related tokens.
    For small files, just returns top tokens as separate "communities".
    """
    unique_tokens = list(set(identifiers))

    if len(unique_tokens) < 5:
        # Too few tokens for clustering
        return [[t] for t in unique_tokens if tfidf.get(t, 0) > 0]

    # Build co-occurrence counts (tokens appearing near each other)
    cooccur: dict[tuple[str, str], int] = defaultdict(int)
    window_size = 3

    for i, token in enumerate(identifiers):
        for j in range(max(0, i - window_size), min(len(identifiers), i + window_size + 1)):
            if i != j:
                other = identifiers[j]
                if token < other:
                    cooccur[(token, other)] += 1
                else:
                    cooccur[(other, token)] += 1

    # Simple greedy community detection
    # Start with each token in its own community
    token_to_community: dict[str, int] = {t: i for i, t in enumerate(unique_tokens)}
    communities: dict[int, set[str]] = {i: {t} for i, t in enumerate(unique_tokens)}

    # Merge communities based on co-occurrence
    for (t1, t2), count in sorted(cooccur.items(), key=lambda x: -x[1]):
        if count < 2:
            continue

        c1 = token_to_community[t1]
        c2 = token_to_community[t2]

        if c1 != c2 and len(communities[c1]) + len(communities[c2]) <= 10:
            # Merge c2 into c1
            for t in communities[c2]:
                token_to_community[t] = c1
                communities[c1].add(t)
            del communities[c2]

    # Filter out single-token communities with low TF-IDF
    result = []
    for tokens in communities.values():
        if len(tokens) > 1 or any(tfidf.get(t, 0) > 0.1 for t in tokens):
            result.append(sorted(tokens, key=lambda t: tfidf.get(t, 0), reverse=True))

    # Limit to top 5 communities
    result.sort(key=lambda c: sum(tfidf.get(t, 0) for t in c), reverse=True)
    return result[:5]


def compute_entropy(weights: list[float]) -> float:
    """Compute Shannon entropy of weight distribution.

    H = -sum(p * log2(p)) for p > 0
    """
    if not weights:
        return 0.0

    entropy = 0.0
    for w in weights:
        if w > 0:
            entropy -= w * math.log2(w)

    return entropy


class ConceptExtractor:
    """Two-pass concept extractor for a corpus of files.

    Usage:
        extractor = ConceptExtractor()

        # Pass 1: Build IDF
        for syntax in all_files:
            extractor.add_file(syntax)
        extractor.compute_idf()

        # Pass 2: Extract concepts
        for syntax in all_files:
            concepts, entropy, tier = extractor.extract(syntax, role)
    """

    def __init__(self) -> None:
        """Initialize extractor."""
        self._file_identifiers: dict[str, list[str]] = {}
        self._doc_freq: Counter[str] = Counter()
        self._num_docs: int = 0
        self._idf: dict[str, float] = {}
        self._file_imports: dict[str, set[str]] = {}
        self._import_doc_freq: Counter[str] = Counter()

    def add_file(self, syntax: FileSyntax) -> None:
        """Pass 1: Add file to corpus for IDF computation."""
        identifiers = extract_identifiers(syntax)

        # Add path-based concepts as low-weight identifiers
        path_tokens = extract_path_concepts(syntax.path)
        identifiers.extend(path_tokens)

        self._file_identifiers[syntax.path] = identifiers

        # Update document frequency (count unique tokens per doc)
        unique_tokens = set(identifiers)
        for token in unique_tokens:
            self._doc_freq[token] += 1

        # Track imports for import fingerprinting
        import_modules = set()
        for imp in syntax.imports:
            if imp.source:
                import_modules.add(imp.source)
        self._file_imports[syntax.path] = import_modules
        for mod in import_modules:
            self._import_doc_freq[mod] += 1

        self._num_docs += 1

    def compute_idf(self) -> None:
        """Compute IDF values after all files added."""
        if self._num_docs == 0:
            return

        for token, doc_count in self._doc_freq.items():
            # IDF = log(N / df) + 1 (smoothed)
            self._idf[token] = math.log(self._num_docs / doc_count) + 1

    def compute_import_fingerprint(self, path: str) -> dict[str, float]:
        """Compute import fingerprint for a file.

        Each import is weighted by its surprise: -log2(files_importing / total_files).
        Rare imports have high surprise (more distinctive).
        """
        imports = self._file_imports.get(path, set())
        if not imports or self._num_docs == 0:
            return {}

        fingerprint: dict[str, float] = {}
        for mod in imports:
            freq = self._import_doc_freq.get(mod, 1)
            surprise = -math.log2(freq / self._num_docs)
            fingerprint[mod] = surprise

        return fingerprint

    def extract(self, syntax: FileSyntax, role: Role) -> tuple[list[Concept], float, int]:
        """Pass 2: Extract concepts for a file.

        Args:
            syntax: FileSyntax for the file
            role: Classified role of the file

        Returns:
            (concepts, entropy, tier)
        """
        identifiers = self._file_identifiers.get(syntax.path, [])
        tier = determine_tier(syntax, identifiers)

        if tier == 1:
            concepts, entropy = extract_concepts_tier1(role)
        elif tier == 2:
            concepts, entropy = extract_concepts_tier2(identifiers)
        else:
            concepts, entropy = extract_concepts_tier3(identifiers, self._idf)

        return concepts, entropy, tier
