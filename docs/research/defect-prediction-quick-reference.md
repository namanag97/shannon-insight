# Defect Prediction: Quick Reference Guide

**TL;DR**: Mathematical properties that ACTUALLY predict bugs, with thresholds and formulas.

---

## 1. Statistical Reality Check

### What Distribution Do Metrics Follow?

| Metric | Distribution | Implication |
|--------|-------------|-------------|
| Defect count per file | **Power Law** | 80% of defects in 20% of files |
| Complexity (CC, LOC) | **Lognormal** | Use median, not mean |
| File size | **Lognormal** | Long tail is normal |
| Change frequency | **Power Law** | Most files rarely change |
| Churn | **Lognormal** | Multiplicative process |

**CRITICAL**: DO NOT use z-score, mean±2σ, or normal distribution assumptions. Use percentiles and IQR.

---

## 2. Proven Defect Predictors

### Tier 1: Strong Empirical Evidence

| Metric | Threshold | Correlation | Source |
|--------|-----------|-------------|--------|
| **Relative Churn** | > 75th percentile | 89% accuracy | Nagappan & Ball 2005 |
| **Cyclomatic Complexity** | > 10 | Positive correlation | McCabe 1976 |
| **Change Entropy** | High scatter | r = 0.54 | Co-Change Entropy 2024 |
| **Bus Factor** | < 3 | Post-release failures | Git Bus Factor |
| **Socio-Tech Congruence** | Low overlap | Increased failures | Cataldo 2013 |

### Tier 2: Moderate Evidence

| Metric | Threshold | Risk Level |
|--------|-----------|------------|
| **Cognitive Complexity** | > 15 | Moderate |
| **Betweenness Centrality** | > 95th percentile | High (bottleneck) |
| **Temporal Coupling** | Support > 0.3 (no structural edge) | Hidden coupling |
| **Ownership Concentration** | 1 author > 80% lines | Single point of failure |

---

## 3. Threshold Decision Tree

### For Complexity

```
IF cyclomatic_complexity <= 10:
    RISK = LOW
ELIF cyclomatic_complexity <= 15:
    RISK = MODERATE
    ACTION = "Review for splitting"
ELIF cyclomatic_complexity <= 30:
    RISK = HIGH
    ACTION = "Refactor recommended"
ELSE:
    RISK = CRITICAL
    ACTION = "Must refactor"
```

### For Churn

```
relative_churn = total_changes / current_LOC
churn_CV = std_dev(monthly_churn) / mean(monthly_churn)

IF relative_churn > 75th_percentile AND churn_CV >= 0.5:
    RISK = HIGH
    LABEL = "CHURNING"
ELIF relative_churn > 75th_percentile AND churn_CV < 0.5:
    RISK = MODERATE
    LABEL = "STABILIZING"
ELSE:
    RISK = LOW
```

### For Ownership

```
author_entropy = -Σ (p_i × log₂(p_i))
bus_factor = 2^author_entropy

IF bus_factor == 1:
    RISK = CRITICAL
    ACTION = "Knowledge transfer required"
ELIF bus_factor < 3:
    RISK = HIGH
    ACTION = "Increase ownership diversity"
ELIF bus_factor >= 5:
    RISK = LOW
```

### For Centrality

```
IF pagerank > 90th_percentile:
    IF churn > median:
        RISK = CRITICAL
        LABEL = "HIGH_RISK_HUB"
    ELSE:
        RISK = LOW
        LABEL = "STABLE_HUB"
ELSE:
    IF churn > 90th_percentile:
        RISK = HIGH
        LABEL = "WRONG_ABSTRACTION"
```

---

## 4. Outlier Detection

### IQR Method (RECOMMENDED)

```python
def detect_outliers(values):
    Q1 = percentile(values, 25)
    Q3 = percentile(values, 75)
    IQR = Q3 - Q1

    lower_fence = Q1 - 1.5 * IQR
    upper_fence = Q3 + 1.5 * IQR

    outliers = [v for v in values if v < lower_fence or v > upper_fence]
    extreme = [v for v in values if v < Q1 - 3*IQR or v > Q3 + 3*IQR]

    return {
        'moderate_outliers': outliers,
        'extreme_outliers': extreme
    }
```

### When NOT to Use Outlier Detection

- **Small samples** (< 15 files): Use absolute thresholds
- **Expected power law**: Top 20% are "outliers" by definition (use percentile ranking instead)

---

## 5. Composite Scoring

### Hotspot Formula (CodeScene-Inspired)

