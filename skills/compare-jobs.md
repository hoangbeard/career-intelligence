---
name: compare-jobs
description: "Compare and rank several jobs and recommend one. Use when the user asks to compare, rank or choose between jobs or offers."
---

# Skill: Compare jobs

A cross-job report. It does not belong to one job folder.

## Output

Use `templates/comparison.md`. Save to
`<data>/reports/comparison-YYYY-MM-<topic>.md`. Never save it inside
`jobs/`.

## Pick the jobs

1. Resolve each job through `<data>/index.json` (prefer the job ID). Do not
   guess from a similar name.
2. Read `metadata.yml` first, then `report.md`. Open `jd.md` or `notes.md`
   only when needed.
3. If the user gives a filter (month, domain, status…), filter `index.json`.
4. Include jobs in `watching` and jobs with `Needs Info`. `Needs Info` means
   worth chasing; never rank it with `Skip`.

## Ranking order

1. Career Acceleration toward the profile's target roles.
2. Overall Match.
3. Pay (keep facts and `Estimated` apart).
4. Risk.

## Content

- Scores in tables. State assumptions and open points.
- Separate facts from inference.
- If the role mix differs a lot between jobs, show it as its own row.
- End with **one** clear decision and the next action for it.

## Save

The comparison does not change any `metadata.yml`. Update metadata only if the
user decides to change a job's `status` or `priority`.

Then save: `python3 scripts/save.py "<what changed>"` (rebuilds the index, commits and pushes; see "Saving work" in `AGENTS.md`).
