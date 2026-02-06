"""UnstableFileFinder — never-stabilizing churn."""

from ..models import Evidence, Finding
from ..ranking import compute_percentiles
from ..store import AnalysisStore

_MIN_FILES = 5


class UnstableFileFinder:
    name = "unstable_file"
    requires: set[str] = {"temporal"}
    BASE_SEVERITY = 0.7

    def find(self, store: AnalysisStore) -> list[Finding]:
        if not store.churn:
            return []
        if len(store.churn) < _MIN_FILES:
            return []

        # Find the median total_changes
        all_changes = sorted(cs.total_changes for cs in store.churn.values())
        n = len(all_changes)
        median_changes = all_changes[n // 2] if n > 0 else 0

        # Compute churn percentiles for severity
        churn_vals = {p: float(cs.total_changes) for p, cs in store.churn.items()}
        churn_pct = compute_percentiles(churn_vals)

        # Get span for context
        span_weeks = 0
        if store.git_history:
            span_weeks = max(1, store.git_history.span_days // 7)

        findings = []
        for path, cs in store.churn.items():
            if cs.trajectory not in ("churning", "spiking"):
                continue
            if cs.total_changes <= median_changes:
                continue

            pct = churn_pct.get(path, 0)
            strength = max(0.1, min(1.0, pct / 100))
            severity = self.BASE_SEVERITY * strength

            # Build time-aware description
            if span_weeks > 0:
                rate_desc = f"changed {cs.total_changes} times over {span_weeks} weeks"
            else:
                rate_desc = f"changed {cs.total_changes} times"

            if cs.trajectory == "spiking":
                trend_desc = (
                    "the change rate is increasing — more edits in recent weeks than earlier"
                )
                suggestion = (
                    "This file is being edited more and more frequently. "
                    "This often signals unclear requirements, "
                    "a leaky abstraction that needs constant patching, "
                    "or missing test coverage that lets bugs through. "
                    "Investigate why it keeps needing changes."
                )
            else:
                trend_desc = "the change rate is volatile — no sign of settling down"
                suggestion = (
                    "This file has been modified repeatedly without "
                    "stabilizing. Common causes: unclear ownership, "
                    "too many responsibilities (consider splitting), "
                    "or insufficient tests causing bug-fix churn. "
                    "Review recent commits to find the pattern."
                )

            findings.append(
                Finding(
                    finding_type="unstable_file",
                    severity=severity,
                    title=f"{path} keeps changing without stabilizing",
                    files=[path],
                    evidence=[
                        Evidence(
                            signal="total_changes",
                            value=float(cs.total_changes),
                            percentile=pct,
                            description=rate_desc,
                        ),
                        Evidence(
                            signal="churn_trajectory",
                            value=cs.slope,
                            percentile=0,
                            description=trend_desc,
                        ),
                    ],
                    suggestion=suggestion,
                )
            )

        return findings
