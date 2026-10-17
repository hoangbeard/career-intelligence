---
name: recruiter-reply
description: "Draft a reply to a recruiter, hiring manager or agency (accept, decline, postpone, ask for details, follow up) and log the conversation. Use when the user needs to answer a recruiter message."
---

# Skill: Recruiter reply

## Style

Follow "Recruiter message style" in `AGENTS.md`. Do not restate those rules
here.

Write in the language of the conversation you answer. If there is none, use
the profile `language`.

## Before writing

1. Resolve the job through `<data>/index.json`. Mention the job ID to the user,
   never in the message to the recruiter.
2. Read `metadata.yml`: `contact_person`, `contact_channel`,
   `contact_history`, `conversation_history`. Use the right name and form of
   address.
3. Read `report.md` (reasons to chase, risks) so that a reason to decline or a
   question matches the existing assessment. Do not invent new reasons.
4. If pay is the topic, check the company Hiring intel and `notes.md` so you
   never state a wrong or private number.

## Data limits

- Never put the user's floor, target or walk-away point in the message.
- Never reveal internal scores, the company assessment or other jobs.
- Never claim experience that is not in work history.

## Save

1. Save the draft in the job's `artifacts/`, for example
   `linkedin-reply-<name>.md` or `email-decline-<name>-YYYY-MM-DD.md`. No Job
   ID line in `artifacts/` files.
2. When the user confirms it was sent: add an entry to `contact_history` and
   `conversation_history`, update `last_checked_at`.
3. If the reply changes the status (`applied`, `skipped`, `declined`…): update
   `status` and `status_changed_at`, and write the reason in `notes.md`.
4. New facts from the recruiter (process, package, benefits): merge into the
   company Hiring intel, scoped to the job.
5. `node scripts/build-index.mjs` after any metadata change.

## Reply

Return the message ready to copy and paste. Add one or two lines with the job
ID and any assumption you made.
