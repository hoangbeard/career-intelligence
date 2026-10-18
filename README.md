# rexcareer

> Job search workflows for AI coding agents. Analyse job descriptions, track
> applications, prepare for interviews, answer recruiters and review offers,
> with your data kept in your own private folder.

[![ci](https://github.com/hoangbeard-labs/rexcareer/actions/workflows/ci.yml/badge.svg)](https://github.com/hoangbeard-labs/rexcareer/actions/workflows/ci.yml)
[![security](https://github.com/hoangbeard-labs/rexcareer/actions/workflows/security.yml/badge.svg)](https://github.com/hoangbeard-labs/rexcareer/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Why

A job search produces a lot of scattered material: job descriptions, recruiter
chats, company research, CV versions, interview notes, offers. Chat assistants
forget it between sessions and score jobs against a vague idea of you.

rexcareer gives your agent a fixed method and a fixed place for everything:

- **Decision first.** Each job gets a short Decision Card with scores, risks and
  one recommendation.
- **Scored against you.** Fit comes from your verified work history and your
  own targets, never from a generic profile.
- **Honest by default.** Skills never invent experience and never copy
  confidential employer details into a CV.
- **Your data stays yours.** Tools live here; your data lives in a separate
  folder or private repo.

## What it does

| Ask your agent | Skill |
|---|---|
| "Set me up" (first run) | [`onboarding`](skills/onboarding.md) |
| "Analyze this JD" (link, file or text) | [`jd-pipeline`](skills/jd-pipeline.md) |
| "Research this company" | [`company-analysis`](skills/company-analysis.md) |
| "Is this salary fair?" | [`compensation-analysis`](skills/compensation-analysis.md) |
| "Compare these jobs" | [`compare-jobs`](skills/compare-jobs.md) |
| "Prepare me for the interview" | [`interview-prep`](skills/interview-prep.md) |
| "Reply to this recruiter" | [`recruiter-reply`](skills/recruiter-reply.md) |
| "Review this offer" | [`offer-review`](skills/offer-review.md) |
| "Add my last job to my history" | [`work-history`](skills/work-history.md) |

Supporting skills: [`job-evaluation`](skills/job-evaluation.md) and
[`career-prioritization`](skills/career-prioritization.md).

## Quick start

You use rexcareer through your own **private copy** of this repo (an
*instance*). Your data lives in its `data/` folder and is committed, so the
same job search opens on your laptop, in a cloud agent and on your phone.

Requires Node.js 20.11 or later, git, the GitHub CLI (`gh`, logged in) and one
of the supported agents.

```bash
git clone https://github.com/hoangbeard-labs/rexcareer.git
rexcareer/scripts/create-instance.sh <your-github-user>/career
cd career
```

The script creates a private GitHub repo, copies the skeleton into it, adds a
`data/` folder, and keeps this repo as the `upstream` remote. GitHub does not
allow a private fork of a public repo, which is why it copies instead.

Then open your agent in that folder and:

1. Say **"set me up"**. The onboarding skill asks a few questions (language,
   target roles, role mix, pay) and builds your work history from your CV or
   from a short interview.
2. Paste a job link or description and say **"analyze this JD"**.

Every skill ends with `node scripts/save.mjs`, which commits and pushes your
data. The next session, on any device, starts with `scripts/doctor.mjs` and
shows your open jobs and their next steps.

To get new skills later:

```bash
git fetch upstream && git merge upstream/main
```

Only change files under `data/` in your instance. Put personal preferences in
`data/instructions.md`; then upstream merges never conflict.

### Try the demo

`examples/demo-data` is a fictional security engineer with a finished job
analysis.

```bash
cp -R examples/demo-data /tmp/rexcareer-demo
export REXCAREER_DATA=/tmp/rexcareer-demo
```

Then ask: "analyze the JD in examples/jds/acme-fintech-cloud-security.md".
The demo is for trying the skills; nothing is saved to git outside an instance.

## Supported agents

`skills/` holds every workflow. `scripts/sync-wrappers.mjs` generates thin
wrappers that point to it.

| Agent | Reads |
|---|---|
| Claude Code | `CLAUDE.md` (imports `AGENTS.md`), `.claude/skills/` |
| Codex | `AGENTS.md`, `.agents/skills/` |
| Cursor | `AGENTS.md`, `.agents/skills/` |
| Kilo | `kilo.jsonc` (points to `AGENTS.md`), `.agents/skills/` |
| Oh My Pi | `AGENTS.md`, `.omp/skills/` |

Claude Code also runs `scripts/doctor.mjs` at every session start through
`.claude/settings.json`. Cursor runs it from `.cursor/environment.json`.

## Cloud agents and your phone

Work from anywhere with the same data. Setup:

**Claude Code on the web** (claude.ai/code, and the Code tab of the Claude
mobile app)

1. Install the Claude GitHub App on your private instance repo
   (github.com/apps/claude).
2. At claude.ai/code, create an environment for the repo with network access
   **Full**. Job sites are not on the default "Trusted" list, so job links
   would fail to load. "Custom" works too if you list your usual job sites.
3. Start a session on the repo and paste a job link. The session-start hook
   pulls your latest data; `save.mjs` pushes the result to `main`.
4. Back at your computer, `git pull`, or move the session to your terminal
   with `claude --teleport`.

**Cursor cloud agents**: enable cloud agents for the repo and allow internet
access for job sites. `.cursor/environment.json` runs the doctor on start.

Commits made in the cloud are not signed (there is no signing key there).
Do not turn on "require signed commits" for your instance repo.

## How it works

```mermaid
flowchart LR
  JD[Job description] --> P[jd-pipeline skill]
  Profile[profile/ in your data folder] --> P
  P --> Job[jobs/company/YYYY-MM-role/<br/>report.md, metadata.yml, cv.md]
  P --> Co[companies/company/profile.md]
  Job --> Index[build-index.mjs<br/>INDEX.md, index.json]
```

Your data folder (`data/` in your instance):

```text
data/
├── profile/career-profile.md     # targets, role mix, language, pay
├── profile/work-history/*.md     # the only evidence source
├── companies/<company>/profile.md
├── jobs/<company>/YYYY-MM-<role>/
├── reports/
├── instructions.md               # optional: your lasting preferences
├── memory.md                     # optional: facts agents keep across sessions
└── INDEX.md, index.json          # generated
```

Conventions are in [`AGENTS.md`](AGENTS.md). Output shapes are in
[`templates/`](templates/).

## Scripts

All scripts are plain Node.js with no dependencies.

| Command | Does |
|---|---|
| `scripts/create-instance.sh <owner>/<repo>` | Create your private instance |
| `node scripts/doctor.mjs [--session-start]` | Setup check, open jobs, next steps |
| `node scripts/save.mjs "<message>"` | Commit and push `data/`, fixing index and ID clashes |
| `node scripts/migrate.mjs [--write]` | Upgrade an older data folder (dry run first) |
| `node scripts/renumber-job.mjs <job dir>` | Give a job a new ID |
| `node scripts/guard.mjs` | Fail if personal data is about to enter the skeleton |
| `node scripts/init.mjs <path>` | Create an empty data folder |
| `node scripts/data-root.mjs` | Print the data folder in use |
| `node scripts/next-job-id.mjs <YYYY>` | Next free job ID |
| `node scripts/build-index.mjs [--check]` | Rebuild or check the index |
| `node scripts/sync-wrappers.mjs [--check]` | Regenerate or check agent wrappers |
| `npm test` | Run the tests |

## Privacy notes

- Keep your instance repo private. It holds CVs, pay and conversations.
- This repo never stores personal data. `examples/` is fictional, and
  `scripts/guard.mjs` (pre-commit and CI) refuses `data/` in the skeleton.
- Cloud agents copy your repo into their sandbox while they work. Use them
  only if you are fine with that provider seeing your data.
- Agents send what they read to their model provider. Check your agent's data
  settings before you use it with real data.

## Roadmap

- [ ] CV export to PDF (planned in a separate web app)
- [ ] More languages for templates
- [ ] Job tracker views

## License

[MIT](LICENSE) © Pham Huy Hoang (HoangBeard)
