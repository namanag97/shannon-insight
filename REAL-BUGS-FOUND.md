# Shannon Insight: REAL Bugs Found (Systematic Audit)

**Date:** 2026-02-16 13:50
**Method:** Actual testing + build verification
**Status:** IN PROGRESS

---

## 🔴 CRITICAL BUGS (Confirmed)

### BUG-001: SEVERITY_MAP Not Exported ✅ CONFIRMED
**File:** `src/shannon_insight/server/frontend/src/utils/constants.js`
**Impact:** Build warning, OverviewScreen.v2 cannot import it
**Evidence:**
```
vite build output:
"SEVERITY_MAP" is not exported by "src/utils/constants.js",
imported by "src/components/screens/OverviewScreen.v2.jsx".
```
**Severity:** CRITICAL
**Fix Required:** Add to constants.js:
```javascript
export const SEVERITY_MAP = {
  0.9: 'critical',
  0.8: 'high',
  0.6: 'medium',
  0.4: 'low',
  0: 'info'
};
```

### BUG-002: Frontend Build Outdated ✅ CONFIRMED
**Impact:** Missing features in production (Signals tab invisible)
**Evidence:**
- Before rebuild: 639KB app.js, 0 occurrences of "SignalInspectorScreen"
- After rebuild: 683KB app.js (size changed = code updated)
**Root Cause:** `npm run build` not run after code changes
**Severity:** HIGH
**Fix:** Document build requirement in README:
```bash
cd src/shannon_insight/server/frontend
npm run build  # REQUIRED after any frontend code changes
```

---

## 🟠 HIGH SEVERITY BUGS (To Verify)

### BUG-003: Signals Tab Missing from Navigation
**Status:** TESTING NOW - rebuild completed, checking if it appears
**Expected:** Should see "Signals" tab in header after rebuild
**If Still Missing:** Additional CSS or JS issue

### BUG-004: Missing Build Step in Development Workflow
**Impact:** Developers change frontend/src but don't rebuild → users see old code
**Fix:** Add to Makefile:
```makefile
build-frontend:
	cd src/shannon_insight/server/frontend && npm run build
```

---

## 📋 SYSTEMATIC TEST CHECKLIST

### Build & Deploy ✅
- [x] Frontend source exists (frontend/src/)
- [x] Build script exists (npm run build)
- [x] Build produces static files (static/app.js, static/style.css)
- [x] Server serves static files (/static/)
- [x] Build warnings logged (SEVERITY_MAP warning)
- [ ] Build warnings fixed
- [ ] Server restarted with new build

### Navigation Tabs (After Rebuild)
- [ ] Overview tab visible
- [ ] Issues tab visible
- [ ] Files tab visible
- [ ] Modules tab visible
- [ ] Health tab visible
- [ ] Graph tab visible
- [ ] Churn tab visible
- [ ] **Signals tab visible** ← TESTING THIS NOW

### Screens Actually Load
- [ ] Overview screen renders
- [ ] Issues screen renders
- [ ] Files screen renders
- [ ] Modules screen renders
- [ ] Health screen renders
- [ ] Graph screen renders
- [ ] Churn screen renders
- [ ] Signals screen renders

### Features Work
- [ ] WebSocket connects
- [ ] Real-time updates work
- [ ] Navigation between screens works
- [ ] File detail view works
- [ ] Search works
- [ ] Filters work
- [ ] Sorting works
- [ ] Export JSON works
- [ ] Export CSV works

---

## 🔍 INVESTIGATION NOTES

### Build Process
1. Source: `src/shannon_insight/server/frontend/src/`
2. Build tool: Vite
3. Output: `src/shannon_insight/server/static/`
4. Command: `npm run build` (from frontend dir)
5. Server: Serves `/static/` from `server/static/`

### Build Warning Analysis
```
"SEVERITY_MAP" is not exported by "src/utils/constants.js"
```
This means:
- OverviewScreen.v2.jsx imports SEVERITY_MAP
- constants.js does NOT export it
- Build continues anyway (warning, not error)
- **Result:** OverviewScreen.v2 will crash at runtime when it tries to use SEVERITY_MAP

### What SEVERITY_MAP Should Be
Looking at usage in OverviewScreen.v2.jsx, it likely maps severity numbers to labels:
```javascript
// Probable usage:
const label = SEVERITY_MAP[finding.severity]; // e.g., SEVERITY_MAP[0.95] = "critical"
```

Need to check:
1. How it's actually used in OverviewScreen.v2
2. What the correct mapping should be
3. Add proper export

---

## ⏭️ NEXT STEPS

1. ✅ Rebuild frontend (DONE)
2. ⏳ Restart server
3. ⏳ Open http://127.0.0.1:8765
4. ⏳ Check if Signals tab appears
5. ⏳ Click Signals tab
6. ⏳ Verify it loads
7. ⏳ Click all other tabs
8. ⏳ Test all features
9. ⏳ Fix SEVERITY_MAP export
10. ⏳ Rebuild again
11. ⏳ Final verification

---

## 📝 LESSONS LEARNED

1. **Code review ≠ Functional testing**
2. **Always run the actual build**
3. **Always check what's actually being served**
4. **Build warnings matter**
5. **Frontend bundlers can hide bugs**
6. **Source code ≠ Deployed code**

---

**Status:** Waiting for server restart to verify Signals tab fix
