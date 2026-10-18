---
name: offer-review
description: "Analyse a job offer, compare it with the target and other options, plan the negotiation, and record the decision. Use when the user receives, negotiates, accepts or declines an offer."
---

# Skill: Offer review

## Find the job

Resolve the job through `<data>/index.json`. Set `status: offer` when the
offer arrives (update `status_changed_at`).

## Read

- The offer as received. Save the document or text in the job's
  `artifacts/` (for example `offer-YYYY-MM-DD.pdf` or `.md`).
- `report.md`, `notes.md` (floor, target, what was already said), the company
  Hiring intel and the career profile.
- Other active jobs in `interviewing` or `offer`, from `index.json`.

## Analyse

Write `offer-review.md` in the job folder from `templates/offer-review.md`:

1. **Terms:** title, level, start date, base, bonus, equity with vesting,
   benefits, work mode, probation, notice period, non-compete or other
   restrictive clauses. Mark anything missing or vague.
2. **Total package per year** in the profile `currency`, with the
   assumptions used.
3. **Against the user's numbers:** floor, target and the current package, if
   the profile or notes have them.
4. **Against the market** (`skills/compensation-analysis.md`), labelled
   `Estimated` when not sourced.
5. **Did the role change?** Compare title, scope and level with the JD and the
   interviews.
6. **Risks:** contract clauses, team or company signals from the process.
7. **Other options:** how it ranks against other active jobs. Use
   `skills/compare-jobs.md` if there are two or more offers.

## Negotiate

- What to ask for, in priority order, with the reason for each.
- A realistic counter-offer range.
- Non-salary items: start date, title, remote days, training budget, equity.
- A short script for the call and a written follow-up. Draft messages with
  `skills/recruiter-reply.md`.

Never reveal the user's floor or other offers' details unless the user decides
to.

## Decide

End with one recommendation: `Accept`, `Negotiate`, `Wait` (with what to wait
for) or `Decline`, and the next action with a date.

## Save

1. `offer-review.md` and the offer in `artifacts/`.
2. Pay and benefit facts from the offer: company Hiring intel, scoped to the
   job.
3. On the final answer: `status: accepted` or `declined`, `status_changed_at`,
   reason in `notes.md`. If accepted, offer to close other active jobs politely.
4. Save: `node scripts/save.mjs "<what changed>"` (rebuilds the index, commits and pushes; see "Saving work" in `AGENTS.md`).
