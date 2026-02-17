# Shannon Insight Dashboard — UI/UX Roadmap

## Current State

The `shannon-insight serve` command launches a live dashboard at `localhost:8765` with file watching and WebSocket updates. The dashboard has 4 screens (Overview, Issues, Files, Health) with a dark terminal aesthetic.

**What works**: real-time file watching, WebSocket push, basic finding display, file drill-down, health score.

**What doesn't**: no charts, no graphs, no trends, no search, no keyboard navigation, no module view, no dependency visualization, half the computed data is never surfaced, no progressive disclosure, weak information architecture, no accessibility consideration.

---

## Information Architecture

The current IA is flat — 4 tabs with no clear drill-down hierarchy. Developer tools that work (SonarQube, CodeScene, Snyk) all follow the same pattern:

```
Verdict → KPIs → Prioritized List → Detail → Action
```

### Proposed IA

```
LEVEL 0: Quality Gate
  PASS / FAIL — binary, no ambiguity
  "Your code is / is not releasable"

LEVEL 1: Dashboard (Overview)
  Health score + 3-5 stat KPIs
  Concern radar (6 dimensions at a glance)
  Focus point ("start here")
  Category summary (Incomplete / Fragile / Tangled / Team)

LEVEL 2: Exploration
  Issues → tabbed by category → sorted by severity × effort
  Files → sortable table → search/filter
  Modules → module list with Martin metrics
  Graph → dependency visualization

LEVEL 3: Detail
  File detail → signals grouped by category → findings → trend sparkline
  Module detail → files in module → instability/abstractness → violations
  Finding detail → evidence → interpretation → suggestion → effort

LEVEL 4: History (if .shannon/history.db exists)
  Health trend line chart (last 20 snapshots)
  Top movers (biggest metric changes)
  Chronic findings (persisting 3+ snapshots)
  Per-file signal sparklines
```

### Navigation Model

**Primary**: top nav tabs (Overview, Issues, Files, Modules, Health)
**Secondary**: click-through drill-down (file → detail, finding → file, module → files)
**Tertiary**: hash-based deep links (`#files/<path>`, `#issues/<category>`, `#modules/<path>`)
**Keyboard**: `1-5` for tabs, `/` for search, `Esc` for back, `j/k` for list navigation

---

## Visual Communication System

### The Problem

Color, typography, and layout must communicate meaning — not decoration. Every pixel should answer one of three questions:
1. **How healthy?** (color = health signal)
2. **How important?** (size/position = priority)
3. **What changed?** (delta indicators, sparklines, trend arrows)

### Color System

Use OKLCH for perceptual uniformity. Never rely on color alone — always pair with text labels or icons.

```
Health gradient (4 stops):
  Critical  : oklch(0.65 0.24 25)   — red     #ef4444
  Degraded  : oklch(0.72 0.18 55)   — orange  #f97316
  Warning   : oklch(0.80 0.17 85)   — yellow  #eab308
  Healthy   : oklch(0.70 0.18 145)  — green   #22c55e

Severity indicators:
  CRITICAL  : red dot (6px) + "CRITICAL" text
  HIGH      : orange dot + "HIGH" text
  MEDIUM    : yellow dot + "MEDIUM" text
  LOW       : blue dot + "LOW" text
  INFO      : gray dot + "INFO" text

Surface palette:
  bg-0      : #0a0a0a   (page background)
  bg-1      : #141414   (cards/surfaces)
  bg-2      : #1a1a1a   (hover/active states)
  border    : #1e1e1e   (dividers)
  text-1    : #d4d4d4   (primary text)
  text-2    : #737373   (secondary/labels)
  text-3    : #525252   (tertiary/disabled)
  accent    : #3b82f6   (links, interactive elements)
```

Colorblind safety: the red-orange-yellow-green gradient is distinguishable in protanopia/deuteranopia because lightness varies (0.65 → 0.70 → 0.80 → 0.70) and the hue range avoids pure red/green adjacency. For critical contexts, always pair with text labels.

### Typography

```
Data/numbers  : JetBrains Mono, 11px — all numeric values, file paths, signal names
Labels        : Inter, 12px — UI labels, section headers, nav items
Body          : Inter, 13px — descriptions, interpretations
Big numbers   : JetBrains Mono, 48px — health score, primary KPIs
Section heads : Inter 600, 11px uppercase tracking 0.5px — card titles
```

### Data Density Target

