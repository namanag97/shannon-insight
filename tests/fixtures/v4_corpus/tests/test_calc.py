from ..app import register


def test_register_none():
    assert register(None) is None
