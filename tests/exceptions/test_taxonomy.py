"""Tests for enterprise error taxonomy."""

import pytest

from shannon_insight.exceptions.taxonomy import (
    ArchitectureError,
    ErrorCode,
    FinderError,
    GraphError,
    PersistenceError,
    ScanningError,
    SemanticError,
    ShannonError,
    SignalError,
    TemporalError,
    ValidationError,
)


class TestErrorCode:
    """Test ErrorCode enum."""

    def test_scanning_error_codes(self):
        """Scanning errors are SC1xx."""
        assert ErrorCode.SC100.value == "SC100"  # File read error
        assert ErrorCode.SC101.value == "SC101"  # Encoding detection failed
        assert ErrorCode.SC102.value == "SC102"  # Tree-sitter parse failed
        assert ErrorCode.SC103.value == "SC103"  # Regex fallback failed

    def test_semantic_error_codes(self):
        """Semantic errors are SC2xx."""
        assert ErrorCode.SC200.value == "SC200"  # Concept extraction failed
        assert ErrorCode.SC201.value == "SC201"  # Role classification ambiguous
        assert ErrorCode.SC202.value == "SC202"  # TF-IDF computation failed

    def test_graph_error_codes(self):
        """Graph errors are SC3xx."""
        assert ErrorCode.SC300.value == "SC300"  # Import resolution failed
        assert ErrorCode.SC301.value == "SC301"  # Call resolution failed
        assert ErrorCode.SC302.value == "SC302"  # Clone detection timeout
        assert ErrorCode.SC303.value == "SC303"  # Graph has unreachable nodes

    def test_temporal_error_codes(self):
        """Temporal errors are SC4xx."""
        assert ErrorCode.SC400.value == "SC400"  # Git not found
        assert ErrorCode.SC401.value == "SC401"  # Git log parse failed
        assert ErrorCode.SC402.value == "SC402"  # Git subprocess timeout
        assert ErrorCode.SC403.value == "SC403"  # Shallow clone detected

    def test_architecture_error_codes(self):
        """Architecture errors are SC5xx."""
        assert ErrorCode.SC500.value == "SC500"  # Module detection failed
        assert ErrorCode.SC501.value == "SC501"  # Layer inference cycle detected
        assert ErrorCode.SC502.value == "SC502"  # Martin metrics undefined

    def test_signal_error_codes(self):
        """Signal errors are SC6xx."""
        assert ErrorCode.SC600.value == "SC600"  # Percentile on non-percentileable signal
        assert ErrorCode.SC601.value == "SC601"  # Composite input missing
        assert ErrorCode.SC602.value == "SC602"  # Normalization tier mismatch

    def test_finder_error_codes(self):
        """Finder errors are SC7xx."""
        assert ErrorCode.SC700.value == "SC700"  # Required signal unavailable
        assert ErrorCode.SC701.value == "SC701"  # Threshold evaluation failed
        assert ErrorCode.SC702.value == "SC702"  # Confidence computation failed

    def test_validation_error_codes(self):
        """Validation errors are SC8xx."""
        assert ErrorCode.SC800.value == "SC800"  # Phase contract violated
        assert ErrorCode.SC801.value == "SC801"  # Store slot type mismatch
        assert ErrorCode.SC802.value == "SC802"  # Adjacency/reverse inconsistent

    def test_persistence_error_codes(self):
        """Persistence errors are SC9xx."""
        assert ErrorCode.SC900.value == "SC900"  # SQLite write failed
        assert ErrorCode.SC901.value == "SC901"  # Schema migration failed
        assert ErrorCode.SC902.value == "SC902"  # Snapshot corruption detected


