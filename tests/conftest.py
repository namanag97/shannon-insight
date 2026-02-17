"""Shared test fixtures for Shannon Insight math tests."""

import numpy as np
import pytest


def pytest_addoption(parser):
    """Add --run-slow option for slow tests."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="run slow tests",
    )


def pytest_configure(config):
    """Configure slow marker."""
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    """Skip slow tests unless --run-slow is given."""
    if config.getoption("--run-slow"):
        return
    skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def uniform_distribution():
    """Uniform distribution over 4 events."""
    return {"a": 25, "b": 25, "c": 25, "d": 25}


@pytest.fixture
def skewed_distribution():
    """Heavily skewed distribution."""
    return {"a": 97, "b": 1, "c": 1, "d": 1}


@pytest.fixture
def single_event_distribution():
    """Distribution with a single event."""
    return {"a": 100}


@pytest.fixture
def empty_distribution():
    """Empty distribution."""
    return {}


@pytest.fixture
def known_distribution():
    """Distribution with known entropy: fair coin = 1.0 bit."""
    return {"heads": 50, "tails": 50}


@pytest.fixture
def star_graph():
    """Star graph: center connected to 4 leaves."""
    return {
        "center": ["a", "b", "c", "d"],
        "a": [],
        "b": [],
        "c": [],
        "d": [],
    }


@pytest.fixture
def chain_graph():
    """Chain graph: a -> b -> c -> d."""
    return {
        "a": ["b"],
        "b": ["c"],
        "c": ["d"],
        "d": [],
    }


@pytest.fixture
def empty_graph():
    """Empty graph with no nodes."""
    return {}


@pytest.fixture
def single_node_graph():
    """Graph with a single node."""
    return {"a": []}


@pytest.fixture
def normal_values():
    """Known normal-ish values for statistics tests."""
    return [2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]


@pytest.fixture
def outlier_values():
    """Values with an obvious outlier."""
    return [1.0, 1.0, 1.0, 1.0, 100.0]


@pytest.fixture
def constant_values():
    """Constant values (zero variance)."""
    return [5.0, 5.0, 5.0, 5.0, 5.0]


@pytest.fixture
def identity_cov_3d():
    """3x3 identity covariance matrix."""
    return np.eye(3)
