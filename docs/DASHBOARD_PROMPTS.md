# Dashboard Implementation Prompts

Each prompt below is self-contained. Copy-paste one into a Claude Code session to execute that task. Run them in order within each phase. Phases 2-3 can run in parallel after Phase 1 is complete.

Before every session: `cd /Users/namanagarwal/Projects/shannon-insight`

After every session: `ruff check src/ tests/ && python -m pytest tests/ -q`

---

## Phase 1: Surface Existing Data

### Prompt 1.1 — Enrich the API Response

```
In the shannon-insight codebase, the dashboard API at src/shannon_insight/server/api.py builds the JSON state but omits data that TensorSnapshot already has. Fix this.

Read these files first:
- src/shannon_insight/server/api.py
- src/shannon_insight/persistence/models.py (TensorSnapshot fields)
- src/shannon_insight/cli/_concerns.py (ConcernReport attributes)

Then edit api.py build_dashboard_state() to add:

1. "dependency_edges": snapshot.dependency_edges (list of [src, tgt] pairs)
2. "delta_h": snapshot.delta_h (dict of file_path -> float)
3. "violations": snapshot.violations (list of dicts)
4. "layers": snapshot.layers (list of dicts)
5. "analyzers_ran": snapshot.analyzers_ran (list of strings)
6. "analyzed_path": snapshot.analyzed_path (string)

For the "concerns" list, expand each concern to include:
- "description": from Concern.description
- "attributes": from ConcernReport.attributes (dict of metric_key -> value)
- "file_count": from ConcernReport.file_count
- "finding_count": existing

For each finding in _finding_to_dict(), the "suggestion", "confidence", "effort", "scope", and "icon" fields are already serialized. No change needed there.

Add a test in tests/server/test_api.py that verifies the new fields are present in build_dashboard_state() output when the snapshot has dependency_edges and delta_h populated.

Run: ruff check src/shannon_insight/server/api.py tests/server/test_api.py && python -m pytest tests/server/ -v
```

### Prompt 1.2 — Render Finding Suggestions and Effort

```
In the shannon-insight dashboard HTML (src/shannon_insight/server/app.py, the _DASHBOARD_HTML string), findings currently show type + files + interpretation but ignore suggestion, effort, and confidence.

Read src/shannon_insight/server/app.py and find the JavaScript functions that render findings (search for "finding-interp" and the finding rendering loops in renderIssues, renderHome, and showFileDetail).

For every place a finding is rendered, add after the interpretation line:

1. Suggestion text — render f.suggestion as a separate line in text-2 color, 11px, prefixed with a right-arrow character "→". Only show if f.suggestion is non-empty.

2. Effort badge — render f.effort as inline text: "LOW" in green, "MEDIUM" in yellow, "HIGH" in orange. Use a small bordered span, 10px font, monospace. Place it next to the severity indicator.

3. Confidence — if f.confidence < 0.7, add style="opacity:0.65" to the entire finding div. This visually de-emphasizes low-confidence findings without hiding them.

Do NOT change any Python code. Only modify the _DASHBOARD_HTML string.

Test by running: python -c "from shannon_insight.server.app import _DASHBOARD_HTML; assert 'suggestion' in _DASHBOARD_HTML.lower() or 'f.suggestion' in _DASHBOARD_HTML"
Then: ruff check src/shannon_insight/server/app.py
```

### Prompt 1.3 — Add Modules Screen

