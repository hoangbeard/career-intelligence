---
name: company-analysis
description: "Research an employer from public sources (history, business and finances, employee reviews, hiring, pay, interview process, leadership, controversies), score it, and record hiring intel in its company file. Use for every new job analysis, or when the user shares company facts."
---

# Skill: Company analysis

Runs for every new job analysis, because the Decision Card needs it. The company
file is `<data>/jobs/<company-slug>/company.md` (`templates/company-profile.md`).
Merge into it; never create a second file.

Reuse the research when `researched_at` is within the last 90 days. Otherwise
research and set `researched_at` to today. If the file still has an older
layout, move its content into the template sections and keep **Applications**
and **Hiring intel** complete. If only a section is missing, research that section.

## Research checklist

Cover all nine. Search the company's legal name and its local name.

| Section | Look for | Where to look |
|---|---|---|
| Overview | Legal entity, ownership, products, customers, offices | Company site, business registry |
| History | Dated milestones from founding to today: founding, ownership and funding changes, major acquisitions, expansions, the local office, leadership changes, crises | Company site, press releases, business registry, press |
| Finance and business | Revenue, funding, profit or loss, growth, layoffs | Filings, annual reports, press |
| Employee reviews | Rating, review count and date, recurring themes | Employer review sites and local job boards |
| Hiring activity | Open roles, freezes, turnover signals | Careers page, job boards, LinkedIn |
| Public pay range | Ranges for similar roles and levels | The JD, job boards, salary sites |
| Interview process | Rounds, length, difficulty | Interview review sites, candidate posts |
| Leadership | CEO or country head, function leader, recent changes | Company site, LinkedIn, press |
| Controversies | Lawsuits, fines, unpaid wages, mass layoffs, breaches, scandals | Press, regulators, court records, forums |

Also classify the company: product company, SaaS, platform, fintech, bank,
insurance, e-commerce, consulting, outsourcing, startup, scale-up, enterprise,
public sector.

## Reporting rules

- Give every finding its source and a confidence: `high`, `medium` or `low`.
  Mark inference as inference.
- When there is no finding, say which case it is:
  - `not found`: you searched and found nothing;
  - `not accessible`: the source blocked you;
  - `not checked`: you did not search.

  Never write "no controversies" unless you searched. `not found` means no
  public record was found, not that nothing happened.
- Treat self-reported figures and sponsored awards as the company's claim.
- Summarise reviews and articles in your own words. Do not paste them.
- If the employer is hidden behind an agency or an unnamed client, write
  `client unknown` and research the agency. Name a suspected client only as
  inference, with the evidence.

## Controversies

- Always show this row on the Decision Card, including `low` confidence items.
- Report an allegation as an allegation and say who made it. Mark an item
  without a credible source `unconfirmed`.
- Name only leaders with a public role. Do not name ordinary employees or
  reviewers.

## Effect on the decision

- Overall Match stays comparable across jobs: reviews and controversies never
  change it, nor the skill scores.
- A well-sourced red flag (unpaid wages, large layoffs, serious legal action)
  can lower the recommendation. Say so on the card and give the reason.
- An unconfirmed item can only become a question to ask or a point to check.

## Assessment

Score the **Assessment** table in the company file once per research. Reports
link to it and do not score the company again.

## Hiring intel

When you learn a fact about the interview process, a pay band, benefits or a
hiring note while following a job:

- add a row to the **Hiring intel** log of the company file;
- type: `process`, `compensation`, `benefits` or `note`;
- scope: the job ID being followed by default; `*` only when the user says so
  or the fact is clearly company-wide;
- never delete old rows; update `updated_at`;
- add the job to the **Applications** table.

The user's own strategy (salary floor, what they told the recruiter, how a
round felt) goes in the job's `notes.md`, not in Hiring intel.

## Save

After writing the company file, save: `python3 scripts/save.py "<what changed>"` (rebuilds the index, commits and pushes; see "Saving work" in `AGENTS.md`). When this skill runs
inside another skill (for example the JD pipeline), that skill saves once at
the end instead.
