"""Tests for scripts/export_cv.py. They need the optional PDF tools
(scripts/setup-pdf.sh); without them they are skipped. CI runs them in the
`pdf` job."""

import os
import shutil
import subprocess
import sys
import unittest

from helpers import REPO_ROOT, add_job, temp_dir
from lib.paths import DATA_ENV

try:
    import export_cv
except ImportError:
    export_cv = None

CV = """---
name: MAI NGUYEN
header:
  - text: Cloud Security Engineer
  - text: <span class="iconify" data-icon="tabler:mail"></span> mai@example.com
    link: mailto:mai@example.com
    newLine: true
  - text: GitHub
    link: https://github.com/example
---

## Summary

Cloud security engineer.

## Experience

### Initech (fictional)

Senior Engineer
: 2022 - now

- Built guardrails.

\\newpage

## Education

University (fictional)
"""


@unittest.skipIf(export_cv is None, "PDF tools not installed (scripts/setup-pdf.sh)")
class RenderTest(unittest.TestCase):
    def test_renders_header_sections_icons_and_page_breaks(self):
        html = export_cv.render_cv_html(CV)
        self.assertTrue(html.startswith('<header class="resume-header">'))
        self.assertIn("<h1>MAI NGUYEN</h1>", html)
        self.assertNotIn("iconify", html, "iconify placeholders are dropped")
        self.assertIn('data-icon-name="mail"', html)
        self.assertIn('data-icon-name="github"', html)
        self.assertIn('<span class="resume-header-break"', html)
        self.assertEqual(html.count('<section class="resume-section">'), 3)
        self.assertIn('data-icon-name="briefcase"', html)
        self.assertIn("<dt>Senior Engineer</dt>", html)
        self.assertIn('data-page-break="true"', html)

    def test_cv_without_front_matter_has_no_header(self):
        html = export_cv.render_cv_html("# Mai Nguyen\n\n## Skills\n\n- AWS\n")
        self.assertTrue(html.startswith("<h1>Mai Nguyen</h1>"))

    def test_file_names(self):
        self.assertEqual(export_cv.ascii_words("Senior DevSecOps Engineer"), "SeniorDevSecOpsEngineer")
        self.assertEqual(export_cv.ascii_words("Kỹ sư bảo mật (Đà Nẵng)"), "KySuBaoMatDaNang")

    def test_set_cv_pdf_adds_then_replaces_the_field(self):
        meta = add_job(temp_dir(), "acme", "2026-01-a", "JOB-2026-001", extra='cv_markdown: "x/cv.md"\ncv_used: null\n')
        path = meta / "metadata.yml"
        export_cv.set_cv_pdf(path, "jobs/acme/2026-01-a/artifacts/A.pdf")
        self.assertIn('cv_markdown: "x/cv.md"\ncv_pdf: "jobs/acme/2026-01-a/artifacts/A.pdf"\ncv_used', path.read_text())
        export_cv.set_cv_pdf(path, "jobs/acme/2026-01-a/artifacts/B.pdf")
        self.assertEqual(path.read_text().count("cv_pdf:"), 1)
        self.assertIn('cv_pdf: "jobs/acme/2026-01-a/artifacts/B.pdf"', path.read_text())


def chromium_available() -> bool:
    if export_cv is None:
        return False
    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:  # noqa: BLE001
        return False


@unittest.skipUnless(chromium_available(), "Chromium for Playwright not installed (scripts/setup-pdf.sh)")
class ExportTest(unittest.TestCase):
    def test_exports_the_demo_job_and_records_cv_pdf(self):
        root = temp_dir()
        shutil.copytree(REPO_ROOT / "examples" / "demo-data", root, dirs_exist_ok=True)
        job = root / "jobs" / "globex-cloud" / "2026-10-application-security-lead"
        run = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "export_cv.py"), str(job), "--name", "Demo_CV"],
            env={**os.environ, DATA_ENV: str(root)},
            capture_output=True,
            text=True,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        pdf = job / "artifacts" / "Demo_CV.pdf"
        self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))
        self.assertTrue((job / "artifacts" / "cv-preview" / "page-01.png").exists())
        self.assertIn('cv_pdf: "jobs/globex-cloud/2026-10-application-security-lead/artifacts/Demo_CV.pdf"',
                      (job / "metadata.yml").read_text())

    def test_manual_page_break_starts_a_new_page(self):
        result = export_cv.export_pdf(CV, temp_dir() / "cv.pdf", None)
        self.assertEqual(result["pages"], 2)
        self.assertEqual(result["overflow"], [])


if __name__ == "__main__":
    unittest.main()
