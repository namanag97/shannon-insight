"""File with stub functions for testing HOLLOW_CODE detection."""

from typing import Any


def implemented_function(data: list[int]) -> int:
    """A fully implemented function."""
    total = 0
    for item in data:
        if item > 0:
            total += item
        else:
            total -= item
    return total


def stub_pass() -> None:
    """Stub with pass."""
    pass


def stub_ellipsis() -> None:
    """Stub with ellipsis."""
    ...


def stub_return_none() -> None:
    """Stub with return None."""
    return None


def stub_not_implemented() -> int:
    """Stub with NotImplementedError."""
    raise NotImplementedError()


def stub_todo() -> str:
    """Stub with TODO."""
    # TODO: implement this
    pass


class PartialImplementation:
    """Class with mix of stubs and implementations."""

    def real_method(self, x: int) -> int:
        """Real implementation."""
        return x * 2 + 1

    def stub_method(self) -> None:
        """Stub method."""
        pass

    def another_stub(self) -> dict[str, Any]:
        """Another stub."""
        ...

    def yet_another_real(self, items: list[str]) -> str:
        """Another real method."""
        result = []
        for item in items:
            result.append(item.upper())
        return ", ".join(result)
