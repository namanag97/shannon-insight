# Output UX Theory: Why "Focus Point First" is Correct

## The Problem We're Solving

When a developer runs `shannon-insight`, they have one of three questions:

1. **Status check**: "Is my codebase healthy?"
2. **Action question**: "What should I work on next?"
3. **Exploration**: "What patterns exist in my codebase?"

v0.4.0 answered question #2 directly: ranked file list, #1 is your answer.
v0.7.0 answers questions #1 and #3, but forces users to compute #2 themselves.

**The regression**: We made users do cognitive work that the tool should do.

---

## Theoretical Foundation

### 1. Attention is Scarce, Decisions are Expensive

From cognitive psychology (Kahneman's "Thinking Fast and Slow"):
- **System 1** (fast): Pattern recognition, scanning lists
- **System 2** (slow): Deliberate reasoning, comparing options, making decisions

When v0.7.0 outputs "47 findings in 6 categories," it hands the user a System 2 task:
"Synthesize these 47 findings, weight them by severity/impact, and decide what's most important."

When v0.4.0 output "#1: persistence/models.py", it handed the user a System 1 task:
"Here's the answer. Scan to verify it makes sense."

**Principle**: A tool's job is to convert System 2 tasks into System 1 tasks.

### 2. The Paradox of Choice (Barry Schwartz)

Research shows that more options → worse decisions + lower satisfaction.
- 47 findings = choice paralysis
- 1 focus point + 5 alternatives = actionable

This isn't about "dumbing down." It's about respecting that attention is finite.

### 3. Progressive Disclosure (Don Norman)

Show the minimum information needed for the current decision, with details available on demand.

```
Level 0: Verdict        "Your codebase is at risk"
Level 1: Focus          "Start with persistence/models.py"
Level 2: Alternatives   "Also consider: cli/tui.py, signals/fusion.py"
Level 3: Context        "Broader patterns: coupling issues, architecture debt"
Level 4: Raw data       "--verbose" or "explain <file>" for full evidence
```

Each level answers the question raised by the previous level:
- L0 → "What's at risk?"
- L1 → "What else might be important?"
- L2 → "What's the bigger picture?"
- L3 → "Show me the evidence"

### 4. The Hierarchy of Tool Value

```
MOST VALUABLE    Decision:      "Work on X"
      ↓          Priority:      "These 5 are highest risk"
      ↓          Categorization:"You have coupling + architecture issues"
LEAST VALUABLE   Raw data:      "Here are 62 signals per file"
```

v0.7.0 is strong at categorization and raw data.
v0.7.0 is weak at decision and priority.

The fix: Add the top two levels without removing the bottom two.

### 5. How Senior Engineers Communicate

When a senior engineer reviews a codebase, they don't say:
> "You have 3 layer violations, 17 coupling issues, and 9 review blindspots."

They say:
> "The main thing I'd look at is persistence/models.py — it's highly connected,
> frequently changing, and has some complexity issues. After that, cli/tui.py
> is similar but less severe. The broader pattern I'm seeing is coupling
> between your persistence and CLI layers."

This is: **Focus → Alternatives → Context**

---

## The Focus Point Formula

The "focus point" should be the file with the highest **actionability score**:

```
actionability = risk × impact × tractability × confidence
```

Where:
- **risk**: How likely is this to cause problems? (risk_score, findings count)
- **impact**: How much does this file affect? (pagerank, blast_radius)
- **tractability**: Can a developer actually do something? (not orphan, not external)
- **confidence**: How reliable is our measurement? (has git history, has structure)

This is NOT just the highest risk_score file. A file with risk=0.95 but zero dependents is less actionable than a file with risk=0.7 that has 50 dependents.

### Computing Actionability

```python
def actionability(f: FileSignals, finding_count: int) -> float:
    # Risk: composite of churn, complexity, findings
    risk = f.risk_score * 0.5 + min(finding_count / 5, 1.0) * 0.5

    # Impact: how much does fixing this help the codebase?
    # High pagerank + high blast radius = high leverage
    impact = (f.pagerank + f.blast_radius_size / 50) / 2

    # Tractability: can we actually do something?
    # Orphans are low tractability (might be intentional)
    # Very large files are harder to change
    tractability = 1.0
    if f.is_orphan:
        tractability *= 0.5  # Might be intentional
    if f.lines > 1000:
        tractability *= 0.8  # Harder to refactor

    # Confidence: do we have good data?
    confidence = 1.0
    if f.total_changes == 0:
        confidence *= 0.7  # No temporal data

    return risk * impact * tractability * confidence
```

---

## The Output Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ VERDICT: One-line health status                                 │
├─────────────────────────────────────────────────────────────────┤
│ FOCUS POINT                                                     │
│   The single most actionable file                               │
│   WHY: The signals that make this #1                            │
│   WHAT: The specific findings on this file                      │
├─────────────────────────────────────────────────────────────────┤
│ ALSO CONSIDER (4 more files)                                    │
│   Ranked alternatives if user disagrees with #1                 │
├─────────────────────────────────────────────────────────────────┤
│ PATTERNS (optional, collapsed by default)                       │
│   Broader codebase patterns for context                         │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Order?

1. **Verdict first**: Answers "should I care?" before investing attention
2. **Focus point second**: Answers "what should I do?" immediately
3. **Alternatives third**: Provides escape hatch if #1 isn't right
4. **Patterns last**: Context for understanding, not for deciding

---

## Objections and Responses

### "But what if the #1 file isn't actually most important?"

That's what the alternatives section is for. We're not hiding information — we're ordering it by actionability. The user can always disagree and pick #2 or #3.

### "But developers need to understand the patterns, not just fix files"

Yes, and they can:
- Use `--verbose` to see patterns
- Use `--concerns` to see the category view
- Use the TUI to explore
- Use `explain <file>` to drill into any file

The default output answers the most common question. Power users have options.

### "But some findings are codebase-level, not file-level"

True. The focus point is for file-level action. Codebase-level findings (flat_architecture, high cycle_count) appear in the Patterns section with appropriate framing.

### "But what if there are no high-risk files?"

Then the verdict is positive and the focus point section says:
> "No critical hotspots detected. Lowest-health file is X (still healthy)."

This is still useful — it confirms the codebase is in good shape.

---

## Success Metrics

The new output succeeds if:

1. **Time to decision drops**: User knows what to do within 5 seconds of output
2. **Scroll depth drops**: Most users don't need to scroll past the focus point
3. **"What should I do?" questions drop**: The output answers this proactively
4. **Perceived usefulness increases**: Users feel the tool made a recommendation

---

## Implementation Notes

1. **Compute actionability score** using the formula above
2. **Select focus point** as max(actionability)
3. **Select alternatives** as top 5 by actionability (excluding focus)
4. **Render in order**: Verdict → Focus → Alternatives → Patterns
5. **Make patterns collapsible** or behind `--verbose`

The key insight: we're not removing information, we're reordering it by actionability.
