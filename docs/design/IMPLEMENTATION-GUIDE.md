# Implementation Guide: Frontend Redesign Rollout

**Systematic rollout of the new design system and information architecture.**

This guide provides a step-by-step plan to migrate Shannon Insight's frontend from the current implementation to the redesigned system WITHOUT breaking production.

---

## Overview

We have built:

1. **Design System** (`src/styles/design-system.css`) - Grid, spacing, typography, components
2. **Information Architecture** (documented in `INFORMATION-ARCHITECTURE.md`) - What to show, in what order
3. **Proof-of-Concept** (`OverviewScreen.v2.jsx`) - Redesigned Overview screen

**Strategy:** Parallel implementation → A/B test → Gradual rollout → Full migration

---

## Phase 1: Setup & Integration (1-2 hours)

### Step 1.1: Import Design System

**File:** `src/shannon_insight/server/frontend/src/index.jsx`

```jsx
import './styles/design-system.css';  // ADD THIS LINE
import './index.css';  // Keep existing styles for now
```

**Why:** Design system classes are now available globally. Old CSS still works - no breaking changes.

### Step 1.2: Verify No Conflicts

```bash
cd src/shannon_insight/server/frontend
npm run dev
```

**Check:**
- App still renders correctly
- No console errors
- Existing styles unchanged

**If conflicts arise:** Design system uses prefixed classes (`.ds-*`, `.grid`, `.span-*`) - they won't clash with existing styles.

---

## Phase 2: Migrate Overview Screen (2-4 hours)

### Step 2.1: Create Feature Flag

**File:** `src/shannon_insight/server/frontend/src/state/store.js`

```js
// Add to state
useNewOverview: false,  // Feature flag

// Add action
toggleNewOverview: () => set((state) => ({ useNewOverview: !state.useNewOverview })),
```

### Step 2.2: Conditionally Render New Overview

**File:** `src/shannon_insight/server/frontend/src/components/core/App.jsx`

```jsx
import { OverviewScreen } from "../screens/OverviewScreen.jsx";
import { OverviewScreenV2 } from "../screens/OverviewScreen.v2.jsx";  // ADD

export function App() {
  const useNewOverview = useStore((s) => s.useNewOverview);  // ADD

  return (
    <>
      {/* ... */}
      <div class={`screen${currentScreen === "overview" ? " active" : ""}`}>
        {currentScreen === "overview" && (
          useNewOverview ? <OverviewScreenV2 /> : <OverviewScreen />
        )}
      </div>
      {/* ... */}
    </>
  );
}
```

### Step 2.3: Add Toggle Button (Dev Only)

**File:** `src/shannon_insight/server/frontend/src/components/core/Header.jsx`

```jsx
// In development only
{process.env.NODE_ENV === 'development' && (
  <button
    onClick={() => useStore.getState().toggleNewOverview()}
    style={{
      padding: '4px 8px',
      fontSize: '10px',
      fontFamily: 'var(--font-mono)',
      background: 'var(--accent)',
      color: 'white',
      border: 'none',
      borderRadius: 'var(--radius-sm)',
      cursor: 'pointer'
    }}
  >
    Toggle v2
  </button>
)}
```

### Step 2.4: Test Both Versions

```bash
npm run dev
```

**Test:**
1. Load Overview screen (v1 by default)
2. Click "Toggle v2" button
3. Verify v2 renders correctly with new layout
4. Toggle back to v1
5. Compare layouts side-by-side

### Step 2.5: Fix Bugs in v2

**Common issues:**
- Missing data fields (handle gracefully with optional chaining)
- Color function imports (ensure `hColor` works)
- Missing React import for `useState` (already added)
- Chart component compatibility

**Test with real data:**
```bash
# Terminal 1: Run server on a real codebase
cd /path/to/your/project
shannon-insight serve .

# Terminal 2: Check browser console for errors
```

---

## Phase 3: Polish & Test (1-2 hours)

### Step 3.1: Responsive Testing

**Test at breakpoints:**
- Desktop (1440px) ✓
- Laptop (1280px) ✓
- Tablet (768px) - Should see 6-column grid
- Mobile (640px) - Should stack vertically

**Fix issues:**
```css
/* Add to OverviewScreen.v2.jsx specific overrides if needed */
@media (max-width: 768px) {
  .priority-hero {
    font-size: var(--text-4xl);  /* Smaller on tablet */
  }
}
```

### Step 3.2: Accessibility Audit

