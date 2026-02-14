# Architecture Redesign Plan

## Current Problem

**Data flows inconsistently from DB → API → Frontend with no transformation layer.**

Result:
- Health scores on different scales (0.6, 6.0, 7.0)
- Missing evolution data (files over time, LOC growth, etc.)
- No analysis metadata (performance, what was analyzed)
- Frontend guesses what each value means

## The Fix (4 Layers)

```
┌──────────────────────────────────────────────────────┐
│ LAYER 1: Storage (SQLite .shannon/history.db)       │
│ ────────────────────────────────────────────────────│
│ Tables:                                              │
│ - snapshots: metadata (timestamp, file_count, etc.) │
│ - signal_history: per-file signals per snapshot     │
│ - module_signal_history: per-module signals         │
│ - global_signal_history: codebase-level signals     │
│                                                      │
│ Data stored in NATIVE format (0-1 scale)            │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ LAYER 2: Domain Models                               │
│ ────────────────────────────────────────────────────│
│ - TensorSnapshot (loads from DB)                    │
│ - FileSignals, ModuleSignals                         │
│ - Pure business logic, no display concerns          │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ LAYER 3: API Serialization (NEW!)                   │
│ ────────────────────────────────────────────────────│
│ File: src/shannon_insight/server/serializers.py     │
│                                                      │
│ class DashboardSerializer:                           │
│   - serialize_snapshot() → DashboardState           │
│   - serialize_health() → HealthData                  │
│   - serialize_evolution() → EvolutionData            │
│   - serialize_files() → Dict[str, FileData]         │
│   - serialize_modules() → Dict[str, ModuleData]     │
│                                                      │
│ CONSISTENT TRANSFORMATION RULES:                     │
│ - Health: ALWAYS 1-10 scale                         │
│ - Risk: ALWAYS 0-1 scale (percentile/100)           │
│ - Percentiles: ALWAYS 0-100                         │
│ - All trends transformed consistently                │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│ LAYER 4: Frontend (React Components)                │
│ ────────────────────────────────────────────────────│
│ - Knows EXACTLY what to expect (TypeScript types)   │
│ - Reusable components for evolution charts          │
│ - No scale guessing                                  │
└──────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Create Serialization Layer (TODAY)

**File: `src/shannon_insight/server/serializers.py`**

```python
"""API serialization layer - transforms domain models to frontend contract."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from ..persistence.models import TensorSnapshot
from ..persistence.database import HistoryDB
from ..persistence.queries import HistoryQuery


@dataclass
class EvolutionMetrics:
    """Codebase evolution over time."""
    file_count_trend: List[tuple[str, int]]      # [(timestamp, count), ...]
    module_count_trend: List[tuple[str, int]]
    total_loc_trend: List[tuple[str, int]]
    avg_complexity_trend: List[tuple[str, float]]
    unique_authors_trend: List[tuple[str, int]]
    commits_per_snapshot: List[tuple[str, int]]


@dataclass
class AnalysisMetadata:
    """What was analyzed and how."""
    files_scanned: int
    files_analyzed: int
    modules_detected: int
    commits_processed: int
    analyzers_ran: List[str]
    analysis_duration_ms: Optional[float]
    snapshot_count: int
    db_size_mb: float


class DashboardSerializer:
    """Transforms domain models to API contract with consistent scales."""

    def __init__(self, db: HistoryDB):
        self.db = db
        self.query = HistoryQuery(db.conn)

    def serialize_health(self, snapshot: TensorSnapshot) -> dict:
        """Health data with CONSISTENT 1-10 scale everywhere."""
        raw_health = snapshot.global_signals.get("codebase_health", 0.5)
        display_health = raw_health * 10  # ALWAYS multiply

        # Get trend (also multiply by 10)
        health_points = self.query.codebase_health(last_n=20)
        trend = []
        for hp in health_points:
            raw = hp.metrics.get("codebase_health", 0.5)
            trend.append({
                "timestamp": hp.timestamp,
                "score": round(raw * 10, 1),  # ALWAYS 1-10 scale
                "finding_count": int(hp.metrics.get("active_findings", 0)),
            })

        return {
            "score": round(display_health, 1),
            "label": self._health_label(display_health),
            "verdict": self._compute_verdict(snapshot),
            "trend": trend,
        }

    def serialize_evolution(self) -> dict:
        """Compute codebase evolution metrics from history."""
        cur = self.db.conn.cursor()

        # File count over time
        rows = cur.execute("""
            SELECT timestamp, file_count
            FROM snapshots
            ORDER BY timestamp ASC
        """).fetchall()
        file_count_trend = [(r["timestamp"], r["file_count"]) for r in rows]

        # Module count over time
        rows = cur.execute("""
            SELECT timestamp, module_count
            FROM snapshots
            ORDER BY timestamp ASC
        """).fetchall()
        module_count_trend = [(r["timestamp"], r["module_count"]) for r in rows]

        # Total LOC over time (sum of all files' lines per snapshot)
        rows = cur.execute("""
            SELECT s.timestamp, SUM(sh.value) as total_loc
            FROM snapshots s
            JOIN signal_history sh ON s.id = sh.snapshot_id
            WHERE sh.signal_name = 'lines'
            GROUP BY s.id
            ORDER BY s.timestamp ASC
        """).fetchall()
        total_loc_trend = [(r["timestamp"], int(r["total_loc"])) for r in rows]

        # Average complexity over time
        rows = cur.execute("""
            SELECT s.timestamp, AVG(sh.value) as avg_complexity
            FROM snapshots s
            JOIN signal_history sh ON s.id = sh.snapshot_id
            WHERE sh.signal_name = 'cognitive_load'
            GROUP BY s.id
            ORDER BY s.timestamp ASC
        """).fetchall()
        avg_complexity_trend = [(r["timestamp"], round(r["avg_complexity"], 1)) for r in rows]

        # Commits analyzed per snapshot
        rows = cur.execute("""
            SELECT timestamp, commits_analyzed
            FROM snapshots
            ORDER BY timestamp ASC
        """).fetchall()
        commits_trend = [(r["timestamp"], r["commits_analyzed"]) for r in rows]

        return {
            "file_count": file_count_trend,
            "module_count": module_count_trend,
            "total_loc": total_loc_trend,
            "avg_complexity": avg_complexity_trend,
            "commits_analyzed": commits_trend,
        }

    def serialize_metadata(self, snapshot: TensorSnapshot) -> dict:
        """Analysis metadata - what was analyzed."""
        cur = self.db.conn.cursor()

        # Count snapshots
        snapshot_count = cur.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]

        # DB size
        import os
        db_size_bytes = os.path.getsize(self.db.db_path)
        db_size_mb = db_size_bytes / (1024 * 1024)

        return {
            "files_scanned": snapshot.file_count,
            "files_analyzed": snapshot.file_count,  # Could add filtered count
            "modules_detected": snapshot.module_count,
            "commits_processed": snapshot.commits_analyzed,
            "analyzers_ran": snapshot.analyzers_ran,
            "snapshot_count": snapshot_count,
            "db_size_mb": round(db_size_mb, 2),
        }

    def serialize_top_movers(self) -> list:
        """Files with biggest risk changes - COMPARE TO BASELINE."""
        cur = self.db.conn.cursor()

        # Get baseline snapshot (first one)
        baseline_id = cur.execute(
            "SELECT id FROM snapshots ORDER BY timestamp ASC LIMIT 1"
        ).fetchone()["id"]

        # Get latest snapshot
        latest_id = cur.execute(
            "SELECT id FROM snapshots ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()["id"]

        # Compare risk_score between baseline and latest
        rows = cur.execute("""
            SELECT
                latest.file_path,
                baseline.value as old_value,
                latest.value as new_value,
                latest.value - baseline.value as delta
            FROM signal_history latest
            JOIN signal_history baseline
                ON latest.file_path = baseline.file_path
                AND baseline.snapshot_id = ?
            WHERE latest.snapshot_id = ?
                AND latest.signal_name = 'risk_score'
                AND baseline.signal_name = 'risk_score'
            ORDER BY ABS(latest.value - baseline.value) DESC
            LIMIT 10
        """, (baseline_id, latest_id)).fetchall()

        return [
            {
                "path": r["file_path"],
                "old_value": round(r["old_value"], 3),
                "new_value": round(r["new_value"], 3),
                "delta": round(r["delta"], 3),
            }
            for r in rows
        ]

    def _health_label(self, score: float) -> str:
        if score >= 8: return "Healthy"
        if score >= 6: return "Moderate"
        if score >= 4: return "At Risk"
        return "Critical"

    def _compute_verdict(self, snapshot: TensorSnapshot) -> str:
        # ... existing logic
        pass
```

### Phase 2: Replace api.py with Serializer

**File: `src/shannon_insight/server/api.py`** (SIMPLIFIED)

```python
def build_dashboard_state(
    result: InsightResult,
    snapshot: TensorSnapshot,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Convert analysis results to dashboard JSON - NOW WITH SERIALIZER."""

    # Use serializer for consistent transformation
    with HistoryDB(Path(db_path).parent.parent if db_path else ".") as db:
        serializer = DashboardSerializer(db)

        return {
            "version": __version__,
            "metadata": serializer.serialize_metadata(snapshot),
            "health": serializer.serialize_health(snapshot),
            "evolution": serializer.serialize_evolution(),
            "top_movers": serializer.serialize_top_movers(),
            # ... rest of the fields (files, modules, findings)
        }
