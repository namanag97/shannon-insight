# Information Architecture Redesign

**Shannon Insight Dashboard - Screen-by-Screen Redesign**

This document defines **what to show, in what order, and why** for each screen. Every section has a clear purpose and priority level.

---

## Core User Questions

Shannon Insight answers these questions in priority order:

1. **"How healthy is my codebase?"** → Health Score (Overview)
2. **"What should I fix first?"** → Focus Point (Overview)
3. **"Where is the risk?"** → Risk Distribution (Overview)
4. **"What problems exist?"** → Issues (Issues screen)
5. **"Which files need attention?"** → Files (Files screen)
6. **"How is the architecture?"** → Modules (Modules screen)
7. **"Is it getting better or worse?"** → Health Trends (Health screen)

---

## 1. Overview Screen

**Purpose:** Give immediate health status and actionable next steps.

### Layout Structure (Priority Order)

```
┌─────────────────────────────────────────────────────┐
│ 1. HERO - Health Score + Verdict + Trend           │  ~20vh
│    Answer: "How healthy is my codebase?"           │
│    Visual: Large number (7.2), color-coded         │
│    Context: Trend arrow (↑/↓), verdict badge       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 2. FOCUS POINT - Recommended Starting Point        │  ~25vh
│    Answer: "What should I fix first?"              │
│    Visual: Large card with file path, metrics      │
│    Action: Click to view file detail               │
└─────────────────────────────────────────────────────┘

┌───────────────────────┬─────────────────────────────┐
│ 3a. RISK DISTRIBUTION │ 3b. CRITICAL ISSUES        │  ~25vh
│    Answer: "Where is  │     Answer: "What are the  │
│    the risk?"         │     worst problems?"       │
│    Visual: Histogram  │     Visual: Top 5 list     │
└───────────────────────┴─────────────────────────────┘

┌───────────────────────┬─────────────────────────────┐
│ 4a. KEY METRICS       │ 4b. CATEGORY BREAKDOWN     │  ~20vh
│    Files: 247         │     [Bar chart by type]    │
│    Modules: 12        │     Incomplete: 23         │
│    Commits: 340       │     Design: 12             │
│    Issues: 78         │     ...                    │
└───────────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 5. SUPPORTING DATA (Collapsible)                   │  Optional
│    Evolution charts, metadata, etc.                │
│    Low priority - below the fold                   │
└─────────────────────────────────────────────────────┘
```

### Information Priority Breakdown

**Priority 1: Hero** (Must see first)
- Health Score: `7.2`
- Verdict: `"Needs Attention"` or `"Healthy"` or `"Critical"`
- Trend: `↓ 0.4 points since last analysis`
- Rationale: Instant status - like checking a dashboard warning light

**Priority 2: Action** (What to do)
- Focus Point file path: `src/auth/service.py`
- Why: `"Highest risk-to-effort ratio"`
- Key metrics: Risk `0.83`, `12 findings`, `47 dependents`
- Rationale: User shouldn't have to hunt for where to start

**Priority 3: Context** (Why it matters)
- **3a. Risk Heatmap:** Shows distribution of high/med/low risk files
- **3b. Top Issues:** Shows 5 critical findings (God File, High Risk Hub, etc.)
- Rationale: Understand severity and scope before diving in

**Priority 4: Details** (Supporting info)
- **4a. Metrics:** File count, module count, commits, issues
- **4b. Categories:** Breakdown of issue types
- Rationale: Nice to know, but not critical for decision-making

**Priority 5: Deep Data** (Optional)
- Evolution charts (how metrics changed over time)
- Metadata (DB size, analyzers ran, etc.)
- Rationale: For power users who want historical context

### What Gets Removed/Moved

**REMOVED from top of page:**
- Evolution charts (moved to collapsible section or Health screen)
- Metadata grid (moved to collapsible section)

