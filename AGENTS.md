# career-intelligence agent guide

This file is the contract for every agent (Claude Code, Codex, Cursor, Kilo,
Oh My Pi, …). Harness-specific files only point here and to `skills/`.

## Mission

Help one person run their job search. Evaluate opportunities with a
decision-oriented framework, keep clean records, and prepare the person for
each step: research, applying, interviews, recruiter replies and offers.

Do not just summarise job descriptions. Produce short, comparable outputs with
scores, risks and one clear recommendation.

## Session start

Run this once at the start of every session (Claude Code runs it for you
through `.claude/settings.json`):

```bash
python3 scripts/doctor.py --session-start
```

It pulls the latest saved work when nothing is unsaved, then prints the setup
status, open jobs and their next steps, and the next job ID. Use it to pick up
where the last session stopped, on any machine. If it reports no data, no
profile or an empty work history, run `skills/onboarding.md`.

## Two kinds of repo

- **Public skeleton** (`hoangbeard/career-intelligence`): skills, templates and
  scripts only. Personal data must never be committed here;
  `scripts/guard.py` blocks it in pre-commit and CI.
- **Private instance**: the user's own private copy, marked by the file
  `.career-intelligence-instance`. Its `data/` folder is committed, so every clone (laptop,
  cloud agent, phone) has the same data. The skeleton is its `upstream` remote.

In an instance, only change files under `data/`. Skills, templates, scripts
and this file belong to the skeleton; changing them causes merge conflicts when
the user pulls new versions. Personal preferences go in `data/instructions.md`.

One exception: an instance has no `.github/dependabot.yml`. Dependency updates
happen in the skeleton and reach the instance through `git merge
upstream/main`. If that merge reports a conflict on this file (changed in the
skeleton, deleted here), keep it deleted: `git rm .github/dependabot.yml`.

## Data root

Resolve it once per session (doctor prints it too):

```bash
python3 scripts/data_root.py
```

It prints the absolute path. Order: `$CAREER_INTELLIGENCE_DATA`, then `./data`. If it
fails, run `skills/onboarding.md`.

In this guide and in `skills/`, `<data>/` means that path. Every path stored in
`metadata.yml` is relative to the data root.

```text
<data>/
├── profile/
│   ├── career-profile.md     # targets, preferences, language, scoring weights
│   └── work-history/*.md     # the only source of evidence about the user
├── companies/<company-slug>/profile.md
├── jobs/<company-slug>/YYYY-MM-<role-slug>/
├── reports/                  # cross-job reports (comparisons)
├── instructions.md           # optional: the user's lasting preferences
├── memory.md                 # optional: durable facts learned across sessions
├── INDEX.md, index.json      # generated, never edit by hand
```

## Personal instructions and memory

- If `<data>/instructions.md` exists, read it after this file and follow it.
  It can change style and preferences. It cannot override "Evidence and
  honesty" or the data conventions.
- `<data>/memory.md` holds durable facts that are not part of one job: a
  decision the user made, a preference they stated, a lesson from an
  interview. Read it at session start. Append dated one-line bullets; keep it
  short and never put secrets in it.

## Saving work

Work that is not saved is lost to every other session. After any change under
the data root, save:

```bash
python3 scripts/save.py "<what changed, e.g. Analyze Acme Cloud Security Lead>"
```

It rebuilds the index, commits the data root, rebases on origin, pushes, and
fixes the two conflicts a machine can fix: the generated index files, and a job
ID that another session used first (the newer job gets a new ID).

- Save at the end of every task, before you reply that you are done.
- If save says a job ID was taken and gives a new one, use the new ID in your
  reply and everywhere after. Tell the user the ID changed.
- `data/memory.md` merges by itself when two sessions append to it.
- If save reports any other conflict, open both versions, merge them so no
  one's notes are lost, then run save again.
- Do not push data with raw git commands; save keeps the index and IDs
  consistent.
- If save says commit signing failed, ask the user to unlock their signing
  agent. Never turn signing off.