```
The dashboard at src/shannon_insight/server/app.py has 4 screens (overview, issues, files, health). The API already returns DATA.modules (dict of module_path -> {health_score, instability, abstractness, file_count, velocity}) but no screen renders it.

Add a 5th screen: Modules.

Read src/shannon_insight/server/app.py (the full _DASHBOARD_HTML string).

1. Add a "Modules" tab to the nav bar (between Files and Health).

2. Add a <div class="screen" id="screen-modules"> with:
   - A sortable table with columns: Module, Health, Instability, Abstractness, Files, Velocity
   - Same table style as the files table
   - Sortable by clicking headers (default: health ascending = worst first)
   - Module paths in monospace, clickable
   - Health column colored by health color function
   - Instability shows "—" when null (isolated modules)

3. Add a module detail view (shown when clicking a module row):
   - Back link "← Modules"
   - Module path in large monospace
   - Health score colored, instability, abstractness as stat boxes
   - List of files in this module: filter DATA.files where file.signals.module_path matches
   - If DATA.violations exists, show violations where src or tgt starts with this module path

4. Wire up routing: #modules for list, #modules/<path> for detail.

5. Update the navigate() function and hash routing to handle "modules".

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

### Prompt 1.4 — Signal Labels, Categories, and Polarity in File Detail

```
The file detail view in the dashboard (src/shannon_insight/server/app.py, _DASHBOARD_HTML, the showFileDetail function) shows all signals as a flat alphabetically sorted grid with generic labels (key.replace(/_/g, ' ')) and no color coding.

The Python code at src/shannon_insight/cli/_signal_display.py has:
- SIGNAL_LABELS: dict mapping signal names to human labels (e.g. "blast_radius_size" -> "Blast radius (files affected)")
- SIGNAL_CATEGORIES: 6 categories (Size & Complexity, Graph Position, Code Health, Change History, Team Context, Computed Risk) each with a list of signal names
- SIGNAL_POLARITY: dict mapping signal names to polarity (true=higher is worse, false=higher is better, null=neutral)

Read both files. Then:

1. Embed SIGNAL_LABELS as a JS object in the HTML (const SIGNAL_LABELS = {...})
2. Embed SIGNAL_CATEGORIES as a JS array of {key, name, signals} objects
3. Embed SIGNAL_POLARITY as a JS object (true/false/null)

4. In showFileDetail(), replace the flat signal grid with grouped display:
   - For each category, show a section header (category name, 11px uppercase, text-2 color)
   - Under each header, list the signals in that category
   - Use SIGNAL_LABELS for display names instead of key.replace(/_/g, ' ')
   - Color values using SIGNAL_POLARITY:
     - polarity=true (higher is worse): red if value is high (>75th percentile or above threshold), green if low
     - polarity=false (higher is better): green if high, red if low
     - polarity=null: accent color (neutral)
   - Format values properly: ratios as percentages, scores to 3 decimals, counts as integers

5. Make the signals section collapsible (collapsed by default) with a toggle header "All Signals (N)"

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

### Prompt 1.5 — Focus Point Improvements

```
The focus point on the dashboard overview (src/shannon_insight/server/app.py, _DASHBOARD_HTML) shows path, why text, and findings. But it ignores:
- The actionability score breakdown (risk × impact × tractability × confidence)
- Alternative files' why text (DATA.focus.alternatives[].why exists but isn't rendered)

Read the app.py _DASHBOARD_HTML and find the focus point rendering section.

1. Below the focus point "why" text, add a small 4-column breakdown showing:
   risk: X.XX | impact: X.XX | tractability: X.XX | confidence: X.XX
   Use monospace 11px, text-2 color. These fields need to be added to the API first.

2. Read src/shannon_insight/server/api.py — the focus_data dict. Add these fields from the FocusPoint object:
   "risk_score": round(focus.risk_score, 3)
   "impact_score": round(focus.impact_score, 3)
   "tractability_score": round(focus.tractability_score, 3)
   "confidence_score": round(focus.confidence_score, 3)

3. In the alternatives list (below the main focus point), show each alternative's why text:
   Currently alternatives render as just paths. Change to: "path — why_text" with why in text-2 color.

4. Read src/shannon_insight/cli/_focus.py get_verdict(). In api.py, call get_verdict(raw_health, focus, total_findings_count) and add its result as "verdict" and "verdict_color" to the state dict. Render this verdict as a one-line banner above the health score on the overview.

Run: ruff check src/shannon_insight/server/api.py && python -m pytest tests/server/ -v
```

---

## Phase 2: Search, Sort, Filter

### Prompt 2.1 — File Table Search and Filters

