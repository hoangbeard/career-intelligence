#!/usr/bin/env python3
"""Gives a job a new free ID, for example after two sessions picked the same
one. Updates metadata.yml and the "Job ID" line of the job's Markdown files
(never source.* or artifacts/).

Also updates the company profile when that is safe: if no other job of the
same company holds the old ID, every mention of it there means this job.

  python3 scripts/renumber_job.py <data>/jobs/<company>/<slot>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from lib.flat_yaml import parse_flat_yaml
from lib.jobs import JOB_ID, load_jobs, next_job_id
from lib.paths import resolve_data_root


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")


def renumber_job(data_root: Path, job_dir: Path) -> dict:
    meta_path = job_dir / "metadata.yml"
    if not meta_path.exists():
        raise ValueError(f"{job_dir}: no metadata.yml")
    meta_text = _read(meta_path)
    meta = parse_flat_yaml(meta_text)
    old_id = meta.get("id") or ""
    m = JOB_ID.match(old_id)
    if not m:
        raise ValueError(f'{job_dir}: invalid job id "{old_id}"')

    others = [
        j for j in load_jobs(data_root, allow_duplicates=True) if (data_root / j["_path"]).resolve() != job_dir.resolve()
    ]
    new_id = next_job_id([*others, {"id": old_id}], m.group(1))

    _write(meta_path, re.sub(r"^id:\s*[^\r\n]*$", f'id: "{new_id}"', meta_text, count=1, flags=re.M))
    changed = ["metadata.yml"]
    job_id_line = re.compile(r"(\*\*Job ID:\*\* )" + re.escape(old_id) + r"\b")
    for path in sorted(job_dir.iterdir()):
        if not path.is_file() or not path.name.endswith(".md") or path.name.startswith("source."):
            continue
        text = _read(path)
        updated = job_id_line.sub(lambda mm: mm.group(1) + new_id, text)
        if updated != text:
            _write(path, updated)
            changed.append(path.name)

    company = meta.get("company_slug")
    same_company_clash = any(j["id"] == old_id and j.get("company_slug") == company for j in others)
    warnings = []
    profile = data_root / "companies" / company / "profile.md" if company else None
    if profile and profile.exists():
        text = _read(profile)
        if old_id in text:
            if same_company_clash:
                warnings.append(
                    f"companies/{company}/profile.md mentions {old_id}; two jobs of this company had it, fix by hand"
                )
            else:
                _write(profile, re.sub(r"\b" + re.escape(old_id) + r"\b", new_id, text))
                changed.append(f"companies/{company}/profile.md")
    return {
        "old_id": old_id,
        "new_id": new_id,
        "changed": changed,
        "warnings": warnings,
        "job_path": job_dir.resolve().relative_to(data_root).as_posix(),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/renumber_job.py <job folder>", file=sys.stderr)
        sys.exit(1)
    try:
        r = renumber_job(resolve_data_root(), Path(sys.argv[1]).resolve())
    except (RuntimeError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    print(f"{r['job_path']}: {r['old_id']} -> {r['new_id']} ({', '.join(r['changed'])})")
    for w in r["warnings"]:
        print(f"warning: {w}")
    print(f"Check reports/ for other mentions of {r['old_id']}.")