```python
def hotspot_score(file):
    # Multiplicative, not additive
    change_frequency = percentile_rank(file.total_changes)
    code_health = compute_health(file)

    return change_frequency * (1 - code_health)

def compute_health(file):
    # Normalized 0-1 (0 = worst, 1 = best)
    complexity_health = 1 - min(file.cyclomatic / 30, 1.0)
    coupling_health = 1 - min(file.efferent_coupling / 20, 1.0)
    test_health = file.test_coverage

    return (complexity_health + coupling_health + test_health) / 3
```

### Risk Score (Shannon Insight v2)

```python
def risk_score(file):
    # Only compute for hotspots (change_freq > median)
    if file.total_changes <= median_changes:
        return 0.0

    # Weighted combination
    structural = 0.3 * pagerank_percentile(file)
    temporal = 0.3 * churn_percentile(file)
    coupling = 0.2 * efferent_coupling_percentile(file)
    ownership = 0.2 * (1 - bus_factor_health(file))

    return structural + temporal + coupling + ownership
```

---

## 6. Cross-Dimensional Detection

### Structural-Temporal Mismatch

```python
def detect_mismatch(file):
    structural_risk = percentile(pagerank[file])
    temporal_risk = percentile(churn[file])

    if abs(structural_risk - temporal_risk) > 0.3:
        if structural_risk > temporal_risk:
            return "STABLE_HUB"  # Good
        else:
            return "WRONG_ABSTRACTION"  # Bad
    return "ALIGNED"
```

### Hidden Coupling

```python
def detect_hidden_coupling(file_a, file_b, graph, commits):
    # Temporal coupling
    support = cochange_support(file_a, file_b, commits)

    # Structural coupling
    has_edge = graph.has_edge(file_a, file_b)
    distance = graph.shortest_path(file_a, file_b)

    # Same module?
    same_module = get_module(file_a) == get_module(file_b)

    if support > 0.3 and not has_edge and not same_module:
        return True  # Hidden coupling
    return False
```

### Socio-Technical Congruence

```python
def socio_technical_congruence(file_a, file_b):
    # Technical distance
    tech_distance = dependency_graph.shortest_path(file_a, file_b)

    # Coordination distance (from co-change or co-authorship)
    coord_distance = cochange_graph.shortest_path(file_a, file_b)

    # Mismatch detection
    if tech_distance > 3 and coord_distance < 2:
        return "COORDINATION_OVERHEAD"  # Teams coordinate but no dependency
    elif tech_distance < 2 and coord_distance > 3:
        return "MISSING_COORDINATION"  # Dependency but no coordination
    else:
        return "ALIGNED"
```

---

## 7. Tier-Based Thresholds

### Shannon Insight v2 Strategy

```python
def get_threshold_strategy(codebase_size):
    if codebase_size < 15:
        return ThresholdStrategy.ABSOLUTE
    elif codebase_size < 50:
        return ThresholdStrategy.BAYESIAN
    else:
        return ThresholdStrategy.FULL

class ThresholdStrategy:
    ABSOLUTE = "absolute"  # Fixed thresholds (CC > 15, etc.)
    BAYESIAN = "bayesian"  # Priors + small sample
    FULL = "full"          # Percentile-based
```

### Absolute Thresholds (< 15 files)

```python
ABSOLUTE_THRESHOLDS = {
    'cyclomatic_complexity': 15,
    'cognitive_complexity': 15,
    'function_length': 50,
    'efferent_coupling': 10,
    'afferent_coupling': 10,
    'depth': 5,
}
```

### Percentile Thresholds (50+ files)

```python
PERCENTILE_THRESHOLDS = {
    'high_risk': 90,      # Top 10%
    'moderate_risk': 75,  # Top 25%
    'low_risk': 50,       # Above median
}
```

---

## 8. Entropy Interpretation

### Change Entropy (Process Metric)

```python
def change_entropy(commits, time_window):
    # Group commits by time window
    changes_per_file = count_changes_per_file(commits, time_window)

    # Compute entropy
    total_changes = sum(changes_per_file.values())
    probabilities = [c / total_changes for c in changes_per_file.values()]

    entropy = -sum(p * log2(p) for p in probabilities if p > 0)

    # Interpretation
    if entropy > log2(len(changes_per_file)) * 0.8:
        return "HIGH_SCATTER"  # Bad: changes everywhere
    elif entropy < log2(len(changes_per_file)) * 0.3:
        return "FOCUSED"  # Good: concentrated changes
    else:
        return "MODERATE"
```

### Author Entropy (Ownership)

