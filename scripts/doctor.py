#!/usr/bin/env python3
"""Checks the setup and prints a short status so a new session (local or
cloud) can carry on where the last one stopped.

  python3 scripts/doctor.py                  check and print status
  python3 scripts/doctor.py --session-start  also fast-forward from origin first;
                                             never fails (used by session hooks)
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from pathlib import Path

from lib.flat_yaml import parse_front_matter
from lib.git import current_branch, git, has_remote, is_clean, repo_top, upstream_ref
from lib.jobs import duplicate_groups, load_jobs, next_job_id
from lib.paths import REPO_ROOT, is_instance, resolve_data_root

MIN_PYTHON = (3, 10)
ACTIVE = ["offer", "interviewing", "applied", "watching", "analyzed", "new"]
OPEN = ["offer", "interviewing", "applied", "watching"]


def next_step(data_root: Path, job: dict) -> str | None:
    """'- Next: ...' (or '- Blocker: ...') from a job's CONTEXT.md."""
    path = data_root / job["_path"] / "CONTEXT.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    for key in ("Next", "Blocker"):
        m = re.search(rf"^- {key}:\s*([^\r\n]+)$", text, flags=re.M)
        if not m:
            continue
        value = m.group(1)
        if not re.fullmatch(r"(none|-|n/a)?", value.strip(), flags=re.I) and not value.startswith("("):
            return f"{key.lower()}: {value.strip()}"
    return None


def profile_status(data_root: Path) -> list[str]:
    lines = []
    profile = data_root / "profile" / "career-profile.md"
    if not profile.exists():
        lines.append("career profile: missing (run the onboarding skill)")
    else:
        fm = parse_front_matter(profile.read_text(encoding="utf-8"))
        if not fm.get("language"):
            lines.append("career profile: no front matter (language, timezone, currency); run the onboarding skill")
        elif not fm.get("name") or "<" in str(fm["name"]):
            lines.append("career profile: not filled in yet (template placeholders); run the onboarding skill")
        else:
            lines.append(
                f"career profile: language {fm['language']}, timezone {fm.get('timezone') or '?'}, "
                f"currency {fm.get('currency') or '?'}"
            )
    directory = data_root / "profile" / "work-history"
    files = (
        [f for f in directory.iterdir() if f.name.endswith(".md") and not f.name.startswith("_")]
        if directory.exists()
        else []
    )
    verified = sum(1 for f in files if parse_front_matter(f.read_text(encoding="utf-8")).get("verified") == "true")
    lines.append(
        f"work history: {len(files)} employer file(s), {verified} verified"
        if files
        else "work history: empty (run the onboarding or work-history skill)"
    )
    return lines


def git_status(top: Path | None, data_root: Path, pull: bool) -> list[str]:
    if not top:
        return ["git: data root is not in a git repository; work is not saved anywhere"]
    lines = []
    if pull and has_remote(top) and upstream_ref(top):
        if is_clean(top):
            ok = git(top, ["pull", "--ff-only", "--quiet"], allow_fail=True)
            lines.append("git: could not fast-forward from origin (check `git status`)" if ok is None else "git: up to date with origin")
        else:
            lines.append("git: local changes present, did not pull")
    data_rel = os.path.relpath(data_root, top)
    dirty = [l for l in (git(top, ["status", "--porcelain", "--", data_rel], allow_fail=True) or "").split("\n") if l]
    if dirty:
        lines.append(f'git: {len(dirty)} unsaved change(s) in {data_rel}/ (run: python3 scripts/save.py "<message>")')
    if upstream_ref(top):
        ahead = int(git(top, ["rev-list", "--count", "@{u}..HEAD"], allow_fail=True) or 0)
        if ahead:
            lines.append(f'git: {ahead} commit(s) not pushed (run: python3 scripts/save.py "<message>")')
    branch = current_branch(top)
    if branch and branch not in ("main", "HEAD"):
        lines.append(f"git: on branch {branch}; saves go to this branch")
    return lines


def report(pull: bool = False) -> list[str]:
    out = []
    if sys.version_info < MIN_PYTHON:
        out.append(f"python: {sys.version.split()[0]} is too old; need {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer")

    try:
        data_root = resolve_data_root()
    except RuntimeError:
        out.append('data: none yet. Ask the agent to run the onboarding skill ("set me up").')
        if not is_instance():
            out.append(
                "note: this is the public skeleton; keep real data in a private instance (scripts/create-instance.sh)."
            )
        return out

    top = repo_top(data_root)
    out.extend(git_status(top, data_root, pull))
    private = is_instance() and str(data_root).startswith(str(REPO_ROOT))
    out.append(f"data root: {data_root}{' (private instance)' if private else ''}")
    out.extend(profile_status(data_root))

    jobs = load_jobs(data_root, allow_duplicates=True)
    for group in duplicate_groups(jobs):
        paths = " and ".join(j["_path"] for j in group)
        out.append(f"problem: duplicate {group[0]['id']} in {paths} (run: python3 scripts/renumber_job.py <newer job dir>)")
    counts = [(s, sum(1 for j in jobs if j.get("status") == s)) for s in ACTIVE]
    counts = [(s, n) for s, n in counts if n]
    open_text = f"; open: {', '.join(f'{n} {s}' for s, n in counts)}" if counts else ""
    out.append(f"jobs: {len(jobs)} total{open_text}; next ID {next_job_id(jobs, datetime.now().year)}")

    open_jobs = sorted((j for j in jobs if j.get("status") in OPEN), key=lambda j: (ACTIVE.index(j["status"]), j["id"]))
    for job in open_jobs[:12]:
        step = next_step(data_root, job)
        line = f"  {job['id']} {job['status']:<12} {job.get('role') or '?'} @ {job.get('company') or '?'}"
        out.append(f"{line} | {step}" if step else line)
    if len(open_jobs) > 12:
        out.append(f"  … {len(open_jobs) - 12} more in INDEX.md")
    return out


if __name__ == "__main__":
    session_start = "--session-start" in sys.argv
    try:
        lines = report(pull=session_start)
        print("\n".join(["career-intelligence status", *(l if l.startswith("  ") else f"- {l}" for l in lines)]))
    except Exception as error:  # noqa: BLE001 - a session hook must never fail
        print(f"career-intelligence status\n- problem: {error}")
        if not session_start:
            sys.exit(1)
