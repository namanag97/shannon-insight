"""Simple Python file for testing basic scanning."""


def hello() -> str:
    """A simple function with docstring."""
    return "hello"


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


class Calculator:
    """A simple calculator class."""

    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y

    def divide(self, x: int, y: int) -> float:
        """Divide two numbers."""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y
