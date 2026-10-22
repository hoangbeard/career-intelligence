"""Shared test helpers. Tests always pass a temporary data root, or "" only
where a test checks that the skeleton has no data (see test_save.py)."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from lib.paths import DATA_ENV  # noqa: E402


@dataclass
class Result:
    code: int
    stdout: str
    stderr: str


def temp_dir(prefix: str = "career-intelligence-test-") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix)).resolve()


def add_job(root: Path, company: str, slot: str, job_id: str, status: str = "new", extra: str = "") -> Path:
    directory = root / "jobs" / company / slot
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "metadata.yml").write_text(
        f'schema: 5\nid: "{job_id}"\nname: "{company}/{slot}"\ncompany: "{company}"\ncompany_slug: "{company}"\n'
        f'role: "Engineer"\nstatus: "{status}"\ndomains: ["cloud-security"]\n{extra}',
        encoding="utf-8",
    )
    return directory


def script(name: str, args: list[str] | None = None, data_root: Path | str | None = None) -> Result:
    """Runs a script and returns its exit code and output without raising."""
    env = {**os.environ, DATA_ENV: "" if data_root is None else str(data_root)}
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / name), *(args or [])],
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
    )
    return Result(result.returncode, result.stdout, result.stderr)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
