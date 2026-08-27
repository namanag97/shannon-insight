# Bridging Attractor Discovery to Neuro-Symbolic Learning

## How Mahima's Work Can Actually Solve LossFunk's Problem

---

## The Gap (Reminder)

**LossFunk's Question:**
> "How to enable deep networks to learn and use symbolic abstractions WITHOUT sacrificing their subsymbolic/vector space knowledge?"

**Mahima's Current Proposal:**
> "Discover and study symbolic attractors in frozen neural networks"

**Problem:** Analysis ≠ Solution

---

## The Key Insight: From Discovery to Training

Mahima's method DISCOVERS attractors. But attractors can be used as:

1. **Training Targets** - "This is what a good symbol looks like"
2. **Symbolic Vocabulary** - "These are the symbols we want networks to learn"
3. **Quality Metrics** - "Is this network learning good symbols?"
4. **Curriculum** - "Learn simple symbols first, then complex ones"

---

## Proposed Framework: Attractor-Guided Neuro-Symbolic Learning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   PHASE 1: DISCOVERY (Mahima's work)                                       │
│   ══════════════════════════════                                            │
│                                                                             │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │                                                                  │     │
│   │   Frozen Pre-trained Models (SDXL, CLIP, etc.)                  │     │
│   │                         │                                        │     │
│   │                         ▼                                        │     │
│   │   ┌─────────────────────────────────────────────────────────┐   │     │
│   │   │  Attractor Discovery (MAP-Elites + Observers)           │   │     │
│   │   │                                                         │   │     │
│   │   │  Find:                                                  │   │     │
│   │   │  • Stable attractors (robust to noise)                  │   │     │
│   │   │  • Universal attractors (across architectures)          │   │     │
│   │   │  • Disentangled attractors (cleanly accessible)         │   │     │
│   │   │                                                         │   │     │
│   │   └─────────────────────────────────────────────────────────┘   │     │
│   │                         │                                        │     │
│   │                         ▼                                        │     │
│   │   ┌─────────────────────────────────────────────────────────┐   │     │
│   │   │  Symbolic Vocabulary (Output of Phase 1)                │   │     │
│   │   │                                                         │   │     │
│   │   │  For concept "dog":                                    │   │     │
│   │   │  • A₁ = attractor at {complexity: low, purity: high}   │   │     │
│   │   │  • A₂ = attractor at {complexity: med, purity: med}    │   │     │
│   │   │  • A₃ = attractor at {complexity: high, purity: low}   │   │     │
│   │   │  • ...                                                  │   │     │
│   │   │                                                         │   │     │
│   │   │  Each attractor = a latent vector z + properties        │   │     │
│   │   │                                                         │   │     │
│   │   └─────────────────────────────────────────────────────────┘   │     │
│   │                                                                  │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│   OUTPUT: Dictionary of {concept → attractors}                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ This becomes INPUT to Phase 2
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   PHASE 2: TRAINING (New contribution)                                     │
│   ══════════════════════════════                                            │
│                                                                             │
│   Goal: Train NEW networks to REPRODUCE these attractors                   │
│                                                                             │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │                                                                  │     │
│   │   New Network (to be trained)                                   │     │
│   │                         │                                        │     │
│   │                         ▼                                        │     │
│   │   ┌─────────────────────────────────────────────────────────┐   │     │
│   │   │  Forward Pass                                           │   │     │
│   │   │                                                         │   │     │
│   │   │  Input x → Network f(x; θ) → Representation h(x)        │   │     │
│   │   │                                                         │   │     │
│   │   └─────────────────────────────────────────────────────────┘   │     │
│   │                         │                                        │     │
│   │                         ▼                                        │     │
│   │   ┌─────────────────────────────────────────────────────────┐   │     │
│   │   │  Attractor Matching Loss                                │   │     │
│   │   │                                                         │   │     │
│   │   │  L_attractor = Distance(h(x), attractor_for_label(y))   │   │     │
│   │   │                                                         │   │     │
│   │   │  Where:                                                 │   │     │
│   │   │  • y = label (e.g., "dog")                             │   │     │
│   │   │  • attractor_for_label(y) comes from Phase 1           │   │     │
│   │   │                                                         │   │     │
│   │   └─────────────────────────────────────────────────────────┘   │     │
│   │                         │                                        │     │
│   │                         ▼                                        │     │
│   │   ┌─────────────────────────────────────────────────────────┐   │     │
│   │   │  Properties Loss (from Observers)                       │   │     │
│   │   │                                                         │   │     │
│   │   │  L_properties = λ₁ · L_stability +                     │   │     │
│   │   │                  λ₂ · L_universality +                  │   │     │
│   │   │                  λ₃ · L_disentanglement                 │   │     │
│   │   │                                                         │   │     │
│   │   │  These encourage the NEW network to learn:              │   │     │
│   │   │  • Stable representations                              │   │     │
│   │   │  • Universal representations                            │   │     │
│   │   │  • Disentangled representations                         │   │     │
│   │   │                                                         │   │     │
│   │   └─────────────────────────────────────────────────────────┘   │     │
│   │                         │                                        │     │
│   │                         ▼                                        │     │
│   │   ┌─────────────────────────────────────────────────────────┐   │     │
│   │   │  Total Loss                                             │   │     │
│   │   │                                                         │   │     │
│   │   │  L_total = L_task + α · L_attractor + β · L_properties │   │     │
│   │   │                                                         │   │     │
│   │   │  Where:                                                 │   │     │
│   │   │  L_task = standard task loss (classification, etc.)    │   │     │
│   │   │                                                         │   │     │
│   │   └─────────────────────────────────────────────────────────┘   │     │
│   │                                                                  │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│   OUTPUT: Network that learns symbolic representations                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Mathematical Formulation

