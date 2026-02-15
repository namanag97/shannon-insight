# Temporal UX Strategy: Long-Term Solution

**Problem Statement:** Shannon Insight is a **temporal analysis tool** (tracking code health over time), but the frontend treats temporal data as an afterthought. Users can't navigate time, compare snapshots, or understand temporal context.

---

## Current State Audit (Problems Identified)

### ❌ **Critical Issues**

1. **No Temporal Context Awareness**
   - User doesn't know WHICH snapshot they're viewing
   - No "current timestamp" indicator
   - No way to know if data is from today, yesterday, or last week

2. **No Temporal Navigation**
   - Can't go "back in time" to view previous snapshots
   - Can't compare "now vs 1 week ago"
   - Health screen shows trends, but can't click on a point to "jump to that snapshot"

3. **Inconsistent Temporal Data**
   - Evolution charts on Overview (de-prioritized, hidden in collapsible)
   - Health trends on Health screen (prominent, but can't drill down)
   - Top movers computed but not contextualized (vs when?)
   - Chronic findings shown but no timeline (when did they first appear?)

4. **No Temporal Filtering**
   - Can't filter findings by "introduced in last week"
   - Can't filter files by "changed since last snapshot"
   - Can't see "new issues vs old issues"

5. **Missing Temporal Features**
   - No snapshot comparison (diff between two points in time)
   - No temporal heatmap (which files churn most over time)
   - No temporal annotations (mark events: "deployed v2.0", "refactor started")
   - No forecasting/projections ("at this rate, health will hit 5.0 in 2 weeks")

---

## Data Available (Backend Provides)

```python
# From serializers.py:
data = {
    "health": {
        "score": 7.2,  # Current snapshot
        "trend": [      # Last 20 snapshots
            {"timestamp": "2026-02-10", "score": 7.1, "finding_count": 50},
            {"timestamp": "2026-02-11", "score": 7.0, "finding_count": 52},
            # ...
        ]
    },
    "evolution": {
        "file_count": [{"timestamp": "...", "value": 247}, ...],
        "total_loc": [...],
        "avg_complexity": [...],
        "avg_risk": [...],
    },
    "movers": {  # Files with biggest changes (baseline vs latest)
        "improved": [{"path": "...", "old_value": 0.3, "new_value": 0.7, "delta": +0.4}, ...],
        "degraded": [...]
    },
    "chronic": [  # Findings that never get resolved
        {"type": "God File", "snapshot_count": 5, "occurrences": 5},
        ...
    ],
    "metadata": {
        "snapshot_count": 81,  # Total snapshots in history
        "db_size_mb": 15.3,
    }
}
```

**What's missing from backend:**
- API to fetch a SPECIFIC snapshot by ID or timestamp
- API to compare TWO snapshots (diff)
- API to list all snapshots with metadata (for timeline picker)
- Temporal aggregations (week-over-week changes, monthly averages)

---

## Long-Term Solution: Temporal-First UX

### **Phase 1: Temporal Context (Foundation)**

#### 1.1 Add Temporal Context to Global State

```js
// store.js - NEW temporal state
const useStore = create((set, get) => ({
  // ... existing state ...

  // ── Temporal Context ───────────────────────────────────────
  currentSnapshotId: null,        // null = "latest", or specific snapshot ID
  currentSnapshotTimestamp: null, // Timestamp of current snapshot
  snapshotList: [],               // List of all snapshots (for timeline)
  temporalMode: "live",           // "live" | "historical" | "comparison"
  comparisonSnapshotId: null,     // For comparison mode

  // Temporal actions
  setSnapshot: (snapshotId, timestamp) =>
    set({ currentSnapshotId: snapshotId, currentSnapshotTimestamp: timestamp }),

  setTemporalMode: (mode) => set({ temporalMode: mode }),

  setComparison: (baseId, compareId) =>
    set({
      temporalMode: "comparison",
      currentSnapshotId: baseId,
      comparisonSnapshotId: compareId
    }),

  goToLatest: () => set({
    currentSnapshotId: null,
    temporalMode: "live",
    comparisonSnapshotId: null
  }),
}));
```

#### 1.2 Add Temporal Context Bar (Global UI Component)

```
┌─────────────────────────────────────────────────────────┐
│ Shannon Insight | Overview | Issues | Files | ...      │  ← Existing topbar
├─────────────────────────────────────────────────────────┤
│ 📅 Viewing: Feb 15, 2026 10:30 AM (LIVE) [Timeline ▼]  │  ← NEW temporal bar
│    81 snapshots in history | Compared to: <none>       │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- **Live indicator:** Shows if viewing latest snapshot (green dot) or historical (amber dot)
- **Timestamp:** Always visible - user knows WHEN this data is from
- **Timeline dropdown:** Quick access to recent snapshots
  - "Latest (now)"
  - "1 hour ago"
  - "Yesterday"
  - "1 week ago"
  - "1 month ago"
  - "Show all snapshots..." → Opens timeline modal
- **Comparison mode toggle:** Button to enter comparison mode

#### 1.3 Timeline Modal (Snapshot Picker)

```
┌──────────────────── Snapshot Timeline ─────────────────┐
│                                                         │
│  [━━━━━━━━●━━━━━━●━━━●━━━━━━●━━━━━━━●━━━━━━━━━━━━━━━━] │
│  Jan 1   Jan 15  Feb 1  Feb 8   Feb 15   Feb 22  Mar 1│
│                                    ↑ You are here       │
│                                                         │
│  Recent Snapshots:                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ✓ Feb 15, 2026 10:30 AM  •  Health: 7.2  •  ... │   │
│  │   Feb 14, 2026 18:45 PM  •  Health: 7.1  •  ... │   │
│  │   Feb 13, 2026 09:12 AM  •  Health: 7.3  •  ... │   │
│  │   ...                                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Cancel]  [Select Snapshot]  [Enter Comparison Mode]  │
└─────────────────────────────────────────────────────────┘
```

**Interaction:**
- Click snapshot → view that snapshot (historical mode)
- Shift+Click two snapshots → enter comparison mode
- Timeline scrubber → drag to explore history visually

---

### **Phase 2: Temporal Navigation & Comparison**

#### 2.1 Backend API Extensions

**New endpoints needed:**

```python
# GET /api/snapshots
# Returns list of all snapshots with metadata
{
  "snapshots": [
    {
      "id": 123,
      "timestamp": "2026-02-15T10:30:00Z",
      "health": 7.2,
      "file_count": 247,
      "finding_count": 78,
      "git_commit": "abc123",  # If available
      "notes": "Deployed v2.0"  # User annotations
    },
    ...
  ]
}

