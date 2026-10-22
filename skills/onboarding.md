---
name: onboarding
description: "Set up a new user: create the data folder if needed, fill the career profile from a few short questions, and build the work history from an existing CV or an interview. Use when the user says set me up or get started, or when doctor reports no data, no profile front matter or an empty work history."
---

# Skill: Onboarding

Goal: the user answers a few questions and shares their history once. After
that, every other skill works.

## 1. Check the setup

Run `python3 scripts/doctor.py` and read its status.

- **No data yet, in a private instance** (the repo has `.career-intelligence-instance`):
  run `python3 scripts/init.py data`.
- **No data yet, in the public skeleton** (no `.career-intelligence-instance`): stop.
  Personal data must not go into the public repo. Explain how to make a
  private copy: `scripts/create-instance.sh <owner>/<repo>` (see README), then
  continue there.
- Profile and work history already filled: tell the user, show the doctor
  status, and only fix what they ask for.

## 2. Career profile

Ask in **one** short message. Accept partial answers; never guess.

1. Full name, as it should appear on a CV.
2. Language for reports and chat (for example `en`, `vi`).
3. Time zone (offset such as `+07:00`), currency, city and country.
4. Two to four target roles.
5. The work dimensions they care about and the target share of each (the
   **role mix**, for example "hands-on engineering 70 / governance 30").
6. Optional: pay floor and target, preferred and avoided company types.

Write `<data>/profile/career-profile.md` from `templates/career-profile.md`:
front matter first, then the sections. Leave a section as `-` when the user
did not answer. Keep the default Overall Match weights unless they change
them.

## 3. Work history

Offer two ways and let the user pick:

- **From a CV or LinkedIn export** (file, PDF, or pasted text). Draft one file
  per employer from `templates/work-history.md` with `verified: false`. Put
  every number, date and title exactly as written. Then go through the files
  with the user to fill gaps: what they did **not** do, depth of each skill,
  why they left. Mark confidential detail with `Confidential:`.
- **Interview**: follow `skills/work-history.md`, one employer at a time,
  most recent first. The last 5 years matter most.

Set `verified: true` on a file only after the user confirms it.

## 4. Personal rules (optional)

If the user states lasting preferences ("never suggest agencies", "keep CVs to
one page", "write recruiter replies in English"), put them in
`<data>/instructions.md`. Agents read it after `AGENTS.md`. It cannot override
the evidence and honesty rules.

## 5. Save and next step

1. Save: `python3 scripts/save.py "Onboarding: profile and work history"`.
2. Run `python3 scripts/doctor.py` and show the result.
3. Tell the user what to do next: paste a job link, a JD or a recruiter
   message. They can do it from any device that opens this repo with an agent.
