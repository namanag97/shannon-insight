"""Complex file with deep nesting for testing cognitive_load."""

from typing import Any, Optional


def deeply_nested(data: list[dict[str, Any]], config: dict[str, Any]) -> list[str]:
    """
    A function with deep nesting.
    Expected max_nesting = 5 (function + for + if + for + if)
    """
    results = []

    for item in data:  # depth 1
        if item.get("active"):  # depth 2
            for key, value in item.items():  # depth 3
                if key.startswith("prefix_"):  # depth 4
                    if value is not None:  # depth 5
                        results.append(str(value))

    return results


def moderately_nested(items: list[int]) -> int:
    """
    Moderate nesting.
    Expected max_nesting = 3 (function + for + if + else)
    """
    total = 0

    for item in items:  # depth 1
        if item > 0:  # depth 2
            if item % 2 == 0:  # depth 3
                total += item * 2
            else:
                total += item
        else:
            total -= item

    return total


def flat_function(a: int, b: int, c: int) -> int:
    """
    Flat function with no nesting.
    Expected max_nesting = 0
    """
    result = a + b
    result = result * c
    result = result - 1
    return result


def try_except_nested(data: dict[str, Any]) -> Optional[str]:
    """
    Function with try/except nesting.
    Expected max_nesting = 4
    """
    try:  # depth 1
        for key in data:  # depth 2
            try:  # depth 3
                if data[key]:  # depth 4
                    return str(data[key])
            except (KeyError, TypeError):
                continue
    except Exception:
        return None

    return None


class ComplexClass:
    """Class with multiple complex methods."""

    def __init__(self, data: list[int]) -> None:
        self.data = data
        self._cache: dict[str, Any] = {}

    def process(self) -> list[int]:
        """Process with nesting."""
        results = []
        for item in self.data:
            if item > 0:
                for i in range(item):
                    if i % 2 == 0:
                        results.append(i)
        return results

    def simple(self) -> int:
        """Simple method."""
        return sum(self.data)
