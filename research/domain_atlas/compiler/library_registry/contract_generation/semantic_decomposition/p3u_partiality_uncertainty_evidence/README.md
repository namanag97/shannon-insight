# P3U partiality/uncertainty evidence campaign

This campaign supplies one bounded primary-source evidence candidate and one
negative twin for every family targeted on the `partiality_and_uncertainty`
semantic axis. The five family dockets route all 73 family-library occurrences
from the live targeted-evidence work packages.

The campaign does **not** choose family defaults, decide member applicability,
assign semantic owners, write exact contracts, qualify implementations or close
canonical gaps. Every candidate remains unratified and every docket preserves
those residual decisions explicitly.

The sources show why one optional carrier or `Unknown` value would be false.
The campaign keeps at least these distinctions open for adjudication:

- absent, null, unbound, invalid, failed and unknown;
- unknown truth versus unknown completion versus stale observation;
- point estimate, distribution, quantile, interval and simulated path;
- statistical uncertainty versus missing-data reason and model inadequacy;
- virtual relation definition versus evaluation-time result and materialized state;
- partial updateability versus partial visibility and incomplete result sets;
- temporally undefined position versus absent occurrence and unobserved position;
- exact, approximate and lossy results with different error contracts.

Build and validate:

```text
python3 build_p3u.py
python3 validate.py
```

The shared `axis_evidence_campaign.py` module owns only deterministic campaign
mechanics. Evidence meaning, uncertainty carriers, propagation rules,
applicability, owners, exceptions and acceptance remain local and independently
reviewable.
