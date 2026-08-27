# P1B foundation authority adjudication

P1B makes four previously implicit P5 prerequisites independently attestable:

```text
23 source-authority decisions
        |
146 cross-owner collision decisions
        |
460 bounded-context boundary decisions (covering 674 libraries exactly once)
        |
23 family constitutions + 368 family-axis decisions
        v
exact library contract authoring
```

The graph is dependency-ordered, not bulk-approved. A source authority cannot decide SAN semantic
ownership. One context owner cannot resolve another context's collision. A family constitution
cannot erase library exceptions or absorb shared-symbol meaning.

P1B emits 652 snapshot-bound ratification templates:

- 23 source-authority templates are structurally ready for named-authority review;
- 146 collision templates are ready for the affected context owners;
- 358 boundary templates have no collision prerequisite and are review-ready;
- 102 boundary templates wait for collision decisions;
- all 23 family-constitution templates wait for source, boundary, collision and sixteen-axis receipts.

Therefore 527 templates are review-ready and 125 are blocked. Every selected decision and receipt
remains empty; ratified decisions and canonical mutations remain zero.

Run `python3 build_p1b.py` and `python3 validate.py`.