class TestShannonError:
    """Test ShannonError base exception."""

    def test_basic_creation(self):
        """Can create with message and code."""
        err = ShannonError(
            message="Test error",
            code=ErrorCode.SC100,
        )
        assert err.message == "Test error"
        assert err.code == ErrorCode.SC100
        assert err.recoverable is True  # default
        assert err.context == {}
        assert err.recovery_hint is None

    def test_str_includes_code(self):
        """String representation includes error code."""
        err = ShannonError(message="File read failed", code=ErrorCode.SC100)
        assert str(err) == "[SC100] File read failed"

    def test_with_context(self):
        """Can include context dict."""
        err = ShannonError(
            message="Parse failed",
            code=ErrorCode.SC102,
            context={"path": "/foo/bar.py", "line": 42},
        )
        assert err.context["path"] == "/foo/bar.py"
        assert err.context["line"] == 42

    def test_with_recovery_hint(self):
        """Can include recovery hint."""
        err = ShannonError(
            message="Git not found",
            code=ErrorCode.SC400,
            recoverable=True,
            recovery_hint="Install git or skip temporal analysis",
        )
        assert err.recoverable is True
        assert err.recovery_hint == "Install git or skip temporal analysis"

    def test_to_json(self):
        """Structured logging format."""
        err = ShannonError(
            message="Test",
            code=ErrorCode.SC100,
            context={"foo": "bar"},
            recoverable=False,
            recovery_hint="Fix it",
        )
        json_data = err.to_json()
        assert json_data["error_code"] == "SC100"
        assert json_data["message"] == "Test"
        assert json_data["context"] == {"foo": "bar"}
        assert json_data["recoverable"] is False
        assert json_data["recovery_hint"] == "Fix it"

    def test_is_exception(self):
        """ShannonError is a valid Exception."""
        err = ShannonError(message="test", code=ErrorCode.SC100)
        assert isinstance(err, Exception)

        with pytest.raises(ShannonError) as exc_info:
            raise err
        assert exc_info.value.code == ErrorCode.SC100


class TestDomainExceptions:
    """Test domain-specific exception subclasses."""

    def test_scanning_error(self):
        """ScanningError is a ShannonError."""
        err = ScanningError(message="Parse failed", code=ErrorCode.SC102)
        assert isinstance(err, ShannonError)
        assert isinstance(err, ScanningError)

    def test_semantic_error(self):
        """SemanticError is a ShannonError."""
        err = SemanticError(message="Concept failed", code=ErrorCode.SC200)
        assert isinstance(err, ShannonError)
        assert isinstance(err, SemanticError)

    def test_graph_error(self):
        """GraphError is a ShannonError."""
        err = GraphError(message="Import failed", code=ErrorCode.SC300)
        assert isinstance(err, ShannonError)
        assert isinstance(err, GraphError)

    def test_temporal_error(self):
        """TemporalError is a ShannonError."""
        err = TemporalError(message="Git missing", code=ErrorCode.SC400)
        assert isinstance(err, ShannonError)
        assert isinstance(err, TemporalError)

    def test_architecture_error(self):
        """ArchitectureError is a ShannonError."""
        err = ArchitectureError(message="Module detection failed", code=ErrorCode.SC500)
        assert isinstance(err, ShannonError)
        assert isinstance(err, ArchitectureError)

    def test_signal_error(self):
        """SignalError is a ShannonError."""
        err = SignalError(message="Bad percentile", code=ErrorCode.SC600)
        assert isinstance(err, ShannonError)
        assert isinstance(err, SignalError)

    def test_finder_error(self):
        """FinderError is a ShannonError."""
        err = FinderError(message="Signal missing", code=ErrorCode.SC700)
        assert isinstance(err, ShannonError)
        assert isinstance(err, FinderError)

    def test_validation_error(self):
        """ValidationError is a ShannonError."""
        err = ValidationError(message="Contract violated", code=ErrorCode.SC800)
        assert isinstance(err, ShannonError)
        assert isinstance(err, ValidationError)

    def test_persistence_error(self):
        """PersistenceError is a ShannonError."""
        err = PersistenceError(message="SQLite failed", code=ErrorCode.SC900)
        assert isinstance(err, ShannonError)
        assert isinstance(err, PersistenceError)
