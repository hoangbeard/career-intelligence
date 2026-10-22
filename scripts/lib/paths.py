"""Shared path helpers.

Data root: $CAREER_INTELLIGENCE_DATA, else <repo>/data. In the public skeleton
the data root is never committed (scripts/guard.py blocks it). In a private
instance, marked by the file .career-intelligence-instance, <repo>/data is
committed so that every clone, local or cloud, has the same data.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTANCE_MARKER = ".career-intelligence-instance"
DATA_ENV = "CAREER_INTELLIGENCE_DATA"


def is_instance(root: Path = REPO_ROOT) -> bool:
    """True in a private instance repo, false in the public skeleton."""
    return (root / INSTANCE_MARKER).exists()


def resolve_data_root(env: dict | None = None) -> Path:
    env = os.environ if env is None else env
    raw = (env.get(DATA_ENV) or "").strip()
    root = Path(raw) if raw else REPO_ROOT / "data"
    if raw and not root.is_absolute():
        root = Path.cwd() / root
    if not root.is_dir():
        hint = f"{DATA_ENV} points to {root}" if raw else f"no {DATA_ENV} and no {root}"
        raise RuntimeError(
            f"Data root not found ({hint}). "
            "Ask the agent to run the onboarding skill, or run: python3 scripts/init.py data"
        )
    # Real path, so it compares equal to what git reports (macOS: /var -> /private/var).
    return root.resolve()
