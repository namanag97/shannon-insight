"""PatternsExecutor — Detect code issues using pattern-based finders.

This phase runs pattern-based finders against the FactStore:
- FILE scope patterns (god_file, high_risk_hub, etc.)
- FILE_PAIR scope patterns (hidden_coupling, clone_pair, etc.)
- MODULE scope patterns (zone_of_pain, module_instability, etc.)
- CODEBASE scope patterns (flat_architecture, low_modularity, etc.)

Produces:
- List of findings stored in ctx._findings for reporting phase
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...infrastructure.runtime import Phase
from ...logging_config import get_logger
from ..executor import BaseExecutor
from ..result import PhaseResult

if TYPE_CHECKING:
    from ...infrastructure.runtime import RuntimeContext
    from ...insights.store import AnalysisStore
    from ...session import AnalysisSession

logger = get_logger(__name__)


class PatternsExecutor(BaseExecutor):
    """Detect code issues using pattern-based finders.

    Executes ALL_PATTERNS against FactStore, applying:
    - Requirements checking (skip if signals unavailable)
    - Tier filtering (some patterns require percentiles)
    - Hotspot filtering (temporal patterns on hot files only)
    """

    phase = Phase.PATTERNS
    timeout_seconds = 120  # 2 minutes
    name = "patterns"

    def _execute(
        self,
        ctx: RuntimeContext,
        store: AnalysisStore,
        session: AnalysisSession,
    ) -> PhaseResult:
        """Execute patterns to detect code issues."""
        from ...insights.finders.executor import execute_patterns
        from ...insights.finders.registry import ALL_PATTERNS

        if store.file_count == 0:
            logger.warning("No files in store, skipping pattern detection")
            ctx._findings = []  # type: ignore
            return PhaseResult.ok(items_processed=0)

        tier = session.tier
        logger.debug(f"Running patterns in tier: {tier.value}")

        # Execute patterns
        pattern_findings = execute_patterns(
            store=store.fact_store,
            patterns=ALL_PATTERNS,
            tier=tier,
            max_findings=session.config.max_findings * 2,  # Request extra for post-filtering
        )

        # Convert to output format
        from ...insights.models import Evidence
        from ...insights.models import Finding as OutputFinding

        findings = []
        for pf in pattern_findings:
            # Extract file paths from target
            if isinstance(pf.target, tuple):
                files = [pf.target[0].key, pf.target[1].key]
            else:
                files = [pf.target.key]

            # Convert evidence dict to Evidence objects
            evidence = []
            for k, v in pf.evidence.items():
                try:
                    numeric_value = float(v) if not isinstance(v, str) else 0.0
                except (ValueError, TypeError):
                    numeric_value = 0.0

                if isinstance(v, bool):
                    description = f"{k}={v}"
                elif isinstance(v, (int, float)):
                    description = f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}"
                else:
                    description = str(v) if len(str(v)) > 5 else f"{k}={v}"

                evidence.append(
                    Evidence(signal=k, value=numeric_value, percentile=0.0, description=description)
                )

            finding = OutputFinding(
                finding_type=pf.pattern,
                severity=pf.severity,
                title=pf.description,
                files=files,
                evidence=evidence,
                suggestion=pf.remediation,
                confidence=pf.confidence,
            )
            findings.append(finding)

        # Store findings for reporting phase
        ctx._findings = findings  # type: ignore
        ctx._pattern_findings = pattern_findings  # type: ignore

        logger.info(f"Pattern detection complete: {len(findings)} findings")
        return PhaseResult.ok(items_processed=len(findings))
