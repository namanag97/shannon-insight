"""Baseline management for diff/PR mode."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from .models import AnomalyReport, DiffReport
from .logging_config import get_logger

logger = get_logger(__name__)


def save_baseline(reports: List[AnomalyReport], path: str) -> None:
    """Save current analysis scores as a JSON baseline file.

    The baseline maps file paths to their overall scores and confidence.
    """
    data = {}
    for r in reports:
        data[r.file] = {
            "overall_score": r.overall_score,
            "confidence": r.confidence,
        }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Saved baseline with {len(data)} entries to {path}")


def load_baseline(path: str) -> Dict[str, float]:
    """Load baseline scores from JSON file.

    Returns:
        Dict mapping file path -> overall_score.
        Empty dict if file does not exist.
    """
    p = Path(path)
    if not p.exists():
        logger.info(f"No baseline file at {path}")
        return {}

    with open(p) as f:
        raw = json.load(f)

    # Support both flat {file: score} and nested {file: {overall_score: ...}}
    result: Dict[str, float] = {}
    for fpath, val in raw.items():
        if isinstance(val, dict):
            result[fpath] = val.get("overall_score", 0.0)
        else:
            result[fpath] = float(val)

    logger.info(f"Loaded baseline with {len(result)} entries from {path}")
    return result


def diff_reports(
    current_reports: List[AnomalyReport],
    baseline: Dict[str, float],
    changed_files: Optional[Set[str]] = None,
) -> List[DiffReport]:
    """Compute diff between current reports and baseline.

    If ``changed_files`` is provided (e.g. from ``git diff --name-only``),
    only those files are included.  Otherwise all current reports are compared.

    Classification:
    - ``new``       — file not in baseline
    - ``regressed`` — score increased (delta > 0)
    - ``improved``  — score decreased (delta < 0)
    - ``modified``  — score unchanged but file changed
    """
    diffs: List[DiffReport] = []

    for report in current_reports:
        # If we have a changed-file set, filter to it
        if changed_files is not None and report.file not in changed_files:
            continue

        prev_score = baseline.get(report.file)

        if prev_score is None:
            diffs.append(DiffReport(
                file=report.file,
                status="new",
                current=report,
            ))
        else:
            delta = report.overall_score - prev_score
            if delta > 0.001:
                status = "regressed"
            elif delta < -0.001:
                status = "improved"
            else:
                status = "modified"

            diffs.append(DiffReport(
                file=report.file,
                status=status,
                current=report,
                previous_score=prev_score,
                score_delta=delta,
            ))

    # Sort: regressed first, then new, then modified, then improved
    order = {"regressed": 0, "new": 1, "modified": 2, "improved": 3}
    diffs.sort(key=lambda d: (order.get(d.status, 9), -(d.score_delta or 0)))

    return diffs
