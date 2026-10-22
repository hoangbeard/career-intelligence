"""Small git helpers for the save and doctor scripts. Every call runs in `cwd`."""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def git(cwd: Path | str, args: list[str], allow_fail: bool = False, env: dict | None = None) -> str | None:
    """Runs git and returns stripped stdout. On failure returns None with
    allow_fail, else raises GitError."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if allow_fail:
            return None
        detail = (result.stderr or result.stdout or "").strip()
        raise GitError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def repo_top(path: Path | str) -> Path | None:
    """Top level of the git repository that contains `path`, or None."""
    out = git(path, ["rev-parse", "--show-toplevel"], allow_fail=True)
    return Path(out) if out else None


def has_remote(cwd: Path | str, name: str = "origin") -> bool:
    return name in (git(cwd, ["remote"], allow_fail=True) or "").split("\n")


def current_branch(cwd: Path | str) -> str | None:
    return git(cwd, ["rev-parse", "--abbrev-ref", "HEAD"], allow_fail=True)


def upstream_ref(cwd: Path | str) -> str | None:
    return git(cwd, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], allow_fail=True)


def is_clean(cwd: Path | str) -> bool:
    out = git(cwd, ["status", "--porcelain"], allow_fail=True)
    return out == ""


def conflicted_files(cwd: Path | str) -> list[str]:
    out = git(cwd, ["diff", "--name-only", "--diff-filter=U"], allow_fail=True) or ""
    return [f for f in out.split("\n") if f]
