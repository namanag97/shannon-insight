# Contributing to Shannon Insight

Thank you for your interest in contributing to Shannon Insight! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- **Add new language support** - Implement analyzers for Python, Rust, Java, etc.
- **Improve primitives** - Enhance existing mathematical models
- **Add new primitives** - Propose and implement new quality dimensions
- **Fix bugs** - Report and fix issues
- **Improve documentation** - Help others understand the math and implementation
- **Write tests** - Increase code coverage and reliability

## 🚀 Getting Started

### Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/shannon-insight.git
cd shannon-insight
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
pip install -r requirements.txt
```

4. Run the analyzer to verify:
```bash
shannon-insight --help
```

## 📝 Adding a New Language

To add support for a new language, create a new scanner in `src/shannon_insight/analyzers/`:

### Step 1: Create Scanner Class

```python
# src/shannon_insight/analyzers/python_analyzer.py
from .base import BaseScanner
from ..models import FileMetrics

class PythonScanner(BaseScanner):
    def __init__(self, root_dir: str):
        super().__init__(root_dir, extensions=[".py"])

    def _should_skip(self, filepath: Path) -> bool:
        """Skip test files and virtual environments"""
        path_str = str(filepath)
        return "__pycache__" in path_str or ".venv" in path_str

    def _analyze_file(self, filepath: Path) -> FileMetrics:
        """Extract metrics from Python file"""
        # Implement language-specific parsing
        pass

    # Implement all abstract methods from BaseScanner
    def _count_tokens(self, content: str) -> int:
        pass

    def _extract_imports(self, content: str) -> List[str]:
        pass

    # ... etc
```

### Step 2: Register Scanner

Update `src/shannon_insight/analyzers/__init__.py`:

```python
from .python_analyzer import PythonScanner

__all__ = ["BaseScanner", "GoScanner", "TypeScriptScanner", "PythonScanner"]
```

### Step 3: Update Core

Add auto-detection in `src/shannon_insight/core.py`:

```python
def _get_scanner(self):
    if self.language == "python":
        return PythonScanner(self.root_dir)
    # ... existing code
```

### Step 4: Test

Test your analyzer on real codebases:

```bash
shannon-insight /path/to/python/project --language python
```

## 🧮 Adding a New Primitive

To add a sixth quality primitive:

### Step 1: Update Models

Add the field to `Primitives` in `src/shannon_insight/models.py`:

```python
@dataclass
class Primitives:
    structural_entropy: float
    network_centrality: float
    churn_volatility: float
    semantic_coherence: float
    cognitive_load: float
    test_coverage: float  # NEW PRIMITIVE
```

### Step 2: Implement Computation

Add computation method in `src/shannon_insight/primitives/extractor.py`:

```python
def _compute_test_coverage(self) -> Dict[str, float]:
    """Compute test coverage metric"""
    coverage = {}
    # Implement your algorithm
    return coverage
```

Update `extract_all()` to include the new primitive.

### Step 3: Update Fusion

Modify weights in `src/shannon_insight/primitives/fusion.py`:

```python
weights = [0.15, 0.2, 0.15, 0.15, 0.15, 0.2]  # 6 primitives now
```

### Step 4: Document

Add mathematical foundation to `docs/MATHEMATICAL_FOUNDATION.md`.

## 🐛 Reporting Bugs

When reporting bugs, please include:
- Python version
- Shannon Insight version
- Operating system
- Minimal code example to reproduce
- Expected vs actual behavior

## 💡 Feature Requests

Feature requests are welcome! Please:
- Check existing issues first
- Explain the use case
- Propose implementation if possible
- Consider mathematical soundness

## 📐 Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Keep functions focused and small
- Add comments for complex mathematical operations

## ✅ Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Test thoroughly
4. Update documentation
5. Commit with clear messages
6. Push and create a PR
7. Respond to review feedback

## 🧪 Testing

We value tests! Please add tests for:
- New analyzers
- New primitives
- Bug fixes
- Edge cases

Run tests (when test suite exists):
```bash
pytest
```

## 📖 Documentation

Good documentation helps everyone:
- Update README.md for user-facing changes
- Update MATHEMATICAL_FOUNDATION.md for algorithmic changes
- Add docstrings to new code
- Include examples in docs

## 🎓 Mathematical Rigor

Shannon Insight is built on mathematical principles. When proposing changes:
- Explain the mathematical foundation
- Show it's orthogonal to existing primitives
- Provide empirical validation if possible
- Consider computational complexity

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

- Open an issue for questions
- Tag with "question" label
- Be specific and provide context

## 🙏 Thank You!

Every contribution makes Shannon Insight better for everyone. Thank you for being part of this project!

---

**Happy coding! 🚀**
