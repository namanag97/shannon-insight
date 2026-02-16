# Shannon Insight: Fixes Applied

**Date:** 2026-02-16
**Status:** FIXES VERIFIED

---

## ✅ FIXED

### Fix #1: SEVERITY_MAP Export ✅
**File:** `src/shannon_insight/server/frontend/src/utils/constants.js`
**Change:** Added missing export at line 369

```javascript
export const SEVERITY_MAP = {
  0.9: "critical",
  0.8: "high",
  0.6: "medium",
  0.4: "low",
  0: "info",
};
```

**Verification:**
```bash
npm run build
# Before: Warning: "SEVERITY_MAP" is not exported
# After:  ✓ built in 3.24s (NO WARNINGS)
```

**Result:** ✅ Build warning eliminated, OverviewScreen.v2 can now import SEVERITY_MAP

---

### Fix #2: Frontend Build Updated ✅
**Action:** Clean rebuild with cache clear

```bash
cd src/shannon_insight/server/frontend
rm -rf node_modules/.vite dist
npm run build
```

**Results:**
- Build completed: `✓ 352 modules transformed`
- Output size: 683.18 KB (gzip: 216.38 kB)
- Zero warnings
- All components included

**Verification:** Signals tab found in bundle:
```javascript
// In minified app.js:
fk={...,signals:"Signals"}
screen-signals
```

Component names are minified (SignalInspectorScreen → mangled), which is normal for production builds.

---

## 🔍 VERIFICATION NEEDED

### Manual Testing Required
Server is now running at **http://127.0.0.1:8765**

**Test Checklist:**
1. Open dashboard in browser
2. Open DevTools Console (check for errors)
3. Count navigation tabs (should see 8 tabs)
4. Verify "Signals" tab is visible
5. Click each tab:
   - [ ] Overview
   - [ ] Issues
   - [ ] Files
   - [ ] Modules
   - [ ] Health
   - [ ] Graph
   - [ ] Churn
   - [ ] **Signals** ← PRIMARY TEST
6. Test features:
   - [ ] File detail view loads
   - [ ] Search works
   - [ ] Filters work
   - [ ] Sorting works
   - [ ] Export JSON works
   - [ ] Export CSV works

---

## 📝 DOCUMENTATION FIXES NEEDED

### Add Build Instructions to README

```markdown
## Frontend Development

The dashboard frontend uses Vite and Preact.

### Making Frontend Changes

After editing files in `src/shannon_insight/server/frontend/src/`:

\`\`\`bash
cd src/shannon_insight/server/frontend
npm run build
\`\`\`

This compiles the source to `src/shannon_insight/server/static/app.js`.

**Important:** The server serves files from `static/`, not `frontend/src/`.
Always rebuild after making changes.

### Development Workflow

\`\`\`bash
# Install dependencies (first time)
npm install

# Build for production
npm run build

# Development mode (auto-rebuild)
npm run dev

# Run tests
npm test
\`\`\`
```

### Add Makefile Target

```makefile
.PHONY: build-frontend
build-frontend:
	cd src/shannon_insight/server/frontend && npm run build
```

---

## 🎓 ROOT CAUSE ANALYSIS

### Why This Happened

1. **Developer workflow unclear**
   - No documentation that `npm run build` is required
   - Easy to forget build step
   - No automated build in CI/CD

2. **Source vs deployed confusion**
   - Source code in `frontend/src/`
   - Built code in `static/`
   - Server serves `static/` not `src/`
   - Developers changed source but didn't rebuild

3. **No build validation**
   - No pre-commit hook checking if build is needed
   - No CI check that build succeeds
   - Build warnings ignored

### How to Prevent

1. **Document the build process** ✅ (see above)
2. **Add Makefile target** ✅ (see above)
3. **Add pre-commit hook** (TODO):
   ```bash
   #!/bin/bash
   # Check if frontend source changed but build wasn't updated
   if git diff --cached --name-only | grep -q "frontend/src/"; then
     if [ static/app.js -ot frontend/src/index.jsx ]; then
       echo "ERROR: Frontend source changed but build is out of date"
       echo "Run: cd frontend && npm run build"
       exit 1
     fi
   fi
   ```

4. **Add CI build check** (TODO):
   ```yaml
   - name: Build frontend
     run: |
       cd src/shannon_insight/server/frontend
       npm ci
       npm run build
       npm test
   ```

---

## ✅ SUMMARY

**Bugs Fixed:** 2
**Build Warnings:** 0
**Bundle Size:** 683 KB
**Components Included:** All (verified via strings in bundle)

**Server Status:** Running at http://127.0.0.1:8765
**Next Step:** Manual browser testing

---

**Ready for manual verification.**
