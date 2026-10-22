---
name: export-cv
description: "Export a job's tailored CV (artifacts/cv.md) to PDF with the CV template, check the page previews, and record the file in metadata. Used by the JD pipeline when the recommendation is Strong Apply or Apply, and when the user asks for the PDF, says they will apply, or wants to send the CV."
---

# Skill: Export CV to PDF

Resolve `<data>` first (`python3 scripts/data_root.py`). Find the job through
`<data>/index.json` (prefer the job ID).

## Steps

1. The job must have `artifacts/cv.md`. If not, write it first (see the CV step
   in `skills/jd-pipeline.md`) in the format of `templates/cv.md`.
2. Export:

   ```bash
   python3 scripts/export_cv.py <data>/jobs/<company-slug>/<slot>
   ```

   It writes `artifacts/<cv_file_pattern>.pdf` (pattern from the profile, for
   example `MaiNguyen_<Company>_<Role>`), one PNG per page in
   `artifacts/cv-preview/`, and sets `cv_pdf` in `metadata.yml`. Use
   `--name <FileName>` for a shorter name, such as a short role title.
3. If it says the PDF tools are not installed, run `scripts/setup-pdf.sh` once
   (needs internet; about one minute), then export again. If setup fails in a
   cloud session, say so plainly, keep `cv.md`, and note it in `CONTEXT.md`.
4. Open every `cv-preview/page-NN.png` and check: nothing cut off, no near-empty
   last page, the header and section titles look right. A warning that content
   "does not fit" means one block is taller than a page: shorten it.
5. If the profile CV rules set a page limit and the PDF is longer, shorten
   `cv.md` (facts only from work history) and export again.
6. Save: `python3 scripts/save.py "Export CV for <job ID>"` (commits the PDF
   and previews so the user can open them on any device).
7. Reply with the PDF path, the page count and anything you changed to make it
   fit. Do not change `cv_used`: that is the CV actually sent, which only the
   user confirms.
