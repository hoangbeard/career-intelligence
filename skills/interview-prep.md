---
name: interview-prep
description: "Build an interview prep pack for a job (study notes on core topics plus outlines for common questions). Use when the user says \"prepare for the interview\", when a job moves to interviewing, or when they share process, pay or hiring facts to record."
---

# Skill: Interview prep

Do not run the full pack during a JD analysis. The Decision Card keeps only a
2–3 item "Study" line. The JD pipeline calls this skill only when the job is,
or just became, `interviewing`.

## Goal

Write `<data>/jobs/.../interview-prep.md` from `templates/interview-prep.md`.
Two parts. No scripts to memorise.

1. **Core topics as study notes.** After reading, the user understands each
   topic well enough to answer without searching. No one-line slogans. Each
   topic has: definition, why it matters for this role, how it works,
   components or stages mapped to techniques, practical use, common mistakes,
   a STAR story from real evidence, and what not to claim.
2. **Common and behavioural questions as outlines.** Short nested bullets, each
   with a "Do not say" line where overclaiming is likely.

If the interview process is known, map topics to rounds in a few lines.

## Find the job

1. The job the user named, through `<data>/index.json` (prefer the job ID).
2. Otherwise the only job with `status: interviewing`.
3. Still unclear: ask once. Do not guess.

## Read

1. The job's `metadata.yml`, `jd.md`, `report.md`, `notes.md`, `CONTEXT.md`.
2. The company profile: Hiring intel rows for `*` and for this job ID.
3. `<data>/profile/work-history/*.md`: evidence and the "Why I left" notes.
4. Standard references of the field for the study notes. Summarise; never
   invent personal experience.

## Writing rules

- Pick 5–8 core topics from the must-haves. Skip weak nice-to-haves.
- About half a page to one page per topic.
- A good topic names the stages or parts and the technique at each one, not
  only a list of tool names.
- STAR stories come only from work history. For a gap, write "study the
  concept; no work evidence".
- "Why are you leaving" and "why this company" come from work history and the
  JD. Never invent.

## Where facts go

| Kind | Place |
|---|---|
| Process, pay band, benefits, hiring note | Company profile, Hiring intel |
| Salary floor, what was said, how a round felt | Job `notes.md` (and `CONTEXT.md` if needed) |
| The prep pack | Job `interview-prep.md` (not in `artifacts/`) |

If the user only shares intel, merge it and rebuild the index. Refresh the pack
only when the job is `interviewing` or the user asks.

## Save

1. Write `interview-prep.md`.
2. Set `interview_prep` in `metadata.yml`.
3. Update `CONTEXT.md` and `notes.md` with new rounds.
4. Merge new Hiring intel.
5. `node scripts/build-index.mjs`.

## Reply

Return the whole pack, not a link. If you only merged intel, confirm in one or
two lines with the scope and the job ID.
