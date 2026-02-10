"""SQL-based finder runner.

Loads .sql files from this directory, executes them against DuckDB,
and converts results to Finding objects compatible with the existing
output format.

Each SQL finder returns rows with specific columns. The runner maps
these to Finding objects using finder-specific conversion functions.
"""

from __future__ import annotations

import logging
from pathlib import Path, PurePosixPath
from typing import Any

from ...insights.models import Evidence, Finding

logger = logging.getLogger(__name__)


def _load_sql(name: str) -> str:
    """Load a .sql file from this package directory.

    Parameters
    ----------
    name:
        SQL filename without extension, e.g. "high_risk_hub"
    """
    # Try loading from the installed package first
    try:
        sql_dir = Path(__file__).parent
        sql_file = sql_dir / f"{name}.sql"
        if sql_file.exists():
            return sql_file.read_text()
    except Exception:
        pass

    raise FileNotFoundError(f"SQL finder not found: {name}.sql")


class SQLFinderRunner:
    """Executes SQL finder queries and converts results to Finding objects.

    Usage::

        from shannon_insight.query.engine import QueryEngine
        from shannon_insight.query.finders.runner import SQLFinderRunner

        engine = QueryEngine("/path/to/project")
        engine.load()
        runner = SQLFinderRunner(engine)

        findings = runner.run_all()
    """

    def __init__(self, engine) -> None:
        """
        Parameters
        ----------
        engine:
            A loaded QueryEngine instance.
        """
        self.engine = engine

    def run_all(self, snapshot_id: str | None = None) -> list[Finding]:
        """Run all SQL finders and return combined findings.

        Parameters
        ----------
        snapshot_id:
            If None, uses the latest snapshot.

        Returns
        -------
        list[Finding]
            Combined findings from all SQL finders, sorted by severity desc.
        """
        sid = snapshot_id or self.engine.latest_snapshot_id()
        if not sid:
            logger.warning("No snapshots available for SQL finders")
            return []

        findings: list[Finding] = []

        # Run each finder with error isolation
        for finder_name, converter in _FINDERS.items():
            try:
                sql = _load_sql(finder_name)
                rows = self.engine.execute_dict(sql, {"snapshot_id": sid})
                finder_findings = converter(rows)
                findings.extend(finder_findings)
                logger.debug(
                    "SQL finder %s: %d findings", finder_name, len(finder_findings)
                )
            except FileNotFoundError:
                logger.warning("SQL file not found for finder: %s", finder_name)
            except Exception as e:
                logger.warning("SQL finder %s failed: %s", finder_name, e)

        findings.sort(key=lambda f: f.severity, reverse=True)
        return findings

    def run_one(
        self, finder_name: str, snapshot_id: str | None = None
    ) -> list[Finding]:
        """Run a single SQL finder.

        Parameters
        ----------
        finder_name:
            Name of the SQL finder, e.g. "high_risk_hub".
        snapshot_id:
            If None, uses the latest snapshot.
        """
        sid = snapshot_id or self.engine.latest_snapshot_id()
        if not sid:
            return []

        sql = _load_sql(finder_name)
        rows = self.engine.execute_dict(sql, {"snapshot_id": sid})

        converter = _FINDERS.get(finder_name)
        if converter is None:
            logger.warning("No converter for finder: %s", finder_name)
            return []

        return converter(rows)


# ---------------------------------------------------------------------------
# Finder-specific row -> Finding converters
# ---------------------------------------------------------------------------


