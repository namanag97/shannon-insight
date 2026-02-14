# Shannon Insight Frontend

Preact-based dashboard UI with Zustand state management.

## For Developers

### Setup
```bash
npm install
```

### Development (Hot Reload)
```bash
npm run dev
# Opens at http://localhost:5173
```

### Production Build
```bash
npm run build
# Outputs to: ../static/app.js (23.76 KB gzipped)
```

### Testing
```bash
npm test
```

## For PyPI Packaging

**IMPORTANT:** The frontend must be built BEFORE packaging for PyPI.

### Workflow
```bash
# From project root:
make build-frontend  # Builds frontend
make package         # Builds PyPI package (includes built frontend)
```

### What Gets Packaged
```
shannon-codebase-insight/
├── shannon_insight/
│   └── server/
│       ├── static/
│       │   ├── app.js      ← Built bundle (INCLUDED in PyPI)
│       │   └── style.css   ← Styles (INCLUDED in PyPI)
│       └── templates/
│           └── index.html  ← HTML shell (INCLUDED in PyPI)
```

**NOT included:** `frontend/src/`, `frontend/node_modules/`, `frontend/package.json`

## Architecture

### Component Hierarchy
```
App.jsx (root)
├── Header.jsx
├── ProgressBar.jsx
├── KeyboardOverlay.jsx
└── Screens:
    ├── OverviewScreen.jsx
    ├── IssuesScreen.jsx
    ├── FilesScreen.jsx
    │   ├── FileListView.jsx
    │   └── FileDetailView.jsx
    ├── ModulesScreen.jsx
    └── HealthScreen.jsx
        └── TrendChart.jsx (reusable)
```

### State Management
- **Zustand store** (`state/store.js`) - Single source of truth
- **No global variables** - All state flows through store
- **Actions**: `setData()`, `setCurrentScreen()`, `setConnectionStatus()`, etc.

### Styling
- **CSS Variables** - Consistent spacing, colors
- **Global styles** - `../static/style.css` (782 lines)
- **Design system**: `--space-{xs,sm,md,lg,xl}`, `--radius-{sm,md,lg}`

### Key Components
| Component | Purpose | Reusable |
|-----------|---------|----------|
| TrendChart | Line chart with axes, tooltips | ✅ Yes |
| Sparkline | Simple line chart | ✅ Yes |
| RadarChart | Spider chart | ✅ Yes |
| Treemap | Hierarchical visualization | ✅ Yes |
| FindingCard | Finding display | ✅ Yes |
| Badge | Label badges | ✅ Yes |
| SortableTable | Sortable data table | ✅ Yes |

## User Installation

Users get the **pre-built** frontend via PyPI:

```bash
pip install shannon-codebase-insight
shannon-insight .
# Dashboard opens at http://localhost:8765
```

**No npm required for end users!**

## Bundle Size

- **Raw:** 71.07 KB
- **Gzipped:** 23.76 KB
- **Target:** < 100 KB ✅

## Testing

- 33 component tests
- Run with: `npm test`
- Coverage: Unit tests for utils, hooks, components
