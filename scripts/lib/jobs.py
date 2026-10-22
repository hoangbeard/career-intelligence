"""Loads job metadata from a data root and allocates job IDs."""

from __future__ import annotations

import re
from pathlib import Path

from .flat_yaml import parse_flat_yaml

JOB_ID = re.compile(r"^JOB-([0-9]{4})-([0-9]{3,})$")


def _dirs(path: Path) -> list[str]:
    if not path.exists():
        return []
    return sorted(e.name for e in path.iterdir() if e.is_dir() and not e.name.startswith("."))


def load_jobs(data_root: Path, allow_duplicates: bool = False) -> list[dict]:
    """Reads every <data>/jobs/<company>/<slot>/metadata.yml and validates IDs
    and names. With allow_duplicates, duplicate IDs are returned instead of
    rejected, so the save script can renumber them.

    Each job dict keeps the metadata keys in file order plus `_path`."""
    jobs_dir = data_root / "jobs"
    jobs: list[dict] = []
    seen: dict[str, str] = {}
    for company in _dirs(jobs_dir):
        for slot in _dirs(jobs_dir / company):
            meta_path = jobs_dir / company / slot / "metadata.yml"
            if not meta_path.exists():
                continue
            path = f"jobs/{company}/{slot}"
            meta = parse_flat_yaml(meta_path.read_text(encoding="utf-8"))
            job_id = meta.get("id")
            if not isinstance(job_id, str) or not JOB_ID.match(job_id):
                raise ValueError(f'{path}: invalid job id "{job_id if job_id is not None else ""}"')
            if job_id in seen and not allow_duplicates:
                raise ValueError(f"{path}: duplicate job id {job_id} (also in {seen[job_id]})")
            seen[job_id] = path
            expected = f"{company}/{slot}"
            if meta.get("name") != expected:
                name = meta.get("name")
                raise ValueError(f'{path}: name "{name if name is not None else ""}" must be "{expected}"')
            jobs.append({**meta, "_path": path})
    return jobs


def duplicate_groups(jobs: list[dict]) -> list[list[dict]]:
    """Groups of jobs that share an ID: [[job_a, job_b], ...]."""
    by_id: dict[str, list[dict]] = {}
    for job in jobs:
        by_id.setdefault(job["id"], []).append(job)
    return [group for group in by_id.values() if len(group) > 1]


def next_job_id(jobs: list[dict], year: int | str) -> str:
    """Next free ID for a year, given every job (duplicates allowed)."""
    highest = 0
    for job in jobs:
        m = JOB_ID.match(job["id"])
        if m and m.group(1) == str(year):
            highest = max(highest, int(m.group(2)))
    return f"JOB-{year}-{highest + 1:03d}"
