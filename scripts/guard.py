#!/usr/bin/env python3
"""Keeps personal data out of the public skeleton.

In the skeleton (no .career-intelligence-instance file) nothing under data/
and no instance marker may be committed. In a private instance the check passes.

  python3 scripts/guard.py [files...]   check the given paths (pre-commit passes staged files)
  python3 scripts/guard.py              check every file git tracks
"""

import subprocess
import sys

from lib.paths import INSTANCE_MARKER, REPO_ROOT, is_instance


def forbidden_paths(paths: list[str], instance: bool) -> list[str]:
    if instance:
        return []
    bad = []
    for p in paths:
        rel = p[2:] if p.startswith("./") else p
        if rel == "data" or rel.startswith("data/") or rel == INSTANCE_MARKER:
            bad.append(p)
    return bad


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout
    return [f for f in out.split("\0") if f]


if __name__ == "__main__":
    paths = sys.argv[1:] or tracked_files()
    bad = forbidden_paths(paths, is_instance())
    if bad:
        more = f"\n  … and {len(bad) - 20} more" if len(bad) > 20 else ""
        print(
            "guard: personal data must not be committed to the career-intelligence skeleton.\n  "
            + "\n  ".join(bad[:20])
            + more
            + "\nKeep your data in a private instance: scripts/create-instance.sh <owner>/<repo>",
            file=sys.stderr,
        )
        sys.exit(1)
