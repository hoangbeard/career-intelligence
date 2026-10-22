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
