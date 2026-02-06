"""ChronicProblemFinder -- detects findings that persist across multiple consecutive snapshots.

Unlike the other finders which operate purely on the current AnalysisStore,
this finder queries the history database to identify findings that have
appeared in N+ consecutive analysis runs without being addressed.  These
"chronic" problems are often more important than new findings because they
represent accumulated tech debt that teams have been ignoring.
"""

import sqlite3
from typing import List, Optional

from ..models import Evidence, Finding


class ChronicProblemFinder:
    """Detect findings that have persisted across N+ consecutive snapshots.

    This finder requires an open ``sqlite3.Connection`` to the history
    database.  If no connection is provided it silently returns an empty
    list, making it safe to include in the default finder pipeline.

    Parameters
    ----------
    history_conn:
        An open ``sqlite3.Connection`` (with ``row_factory = sqlite3.Row``)
        pointing at the ``.shannon/history.db`` database.  ``None`` disables
        the finder.
    min_persistence:
        Minimum number of **consecutive** snapshots a finding must appear
        in before it is flagged.  Defaults to ``3``.
    """

    name = "chronic_problem"
    requires = {"files"}
    BASE_SEVERITY = 0.75

    def __init__(
        self,
        history_conn: Optional[sqlite3.Connection] = None,
        min_persistence: int = 3,
    ):
        self.history_conn = history_conn
        self.min_persistence = min_persistence

    def find(self, store) -> List[Finding]:
        """Run the finder against the current store + history.

        Parameters
        ----------
        store:
            The ``AnalysisStore`` for the current run.  Not directly used
            by this finder (the history DB is the primary data source),
            but accepted to match the standard finder protocol.

        Returns
        -------
        List[Finding]
            One finding per chronically-persistent issue.
        """
        if not self.history_conn:
            return []

        from ...persistence.queries import HistoryQuery

        query = HistoryQuery(self.history_conn)
        chronic = query.persistent_findings(min_snapshots=self.min_persistence)

        findings: List[Finding] = []
        for item in chronic:
            # Severity scales with persistence, capped at BASE_SEVERITY.
            severity = self.BASE_SEVERITY * min(1.0, item["count"] / 10)

            findings.append(
                Finding(
                    finding_type="chronic_problem",
                    severity=severity,
                    title=(f"{item['title']} (unresolved for {item['count']} runs)"),
                    files=item["files"],
                    evidence=[
                        Evidence(
                            signal="persistence",
                            value=float(item["count"]),
                            percentile=0.0,
                            description=(
                                f"This finding has appeared in {item['count']} "
                                f"consecutive analysis runs without being addressed"
                            ),
                        ),
                    ],
                    suggestion=(
                        f"This has been flagged {item['count']} times. "
                        f"Consider prioritizing a fix or explicitly "
                        f"suppressing it."
                    ),
                )
            )
        return findings
