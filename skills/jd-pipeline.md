---
name: jd-pipeline
description: "Analyze a job description end to end: capture and deduplicate it, score fit against work history, write the Decision Card and a tailored CV, and update the index. Use when the user shares a JD, a job link or file, or a recruiter message about a role."
---

# Skill: JD pipeline

Entry point when the user shares a job: "analyze this JD" plus a URL, text,
PDF, DOCX, image or a recruiter message.

Resolve `<data>` first (`node scripts/data-root.mjs`). Read
`<data>/profile/career-profile.md` and `<data>/profile/work-history/*.md`
before scoring.

## A. Capture and deduplicate

1. Get the JD text from the URL, file or message.
2. Check `<data>/index.json` for the same job: same `company_slug` and the same
   requisition (title plus the main responsibilities). If found, refresh that
   job. Do not allocate a new ID.
3. Search the web for duplicates only when the JD is thin (no company name,
   fewer than 8 bullets, or a hidden client). Record what you find in
   `source_urls`. Same title and city alone is not a duplicate.
4. For a new job:
   - `node scripts/next-job-id.mjs <YYYY>` (contact year);
   - create `<data>/jobs/<company-slug>/YYYY-MM-<role-slug>/` with `source.*`,
     `jd.md`, `metadata.yml` (`status: new`, from `templates/metadata.yml`),
     `notes.md`, `CONTEXT.md` (from `templates/context.md`) and `artifacts/`.
5. Contact details: if missing, ask once. Do not block the Decision Card.

## B. Extract

- Must-have vs nice-to-have requirements.
- Responsibilities, grouped.
- Role mix: estimate the share of each dimension in the profile's role mix.
- Who would succeed in this role.
- Company facts: merge into the company profile (`skills/company-analysis.md`).
- Culture or reputation signals: record source and confidence; keep them out of
  the skill scoring.

## C. Match against work history

Build the Requirement Match Matrix for every must-have
(`skills/job-evaluation.md`, section 3). Never invent evidence.

## D. Decide

Run `skills/job-evaluation.md` and `skills/career-prioritization.md`. Use
`skills/compensation-analysis.md` when pay is mentioned or unclear.

Recommendation: `Strong Apply`, `Apply`, `Apply If Interested`, `Needs Info`,
`Low Priority` or `Skip`. Use `Needs Info` when the job is worth chasing but a
key fact is missing.

For `Strong Apply`, `Apply`, `Apply If Interested`, or when the user says they
will apply, write a tailored CV to `artifacts/cv.md`:

- facts only from work history;
- follow the CV rules in the profile (layout, length, title rules);
- general skills and types of work only (see "Evidence and honesty" in
  `AGENTS.md`).

## E. Save and reply

1. `report.md`: Decision Card first, from `templates/job-report.md`. For `Skip`
   or `Low Priority`: card, risks and sources only. Keep the "Study" line on the
   card to 2–3 items. Do not create `interview-prep.md` here.
2. Update `CONTEXT.md` and `notes.md` (paths to artifacts).
3. Update `metadata.yml`: `status` (`analyzed` or `watching`), scores,
   `role_mix`, `recommendation`, `cv_markdown`, `last_checked_at`,
   `status_changed_at`.
4. If the job is (or just became) `interviewing`, run `skills/interview-prep.md`.
5. `node scripts/build-index.mjs`.
6. Reply with the full Decision Card.
