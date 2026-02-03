"""Analysis-related exceptions: file access, parsing, data issues."""

from pathlib import Path
from typing import Optional, List, Dict

from .base import ShannonInsightError


class AnalysisError(ShannonInsightError):
    """Base class for analysis-related errors."""
    pass


class FileAccessError(AnalysisError):
    """Raised when a file cannot be accessed or read."""

    def __init__(self, filepath: Path, reason: str):
        super().__init__(
            f"Cannot access file: {filepath}",
            details={"filepath": str(filepath), "reason": reason},
        )
        self.filepath = filepath
        self.reason = reason


class ParsingError(AnalysisError):
    """Raised when file content cannot be parsed."""

    def __init__(self, filepath: Path, language: str, reason: str):
        super().__init__(
            f"Failed to parse {language} file: {filepath}",
            details={"filepath": str(filepath), "language": language, "reason": reason},
        )
        self.filepath = filepath
        self.language = language
        self.reason = reason


class UnsupportedLanguageError(AnalysisError):
    """Raised when attempting to analyze an unsupported language."""

    def __init__(self, language: str, supported_languages: List[str]):
        super().__init__(
            f"Unsupported language: {language}",
            details={"language": language, "supported": ", ".join(supported_languages)},
        )
        self.language = language
        self.supported_languages = supported_languages


class InsufficientDataError(AnalysisError):
    """Raised when there's not enough data for analysis."""

    def __init__(self, reason: str, minimum_required: Optional[int] = None):
        details: Dict[str, str] = {"reason": reason}
        if minimum_required is not None:
            details["minimum_required"] = str(minimum_required)

        super().__init__(f"Insufficient data for analysis: {reason}", details=details)
        self.reason = reason
        self.minimum_required = minimum_required


class PrimitiveExtractionError(AnalysisError):
    """Raised when primitive extraction fails."""

    def __init__(self, primitive_name: str, filepath: Path, reason: str):
        super().__init__(
            f"Failed to extract {primitive_name} from {filepath}",
            details={
                "primitive": primitive_name,
                "filepath": str(filepath),
                "reason": reason,
            },
        )
        self.primitive_name = primitive_name
        self.filepath = filepath
        self.reason = reason