# GET /api/snapshot/:id
# Returns full snapshot data (same structure as /api/state, but for specific snapshot)

# GET /api/compare?base=:id1&target=:id2
# Returns diff between two snapshots
{
  "base": { "timestamp": "...", "health": 7.1 },
  "target": { "timestamp": "...", "health": 7.2 },
  "changes": {
    "health_delta": +0.1,
    "files_added": ["new_file.py"],
    "files_removed": ["old_file.py"],
    "files_changed": [
      {
        "path": "auth.py",
        "old_risk": 0.3,
        "new_risk": 0.7,
        "delta": +0.4,
        "findings_added": ["God File"],
        "findings_resolved": []
      }
    ],
    "new_findings": [...],
    "resolved_findings": [...],
  }
}

# POST /api/snapshot/:id/annotate
# Add user annotation to a snapshot
{
  "note": "Deployed v2.0 - expect churn spike"
}
```

#### 2.2 Historical View Mode

When user selects a historical snapshot:

1. **Temporal bar changes:**
   ```
   📅 Viewing: Feb 10, 2026 3:45 PM (HISTORICAL) [Back to Live]
      5 days ago | 3 snapshots behind latest
   ```

2. **All data updates:**
   - Fetch `/api/snapshot/:id`
   - Replace `data` in store with historical data
   - All screens show historical state

3. **Visual indicators:**
   - Amber banner: "You are viewing historical data from 5 days ago"
   - All charts show "point in time" indicator
   - Disable real-time WebSocket updates (don't mix live + historical)

#### 2.3 Comparison View Mode

When user enters comparison mode:

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Comparing: Feb 10 (Base) vs Feb 15 (Target)          │
│    [← Prev Pair] [Swap] [Next Pair →] [Exit Comparison] │
└─────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────────┐
│ Feb 10, 2026         │ Feb 15, 2026                     │
│ Health: 7.1          │ Health: 7.2  (+0.1 ▲)           │
│ Files: 240           │ Files: 247   (+7)               │
│ Issues: 82           │ Issues: 78   (-4 ✓)             │
└──────────────────────┴──────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ CHANGES SUMMARY                                          │
│ ────────────────────────────────────────────────────────│
│ 🟢 Resolved Issues (4):                                  │
│    • Unstable File: database.py (stabilized)            │
│    • God File: utils.py (split into 3 files)            │
│                                                          │
│ 🔴 New Issues (1):                                       │
│    • High Risk Hub: auth_service.py                     │
│                                                          │
│ 📈 Top Movers (files with biggest changes):             │
│    ↑ auth_service.py: +0.4 risk (WORSE)                │
│    ↓ database.py: -0.3 risk (BETTER)                   │
└─────────────────────────────────────────────────────────┘
```

