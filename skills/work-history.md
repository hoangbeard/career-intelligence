---
name: work-history
description: "Add or update a past job in the user's work history, the only evidence source for scoring and CVs. Use when the user describes past work, a new role, or asks to fix their history."
---

# Skill: Work history

Work history is the only evidence source. Scoring, CVs and interview stories
all depend on it, so accuracy matters more than polish.

## Files

One file per employer: `<data>/profile/work-history/<company-slug>.md`, from
`templates/work-history.md`. Several roles at one employer stay in one file.
Files whose name starts with `_` (for example `_index.md`) are notes, not
employer files: do not score from them.

## Interview the user

Ask short questions, a few at a time:

1. Employer, dates (`YYYY-MM`), real titles.
2. Team, reporting line, what they owned.
3. Main work, grouped by theme. For each: what they did, the result, and a
   number only if they are sure of it.
4. Tools and skills used, with depth (`expert`, `working`, `familiar`) and the
   last time used.
5. What they did **not** do, so it is never claimed.
6. Why they left, in words they are comfortable saying in an interview.

Do not fill gaps with guesses. Write "unknown" and ask.

## Confidential details

The file may hold detail for interview prep. Mark anything confidential
(incident details, internal system or customer names, vulnerability IDs,
exact figures under NDA) with a `Confidential:` prefix. Skills must never copy
those lines into a CV or a message.

## Save

1. Write or merge the file. Keep earlier content unless the user corrects it.
2. Set `verified: true` only after the user reads the file and confirms it.
3. Save: `python3 scripts/save.py "<what changed>"` (rebuilds the index, commits and pushes; see "Saving work" in `AGENTS.md`).
4. Tell the user which open jobs might score differently now. Offer to
   re-run the evaluation for them.
