import os

import helper
import pkg
import requests
from pkg import alpha
from pkg import beta
from pkg import delta
from pkg import sigma
from pkg import thing
from pkg.deep import nested
from .missing import x


def main() -> int:
    return x or len(nested.drill()) + alpha.run() + beta.load() + delta.value + sigma.sig() + thing.THINGS


if __name__ == "__main__":
    raise SystemExit(main())
