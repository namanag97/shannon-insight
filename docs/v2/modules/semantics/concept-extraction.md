# semantics/ -- Concept Extraction

## Overview

Concept extraction answers: *what is this file about?* It groups a file's identifiers into coherent topic clusters using TF-IDF weighting and Louvain community detection on an identifier co-occurrence graph. Each cluster is a `Concept` -- a named topic with member tokens and a weight reflecting its dominance in the file.

This produces signals #9 (`concept_count`) and #10 (`concept_entropy`) from registry/signals.md.

## Pipeline

```
FileSyntax
    |
    v
[1. Token Extraction]     -- pull all identifiers from functions, classes, variables
    |
    v
[2. Token Normalization]  -- split camelCase/snake_case, lowercase, remove stops
    |
    v
[3. Threshold Check]      -- < 20 unique tokens? skip to fallback
    |
    v
[4. TF-IDF Vectors]       -- weight tokens by corpus-wide importance
    |
    v
[5. Co-occurrence Graph]  -- edge between tokens appearing in same function
    |
    v
[6. Louvain Clustering]   -- detect communities in co-occurrence graph
    |
    v
[7. Concept Assembly]     -- each community = one Concept
    |
    v
list[Concept]
```

## Step 1: Token Extraction

Extract all user-defined identifiers from the FileSyntax:

**Sources** (in priority order):
- Function names: `file.functions[*].name`
- Parameter names: `file.functions[*].params[*]`
- Class names: `file.classes[*].name`
- Class field names: `file.classes[*].fields[*]`
- Method names: `file.classes[*].methods[*].name`
- Variable names from function bodies: simple regex on `body_source` for assignment targets
- Import names: `file.imports[*].names[*]` (included because they indicate domain vocabulary)

**Excluded**:
- Language keywords (`def`, `class`, `return`, `if`, `for`, etc.)
- Built-in type names (`int`, `str`, `bool`, `float`, `None`, `string`, etc.)
- Single-character identifiers (`i`, `j`, `k`, `x`, `_`)
- Dunder methods (`__init__`, `__str__`, `__repr__`)

## Step 2: Token Normalization

Split compound identifiers into sub-tokens, then normalize:

```
"getUserProfile"  -> ["get", "user", "profile"]
"get_user_profile" -> ["get", "user", "profile"]
"HTTPResponse"    -> ["http", "response"]
"parseJSON"       -> ["parse", "json"]
"__init__"        -> (excluded)
"MAX_RETRIES"     -> ["max", "retries"]
```

**Splitting rules**:
1. Split on `_` (snake_case).
2. Split on camelCase boundaries: lowercase-to-uppercase transitions (`getUser` -> `get`, `User`).
3. Split on acronym boundaries: uppercase run followed by lowercase (`HTTPResponse` -> `HTTP`, `Response`).
4. Lowercase all resulting tokens.
5. Remove tokens in a stopword list:
   - Generic programming words: `get`, `set`, `create`, `delete`, `update`, `init`, `new`, `make`, `handle`, `process`, `run`, `execute`, `data`, `result`, `value`, `item`, `self`, `this`, `cls`, `args`, `kwargs`
   - Language-specific noise varies by language but is kept minimal to avoid over-filtering.

**Rationale for stopwords**: Terms like `get` and `set` appear in every file and carry no discriminative power. Removing them improves TF-IDF signal quality without losing domain-specific vocabulary.

## Step 3: Threshold Check (Small File Handling)

**Threshold: 20 unique normalized tokens.**

This is the W6 solution from `docs/solutions.md`. Below this threshold, TF-IDF and Louvain produce noise because:
- TF-IDF vectors are too sparse to compute meaningful cosine similarity.
- The co-occurrence graph has too few edges for Louvain to find structure.
- Concept entropy is unreliable with < 3 potential clusters.

