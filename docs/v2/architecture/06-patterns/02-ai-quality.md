# AI Code Quality Patterns

6 patterns for detecting AI-generated code issues.

---

## 8. ORPHAN_CODE

File with no incoming dependencies.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.55 |
| **Phase** | 3 |
| **Hotspot** | No |
| **Requires** | is_orphan, role |

### Condition

```python
is_orphan = True
# Equivalent to:
# in_degree = 0 AND role ∉ {ENTRY_POINT, TEST}
```

### Evidence

- **IR3**: in_degree = 0, depth = -1
- **IR2**: role
- **G6**: nearest semantic neighbor (if available)

### Remediation

"This file is unreachable. Wire it into [semantic neighbor] or remove it."

### Effort

LOW

---

## 9. HOLLOW_CODE

File with many stub functions.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.71 |
| **Phase** | 1 |
| **Hotspot** | No |
| **Requires** | stub_ratio, impl_gini |

### Condition

```python
stub_ratio > 0.5 AND
impl_gini > 0.6
```

- `stub_ratio > 0.5`: More than half the functions are stubs
- `impl_gini > 0.6`: Bimodal distribution (some complete, some stubs) — AI signature

### Evidence

- **IR1**: stub functions listed with body
- **IR2**: stub_ratio, impl_gini
- **IR5t**: author (bot/AI indicator)

### Remediation

"Implement the stub functions. Priority: functions called by other files."

### Effort

MEDIUM

---

## 10. PHANTOM_IMPORTS

File with unresolved imports.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.65 |
| **Phase** | 3 |
| **Hotspot** | No |
| **Requires** | phantom_import_count |

### Condition

```python
phantom_import_count > 0
```

### Evidence

- **IR1**: unresolved import statements with source references
- **IR3**: phantom_ratio for file

### Remediation

"Create missing module or replace with existing library."

### Effort

MEDIUM

---

## 11. COPY_PASTE_CLONE

Files with high content similarity (NCD).

| Property | Value |
|----------|-------|
| **Scope** | FILE_PAIR |
| **Severity** | 0.50 |
| **Phase** | 3 |
| **Hotspot** | No |
| **Requires** | CLONED_FROM |

### Condition

```python
NCD(A, B) < 0.3
# Where NCD = Normalized Compression Distance
```

### Detection Algorithm

1. **MinHash pre-filter**: Compute 128-bit MinHash signature for each file
2. **LSH bucketing**: Hash signatures into buckets, candidate pairs share bucket
3. **NCD verification**: For candidates, compute actual NCD:
   ```
   NCD(A, B) = (C(A+B) - min(C(A), C(B))) / max(C(A), C(B))
   ```
   where C(x) = len(zlib.compress(x))

### Evidence

- **IR3**: NCD score, file sizes, shared content estimate

### Remediation

"Extract shared logic into a common module."

### Effort

MEDIUM

---

## 12. FLAT_ARCHITECTURE

Codebase with no orchestration layer.

| Property | Value |
|----------|-------|
| **Scope** | CODEBASE |
| **Severity** | 0.60 |
| **Phase** | 3 |
| **Hotspot** | No |
| **Requires** | depth (max), glue_deficit |

### Condition

```python
max(depth across all files) <= 1 AND
glue_deficit > 0.5
```

- `max_depth <= 1`: No deep call chains
- `glue_deficit > 0.5`: Few files are "glue" (both in_degree > 0 and out_degree > 0)

### Evidence

- **IR3**: max depth, glue_deficit, internal_ratio

### Remediation

"Add composition layer. Many leaf modules exist but nothing orchestrates them."

### Effort

HIGH

---

## 13. NAMING_DRIFT

Filename doesn't match content.

| Property | Value |
|----------|-------|
| **Scope** | FILE |
| **Severity** | 0.45 |
| **Phase** | 2 |
| **Hotspot** | No |
| **Requires** | naming_drift |

### Condition

```python
naming_drift > 0.7
```

### Evidence

- **IR2**: filename tokens vs content concept tokens
- Cosine similarity score

### Remediation

"Rename file to match its actual content, or extract mismatched logic."

### Effort

LOW

### Edge Cases

- Generic filenames (utils.py, helpers.py, common.py) → naming_drift = 0.0
- Single-function files → naming_drift based on function name