```python
def author_entropy(file, git_blame):
    # Lines per author
    lines_per_author = count_lines_per_author(file, git_blame)
    total_lines = sum(lines_per_author.values())

    # Compute entropy
    probabilities = [lines / total_lines for lines in lines_per_author.values()]
    entropy = -sum(p * log2(p) for p in probabilities if p > 0)

    # Bus factor
    bus_factor = 2 ** entropy

    return {
        'entropy': entropy,
        'bus_factor': int(bus_factor),
        'interpretation': interpret_ownership(bus_factor)
    }

def interpret_ownership(bus_factor):
    if bus_factor == 1:
        return "CRITICAL: Single owner"
    elif bus_factor < 3:
        return "HIGH_RISK: Low ownership diversity"
    elif bus_factor >= 5:
        return "HEALTHY: Distributed ownership"
    else:
        return "MODERATE: Some ownership concentration"
```

---

## 9. Polarity Reference

### High = Good

| Metric | Interpretation |
|--------|----------------|
| Test coverage | Higher is better |
| Modularity (Q) | Higher is better (> 0.3) |
| Bus factor | Higher is better (≥ 5) |
| Abstractness (for interfaces) | Higher is better |
| Code health | Higher is better |

### High = Bad

| Metric | Interpretation |
|--------|----------------|
| Cyclomatic complexity | Higher is worse (> 10) |
| Churn volatility (CV) | Higher is worse (≥ 0.5) |
| Change entropy (scatter) | Higher is worse |
| Efferent coupling | Higher is worse (God file) |
| Instability (for stable components) | Higher is worse |

### Context-Dependent

| Metric | Good When | Bad When |
|--------|-----------|----------|
| Centrality | Low churn (stable hub) | High churn (risky hub) |
| Entropy (information) | Feature-rich | Chaotic |
| Instability | Interface/plugin (meant to change) | Core library |
| Co-change | Structural coupling exists | No structural coupling |

---

## 10. Common Pitfalls

### ❌ Don't Do This

```python
# DON'T: Assume normal distribution
mean = np.mean(complexities)
std = np.std(complexities)
outliers = [c for c in complexities if c > mean + 2*std]  # WRONG

# DON'T: Simple weighted sum without context
risk = 0.25*complexity + 0.25*churn + 0.25*coupling + 0.25*centrality  # WRONG

# DON'T: Flag all temporal coupling
if cochange_support(A, B) > 0.3:
    flag_as_problem(A, B)  # WRONG (might be expected)

# DON'T: Use z-score on skewed data
z_score = (value - mean) / std  # WRONG for lognormal/power law
```

### ✅ Do This Instead

```python
# DO: Use percentiles
Q1, Q3 = percentile(complexities, [25, 75])
IQR = Q3 - Q1
outliers = [c for c in complexities if c > Q3 + 1.5*IQR]  # CORRECT

# DO: Multiplicative scoring with filtering
if churn > median:
    risk = change_frequency * (1 - code_health)  # CORRECT
else:
    risk = 0  # Not a hotspot

# DO: Check structural coupling before flagging
if cochange_support(A, B) > 0.3 and not has_structural_edge(A, B):
    flag_as_hidden_coupling(A, B)  # CORRECT

# DO: Use percentile ranking
percentile_rank = sum(v <= value for v in values) / len(values)  # CORRECT
```

---

## 11. Formula Cheat Sheet

### Entropy

```
H = -Σ (p_i × log₂(p_i))
where p_i = proportion of category i
```

### Bus Factor

```
Bus Factor = 2^H
where H = author entropy
```

### Gini Coefficient (Inequality)

```
G = (2 × Σ(i × x_i)) / (n × Σx_i) - (n+1)/n
where x_i is sorted ascending, i is 1-indexed
```

### Coefficient of Variation

```
CV = σ / μ
CV < 0.5 → STABILIZING
CV ≥ 0.5 → CHURNING
```

### Modularity (Newman)

```
Q = (1/2m) Σ [A_ij - (k_i × k_j)/2m] × δ(c_i, c_j)
Q > 0.3 → meaningful community structure
```

### Martin Metrics

```
Instability = Ce / (Ca + Ce)
  Ce = efferent coupling (outgoing)
  Ca = afferent coupling (incoming)

Zone of Pain: Instability > 0.7 AND Abstractness < 0.3
```

### IQR Fences

```
Lower fence = Q1 - 1.5 × IQR
Upper fence = Q3 + 1.5 × IQR
Extreme fence = Q1 - 3 × IQR, Q3 + 3 × IQR
```

---

## 12. References for Deep Dive

- **Full Research**: See `mathematical-foundations-of-defects.md`
- **Nagappan & Ball (2005)**: Relative churn metrics (89% accuracy)
- **Co-Change Entropy (2024)**: Process metrics (r=0.54)
- **Cataldo (2013)**: Socio-technical congruence
- **McCabe (1976)**: Cyclomatic complexity thresholds
- **CodeScene**: Hotspot analysis methodology
- **SonarQube**: Cognitive complexity, technical debt formulas

---

**Quick Lookup**: Use Ctrl+F to jump to specific metrics or formulas.
