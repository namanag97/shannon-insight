# Registry: Temporal Operators

Time is not a dimension — it is the axis along which all dimensions are measured repeatedly. The full measurement model is:

```
M(dimension, scale, time) → value
```

Every signal in `signals.md` can have these operators applied, producing **second-order signals**. For example: "the velocity of cognitive_load" or "the trajectory of modularity."

## The Two-Dimensional Analysis Model

Analysis is a matrix, not a pipeline:

```
              t₀         t₁         t₂         now
           ┌──────────┬──────────┬──────────┬──────────┐
IR0 Files  │ files₀   │ files₁   │ files₂   │ files₃   │
IR1 Syntax │ syntax₀  │ syntax₁  │ syntax₂  │ syntax₃  │
IR2 Semant │ sem₀     │ sem₁     │ sem₂     │ sem₃     │
IR3 Graph  │ graph₀   │ graph₁   │ graph₂   │ graph₃   │
IR4 Arch   │ arch₀    │ arch₁    │ arch₂    │ arch₃    │
IR5s Sigs  │ sigs₀    │ sigs₁    │ sigs₂    │ sigs₃    │
IR6 Insigh │ ins₀     │ ins₁     │ ins₂     │ ins₃     │
           └──────────┴──────────┴──────────┴──────────┘
```

- Every **cell** is a snapshot.
- Every **row** is a time series (same IR, different time points).
- Every **column** is a full analysis at one time point.
- Every **diagonal** is an evolution question: "how did this file's ROLE change as the GRAPH grew?"

## Three Sources of Temporal Data

### Kind 1: Git-derived (the `temporal/` package)

**Source**: `git log`.
**Produces**: Churn trajectories, co-change lift, author entropy, bus factor, fix ratio.
**Availability**: Always available if git history exists. Covers full project lifetime.
**Scope**: Populates D6 (CHANGE), D7 (AUTHORSHIP), D8 (INTENT) signals.

### Kind 2: Cross-snapshot (the `persistence/` layer)

**Source**: Comparing our own saved analysis snapshots (`.shannon/history.db`).
**Produces**: Delta at every IR level, trend of any signal, sparklines, finding lifecycle.
**Availability**: Only after 2+ `--save` runs. Forward-looking only.
**Scope**: Enables temporal operators on ALL signals, not just D6-D8.

### Kind 3: Historical reconstruction

**Source**: `git show <sha>:<path>` to read files at past commits, then re-run the full pipeline.
**Produces**: The complete matrix — any IR at any past time point.
**Availability**: On demand. Expensive (re-parse every file at each historical commit).
**Scope**: Fills the entire temporal tensor retroactively. Required for CP/Tucker decomposition.

## Operators

For any signal `S(entity, t)` tracked over time points t₀, t₁, ..., tₙ:

### Delta

```
Δ(S, t) = S(t) - S(t-1)
```

What changed in one step. The most basic temporal signal.

### Velocity

```
v(S) = slope of linear_regression(S(t₀), S(t₁), ..., S(tₙ))

Fit S(t) = a + bt via OLS:
  b = (T Σtcₜ - ΣtΣcₜ) / (T Σt² - (Σt)²)
```

Rate of change. Positive = growing. Negative = shrinking.

### Acceleration

```
a(S) = d²S/dt² ≈ v(S, recent_window) - v(S, older_window)
```

Is change speeding up or slowing down?

### Trajectory

```
if Σ S(t) ≤ 1:                              DORMANT
elif velocity < -threshold AND CV < 1:        STABILIZING
elif velocity > threshold AND CV > 0.5:       SPIKING
elif CV > 0.5:                                CHURNING
else:                                         STABLE
```

Qualitative classification. Used for churn_trajectory (D6) but applicable to any signal.

### Volatility

```
volatility(S) = std(S(t₀..tₙ)) / mean(S(t₀..tₙ))    (coefficient of variation)
```

How erratic is this signal? CV > 1 = highly erratic. CV < 0.5 = relatively steady.

### Trend

```
trend(S) = direction of rolling_mean(S, window=3)
→ IMPROVING | STABLE | WORSENING
```

Long-term direction ignoring noise. "Improving" vs "worsening" depends on signal polarity (defined in `signals.md` per signal).

### Seasonality

```
r(lag) = autocorrelation(S(t), S(t + lag))
```

If r(lag = 2 weeks) is high, signal has a fortnightly rhythm (release cycles).

### Stationarity

```
Augmented Dickey-Fuller test on S(t₀..tₙ)
→ STATIONARY (stable process) | NON_STATIONARY (drifting)
```

Is this signal a stable process or is it drifting?

## Which Operators Apply When

Not all operators are meaningful for all signals:

| Signal type | Useful operators |
|---|---|
| Numeric (pagerank, lines, etc.) | All operators |
| Boolean (is_orphan) | Delta only (became orphan / stopped being orphan) |
| Enum (role, trajectory) | Delta only (role changed from X to Y) |
| Ratio [0,1] (stub_ratio, coherence) | Delta, velocity, trend (not CV — bounded range) |

Each signal in `signals.md` lists its applicable temporal operators.

## Second-Order Signals

Temporal operators on signals produce derived signals. These are NOT listed separately in `signals.md` — they are implicit. Any signal with temporal_operators defined in the registry automatically has these derived forms:

```
pagerank                  → the base signal
Δ(pagerank)               → change since last snapshot
velocity(pagerank)        → rate of change
trend(pagerank)           → IMPROVING | STABLE | WORSENING
```

## The Temporal Tensor

The full data is a 3D tensor:

```
T ∈ R^(n × d × t)

where n = entities (files), d = signal dimensions (~50), t = time points
```

**CP decomposition** approximates T as sum of rank-1 tensors, revealing **evolution archetypes**:

```
T ≈ Σᵣ λᵣ (aᵣ ⊗ bᵣ ⊗ cᵣ)

aᵣ ∈ R^n = entity profile (which files)
bᵣ ∈ R^d = signal profile (which signals)
cᵣ ∈ R^t = time profile (what temporal pattern)
```

Each component is a latent factor: "Files A, B, C are becoming more complex and churny over time."

**Tucker decomposition** captures three-way interactions that CP cannot.

CP/Tucker require Kind 3 temporal data (historical reconstruction) to fill the tensor.

## Per-Module Temporal Contract

Every module spec (`modules/*/README.md`) MUST define:

1. **Output at time t**: What this module produces is parameterized by time.
2. **Delta(t₁, t₂)**: The structured diff between two snapshots at this IR level.
3. **Time series**: Which outputs become signals over time.
4. **Reconstruction**: How to produce this module's output for a historical commit.
