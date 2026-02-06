"""Rich terminal formatter for SnapshotDiff output.

Renders a structured diff between two analysis snapshots with colour-coded
sections for new findings, resolved findings, severity changes, and
per-file metric deltas.
"""

import json
from typing import Optional

from rich.console import Console
from rich.table import Table

from ..persistence.diff_models import FileDelta, FindingDelta, MetricDelta, SnapshotDiff
from ..persistence.models import FindingRecord

# ── Finding type presentation ────────────────────────────────────────────────

_TYPE_COLORS = {
    "high_risk_hub": "red",
    "hidden_coupling": "yellow",
    "god_file": "magenta",
    "unstable_file": "yellow",
    "boundary_mismatch": "cyan",
    "dead_dependency": "dim",
}

_TYPE_LABELS = {
    "high_risk_hub": "HIGH RISK HUB",
    "hidden_coupling": "HIDDEN COUPLING",
    "god_file": "GOD FILE",
    "unstable_file": "UNSTABLE FILE",
    "boundary_mismatch": "BOUNDARY MISMATCH",
    "dead_dependency": "DEAD DEPENDENCY",
}


def _direction_icon(direction: str) -> str:
    """Return a Rich-markup icon for a metric direction."""
    if direction == "better":
        return "[green]+[/green]"
    elif direction == "worse":
        return "[red]![/red]"
    return "[dim]~[/dim]"


def _delta_str(delta: float) -> str:
    """Format a numeric delta with sign."""
    if delta >= 0:
        return f"+{delta:.4f}"
    return f"{delta:.4f}"


def _short_sha(sha: Optional[str]) -> str:
    """Shorten a commit SHA for display, or return a placeholder."""
    if not sha:
        return "(no commit)"
    return sha[:8]


