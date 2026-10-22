#!/usr/bin/env bash
# Creates your private career-intelligence instance: a private GitHub repo with the
# skeleton, a committed data/ folder, and the skeleton as the `upstream`
# remote so you can pull new skills later.
#
# GitHub does not allow a private fork of a public repo, so this copies the
# skeleton's history into a new private repo instead.
#
# Usage: scripts/create-instance.sh <owner>/<repo> [directory]
# Needs: git, Python 3.10+, and the GitHub CLI (gh) logged in.
set -euo pipefail

repo=${1:?usage: create-instance.sh <owner>/<repo> [directory]}
dir=${2:-$(basename "$repo")}
skeleton="$(cd "$(dirname "$0")/.." && pwd)"
upstream_url=${CAREER_INTELLIGENCE_UPSTREAM:-$(git -C "$skeleton" remote get-url origin)}

command -v gh >/dev/null || { echo "Install the GitHub CLI (gh) and run: gh auth login" >&2; exit 1; }
[ -e "$dir" ] && { echo "$dir already exists" >&2; exit 1; }
if gh repo view "$repo" >/dev/null 2>&1; then
  echo "$repo already exists on GitHub; pick another name" >&2
  exit 1
fi

echo "==> creating private repo $repo"
gh repo create "$repo" --private --description "My job search, run with career-intelligence" >/dev/null
origin_url=$(gh repo view "$repo" --json url --jq .url).git

echo "==> copying the skeleton into $dir"
git clone --quiet "$upstream_url" "$dir"
cd "$dir"
git remote rename origin upstream
git remote add origin "$origin_url"

touch .career-intelligence-instance
python3 scripts/init.py data >/dev/null
git add .career-intelligence-instance data
git commit --quiet -m "Create private career-intelligence instance"
git push --quiet -u origin main

cat <<MSG

Done: $repo (private), cloned in $dir.

Next:
  1. cd $dir and open your AI agent (Claude Code, Codex, Cursor...).
  2. Say "set me up": the onboarding skill asks for your profile and work history.
  3. Paste a job link or description.

Use it from your phone or any machine: see "Cloud agents" in README.md.
Get new skills later: git fetch upstream && git merge upstream/main
MSG
