# Autonomous Discovery of Emergent Symbolic Attractors

## A Plain-Language Explanation

---

## Overview

| Aspect | Description |
|--------|-------------|
| **Goal** | Find the "essence" of concepts (like "dog") in neural networks |
| **Approach** | Search for stable patterns that trigger concepts |
| **Method** | Combine a generator (SDXL), observers (judges), and search (MAP-Elites) |
| **Output** | A map of all ways a concept can emerge in a network |

---

## The Big Question

### What Is the Paper Trying to Solve?

Neural networks can recognize "dog" in many different images. But we don't understand **why** or **how**.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Show network these images:                            │
│                                                         │
│   🐕  🐩  🦮  🐕‍🦺  🐶                                    │
│                                                         │
│   Network says: "dog, dog, dog, dog, dog"              │
│                                                         │
│   But WHY?                                              │
│                                                         │
│   What is the MINIMAL thing that makes it say "dog"?   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

Is it fur? Four legs? A snout? Ears? Something we can't describe?

**This paper tries to find out.**

---

## The Core Idea: Symbolic Attractors

### What Is an Attractor?

Think of a bowl with a marble:

```
            ○  ← marble starts here
           / \
          /   \
         /     \
        /   ●   \  ← marble ends up here
       /_________ \
```

No matter where you start the marble, it rolls to the bottom.

- **Attractor** = the stable point at the bottom
- **Basin** = the bowl (the region that leads to the attractor)

### In Neural Networks

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Input space = all possible images                    │
│                                                         │
│   Some images make the network say "dog!"              │
│                                                         │
│   If you slightly change those images,                 │
│   the network STILL says "dog!"                        │
│                                                         │
│   These stable regions = ATTRACTORS for "dog"          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

An attractor is like a "trap" — once you're in it, you stay in it.

---

## Three Types of Attractors

### Type 1: Geometric Attractors (The "Snap")

**Idea:** Networks collapse high-dimensional input into a single concept.

```
Input:  196,608 pixel values (256×256×3 image)
              │
              ▼
        Network processes...
              │
              ▼
Output: "dog" (one concept!)
```

The "snap" happens where all that variation collapses into ONE symbolic output.

### Type 2: Stability Attractors (The "Basin")

**Idea:** A true attractor is stable under noise.

```
Original image:   🐕  → Network says "dog"
Add some noise:   ░🐕░ → Network says "dog"
Add more noise:   ▓🐕▓ → Network says "dog"
```

The "dog" concept survives perturbation. This defines the boundary of the attractor.

### Type 3: Disentangled Attractors (The "Essence")

**Idea:** The attractor contains ONLY the relevant information.

```
Image with clutter:
┌───────────────────┐
│ ☀️🌳🐕🏠🌿         │
│  dog + stuff      │
└───────────────────┘
          │
          ▼
Network extracts:
┌───────────────────┐
│      🐕           │  ← Just the "dog essence"
│   (dog concept)   │
└───────────────────┘
```

This is **disentanglement** — relevant info separated from noise.

---

## The Method: Three Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                          ┌─────────────┐                                │
│                          │   SEARCH    │                                │
│                          │ (MAP-Elites)│                                │
│                          │             │                                │
│                          │ "Where      │                                │
│                          │  should I   │                                │
│                          │  look?"     │                                │
│                          └──────┬──────┘                                │
│                                 │                                       │
│                                 │ picks a place to explore              │
│                                 ▼                                       │
│                          ┌─────────────┐                                │
│                          │  GENERATOR  │                                │
│                          │   (SDXL)    │                                │
│                          │             │                                │
│                          │ "Here's an  │                                │
│                          │  image from │                                │
│                          │  that spot" │                                │
│                          └──────┬──────┘                                │
│                                 │                                       │
│                                 │ creates an image                      │
│                                 ▼                                       │
│                          ┌─────────────┐                                │
│                          │  OBSERVERS  │                                │
│                          │             │                                │
│                          │ "Is this a  │                                │
│                          │  good dog   │                                │
│                          │  attractor?"│                                │
│                          └──────┬──────┘                                │
│                                 │                                       │
│                                 │ gives score and feedback              │
│                                 ▼                                       │
│                          ┌─────────────┐                                │
│                          │   SEARCH    │                                │
│                          │             │                                │
│                          │ "Based on   │                                │
│                          │  the score, │                                │
│                          │  where now?"│                                │
│                          └──────┬──────┘                                │
│                                 │                                       │
│                                 ▼                                       │
│                            (repeat)                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component 1: The Generator (SDXL)

