"""Tests for identifier token extraction and coherence analysis."""

from shannon_insight.math.identifier import IdentifierAnalyzer


class TestExtractIdentifierTokens:
    """Tests for IdentifierAnalyzer.extract_identifier_tokens."""

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

    def test_consecutive_uppercase(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens("XMLParser HTTPClient")
        assert "xml" in tokens
        assert "parser" in tokens
        assert "http" in tokens
        assert "client" in tokens

    def test_stop_words_filtered(self):
        # Language keywords should be filtered out
        code = "def return if else for while class import from"
        tokens = IdentifierAnalyzer.extract_identifier_tokens(code)
        for kw in ["def", "return", "else", "for", "while", "class", "import", "from"]:
            assert kw not in tokens

    def test_short_tokens_filtered(self):
        # Tokens < 3 chars should be excluded
        tokens = IdentifierAnalyzer.extract_identifier_tokens("do_it go_on")
        # "do" and "it" and "go" and "on" are all < 3 chars or stop words
        for t in tokens:
            assert len(t) >= 3

    def test_real_python_code(self):
        code = """
def validateEmailAddress(email):
    if not email:
        return False
    return checkDomainValid(email)

def transformUpperCase(text):
    return text.upper()

def cacheResult(key, value):
    _internal_cache[key] = value
"""
        tokens = IdentifierAnalyzer.extract_identifier_tokens(code)
        assert "validate" in tokens
        assert "email" in tokens
        assert "address" in tokens
        assert "transform" in tokens
        assert "upper" in tokens
        assert "cache" in tokens
        assert "result" in tokens

    def test_numbers_only_filtered(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens("var123 test456")
        # "123" and "456" should be filtered, but "var" is too short
        for t in tokens:
            assert not t.isdigit()

    def test_mixed_case_patterns(self):
        tokens = IdentifierAnalyzer.extract_identifier_tokens(
            "getUserById_fromCache processHTTPRequest"
        )
        assert "user" in tokens
        assert "cache" in tokens
        assert "process" in tokens
        assert "http" in tokens
        assert "request" in tokens


class TestDetectSemanticClusters:
    """Tests for IdentifierAnalyzer.detect_semantic_clusters."""

    def test_empty_tokens(self):
        assert IdentifierAnalyzer.detect_semantic_clusters([]) == []

    def test_few_tokens_single_cluster(self):
        clusters = IdentifierAnalyzer.detect_semantic_clusters(["hello", "world"])
        # Too few unique tokens for multiple clusters
        assert len(clusters) <= 1

    def test_distinct_groups(self):
        tokens = ["validate", "validator", "validation"] * 3 + ["cache", "cached", "caching"] * 3
        clusters = IdentifierAnalyzer.detect_semantic_clusters(tokens)
        assert len(clusters) >= 2

    def test_cluster_structure(self):
        tokens = ["alpha", "alpha", "alpha", "beta", "beta", "beta"]
        clusters = IdentifierAnalyzer.detect_semantic_clusters(tokens)
        for cluster in clusters:
            assert "tokens" in cluster
            assert "top_terms" in cluster
            assert "count" in cluster
            assert cluster["count"] >= 3


class TestComputeCoherence:
    """Tests for IdentifierAnalyzer.compute_coherence."""

    def test_empty_tokens(self):
        assert IdentifierAnalyzer.compute_coherence([]) == 0.0

    def test_single_cluster_high_coherence(self):
        # All same-prefix tokens = single cluster = high coherence
        tokens = ["validate", "validator", "validation"] * 5
        coherence = IdentifierAnalyzer.compute_coherence(tokens)
        assert coherence == 1.0

    def test_coherence_in_valid_range(self):
        tokens = (
            ["validate", "validator", "validation"] * 3
            + ["cache", "cached", "caching"] * 3
            + ["transform", "transformer", "transformed"] * 3
        )
        coherence = IdentifierAnalyzer.compute_coherence(tokens)
        assert 0.0 <= coherence <= 1.0

    def test_mixed_responsibilities_lower_coherence(self):
        # Many different clusters should have lower coherence
        focused = ["validate", "validator", "validation"] * 10
        mixed = (
            ["validate", "validator", "validation"] * 3
            + ["cache", "cached", "caching"] * 3
            + ["transform", "transformer", "transformed"] * 3
            + ["render", "renderer", "rendering"] * 3
        )
        c_focused = IdentifierAnalyzer.compute_coherence(focused)
        c_mixed = IdentifierAnalyzer.compute_coherence(mixed)
        assert c_focused >= c_mixed