class InsightDiffFormatter:
    """Render a SnapshotDiff to a Rich console.

    Usage::

        formatter = InsightDiffFormatter()
        formatter.render(diff)                # default: rich console
        formatter.render(diff, fmt="json")    # machine-readable JSON
    """

    def __init__(self, console: Optional[Console] = None):
        self._console = console or Console()

    # ── Public API ───────────────────────────────────────────────────────

    def render(
        self,
        diff: SnapshotDiff,
        fmt: str = "rich",
        verbose: bool = False,
    ) -> None:
        """Render the diff to the console.

        Args:
            diff: The SnapshotDiff to render.
            fmt: Output format — ``"rich"`` for terminal, ``"json"`` for
                 machine-readable output.
            verbose: If True, show per-file metric details even when there
                     are no findings-level changes.
        """
        if fmt == "json":
            self._render_json(diff)
        else:
            self._render_rich(diff, verbose=verbose)

    # ── JSON output ──────────────────────────────────────────────────────

    def _render_json(self, diff: SnapshotDiff) -> None:
        """Emit machine-readable JSON representation of the diff."""
        output = {
            "old_commit": diff.old_commit,
            "new_commit": diff.new_commit,
            "old_timestamp": diff.old_timestamp,
            "new_timestamp": diff.new_timestamp,
            "new_findings": [self._finding_to_dict(f) for f in diff.new_findings],
            "resolved_findings": [self._finding_to_dict(f) for f in diff.resolved_findings],
            "worsened_findings": [self._finding_delta_to_dict(fd) for fd in diff.worsened_findings],
            "improved_findings": [self._finding_delta_to_dict(fd) for fd in diff.improved_findings],
            "file_deltas": [self._file_delta_to_dict(fd) for fd in diff.file_deltas],
            "codebase_deltas": {
                k: self._metric_delta_to_dict(v) for k, v in diff.codebase_deltas.items()
            },
            "renames": [{"old": old, "new": new} for old, new in diff.renames],
        }
        print(json.dumps(output, indent=2))

    @staticmethod
    def _finding_to_dict(f: FindingRecord) -> dict:
        return {
            "finding_type": f.finding_type,
            "identity_key": f.identity_key,
            "severity": round(f.severity, 4),
            "title": f.title,
            "files": f.files,
            "suggestion": f.suggestion,
        }

    @staticmethod
    def _finding_delta_to_dict(fd: FindingDelta) -> dict:
        return {
            "status": fd.status,
            "finding_type": fd.finding.finding_type,
            "identity_key": fd.finding.identity_key,
            "title": fd.finding.title,
            "files": fd.finding.files,
            "old_severity": round(fd.old_severity, 4) if fd.old_severity is not None else None,
            "new_severity": round(fd.new_severity, 4) if fd.new_severity is not None else None,
            "severity_delta": round(fd.severity_delta, 4)
            if fd.severity_delta is not None
            else None,
        }

    @staticmethod
    def _file_delta_to_dict(fd: FileDelta) -> dict:
        return {
            "filepath": fd.filepath,
            "status": fd.status,
            "metric_deltas": {
                k: {
                    "old": round(v.old_value, 4),
                    "new": round(v.new_value, 4),
                    "delta": round(v.delta, 4),
                    "direction": v.direction,
                }
                for k, v in fd.metric_deltas.items()
            },
        }

    @staticmethod
    def _metric_delta_to_dict(md: MetricDelta) -> dict:
        return {
            "old": round(md.old_value, 4),
            "new": round(md.new_value, 4),
            "delta": round(md.delta, 4),
            "direction": md.direction,
        }

    # ── Rich terminal output ─────────────────────────────────────────────

    def _render_rich(self, diff: SnapshotDiff, verbose: bool = False) -> None:
        con = self._console
        con.print()

        # ── Header ───────────────────────────────────────────────────
        old_label = _short_sha(diff.old_commit)
        new_label = _short_sha(diff.new_commit)
        con.print(
            f"[bold cyan]SHANNON INSIGHT DIFF[/bold cyan] "
            f"[dim]{old_label}[/dim] -> [bold]{new_label}[/bold]"
        )
        con.print(f"  [dim]{diff.old_timestamp} -> {diff.new_timestamp}[/dim]")

        if diff.renames:
            con.print(f"  [dim]{len(diff.renames)} file rename(s) detected[/dim]")

        con.print()

        # Compute summary counts
        has_finding_changes = (
            diff.new_findings
            or diff.resolved_findings
            or diff.worsened_findings
            or diff.improved_findings
        )

        # ── Summary line ─────────────────────────────────────────────
        parts = []
        if diff.new_findings:
            parts.append(f"[red]+{len(diff.new_findings)} new[/red]")
        if diff.resolved_findings:
            parts.append(f"[green]-{len(diff.resolved_findings)} resolved[/green]")
        if diff.worsened_findings:
            parts.append(f"[red]{len(diff.worsened_findings)} worsened[/red]")
        if diff.improved_findings:
            parts.append(f"[green]{len(diff.improved_findings)} improved[/green]")

        changed_files = [fd for fd in diff.file_deltas if fd.status == "changed"]
        new_files = [fd for fd in diff.file_deltas if fd.status == "new"]
        removed_files = [fd for fd in diff.file_deltas if fd.status == "removed"]

        file_parts = []
        if changed_files:
            file_parts.append(f"{len(changed_files)} changed")
        if new_files:
            file_parts.append(f"{len(new_files)} new")
        if removed_files:
            file_parts.append(f"{len(removed_files)} removed")

        if parts:
            con.print(f"  Findings: {', '.join(parts)}")
        else:
            con.print("  [dim]No finding-level changes.[/dim]")

        if file_parts:
            con.print(f"  Files: {', '.join(file_parts)}")

        con.print()

        # ── NEW FINDINGS ─────────────────────────────────────────────
        if diff.new_findings:
            con.print(f"[bold red]NEW FINDINGS[/bold red] [dim]({len(diff.new_findings)})[/dim]")
            for finding in diff.new_findings:
                self._render_finding(finding, prefix="  [red]+[/red] ")
            con.print()

        # ── RESOLVED FINDINGS ────────────────────────────────────────
        if diff.resolved_findings:
            con.print(
                f"[bold green]RESOLVED[/bold green] [dim]({len(diff.resolved_findings)})[/dim]"
            )
            for finding in diff.resolved_findings:
                self._render_finding(finding, prefix="  [green]-[/green] ")
            con.print()

        # ── WORSENED FINDINGS ────────────────────────────────────────
        if diff.worsened_findings:
            con.print(f"[bold red]WORSENED[/bold red] [dim]({len(diff.worsened_findings)})[/dim]")
            for fd in diff.worsened_findings:
                self._render_finding_delta(fd, color="red")
            con.print()

        # ── IMPROVED FINDINGS ────────────────────────────────────────
        if diff.improved_findings:
            con.print(
                f"[bold green]IMPROVED[/bold green] [dim]({len(diff.improved_findings)})[/dim]"
            )
            for fd in diff.improved_findings:
                self._render_finding_delta(fd, color="green")
            con.print()

        # ── METRIC CHANGES (per-file) ────────────────────────────────
        if diff.file_deltas and (verbose or not has_finding_changes):
            self._render_file_deltas(diff.file_deltas, verbose=verbose)

        # ── CODEBASE-LEVEL DELTAS ────────────────────────────────────
        non_neutral = {k: v for k, v in diff.codebase_deltas.items() if v.direction != "neutral"}
        if non_neutral:
            con.print("[bold]CODEBASE SIGNALS[/bold]")
            for metric, md in sorted(non_neutral.items()):
                icon = _direction_icon(md.direction)
                con.print(
                    f"  {icon} {metric}: "
                    f"{md.old_value:.4f} -> {md.new_value:.4f} "
                    f"[dim]({_delta_str(md.delta)})[/dim]"
                )
            con.print()

        # ── Footer ───────────────────────────────────────────────────
        if not has_finding_changes and not diff.file_deltas:
            con.print("[bold green]No significant changes detected.[/bold green]")
            con.print()

    def _render_finding(self, finding: FindingRecord, prefix: str = "  ") -> None:
        """Render a single finding in compact form."""
        con = self._console
        label = _TYPE_LABELS.get(finding.finding_type, finding.finding_type.upper())
        color = _TYPE_COLORS.get(finding.finding_type, "white")

        files_str = ", ".join(finding.files[:3])
        if len(finding.files) > 3:
            files_str += f" +{len(finding.files) - 3} more"

        con.print(
            f"{prefix}[bold {color}]{label}[/bold {color}] "
            f"[dim]sev={finding.severity:.2f}[/dim]  "
            f"[bold]{files_str}[/bold]"
        )

    def _render_finding_delta(self, fd: FindingDelta, color: str = "white") -> None:
        """Render a finding with severity change information."""
        con = self._console
        finding = fd.finding
        label = _TYPE_LABELS.get(finding.finding_type, finding.finding_type.upper())
        fcolor = _TYPE_COLORS.get(finding.finding_type, "white")

        files_str = ", ".join(finding.files[:3])
        if len(finding.files) > 3:
            files_str += f" +{len(finding.files) - 3} more"

        sev_old = fd.old_severity if fd.old_severity is not None else 0.0
        sev_new = fd.new_severity if fd.new_severity is not None else 0.0
        sev_delta = fd.severity_delta if fd.severity_delta is not None else 0.0

        con.print(
            f"  [{color}]{'!' if color == 'red' else '-'}[/{color}] "
            f"[bold {fcolor}]{label}[/bold {fcolor}] "
            f"[bold]{files_str}[/bold]"
        )
        con.print(
            f"    severity: {sev_old:.3f} -> {sev_new:.3f} "
            f"[{color}]({_delta_str(sev_delta)})[/{color}]"
        )

    def _render_file_deltas(self, file_deltas: list, verbose: bool = False) -> None:
        """Render per-file metric changes as a Rich table."""
        con = self._console

        # Cap display: show only files with "worse" metrics or top N changed
        if not verbose:
            # In non-verbose mode, show only files with at least one "worse" metric
            # or files that are new/removed, limited to 15 entries
            interesting = [
                fd
                for fd in file_deltas
                if fd.status in ("new", "removed")
                or any(md.direction == "worse" for md in fd.metric_deltas.values())
            ]
            if not interesting:
                interesting = file_deltas[:10]
            display = interesting[:15]
        else:
            display = file_deltas[:50]

        if not display:
            return

        con.print(
            f"[bold]METRIC CHANGES[/bold] [dim]({len(display)} of {len(file_deltas)} files)[/dim]"
        )

        table = Table(expand=True, show_lines=False, pad_edge=False)
        table.add_column("File", style="bold", no_wrap=False, ratio=3)
        table.add_column("Status", width=9)
        table.add_column("Metric", ratio=2)
        table.add_column("Old", justify="right", width=9)
        table.add_column("New", justify="right", width=9)
        table.add_column("Delta", justify="right", width=10)
        table.add_column("", width=3)  # direction icon

        for fd in display:
            status_style = {
                "new": "[green]new[/green]",
                "removed": "[red]removed[/red]",
                "changed": "[yellow]changed[/yellow]",
                "unchanged": "[dim]unchanged[/dim]",
            }.get(fd.status, fd.status)

            # Show up to 5 most important metric deltas per file
            sorted_metrics = sorted(
                fd.metric_deltas.items(),
                key=lambda kv: abs(kv[1].delta),
                reverse=True,
            )

            if not verbose:
                sorted_metrics = sorted_metrics[:5]

            for i, (metric_name, md) in enumerate(sorted_metrics):
                icon = _direction_icon(md.direction)
                delta_color = (
                    "red"
                    if md.direction == "worse"
                    else "green"
                    if md.direction == "better"
                    else "dim"
                )

                table.add_row(
                    fd.filepath if i == 0 else "",
                    status_style if i == 0 else "",
                    metric_name,
                    f"{md.old_value:.4f}",
                    f"{md.new_value:.4f}",
                    f"[{delta_color}]{_delta_str(md.delta)}[/{delta_color}]",
                    icon,
                )

        con.print(table)
        con.print()
