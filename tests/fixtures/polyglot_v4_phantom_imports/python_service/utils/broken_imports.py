"""Module with unresolved imports - triggers PHANTOM_IMPORTS."""

# These imports don't exist - they're phantoms
from nonexistent_module import MissingClass
from python_service.deprecated import OldHelper  # Module doesn't exist
import ghost_package
from ..legacy.removed_module import LegacyThing


def use_phantoms():
    """Function that references phantom imports."""
    obj1 = MissingClass()
    obj2 = OldHelper()
    obj3 = ghost_package.run()
    obj4 = LegacyThing()
    return obj1, obj2, obj3, obj4


def real_function(x: int) -> int:
    """A real function that works."""
    return x * 2


class RealClass:
    """A real class that works."""

    def __init__(self, value: str):
        self.value = value

    def process(self) -> str:
        return self.value.upper()