### Step 1: Formalize Attractors

**Definition:** An attractor A for concept c is:

```
A_c = (z_c, P_c)

where:
z_c = latent vector that triggers concept c
P_c = properties {stability, universality, disentanglement}
```

**From Mahima's method:**
```
A_c = argmax_z  [ α · stability(z) + 
                 β · universality(z) + 
                 γ · disentanglement(z) ]

subject to: concept(decode(z)) = c
```

### Step 2: Define Attractor Loss

For a new network f(x; θ), we want representations h = f(x; θ) to be close to attractors:

```
L_attractor(x, y; θ) = min_{A ∈ Attractors_y} ||h - encode(A)||²

where:
h = f(x; θ)                           (network's representation)
Attractors_y = {A | concept(A) = y}   (attractors for label y)
encode(A) = mapping from attractor to representation space
```

**Intuition:** The network's representation should be close to at least one attractor for the correct concept.

### Step 3: Define Property Losses

**Stability Loss:**
```
L_stability = ||h(x) - h(x + ε)||²

where ε ~ N(0, σ²)

Goal: Small changes in input → small changes in representation
```

**Universality Loss:**
```
L_universality = Σ_i KL(p_i(h) || p̄(h))

where:
p_i(h) = distribution from model i
p̄(h) = average distribution

Goal: Different models should agree on representation
```

**Disentanglement Loss:**
```
L_disentanglement = -Σ_j ||∇_{h_j} linear_probe(h)||²

Goal: Each dimension of h should be independently interpretable
```

### Step 4: Total Training Objective

```
L_total = L_task + α · L_attractor + β · L_stability + γ · L_disentanglement

where:
L_task = standard cross-entropy or other task loss
α, β, γ = hyperparameters balancing the terms
```

---

## Concrete Example: Training a Dog Classifier

### Phase 1: Discovery

Run Mahima's algorithm on frozen SDXL:

```
For concept "dog":
  Find attractors using MAP-Elites + Observers
  
  Result:
  A_dog = {
    A₁ = (z₁, stability=0.9, universality=0.85, disentanglement=0.7),
    A₂ = (z₂, stability=0.8, universality=0.9, disentanglement=0.6),
    ...
  }
```

### Phase 2: Training

Train a new ResNet classifier:

```python
class AttractorGuidedClassifier(nn.Module):
    def __init__(self, num_classes, attractor_dict):
        self.backbone = ResNet50()
        self.attractor_dict = attractor_dict  # From Phase 1
        
    def forward(self, x):
        # Get representation
        h = self.backbone(x)
        
        # Classification head
        logits = self.classifier(h)
        
        return logits, h

def compute_loss(model, x, y, attractor_dict):
    logits, h = model(x)
    
    # Task loss
    L_task = F.cross_entropy(logits, y)
    
    # Attractor loss
    # Find nearest attractor for label y
    attractors_y = attractor_dict[y]
    min_dist = float('inf')
    for A in attractors_y:
        dist = torch.norm(h - A.representation, dim=1).mean()
        min_dist = min(min_dist, dist)
    L_attractor = min_dist
    
    # Stability loss
    x_noisy = x + torch.randn_like(x) * 0.1
    _, h_noisy = model(x_noisy)
    L_stability = F.mse_loss(h, h_noisy)
    
    # Total loss
    L_total = L_task + 0.5 * L_attractor + 0.1 * L_stability
    
    return L_total
```

