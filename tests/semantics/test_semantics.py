"""Tests for semantic analysis (concepts, naming, completeness)."""

import pytest

from shannon_insight.scanning.syntax import ClassDef, FileSyntax, FunctionDef
from shannon_insight.semantics import (
    Concept,
    Role,
    compute_completeness,
    compute_naming_drift,
    cosine_similarity,
    count_todos,
    extract_identifiers,
)
from shannon_insight.semantics.concepts import (
    ConceptExtractor,
    determine_tier,
    extract_concepts_tier1,
    extract_concepts_tier2,
    split_identifier,
)


def make_syntax(
    path: str = "test.py",
    functions: list[FunctionDef] | None = None,
    classes: list[ClassDef] | None = None,
    language: str = "python",
) -> FileSyntax:
    """Helper to create FileSyntax."""
    return FileSyntax(
        path=path,
        functions=functions or [],
        classes=classes or [],
        imports=[],
        language=language,
    )


def make_function(
    name: str = "foo",
    params: list[str] | None = None,
) -> FunctionDef:
    """Helper to create FunctionDef."""
    return FunctionDef(
        name=name,
        params=params or [],
        body_tokens=10,
        signature_tokens=5,
        nesting_depth=1,
        start_line=1,
        end_line=5,
    )


class TestIdentifierExtraction:
    """Test identifier extraction and splitting."""

    def test_split_snake_case(self):
        """Splits snake_case identifiers."""
        assert split_identifier("my_function_name") == ["my", "function", "name"]

    def test_split_camel_case(self):
        """Splits camelCase identifiers (lowercased)."""
        assert split_identifier("myFunctionName") == ["my", "function", "name"]

    def test_split_pascal_case(self):
        """Splits PascalCase identifiers."""
        result = split_identifier("MyClassName")
        assert "My" in result or "my" in [r.lower() for r in result]

    def test_extract_identifiers_from_functions(self):
        """Extracts identifiers from function names and params."""
        fn = make_function(name="process_data", params=["input_file", "outputPath"])
        syntax = make_syntax(functions=[fn])
        identifiers = extract_identifiers(syntax)

        # Should contain parts of the identifiers (not stopwords)
        # Note: common words like "file", "input", "output", "data" are in STOPWORDS
        assert "process" in identifiers


class TestTierDetermination:
    """Test concept extraction tier determination."""

    def test_tier1_few_functions(self):
        """Files with <3 functions get Tier 1."""
        fn1 = make_function(name="foo")
        fn2 = make_function(name="bar")
        syntax = make_syntax(functions=[fn1, fn2])
        identifiers = extract_identifiers(syntax)

        tier = determine_tier(syntax, identifiers)
        assert tier == 1

    def test_tier2_medium_functions(self):
        """Files with 3-9 functions get Tier 2."""
        functions = [make_function(name=f"func_{i}") for i in range(5)]
        syntax = make_syntax(functions=functions)
        identifiers = extract_identifiers(syntax)

        tier = determine_tier(syntax, identifiers)
        assert tier == 2

    def test_tier3_many_functions(self):
        """Files with 10+ functions and 20+ identifiers get Tier 3."""
        # Create functions with many unique non-stopword identifiers
        # Each function contributes 5 unique tokens (avoiding stopwords)
        words = [
            "alpha",
            "beta",
            "gamma",
            "delta",
            "epsilon",
            "zeta",
            "eta",
            "theta",
            "iota",
            "kappa",
            "lambda",
            "sigma",
            "omega",
            "tau",
            "phi",
        ]
        functions = []
        for _i, word in enumerate(words):
            functions.append(
                make_function(
                    name=f"compute_{word}_metric",
                    params=[f"source_{word}", f"target_{word}", f"cache_{word}"],
                )
            )
        syntax = make_syntax(functions=functions)
        identifiers = extract_identifiers(syntax)

        # Should have 10+ functions and 20+ unique identifiers
        assert syntax.function_count >= 10
        unique_count = len(set(identifiers))
        assert unique_count >= 20, f"Only got {unique_count} unique identifiers"
        tier = determine_tier(syntax, identifiers)
        assert tier == 3


class TestConceptExtractionTier1:
    """Test Tier 1 concept extraction."""

    def test_tier1_single_concept(self):
        """Tier 1 produces single concept from role."""
        concepts, entropy = extract_concepts_tier1(Role.UTILITY)

        assert len(concepts) == 1
        assert concepts[0].topic == "utility"
        assert concepts[0].weight == 1.0
        assert entropy == 0.0


class TestConceptExtractionTier2:
    """Test Tier 2 concept extraction."""

    def test_tier2_top_keywords(self):
        """Tier 2 extracts top keywords."""
        identifiers = ["process", "process", "data", "data", "data", "file"]
        concepts, entropy = extract_concepts_tier2(identifiers)

        assert len(concepts) <= 3
        # "data" should be most common
        topics = [c.topic for c in concepts]
        assert "data" in topics

    def test_tier2_entropy_nonzero(self):
        """Tier 2 with multiple concepts has non-zero entropy."""
        identifiers = ["alpha", "alpha", "beta", "beta", "gamma"]
        concepts, entropy = extract_concepts_tier2(identifiers)

        assert entropy > 0