**Check:**
- [ ] Keyboard navigation works (Tab through elements)
- [ ] Focus states visible (blue outline on focused elements)
- [ ] Color contrast meets WCAG AA (use browser DevTools)
- [ ] Screen reader compatibility (aria labels where needed)

### Step 3.3: Performance Check

**Metrics to verify:**
- [ ] No layout shift when v2 loads
- [ ] Grid doesn't cause horizontal scroll
- [ ] Charts render smoothly
- [ ] No unnecessary re-renders (check React DevTools Profiler)

---

## Phase 4: Rollout Decision (Review Meeting)

### Prepare Comparison

**Create side-by-side screenshots:**

| Aspect | v1 (Current) | v2 (Redesigned) |
|--------|--------------|-----------------|
| **Information Priority** | Evolution charts dominate | Health score → Focus point → Risk |
| **Grid System** | Ad-hoc 2-column | 12-column mathematical grid |
| **Spacing** | Inconsistent (mix of 24px/32px) | 8px baseline, consistent |
| **Visual Hierarchy** | Everything same weight | Clear priority 1-5 |
| **Actionability** | Focus point buried | Focus point priority #2 |

### Decision Criteria

**Ship v2 if:**
- [ ] No regressions in functionality
- [ ] Responsive design works on all screens
- [ ] Performance is equal or better
- [ ] Team agrees on improved UX
- [ ] All critical bugs fixed

**Rollback to v1 if:**
- [ ] Major bugs discovered
- [ ] Performance degradation
- [ ] Negative user feedback (if testing with users)

---

## Phase 5: Production Deployment

### Step 5.1: Make v2 Default

**File:** `src/shannon_insight/server/frontend/src/state/store.js`

```js
// Change default value
useNewOverview: true,  // v2 is now default
```

### Step 5.2: Keep Rollback Option

**Keep both implementations for 1-2 releases:**
- Users can toggle back to v1 if they prefer (add UI toggle in settings)
- Monitor for bug reports
- After stable period, remove v1 code

### Step 5.3: Deploy

```bash
# Build production bundle
cd src/shannon_insight/server/frontend
npm run build

# Copy to static/
cp dist/app.js ../static/
cp dist/style.css ../static/

# Test production build locally
cd ../../../..
shannon-insight serve .
```

**Verify:**
- [ ] Production build works
- [ ] No console errors
- [ ] Assets load correctly
- [ ] Performance acceptable

---

## Phase 6: Migrate Remaining Screens (Iterative)

**Priority order:**

1. **Issues Screen** (High impact) - 4-6 hours
   - Implement severity summary bar
   - Collapse high/medium findings by default
   - Move tools below insights

2. **Files Screen** (High impact) - 4-6 hours
   - Add summary cards (high/medium/low risk counts)
   - Add "Top 10 Files" section
   - Move search below insights
   - Group table by risk tier

3. **Modules Screen** (Medium impact) - 2-4 hours
   - Add summary metrics
   - Add "Top 5 Problem Modules"
   - Apply grid system

4. **Health Screen** (Medium impact) - 2-4 hours
   - Make trend chart larger
   - Add movers/chronic sections
   - Apply grid system

5. **Graph Screen** (Low priority) - No changes needed
   - Current implementation is solid

### Per-Screen Migration Checklist

For each screen:

1. **Read the info architecture spec** (`INFORMATION-ARCHITECTURE.md`)
2. **Create `.v2.jsx` version** (parallel implementation)
3. **Add feature flag** to store
4. **Conditionally render** in App.jsx
5. **Test with real data**
6. **Fix bugs**
7. **Get review approval**
8. **Make v2 default**
9. **Monitor for issues**
10. **Remove v1 after stable period**

---

## Phase 7: Cleanup (After All Screens Migrated)

### Step 7.1: Remove Old CSS

**File:** `src/shannon_insight/server/frontend/src/styles/style.css` (or whatever the old file is)

**Strategy:**
1. Identify unused classes (use browser DevTools coverage tool)
2. Remove incrementally, test after each removal
3. Keep only styles that can't be replaced by design system

**Goal:** Reduce CSS from ~1400 lines to ~500 lines (design system handles the rest)

### Step 7.2: Remove Feature Flags

```js
// Remove from store.js
useNewOverview: true,  // DELETE THIS (always use v2)
toggleNewOverview: () => ...,  // DELETE THIS

// Simplify App.jsx
<div class="screen">
  {currentScreen === "overview" && <OverviewScreen />}  // Just OverviewScreen (v2 renamed)
</div>
```

