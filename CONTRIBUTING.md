# Contributing to Shannon Insight

Thank you for your interest in contributing to Shannon Insight! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this standard.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Make (optional, for using the Makefile)

### Setup Development Environment

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/namanagarwal/shannon-insight.git
   cd shannon-insight
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Or use the Makefile:
   ```bash
   make install
   ```

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards (see below).

3. Run tests and linting:
   ```bash
   make check
   make test
   ```

4. Commit your changes with a clear message:
   ```bash
   git commit -m "Add feature: brief description of changes"
   ```

5. Push to your fork and create a pull request.

### Coding Standards

- Follow PEP 8 style guidelines
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Add type hints to all functions
- Write Google-style docstrings for public functions and classes
- Keep functions focused and under 50 lines when possible
- Add tests for new functionality

### Code Formatting

We use ruff for both linting and formatting:

```bash
# Format code
make format

# Check formatting
ruff format --check src/ tests/
ruff check src/ tests/
```

## Testing

### Running Tests

```bash
# Run all tests with coverage
make test

# Run tests without coverage
make test-quick

# Run specific test file
pytest tests/test_integration.py -v
```

### Writing Tests

- Add tests for new features and bugfixes
- Write integration tests for end-to-end functionality
- Write unit tests for individual components
- Follow the existing test structure

### Test Coverage

Maintain test coverage above 80% for new code. Check coverage with:

```bash
pytest --cov=src/shannon_insight --cov-report=html
open htmlcov/index.html
```

## Type Checking

We use mypy for static type checking:

```bash
make type-check
```

## Adding New Features

### Adding a New Language

1. Create a new scanner in `src/shannon_insight/analyzers/`
2. Register in `analyzers/__init__.py`
3. Add auto-detection in `core/scanner_factory.py`
4. Update entry points in `pyproject.toml`
5. Add tests for the new language

### Adding a New Primitive

1. Create plugin in `src/shannon_insight/primitives/plugins/`
2. Add field to `Primitives` dataclass in `models.py`
3. Register in `primitives/registry.py`
4. Add tests for the new primitive

### Adding a New Insight Finder

1. Create finder in `src/shannon_insight/insights/finders/`
2. Implement the `Finder` protocol: declare `requires` and `find(store) -> list[Finding]`
3. Register in `InsightKernel`
4. Add tests for the new finder

## Pull Request Guidelines

1. Ensure all tests pass
2. Run linting and fix any issues
3. Run type checking and fix any issues
4. Update documentation if needed
5. Add tests for new functionality

## Release Process

Releases are handled by maintainers:

1. Update version in `src/shannon_insight/__init__.py`
2. Update CHANGELOG.md with release notes
3. Create git tag: `git tag -a v0.x.x -m "Release v0.x.x"`
4. Push tag: `git push origin v0.x.x`
5. GitHub Actions will build and publish to PyPI

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
