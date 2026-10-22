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
Also reports relative Markdown links that point to missing files. Report and
note text is never rewritten.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from lib.paths import resolve_data_root


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

    # Walk again: --write may have renamed files.
    broken = []
    for path in _walk(data_root):
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"\]\(([^)\s]+)\)", text):
            target = m.group(1).split("#")[0]
            if not target or re.match(r"[a-z]+:", target, flags=re.I):
                continue
            if not os.path.exists(os.path.join(path.parent, unquote(target))):
                broken.append(f"{rel(path)} -> {target}")
    return {"write": write, "changes": changes, "broken": broken}


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
    if broken:
        print(f"\nBroken links, not changed ({len(broken)}):\n  " + "\n  ".join(broken))
    if not result["write"] and changes:
        print("\nRun again with --write to apply, then: python3 scripts/build_index.py")