### Step 7.3: Rename Files

```bash
# Remove old versions
rm OverviewScreen.jsx  # (old v1)
mv OverviewScreen.v2.jsx OverviewScreen.jsx  # v2 becomes the main version

# Repeat for all screens
```

---

## Phase 8: Documentation Update

### Step 8.1: Update README

**Add to project README:**

```markdown
## Frontend Architecture

Shannon Insight uses a comprehensive design system built on:
- **12-column grid** with 24px gutters
- **8px baseline** spacing scale
- **Mathematical precision** - all spacing is intentional
- **Clear information hierarchy** - priority-based layouts

See [DESIGN-SYSTEM.md](./DESIGN-SYSTEM.md) for full documentation.
```

### Step 8.2: Component Documentation

For each major component, add a header comment:

```jsx
/**
 * OverviewScreen - Dashboard landing page
 *
 * Information Priority:
 * 1. Health Score (hero)
 * 2. Focus Point (what to fix first)
 * 3. Risk + Top Issues (context)
 * 4. Metrics + Categories (supporting data)
 * 5. Evolution (historical, collapsible)
 *
 * Grid: Uses 12-column grid with span-6, span-12 layouts
 * Spacing: 8px baseline (stack--md, mb-12, etc.)
 */
```

---

## Rollback Plan (Emergency)

**If major issues discovered after v2 deploy:**

### Immediate Rollback (5 minutes)

```js
// In store.js
useNewOverview: false,  // Flip back to v1
```

Re-deploy. Done.

### Permanent Rollback (If v2 fundamentally flawed)

```bash
# Revert commits
git revert <commit-sha>

# Or delete v2 files
rm src/components/screens/*.v2.jsx
rm src/styles/design-system.css
```

**Why parallel implementation is smart:** Zero-downtime rollback.

---

## Success Metrics

After full migration, measure:

1. **Code Quality**
   - [ ] CSS reduced by 50%+ (fewer custom styles)
   - [ ] Component consistency (all use grid/spacing system)
   - [ ] No more arbitrary spacing values

2. **User Experience**
   - [ ] Faster task completion (users find critical info faster)
   - [ ] Reduced cognitive load (clear hierarchy)
   - [ ] Better mobile experience (responsive design)

3. **Developer Experience**
   - [ ] Faster feature development (reuse design system)
   - [ ] Fewer design decisions (system provides guardrails)
   - [ ] Easier onboarding (documented patterns)

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 1. Setup | 1-2 hours | None |
| 2. Migrate Overview | 2-4 hours | Phase 1 |
| 3. Polish & Test | 1-2 hours | Phase 2 |
| 4. Review | 1 hour | Phase 3 |
| 5. Deploy | 1 hour | Phase 4 |
| 6. Migrate Others | 16-24 hours | Phase 5 (iterative) |
| 7. Cleanup | 2-4 hours | Phase 6 |
| 8. Documentation | 2 hours | Phase 7 |

**Total:** ~26-38 hours of focused work (3-5 days)

**Recommended:** Do 1 screen per day, test thoroughly between each.

---

## Questions & Edge Cases

### Q: What if the design system doesn't fit a specific use case?

**A:** Extend the design system, don't bypass it.

```css
/* Add to design-system.css */
.span-7 { grid-column: span 7; }  /* If you need 7 columns */

/* Don't do this: */
<div style="width: 58.33%">  /* Breaks the system */
```

### Q: What if old styles conflict with new design system?

**A:** Use CSS specificity or scope old styles.

```css
/* Option 1: Increase specificity */
.legacy-screen .ds-card { /* override */ }

/* Option 2: Rename old classes */
.old-card { ... }  /* Keep until migration done */
```

### Q: Can I mix old and new styles during migration?

**A:** Yes, but only temporarily. A screen should be fully migrated before moving to the next.

---

## Final Checklist

Before declaring migration complete:

- [ ] All 5 screens using design system
- [ ] No arbitrary spacing values in components
- [ ] All layouts using grid system
- [ ] Responsive design tested at all breakpoints
- [ ] Old CSS removed or scoped
- [ ] Feature flags removed
- [ ] Documentation updated
- [ ] Team trained on design system
- [ ] Design system is documented and discoverable

---

**The goal:** Every component follows the same mathematical rigor. Every spacing decision is intentional. Every layout is grid-based. No exceptions.

This is how you build a professional, maintainable, scalable dashboard frontend.