---

## Why This Addresses LossFunk's Problem

| LossFunk's Requirement | How This Framework Addresses It |
|------------------------|--------------------------------|
| "Learn symbolic abstractions" | Networks learn to produce representations that match discovered attractors (which ARE symbolic) |
| "Use symbolic abstractions" | The attractors become the "vocabulary" for the network |
| "Without sacrificing subsymbolic knowledge" | We still train with standard task loss + neural backpropagation |
| "From data" | Attractors are discovered from existing pre-trained models, then used to guide new training |

---

## Key Innovation: The Two-Phase Approach

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   TRADITIONAL NEURO-SYMBOLIC:                                              │
│   ════════════════════════════                                              │
│                                                                             │
│   Human defines symbols → Network learns to use them                       │
│                                                                             │
│   Problem: Humans may not know the right symbols!                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   THIS APPROACH:                                                            │
│   ═══════════════                                                            │
│                                                                             │
│   Phase 1: DISCOVER symbols from existing networks                         │
│            (Mahima's contribution)                                          │
│                                                                             │
│   Phase 2: TRAIN new networks to reproduce these symbols                   │
│            (New contribution)                                               │
│                                                                             │
│   Advantage: Symbols are DISCOVERED, not manually defined!                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Research Contributions

### Mahima's Contribution (Phase 1)

1. **Attractor Discovery Algorithm**
   - MAP-Elites for diversity
   - Three observers for quality
   - SDS for refinement

2. **Symbolic Vocabulary Extraction**
   - Map concepts → attractors
   - Characterize attractor properties
   - Build attractor dictionary

### New Contribution (Phase 2)

3. **Attractor-Guided Training**
   - Loss functions based on attractors
   - Property-based regularization
   - End-to-end differentiable

4. **Evaluation**
   - Do trained networks have better symbolic properties?
   - Are they more interpretable?
   - Do they transfer better?

---

## Experimental Validation

### Experiment 1: Does attractor-guided training improve interpretability?

```
Setup:
- Train two classifiers on ImageNet
  (a) Standard training
  (b) Attractor-guided training

Evaluation:
- Linear probe accuracy on concept prediction
- Stability under noise
- Universality across architectures

Hypothesis: (b) > (a) on all metrics
```

### Experiment 2: Does attractor-guided training improve data efficiency?

```
Setup:
- Train with limited data (1%, 10%, 100% of ImageNet)
- Compare standard vs attractor-guided

Hypothesis: Attractor-guided learns faster with less data
```

### Experiment 3: Do learned representations transfer better?

```
Setup:
- Pre-train on ImageNet
- Fine-tune on new task (e.g., medical imaging)
- Compare standard vs attractor-guided

Hypothesis: Attractor-guided representations transfer better
```

---

## Timeline

| Week | Task |
|------|------|
| 1-2 | Implement Phase 1 (attractor discovery) on existing models |
| 3-4 | Build attractor dictionary for ImageNet classes |
| 5-6 | Implement Phase 2 (attractor-guided training) |
| 7-8 | Run experiments on data efficiency |
| 9-10 | Run experiments on interpretability |
| 11-12 | Write up results |

---

## Summary

**The reframed proposal:**

1. **Don't just discover attractors → USE them for training**

2. **Two-phase approach:**
   - Phase 1: Discover symbolic attractors (Mahima's work)
   - Phase 2: Train networks to reproduce them (new work)

3. **This directly addresses LossFunk's problem:**
   - Networks LEARN symbolic representations
   - Symbols come from DATA (via pre-trained models)
   - Subsymbolic knowledge preserved (still neural training)

4. **Novel contribution:**
   - First framework to use attractor discovery as training signal
   - Bridges analysis and synthesis
   - Creates a complete pipeline from discovery to learning

---

## Key Messages for LossFunk

1. **We don't just analyze → We use analysis to guide learning**

2. **Symbols emerge from data, not human definition**

3. **The whole pipeline is differentiable and trainable**

4. **We can measure if it works (interpretability, data efficiency, transfer)**

This is a complete research program that builds on Mahima's foundation but actually SOLVES the problem LossFunk posed.