```
The file table in the dashboard (src/shannon_insight/server/app.py, _DASHBOARD_HTML, the showFileList function) shows up to 200 files with no search or filtering.

Add search and filter controls above the file table:

1. Search input:
   - Full-width text input, monospace, placeholder "Search files..."
   - Filters file list in real-time as you type (client-side substring match on path)
   - Style: bg-1 background, border color, 13px monospace, 8px padding

2. Filter chips (row of toggleable buttons below search):
   - "Has Issues" — only show files where finding_count > 0
   - "Orphans" — only show files where is_orphan === true
   - Role filters: "MODEL", "SERVICE", "ENTRY_POINT", "TEST" — toggle each
   - Active chip: accent border + slightly lighter background
   - Multiple chips can be active simultaneously (AND logic)

3. Result count: show "Showing X of Y files" text below filters

4. The search and filter state should be preserved when navigating away and back to #files

Implementation:
- Add state variables: fileSearch (string), fileFilters (Set of active filter keys)
- In showFileList(), apply search + filters before sorting and slicing
- Chips are <button> elements with click handlers that toggle the filter set
- Search input has an 'input' event listener that updates fileSearch and re-renders

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

### Prompt 2.2 — Issue Sorting and Severity Filter

```
The Issues screen in the dashboard (src/shannon_insight/server/app.py, _DASHBOARD_HTML, renderIssues function) shows findings in whatever order the API returns them, with no sorting or filtering controls.

Add:

1. Sort dropdown above the findings list:
   - Options: "Severity (high first)", "Severity (low first)", "Effort (low first)", "File count"
   - Style: select element with bg-1 background, border, monospace
   - Default: severity descending

2. Severity filter toggles (row of small buttons):
   - CRITICAL, HIGH, MEDIUM, LOW, INFO — each toggleable
   - All active by default
   - Clicking toggles visibility of findings at that severity level
   - Show count next to each: "HIGH (3)"
   - Use severity dot colors for each button

3. Apply sort and filter before rendering:
   - Sort the findings array within each category based on selected sort
   - Filter out findings whose severity level is toggled off
   - Update tab counts to reflect filtered counts

State variables: issueSortKey (string), issueSeverityFilter (Set of active levels).
Preserve state when switching between category tabs.

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

### Prompt 2.3 — Keyboard Navigation

```
The dashboard at src/shannon_insight/server/app.py (_DASHBOARD_HTML) has no keyboard navigation.

Add a global keydown listener with these bindings:

1. Tab switching: keys 1-5 switch to tabs (1=overview, 2=issues, 3=files, 4=modules, 5=health)
   - Only when no input is focused
   - Call navigate() with the appropriate screen name

2. Search focus: "/" focuses the file search input (if on files screen) or navigates to files screen and focuses search
   - Prevent "/" from being typed into the input

3. List navigation: "j" moves selection down, "k" moves selection up
   - On files screen: highlight the next/previous row in the file table
   - On issues screen: highlight the next/previous finding
   - Use a CSS class "kbd-selected" with bg-2 background
   - Track selectedIndex per screen

4. Drill in: "Enter" activates the selected item
   - On files screen: navigate to file detail for the selected row
   - On issues screen: navigate to the first file in the selected finding

5. Go back: "Escape" goes back one level
   - File detail → file list
   - Module detail → module list
   - Any screen → overview

6. Show a small keyboard shortcut hint in the bottom-right corner:
   - "? for shortcuts" text in text-3 color, 10px
   - Pressing "?" toggles a small overlay showing all shortcuts

Implementation: single document.addEventListener('keydown', ...) handler.
Check document.activeElement.tagName !== 'INPUT' before handling non-search keys.

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

---

## Phase 3: Charts and Visualization

### Prompt 3.1 — Concern Radar Chart

```
The Health screen in the dashboard (src/shannon_insight/server/app.py, _DASHBOARD_HTML) shows concern dimensions as horizontal bars. Replace the bars with a hexagonal radar chart that communicates the same data in less space and shows the SHAPE of health.