```

### Phase 3: Update Frontend to Use Evolution Data

**File: `src/shannon_insight/server/frontend/src/components/screens/OverviewScreen.jsx`**

Add evolution charts:

```jsx
// NEW: Evolution section
{data.evolution && (
  <div class="overview-evolution">
    <h3>Codebase Evolution</h3>
    <div class="evolution-charts">
      <EvolutionChart
        title="Files Over Time"
        data={data.evolution.file_count}
        color="var(--blue)"
      />
      <EvolutionChart
        title="Total Lines of Code"
        data={data.evolution.total_loc}
        color="var(--green)"
      />
      <EvolutionChart
        title="Average Complexity"
        data={data.evolution.avg_complexity}
        color="var(--orange)"
      />
    </div>
  </div>
)}

// NEW: Metadata section
{data.metadata && (
  <div class="overview-metadata">
    <MetadataStat label="Files Scanned" value={data.metadata.files_scanned} />
    <MetadataStat label="Commits Processed" value={data.metadata.commits_processed} />
    <MetadataStat label="Snapshots" value={data.metadata.snapshot_count} />
    <MetadataStat label="DB Size" value={`${data.metadata.db_size_mb} MB`} />
  </div>
)}
```

## Commit to Timeline

- **Today (2 hours):** Implement `serializers.py`
- **Today (1 hour):** Update `api.py` to use serializer
- **Today (1 hour):** Add evolution charts to Overview
- **Today (30 min):** Test end-to-end

**Total: 4.5 hours to fix architecture properly.**

## Success Criteria

✅ Health score is ALWAYS 1-10 everywhere
✅ Top movers shows real deltas (baseline comparison)
✅ Overview shows file/LOC/complexity growth over time
✅ Metadata shows what was analyzed
✅ All transformations in ONE place (serializers.py)
✅ Frontend has reusable components

---

**I commit to implementing this properly. No more hacks.**
