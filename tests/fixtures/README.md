# Test Fixtures

Sample Python files for testing Shannon Insight v2 signals and finders.

## Fixtures

| File | Purpose | Key Signals/Finders |
|------|---------|---------------------|
| `sample_simple.py` | Basic Python file | lines, function_count, class_count |
| `sample_stubs.py` | Mix of stubs and implementations | stub_ratio, impl_gini, HOLLOW_CODE |
| `sample_complex.py` | Deep nesting | max_nesting, cognitive_load |
| `sample_entry.py` | Entry point with `if __name__` | role=ENTRY_POINT, depth=0 |
| `sample_orphan.py` | File nothing imports | is_orphan, ORPHAN_CODE |
| `sample_model.py` | Data classes only | role=MODEL |
| `test_sample.py` | Test file | role=TEST |

## Expected Values

### sample_simple.py
- lines: ~30
- function_count: 4 (hello, add, multiply, divide)
- class_count: 1 (Calculator)
- max_nesting: 1 (if in divide)
- stub_ratio: 0.0 (all implemented)

### sample_stubs.py
- function_count: 7
- stub_ratio: ~0.57 (4/7 are stubs)
- impl_gini: > 0.5 (high variance in body tokens)
- HOLLOW_CODE should fire

### sample_complex.py
- max_nesting: 5 (deeply_nested function)
- cognitive_load: high
- Multiple functions with varying complexity

### sample_entry.py
- role: ENTRY_POINT (has `if __name__ == "__main__"`)
- depth: 0 (entry points are roots)

### sample_orphan.py
- is_orphan: true (nothing imports it)
- ORPHAN_CODE should fire

### sample_model.py
- role: MODEL (only classes, no functions)
- class_count: 4

### test_sample.py
- role: TEST (filename starts with test_)

## Usage in Tests

```python
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

def test_scanning_simple():
    from scanning import scan_file
    syntax = scan_file(FIXTURES / "sample_simple.py")
    assert syntax.function_count == 4
    assert syntax.class_count == 1

def test_hollow_code_detection():
    from scanning import scan_file
    syntax = scan_file(FIXTURES / "sample_stubs.py")
    assert syntax.stub_ratio > 0.5
    assert syntax.impl_gini > 0.5
```