### What Is SDXL?

| Aspect | Value |
|--------|-------|
| **Full Name** | Stable Diffusion Xtra Large |
| **Created By** | Stability AI |
| **Released** | July 2023 |
| **What It Does** | Text → Image |
| **Resolution** | 1024×1024 |

### Why SDXL?

1. **Continuous Latent Space**

   ```
   Image (1024×1024×3) → Latent (128×128×4)
   3,145,728 values    → 65,536 values
   
   Small changes in latent → small changes in image
   ```

2. **Rich Semantic Structure**

   ```
   z₁ → dog looking left
   z₂ → dog looking right
   z₃ → cat looking left
   
   (z₁ + z₂)/2 → dog looking forward
   (z₁ + z₃)/2 → animal looking left
   ```

3. **Frozen = Stable Search Space**

   ```
   If SDXL was being trained:
   • The meaning of z would keep changing
   • z₁ = "dog" today, z₁ = "car" tomorrow
   • No way to reliably search
   
   FROZEN = The space is fixed and searchable
   ```

---

## Component 2: The Observers (Three Judges)

### Why Three?

Each observer measures a DIFFERENT property:

| Observer | Measures | Question |
|----------|----------|----------|
| Committee | Universality | Do all models agree? |
| Stability | Robustness | Does it survive noise? |
| Probe | Disentanglement | Is it cleanly accessible? |

Together they form a COMPLETE picture of the attractor.

### Observer 1: The Committee

**Goal:** Ensure the attractor is universal, not just one model's quirk.

```
Show same image to MULTIPLE architectures:

Image: 🐕
   │
   ├─→ CNN (ResNet)      → "dog!" ✓
   ├─→ ViT (Transformer) → "dog!" ✓
   └─→ SSL (I-JEPA)      → "dog!" ✓

If ALL agree → It's a UNIVERSAL attractor
```

**Why different architectures?**

| Architecture | Good At | Bias |
|--------------|---------|------|
| CNN | Local patterns, textures | Translation invariance |
| ViT | Global relationships | Attention mechanism |
| SSL | Structural understanding | No labels needed |

If ALL three say "dog" → something FUNDAMENTAL about dog-ness exists.

**Loss Function:**

```
L_comm = -Σᵢ log P_Mi(concept | image)

Minimize this = maximize joint probability
```

### Observer 2: The Stability Check

**Goal:** Find STABLE attractors (big basins).

**Uses:** I-JEPA (Image Joint-Embedding Predictive Architecture)

```
What is I-JEPA?
• Self-supervised model by Meta AI
• Learns to predict parts of images from other parts
• Good at understanding structure

Test:
Original:   🐕  → encoding h₁
Perturbed:  🐕 + noise → encoding h₂

If ||h₁ - h₂|| is SMALL  → STABLE attractor
If ||h₁ - h₂|| is LARGE  → BRITTLE attractor
```

**Visual:**

```
Stable:
  h(x)      ●←───────┐
                    │ Small distance
  h(x+ε)    ●←───────┘
  
  Adding noise doesn't change the meaning much

Brittle:
  h(x)      ●←─────────────────────┐
                                  │ Large distance
  h(x+ε)                        ●←─┘
  
  Adding noise completely changes the meaning
```

**Loss Function:**

```
L_stab = ||h(x) - h(x + noise)||²

Minimize this = more stable
```

### Observer 3: Linear Probes

**Goal:** Check if concept is CLEANLY represented.

```
Take frozen network's intermediate layer

Image → [Network] → φ(x) (activations)
                      │
                      ▼
Can a SIMPLE LINEAR classifier extract concept?

R_probe = w · φ(x) + b

If YES → Concept is DISENTANGLED (clean)
If NO  → Concept is ENTANGLED (messy)
```

**Why linear?**

```
Linear = can only find straight-line decisions

If a LINEAR classifier works, the concept
must be cleanly separated in the representation

       dogs ●●●●●│              │
              │    ○○○○○ cats     
              │                   
       Linear boundary works!    

         ●●○       ○●●               
           ●●○   ○●●   (mixed)       
             ●●○●●                    
       Linear boundary doesn't work!    
```

---

## Component 3: The Search (MAP-Elites)

### Why Not Just Gradient Descent?

```
Gradient descent finds ONE solution

"Show me a dog" → Gives you ONE dog image

But there are MANY ways to make a network say "dog"!

• A realistic dog photo
• A cartoon dog
• A silhouette of a dog
• Just dog ears visible
• Abstract patterns that "look dog-like"

The paper wants to find ALL of these!
```

