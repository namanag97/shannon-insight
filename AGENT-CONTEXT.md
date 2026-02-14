# Agent Implementation Context

**CRITICAL: Read this entire document before making ANY changes.**

You are implementing a comprehensive frontend redesign for Shannon Insight dashboard. This is NOT a hack job - every decision must follow the design system and information architecture specifications.

---

## Your Mission

Migrate Shannon Insight frontend from current implementation to the new design system + information architecture WITHOUT breaking functionality.

---

## Core Documents (MUST READ)

1. **DESIGN-SYSTEM.md** - Complete design system reference
   - 12-column grid system
   - 8px baseline spacing
   - Typography scale
   - Component patterns

2. **INFORMATION-ARCHITECTURE.md** - What to show, in what order, why
   - Screen-by-screen specs
   - Priority levels (1-5)
   - Rationale for every decision

3. **IMPLEMENTATION-GUIDE.md** - Step-by-step rollout plan
   - 8-phase migration process
   - Feature flag strategy
   - Testing checklist

4. **OverviewScreen.v2.jsx** - Proof-of-concept reference
   - Shows correct patterns
   - Demonstrates grid usage
   - Example sub-components

---

## Rules You MUST Follow

### ❌ NEVER Do These Things

1. **Don't use arbitrary spacing**
   - ❌ `margin: 23px`, `gap: 15px`, `padding: 27px`
   - ✅ Use design system tokens: `--space-2`, `--space-4`, `--space-6`

2. **Don't create custom grids**
   - ❌ `display: grid; grid-template-columns: 35% 65%;`
   - ✅ Use `.grid` with `.span-*` classes

3. **Don't bypass the design system**
   - ❌ Inline styles for layout
   - ✅ Use design system classes

4. **Don't skip the information architecture**
   - ❌ Keep old layout order "because it works"
   - ✅ Follow priority order from INFORMATION-ARCHITECTURE.md

5. **Don't break existing functionality**
   - ❌ Remove features without asking
   - ✅ Keep all existing features, just reorganize them

6. **Don't hack tests**
   - ❌ Change test assertions to make them pass
   - ✅ Fix the code to satisfy tests

### ✅ ALWAYS Do These Things

1. **Use the grid system**
   ```jsx
   // Always wrap content in .grid
   <div className="grid">
     <div className="span-6">Left</div>
     <div className="span-6">Right</div>
   </div>
   ```

2. **Use spacing tokens**
   ```jsx
   // Use design system spacing
   <div className="mb-12">...</div>  // 48px section break
   <div className="stack stack--md">...</div>  // 16px gaps
   ```

3. **Follow information architecture**
   ```jsx
   // Priority 1 first, Priority 2 second, etc.
   <section>{/* Priority 1: Hero */}</section>
   <section>{/* Priority 2: Action */}</section>
   <section>{/* Priority 3: Context */}</section>
   ```

4. **Use layout components**
   ```jsx
   // Prefer layout components over manual flexbox
   <div className="stack stack--lg">  // Not: display: flex; flex-direction: column; gap: 24px
     <Card />
     <Card />
   </div>
   ```

5. **Test your changes**
   ```bash
   # After every change
   npm run dev
   # Check browser console for errors
   # Test responsive at 768px, 640px
   ```

6. **Preserve functionality**
   ```jsx
   // Keep all existing features
   // Just reorganize layout and styling
   // Don't remove onClick handlers, data flow, etc.
   ```

---

## Design System Quick Reference

### Grid System

```jsx
// 12-column grid with 24px gutters
<div className="grid">
  <div className="span-3">25%</div>
  <div className="span-6">50%</div>
  <div className="span-3">25%</div>
</div>

// Compact grid (16px gutters)
<div className="grid grid--compact">
  <div className="span-4">...</div>
  <div className="span-4">...</div>
  <div className="span-4">...</div>
</div>
```

### Spacing Scale

| Token | Value | Use Case |
|-------|-------|----------|
| `--space-2` | 8px | Baseline - intra-component gaps |
| `--space-4` | 16px | Standard padding |
| `--space-6` | 24px | Component gaps |
| `--space-8` | 32px | Section spacing |
| `--space-12` | 48px | Major section breaks |

