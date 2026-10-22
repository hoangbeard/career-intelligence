#!/usr/bin/env python3
"""Prints the absolute data root. Agents run this once per session."""

import sys

from lib.paths import resolve_data_root

if __name__ == "__main__":
    try:
        print(resolve_data_root())
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