**Comparison features:**
- Side-by-side metrics
- Diff visualization (added/removed/changed)
- Attribution (which commits caused changes, if git data available)
- Export comparison report

---

### **Phase 3: Temporal Intelligence (Advanced)**

#### 3.1 Temporal Filtering

Add temporal filters to every screen:

```
┌─────────────────────────────────────────────────────────┐
│ Issues Screen                                            │
│ ────────────────────────────────────────────────────────│
│ [Sort ▼] [Severity ▼] [Time Range ▼]  ← NEW             │
│                       └─ All Time                        │
│                          Last Week                       │
│                          Last Month                      │
│                          Since Last Deploy               │
│                          Custom Range...                 │
└─────────────────────────────────────────────────────────┘
```

**Use cases:**
- Show only findings introduced in last week
- Show only files changed in last month
- Filter movers by time range

#### 3.2 Temporal Annotations

Allow users to mark events on the timeline:

```
Timeline:
[━━━●━━━━🏷━━━●━━━━━━🚀━━━●━━━━━━━━━━━━━]
     ↑       ↑        ↑
     Spike   Deploy   Latest
```

**Annotations:**
- Manual: "Refactor started", "Bug fix deployed"
- Automatic: Detect spikes/drops in metrics
- Git-based: Link to commits/tags if available

#### 3.3 Forecasting & Alerts

```
┌──────────────── Health Forecast ────────────────┐
│                                                  │
│  Current: 7.2                                    │
│  Trend: ↓ -0.05/day (last 7 days)               │
│                                                  │
│  Projection:                                     │
│  • In 7 days: 6.9 (Moderate)                    │
│  • In 30 days: 5.7 ⚠ (At Risk)                  │
│                                                  │
│  ⚠️ Alert: At current rate, health will drop    │
│     below 6.0 (Moderate threshold) in 24 days.  │
│                                                  │
│  Recommendation:                                 │
│  Focus on top movers: auth_service.py declining │
│  -0.1 risk/week.                                │
└──────────────────────────────────────────────────┘
```

**Features:**
- Linear regression on health trend
- Alert thresholds (configurable)
- Velocity tracking (rate of change per day/week)
- Intervention impact ("if you fix these 3 files, health could improve by +0.5")

#### 3.4 Temporal Heatmap

Visualize file churn/risk over time:

```
File Temporal Heatmap (Risk Over Time):

auth/service.py   [█▓░░░▓▓▓███] ← Getting worse
database.py       [███▓▓░░░░░░] ← Getting better
utils.py          [░░░░░░░░░░░] ← Stable (low)
models.py         [▓▓▓▓▓▓▓▓▓▓▓] ← Stable (medium)
                   └─────────┘
                   Jan   →  Feb

Legend:
█ High risk (>0.8)
▓ Medium risk (0.4-0.8)
░ Low risk (<0.4)
```

