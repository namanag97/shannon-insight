"""Test file for testing TEST role detection."""

import pytest


def test_basic_assertion():
    """Basic test."""
    assert 1 + 1 == 2


def test_list_operations():
    """Test list operations."""
    items = [1, 2, 3]
    assert len(items) == 3
    items.append(4)
    assert len(items) == 4


class TestCalculator:
    """Test class for calculator."""

    def test_add(self):
        """Test addition."""
        assert 2 + 2 == 4

    def test_subtract(self):
        """Test subtraction."""
        assert 5 - 3 == 2

    def test_multiply(self):
        """Test multiplication."""
        assert 3 * 4 == 12


@pytest.fixture
def sample_data() -> list[int]:
    """Sample data fixture."""
    return [1, 2, 3, 4, 5]


def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sum(sample_data) == 15
