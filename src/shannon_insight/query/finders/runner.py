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
                logger.debug("SQL finder %s: %d findings", finder_name, len(finder_findings))
            except FileNotFoundError:
                logger.warning("SQL file not found for finder: %s", finder_name)
            except Exception as e:
                logger.warning("SQL finder %s failed: %s", finder_name, e)

        findings.sort(key=lambda f: f.severity, reverse=True)
        return findings

    def run_one(self, finder_name: str, snapshot_id: str | None = None) -> list[Finding]:
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

        return list(converter(rows))


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

        # Percentiles are 0-1 (0.90 = 90th percentile)
        if pr_pctl >= 0.90:
            pcts.append(pr_pctl)
            evidence.append(
                Evidence(
                    signal="pagerank",
                    value=row.get("pagerank", 0) or 0,
                    percentile=pr_pctl,
                    description=f"{row.get('in_degree', 0) or 0} files import this directly",
                )
            )

        if br_pctl >= 0.90:
            pcts.append(br_pctl)
            br_size = row.get("blast_radius_size", 0) or 0
            evidence.append(
                Evidence(
                    signal="blast_radius_size",
                    value=float(br_size),
                    percentile=br_pctl,
                    description=f"a bug here could affect {br_size} files",
                )
            )

        if row.get("has_high_complexity"):
            pcts.append(cog_pctl)
            evidence.append(
                Evidence(
                    signal="cognitive_load",
                    value=row.get("cognitive_load", 0) or 0,
                    percentile=cog_pctl,
                    description=f"harder to understand than {cog_pctl:.0f}% of files",
                )
            )

        if row.get("has_high_churn"):
            traj = row.get("churn_trajectory", "")
            changes = row.get("total_changes", 0) or 0
            evidence.append(
                Evidence(
                    signal="churn_trajectory",
                    value=0.0,
                    percentile=0.0,
                    description=f"trajectory={traj}, {changes} changes",
                )
            )

        avg_pctl = (sum(pcts) / len(pcts) / 100.0) if pcts else 0.9
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

        findings.append(
            Finding(
                finding_type="high_risk_hub",
                severity=severity,
                title=f"High-risk hub: {path}",
                files=[path],
                evidence=evidence,
                suggestion=suggestion,
                confidence=0.9,
                effort="MEDIUM",
                scope="FILE",
            )
        )

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
            evidence.append(
                Evidence(
                    signal="depth",
                    value=-1.0,
                    percentile=0.0,
                    description="Unreachable from entry points",
                )
            )

        findings.append(
            Finding(
                finding_type="orphan_code",
                severity=0.55,
                title=f"Orphan file: {path}",
                files=[path],
                evidence=evidence,
                suggestion="Wire into dependency graph or remove if unused.",
                confidence=1.0,
                effort="LOW",
                scope="FILE",
            )
        )

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
                f"when {a_name} changed, {b_name} also changed {count} times ({conf_ab * 100:.0f}%)"
            )
        else:
            conf_desc = (
                f"when {b_name} changed, {a_name} also changed {count} times ({conf_ba * 100:.0f}%)"
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

        findings.append(
            Finding(
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
            )
        )

    return findings


def _convert_phantom_imports(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert phantom_imports SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        count = row.get("phantom_import_count", 0) or 0
        import_count = row.get("import_count", 0) or 0
        phantom_ratio = row.get("phantom_ratio", 0) or 0

        evidence = [
            Evidence(
                signal="phantom_import_count",
                value=float(count),
                percentile=0.0,
                description=f"{count} unresolved import(s)",
            ),
            Evidence(
                signal="phantom_ratio",
                value=phantom_ratio,
                percentile=0.0,
                description=(
                    f"{count} of {import_count} imports are phantoms"
                    if import_count > 0
                    else f"{count} phantom import(s)"
                ),
            ),
        ]

        findings.append(
            Finding(
                finding_type="phantom_imports",
                severity=0.65,
                title=f"Phantom imports in {path}",
                files=[path],
                evidence=evidence,
                suggestion="Create missing module or replace with existing library.",
                confidence=1.0,
                effort="MEDIUM",
                scope="FILE",
            )
        )

    return findings


def _convert_hollow_code(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert hollow_code SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        stub_ratio = row.get("stub_ratio", 0) or 0
        impl_gini = row.get("impl_gini", 0) or 0
        func_count = row.get("function_count", 0) or 0

        evidence = [
            Evidence(
                signal="stub_ratio",
                value=stub_ratio,
                percentile=0.0,
                description=f"{stub_ratio * 100:.0f}% of functions are stubs",
            ),
            Evidence(
                signal="impl_gini",
                value=impl_gini,
                percentile=0.0,
                description=f"implementation unevenness: {impl_gini:.2f}",
            ),
            Evidence(
                signal="function_count",
                value=float(func_count),
                percentile=0.0,
                description=f"{func_count} functions total",
            ),
        ]

        findings.append(
            Finding(
                finding_type="hollow_code",
                severity=0.71,
                title=f"Hollow code: {path}",
                files=[path],
                evidence=evidence,
                suggestion=(
                    "Implement the stub functions. Priority: functions called by other files."
                ),
                confidence=0.9,
                effort="MEDIUM",
                scope="FILE",
            )
        )

    return findings


def _convert_unstable_file(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert unstable_file SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        trajectory = row.get("churn_trajectory", "") or ""
        total_changes = row.get("total_changes", 0) or 0
        churn_slope = row.get("churn_slope", 0) or 0
        churn_cv = row.get("churn_cv", 0) or 0
        fix_ratio = row.get("fix_ratio", 0) or 0

        evidence = [
            Evidence(
                signal="churn_trajectory",
                value=0.0,
                percentile=0.0,
                description=f"trajectory: {trajectory}",
            ),
            Evidence(
                signal="total_changes",
                value=float(total_changes),
                percentile=0.0,
                description=f"{total_changes} total changes",
            ),
            Evidence(
                signal="churn_slope",
                value=churn_slope,
                percentile=0.0,
                description=f"churn slope: {churn_slope:.2f}",
            ),
            Evidence(
                signal="churn_cv",
                value=churn_cv,
                percentile=0.0,
                description=f"coefficient of variation: {churn_cv:.2f}",
            ),
        ]

        if fix_ratio > 0:
            evidence.append(
                Evidence(
                    signal="fix_ratio",
                    value=fix_ratio,
                    percentile=0.0,
                    description=f"{fix_ratio * 100:.0f}% of changes are bug fixes",
                )
            )

        findings.append(
            Finding(
                finding_type="unstable_file",
                severity=0.7,
                title=f"Unstable file: {path}",
                files=[path],
                evidence=evidence,
                suggestion=(
                    "Investigate why this file isn't stabilizing. "
                    "Check fix_ratio for recurring bugs."
                ),
                confidence=0.85,
                effort="MEDIUM",
                scope="FILE",
            )
        )

    return findings


def _convert_god_file(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert god_file SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        cog_load = row.get("cognitive_load", 0) or 0
        cog_pctl = row.get("cognitive_load_pctl", 0) or 0
        coherence = row.get("semantic_coherence", 0) or 0
        coherence_pctl = row.get("coherence_pctl", 0) or 0
        func_count = row.get("function_count", 0) or 0
        concept_count = row.get("concept_count", 0) or 0
        concept_entropy = row.get("concept_entropy", 0) or 0

        evidence = [
            Evidence(
                signal="cognitive_load",
                value=cog_load,
                percentile=cog_pctl,
                description=(f"harder to understand than {cog_pctl:.0f}% of files"),
            ),
            Evidence(
                signal="semantic_coherence",
                value=coherence,
                percentile=coherence_pctl,
                description=(f"less focused than {(1 - coherence_pctl):.0f}% of files"),
            ),
        ]

        if func_count > 0:
            evidence.append(
                Evidence(
                    signal="function_count",
                    value=float(func_count),
                    percentile=0.0,
                    description=f"{func_count} functions",
                )
            )

        if concept_count > 0:
            evidence.append(
                Evidence(
                    signal="concept_count",
                    value=float(concept_count),
                    percentile=0.0,
                    description=f"{concept_count} distinct concepts (entropy: {concept_entropy:.2f})",
                )
            )

        # Severity scales with percentile gap
        severity = 0.8 * max(0.5, cog_pctl)

        findings.append(
            Finding(
                finding_type="god_file",
                severity=severity,
                title=f"God file: {path}",
                files=[path],
                evidence=evidence,
                suggestion=("Split by concept clusters. Each concept = a candidate file."),
                confidence=0.85,
                effort="HIGH",
                scope="FILE",
            )
        )

    return findings


def _convert_naming_drift(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert naming_drift SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        drift = row.get("naming_drift", 0) or 0

        evidence = [
            Evidence(
                signal="naming_drift",
                value=drift,
                percentile=0.0,
                description=f"naming drift score: {drift:.2f}",
            ),
        ]

        findings.append(
            Finding(
                finding_type="naming_drift",
                severity=0.45,
                title=f"Naming drift: {path}",
                files=[path],
                evidence=evidence,
                suggestion=(
                    "Rename file to match its actual content, or extract mismatched logic."
                ),
                confidence=0.8,
                effort="LOW",
                scope="FILE",
            )
        )

    return findings


def _convert_flat_architecture(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert flat_architecture SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        max_depth = row.get("max_depth", 0) or 0
        glue_deficit = row.get("glue_deficit", 0) or 0
        file_count = row.get("file_count", 0) or 0
        orphan_ratio = row.get("orphan_ratio", 0) or 0

        evidence = [
            Evidence(
                signal="depth",
                value=float(max_depth),
                percentile=0.0,
                description=f"maximum dependency depth: {max_depth}",
            ),
            Evidence(
                signal="glue_deficit",
                value=glue_deficit,
                percentile=0.0,
                description=f"glue deficit: {glue_deficit:.2f}",
            ),
            Evidence(
                signal="file_count",
                value=float(file_count),
                percentile=0.0,
                description=f"{file_count} files analyzed",
            ),
            Evidence(
                signal="orphan_ratio",
                value=orphan_ratio,
                percentile=0.0,
                description=f"orphan ratio: {orphan_ratio:.2f}",
            ),
        ]

        findings.append(
            Finding(
                finding_type="flat_architecture",
                severity=0.60,
                title="Flat architecture: no composition layer",
                files=[],
                evidence=evidence,
                suggestion=(
                    "Add composition layer. Many leaf modules exist but nothing orchestrates them."
                ),
                confidence=0.9,
                effort="HIGH",
                scope="CODEBASE",
            )
        )

    return findings


def _convert_dead_dependency(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert dead_dependency SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        file_a = row["file_a"]
        file_b = row["file_b"]
        source_changes = row.get("source_changes", 0) or 0
        target_changes = row.get("target_changes", 0) or 0

        a_name = PurePosixPath(file_a).name
        b_name = PurePosixPath(file_b).name

        evidence = [
            Evidence(
                signal="structural_edge",
                value=1.0,
                percentile=0.0,
                description=f"{a_name} imports {b_name}",
            ),
            Evidence(
                signal="cochange_count",
                value=0.0,
                percentile=0.0,
                description=(f"zero co-changes over {source_changes} + {target_changes} commits"),
            ),
        ]

        findings.append(
            Finding(
                finding_type="dead_dependency",
                severity=0.4,
                title=f"Dead dependency: {file_a} -> {file_b}",
                files=[file_a, file_b],
                evidence=evidence,
                suggestion=(
                    "This import may be dead. Verify the imported symbols are actually used."
                ),
                confidence=0.7,
                effort="LOW",
                scope="FILE_PAIR",
            )
        )

    return findings


def _convert_zone_of_pain(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert zone_of_pain SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        module = row["module_path"]
        abstractness = row.get("abstractness", 0) or 0
        instability = row.get("instability", 0) or 0
        distance = row.get("main_seq_distance", 0) or 0
        file_count = row.get("file_count", 0) or 0

        evidence = [
            Evidence(
                signal="abstractness",
                value=abstractness,
                percentile=0.0,
                description=f"abstractness: {abstractness:.2f} (< 0.3 = concrete)",
            ),
            Evidence(
                signal="instability",
                value=instability,
                percentile=0.0,
                description=f"instability: {instability:.2f} (< 0.3 = hard to change)",
            ),
            Evidence(
                signal="main_seq_distance",
                value=distance,
                percentile=0.0,
                description=f"distance from main sequence: {distance:.2f}",
            ),
            Evidence(
                signal="file_count",
                value=float(file_count),
                percentile=0.0,
                description=f"{file_count} files in module",
            ),
        ]

        findings.append(
            Finding(
                finding_type="zone_of_pain",
                severity=0.60,
                title=f"Zone of pain: {module}",
                files=[],
                evidence=evidence,
                suggestion=(
                    "Concrete and stable -- hard to change. "
                    "Extract interfaces or reduce dependents."
                ),
                confidence=0.85,
                effort="HIGH",
                scope="MODULE",
            )
        )

    return findings


def _convert_boundary_mismatch(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert boundary_mismatch SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        module = row["module_path"]
        alignment = row.get("boundary_alignment", 0) or 0
        file_count = row.get("file_count", 0) or 0
        cohesion = row.get("cohesion", 0) or 0

        evidence = [
            Evidence(
                signal="boundary_alignment",
                value=alignment,
                percentile=0.0,
                description=f"boundary alignment: {alignment:.2f} (< 0.7 = mismatch)",
            ),
            Evidence(
                signal="file_count",
                value=float(file_count),
                percentile=0.0,
                description=f"{file_count} files in module",
            ),
            Evidence(
                signal="cohesion",
                value=cohesion,
                percentile=0.0,
                description=f"internal cohesion: {cohesion:.2f}",
            ),
        ]

        findings.append(
            Finding(
                finding_type="boundary_mismatch",
                severity=0.6,
                title=f"Boundary mismatch: {module}",
                files=[],
                evidence=evidence,
                suggestion=(
                    "Directory boundary doesn't match dependency structure. Consider reorganizing."
                ),
                confidence=0.8,
                effort="HIGH",
                scope="MODULE",
            )
        )

    return findings


def _convert_layer_violation(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert layer_violation SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        module = row["module_path"]
        violation_count = row.get("layer_violation_count", 0) or 0
        file_count = row.get("file_count", 0) or 0

        evidence = [
            Evidence(
                signal="layer_violation_count",
                value=float(violation_count),
                percentile=0.0,
                description=f"{violation_count} layer violation(s)",
            ),
            Evidence(
                signal="file_count",
                value=float(file_count),
                percentile=0.0,
                description=f"{file_count} files in module",
            ),
        ]

        findings.append(
            Finding(
                finding_type="layer_violation",
                severity=0.52,
                title=f"Layer violation in {module}",
                files=[],
                evidence=evidence,
                suggestion=("Inject dependency or restructure to respect layer ordering."),
                confidence=0.8,
                effort="MEDIUM",
                scope="MODULE",
            )
        )

    return findings


def _convert_copy_paste_clone(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert copy_paste_clone SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        file_a = row["file_a"]
        file_b = row["file_b"]
        ncd_score = row.get("ncd_score", 0) or 0
        lines_a = row.get("lines_a", 0) or 0
        lines_b = row.get("lines_b", 0) or 0

        a_name = PurePosixPath(file_a).name
        b_name = PurePosixPath(file_b).name

        evidence = [
            Evidence(
                signal="ncd_score",
                value=ncd_score,
                percentile=0.0,
                description=f"NCD similarity: {ncd_score:.2f} (< 0.3 = clone)",
            ),
            Evidence(
                signal="lines",
                value=float(lines_a + lines_b),
                percentile=0.0,
                description=f"{a_name}: {lines_a} lines, {b_name}: {lines_b} lines",
            ),
        ]

        findings.append(
            Finding(
                finding_type="copy_paste_clone",
                severity=0.50,
                title=f"Copy-paste clone: {file_a} <-> {file_b}",
                files=[file_a, file_b],
                evidence=evidence,
                suggestion="Extract shared logic into a common module.",
                confidence=0.85,
                effort="MEDIUM",
                scope="FILE_PAIR",
            )
        )

    return findings


def _convert_weak_link(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert weak_link SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        delta_h = row.get("delta_h", 0) or 0
        raw_risk = row.get("raw_risk", 0) or 0
        risk_score = row.get("risk_score", 0) or 0

        evidence = [
            Evidence(
                signal="delta_h",
                value=delta_h,
                percentile=0.0,
                description=(
                    f"health Laplacian delta: {delta_h:.2f} (file much worse than neighbors)"
                ),
            ),
            Evidence(
                signal="raw_risk",
                value=raw_risk,
                percentile=0.0,
                description=f"raw risk score: {raw_risk:.2f}",
            ),
            Evidence(
                signal="risk_score",
                value=risk_score,
                percentile=0.0,
                description=f"normalized risk: {risk_score:.2f}",
            ),
        ]

        findings.append(
            Finding(
                finding_type="weak_link",
                severity=0.75,
                title=f"Weak link: {path}",
                files=[path],
                evidence=evidence,
                suggestion=(
                    "This file drags down its healthy neighborhood. Prioritize improvement."
                ),
                confidence=0.8,
                effort="MEDIUM",
                scope="FILE",
            )
        )

    return findings


def _convert_knowledge_silo(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert knowledge_silo SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        bus_factor = row.get("bus_factor", 0) or 0
        author_entropy = row.get("author_entropy", 0) or 0
        pagerank = row.get("pagerank", 0) or 0
        pagerank_pctl = row.get("pagerank_pctl", 0) or 0
        total_changes = row.get("total_changes", 0) or 0

        evidence = [
            Evidence(
                signal="bus_factor",
                value=bus_factor,
                percentile=0.0,
                description=f"bus factor: {bus_factor:.1f} (only ~{bus_factor:.0f} contributor(s))",
            ),
            Evidence(
                signal="author_entropy",
                value=author_entropy,
                percentile=0.0,
                description=f"author entropy: {author_entropy:.2f}",
            ),
            Evidence(
                signal="pagerank",
                value=pagerank,
                percentile=pagerank_pctl,
                description=f"more central than {pagerank_pctl:.0f}% of files",
            ),
            Evidence(
                signal="total_changes",
                value=float(total_changes),
                percentile=0.0,
                description=f"{total_changes} total changes",
            ),
        ]

        findings.append(
            Finding(
                finding_type="knowledge_silo",
                severity=0.70,
                title=f"Knowledge silo: {path}",
                files=[path],
                evidence=evidence,
                suggestion=("Pair-program or rotate ownership. Single point of knowledge failure."),
                confidence=0.8,
                effort="LOW",
                scope="FILE",
            )
        )

    return findings


def _convert_review_blindspot(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert review_blindspot SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        bus_factor = row.get("bus_factor", 0) or 0
        pagerank = row.get("pagerank", 0) or 0
        pagerank_pctl = row.get("pagerank_pctl", 0) or 0
        total_changes = row.get("total_changes", 0) or 0

        evidence = [
            Evidence(
                signal="pagerank",
                value=pagerank,
                percentile=pagerank_pctl,
                description=f"more central than {pagerank_pctl:.0f}% of files",
            ),
            Evidence(
                signal="bus_factor",
                value=bus_factor,
                percentile=0.0,
                description=f"bus factor: {bus_factor:.1f}",
            ),
            Evidence(
                signal="no_test_file",
                value=0.0,
                percentile=0.0,
                description="no corresponding test file found",
            ),
            Evidence(
                signal="total_changes",
                value=float(total_changes),
                percentile=0.0,
                description=f"{total_changes} total changes",
            ),
        ]

        findings.append(
            Finding(
                finding_type="review_blindspot",
                severity=0.80,
                title=f"Review blindspot: {path}",
                files=[path],
                evidence=evidence,
                suggestion=(
                    "High-centrality code with single owner and no tests. Add tests and reviewer."
                ),
                confidence=0.75,
                effort="MEDIUM",
                scope="FILE",
            )
        )

    return findings


def _convert_bug_attractor(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert bug_attractor SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        path = row["file_path"]
        fix_ratio = row.get("fix_ratio", 0) or 0
        pagerank = row.get("pagerank", 0) or 0
        pagerank_pctl = row.get("pagerank_pctl", 0) or 0
        total_changes = row.get("total_changes", 0) or 0
        blast_radius = row.get("blast_radius_size", 0) or 0

        evidence = [
            Evidence(
                signal="fix_ratio",
                value=fix_ratio,
                percentile=0.0,
                description=f"{fix_ratio * 100:.0f}% of changes are bug fixes",
            ),
            Evidence(
                signal="pagerank",
                value=pagerank,
                percentile=pagerank_pctl,
                description=f"more central than {pagerank_pctl:.0f}% of files",
            ),
            Evidence(
                signal="blast_radius_size",
                value=float(blast_radius),
                percentile=0.0,
                description=f"a bug here could affect {blast_radius} files",
            ),
            Evidence(
                signal="total_changes",
                value=float(total_changes),
                percentile=0.0,
                description=f"{total_changes} total changes",
            ),
        ]

        findings.append(
            Finding(
                finding_type="bug_attractor",
                severity=0.70,
                title=f"Bug attractor: {path}",
                files=[path],
                evidence=evidence,
                suggestion=(
                    "40%+ of changes are bug fixes in a central file. Root-cause analysis needed."
                ),
                confidence=0.8,
                effort="MEDIUM",
                scope="FILE",
            )
        )

    return findings


def _convert_conway_violation(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert conway_violation SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        module_a = row["module_a"]
        module_b = row["module_b"]
        gini_a = row.get("gini_a", 0) or 0
        gini_b = row.get("gini_b", 0) or 0
        coupling_a = row.get("coupling_a", 0) or 0
        coupling_b = row.get("coupling_b", 0) or 0

        evidence = [
            Evidence(
                signal="knowledge_gini",
                value=max(gini_a, gini_b),
                percentile=0.0,
                description=(
                    f"ownership concentration: {module_a}={gini_a:.2f}, {module_b}={gini_b:.2f}"
                ),
            ),
            Evidence(
                signal="coupling",
                value=max(coupling_a, coupling_b),
                percentile=0.0,
                description=(
                    f"structural coupling: {module_a}={coupling_a:.2f}, {module_b}={coupling_b:.2f}"
                ),
            ),
        ]

        findings.append(
            Finding(
                finding_type="conway_violation",
                severity=0.55,
                title=f"Conway violation: {module_a} <-> {module_b}",
                files=[],
                evidence=evidence,
                suggestion=(
                    "Coupled modules maintained by different teams. Align team boundaries."
                ),
                confidence=0.7,
                effort="HIGH",
                scope="MODULE_PAIR",
            )
        )

    return findings


def _convert_accidental_coupling(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert accidental_coupling SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        file_a = row["file_a"]
        file_b = row["file_b"]
        coherence_a = row.get("coherence_a", 0) or 0
        coherence_b = row.get("coherence_b", 0) or 0
        disparity = row.get("concept_disparity", 0) or 0
        sem_dist = row.get("semantic_distance")

        a_name = PurePosixPath(file_a).name
        b_name = PurePosixPath(file_b).name

        evidence = [
            Evidence(
                signal="structural_edge",
                value=1.0,
                percentile=0.0,
                description=f"{a_name} depends on {b_name}",
            ),
        ]

        if sem_dist is not None:
            evidence.append(
                Evidence(
                    signal="semantic_distance",
                    value=sem_dist,
                    percentile=0.0,
                    description=f"semantic distance: {sem_dist:.2f} (> 0.8 = unrelated)",
                )
            )
        else:
            evidence.append(
                Evidence(
                    signal="concept_disparity",
                    value=disparity,
                    percentile=0.0,
                    description=f"concept disparity: {disparity:.2f}",
                )
            )

        evidence.append(
            Evidence(
                signal="semantic_coherence",
                value=0.0,
                percentile=0.0,
                description=(f"coherence: {a_name}={coherence_a:.2f}, {b_name}={coherence_b:.2f}"),
            )
        )

        findings.append(
            Finding(
                finding_type="accidental_coupling",
                severity=0.50,
                title=f"Accidental coupling: {file_a} -> {file_b}",
                files=[file_a, file_b],
                evidence=evidence,
                suggestion=(
                    "Connected but unrelated concepts. "
                    "Consider removing or abstracting the dependency."
                ),
                confidence=0.65,
                effort="MEDIUM",
                scope="FILE_PAIR",
            )
        )

    return findings


def _convert_chronic_problem(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert chronic_problem SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        finding_type = row.get("finding_type", "") or ""
        snapshot_count = row.get("snapshot_count", 0) or 0
        chronic_severity = row.get("chronic_severity", 0.65) or 0.65
        title = row.get("title", "") or ""
        files_str = row.get("files", "") or ""
        suggestion = row.get("suggestion", "") or ""
        effort = row.get("effort", "MEDIUM") or "MEDIUM"
        scope = row.get("scope", "FILE") or "FILE"

        # Parse files from stored format (could be JSON array or comma-separated)
        files: list[str] = []
        if files_str:
            if files_str.startswith("["):
                import json

                try:
                    files = json.loads(files_str)
                except (json.JSONDecodeError, TypeError):
                    files = [files_str]
            else:
                files = [f.strip() for f in files_str.split(",") if f.strip()]

        evidence = [
            Evidence(
                signal="persistence_count",
                value=float(snapshot_count),
                percentile=0.0,
                description=f"persisted across {snapshot_count} snapshots",
            ),
            Evidence(
                signal="base_finding_type",
                value=0.0,
                percentile=0.0,
                description=f"wraps: {finding_type} - {title}",
            ),
        ]

        findings.append(
            Finding(
                finding_type="chronic_problem",
                severity=chronic_severity,
                title=f"Chronic problem ({snapshot_count} snapshots): {title}",
                files=files,
                evidence=evidence,
                suggestion=(
                    f"This issue has persisted for {snapshot_count} snapshots. "
                    f"Prioritize resolution. Original: {suggestion}"
                ),
                confidence=0.95,
                effort=effort,
                scope=scope,
            )
        )

    return findings


def _convert_architecture_erosion(rows: list[dict[str, Any]]) -> list[Finding]:
    """Convert architecture_erosion SQL results to Findings."""
    findings: list[Finding] = []

    for row in rows:
        snapshot_count = row.get("snapshot_count", 0) or 0
        latest_rate = row.get("latest_violation_rate", 0) or 0
        first_rate = row.get("first_violation_rate", 0) or 0
        delta = row.get("violation_rate_delta", 0) or 0
        arch_health = row.get("latest_arch_health", 0) or 0

        evidence = [
            Evidence(
                signal="violation_rate",
                value=latest_rate,
                percentile=0.0,
                description=(
                    f"violation rate: {first_rate:.2f} -> {latest_rate:.2f} "
                    f"over {snapshot_count} snapshots"
                ),
            ),
            Evidence(
                signal="violation_rate_delta",
                value=delta,
                percentile=0.0,
                description=f"rate increased by {delta:.2f}",
            ),
            Evidence(
                signal="architecture_health",
                value=arch_health,
                percentile=0.0,
                description=f"current architecture health: {arch_health:.2f}",
            ),
        ]

        findings.append(
            Finding(
                finding_type="architecture_erosion",
                severity=0.65,
                title="Architecture erosion: violations increasing",
                files=[],
                evidence=evidence,
                suggestion=("Architecture is actively eroding. Schedule structural refactoring."),
                confidence=0.85,
                effort="HIGH",
                scope="CODEBASE",
            )
        )

    return findings


# Registry of SQL finders -> their converter functions
_FINDERS: dict[str, Any] = {
    "high_risk_hub": _convert_high_risk_hub,
    "orphan_code": _convert_orphan_code,
    "hidden_coupling": _convert_hidden_coupling,
    "phantom_imports": _convert_phantom_imports,
    "hollow_code": _convert_hollow_code,
    "unstable_file": _convert_unstable_file,
    "god_file": _convert_god_file,
    "naming_drift": _convert_naming_drift,
    "flat_architecture": _convert_flat_architecture,
    "dead_dependency": _convert_dead_dependency,
    "zone_of_pain": _convert_zone_of_pain,
    "boundary_mismatch": _convert_boundary_mismatch,
    "layer_violation": _convert_layer_violation,
    "copy_paste_clone": _convert_copy_paste_clone,
    "weak_link": _convert_weak_link,
    "knowledge_silo": _convert_knowledge_silo,
    "review_blindspot": _convert_review_blindspot,
    "bug_attractor": _convert_bug_attractor,
    "conway_violation": _convert_conway_violation,
    "accidental_coupling": _convert_accidental_coupling,
    "chronic_problem": _convert_chronic_problem,
    "architecture_erosion": _convert_architecture_erosion,
}
