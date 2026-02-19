# Level 5: Composite Signals

## Overview

Composites combine signals into interpretable scores on [1, 10] scale.

## Per-File Composites

### raw_risk (pre-percentile, for health Laplacian)
```
raw_risk = 0.25 × norm(pagerank)
         + 0.20 × norm(blast_radius)
         + 0.20 × norm(cognitive_load)
         + 0.20 × min(churn_cv/2, 1)
         + 0.15 × max(0, 1 - bus_factor/5)
```

### risk_score (percentile-based)
```
risk_score = 0.25 × pctl(pagerank)
           + 0.20 × pctl(blast_radius)
           + 0.20 × pctl(cognitive_load)
           + 0.20 × instability_factor
           + 0.15 × (1 - bus_factor/5)
```

### wiring_quality
```
wiring_quality = 1 - (
    0.375 × is_orphan
  + 0.3125 × stub_ratio
  + 0.3125 × phantom_ratio
)
```

### health_score (1-10)
```
health_score = 10 × (1 - 0.40×risk_score - 0.25×(1-wiring) - ...)
```

### delta_h (Health Laplacian)
```
delta_h(v) = raw_risk(v) - mean(raw_risk(neighbors))
           = 0 if orphan
```

## Per-Module Composites

### health_score (1-10)
```
health_score = 0.20 × cohesion
             + 0.15 × (1 - coupling)
             + 0.20 × (1 - main_seq_distance)  # skip if instability=None
             + 0.15 × boundary_alignment
             + 0.15 × role_consistency
             + 0.15 × (1 - mean_stub_ratio)
```

## Global Composites

### codebase_health (1-10)
```
codebase_health = 0.30 × architecture_health
                + 0.30 × wiring_score
                + 0.20 × (bus_factor / team_size)
                + 0.20 × modularity
```

## Normalization Tiers

| Tier | File Count | Strategy |
|------|------------|----------|
| ABSOLUTE | < 15 | Raw values only |
| BAYESIAN | 15-50 | Blend raw + percentile |
| FULL | 50+ | Percentiles |

## Current Implementation

**Files:**
- `src/shannon_insight/signals/composites.py`
- `src/shannon_insight/signals/health_laplacian.py`
- `src/shannon_insight/signals/normalization.py`
