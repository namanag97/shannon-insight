"""Orphan file that nothing imports - for testing ORPHAN_CODE detection."""

from typing import List


def unused_helper(items: List[str]) -> List[str]:
    """A helper function that no one calls."""
    return [item.strip() for item in items]


def another_unused(x: int, y: int) -> int:
    """Another unused function."""
    return x * y + 1


class OrphanClass:
    """A class that no one uses."""

    def orphan_method(self) -> str:
        """Orphan method."""
        return "I am unused"
