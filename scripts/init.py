#!/usr/bin/env python3
"""Creates an empty data root: python3 scripts/init.py <path>

Never overwrites existing files."""

import shutil
import sys
from pathlib import Path

from lib.paths import DATA_ENV, REPO_ROOT


def init(root: Path) -> list[str]:
    created = []
    for directory in ("profile/work-history", "companies", "jobs", "reports"):
        path = root / directory
        if not path.exists():
            path.mkdir(parents=True)
            (path / ".gitkeep").write_text("")
            created.append(f"{directory}/")

    for source, target in (("templates/career-profile.md", "profile/career-profile.md"),):
        path = root / target
        if not path.exists():
            shutil.copyfile(REPO_ROOT / source, path)
            created.append(target)

    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Job search data\n\nPersonal data for career-intelligence. Keep it in a private repo.\n"
            "Agents edit these files through the skills and save with `python3 scripts/save.py`.\n",
            encoding="utf-8",
        )
        created.append("README.md")
    return created


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/init.py <path>", file=sys.stderr)
        sys.exit(1)
    root = Path(sys.argv[1]).resolve()
    created = init(root)
    print(f"Created in {root}:\n  " + "\n  ".join(created) if created else f"{root} is already set up.")
    # <repo>/data needs no environment variable; any other place does.
    repo_data = REPO_ROOT / "data"
    in_repo = repo_data.exists() and root.resolve() == repo_data.resolve()
    export = "" if in_repo else f'  export {DATA_ENV}="{root}"\n'
    print(f'\nNext:\n{export}  ask your agent to "set me up" (onboarding skill), or edit profile/career-profile.md')