```jsx
// Spacing utilities
<div className="mb-12">Section break</div>
<div className="stack stack--md">Vertical stack with 16px gaps</div>
<div className="cluster cluster--sm">Horizontal wrap with 8px gaps</div>
```

### Typography

```jsx
// Display (hero numbers)
<div className="text-display text-mono">{score.toFixed(1)}</div>

// Section headers
<h2 className="text-h2 mb-6">Section Title</h2>

// Card titles
<div className="text-h4 mb-4">Card Title</div>

// Body text
<p className="text-body">Description text</p>

// Labels
<div className="text-label">Metadata label</div>
```

### Cards

```jsx
// Standard card
<div className="ds-card">
  <div className="ds-card__header">
    <div className="ds-card__title">Title</div>
  </div>
  <div className="ds-card__body">
    {/* Content */}
  </div>
</div>

// Compact card
<div className="ds-card ds-card--compact">
  {/* Less padding */}
</div>
```

---

## Information Architecture Patterns

### Priority Levels

Every screen follows this structure:

```jsx
<div className="stack stack--2xl">
  {/* Priority 1: Hero - Answer "What's the status?" */}
  <section>
    <div className="priority-hero">...</div>
  </section>

  {/* Priority 2: Action - Answer "What should I do?" */}
  <section>
    <div className="priority-primary">...</div>
  </section>

  {/* Priority 3: Context - Answer "Why does it matter?" */}
  <section>
    <div className="grid">
      <div className="span-6">...</div>
      <div className="span-6">...</div>
    </div>
  </section>

  {/* Priority 4: Details - Supporting data */}
  <section>...</section>

  {/* Priority 5: Optional - Historical/metadata */}
  <CollapsibleSection>...</CollapsibleSection>
</div>
```

### Overview Screen (Example)

```jsx
// Priority 1: Health Score
<div className="grid">
  <div className="span-12">
    <div className="priority-hero">
      <div className="text-display">{score}</div>
    </div>
  </div>
</div>

// Priority 2: Focus Point
<div className="grid">
  <div className="span-12">
    <div className="priority-primary">
      <div className="text-h4">🎯 RECOMMENDED STARTING POINT</div>
      <FocusPoint />
    </div>
  </div>
</div>

// Priority 3: Risk + Issues
<div className="grid">
  <div className="span-6">
    <div className="ds-card">
      <RiskHistogram />
    </div>
  </div>
  <div className="span-6">
    <div className="ds-card">
      <TopIssues />
    </div>
  </div>
</div>
```

---

## Implementation Checklist

Before considering a screen "done":

- [ ] Imports `design-system.css`
- [ ] Uses `.grid` with `.span-*` for all layouts
- [ ] All spacing uses design system tokens (no arbitrary values)
- [ ] Follows information architecture priority order
- [ ] Typography uses `.text-*` classes
- [ ] Cards use `.ds-card` variants
- [ ] Responsive at 768px and 640px breakpoints
- [ ] No console errors
- [ ] No broken functionality
- [ ] Tested with real data from shannon-insight

---

## Common Patterns

### Metric Display

```jsx
<div className="ds-card ds-card--compact text-center">
  <div className="text-2xl text-mono">{value}</div>
  <div className="text-label mt-1">{label}</div>
</div>
```

### Two-Column Layout

```jsx
<div className="grid">
  <div className="span-6">
    <div className="ds-card">Left content</div>
  </div>
  <div className="span-6">
    <div className="ds-card">Right content</div>
  </div>
</div>
```

### Vertical Stack

```jsx
<div className="stack stack--md">
  <Card />
  <Card />
  <Card />
</div>
```

### Horizontal Cluster (Tags/Badges)

```jsx
<div className="cluster cluster--sm">
  <Badge />
  <Badge />
  <Badge />
</div>
```

---

## Testing Protocol

After implementing each component:

1. **Visual Check**
   ```bash
   npm run dev
   # Open http://localhost:5173
   # Check layout looks correct
   ```

