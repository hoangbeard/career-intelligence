#!/usr/bin/env python3
"""Prints the next free job ID for a year: JOB-YYYY-NNN."""

import re
import sys

from lib.jobs import load_jobs, next_job_id
from lib.paths import resolve_data_root

if __name__ == "__main__":
    year = sys.argv[1] if len(sys.argv) > 1 else ""
    if not re.fullmatch(r"[0-9]{4}", year):
        print("Usage: python3 scripts/next_job_id.py <YYYY>", file=sys.stderr)
        sys.exit(1)
    try:
        print(next_job_id(load_jobs(resolve_data_root()), year))
    except (RuntimeError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