**Use cases:**
- Spot files that are consistently problematic
- Identify "risk oscillation" (flipping between high/low)
- Detect seasonal patterns (complexity spikes every Monday?)

---

## Implementation Plan (Phased Rollout)

### **Phase 1: Foundation (Week 1-2)**

**Goal:** Users always know WHEN they're viewing data.

- [ ] Add temporal state to store (currentSnapshotId, timestamp)
- [ ] Add temporal context bar (fixed UI component below topbar)
- [ ] Fetch snapshot list from backend (`/api/snapshots`)
- [ ] Show "LIVE" indicator when viewing latest
- [ ] Show timestamp for current snapshot

**Backend work:**
- [ ] Create `/api/snapshots` endpoint (list all)
- [ ] Add `current_snapshot_timestamp` to `/api/state` response

**Acceptance:**
- User can see "Viewing: Feb 15, 2026 10:30 AM (LIVE)" at all times
- Temporal bar is always visible

### **Phase 2: Historical Navigation (Week 3-4)**

**Goal:** Users can "go back in time" to view previous snapshots.

- [ ] Add timeline dropdown (quick access to recent)
- [ ] Create timeline modal (full snapshot picker)
- [ ] Implement snapshot switching (fetch `/api/snapshot/:id`)
- [ ] Add "Back to Live" button
- [ ] Add visual indicator for historical mode (amber banner)

**Backend work:**
- [ ] Create `/api/snapshot/:id` endpoint
- [ ] Optimize query performance (cache snapshots?)

**Acceptance:**
- User can click timeline → select "Feb 10, 2026" → view all data from that snapshot
- User can return to live mode

### **Phase 3: Comparison Mode (Week 5-6)**

**Goal:** Users can compare two snapshots side-by-side.

- [ ] Add comparison mode to temporal bar
- [ ] Create comparison view component
- [ ] Implement diff visualization (changes summary)
- [ ] Add "swap" and "next/prev pair" navigation

**Backend work:**
- [ ] Create `/api/compare?base=:id&target=:id` endpoint
- [ ] Compute diff logic (files added/removed/changed, findings delta)

**Acceptance:**
- User can select two snapshots → see side-by-side comparison
- Diff shows new/resolved findings, file changes, metric deltas

### **Phase 4: Temporal Filtering (Week 7)**

**Goal:** Users can filter data by time range.

- [ ] Add "Time Range" filter to Issues screen
- [ ] Add "Time Range" filter to Files screen
- [ ] Implement "since last snapshot" logic
- [ ] Add custom date range picker

**Backend work:**
- [ ] Add `since` parameter to `/api/state` (filter findings by introduction date)

**Acceptance:**
- User can filter issues to "Last Week" → see only findings introduced in last 7 days

### **Phase 5: Temporal Intelligence (Week 8+)**

**Goal:** Proactive insights from temporal data.

- [ ] Add forecasting widget to Health screen
- [ ] Implement velocity tracking (health change rate)
- [ ] Add temporal annotations (manual + auto-detected)
- [ ] Create temporal heatmap visualization

**Backend work:**
- [ ] Implement forecasting algorithm (linear regression)
- [ ] Add annotation storage (new DB table)
- [ ] Detect anomalies (spikes/drops in metrics)

**Acceptance:**
- User sees forecast: "Health will drop below 6.0 in 24 days"
- User can annotate timeline: "Deployed v2.0 here"
- User sees heatmap of file risk over time

---

## Design Patterns & Best Practices

### **Pattern 1: Temporal Context Everywhere**

**Rule:** Every piece of data must be contextual to a timestamp.

```js
// ❌ BAD - No temporal context
<div>Health: {data.health}</div>

// ✅ GOOD - Always show timestamp
<div>
  Health: {data.health}
  <span className="text-label">
    as of {formatTimestamp(currentSnapshotTimestamp)}
  </span>
</div>
```

### **Pattern 2: Immutable Historical Data**

**Rule:** Historical snapshots are READ-ONLY. Never mutate.