2. **Responsive Check**
   ```
   # Browser DevTools
   # Test at 1440px (desktop)
   # Test at 768px (tablet)
   # Test at 640px (mobile)
   ```

3. **Console Check**
   ```
   # Browser DevTools Console
   # Should have NO errors
   # Should have NO warnings about missing props
   ```

4. **Functionality Check**
   ```
   # Click all interactive elements
   # Verify navigation works
   # Verify data displays correctly
   # Verify sorting/filtering works
   ```

5. **Grid Check**
   ```
   # Browser DevTools Elements tab
   # Verify .grid classes present
   # Verify .span-* classes correct
   # Verify no custom grid-template-columns
   ```

---

## Anti-Patterns to Avoid

### ❌ Don't do this:

```jsx
// Arbitrary spacing
<div style={{ marginBottom: '27px' }}>

// Custom grid
<div style={{ display: 'grid', gridTemplateColumns: '35% 65%' }}>

// Inline layout
<div style={{ display: 'flex', gap: '20px' }}>

// Arbitrary font sizes
<div style={{ fontSize: '17px' }}>

// Tool-first UX
<div>
  <SearchBar />
  <Filters />
  <DataTable />  {/* Insights buried below tools */}
</div>
```

### ✅ Do this instead:

```jsx
// Design system spacing
<div className="mb-8">  {/* 32px */}

// Design system grid
<div className="grid">
  <div className="span-4">...</div>
  <div className="span-8">...</div>
</div>

// Layout component
<div className="cluster cluster--md">

// Typography class
<div className="text-lg">

// Insight-first UX
<div>
  <TopInsights />
  <SearchBar />
  <Filters />
  <DataTable />
</div>
```

---

## File Structure

```
src/shannon_insight/server/frontend/src/
├── styles/
│   ├── design-system.css      ← Design system (NEW)
│   └── style.css              ← Old styles (keep for now)
├── components/
│   ├── screens/
│   │   ├── OverviewScreen.jsx      ← MIGRATE THIS
│   │   ├── OverviewScreen.v2.jsx   ← REFERENCE (already done)
│   │   ├── IssuesScreen.jsx        ← MIGRATE THIS
│   │   ├── FilesScreen.jsx         ← MIGRATE THIS (delegates to FileListView)
│   │   ├── ModulesScreen.jsx       ← MIGRATE THIS
│   │   ├── HealthScreen.jsx        ← MIGRATE THIS
│   │   └── files/
│   │       ├── FileListView.jsx    ← MIGRATE THIS
│   │       └── FileDetailView.jsx  ← MIGRATE THIS
│   ├── cards/          ← May need updates
│   ├── charts/         ← Keep as-is
│   └── ui/             ← Keep as-is
└── state/
    └── store.js        ← May need feature flags
```

---

## Questions to Ask Yourself

Before making a change, ask:

1. **Does this use the grid system?**
   - If no: Why not? Rewrite to use `.grid`.

2. **Is this spacing intentional?**
   - If arbitrary: Replace with design system token.

3. **What's the priority level?**
   - If unclear: Check INFORMATION-ARCHITECTURE.md.

4. **Am I breaking functionality?**
   - If yes: Don't do it. Preserve all features.

5. **Would a new developer understand this?**
   - If no: Add comments, use semantic classes.

---

## Success Criteria

A migration is successful when:

- ✅ Uses design system classes (grid, spacing, typography)
- ✅ Follows information architecture (priority order)
- ✅ Zero arbitrary values (all spacing is `--space-*`)
- ✅ Responsive (works at 768px, 640px)
- ✅ No console errors
- ✅ All features work exactly as before
- ✅ Code is cleaner and more maintainable

---

## Getting Help

If stuck:

1. Check **DESIGN-SYSTEM.md** for patterns
2. Look at **OverviewScreen.v2.jsx** for examples
3. Read **INFORMATION-ARCHITECTURE.md** for layout rationale
4. Follow **IMPLEMENTATION-GUIDE.md** step-by-step

**Remember:** This is a professional refactor. Take your time. Do it right. Every pixel, every spacing value, every layout decision must be intentional.
