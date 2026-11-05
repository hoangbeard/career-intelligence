---
name: job-evaluation
description: "The full job evaluation framework (company, technical and soft skill match, role mix, seniority, direction and growth, risks, scores, recommendation). Used by the JD pipeline, or when the user asks for a detailed evaluation of one job."
---

# Skill: Job evaluation framework

Use for every JD, recruiter message, hiring link or company opportunity.

## Goal

Decide whether the role is worth pursuing and how it compares with the user's
target path. Avoid generic summaries.

## Inputs

- JD, recruiter message and hiring link, when available.
- Company file: `<data>/jobs/<slug>/company.md`.
- Career profile: `<data>/profile/career-profile.md`.
- Work history: `<data>/profile/work-history/` (the only evidence source).

## Output

Fill `templates/job-report.md`: the Decision Card first, then the evidence. Each
step below names where its result goes. The card is at most 60 lines, so it
carries conclusions and the evidence section carries the detail. For `Skip` or
`Low Priority`, write the full card, then only risks and sources.

To understand the role, first group the responsibilities with an estimated
workload split and picture who would succeed in it. Those are working notes:
use them in the steps below, and do not add them to the report.

## Process

### 1. Company

Run `skills/company-analysis.md`. Summarise its eight sections in the **Company**
table of the card, with sources and confidence. Do not score the company again.

### 2. Technical match

Check every must-have (and a nice-to-have only when it will matter in the
interview) against work history. Evidence names the company and the year.

- **Strong:** direct evidence inside the evidence window.
- **Partial:** related work under another name.
- **Missing:** no evidence. Never put it on the CV.

Full table: **Requirement Match Matrix** in the evidence section. The card lists
what matches and what does not, separately for must-haves and nice-to-haves.

### 3. Soft skills

Take the signals from the JD: stakeholder influence, mentoring, communication,
working language, cross-team work, ambiguity. Match each against work history,
with the same scale and the same evidence rule as technical skills. Do not assume
a soft skill without evidence.

Full table: **Soft skills** in the evidence section. The card gets one row. Feedback
the user recorded about a skill (for example from an earlier interview) counts as
a gap to show.

### 4. Role mix

Estimate the real share of each role-mix dimension from the responsibilities.
Compare with the target and the rules in the career profile. The result goes in
the header line of the card.

### 5. Seniority

Infer the real level, not the title: Senior IC, Staff, Principal, Lead,
Manager, Head of. Explain why when it differs from the title or from the user's
current level. The result goes in the header line of the card.

### 6. Direction and growth

Run `skills/career-prioritization.md`. It fills **Direction** and **Growth in 2–3
years** on the card, and **Career** in the evidence section.

### 7. Gaps and risks

Look for gaps with real interview impact, and for: unrealistic expectations, scope
creep, role ambiguity, understaffing, heavy paperwork, firefighting culture,
limited authority, legacy constraints, low ownership.

Rate each one Minor, Moderate or Significant in the **Risks** table of the evidence
section, with a mitigation. The top three go on the card.

### 8. Recommendation

- Overall Match /100 and Career Acceleration /100. Weigh Overall Match with the
  weights in the career profile, if set.
- Apply the rules in "Effect on the decision" in `skills/company-analysis.md`.
- Recommendation, main reason, and next actions.
