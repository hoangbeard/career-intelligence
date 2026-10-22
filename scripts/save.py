#!/usr/bin/env python3
"""Saves the data root to git so any other session (another machine, a cloud
agent, the phone) continues from the same state.

  python3 scripts/save.py "<what changed>"

Steps: rebuild the index, commit the data root, rebase on origin, fix the two
conflicts that can be fixed by machine (generated index files, a job ID taken
by another session), then push. Anything else stops with a clear message and
leaves your commit in place.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from lib.git import GitError, conflicted_files, git, has_remote, repo_top, upstream_ref
from lib.jobs import duplicate_groups, load_jobs
from lib.paths import DATA_ENV, REPO_ROOT, is_instance, resolve_data_root
from renumber_job import renumber_job

GENERATED = ["INDEX.md", "index.json"]


class SaveError(RuntimeError):
    pass


def build_index(data_root: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build_index.py")],
        env={**os.environ, DATA_ENV: str(data_root)},
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise SaveError(f"build_index failed: {result.stderr.strip()}")


def rebase_in_progress(top: Path) -> bool:
    git_dir = Path(git(top, ["rev-parse", "--git-dir"]))
    if not git_dir.is_absolute():
        git_dir = top / git_dir
    return (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists()


def rebase(top: Path, data_rel: str) -> None:
    """Rebase on the remote. Conflicts limited to the generated index are
    solved by taking the remote copy for now; save() rebuilds it once IDs are
    fixed. Any other conflict aborts the rebase and raises."""
    generated = {f if data_rel == "." else f"{data_rel}/{f}" for f in GENERATED}
    # Nothing new on the remote: push as is. Rebasing here would replay merge
    # commits (such as a merge from the skeleton upstream) as new commits.
    if git(top, ["merge-base", "--is-ancestor", "@{u}", "HEAD"], allow_fail=True) is not None:
        return
    # --rebase-merges keeps merge commits, so the upstream history stays shared.
    if git(top, ["rebase", "--rebase-merges", "@{u}"], allow_fail=True) is not None:
        return
    env = {**os.environ, "GIT_EDITOR": "true"}
    for _ in range(50):
        if not rebase_in_progress(top):
            break
        conflicts = conflicted_files(top)
        other = [f for f in conflicts if f not in generated]
        if other:
            git(top, ["rebase", "--abort"], allow_fail=True)
            raise SaveError(
                f"conflict in {', '.join(other)}. Your commit is kept locally. "
                "Pull, merge those files by hand (or ask the agent), then run save again."
            )
        if conflicts:
            git(top, ["checkout", "--ours", "--", *conflicts])
            git(top, ["add", "--", *conflicts])
        if git(top, ["rebase", "--continue"], allow_fail=True, env=env) is None:
            # Either the next commit conflicts (loop again) or there was nothing left to commit.
            if rebase_in_progress(top) and not conflicted_files(top):
                git(top, ["rebase", "--skip"], allow_fail=True, env=env)


def fix_duplicate_ids(top: Path, data_root: Path) -> list[str]:
    """Jobs added locally that reuse an ID someone else pushed first get a new ID."""
    changed = set((git(top, ["diff", "--name-only", "@{u}..HEAD"], allow_fail=True) or "").split("\n"))
    notes = []
    for group in duplicate_groups(load_jobs(data_root, allow_duplicates=True)):
        local = [j for j in group if os.path.relpath(data_root / j["_path"] / "metadata.yml", top) in changed]
        keep = next((j for j in group if j not in local), group[0])
        for job in group:
            if job is keep:
                continue
            r = renumber_job(data_root, data_root / job["_path"])
            notes.append(f"{r['job_path']}: {r['old_id']} was taken, now {r['new_id']}")
            notes.extend(f"warning: {w}" for w in r["warnings"])
    return notes


def has_staged_changes(top: Path) -> bool:
    return git(top, ["diff", "--cached", "--quiet"], allow_fail=True) is None


def save(message: str, push: bool = True) -> list[str]:
    data_root = resolve_data_root()
    top = repo_top(data_root)
    if not top:
        raise SaveError(f"{data_root} is not in a git repository; nothing to save to")
    if top.resolve() == REPO_ROOT and not is_instance():
        raise SaveError(
            "this is the public career-intelligence skeleton; keep real data in a private instance "
            "(scripts/create-instance.sh)"
        )
    data_rel = os.path.relpath(data_root, top)
    log = []

    build_index(data_root)
    git(top, ["add", "-A", "--", data_rel])
    if has_staged_changes(top):
        try:
            git(top, ["commit", "-q", "-m", message])
        except GitError as error:
            raise SaveError(
                f"commit failed ({error}). If commit signing is on, unlock your signing agent and run save again."
            ) from error
        log.append(f"committed: {message}")
    else:
        log.append("nothing new to commit")

    if not push or not has_remote(top) or not upstream_ref(top):
        log.append("no upstream branch; commit kept locally")
        return log

    for attempt in range(1, 4):
        git(top, ["fetch", "--quiet"])
        rebase(top, data_rel)
        notes = fix_duplicate_ids(top, data_root)
        build_index(data_root)
        git(top, ["add", "-A", "--", data_rel])
        if has_staged_changes(top):
            subject = "Renumber jobs whose ID was taken by another session" if notes else "Rebuild index after sync"
            git(top, ["commit", "-q", "-m", subject])
        log.extend(notes)
        if git(top, ["push", "--quiet"], allow_fail=True) is not None:
            log.append(f"pushed to {upstream_ref(top)}")
            return log
        log.append(f"push rejected (attempt {attempt}), retrying")
    raise SaveError("push failed three times; run `git status` and `git push` to see why")


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        print('Usage: python3 scripts/save.py "<what changed>"', file=sys.stderr)
        sys.exit(1)
    try:
        for line in save(text):
            print(line)
    except (RuntimeError, ValueError) as error:
        print(f"save: {error}", file=sys.stderr)
        sys.exit(1)
