---
name: company-analysis
description: "Research an employer, score it, and record hiring intel (process, pay bands, benefits) in its company profile. Use when the company is unknown or the user shares company facts."
---

# Skill: Company analysis

Use when the employer is unknown or the company profile is thin. Write or merge
into `<data>/companies/<company-slug>/profile.md` (`templates/company-profile.md`).

## Research

Legal entity and background, country, ownership and parent, industry and
business model, products, market position, size and maturity, funding or
revenue, reputation as an employer, technology maturity, regulatory pressure.

Cite sources. Mark anything you inferred.

## Classification

One or more of: product company, SaaS, platform, fintech, bank, insurance,
e-commerce, consulting, outsourcing, startup, scale-up, enterprise, public
sector.

## Output

| Area | Assessment | Score /10 |
|---|---|---:|
| Business quality | | |
| Growth potential | | |
| Financial stability | | |
| Technology maturity | | |
| Employer brand | | |
| Career leverage | | |

## Risks

Business model, industry cycles, regulation, ownership changes, culture and
execution, competition.

## Culture signals

Record source and confidence (`high`, `medium`, `low`). Do not lower skill
scores because of rumours. Leave `low` items off the Decision Card unless the
user asks.

## Hiring intel

When you learn a fact about the interview process, a pay band, benefits or a
hiring note:

- add a row to the **Hiring intel** log of the company profile;
- type: `process`, `compensation`, `benefits` or `note`;
- scope: the job ID being followed by default; `*` only when the user says so
  or the fact is clearly company-wide;
- never delete old rows; update `updated_at`;
- add the job to the **Applications** table of the profile.

The user's own strategy (salary floor, what they told the recruiter, how a
round felt) goes in the job's `notes.md`, not in Hiring intel.

## Save

After writing the company profile, save: `node scripts/save.mjs "<what changed>"` (rebuilds the index, commits and pushes; see "Saving work" in `AGENTS.md`). When this skill runs
inside another skill (for example the JD pipeline), that skill saves once at
the end instead.
