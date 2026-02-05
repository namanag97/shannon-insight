"""Common bootstrap for experiment scripts.

Adds src/ to sys.path, provides load_analysis() that scans a codebase
and runs the full analysis engine, returning (CodebaseAnalysis, List[FileMetrics]).
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Ensure src/ is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from shannon_insight.core.scanner_factory import ScannerFactory
from shannon_insight.analysis.engine import AnalysisEngine
from shannon_insight.analysis.models import CodebaseAnalysis
from shannon_insight.models import FileMetrics
from shannon_insight.config import AnalysisSettings


def load_analysis(
    codebase_path: str = ".",
) -> Tuple[CodebaseAnalysis, List[FileMetrics]]:
    """Scan *codebase_path* and run the full analysis engine.

    Returns (CodebaseAnalysis, List[FileMetrics]).
    """
    path = Path(codebase_path).resolve()
    settings = AnalysisSettings()

    factory = ScannerFactory(path, settings)
    scanners, detected = factory.create("auto")

    all_files: List[FileMetrics] = []
    for scanner, lang in scanners:
        if lang == "universal":
            continue
        all_files.extend(scanner.scan())

    if len(all_files) < 3:
        raise RuntimeError(
            f"Only {len(all_files)} files found in {path} — need at least 3"
        )

    engine = AnalysisEngine(all_files, root_dir=str(path))
    result = engine.run()
    return result, all_files
