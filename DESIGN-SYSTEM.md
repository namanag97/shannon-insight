# Shannon Insight Design System

**A comprehensive design system for data-dense dashboard UIs.**

Built on mathematical precision with an 8px baseline grid and 12-column layout system. Every spacing decision, every component size, every typography choice is intentional and follows strict rules.

---

## Design Principles

1. **Mathematical Precision** - All spacing is multiples of 8px. No arbitrary values.
2. **Grid-Based Layout** - Components snap to a 12-column grid with 24px gutters.
3. **Clear Hierarchy** - Visual weight directly correlates to information priority.
4. **Intentional Spacing** - Every gap has a reason (intra-component, inter-component, section break).
5. **Responsive by Design** - Graceful degradation from desktop → tablet → mobile.

---

## 1. Grid System

### 12-Column Grid

The foundation of all layouts. Components use `.span-*` classes to occupy grid columns.

```jsx
<div className="grid">
  <div className="span-8">Main content (8 columns)</div>
  <div className="span-4">Sidebar (4 columns)</div>
</div>
```

**Common Patterns:**

| Layout | Columns | Use Case |
|--------|---------|----------|
| Full width | `span-12` | Hero sections, full-width tables |
| Two-column | `span-6` + `span-6` | Side-by-side cards |
| 2:1 split | `span-8` + `span-4` | Main content + sidebar |
| Three-column | `span-4` × 3 | Metric cards, stat strips |
| Four-column | `span-3` × 4 | Dense stat grids |

### Grid Variants

```css
.grid              /* Standard 24px gutters */
.grid--compact     /* 16px gutters (dense layouts) */
.grid--dense       /* 8px gutters (metric grids) */
.grid--flush       /* No gutters (seamless tiles) */
```

### Breakpoints

- **Desktop:** 12-column grid, 24px gutters
- **Tablet (≤768px):** 6-column grid, 16px gutters
- **Mobile (≤640px):** 1-column stack, 16px gutters

**Responsive Example:**

```jsx
{/* Desktop: 3 columns, Tablet: 3 columns, Mobile: stack */}
<div className="grid">
  <div className="span-4">Card 1</div>
  <div className="span-4">Card 2</div>
  <div className="span-4">Card 3</div>
</div>
```

---

## 2. Spacing Scale (8px Baseline)

**Every spacing value is a multiple of 8px.** This creates vertical rhythm and visual consistency.

| Token | Value | Use Case |
|-------|-------|----------|
| `--space-1` | 4px | Micro gaps (icon spacing, badge padding) |
| `--space-2` | 8px | **Baseline unit** - minimum spacing |
| `--space-3` | 12px | Compact padding (buttons, chips) |
| `--space-4` | 16px | Standard padding (cards, inputs) |
| `--space-6` | 24px | Component gaps (between cards) |
| `--space-8` | 32px | Section spacing (between major groups) |
| `--space-12` | 48px | Major section breaks |
| `--space-16` | 64px | Screen section breaks |

### Spacing Rules

**Intra-component spacing** (inside cards, between elements in a component):
- Use `--space-2` (8px) or `--space-4` (16px)
- Example: Padding inside a card, gap between icon and text

**Inter-component spacing** (between cards, between sections):
- Use `--space-6` (24px) or `--space-8` (32px)
- Example: Gap between two cards in a grid

**Section breaks** (between major page sections):
- Use `--space-12` (48px) or `--space-16` (64px)
- Example: Space between hero and content area

### Layout Components vs. Utilities

**Prefer layout components** over spacing utilities:

```jsx
// ✅ GOOD - Use layout components
<div className="stack stack--md">
  <Card />
  <Card />
</div>

// ❌ AVOID - Spacing utilities on every element
<Card className="mb-4" />
<Card className="mb-4" />
```

**Layout components:**
- `.stack` - Vertical stack with consistent gaps
- `.cluster` - Horizontal row with wrapping
- `.grid` - 12-column grid

---

## 3. Typography Scale

### Type Hierarchy

