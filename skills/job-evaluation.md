---
name: job-evaluation
description: "The full job evaluation framework (company, requirement match, role mix, seniority, gaps, risks, scores, recommendation). Used by the JD pipeline, or when the user asks for a detailed evaluation of one job."
---

# Skill: Job evaluation framework

Use for every JD, recruiter message, hiring link or company opportunity.

## Goal

Decide whether the role is worth pursuing and how it compares with the user's
target path. Avoid generic summaries.

## Inputs

- JD, recruiter message and hiring link, when available.
- Company profile: `<data>/companies/<slug>/profile.md`.
- Career profile: `<data>/profile/career-profile.md`.
- Work history: `<data>/profile/work-history/` (the only evidence source).

## Process

Start the output with the Decision Card (`templates/job-report.md`). For
`Skip` or `Low Priority`, give the card and risks only.

### 1. Snapshot

Company, role title, location, work mode, seniority inferred from the
responsibilities, domain, recommendation.

### 2. Company

Background, country, ownership, industry and business model, main products,
growth, stability, technology maturity, career upside.

| Area | Score /10 | Notes |
|---|---:|---|
| Business growth | | |
| Financial stability | | |
| Technology maturity | | |
| Innovation | | |
| Learning opportunity | | |
| Career opportunity | | |

### 3. Requirement Match Matrix

Check every must-have (and a nice-to-have only when it will matter in the
interview) against work history. Evidence names the company and the year.

| Requirement | Must/Nice | Evidence (company, year) | Match | Action |
|---|---|---|---|---|
| | Must | | Strong \| Partial \| Missing | Cover in CV / study / do not claim |

- **Strong:** direct evidence inside the evidence window.
- **Partial:** related work under another name.
- **Missing:** no evidence. Never put it on the CV.

### 4. Role mix

Estimate the real share of each role-mix dimension from the responsibilities.
Compare with the target and the rules in the career profile.

| Dimension | Estimated % | Evidence from JD |
|---|---:|---|

### 5. Soft skills

| Skill | Score /10 | Evidence |
|---|---:|---|

### 6. Responsibilities

Group the responsibilities. Use the groups that fit the field (for example
hands-on delivery, architecture, operations, leadership, stakeholder
management, governance, research). Estimate the workload split.

| Area | Estimated % | Notes |
|---|---:|---|

### 7. Seniority

Infer the real level, not the title: Senior IC, Staff, Principal, Lead,
Manager, Head of. Explain why.

### 8. Ideal candidate

Background, years of experience, technical depth, domain exposure,
certifications (mandatory, preferred, bonus) and the top 5 hiring signals.

### 9. Gaps

| Gap | Severity | Interview impact | Mitigation |
|---|---|---|---|

Severity: Minor, Moderate or Significant.

### 10. Risks

Look for: unrealistic expectations, scope creep, role ambiguity, understaffing,
heavy paperwork, firefighting culture, limited authority, legacy constraints,
low ownership.

| Risk | Level | Why it matters | Mitigation |
|---|---|---|---|

### 11. Recommendation

- Biggest advantages and biggest concerns.
- Overall Match /100 and Career Acceleration /100. Weigh Overall Match with the
  weights in the career profile, if set.
- Recommendation and next actions.