class TestConceptExtractor:
    """Test two-pass ConceptExtractor."""

    def test_extractor_two_pass(self):
        """ConceptExtractor uses two-pass architecture."""
        syntax1 = make_syntax(
            path="file1.py",
            functions=[make_function(name="process_data")],
        )
        syntax2 = make_syntax(
            path="file2.py",
            functions=[make_function(name="process_results")],
        )

        extractor = ConceptExtractor()

        # Pass 1: Add files
        extractor.add_file(syntax1)
        extractor.add_file(syntax2)
        extractor.compute_idf()

        # Pass 2: Extract concepts
        concepts1, entropy1, tier1 = extractor.extract(syntax1, Role.UTILITY)
        concepts2, entropy2, tier2 = extractor.extract(syntax2, Role.UTILITY)

        assert tier1 == 1  # Only 1 function
        assert tier2 == 1


class TestNamingDrift:
    """Test naming drift computation."""

    def test_generic_filename_no_drift(self):
        """Generic filenames get 0.0 drift."""
        concepts = [Concept(topic="anything", weight=1.0)]
        drift = compute_naming_drift("utils.py", concepts, tier=3)
        assert drift == 0.0

    def test_tier1_no_drift(self):
        """Tier 1 files get 0.0 drift (not enough data)."""
        concepts = [Concept(topic="processing", weight=1.0)]
        drift = compute_naming_drift("parser.py", concepts, tier=1)
        assert drift == 0.0

    def test_tier2_no_drift(self):
        """Tier 2 files get 0.0 drift (not enough data)."""
        concepts = [Concept(topic="processing", weight=1.0)]
        drift = compute_naming_drift("parser.py", concepts, tier=2)
        assert drift == 0.0

    def test_matching_name_low_drift(self):
        """Files with matching name have low drift."""
        concepts = [Concept(topic="parser", weight=1.0, keywords=["parser", "parse"])]
        drift = compute_naming_drift("parser.py", concepts, tier=3)
        assert drift < 0.5

    def test_mismatched_name_high_drift(self):
        """Files with mismatched name have high drift."""
        concepts = [
            Concept(topic="database", weight=1.0, keywords=["database", "query", "connection"])
        ]
        drift = compute_naming_drift("parser.py", concepts, tier=3)
        assert drift > 0.5


class TestCosineSimilarity:
    """Test cosine similarity computation."""

    def test_identical_tokens(self):
        """Identical token lists have similarity 1.0."""
        tokens = ["foo", "bar", "baz"]
        similarity = cosine_similarity(tokens, tokens)
        assert similarity == pytest.approx(1.0)

    def test_disjoint_tokens(self):
        """Completely different tokens have similarity 0.0."""
        tokens_a = ["foo", "bar"]
        tokens_b = ["baz", "qux"]
        similarity = cosine_similarity(tokens_a, tokens_b)
        assert similarity == 0.0

    def test_partial_overlap(self):
        """Partially overlapping tokens have similarity between 0 and 1."""
        tokens_a = ["foo", "bar", "baz"]
        tokens_b = ["bar", "baz", "qux"]
        similarity = cosine_similarity(tokens_a, tokens_b)
        assert 0 < similarity < 1


class TestTodoDensity:
    """Test TODO/FIXME/HACK detection."""

    def test_counts_todo(self):
        """Counts TODO markers."""
        content = "# TODO: fix this\n# TODO: and this"
        assert count_todos(content) == 2

    def test_counts_fixme(self):
        """Counts FIXME markers."""
        content = "# FIXME: broken code"
        assert count_todos(content) == 1

    def test_counts_hack(self):
        """Counts HACK markers."""
        content = "# HACK: temporary workaround"
        assert count_todos(content) == 1

    def test_case_insensitive(self):
        """Counts markers case-insensitively."""
        content = "# todo: lowercase\n# Todo: mixed"
        assert count_todos(content) == 2


class TestDocstringCoverage:
    """Test docstring coverage computation."""

    def test_documented_function(self):
        """Detects documented functions."""
        fn = FunctionDef(
            name="foo",
            params=[],
            body_tokens=10,
            signature_tokens=5,
            nesting_depth=0,
            start_line=1,
            end_line=5,
        )
        syntax = make_syntax(functions=[fn])
        content = '''def foo():
    """Docstring here."""
    pass
'''
        completeness = compute_completeness(syntax, content)
        assert completeness.docstring_coverage == 1.0

    def test_undocumented_function(self):
        """Detects undocumented functions."""
        fn = FunctionDef(
            name="foo",
            params=[],
            body_tokens=10,
            signature_tokens=5,
            nesting_depth=0,
            start_line=1,
            end_line=3,
        )
        syntax = make_syntax(functions=[fn])
        content = """def foo():
    pass
"""
        completeness = compute_completeness(syntax, content)
        assert completeness.docstring_coverage == 0.0

    def test_non_python_no_coverage(self):
        """Non-Python files have None coverage."""
        syntax = make_syntax(language="go")
        content = "func main() {}"
        completeness = compute_completeness(syntax, content)
        assert completeness.docstring_coverage is None

    def test_todo_density_calculation(self):
        """TODO density is per 100 lines."""
        fn = make_function()
        syntax = make_syntax(functions=[fn])
        # 10 TODOs, 100 lines = 10 per 100 lines
        content = ("# TODO: fix\n" * 10) + ("# regular line\n" * 90)
        completeness = compute_completeness(syntax, content)
        assert completeness.todo_density == pytest.approx(10.0, abs=1.0)
        assert completeness.todo_count == 10
