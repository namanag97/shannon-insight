"""Identifier token extraction and semantic coherence analysis.

Extracts identifiers from source code, splits camelCase/snake_case into
semantic tokens, and computes responsibility coherence based on vocabulary
clustering.
"""

import math
import re
from collections import Counter
from itertools import groupby
from typing import Dict, List, Set


class IdentifierAnalyzer:
    """Extract and analyze identifier tokens from source code."""

    # Language keywords that don't carry semantic meaning.
    STOP_WORDS: frozenset[str] = frozenset(
        {
            # Python
            "def",
            "class",
            "import",
            "from",
            "return",
            "elif",
            "for",
            "while",
            "with",
            "try",
            "except",
            "finally",
            "raise",
            "pass",
            "break",
            "continue",
            "and",
            "not",
            "lambda",
            "yield",
            "async",
            "await",
            "global",
            "nonlocal",
            "assert",
            "del",
            "true",
            "false",
            "none",
            "self",
            # Go
            "func",
            "var",
            "const",
            "type",
            "struct",
            "interface",
            "package",
            "range",
            "chan",
            "select",
            "defer",
            "recover",
            "make",
            "new",
            "append",
            "copy",
            "len",
            "cap",
            "close",
            "nil",
            # TypeScript / JavaScript
            "function",
            "let",
            "switch",
            "case",
            "throw",
            "catch",
            "super",
            "extends",
            "enum",
            "export",
            "default",
            "undefined",
            "this",
            # Rust
            "impl",
            "trait",
            "match",
            "loop",
            "pub",
            "mod",
            "crate",
            "where",
            "unsafe",
            "extern",
            # Java
            "public",
            "private",
            "protected",
            "static",
            "final",
            "void",
            "abstract",
            "implements",
            "throws",
            "synchronized",
            # Ruby
            "require",
            "include",
            "extend",
            "module",
            "begin",
            "rescue",
            "ensure",
            "elsif",
            "unless",
            "until",
            "attr",
            # C / C++
            "define",
            "ifdef",
            "ifndef",
            "endif",
            "typedef",
            "sizeof",
            "template",
            "namespace",
            "using",
            "virtual",
            "inline",
            "volatile",
            "register",
            # Common generic terms (too short or too common to be meaningful)
            "get",
            "set",
            "the",
            "else",
            "null",
            "int",
            "str",
            "bool",
            "float",
            "string",
            "err",
            "error",
        }
    )

    @staticmethod
    def extract_identifier_tokens(content: str) -> List[str]:
        """Extract and split all identifiers into semantic tokens.

        Splits camelCase and snake_case into component words.
        Filters out language keywords and short fragments.

        Examples:
            "validateEmailAddress" -> ["validate", "email", "address"]
            "_transform_upper"    -> ["transform", "upper"]
            "XMLParser"           -> ["xml", "parser"]

        Args:
            content: Source code as string.

        Returns:
            List of semantic tokens (lowercase, >= 3 chars).
        """
        if not content:
            return []

        # Extract identifier-like tokens (words that look like identifiers)
        raw_identifiers = re.findall(r"[a-zA-Z_]\w{2,}", content)

        tokens: List[str] = []
        stop = IdentifierAnalyzer.STOP_WORDS

        for ident in raw_identifiers:
            # Split camelCase: "validateEmail" -> "validate Email"
            # Also handle consecutive uppercase: "XMLParser" -> "XML Parser"
            parts = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", ident)
            parts = re.sub(r"([a-z])([A-Z])", r"\1 \2", parts)

            # Split on underscores and spaces, normalize
            for part in parts.replace("_", " ").split():
                word = part.lower().strip()
                if len(word) >= 3 and not word.isdigit() and word not in stop:
                    tokens.append(word)

        return tokens

    @staticmethod
    def detect_semantic_clusters(
        tokens: List[str],
        min_cluster_size: int = 3,
    ) -> List[Dict]:
        """Detect semantic responsibility clusters by prefix grouping.

        A simple heuristic that groups tokens sharing a common 3-character
        prefix.  For production accuracy, consider replacing with sklearn
        KMeans on TF-IDF vectors.

        Args:
            tokens: List of semantic tokens.
            min_cluster_size: Minimum total occurrences per cluster.

        Returns:
            List of cluster dicts with 'tokens', 'top_terms', 'count' keys.
        """
        if not tokens:
            return []

        token_counts = Counter(tokens)
        unique_tokens = sorted(token_counts.keys())

        if len(unique_tokens) < 3:
            return [
                {
                    "tokens": list(token_counts.keys()),
                    "top_terms": [t for t, _ in token_counts.most_common(3)],
                    "count": len(tokens),
                }
            ]

        clusters: List[Dict] = []
        for _prefix, group in groupby(unique_tokens, key=lambda x: x[:3]):
            group_list = list(group)
            total_count = sum(token_counts[t] for t in group_list)
            if total_count >= min_cluster_size:
                clusters.append(
                    {
                        "tokens": group_list,
                        "top_terms": sorted(group_list, key=lambda x: -token_counts[x])[:3],
                        "count": total_count,
                    }
                )

        return clusters

    @staticmethod
    def compute_coherence(tokens: List[str]) -> float:
        """Compute coherence score using cluster entropy.

        Fewer, larger clusters = high coherence (single responsibility).
        Many small clusters = low coherence (mixed responsibilities).

        Args:
            tokens: List of semantic tokens.

        Returns:
            Coherence score in [0, 1].
            Higher = more focused / fewer responsibilities.
            Lower = mixed responsibilities.
        """
        if not tokens:
            return 0.0

        clusters = IdentifierAnalyzer.detect_semantic_clusters(tokens)

        if len(clusters) <= 1:
            return 1.0  # Single responsibility

        token_count = len(tokens)
        cluster_entropy = 0.0

        for cluster in clusters:
            p = cluster["count"] / token_count
            if p > 0:
                cluster_entropy -= p * math.log2(p)

        max_entropy = math.log2(len(clusters)) if len(clusters) > 1 else 1.0

        return 1.0 - (cluster_entropy / max_entropy) if max_entropy > 0 else 1.0
