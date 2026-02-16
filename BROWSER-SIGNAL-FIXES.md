# Browser & Signal Inspector Fixes

## Summary

Fixed two UX issues with the Shannon Insight server:

1. **Browser Tab Reuse**: Server no longer opens a new tab on every reconnect
2. **Signal Completeness**: Signal Inspector now dynamically discovers ALL signals from data

## Changes Made

### 1. Browser Tab Management (`src/shannon_insight/server/lifecycle.py`)

**Problem**: Line 202 was opening a new browser tab every time the script was run, even when reconnecting to an existing server.

**Fix**: Removed `webbrowser.open(url)` call on reconnect. Now:
- ✅ **First launch**: Opens browser automatically (line 263)
- ✅ **Reconnect**: Just prints URL, no new tab
- ✅ **User tip**: Added helpful message to navigate to existing URL

**Code Change**:
```python
# BEFORE: Opened browser on reconnect
if existing is not None:
    url = f"http://{host}:{existing.port}"
    console.print(...)
    if not no_browser:
        webbrowser.open(url)  # ❌ Opens new tab every time
    return

# AFTER: No browser on reconnect
if existing is not None:
    url = f"http://{host}:{existing.port}"
    console.print(...)
    console.print("[dim]Tip: Server is already running. Navigate to the URL above.[/dim]")
    return  # ✅ No new tab
```

### 2. Signal Inspector Completeness (`src/shannon_insight/server/frontend/src/components/screens/SignalInspectorScreen.jsx`)

**Problem**: The Signal Inspector dropdown was hardcoded from `constants.js`. If the backend sent signals not in that list, they wouldn't appear.

**Fixes Applied**:

#### a) Dynamic Signal Discovery
- Now scans actual data to find ALL numeric/boolean signals
- Merges hardcoded signals from `constants.js` with discovered signals
- Creates a "Discovered Signals" category for undocumented signals

**Code**:
```javascript
function getInspectableSignals(data) {
  // 1. Start with known signals from constants.js
  const known = new Set();
  const signals = [];

  for (const cat of SIGNAL_CATEGORIES) {
    for (const sig of cat.signals) {
      known.add(sig);
      signals.push({ key: sig, label: SIGNAL_LABELS[sig] || sig, category: cat.name });
    }
  }

  // 2. Discover additional signals from actual data
  if (data && data.files) {
    for (const path in data.files) {
      const f = data.files[path];
      const sigs = f.signals || {};

      // Check both f.signals and top-level fields
      for (const sig of Object.keys(sigs)) {
        if (!known.has(sig)) {
          // Add to "Discovered Signals" category
        }
      }
    }
  }

  return signals;
}
```

#### b) Visual Warning for Undocumented Signals
- Yellow banner appears when discovered signals are found
- Lists all undocumented signals
- Suggests adding them to `constants.js`

**Screenshot Preview**:
```
⚠️ 3 undocumented signals discovered: foo_metric, bar_score, baz_ratio
These signals exist in the data but are not defined in constants.js.
Consider adding them with proper labels and descriptions.
```

#### c) Console Logging (Development Mode)
- Logs discovered signals to browser console on localhost
- Format: `[Signal Inspector] Found 3 undocumented signals: ["foo", "bar", "baz"]`
- Only runs in development (localhost check)

#### d) Dynamic Dropdown Rendering
- Dropdown now groups signals by category dynamically
- Handles both hardcoded categories and "Discovered Signals"
- Preserves original signal ordering within categories

## How to Verify

### Test 1: Browser Tab Reuse

```bash
# Terminal 1: Start server
cd /path/to/your/project
shannon-insight serve

# Expected: Browser opens to http://127.0.0.1:8765

# Terminal 2: Try to start again (while server running)
shannon-insight serve

# Expected: No new browser tab, just message:
# "Dashboard -> http://127.0.0.1:8765 (already running, PID 12345)"
# "Tip: Server is already running. Navigate to the URL above."
```

### Test 2: Signal Completeness

```bash
# 1. Start the server
shannon-insight serve

# 2. Open browser to http://127.0.0.1:8765

# 3. Navigate to "Signals" screen

# 4. Open dropdown - you should see:
#    - All hardcoded signals from constants.js (organized by category)
#    - "Discovered Signals" section (if any backend signals aren't in constants.js)
#    - Yellow warning banner if discovered signals exist

# 5. Open browser console (F12) - you should see:
#    [Signal Inspector] Found N undocumented signals: [...]
```

### Test 3: All Signals Are Inspectable

To verify EVERY signal is accessible:

1. Open the dashboard
2. Go to Files screen → click any file
3. Look at the signals table in the detail panel
4. Note all signal names
5. Go to Signals screen
6. Verify ALL signals from step 3 appear in the dropdown

If any are missing:
- Check the yellow banner for "Discovered Signals"
- Check browser console for logged undocumented signals
- Add them to `src/shannon_insight/server/frontend/src/utils/constants.js`

## Adding New Signals to constants.js

If you see discovered signals, add them properly:

```javascript
// In constants.js

// 1. Add label
export const SIGNAL_LABELS = {
  // ...existing...
  new_signal_name: "Human Readable Label",
};

// 2. Add description
export const SIGNAL_DESCRIPTIONS = {
  // ...existing...
  new_signal_name: "What this signal measures and what values mean",
};

// 3. Add to appropriate category
export const SIGNAL_CATEGORIES = [
  {
    key: "appropriate_category",
    name: "Category Name",
    signals: [
      // ...existing signals...
      "new_signal_name",
    ],
  },
  // ...
];

// 4. Add polarity (optional, for color coding)
export const SIGNAL_POLARITY = {
  // true = higher is WORSE (red)
  // false = higher is BETTER (green)
  // null = NEUTRAL (context-dependent)
  new_signal_name: true,  // or false or null
};
```

## Rebuild Frontend

After modifying any `.jsx` files:

```bash
make build-frontend
```

This compiles JSX → `src/shannon_insight/server/static/app.js`

## Files Modified

1. `src/shannon_insight/server/lifecycle.py` (lines 193-203)
2. `src/shannon_insight/server/frontend/src/components/screens/SignalInspectorScreen.jsx` (complete rewrite of discovery logic)

## Notes

- The "Discovered Signals" feature is a **safety net**, not a long-term solution
- Ideally, all signals should be documented in `constants.js`
- The yellow warning banner encourages proper documentation
- Development console logging helps identify missing signals during development

## Benefits

1. **Better UX**: No more tab spam when reconnecting to server
2. **Robustness**: Frontend won't silently drop signals anymore
3. **Discoverability**: Developers see when `constants.js` is incomplete
4. **Debugging**: Console logs make it easy to track down undocumented signals
5. **Backwards Compatible**: Existing signals still work exactly the same