### What Is MAP-Elites?

**MAP-Elites = Quality + Diversity**

```
Traditional evolution:
"Keep only the BEST, throw away the rest"

MAP-Elites:
"Keep the BEST IN EACH CATEGORY"
```

### The Archive (The Grid)

```
                    COMPLEXITY
              Low        Med        High
          ┌─────────┬─────────┬─────────┐
    High  │ z₁=...  │ z₂=...  │ z₃=...  │
  P       │ fit=0.9 │ fit=0.8 │ fit=0.7 │
  U       ├─────────┼─────────┼─────────┤
  R       │ z₄=...  │ z₅=...  │ z₆=...  │
  I  Med  │ fit=0.6 │ fit=0.7 │ fit=0.6 │
  T       ├─────────┼─────────┼─────────┤
  Y       │ z₇=...  │ z₈=...  │ z₉=...  │
    Low   │ fit=0.5 │ fit=0.4 │ fit=0.3 │
          └─────────┴─────────┴─────────┘

zᵢ = latent vector (the solution)
fit = fitness score (how good is it?)
```

Each cell keeps the BEST solution for that combination of descriptors.

---

## The Complete Algorithm

### Initialization

```
For i = 1 to k (initial population size):
    z = random latent vector
    image = decode(z)
    fitness = evaluate(image)
    descriptors = measure(image)
    place in archive cell based on descriptors
```

### Main Loop (Repeat N times)

```
Step 1: SELECTION
─────────────────
• Pick a random cell from the archive
• Get the elite z stored in that cell

Step 2: MUTATION
────────────────
• z' = z + N(0, σ)
• Add Gaussian noise to create variation

Step 3: OPTIONAL REFINEMENT (SDS)
─────────────────────────────────
• Use SDS to push z' toward the target concept
• This "sharpens" the image to be more "dog-like"

Step 4: EVALUATION
──────────────────
• Decode z' to get image
• Run all three observers:
  - Committee: L_comm
  - Stability: L_stab
  - Probe: R_probe
• Combine into fitness score

Step 5: DESCRIPTOR MEASUREMENT
──────────────────────────────
• Measure which "niche" this belongs to
  e.g., complexity = 0.7, purity = 0.5

Step 6: ARCHIVE UPDATE
──────────────────────
• Find the cell for these descriptor values
• If cell is empty OR new fitness > old fitness:
  Store z' in that cell
• Otherwise: discard
```

### Result

A filled grid showing ALL different ways to trigger the concept "dog", organized by characteristics.

---

## The Role of SDS

### What Is SDS?

SDS = Score Distillation Sampling

```
MAP-Elites does MUTATION (random exploration)
SDS does REFINEMENT (directed improvement)
```

### Mutation Alone

```
z' = z + random noise

┌─────┐
│  🐕 │ ──→ random change ──→ ???
└─────┘         │
                │
       could go anywhere!
       might become cat, car, noise...

Problem: Too random, slow to find attractors
```

### With SDS Refinement

```
z' = z + random noise
then use SDS to push toward "dog"

┌─────┐         ┌─────┐         ┌─────┐
│  🐕 │ ──→ ??? ──→│ ░🐕 │ ──SDS─→│  🐕 │
└─────┘         └─────┘         └─────┘
 start        mutated          refined
                             (more dog-like)

SDS acts as a "guide" toward the attractor
```

### Why Both?

```
Mutation → EXPLORES new regions of the space
SDS      → EXPLOITS the knowledge of the frozen model
            to refine toward attractors

Together: explore-diversify + refine-improve
```

---

## How Components Connect

### The Loop

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   1. SEARCH picks a latent z                           │
│   2. GENERATOR turns z into an image                   │
│   3. OBSERVERS score the image                         │
│   4. SEARCH uses score to update strategy              │
│   5. Repeat                                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Why This Order?

| Order | Component | Reason |
|-------|-----------|--------|
| 1 | Generator | Need something to evaluate before judging |
| 2 | Observers | Need to know if what you found is good |
| 3 | Search | Need to decide what to try next based on results |
| 4 | Loop back | Continue the exploration |

### Data Flow

```
SEARCH ─────────────────→ GENERATOR
  │                            │
  │  passes:                   │  passes:
  │  • latent vector z         │  • image (pixels)
  │                            │
  │                            ▼
  │                       OBSERVERS
  │                            │
  │                            │  passes:
  │                            │  • scores (L_comm, L_stab, R_probe)
  │                            │  • fitness
  │                            │  • descriptor values
  │                            │
  └────────────────────────────┘
       (feedback to search)
```