**Below threshold behavior**:
```python
if len(unique_tokens) < 20:
    return []  # empty concept list

# Signals are set to defaults by the caller:
#   concept_count = 1 (role-based, not concept-based)
#   concept_entropy = 0.0
#   naming_drift = None (not computable)
```

The file still gets a `role` (from role classification, which has no minimum size). Role alone provides meaningful semantic annotation for small files.

**Threshold justification**: Empirical testing on Python codebases shows that Louvain communities become stable (reproducible across runs) at ~20 unique tokens. Below this, community assignments are dominated by graph noise.

## Step 4: TF-IDF Vector Construction

For each file, build a TF-IDF weighted token vector.

**Term Frequency (per file)**:
```
tf(token, file) = count(token in file) / total_tokens(file)
```

Raw count normalized by file size. This prevents large files from dominating.

**Inverse Document Frequency (corpus-wide, computed in Pass 1)**:
```
idf(token) = log(N / df(token))

where:
  N = total number of source files in the project
  df(token) = number of files containing this token
```

Tokens appearing in many files (low IDF) are generic. Tokens appearing in few files (high IDF) are distinctive.

**TF-IDF weight**:
```
tfidf(token, file) = tf(token, file) * idf(token)
```

The resulting vector is sparse (most tokens have zero weight in most files). Store as a dictionary: `{token: weight}`.

## Step 5: Co-occurrence Graph

Build an undirected, weighted graph where:
- **Nodes** = unique normalized tokens in this file (after filtering).
- **Edges** = tokens that co-occur within the same function body.
- **Edge weight** = number of functions in which both tokens appear.

```
For each function f in file.functions:
    tokens_in_f = extract_and_normalize(f.body_source + f.name + f.params)
    for each pair (a, b) in tokens_in_f where a != b:
        graph[a][b].weight += 1
```

**Why function-level co-occurrence**: Tokens co-occurring in the same function are semantically related -- they participate in the same computation. File-level co-occurrence is too coarse (everything co-occurs with everything). Line-level is too fine (misses multi-line relationships).

**For files with no functions** (rare after threshold check): Use the entire file as a single scope. All token pairs get weight 1.

**Edge pruning**: Remove edges with weight = 1 when the graph has > 100 edges. Single co-occurrences are noise in large files.

## Step 6: Louvain Community Detection

Apply the Louvain algorithm to the co-occurrence graph. Each detected community becomes a concept.

**Algorithm summary**:
1. Start with each node in its own community.
2. For each node, compute modularity gain from moving it to each neighbor's community.
3. Move node to the community with maximum positive modularity gain.
4. Repeat until no move improves modularity.
5. Contract communities into super-nodes and repeat.

**Resolution parameter**: Use the default resolution (1.0). Higher resolution produces more, smaller communities -- we want a small number of interpretable concepts (typically 1-5 per file).

**Implementation**: Use `networkx.community.louvain_communities()` or equivalent. This is a well-tested, fast implementation suitable for graphs of hundreds of nodes.

**Post-processing**:
- Communities with fewer than 2 tokens are absorbed into the nearest community (by edge weight).
- If Louvain produces > 10 communities, merge the smallest communities until 10 remain. Files with > 10 concepts are already flagged by high concept_entropy.

## Step 7: Concept Assembly

For each Louvain community, create a `Concept`:

```python
for community in louvain_communities:
    tokens = list(community)
    # Topic = token with highest TF-IDF weight in this community
    topic = max(tokens, key=lambda t: tfidf_weights[t])
    # Weight = fraction of the file's total identifier occurrences in this community
    weight = sum(tf(t, file) for t in tokens) / sum(tf(t, file) for t in all_tokens)
    concepts.append(Concept(topic=topic, tokens=tokens, weight=weight))
```

Sort concepts by weight descending.

## Signal Computation

After concept extraction, compute the two signals:

**Signal #9: concept_count** (see registry/signals.md #9)
```
concept_count = len(concepts)
```
When concepts is empty (below threshold), caller sets `concept_count = 1`.