Read the existing Health screen rendering (renderHealth function and the #screen-health div).

Build a pure SVG radar chart:

1. Geometry:
   - 6 axes arranged in a hexagon (0°, 60°, 120°, 180°, 240°, 300°)
   - Labels: Complexity, Coupling, Architecture, Stability, Team, Broken (from DATA.concerns)
   - Concentric hexagonal grid lines at 2, 4, 6, 8, 10
   - Grid lines: 1px stroke, border color (#1e1e1e)
   - Axis lines from center to each vertex: 1px stroke, border color

2. Data polygon:
   - Filled polygon connecting the 6 concern scores
   - Fill: accent color (#3b82f6) at 15% opacity
   - Stroke: accent color at 80% opacity, 2px
   - Vertices as small circles (4px radius) colored by health color of that score

3. Labels:
   - Concern name outside each vertex, 11px Inter
   - Score value next to each vertex, 11px JetBrains Mono, colored by healthColor()

4. Size: 300x300px SVG, centered in the card

5. Keep the global signals table below the radar chart.

6. Add a helper function polarToXY(centerX, centerY, radius, angleIndex) that converts a score (0-10) and axis index (0-5) to SVG x,y coordinates.

The DATA.concerns array has objects with {key, name, score, status, finding_count}. Map the 6 concerns to 6 axes. If fewer than 6 concerns exist, degrade gracefully (show available axes only).

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

### Prompt 3.2 — Risk Distribution Histogram

```
The Overview screen in the dashboard (src/shannon_insight/server/app.py, _DASHBOARD_HTML) shows no visualization of how risk is distributed across files. Add a small histogram.

Add a risk distribution chart to the Overview screen, below the category badges on the right column:

1. Compute bins from DATA.files:
   - 5 bins: [0, 0.2), [0.2, 0.4), [0.4, 0.6), [0.6, 0.8), [0.8, 1.0]
   - Count files in each bin using risk_score

2. Render as an SVG bar chart:
   - Horizontal bars (one per bin)
   - Left label: "0.0", "0.2", "0.4", "0.6", "0.8" in monospace 10px
   - Bar width proportional to file count in that bin
   - Bar color: green for 0-0.2, green for 0.2-0.4, yellow for 0.4-0.6, orange for 0.6-0.8, red for 0.8-1.0
   - Right label: file count in monospace 10px
   - Bar height: 12px each, 2px gap between
   - Total chart height: ~80px

3. Title above: "Risk Distribution" in section-head style (11px uppercase text-2)

4. The chart should update on each DATA refresh (call from render()).

5. If no files exist, show nothing (don't render an empty chart).

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

### Prompt 3.3 — Treemap Visualization

```
The existing report.py at src/shannon_insight/visualization/report.py and treemap.py at src/shannon_insight/visualization/treemap.py have a working squarified treemap algorithm. Port the treemap to the live dashboard.

Read these files first:
- src/shannon_insight/visualization/treemap.py (build_treemap_data, _squarify algorithm)
- src/shannon_insight/visualization/report.py (the HTML/JS treemap rendering in _REPORT_TEMPLATE)
- src/shannon_insight/server/app.py (_DASHBOARD_HTML)

The dashboard receives DATA.files which has per-file signals including "lines" and "risk_score".

Add a treemap view to the Files screen as a toggle (table view / treemap view):

1. Add a view toggle above the file table: two small buttons "Table" and "Treemap"
   - Table view is default
   - Treemap fills the same container when active

2. Implement the squarify algorithm in JavaScript (port from treemap.py):
   - Input: array of {path, area (=lines), color_value (=risk_score)}
   - Output: array of {path, x, y, w, h, color_value}
   - Use the same squarification logic from treemap.py _squarify()

3. Render as SVG:
   - Full width of the container, height = 500px
   - Each file is a rectangle with:
     - Fill color from health gradient based on risk_score percentile
     - 1px border in bg-0 color for separation
     - File name (basename only) as text inside if rectangle is large enough (>60px wide and >20px tall)
     - Text: 10px monospace, white, truncated to fit
   - Hover tooltip showing: full path, lines, risk_score, role
   - Click: navigate to #files/<path>

4. Color scale: same healthColor() function, mapping risk_score 0-1 to green-yellow-orange-red

5. The treemap re-renders when DATA updates.

6. Minimum file size for visibility: files with <10 lines are grouped into an "other" bucket.

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

### Prompt 3.4 — SVG Sparklines for File Detail

```
The file detail view in the dashboard needs sparklines to show signal trends over time. This requires both backend and frontend changes.

BACKEND (api.py + watcher.py):

1. Read src/shannon_insight/persistence/queries.py — find the HistoryQuery class and its file_trend() method.

2. In src/shannon_insight/server/api.py, add an optional parameter to build_dashboard_state():
   db_path: str | None = None

   When db_path is not None and the .shannon/history.db file exists:
   - Create a HistoryQuery connection
   - For each file in file_signals, query file_trend(path, "risk_score", last_n=20)
   - Also query file_trend for: cognitive_load, total_changes, churn_cv
   - Add a "trends" dict to each file's data: {"risk_score": [v1, v2, ...], "cognitive_load": [...], ...}
   - Close the connection

3. In src/shannon_insight/server/watcher.py run_analysis(), detect if .shannon/history.db exists:
   db_path = Path(self.root_dir) / ".shannon" / "history.db"
   Pass db_path to build_dashboard_state() if it exists.

FRONTEND (_DASHBOARD_HTML):

4. Add a renderSparkline(values, width, height, color) JS function:
   - Takes an array of numbers, returns an SVG string
   - Width: 80px, height: 20px
   - Draws a polyline connecting the values (normalized to min-max range)
   - Stroke: color parameter, 1.5px
   - Fill: same color at 10% opacity below the line
   - No axes, no labels — just the shape

5. In showFileDetail(), for each stat box (Lines, Risk, Churn, etc.):
   - Check if f.trends exists and has data for that signal
   - If yes, render a sparkline SVG below the stat value
   - If no trends data, show nothing (graceful degradation)

Run: ruff check src/ && python -m pytest tests/server/ -v
```

---

## Phase 4: History and Trends

### Prompt 4.1 — Wire History DB into the API

```
The dashboard needs access to historical trend data from .shannon/history.db. The query methods already exist in src/shannon_insight/persistence/queries.py.

Read these files:
- src/shannon_insight/persistence/queries.py (HistoryQuery class — codebase_health, top_movers, persistent_findings, get_chronic_findings)
- src/shannon_insight/persistence/__init__.py (HistoryDB class)
- src/shannon_insight/server/api.py

Edit api.py build_dashboard_state() to accept an optional db_path parameter.

When db_path is provided and the file exists:

1. Query codebase_health(last_n=20) — returns list of dicts with metric values per snapshot.
   Add to state as "trends": {"health": [...list of {timestamp, health, finding_count} dicts...]}

2. Query top_movers() — returns files with biggest metric changes.
   Add to state["trends"]["movers"]: [...list of {path, metric, old_value, new_value, delta} dicts...]

3. Query persistent_findings(min_count=3) or get_chronic_findings(min_persistence=3).
   Add to state["trends"]["chronic"]: [...list of {finding_type, identity_key, persistence_count, first_seen, files} dicts...]

Wrap all DB queries in try/except — if any query fails, omit that trends key (graceful degradation).

Edit watcher.py run_analysis() to detect .shannon/history.db and pass its path to build_dashboard_state().

Add tests in tests/server/test_api.py:
- test_build_state_without_db: verify trends key is absent when no db_path
- test_build_state_structure_unchanged: verify existing fields still present

Run: ruff check src/shannon_insight/server/ && python -m pytest tests/server/ -v
```

### Prompt 4.2 — Health Trend Line Chart and Chronic Findings

```
The Health screen in the dashboard (src/shannon_insight/server/app.py, _DASHBOARD_HTML) needs a trend line chart and chronic findings panel.

Read the current renderHealth function and #screen-health div.

Add two new sections to the Health screen (above the concern radar):

1. Health Trend Line Chart (only if DATA.trends && DATA.trends.health exists):
   - SVG line chart, full container width, 200px height
   - X-axis: timestamps (render as short dates: "Jan 5", "Jan 12", etc.)
   - Y-axis: health score 1-10 with gridlines at 2, 4, 6, 8
   - Line: 2px stroke, accent color
   - Fill below line: accent at 10% opacity
   - Data points as 4px circles on hover
   - Tooltip on hover showing exact date + health value
   - If only 1 data point, show just the point (no line)
   - Section title: "Health Trend"

2. Top Movers panel (only if DATA.trends && DATA.trends.movers exists):
   - List of files with delta indicators
   - Each row: file path (monospace, clickable to #files/path), delta value
   - Delta shown as: "+0.8" in green or "-1.2" in red, monospace
   - Sorted by absolute delta descending
   - Max 10 items
   - Section title: "Biggest Changes"

3. Chronic Findings panel (only if DATA.trends && DATA.trends.chronic exists):
   - List of findings that persist across 3+ snapshots
   - Each row: finding type label, file(s), "persisting N snapshots" badge
   - Badge: monospace, orange background, small text
   - These should appear at the top of the Issues screen too, marked with a "Chronic" tag
   - Section title: "Chronic Issues"

All sections gracefully hidden when trends data is absent.

Do NOT change any Python code. Only modify _DASHBOARD_HTML.

Run: ruff check src/shannon_insight/server/app.py
```

---

## Phase 5: Watcher Improvements

### Prompt 5.1 — Track Changed Files and Diff

```
The file watcher at src/shannon_insight/server/watcher.py detects changed file paths but discards them. The dashboard should highlight what changed.

Read:
- src/shannon_insight/server/watcher.py
- src/shannon_insight/server/state.py
- src/shannon_insight/server/api.py

Changes needed:

1. state.py — add a recent_changes field:
   - Add to __init__: self._recent_changes: list[str] = []
   - Add method set_recent_changes(paths: list[str])
   - Add method get_recent_changes() -> list[str]

2. watcher.py — pass changed files to state:
   - In _watch_loop(), after detecting changes, call self.state.set_recent_changes(changed_files) before run_analysis()
   - In run_analysis(), after building dashboard_state, add a "recent_changes" key to the state dict with self.state.get_recent_changes()

3. state.py — retain previous state for diff:
   - In update(), save the old state as self._previous_state before replacing
   - Add method get_previous_state() -> dict | None

4. watcher.py — compute deltas:
   - After building new dashboard_state, if state.get_previous_state() exists:
     - Compare file health scores: for each file in both old and new, compute delta
     - Find new findings (in new but not old) and resolved findings (in old but not new)
     - Add "changes" dict to dashboard_state: {"file_deltas": {path: delta_health}, "new_findings": count, "resolved_findings": count}

5. app.py _DASHBOARD_HTML — show changes:
   - On Overview screen, if DATA.recent_changes exists and is non-empty: show a "N files changed" indicator near the stats
   - In the file table, if a file is in DATA.recent_changes, show a small blue dot or "changed" badge next to its path
   - If DATA.changes exists, show new/resolved finding counts on overview

Add a test for the state changes tracking in tests/server/test_state.py.

Run: ruff check src/ && python -m pytest tests/server/ -v
```

### Prompt 5.2 — Determinate Progress Bar

```
The dashboard progress bar is indeterminate (infinite animation). Make it show real progress.

Read:
- src/shannon_insight/server/watcher.py (run_analysis, the on_progress callback)
- src/shannon_insight/server/state.py (send_progress)
- src/shannon_insight/server/app.py (showProgress in _DASHBOARD_HTML)

The kernel calls on_progress with messages like "Scanning files...", "Running StructuralAnalyzer...", "Detecting issues...", "Ranking findings...", "Capturing snapshot...".

1. In watcher.py, create a PHASE_MAP dict that maps known progress messages to percentage:
   "Scanning files...": 0.1
   "Parsing": 0.15
   "Analyzing dependencies...": 0.2
   "Running StructuralAnalyzer...": 0.3
   "Running TemporalAnalyzer...": 0.4
   "Running SpectralAnalyzer...": 0.5
   "Computing signals...": 0.6
   "Running SignalFusionAnalyzer...": 0.65
   "Detecting issues...": 0.75
   "Checking history...": 0.8
   "Ranking findings...": 0.9
   "Capturing snapshot...": 0.95

2. In the on_progress callback, match the message against PHASE_MAP (use startswith for partial matches). Send the percentage via state.send_progress(msg, phase="analyze", percent=pct).

3. In state.py send_progress, add an optional percent parameter. Include it in the broadcast message dict.

4. In _DASHBOARD_HTML showProgress():
   - If msg.percent exists, set the progress bar width to msg.percent * 100 + "%"
   - Remove the infinite animation class when percent is provided
   - Show the percentage text: "65%" next to the message
   - If no percent, fall back to the indeterminate animation

Run: ruff check src/ && python -m pytest tests/server/ -v
```

---

## Phase 6: Export and Integration

### Prompt 6.1 — Export Buttons

```
The dashboard has no way to export data. Add export functionality.

Read src/shannon_insight/server/app.py — both the Python routes and the _DASHBOARD_HTML.

PYTHON (app.py create_app):

1. Add a route GET /api/export/json that returns the current state as a downloadable JSON file:
   - Content-Disposition: attachment; filename="shannon-insight-{timestamp}.json"
   - Same data as /api/state

2. Add a route GET /api/export/csv that returns the file table as CSV:
   - Columns: path, risk_score, total_changes, cognitive_load, blast_radius, finding_count, role, health, lines
   - Content-Disposition: attachment; filename="shannon-insight-files-{timestamp}.csv"
   - Generate CSV from state.get_state()["files"]

HTML (_DASHBOARD_HTML):

3. Add an export dropdown button in the top header bar (right side):
   - Button text: "Export" with a small down-arrow
   - Dropdown options: "JSON", "CSV"
   - JSON links to /api/export/json
   - CSV links to /api/export/csv
   - Style: bg-1 background dropdown, border, 12px text

Run: ruff check src/shannon_insight/server/app.py && python -m pytest tests/server/ -v
```

### Prompt 6.2 — Quality Gate Endpoint

```
Add a quality gate API endpoint for CI integration.

Read:
- src/shannon_insight/server/app.py (create_app, routes)
- src/shannon_insight/server/state.py

Add to app.py create_app():

1. New route GET /api/gate:
   - Reads current state from state.get_state()
   - Computes gate status based on:
     - health >= 4.0 (on 1-10 scale) → PASS threshold
     - No CRITICAL severity findings (severity >= 0.9)
   - Returns JSON: {"status": "PASS"|"FAIL", "health": 7.2, "critical_count": 0, "finding_count": 12, "reason": "Health 7.2, no critical issues"}
   - If health < 4.0: reason = "Health X.X below threshold 4.0"
   - If critical findings: reason = "N critical findings detected"
   - HTTP 200 for PASS, 200 for FAIL (status is in the body, not HTTP code — CI tools parse JSON)
   - If no state yet: return 202 with {"status": "PENDING", "reason": "Analysis in progress"}

Add test in tests/server/test_api.py:
- test_gate_pass: state with health 7.0, no critical findings → PASS
- test_gate_fail_health: state with health 2.0 → FAIL
- test_gate_fail_critical: state with a severity 0.95 finding → FAIL

Document usage in the serve --help description: append "Quality gate: curl -sf localhost:8765/api/gate | jq .status"

Run: ruff check src/ && python -m pytest tests/server/ -v
```

---

## Verification Prompt (run after all phases)

```
Full verification of the shannon-insight dashboard implementation. Run all checks:

1. ruff check src/ tests/
2. ruff format --check src/ tests/
3. python -m mypy src/shannon_insight/server/ src/shannon_insight/cli/serve.py tests/server/ --ignore-missing-imports
4. python -m pytest tests/ -v

5. Verify serve command works:
   shannon-insight . serve --help

6. Verify all API endpoints exist:
   - Start server in background: shannon-insight . serve --no-browser --port 9999 &
   - Wait 30 seconds for initial analysis
   - curl -s localhost:9999/api/state | python -m json.tool | head -20
   - curl -s localhost:9999/api/gate | python -m json.tool
   - curl -s -o /dev/null -w "%{http_code}" localhost:9999/api/export/json
   - curl -s -o /dev/null -w "%{http_code}" localhost:9999/api/export/csv
   - Kill background server

Report any failures with exact error messages.
```
