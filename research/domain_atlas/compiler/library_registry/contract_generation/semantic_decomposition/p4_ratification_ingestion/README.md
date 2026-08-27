# P4 ratification receipt ingestion

P4 is the authority boundary between review-ready research and canonical change. It ingests a
ratification receipt only when a separate external trust provider verifies the same template,
snapshot, payload digest, authorities and exact source, collision, boundary, family, symbol,
family-axis or library-contract scope.

```text
P1B/P2/P3/P5 template
      |
      +--> ratification receipt --------+
      |                                 |
      +--> external authority proof ----+--> verified ledger entry
                                             |
                                             +--> canonical delta candidate
                                                   (still no mutation)
```

The two input ledgers are deliberately empty:

- `ratification-receipts.jsonl`
- `authority-verification-receipts.jsonl`

Consequently all 1,904 templates remain unratified: 877 are ready but lack verified receipts, while
1,027 remain blocked by upstream prerequisites. The verified ledger, refusal
ledger and delta-candidate ledger are empty.

P4 refuses snapshot drift, payload digest mismatch, missing authority verification, insufficient
scope, incomplete P2 occurrence coverage, incomplete P3 cluster/member coverage, incomplete P5
contract dimensions or prerequisite receipts, duplicate template
ratification and attempts to bypass an upstream blocker. Even a fully verified receipt produces only
a content-addressed delta candidate for a separate canonical-change review; this stage cannot mutate
the registry or close a gap.

Run `python3 build_p4.py` and `python3 validate.py`.