| Class | Size | Weight | Use Case |
|-------|------|--------|----------|
| `.text-display` | 56px | 600 | Health score, hero metrics |
| `.text-h1` | 32px | 600 | Page titles |
| `.text-h2` | 24px | 600 | Section headers |
| `.text-h3` | 20px | 600 | Subsection headers |
| `.text-h4` | 11px | 600 | Card titles (uppercase) |
| `.text-body` | 13px | 400 | Body text, table cells |
| `.text-body-sm` | 11px | 400 | Secondary text |
| `.text-label` | 10px | 400 | Captions, metadata |

### Font Families

- **Sans-serif:** Inter (body text, UI elements)
- **Monospace:** JetBrains Mono (metrics, code, file paths)

### Usage Examples

```jsx
{/* Hero metric */}
<div className="text-display text-mono" style={{ color: hColor(score) }}>
  {score.toFixed(1)}
</div>

{/* Section header */}
<h2 className="text-h2 mb-4">Issues by Category</h2>

{/* Card title */}
<div className="text-h4 mb-4">Recommended Starting Point</div>

{/* Metric value */}
<div className="text-2xl text-mono">{fmtN(data.file_count)}</div>

{/* Label */}
<div className="text-label">Files Analyzed</div>
```

---

## 4. Component Sizing

Components use standardized heights based on 16px baseline:

| Token | Value | Use Case |
|-------|-------|----------|
| `--height-sm` | 32px | Buttons, inputs, chips |
| `--height-md` | 40px | Large buttons, nav items |
| `--component-xs` | 48px | Compact stat cards |
| `--component-sm` | 80px | Mini charts |
| `--component-md` | 160px | Standard card min-height |
| `--component-lg` | 240px | Chart cards |
| `--component-xl` | 320px | Hero sections |

---

## 5. Card Components

### Base Card

All cards use the `.ds-card` class for consistent styling:

```jsx
<div className="ds-card">
  <div className="ds-card__header">
    <div className="ds-card__title">Card Title</div>
  </div>
  <div className="ds-card__body">
    {/* Card content */}
  </div>
</div>
```

### Card Variants

```css
.ds-card              /* Standard padding (24px) */
.ds-card--compact     /* Compact padding (16px) */
.ds-card--spacious    /* Spacious padding (32px) */
.ds-card--bordered    /* Thicker 2px border */
```

---

## 6. Visual Hierarchy Patterns

### Priority System

Use priority classes to establish information hierarchy:

```jsx
{/* Priority 1: Hero (Health Score) */}
<div className="priority-hero">
  7.2
</div>

{/* Priority 2: Primary Action (Focus Point) */}
<div className="priority-primary">
  <h3>Recommended Starting Point</h3>
  <p>Fix auth_service.py first...</p>
</div>

{/* Priority 3: Section Headers */}
<div className="priority-secondary">
  Issues by Category
</div>

{/* Priority 4: Card Titles */}
<div className="priority-tertiary">
  Risk Distribution
</div>
```

**Rule:** Never use more than 3 priority levels on a single screen.

---

## 7. Layout Patterns

### Stack Layout (Vertical)

Use for vertical spacing inside cards or sections:

```jsx
<div className="stack stack--md">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

**Variants:**
- `.stack--xs` - 4px gaps
- `.stack--sm` - 8px gaps
- `.stack--md` - 16px gaps (most common)
- `.stack--lg` - 24px gaps
- `.stack--xl` - 32px gaps

### Cluster Layout (Horizontal)

Use for horizontal groups with wrapping (tags, filters, badges):

```jsx
<div className="cluster cluster--sm">
  <Badge>Tag 1</Badge>
  <Badge>Tag 2</Badge>
  <Badge>Tag 3</Badge>
</div>
```

### Sidebar Layout

Two-column layout with fixed sidebar width:

```jsx
<div className="sidebar-layout">
  <aside>Sidebar (240px)</aside>
  <main>Main content (fluid)</main>
</div>
```

**Variants:**
- `.sidebar-layout` - 240px sidebar
- `.sidebar-layout--wide` - 320px sidebar
- `.sidebar-layout--narrow` - 200px sidebar

---

## 8. Migration Guide

### Step 1: Import Design System

```jsx
// In your main index.jsx
import './styles/design-system.css';
```

### Step 2: Replace Arbitrary Spacing

**Before:**
```jsx
<div style={{ marginBottom: '24px' }}>...</div>
```

**After:**
```jsx
<div className="mb-6">...</div>  {/* mb-6 = 24px */}
```

### Step 3: Use Grid for Layouts

**Before:**
```jsx
<div className="overview-cols">  {/* grid-template-columns: 1fr 1fr */}
  <div>...</div>
  <div>...</div>