```js
// ❌ BAD - Mutating historical data
if (temporalMode === "historical") {
  data.files["new.py"] = { ... };  // WRONG!
}

// ✅ GOOD - Historical data is immutable
if (temporalMode === "historical") {
  // Disable all write operations
  // Show "read-only" indicator
}
```

### **Pattern 3: Comparison State is Separate**

**Rule:** Comparison mode uses DIFFERENT state from normal view.

```js
// Store structure
{
  // Normal view (single snapshot)
  data: { ... },

  // Comparison view (two snapshots + diff)
  comparisonData: {
    base: { ... },
    target: { ... },
    diff: { ... }
  }
}
```

### **Pattern 4: Graceful Degradation**

**Rule:** Temporal features are OPTIONAL. Work without snapshots.

```js
// If no snapshot history exists
if (snapshotList.length === 0) {
  // Hide timeline UI
  // Show: "Run analysis with --save to track history"
}

// If only 1 snapshot exists
if (snapshotList.length === 1) {
  // Hide comparison mode
  // Show trends as "N/A"
}
```

---

## Open Questions / Decisions Needed

1. **Snapshot retention:**
   - Keep all snapshots forever?
   - Auto-delete snapshots older than N months?
   - Compress old snapshots (keep only aggregates)?

2. **Real-time + historical mix:**
   - Should we allow viewing historical snapshot while receiving live updates in background?
   - Or strict mode: historical = pause all live updates?

3. **Comparison granularity:**
   - Compare at file level only?
   - Or also at function/class level (requires deeper AST diffing)?

4. **Performance:**
   - Loading full snapshot (247 files * all signals) could be slow
   - Should we paginate historical snapshots?
   - Client-side caching strategy?

5. **URL routing:**
   - Should snapshot ID be in URL? (`/#overview?snapshot=123`)
   - Enables sharing links to specific historical views
   - But complicates routing logic

---

## Success Metrics

**How to measure if temporal UX is successful:**

1. **Usage metrics:**
   - % of users who use timeline (at least once per session)
   - % of users who enter comparison mode
   - Average snapshots viewed per session

2. **Value metrics:**
   - Time to insight: "How long to identify when a regression was introduced?"
   - Before: Manual git bisect (hours)
   - After: Timeline + comparison (minutes)

3. **User feedback:**
   - Survey: "Does the timeline help you understand code health evolution?" (1-5)
   - Target: >4.0 average

---

## Long-Term Vision

**Shannon Insight becomes a "Time Machine for Code Health":**

- View your codebase at ANY point in history
- Compare ANY two points in time
- Understand HOW and WHEN things degraded
- Predict FUTURE health based on current trends
- Annotate timeline with deployments, refactors, incidents
- **Answer:** "We deployed last Thursday and health dropped by 0.5 points. What changed?"

**Temporal-first mindset:**
- Every metric is a time series
- Every finding has a lifecycle (introduced → active → resolved)
- Every file has a trajectory (improving vs degrading)
- The dashboard is a **temporal navigation interface**, not just a static report

---

## Appendix: Prior Art (Inspiration)

- **Git:** `git log`, `git diff`, `git bisect` - navigating history to find regressions
- **Grafana:** Time range picker, comparison mode, annotations - best-in-class temporal UX
- **DataDog APM:** Before/after comparison, anomaly detection, forecasting
- **GitHub Insights:** Contribution graphs, pulse (weekly summary), traffic trends
- **Linear:** Issue lifecycle tracking, velocity trends, cycle time forecasting

**Lesson:** Temporal features are NOT optional for analysis tools. They're table stakes.

---

## Next Steps

1. **Review this doc with team** - alignment on strategy
2. **Prioritize phases** - which phase gives most value fastest?
3. **Spike backend APIs** - feasibility of `/api/snapshot/:id` and `/api/compare`
4. **Design temporal bar** - Figma mockups for temporal context UI
5. **Implement Phase 1** - get temporal context visible ASAP

**Timeline:** 8 weeks for all phases, or 2 weeks for Phase 1 MVP.