**Signal #10: concept_entropy** (see registry/signals.md #10)
```
H = -sum(c.weight * log2(c.weight) for c in concepts)
```
When concepts is empty (below threshold), caller sets `concept_entropy = 0.0`.

Interpretation:
- H = 0: single concept (perfectly focused file).
- H = 1.0: two equally-weighted concepts.
- H > 1.5: many competing concepts (god file risk, see registry/signals.md #10 absolute threshold).

## Example

File: `src/auth/service.py` with identifiers:

```
authenticate, verify_token, hash_password, User, Token, Session,
create_session, invalidate_session, cache_get, cache_set, cache_ttl,
redis_client, validate_email, validate_password, check_rate_limit
```

After normalization and TF-IDF weighting:

| Token | TF | IDF | TF-IDF |
|-------|---:|----:|-------:|
| authenticate | 0.07 | 2.1 | 0.14 |
| verify | 0.05 | 1.8 | 0.09 |
| token | 0.07 | 1.5 | 0.10 |
| hash | 0.05 | 2.3 | 0.11 |
| password | 0.07 | 2.0 | 0.14 |
| user | 0.05 | 0.8 | 0.04 |
| session | 0.10 | 1.9 | 0.19 |
| cache | 0.10 | 2.2 | 0.22 |
| redis | 0.03 | 2.5 | 0.08 |
| validate | 0.07 | 1.4 | 0.10 |
| rate | 0.03 | 2.8 | 0.08 |
| limit | 0.03 | 2.6 | 0.08 |
| email | 0.03 | 2.1 | 0.06 |
| ttl | 0.03 | 3.0 | 0.09 |

Co-occurrence communities (Louvain):
1. {authenticate, verify, token, hash, password, user} -- auth concept
2. {session, cache, redis, ttl} -- caching concept
3. {validate, email, password, rate, limit} -- validation concept

Result:
```
concepts = [
    Concept(topic="authenticate", tokens=[...], weight=0.40),
    Concept(topic="cache",        tokens=[...], weight=0.30),
    Concept(topic="validate",     tokens=[...], weight=0.30),
]
concept_count = 3
concept_entropy = -0.40*log2(0.40) - 0.30*log2(0.30) - 0.30*log2(0.30) = 1.57
```

This file has concept_entropy > 1.5, flagging it as unfocused. The three concepts (auth, caching, validation) suggest it should be split.

## Scalability

| Metric | Complexity | Bound |
|--------|-----------|-------|
| Token extraction | O(tokens per file) | Linear in file size |
| TF-IDF corpus build (Pass 1) | O(files x mean_tokens) | One pass over all files |
| Co-occurrence graph | O(tokens^2 per function) | Subsampled to top-500 tokens if > 500 unique |
| Louvain | O(n log n) where n = unique tokens | Fast on small graphs (< 1000 nodes) |
| Total per file | O(tokens^2) worst case | ~50ms for a 500-line file |

For a 10,000-file codebase: Pass 1 (IDF) takes ~2 seconds, Pass 2 (per-file) takes ~500 seconds at 50ms/file. Parallelizable across files in Pass 2.

## Future: BERTopic Enhancement

As noted in `docs/solutions.md` (W6), BERTopic (BERT embeddings + UMAP + HDBSCAN + c-TF-IDF) handles short documents better than TF-IDF + Louvain and could lower the threshold from 20 to ~10 unique identifiers.

**Not included in initial implementation** because:
- Adds ~500MB transformer model dependency.
- TF-IDF + Louvain is sufficient for the 80%+ of files above the 20-token threshold.
- BERTopic can be introduced as an optional enhancement behind a feature flag.

When added, BERTopic would replace steps 4-6 (TF-IDF, co-occurrence, Louvain) with:
```
embeddings = SentenceTransformer.encode(identifier_sequences)
reduced = UMAP(embeddings)
clusters = HDBSCAN(reduced)
topics = c_tfidf(clusters)
```

The output `Concept` model remains unchanged.