def _convert_high_risk_hub(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert high_risk_hub SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        evidence: list[Evidence] = []
        pcts: list[float] = []

        pr_pctl = row.get("pagerank_pctl", 0)
        br_pctl = row.get("blast_radius_pctl", 0)
        cog_pctl = row.get("cognitive_load_pctl", 0)

        if pr_pctl >= 0.90:
            pcts.append(pr_pctl)
            evidence.append(Evidence(
                signal="pagerank",
                value=row.get("pagerank", 0) or 0,
                percentile=pr_pctl,
                description=f"{row.get('in_degree', 0) or 0} files import this directly",
            ))

        if br_pctl >= 0.90:
            pcts.append(br_pctl)
            br_size = row.get("blast_radius_size", 0) or 0
            evidence.append(Evidence(
                signal="blast_radius_size",
                value=float(br_size),
                percentile=br_pctl,
                description=f"a bug here could affect {br_size} files",
            ))

        if row.get("has_high_complexity"):
            pcts.append(cog_pctl)
            evidence.append(Evidence(
                signal="cognitive_load",
                value=row.get("cognitive_load", 0) or 0,
                percentile=cog_pctl,
                description=f"harder to understand than {cog_pctl * 100:.0f}% of files",
            ))

        if row.get("has_high_churn"):
            traj = row.get("churn_trajectory", "")
            changes = row.get("total_changes", 0) or 0
            evidence.append(Evidence(
                signal="churn_trajectory",
                value=0.0,
                percentile=0.0,
                description=f"trajectory={traj}, {changes} changes",
            ))

        avg_pctl = sum(pcts) / len(pcts) if pcts else 0.9
        severity = 1.0 * max(0.5, avg_pctl)

        # Build suggestion
        has_complexity = bool(row.get("has_high_complexity"))
        has_churn = bool(row.get("has_high_churn"))
        if has_complexity and has_churn:
            suggestion = (
                "This file is central, complex, and frequently modified. "
                "Split into smaller modules to reduce coupling and simplify changes."
            )
        elif has_complexity:
            suggestion = (
                "This file is central and complex. "
                "Break into smaller pieces to make changes safer and reviews easier."
            )
        else:
            suggestion = (
                "This file is central and churning. "
                "Consider stabilizing the interface or extracting frequently-changing parts."
            )

        findings.append(Finding(
            finding_type="high_risk_hub",
            severity=severity,
            title=f"High-risk hub: {path}",
            files=[path],
            evidence=evidence,
            suggestion=suggestion,
            confidence=0.9,
            effort="MEDIUM",
            scope="FILE",
        ))

    return findings


def _convert_orphan_code(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert orphan_code SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        in_degree = row.get("in_degree", 0) or 0
        role = row.get("role", "UNKNOWN") or "UNKNOWN"
        depth = row.get("depth") if row.get("depth") is not None else -1

        evidence = [
            Evidence(
                signal="in_degree",
                value=float(in_degree),
                percentile=0.0,
                description="No files import this",
            ),
            Evidence(
                signal="role",
                value=0.0,
                percentile=0.0,
                description=f"Classified as {role}",
            ),
        ]

        if depth == -1:
            evidence.append(Evidence(
                signal="depth",
                value=-1.0,
                percentile=0.0,
                description="Unreachable from entry points",
            ))

        findings.append(Finding(
            finding_type="orphan_code",
            severity=0.55,
            title=f"Orphan file: {path}",
            files=[path],
            evidence=evidence,
            suggestion="Wire into dependency graph or remove if unused.",
            confidence=1.0,
            effort="LOW",
            scope="FILE",
        ))

    return findings


def _convert_hidden_coupling(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert hidden_coupling SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        file_a = row["file_a"]
        file_b = row["file_b"]
        lift = row.get("lift", 0) or 0
        conf_ab = row.get("confidence_a_b", 0) or 0
        conf_ba = row.get("confidence_b_a", 0) or 0
        count = row.get("cochange_count", 0) or 0
        severity = row.get("severity", 0.45) or 0.45

        # Determine which direction has higher confidence
        a_name = PurePosixPath(file_a).name
        b_name = PurePosixPath(file_b).name

        if conf_ab >= conf_ba:
            conf_desc = (
                f"when {a_name} changed, {b_name} also changed "
                f"{count} times ({conf_ab * 100:.0f}%)"
            )
        else:
            conf_desc = (
                f"when {b_name} changed, {a_name} also changed "
                f"{count} times ({conf_ba * 100:.0f}%)"
            )

        same_package = str(PurePosixPath(file_a).parent) == str(PurePosixPath(file_b).parent)

        if same_package:
            suggestion = (
                f"{a_name} and {b_name} are in the same package and "
                f"always change together, but neither imports the other. "
                f"Make this explicit: add an import or extract shared logic."
            )
        else:
            suggestion = (
                "These files live in different packages but always change together. "
                "Find what ties them and make it explicit via import or shared module."
            )

        findings.append(Finding(
            finding_type="hidden_coupling",
            severity=severity,
            title=f"{file_a} and {file_b} always change together",
            files=[file_a, file_b],
            evidence=[
                Evidence(
                    signal="cochange_count",
                    value=float(count),
                    percentile=0,
                    description=conf_desc,
                ),
                Evidence(
                    signal="cochange_lift",
                    value=lift,
                    percentile=0,
                    description=f"{lift:.1f}x more often than expected by chance",
                ),
                Evidence(
                    signal="no_import",
                    value=0.0,
                    percentile=0,
                    description="neither file imports the other",
                ),
            ],
            suggestion=suggestion,
            confidence=0.8,
            effort="LOW",
            scope="FILE_PAIR",
        ))

    return findings


# Registry of SQL finders -> their converter functions
_FINDERS: dict[str, Any] = {
    "high_risk_hub": _convert_high_risk_hub,
    "orphan_code": _convert_orphan_code,
    "hidden_coupling": _convert_hidden_coupling,
}