</div>
```

**After:**
```jsx
<div className="grid">
  <div className="span-6">...</div>
  <div className="span-6">...</div>
</div>
```

### Step 4: Adopt Layout Components

**Before:**
```jsx
<div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
  <Card />
  <Card />
</div>
```

**After:**
```jsx
<div className="stack stack--md">
  <Card />
  <Card />
</div>
```

---

## 9. Examples

### Overview Screen Hero (Redesigned)

```jsx
{/* Hero section - Priority 1 */}
<div className="grid mb-12">
  <div className="span-12">
    <div className="priority-hero">
      <div className="text-label mb-2">CODEBASE HEALTH</div>
      <div className="text-display text-mono" style={{ color: hColor(score) }}>
        {score.toFixed(1)}
      </div>
      <div className="text-h3 mt-2" style={{ color: hColor(score) }}>
        {healthInfo.label}
      </div>
      <div className="text-body-sm text-secondary mt-2">
        {healthInfo.description}
      </div>
    </div>
  </div>
</div>

{/* Focus Point - Priority 2 */}
<div className="grid mb-12">
  <div className="span-12">
    <div className="priority-primary">
      <div className="text-h4 mb-4">🎯 RECOMMENDED STARTING POINT</div>
      <FocusPoint focus={data.focus} />
    </div>
  </div>
</div>

{/* Risk + Issues - Priority 3 */}
<div className="grid mb-8">
  <div className="span-6">
    <div className="ds-card">
      <div className="ds-card__title">Risk Distribution</div>
      <RiskHistogram files={data.files} />
    </div>
  </div>
  <div className="span-6">
    <div className="ds-card">
      <div className="ds-card__title">Top Issues</div>
      {/* Top 5 critical issues */}
    </div>
  </div>
</div>
```

### Stat Strip (4 Metrics)

```jsx
<div className="grid grid--compact mb-8">
  <div className="span-3">
    <div className="ds-card ds-card--compact text-center">
      <div className="text-2xl text-mono">{fmtN(data.file_count)}</div>
      <div className="text-label mt-1">Files Analyzed</div>
    </div>
  </div>
  <div className="span-3">
    <div className="ds-card ds-card--compact text-center">
      <div className="text-2xl text-mono">{fmtN(data.module_count)}</div>
      <div className="text-label mt-1">Modules</div>
    </div>
  </div>
  {/* ... 2 more cards */}
</div>
```

---

## 10. Rules & Guidelines

### Do's ✅

- **Always use grid classes** for multi-column layouts
- **Use layout components** (stack, cluster) for consistent spacing
- **Stick to the spacing scale** - only use defined tokens
- **Use typography classes** instead of inline font sizes
- **Follow priority hierarchy** - max 3 levels per screen
- **Test responsive behavior** at 768px and 640px breakpoints

### Don'ts ❌

- **Don't use arbitrary spacing** (`margin: 27px`, `gap: 13px`)
- **Don't mix spacing contexts** (don't use `--space-12` inside a card)
- **Don't create custom grids** - use the 12-column system
- **Don't skip the grid** - even single-column layouts use `.grid .span-12`
- **Don't use more than 4 visual priority levels**
- **Don't add responsive breakpoints** without design system approval

---

## 11. Component Checklist

Before building/refactoring a component, ask:

1. **Grid:** Does this component use `.grid` with proper `.span-*` classes?
2. **Spacing:** Are all gaps using defined spacing tokens (`--space-*`)?
3. **Typography:** Are text sizes using `.text-*` classes?
4. **Hierarchy:** Is the visual weight appropriate for the information priority?
5. **Layout:** Am I using `.stack`/`.cluster` instead of manual flexbox?
6. **Responsive:** Does this degrade gracefully on tablet and mobile?

---

## Questions?

This design system is **living documentation**. As we build, we'll discover edge cases and add patterns. The goal: **every component follows the same mathematical rigor, every spacing decision is intentional, every layout is grid-based.**

Next step: Apply this system to the Overview screen as a proof-of-concept.
