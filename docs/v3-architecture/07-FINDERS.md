# Level 6: Finders (Pattern Detection)

## Overview

28 finders match patterns against signals to emit findings.

## Categories

| Category | Count | Key Signals |
|----------|-------|-------------|
| Structural | 7 | pagerank, cognitive_load, cycles |
| AI Quality | 8 | orphan, stubs, phantom_imports |
| Architecture | 5 | instability, abstractness, violations |
| Team | 3 | bus_factor, fix_ratio |
| Temporal | 3 | churn_trajectory, fix_ratio |
| Cross-Dimensional | 3 | risk_score, concepts |

## Key Finders

| Finder | Condition | Severity |
|--------|-----------|----------|
| HIGH_RISK_HUB | pctl(pagerank) > 0.90 AND pctl(blast) > 0.90 | CRITICAL |
| GOD_FILE | pctl(cognitive_load) > 0.90 AND coherence < 0.20 | HIGH |
| HIDDEN_COUPLING | lift > 2.0 AND NOT imports | MEDIUM |
| ZONE_OF_PAIN | instability < 0.3 AND abstractness < 0.3 | HIGH |
| TRUCK_FACTOR | bus_factor ≤ 1.0 AND central | CRITICAL |
| BUG_MAGNET | fix_ratio > 0.4 AND changes ≥ 5 | HIGH |

## Finding Model

```python
@dataclass
class Finding:
    finder_id: str
    severity: float           # [0, 1]
    scope: Literal["FILE", "MODULE", "CODEBASE"]
    entity_id: str
    title: str
    description: str
    evidence: dict[str, Any]
    confidence: float         # [0, 1]
```

## Hotspot Filter

FILE-scope findings require `total_changes > median` UNLESS structural-only (orphan, phantom, clone).

## Tier Behavior

| Tier | Patterns Available |
|------|-------------------|
| ABSOLUTE | Structural only (no percentiles) |
| BAYESIAN | All patterns |
| FULL | All patterns with normal thresholds |

## Current Implementation

**Files:**
- `src/shannon_insight/insights/finders/executor.py`
- `src/shannon_insight/insights/finders/patterns/` (6 files)

**Status:** 28 patterns implemented, all production-ready.