---

## What the Paper Hopes to Discover

### Three Hypotheses

**Hypothesis 1: Universal Minimal Basis**

```
IF different architectures (CNN, ViT, SSL)
   all recognize the same "dog" attractor...

THEN that attractor represents something
     FUNDAMENTAL about "dog-ness"
     (not just how one model works)
```

**Hypothesis 2: SSL vs CLIP**

```
CLIP (trained on image-text pairs):
• Might have "brittle" attractors
• Relies on text labels, might miss nuances

I-JEPA (self-supervised, no labels):
• Might have more "human-like" attractors
• Learns from structure, not labels
```

**Hypothesis 3: MAP-Elites vs Pure RL**

```
Pure Reinforcement Learning:
• Might find ONE way to trigger "dog"
• Mode collapse: keeps outputting same thing

MAP-Elites:
• Finds MANY ways to trigger "dog"
• Maps the ENTIRE boundary of the attractor
• Discovers the "walls" of the concept
```

---

## The Three Observers in Detail

### Committee Observer

**What it checks:** Do all models agree?

**How:**

```
1. Take candidate image
2. Run through multiple architectures (CNN, ViT, SSL)
3. Get probability of concept from each
4. Multiply probabilities (assuming independence)

P_joint = P_CNN × P_ViT × P_SSL

High P_joint = Universal attractor
```

**Loss:**

```
L_comm = -(log P_CNN + log P_ViT + log P_SSL)

Minimize L_comm = maximize agreement
```

### Stability Observer

**What it checks:** Is it robust to noise?

**How:**

```
1. Get encoding of original image: h(x)
2. Add noise to image: x + ε
3. Get encoding of noisy image: h(x + ε)
4. Measure distance: ||h(x) - h(x + ε)||

Small distance = Stable
Large distance = Brittle
```

**Why I-JEPA?**

I-JEPA learns semantic representations that are robust to pixel-level changes. It focuses on meaning, not pixels.

### Probe Observer

**What it checks:** Is the concept linearly accessible?

**How:**

```
1. Get intermediate activations: φ(x)
2. Train linear classifier: R = w·φ(x) + b
3. Check accuracy

High accuracy = Disentangled (clean)
Low accuracy = Entangled (messy)
```

**Why linear?**

If a simple linear classifier can extract the concept, it means the concept lives in a "clean" direction in the representation space.

---

## Summary

### The Paper in One Sentence

> Use search (MAP-Elites) to explore a generator's (SDXL) latent space, guided by judges (Observers), to find all the ways a concept emerges in neural networks.

### Key Contributions

| Contribution | Description |
|--------------|-------------|
| **Three attractor types** | Geometric, Stability, Disentangled |
| **Three observers** | Committee, Stability, Probe |
| **Search method** | MAP-Elites for diversity |
| **Refinement** | SDS for quality |

### What You Get

A **map** of all the ways a concept (like "dog") can be triggered in a neural network — from realistic photos to abstract patterns.

---

## Glossary

| Term | Definition |
|------|------------|
| **Attractor** | A stable region where the network consistently outputs a concept |
| **Basin** | The region that leads to an attractor |
| **SDXL** | Stable Diffusion Xtra Large - a text-to-image model |
| **MAP-Elites** | A search algorithm that finds diverse high-quality solutions |
| **SDS** | Score Distillation Sampling - uses frozen model to guide search |
| **I-JEPA** | Self-supervised model that learns semantic representations |
| **Disentangled** | Concepts are cleanly separated, not mixed together |
| **Latent space** | The compressed representation space inside a model |
| **Linear probe** | A simple classifier that tests if concepts are accessible |

---

## Key Equations

### Committee Loss

```
L_comm = -Σᵢ log P_Mi(S | x)

Where:
Mᵢ = model i
S = symbol/concept
x = image
```

### Stability Loss

```
L_stab = ||h(x) - h(x + ε)||²

Where:
h = encoder (I-JEPA)
ε = noise
```

### Probe Score

```
R_probe = w·φ(x) + b

Where:
φ(x) = activations
w, b = learned linear classifier parameters
```

---

## Further Reading

- [MAP-Elites Paper](https://arxiv.org/abs/1504.04909)
- [DreamFusion (SDS)](https://arxiv.org/abs/2209.14988)
- [I-JEPA](https://arxiv.org/abs/2301.08243)
- [Information Bottleneck](https://arxiv.org/abs/physics/0004057)
