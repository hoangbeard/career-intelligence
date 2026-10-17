# rexcareer agent guide

This file is the contract for every agent (Claude Code, Codex, Cursor, Kilo,
Oh My Pi, …). Harness-specific files only point here and to `skills/`.

## Mission

Help one person run their job search. Evaluate opportunities with a
decision-oriented framework, keep clean records, and prepare the person for
each step: research, applying, interviews, recruiter replies and offers.

Do not just summarise job descriptions. Produce short, comparable outputs with
scores, risks and one clear recommendation.

## Data root

The tools in this repo hold no personal data. The user's data lives in a
separate **data root**.

Resolve it once per session:

```bash
node scripts/data-root.mjs
```

It prints the absolute path. Order: `$REXCAREER_DATA`, then `./data`. If it
fails, tell the user to run `node scripts/init.mjs <path>` and stop.

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
├── INDEX.md, index.json      # generated, never edit by hand
```

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

Output shapes come from `templates/` unless the user asks otherwise.

## Commands

All scripts use Node.js 20+ and have no dependencies.

| Need | Command |
|---|---|
| Print the data root | `node scripts/data-root.mjs` |
| Create an empty data root | `node scripts/init.mjs <path>` |
| Allocate the next job ID | `node scripts/next-job-id.mjs <YYYY>` |
| Rebuild `INDEX.md` and `index.json` | `node scripts/build-index.mjs` |
| Check the index is current (no writes) | `node scripts/build-index.mjs --check` |

Run `build-index.mjs` after every change to a `metadata.yml` or a company
profile. Use `--check` to confirm you did not forget.

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

- Score fit only from `<data>/profile/work-history/`. Never invent experience.
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
  the sequence restarts each year. Get it from `scripts/next-job-id.mjs`.
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
  | `artifacts/` | Tailored CV (`cv.md`), message drafts, documents sent or received |

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