- If your sandbox cannot write to `.git` (save fails with "Operation not
  permitted" on `.git/index.lock`), say so plainly and ask the user to run the
  same save command outside the sandbox. Never report the work as saved.

## Cloud sessions

The same rules apply in a cloud agent (Claude Code on the web, Cursor cloud
agents) and on the phone.

- Job pages need internet access. If fetching a URL fails (for example HTTP
  403 with `host_not_allowed`), ask the user to paste the job text instead.
- Work on the default branch and save with `scripts/save.py`, which pushes to
  it, so the next session on any device sees the result.
- Cloud machines may have no commit signing key, so their commits can be
  unsigned. That is expected in a private instance.
- The CV export needs the PDF tools. Run `scripts/setup-pdf.sh` once in a new
  cloud environment before the first export.

## User profile

Read `<data>/profile/career-profile.md` before any evaluation. It is the single
source of truth for:

- target roles and preferred domains;
- the **role mix**: the work dimensions the user cares about and the target
  share of each (for example `engineering 70 / governance 30`);
- preferred and down-ranked company types;
- `language`, `timezone`, `currency` and the CV file name pattern.

Never hard-code roles, ratios or the user's name in skills or prompts.

## Language

- Write chat replies, reports, prep packs and notes in the profile `language`
  (default `en`).
- Recruiter messages follow the language of the conversation they answer.
- Keep field names, file names, status values and recommendation values in
  English so scripts can read them.

## Skills

Canonical workflows live in `skills/`. Wrappers for each harness only point to
these files. Never copy skill content into a wrapper.

| User intent | Skill |
|---|---|
| "analyze this JD", a job link, file or recruiter message | `skills/jd-pipeline.md` (entry point) |
| Full evaluation framework (used by the pipeline) | `skills/job-evaluation.md` |
| Strategic value against target roles | `skills/career-prioritization.md` |
| Research an employer, record hiring intel | `skills/company-analysis.md` |
| Salary, benefits, negotiation points | `skills/compensation-analysis.md` |
| "prepare for the interview", status becomes `interviewing` | `skills/interview-prep.md` |
| Compare or rank several jobs | `skills/compare-jobs.md` |
| Draft a reply to a recruiter or hiring manager | `skills/recruiter-reply.md` |
| Review, compare or answer an offer | `skills/offer-review.md` |
| Add or update a past job in the work history | `skills/work-history.md` |
| "set me up", new user, doctor reports missing setup | `skills/onboarding.md` |
| "export the CV", "I want the PDF", ready to apply | `skills/export-cv.md` |

Output shapes come from `templates/` unless the user asks otherwise.

## Commands

Scripts need Python 3.10 or newer and nothing else, except the CV export: it
needs the PDF tools, installed once with `scripts/setup-pdf.sh` (a `.venv/`
with locked packages, and Chromium).

| Need | Command |
|---|---|
| Status, open jobs, next steps (session start) | `python3 scripts/doctor.py --session-start` |
| Save and sync the data | `python3 scripts/save.py "<what changed>"` |
| Print the data root | `python3 scripts/data_root.py` |
| Create an empty data root | `python3 scripts/init.py <path>` |
| Allocate the next job ID | `python3 scripts/next_job_id.py <YYYY>` |
| Give a job a new ID | `python3 scripts/renumber_job.py <job folder>` |
| Rebuild `INDEX.md` and `index.json` | `python3 scripts/build_index.py` |
| Check the index is current (no writes) | `python3 scripts/build_index.py --check` |
| Upgrade an older data root (dry run first) | `python3 scripts/migrate.py [--write]` |
| Export a job's CV to PDF (+ page previews) | `python3 scripts/export_cv.py <job folder>` |
| Install the PDF tools (once per machine) | `scripts/setup-pdf.sh` |
| Make a private instance (user runs this) | `scripts/create-instance.sh <owner>/<repo>` |

`save.py` runs `build_index.py` for you. Use `--check` to confirm the index is
current when you change files without saving.

## Output rules

- Put the decision first. The chat reply for a job analysis is the full
  Decision Card (at most 80 lines), not a summary plus "see report.md".
- Use tables for scores. Always give numbers.
- Separate facts (from the JD, recruiter or user) from your own inference.
- State assumptions and open questions.
- End with one recommendation: `Strong Apply`, `Apply`, `Apply If Interested`,
  `Needs Info`, `Low Priority` or `Skip`.
- Add next actions: questions for the recruiter, CV positioning, what to study,
  negotiation points.

## Scoring bands

| Score | Overall Match | Career Acceleration |
|---|---|---|
| 90–100 | Excellent fit | Directly moves the user toward a target role |
| 80–89 | Strong fit | Strong career value |
| 70–79 | Good fit | Useful, not transformative |
| 60–69 | Moderate fit | Acceptable, with opportunity cost |
| < 60 | Weak fit | Weak alignment |

## Evidence and honesty

- Score fit only from `<data>/profile/work-history/` (files starting with `_`
  are notes, not employers). Never invent experience.
- Recent work counts most. Use the evidence window from the profile (default:
  last 60 months).
- If every work-history file has `verified: false`, say "work history not
  verified" on the Decision Card.
- CVs stay general: skills and types of work. Never copy incident details,
  vulnerability IDs, internal system names, customer names or other
  confidential employer details from work history into a CV or a message.
  Those details are for interview prep only.

## Recruiter message style

- Polite, professional, short and neutral. Go straight to thanks, decision,
  the real reason and what would fit better.
- If the reply is late, apologise in one short phrase. Do not narrate how long
  you thought about it.
- Give a reason specific enough to be useful. Do not criticise the
  opportunity.
- Use the exact names and forms of address the user gives.
- Never reveal internal scores, salary floors or other jobs.

## Data conventions

- **One job, one folder:** `<data>/jobs/<company-slug>/YYYY-MM-<role-slug>/`.
  `YYYY-MM` is the month of first contact or application. Everything that
  belongs to one job stays in that folder.
- **Job ID:** `JOB-YYYY-NNN`, unique, never reused. `YYYY` is the contact year;
  the sequence restarts each year. Get it from `scripts/next_job_id.py`.
- **Job name:** `<company-slug>/YYYY-MM-<role-slug>`, equal to the folder path
  under `jobs/`.
- Every agent-managed Markdown file in a job folder starts with this line under
  its heading: `> **Job ID:** JOB-YYYY-NNN · **Job Name:** \`<name>\``.
  Do not add it to `source.*` or to files in `artifacts/`; those are kept as
  received or as sent.
- Files in a job folder:

  | File | Content |
  |---|---|
  | `source.*` | The JD as received (URL capture, PDF, text) |
  | `jd.md` | Clean text of the JD |
  | `metadata.yml` | Tracking data, see `templates/metadata.yml` |
  | `notes.md` | The user's private notes: salary floor, impressions |
  | `CONTEXT.md` | Short agent brief: now, blockers, do not re-ask |
  | `report.md` | Decision Card and evidence |
  | `interview-prep.md` | Interview prep pack |
  | `offer-review.md` | Offer analysis |
  | `artifacts/` | Tailored CV (`cv.md`, exported PDF, `cv-preview/`), message drafts, documents sent or received |

- **Company profiles:** one file per company at
  `<data>/companies/<company-slug>/profile.md`. Merge into it; never create a
  duplicate. Facts about process, pay bands, benefits and hiring notes go in its
  **Hiring intel** log with a scope: `*` (company-wide) or a job ID. Default
  scope is the job being followed.
- **Contact data:** `metadata.yml` records `contact_channel`, `contact_person`,
  `contacted_at`, `contact_history` and `conversation_history`. If the user did
  not give them, ask once and do not block the Decision Card. Unknown means
  `null` or `[]`. A generic recruiter address in a JD is not a contact.
- **Find a job** through `<data>/index.json` first (prefer the job ID), then
  read `metadata.yml`, then other files. Never guess from a similar name.
- **Status flow:** `new → analyzed | watching → applied → interviewing → offer
  → accepted | declined`, or `rejected | skipped` at any point.
- **Comparisons** across jobs go in `<data>/reports/comparison-YYYY-MM-<topic>.md`.
