# Shannon Insight Design System

## Philosophy

**Fictivekin** + **Palantir** + **Jony Ive**: Information-dense typography, analytical rigor, minimalist purposefulness.

Every pixel serves the user's core question: **"What should I fix first?"**

---

## Typography

### Font Stack
- **Sans-serif**: `'Inter', -apple-system, BlinkMacSystemFont, sans-serif`
- **Monospace**: `'JetBrains Mono', 'Fira Code', 'SF Mono', monospace`

### Scale (based on 13px root)
| Token          | Size   | Weight | Use                                |
|----------------|--------|--------|------------------------------------|
| `--text-hero`  | 48px   | 600    | Health score (single instance)     |
| `--text-xl`    | 20px   | 600    | Section headers, detail scores     |
| `--text-lg`    | 16px   | 500    | Metric values, stat numbers        |
| `--text-md`    | 13px   | 400    | Body text (root size)              |
| `--text-sm`    | 12px   | 500    | Table content, nav items           |
| `--text-xs`    | 11px   | 400    | Labels, metadata, badges           |
| `--text-2xs`   | 10px   | 400    | Tertiary labels, hints             |
| `--text-3xs`   | 9px    | 400    | Sparkline labels, axis ticks       |

### Principles
- Mono for **data** (numbers, paths, code, signal values)
- Sans for **prose** (descriptions, labels, interpretations)
- Never bold body text; use weight 500 (medium) for emphasis
- Letter-spacing: `0.5px` for uppercase labels, `0` everywhere else

---

## Spacing

**4px grid system.** All spacing derives from multiples of 4.

| Token         | Value | Use                              |
|---------------|-------|----------------------------------|
| `--space-xs`  | 4px   | Inline gaps, tight padding       |
| `--space-sm`  | 8px   | Component internal padding       |
| `--space-md`  | 16px  | Card padding, section gaps       |
| `--space-lg`  | 24px  | Section margins                  |
| `--space-xl`  | 32px  | Major sections                   |
| `--space-2xl` | 48px  | Page-level vertical rhythm       |

---

## Color Palette

### Backgrounds
| Token             | Hex       | Use                           |
|-------------------|-----------|-------------------------------|
| `--bg`            | `#0a0a0a` | Page background               |
| `--surface`       | `#111111` | Cards, panels                 |
| `--surface-hover` | `#161616` | Interactive surface on hover  |
| `--border`        | `#1e1e1e` | Primary borders               |
| `--border-subtle` | `#181818` | Row separators                |

### Text
| Token              | Hex       | Use                          |
|--------------------|-----------|------------------------------|
| `--text`           | `#e5e5e5` | Primary text                 |
| `--text-secondary` | `#999999` | Secondary labels             |
| `--text-tertiary`  | `#666666` | Hints, disabled              |

### Semantic
| Token      | Hex       | Use                          |
|------------|-----------|------------------------------|
| `--green`  | `#22c55e` | Healthy, resolved, positive  |
| `--yellow` | `#eab308` | Warning, moderate            |
| `--orange` | `#f97316` | High severity, degrading     |
| `--red`    | `#ef4444` | Critical, broken             |
| `--accent` | `#3b82f6` | Links, active states, accent |

### Severity Mapping
- **Critical** (>= 0.9): `--red`
- **High** (>= 0.8): `--orange`
- **Medium** (>= 0.6): `--yellow`
- **Low** (>= 0.4): `--accent`
- **Info** (< 0.4): `--text-tertiary`

---

## Radius

| Token         | Value | Use                       |
|---------------|-------|---------------------------|
| `--radius-sm` | 6px   | Buttons, badges, inputs   |
| `--radius-md` | 10px  | Cards, panels             |
| `--radius-lg` | 14px  | Modal overlays            |

---

## Component Patterns

### Cards
- Background: `--surface`
- Border: 1px solid `--border`
- Radius: `--radius-md`
- Padding: `--space-lg`
- Title: uppercase, letter-spaced, `--text-tertiary`

### Tables
- Monospace for data columns
- Sticky headers (top: 40px to clear topbar)
- Alternating row backgrounds with subtle opacity
- Hover: left accent bar on first cell
- Click: pointer cursor, brighter hover

### Interactive States
- **Default**: Subtle borders, muted colors
- **Hover**: Border brightens, text lightens, optional background shift
- **Active**: Accent color border/text, subtle accent background
- **Focus**: Accent border color (inputs only)

### Transitions
- Duration: `150ms` for most, `200ms` for layout shifts
- Easing: `ease` for most, `ease-out` for entrances

### Empty States
- Centered, with icon and helpful action text
- Always suggest how to populate (e.g., "Run with --save")
- Never leave blank without explanation

### Loading States
- Top progress bar (accent color)
- Skeleton-free: show empty state until data arrives
- Animated dots for pending operations

---

## Navigation Model

### Screen Hierarchy
```
Overview  -->  Quick links to Issues, Files
Issues    -->  Finding detail, file links
Files     -->  File detail, signal categories
Modules   -->  Module detail, file links
Health    -->  Trend data, signal inspector
Graph     -->  Interactive exploration
```

### New Screens
```
Churn Explorer  -->  Timeline view, trajectory filter
Signal Inspector -->  Cross-file signal comparison
```

### Information Flow
1. **Overview**: "What is the state?" (health score, categories, focus point)
2. **Issues**: "What is wrong?" (findings by category, severity)
3. **Files**: "Where specifically?" (file-level risk, signals)
4. **Modules**: "What groups are affected?" (module-level health)
5. **Health**: "How is it trending?" (time series, movers)
6. **Graph**: "How is it connected?" (dependency visualization)
7. **Churn Explorer**: "What is changing?" (temporal patterns)
8. **Signal Inspector**: "What does this signal look like?" (cross-file)

---

## Data Hierarchy

### Level 1: Codebase Summary
Health score, verdict, file count, module count, commit count

### Level 2: Category Breakdown
4 categories (Incomplete, Fragile, Tangled, Team) with counts and severity

### Level 3: Finding Detail
Individual findings with evidence, affected files, suggestions

### Level 4: File Signals
62 signals across 6 categories per file

### Level 5: Temporal Context
Trends, movers, chronic findings, trajectory patterns
