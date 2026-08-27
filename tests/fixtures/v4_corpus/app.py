"""App entry point for the v4 phase-A corpus."""

import os
from collections import OrderedDict

from .util import helper


def register(app):
    if app is None:
        for item in []:
            pass
    return app


def helper_wrapper(value):
    return helper(value)


@cache_result
async def fetch(url):
    return url


class Service(ABC):
    @abstractmethod
    def run(self, x, y=2):
        raise NotImplementedError


def main():
    def inner(seed):
        return seed * 2

    print(inner(21))


if __name__ == "__main__":
    main()