**MOVED UP:**
- Focus Point (from bottom → priority #2)
- Top 5 critical issues (new component, priority #3)

**Why:** Evolution and metadata are **historical context**, not **actionable insights**. They compete with critical info for attention.

---

## 2. Files Screen

**Purpose:** Show which files need attention and enable drill-down.

### Layout Structure

```
┌───────────┬───────────┬───────────┬───────────────┐
│ 🔴 HIGH   │ 🟡 MEDIUM │ 🟢 LOW    │ ⚪ NO ISSUES  │  Summary Cards
│ 12 files  │ 45 files  │ 98 files  │ 92 files     │
│ (Top 5%)  │ (Next 18%)│ (32%)     │ (45%)        │
└───────────┴───────────┴───────────┴───────────────┘

┌─────────────────────────────────────────────────────┐
│ 🎯 FILES NEEDING ATTENTION (Top 10)                │  Priority List
│ [Compact table: Path | Risk | Issues | Complexity] │
│ auth/service.py    | 0.83 | 12  | 47              │
│ database.py        | 0.72 | 8   | 34              │
│ ...                                                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ [Search] [Filters: Has Issues, Orphans, etc.]      │  Tools
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ALL FILES (247)                                     │  Full Table
│ [Table with 6 columns, sortable, paginated]        │
│ [Grouped by risk tier: HIGH / MEDIUM / LOW]        │
└─────────────────────────────────────────────────────┘
```

### Information Priority Breakdown

**Priority 1: Summary** (At a glance)
- Show distribution: How many high/medium/low risk files?
- Rationale: Instant scope understanding

**Priority 2: Action Items** (Top 10)
- Show worst files first
- Compact view with key metrics only
- Click to drill into file detail
- Rationale: "Just tell me what to fix"

**Priority 3: Tools** (Search/Filter)
- Search bar, filter chips
- Now below the insights, not above
- Rationale: Lead with insights, then offer exploration

**Priority 4: Full Data** (Everything)
- Complete file table
- Grouped by risk tier (visual separation)
- Sortable, paginated
- Rationale: For comprehensive audit

### What Changes

**BEFORE:**
```
[ Search + Filters ]  ← Tool-first (wrong)
[ Table ]             ← Flat, no grouping
```

**AFTER:**
```
[ Summary Cards ]     ← Insight-first (correct)
[ Top 10 Files ]      ← Action items
[ Search + Filters ]  ← Tools below insights
[ Full Table ]        ← Grouped by risk tier
```

---

## 3. Issues Screen

**Purpose:** Show all findings, prioritized by severity and impact.

### Layout Structure

```
┌─────────────────────────────────────────────────────┐
│ SEVERITY OVERVIEW                                   │  Visual Bar
│ ████ Critical (3) | ████████ High (12) | ...       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🔥 CRITICAL FINDINGS (3)                           │  Expanded
│                                                     │
│ 🔴 GOD FILE: auth/service.py                       │
│    → 847 LOC, 23 dependencies, affects 47 files   │
│    → Suggestion: Split into AuthService + ...      │
│                                                     │
│ 🔴 HIGH RISK HUB: database.py                      │
│    → Risk 0.72, PageRank 0.85, 34 importers       │
│    → Suggestion: Add comprehensive tests           │
│                                                     │
│ 🔴 HIDDEN COUPLING: 3 files in auth module        │
│    → semantic_coherence 0.89, should be separate  │
│    → Files: auth/oauth.py, auth/jwt.py, ...       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ▶ HIGH PRIORITY (12)                 [Click to expand]│
│ ▶ MEDIUM PRIORITY (45)               [Collapsed]   │
│ ▶ LOW PRIORITY (18)                  [Collapsed]   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ [Sort: Severity ▼] [Filter: All Categories]        │  Tools
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ INCOMPLETE (23) │ DESIGN (12) │ TEMPORAL (8) │ ... │  Category Tabs
│ [Findings grouped by category]                      │
└─────────────────────────────────────────────────────┘
```

### Information Priority Breakdown

**Priority 1: Severity Summary** (Context)
- Visual bar showing distribution
- Numbers: `CRITICAL (3) | HIGH (12) | MEDIUM (45) | LOW (18)`
- Rationale: Understand scope before diving in

**Priority 2: Critical Findings** (Always Expanded)
- Show ALL critical findings first
- Expanded by default (no hiding critical issues)
- Rich detail: file path, evidence, suggestion
- Rationale: Critical issues demand immediate attention

**Priority 3: High/Medium Findings** (Collapsible)
- Collapsed by default to reduce scroll
- Click to expand
- Rationale: User controls information density

**Priority 4: Tools** (Sort/Filter)
- Below the data, not above
- Rationale: Insights first, tools second

**Priority 5: Category View** (Alternative View)
- Tab-based breakdown by issue type
- For users who want to tackle one category at a time
- Rationale: Different mental model for some users

### What Changes

**BEFORE:**
```
[ Sort + Filter ]     ← Tool-first
[ Category Tabs ]     ← Forces single-category view
[ Flat finding list ] ← No priority separation
```

**AFTER:**
```
[ Severity Bar ]      ← Context
[ Critical (expanded)] ← Highest priority always visible
[ High (collapsed) ]  ← User controls expansion
[ Medium (collapsed)] ← Reduces scroll
[ Tools ]             ← Below insights
[ Category tabs ]     ← Alternative view
```

---

## 4. Modules Screen

**Purpose:** Show architectural health and module boundaries.

### Layout Structure

```
┌───────────────────────┬─────────────────────────────┐
│ MODULE HEALTH         │ ARCHITECTURAL METRICS       │
│ Avg: 7.2             │ Coupling: 0.45              │
│ Best: auth (9.1)      │ Cohesion: 0.72              │
│ Worst: utils (4.3)    │ Violations: 3               │
└───────────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🎯 MODULES NEEDING ATTENTION (Top 5)               │
│ utils/ (health: 4.3, instability: 0.89)            │
│ database/ (health: 5.1, abstractness: 0.12)       │
│ ...                                                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ALL MODULES (12)                                    │
│ [Table: Path | Health | Files | Instability | ...]│
│ [Sorted by health, ascending]                      │
└─────────────────────────────────────────────────────┘
```

### Information Priority Breakdown

**Priority 1: Summary** (Health at a glance)
- Average module health
- Best/worst modules
- Key architectural metrics
- Rationale: Instant architectural health check

**Priority 2: Problem Modules** (What to fix)
- Top 5 worst modules
- Key metrics (health, instability, violations)
- Rationale: Action-oriented

**Priority 3: Full List** (All modules)
- Complete table with all metrics
- Rationale: Comprehensive view

---

## 5. Health Screen

**Purpose:** Show trends over time - is the codebase improving?

### Layout Structure

```
┌─────────────────────────────────────────────────────┐
│ HEALTH TREND                                        │
│ [Large line chart: Health score over time]         │
│ Current: 7.2 | 7 days ago: 7.6 | ↓ 0.4            │
└─────────────────────────────────────────────────────┘

┌───────────────────────┬─────────────────────────────┐
│ TOP MOVERS            │ CHRONIC ISSUES              │
│ Improved:             │ God File: 3 snapshots       │
│ ↑ auth/login.py (+1.2)│ High Risk Hub: 5 snapshots  │
│                       │ (Never resolved)            │
│ Degraded:             │                             │
│ ↓ utils.py (-0.8)     │                             │
└───────────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ EVOLUTION CHARTS                                    │
│ [4 charts: Files, LOC, Complexity, Risk]           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ SNAPSHOT HISTORY (Last 10)                         │
│ [Table: Date | Health | Files | Issues | ...]     │
└─────────────────────────────────────────────────────┘
```

### Information Priority Breakdown

**Priority 1: Trend** (Getting better or worse?)
- Large health chart over time
- Clear indication of direction
- Rationale: First question is "are we improving?"

**Priority 2: Movers** (What changed?)
- Files that improved/degraded the most
- Chronic issues that never get fixed
- Rationale: Understand what drove the change

**Priority 3: Evolution** (Detailed trends)
- Charts for files, LOC, complexity, risk
- Rationale: Deep analysis for power users

**Priority 4: History** (Snapshot log)
- Table of all snapshots
- Rationale: Audit trail

---

## 6. Graph Screen

**Purpose:** Visualize dependency structure and community clustering.

**No changes needed.** Current implementation is solid:
- Interactive force-directed graph
- Community legend
- Node click for detail panel
- Filters and controls

**Rationale:** Graph visualization is inherently exploratory. The current tool-first approach makes sense here.

---

## Design Rationale Summary

### Universal Principles Applied

1. **Insights Before Tools**
   - Show the data FIRST
   - Offer search/filter/sort AFTER
   - Rationale: Users came for insights, not tools

2. **Priority-Based Layout**
   - Most important info at top
   - Supporting data below
   - Historical/metadata at bottom
   - Rationale: Respect user's time and attention

3. **Action-Oriented**
   - Always show "what should I do?" prominently
   - Top N lists, focus points, recommendations
   - Rationale: Users want to improve their code, not just analyze it

4. **Progressive Disclosure**
   - Critical info always visible
   - Medium priority collapsible
   - Low priority below fold
   - Rationale: Reduce cognitive load

5. **Visual Hierarchy**
   - Use size, weight, color to indicate importance
   - Never make everything equally prominent
   - Rationale: Human eyes follow visual weight

---

## Next Step

Apply this information architecture to the **Overview screen** first as a proof-of-concept. Then roll out to other screens.
