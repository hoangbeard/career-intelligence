#!/usr/bin/env python3
"""Brings an older data root up to the current format. Dry run by default.

  python3 scripts/migrate.py                 show what would change
  python3 scripts/migrate.py --write         apply the changes
  options for a profile without front matter:
    --name "<Full Name>" --language vi --timezone +07:00 --currency VND --location "<City, Country>"

Changes (each one is skipped when already done, so running twice is safe):
  - jobs/*/*/metadata.yml: add `schema: 5`; rename `eng_grc_ratio` to `role_mix`.
    Other keys and every value are kept as they are.
  - profile/career-profile.md: add the front matter block if it has none.
  - profile/work-history/README.md: rename to _index.md (files starting with
    "_" are not employer files).
  - companies/<slug>/profile.md: move to jobs/<slug>/company.md and update
    mentions of the old path in job files, reports/ and memory.md. Never touches
    source.*, jd.md or artifacts/ (kept as received or as sent). A company with a
    file at both places is reported as a conflict and left alone.
Also reports relative Markdown links that point to missing files. Apart from
the old company path, report and note text is never rewritten.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from lib.paths import resolve_data_root

# A path from the data root, not part of a URL such as itviec.com/companies/x/profile.md.
OLD_COMPANY_PATH = re.compile(r"(?<![\w./:-])companies/([a-z0-9][a-z0-9-]*)/profile\.md")
JOB_FILES_WITH_PATHS = {"report.md", "notes.md", "CONTEXT.md", "interview-prep.md", "offer-review.md", "metadata.yml"}


def _option(argv: list[str], name: str, fallback: str) -> str:
    flag = f"--{name}"
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv) and argv[i + 1]:
            return argv[i + 1]
    return fallback


def _walk(directory: Path) -> list[Path]:
    out: list[Path] = []
    for entry in sorted(directory.iterdir(), key=lambda p: p.name):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            out.extend(_walk(entry))
        else:
            out.append(entry)
    return out


def migrate_metadata(text: str) -> tuple[str, list[str]]:
    updated = text
    notes = []
    if not re.search(r"^schema:", updated, flags=re.M):
        # After any leading comment lines, before the first key.
        lines = updated.split("\n")
        at = next((i for i, line in enumerate(lines) if re.match(r"[A-Za-z_]", line)), len(lines))
        lines.insert(at, "schema: 5")
        updated = "\n".join(lines)
        notes.append("add schema: 5")
    if re.search(r"^eng_grc_ratio:", updated, flags=re.M) and not re.search(r"^role_mix:", updated, flags=re.M):
        updated = re.sub(r"^eng_grc_ratio:", "role_mix:", updated, count=1, flags=re.M)
        notes.append("eng_grc_ratio -> role_mix")
    return updated, notes


def profile_front_matter(name: str, language: str, timezone: str, currency: str, location: str) -> str:
    def q(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)

    pattern = re.sub(r"\s+", "", name) + "_<Company>_<Role>"
    return "\n".join(
        [
            "---",
            f"name: {q(name)}",
            f"language: {q(language)}",
            f"timezone: {q(timezone)}",
            f"currency: {q(currency)}",
            f"location: {q(location)}",
            f"cv_file_pattern: {q(pattern)}",
            "evidence_window_months: 60",
            "---",
            "",
        ]
    )


def _may_mention_company_path(rel_path: str) -> bool:
    parts = rel_path.split("/")
    if parts[0] == "jobs":
        return (len(parts) == 4 and parts[3] in JOB_FILES_WITH_PATHS) or (len(parts) == 3 and parts[2] == "company.md")
    if parts[0] == "reports":
        return rel_path.endswith(".md")
    return rel_path == "memory.md" or (parts[0] == "companies" and parts[-1] == "profile.md")


def _remove_empty_companies(old_root: Path) -> None:
    for directory in [*(p for p in old_root.iterdir() if p.is_dir()), old_root]:
        (directory / ".gitkeep").unlink(missing_ok=True)
        if not any(directory.iterdir()):
            directory.rmdir()


def migrate_companies(data_root: Path, write: bool) -> tuple[list[str], list[str]]:
    old_root = data_root / "companies"
    jobs_root = data_root / "jobs"
    if not old_root.is_dir():
        return [], []
    changes: list[str] = []
    conflicts: list[str] = []
    moved: set[str] = set()
    for source in sorted(old_root.glob("*/profile.md")):
        slug = source.parent.name
        target = jobs_root / slug / "company.md"
        if target.exists():
            conflicts.append(f"companies/{slug}/profile.md and jobs/{slug}/company.md both exist; merge them by hand")
            continue
        moved.add(slug)
        changes.append(f"companies/{slug}/profile.md -> jobs/{slug}/company.md")
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            source.rename(target)

    def new_path(match: re.Match) -> str:
        return f"jobs/{match.group(1)}/company.md" if match.group(1) in moved else match.group(0)

    for path in _walk(data_root):
        rel = path.relative_to(data_root).as_posix()
        if not _may_mention_company_path(rel):
            continue
        text = path.read_text(encoding="utf-8")
        updated = OLD_COMPANY_PATH.sub(new_path, text)
        if updated != text:
            changes.append(f"{rel}: update company profile path")
            if write:
                path.write_text(updated, encoding="utf-8", newline="")
    if write:
        _remove_empty_companies(old_root)
    return changes, conflicts


def migrate(data_root: Path, argv: list[str] | None = None) -> dict:
    argv = argv or []
    write = "--write" in argv
    changes: list[str] = []

    def rel(path: Path) -> str:
        return path.relative_to(data_root).as_posix()

    for path in _walk(data_root):
        if path.name != "metadata.yml" or not rel(path).startswith("jobs/"):
            continue
        text = path.read_text(encoding="utf-8")
        updated, notes = migrate_metadata(text)
        if notes:
            changes.append(f"{rel(path)}: {', '.join(notes)}")
            if write:
                path.write_text(updated, encoding="utf-8", newline="")

    profile = data_root / "profile" / "career-profile.md"
    if profile.exists():
        text = profile.read_text(encoding="utf-8")
        if not text.startswith("---"):
            fm = profile_front_matter(
                name=_option(argv, "name", "<Your Name>"),
                language=_option(argv, "language", "en"),
                timezone=_option(argv, "timezone", "+00:00"),
                currency=_option(argv, "currency", "USD"),
                location=_option(argv, "location", "<City, Country>"),
            )
            indented = re.sub(r"^", "    ", fm.rstrip(), flags=re.M)
            changes.append(f"profile/career-profile.md: add front matter\n{indented}")
            if write:
                profile.write_text(fm + text, encoding="utf-8", newline="")

    readme = data_root / "profile" / "work-history" / "README.md"
    if readme.exists():
        changes.append("profile/work-history/README.md -> profile/work-history/_index.md")
        if write:
            readme.rename(readme.with_name("_index.md"))

    company_changes, conflicts = migrate_companies(data_root, write)
    changes.extend(company_changes)

    # Walk again: --write may have renamed files. INDEX.md is generated, so its
    # links are fixed by build_index, not by hand.
    broken = []
    for path in _walk(data_root):
        if path.suffix != ".md" or rel(path) == "INDEX.md":
            continue
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"\]\(([^)\s]+)\)", text):
            target = m.group(1).split("#")[0]
            if not target or re.match(r"[a-z]+:", target, flags=re.I):
                continue
            if not os.path.exists(os.path.join(path.parent, unquote(target))):
                broken.append(f"{rel(path)} -> {target}")
    return {"write": write, "changes": changes, "conflicts": conflicts, "broken": broken}


if __name__ == "__main__":
    try:
        result = migrate(resolve_data_root(), sys.argv[1:])
    except (RuntimeError, OSError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    changes, broken = result["changes"], result["broken"]
    if changes:
        print(f"{'Changed' if result['write'] else 'Would change'} ({len(changes)}):\n  " + "\n  ".join(changes))
    else:
        print("Nothing to migrate.")
    if result["conflicts"]:
        print(f"\nConflicts, not changed ({len(result['conflicts'])}):\n  " + "\n  ".join(result["conflicts"]))
    if broken:
        print(f"\nBroken links, not changed ({len(broken)}):\n  " + "\n  ".join(broken))
    if not result["write"] and changes:
        print("\nRun again with --write to apply, then: python3 scripts/build_index.py")
