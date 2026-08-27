#!/usr/bin/env python3
from wave_io_campaign import validate_campaign


def main() -> int:
    return validate_campaign("M02_VERTICAL_CONTEXT_AND_REFERENCE_PRODUCERS", "m02")


if __name__ == "__main__":
    raise SystemExit(main())