40% information density on overview screen (research shows 63% faster pattern recognition). Higher density on detail screens (developers expect it when they've drilled in). No empty space larger than 24px that doesn't serve as a visual separator.

---

## Roadmap: 6 Phases

### Phase 1: Surface Existing Data

Everything listed here is already computed by the backend. The dashboard just doesn't render it.

**1.1 — Render unsurfaced finding fields**
- Show `suggestion` text on each finding (exists in API, ignored by HTML)
- Show `effort` badge (LOW/MEDIUM/HIGH) — helps developers prioritize
- Show `confidence` as opacity modifier (low confidence = slightly faded)
- Use `data_points` from `FINDING_DISPLAY` to order evidence display

**1.2 — Render module data**
- Add Modules screen (data already in `DATA.modules`, never rendered)
- Show per-module: health score, instability, abstractness, file count, velocity
- Instability/abstractness scatter position (main sequence distance)
- Click module → list of files in module

**1.3 — Use SIGNAL_LABELS and SIGNAL_POLARITY in file detail**
- Replace `key.replace(/_/g, ' ')` with proper labels from `SIGNAL_LABELS`
- Group signals by `SIGNAL_CATEGORIES` (Size, Graph, Health, Temporal, Team, Risk)
- Color signal values using `SIGNAL_POLARITY` (red for high-is-bad above threshold, green for high-is-good)
- Use `format_signal_value()` logic (percentages for ratios, proper decimal places)

**1.4 — Enrich the API response**
- Add `dependency_edges` to dashboard state (already on TensorSnapshot)
- Add `delta_h` (health Laplacian) per file
- Add `violations` (architecture violations)
- Add `layers` (layer structure)
- Add concern `attributes` and `description` to concern JSON
- Add `analyzers_ran` to metadata

**1.5 — Focus point improvements**
- Show actionability breakdown: risk × impact × tractability × confidence
- Show alternative `why` text (already serialized, ignored by HTML)
- Use `get_verdict()` for the overview verdict instead of simple `_health_label()`

### Phase 2: Search, Sort, Filter

**2.1 — File table search**
- Text input above file table, filters by path substring (client-side, instant)
- Filter chips: role (MODEL, SERVICE, ENTRY_POINT), has-findings, is-orphan

**2.2 — Issue sorting and filtering**
- Sort findings within each category tab by: severity, confidence, effort, file count
- Severity filter: toggle visibility of LOW/INFO findings
- Scope filter: show only FILE scope, or only CODEBASE scope

**2.3 — Column customization on file table**
- Default 6 columns: File, Risk, Churn, Complexity, Blast R., Issues
- Toggle additional columns: Role, Bus Factor, Churn CV, Orphan, Health Score
- Column selection persisted in localStorage

**2.4 — Keyboard navigation**
- `1-5` switch tabs
- `/` focus search
- `j/k` move through file list or finding list
- `Enter` drill into selected item
- `Esc` go back one level

### Phase 3: Charts and Visualization

**3.1 — Concern radar chart (SVG)**
- Hexagonal radar with 6 axes (Complexity, Coupling, Architecture, Stability, Team, Broken)
- Score 0-10 on each axis
- Filled area shows health profile shape
- Replaces the horizontal bar display — communicates the same data in less space and shows the *shape* of health

**3.2 — Risk distribution histogram (SVG)**
- Horizontal histogram of `risk_score` values across all files
- Bins: 0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0
- Color-coded by health gradient
- Shows whether risk is concentrated in a few files or spread evenly

**3.3 — Treemap (port from report.py)**
- The existing `visualization/treemap.py` has `build_treemap_data()` and a squarified layout algorithm
- Port the treemap rendering to the dashboard as a full-screen overlay or dedicated section
- Color by health score, size by lines of code
- Click file rectangle → file detail

**3.4 — Signal sparklines for file detail**
- When `.shannon/history.db` exists, query `HistoryQuery.file_trend()` for the file being viewed
- Render SVG sparklines (30px tall, 100px wide) next to key signals
- Shows trend direction without needing a separate history screen

**3.5 — Dependency graph (optional, high effort)**
- Force-directed layout of `dependency_edges`
- Nodes = files, sized by PageRank, colored by health
- Edges = imports
- Highlight the selected file and its immediate neighbors
- This is the highest-effort visualization — defer until other phases complete

### Phase 4: History and Trends

Requires connecting the dashboard to `.shannon/history.db`. The `HistoryQuery` class already has all the query methods.

**4.1 — Wire DB queries into the API**
- In `build_dashboard_state()`, optionally accept a DB connection
- Query `codebase_health()` for last 20 snapshots → add `trends.health` to state
- Query `top_movers()` → add `trends.movers` to state
- Query `persistent_findings()` → add `trends.chronic` to state

**4.2 — Health trend line chart**
- SVG line chart showing codebase health score over last 20 snapshots
- X-axis: commit or timestamp
- Y-axis: health score 1-10
- Color: health gradient
- Show finding count as a secondary line or bar overlay

**4.3 — Top movers widget**
- List of files with biggest health changes since last snapshot
- Show delta (e.g., "-1.2" in red, "+0.8" in green)
- Arrow indicators for direction

**4.4 — Chronic findings panel**
- Findings persisting 3+ snapshots highlighted with a "chronic" badge
- Shows finding age (first_seen) and persistence count
- Higher priority than new findings in the issue list

**4.5 — Per-file trend sparklines**
- In file detail view, query `get_signal_time_series()` for key signals
- Render inline SVG sparklines (tiny line charts) next to each signal value
- Signals with sparklines: risk_score, cognitive_load, total_changes, churn_cv

### Phase 5: Watcher Improvements

**5.1 — Track changed files**
- Watcher already detects `changed_files` (list of paths) but discards them
- Pass changed file paths to `ServerState` as `recent_changes`
- Dashboard highlights changed files in the file table (background flash or badge)
- Overview shows "3 files changed" with list

**5.2 — Retain previous snapshot for diff**
- Keep the previous `TensorSnapshot` in `ServerState`
- On re-analysis, compute deltas: health change per file, new findings, resolved findings
- Surface in the WebSocket `complete` message as `changes` field

**5.3 — Determinate progress bar**
- The kernel calls `on_progress("Scanning files...")`, `on_progress("Running StructuralAnalyzer...")`
- Map these to known phase counts (scan=1, parse=2, analyze=3-7, finders=8, rank=9, capture=10)
- Send progress as `{type: "progress", message: "...", percent: 0.4}`
- Dashboard shows a real percentage bar instead of infinite animation

### Phase 6: Export and Integration

**6.1 — Export buttons**
- JSON export: download full `/api/state` as `shannon-insight-<timestamp>.json`
- CSV export: file table as CSV (all columns, all files)
- HTML report: trigger `report.py` generation and serve the file

**6.2 — Deep link sharing**
- Every view state encodable as a URL hash
- `#issues/fragile` — issues tab filtered to fragile
- `#files/src%2Fmodels.py/signals` — file detail with signals section open
- Copy-link button in the UI

**6.3 — Quality gate endpoint**
- `GET /api/gate` returns `{"status": "PASS"|"FAIL", "reason": "..."}`
- Based on configurable thresholds (e.g., health > 5.0, no CRITICAL findings)
- Useful for CI integration: `curl -sf localhost:8765/api/gate | jq .status`

---

## Implementation Priority

| Phase | What | Why first |
|-------|------|-----------|
| **1** | Surface existing data | Zero backend work — all data already computed, just render it |
| **2** | Search, sort, filter | Most requested developer interaction patterns |
| **3** | Charts and visualization | Visual communication — the core thesis of this tool |
| **4** | History and trends | Requires DB wiring — deferred complexity |
| **5** | Watcher improvements | Nice-to-have for the live experience |
| **6** | Export and integration | Sharing and CI — last mile |

Phase 1 should be done first because it costs nothing — the backend already computes all this data. Phases 2-3 can be done in parallel. Phase 4 requires backend changes (DB connection in the server). Phases 5-6 are incremental improvements.

---

## Accessibility Checklist

Apply at every phase:

- [ ] Color is never the sole indicator — always paired with text or icon
- [ ] WCAG AA contrast ratios: 4.5:1 for text, 3:1 for UI components
- [ ] All interactive elements have visible focus states
- [ ] Tab order follows visual layout (left-to-right, top-to-bottom)
- [ ] Screen reader labels on all charts (SVG `<title>` and `<desc>` elements)
- [ ] Reduced motion preference respected (`prefers-reduced-motion` media query)
- [ ] Font sizes never below 11px
- [ ] Touch targets minimum 44x44px on mobile

---

## Design References

| Tool | What to learn | Link |
|------|--------------|------|
| CodeScene | Hotspot map, 3 KPIs, technical debt friction | codescene.com/product/code-health |
| SonarQube | Quality gate, A-E grades, "Clean as You Code" delta focus | docs.sonarsource.com |
| Snyk | Priority Score (1-1000), effort-weighted prioritization | snyk.io/blog/snyk-code-priority-score |
| Linear | Monochrome-first, keyboard-driven, OKLCH color system | linear.app/now/how-we-redesigned-the-linear-ui |
| Grafana | Stat panels, RED method layout, sparklines, collapsible rows | grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices |
| GitHub Next | Circle packing for repo visualization | githubnext.com/projects/repo-visualization |
| NDepend | Treemap (size=LOC, color=metric), dependency structure matrix | ndepend.com/docs/treemap-visualization |
| Codacy | Evolution charts, severity tiers, quality goals with progress | docs.codacy.com/repositories/repository-dashboard |

### Research

| Paper/Article | Key insight |
|--------------|-------------|
| Dashboard Design Patterns (IEEE TVCG, 144 dashboards analyzed) | Hierarchical page structure most common for analysis tools |
| Four Cognitive Design Guidelines (UX Magazine) | <40% info density = 63% faster pattern recognition |
| Tufte's Data-Ink Ratio | Maximize data per pixel, eliminate decorative ink |
| Primer Progressive Disclosure | Reveal detail on demand, never disorient the user's focus point |
| Carbon Design Status Indicators | 3:1 contrast, always pair color with icon/text |

---

## Non-Goals

- **No real-time collaboration** — this is a single-developer tool
- **No user accounts or auth** — local-only, bound to 127.0.0.1
- **No mobile-first design** — desktop is primary, mobile gets basic responsive stacking
- **No framework (React, Vue, etc.)** — self-contained HTML, inline JS/CSS
- **No build step** — the HTML is embedded in `app.py`, must stay self-contained
- **No external CDN dependencies beyond fonts** — works offline except for font loading
