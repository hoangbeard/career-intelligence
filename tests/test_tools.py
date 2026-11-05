import json
import unittest

from helpers import add_job, script, temp_dir
from guard import forbidden_paths
from lib.paths import INSTANCE_MARKER
from migrate import migrate, migrate_metadata


class GuardTest(unittest.TestCase):
    def test_blocks_data_and_the_instance_marker_in_the_skeleton_only(self):
        paths = [
            "README.md",
            "data/profile/career-profile.md",
            "./data/jobs/x/metadata.yml",
            INSTANCE_MARKER,
            "examples/demo-data/INDEX.md",
        ]
        self.assertEqual(
            forbidden_paths(paths, False),
            ["data/profile/career-profile.md", "./data/jobs/x/metadata.yml", INSTANCE_MARKER],
        )
        self.assertEqual(forbidden_paths(paths, True), [])

    def test_passes_on_this_repository(self):
        r = script("guard.py")
        self.assertEqual(r.code, 0, r.stderr)


class MigrateTest(unittest.TestCase):
    def test_turns_v4_metadata_into_v5_and_keeps_everything_else(self):
        v4 = '# comment\nid: "JOB-2025-001"\nname: "a/2025-01-x"\neng_grc_ratio: "70/30"\nnotes: "kept"\n'
        text, notes = migrate_metadata(v4)
        self.assertEqual(
            text, '# comment\nschema: 5\nid: "JOB-2025-001"\nname: "a/2025-01-x"\nrole_mix: "70/30"\nnotes: "kept"\n'
        )
        self.assertEqual(notes, ["add schema: 5", "eng_grc_ratio -> role_mix"])
        self.assertEqual(migrate_metadata(text)[1], [], "second run changes nothing")

    def test_dry_run_writes_nothing_write_applies_second_run_is_a_no_op(self):
        root = temp_dir()
        meta = add_job(root, "a", "2025-01-x", "JOB-2025-001", extra='eng_grc_ratio: "70/30"\n') / "metadata.yml"
        meta.write_text(meta.read_text().replace("schema: 5\n", ""))
        (root / "profile/work-history").mkdir(parents=True)
        (root / "profile/career-profile.md").write_text("# Hồ sơ\n\nNội dung cũ [cv](cv/missing.md)\n", encoding="utf-8")
        (root / "profile/work-history/README.md").write_text("# Index\n")
        before = meta.read_text()

        dry = migrate(root, [])
        self.assertEqual(len(dry["changes"]), 3)
        self.assertEqual(dry["broken"], ["profile/career-profile.md -> cv/missing.md"])
        self.assertEqual(meta.read_text(), before, "dry run writes nothing")

        migrate(root, ["--write", "--name", "Mai Nguyen", "--language", "vi", "--timezone", "+07:00", "--currency", "VND"])
        profile = (root / "profile/career-profile.md").read_text(encoding="utf-8")
        self.assertTrue(
            profile.startswith('---\nname: "Mai Nguyen"\nlanguage: "vi"\ntimezone: "+07:00"\ncurrency: "VND"')
        )
        self.assertIn('cv_file_pattern: "MaiNguyen_<Company>_<Role>"', profile)
        self.assertIn("# Hồ sơ\n\nNội dung cũ", profile, "old text kept")
        self.assertTrue((root / "profile/work-history/_index.md").exists())
        self.assertRegex(meta.read_text(), r"(?m)^schema: 5$")
        self.assertEqual(migrate(root, ["--write"])["changes"], [], "second run is a no-op")

    def _old_company_layout(self):
        root = temp_dir()
        job = add_job(root, "acme", "2026-01-a", "JOB-2026-001")
        (root / "companies/acme").mkdir(parents=True)
        (root / "companies/acme/profile.md").write_text('---\ncompany: "Acme"\n---\nSee companies/client/profile.md\n')
        (root / "companies/client").mkdir()
        (root / "companies/client/profile.md").write_text('---\ncompany: "Client"\n---\n')
        (root / "reports").mkdir()
        (root / "reports/comparison.md").write_text("`companies/acme/profile.md`\n")
        (root / "memory.md").write_text("- see companies/acme/profile.md\n")
        (job / "report.md").write_text(
            "Profile: companies/acme/profile.md, [ITviec](https://itviec.com/companies/acme/profile.md)\n"
        )
        kept = {
            job / "source.md": "companies/acme/profile.md\n",
            job / "jd.md": "companies/acme/profile.md\n",
            job / "artifacts/sent.md": "companies/acme/profile.md\n",
        }
        (job / "artifacts").mkdir()
        for path, text in kept.items():
            path.write_text(text)
        return root, job, kept

    def test_moves_company_profiles_into_jobs_and_updates_paths(self):
        root, job, kept = self._old_company_layout()

        dry = migrate(root, [])
        self.assertIn("companies/acme/profile.md -> jobs/acme/company.md", dry["changes"])
        self.assertTrue((root / "companies/acme/profile.md").exists(), "dry run writes nothing")
        self.assertNotIn("jobs/acme/company.md", (job / "report.md").read_text())

        migrate(root, ["--write"])
        self.assertFalse((root / "companies").exists())
        self.assertIn("See jobs/client/company.md", (root / "jobs/acme/company.md").read_text())
        self.assertTrue((root / "jobs/client/company.md").exists(), "a company without a job moves too")
        self.assertEqual((root / "reports/comparison.md").read_text(), "`jobs/acme/company.md`\n")
        self.assertEqual((root / "memory.md").read_text(), "- see jobs/acme/company.md\n")
        self.assertEqual(
            (job / "report.md").read_text(),
            "Profile: jobs/acme/company.md, [ITviec](https://itviec.com/companies/acme/profile.md)\n",
            "external URLs stay as they are",
        )
        for path, text in kept.items():
            self.assertEqual(path.read_text(), text, f"{path.name} is kept as received")
        self.assertEqual(migrate(root, ["--write"])["changes"], [], "second run is a no-op")

        script("build_index.py", [], root)
        index = json.loads((root / "index.json").read_text(encoding="utf-8"))
        self.assertEqual([c["path"] for c in index["companies"]], ["jobs/acme/company.md", "jobs/client/company.md"])
        self.assertEqual(index["job_count"], 1, "a company file is not a job")

    def test_a_company_at_both_places_is_a_conflict_and_nothing_is_lost(self):
        root, job, _ = self._old_company_layout()
        (root / "jobs/acme/company.md").write_text("newer\n")

        result = migrate(root, ["--write"])
        self.assertEqual(len(result["conflicts"]), 1)
        self.assertEqual((root / "jobs/acme/company.md").read_text(), "newer\n")
        self.assertTrue((root / "companies/acme/profile.md").exists())
        self.assertIn("companies/acme/profile.md", (job / "report.md").read_text(), "path stays valid")
        self.assertTrue((root / "jobs/client/company.md").exists(), "other companies still move")
        self.assertRegex(script("doctor.py", [], root).stdout, r"still in companies/")


class DoctorTest(unittest.TestCase):
    def test_reports_profile_open_jobs_with_next_steps_and_the_next_id(self):
        root = temp_dir()
        self.assertEqual(script("init.py", [str(root)]).code, 0)
        job = add_job(root, "acme", "2026-01-a", "JOB-2026-004", status="interviewing")
        (job / "CONTEXT.md").write_text(
            "# CONTEXT\n\n## Now\n\n- Status: interviewing\n- Next: 2026-11-03 panel interview\n"
        )
        r = script("doctor.py", [], root)
        self.assertEqual(r.code, 0, r.stderr)
        self.assertIn("career profile: not filled in yet", r.stdout)
        self.assertIn("work history: empty", r.stdout)
        self.assertRegex(r.stdout, r"JOB-2026-004 interviewing .*next: 2026-11-03 panel interview")
        self.assertRegex(r.stdout, r"next ID JOB-\d{4}-\d{3}")

    def test_never_fails_at_session_start_even_without_data(self):
        r = script("doctor.py", ["--session-start"], "/nonexistent/career-intelligence-data")
        self.assertEqual(r.code, 0)
        self.assertRegex(r.stdout, r"problem|onboarding")


if __name__ == "__main__":
    unittest.main()
