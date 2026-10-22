import json
import unittest

from helpers import REPO_ROOT, add_job, script, temp_dir


class ScriptsTest(unittest.TestCase):
    def test_data_root_fails_with_a_hint_when_the_folder_is_missing(self):
        r = script("data_root.py", [], "/nonexistent/career-intelligence-data")
        self.assertEqual(r.code, 1)
        self.assertIn("init.py", r.stderr)

    def test_init_creates_a_data_root_and_never_overwrites(self):
        root = temp_dir()
        self.assertEqual(script("init.py", [str(root)]).code, 0)
        for p in ["profile/career-profile.md", "profile/work-history", "companies", "jobs", "reports"]:
            self.assertTrue((root / p).exists(), p)
        (root / "profile/career-profile.md").write_text("mine")
        script("init.py", [str(root)])
        self.assertEqual((root / "profile/career-profile.md").read_text(), "mine")
        r = script("data_root.py", [], root)
        self.assertEqual(r.stdout.strip(), str(root.resolve()))

    def test_next_job_id_continues_the_sequence_per_year(self):
        root = temp_dir()
        self.assertEqual(script("next_job_id.py", ["2026"], root).stdout.strip(), "JOB-2026-001")
        add_job(root, "acme", "2026-01-a", "JOB-2026-007")
        add_job(root, "acme", "2025-12-b", "JOB-2025-030")
        self.assertEqual(script("next_job_id.py", ["2026"], root).stdout.strip(), "JOB-2026-008")
        self.assertEqual(script("next_job_id.py", ["26"], root).code, 1)

    def test_build_index_writes_checks_and_detects_drift(self):
        root = temp_dir()
        add_job(root, "acme", "2026-01-a", "JOB-2026-001", status="interviewing")
        add_job(root, "globex", "2026-02-b", "JOB-2026-002", status="accepted", extra='eng_grc_ratio: "80/20"\n')
        self.assertEqual(script("build_index.py", ["--check"], root).code, 1)
        self.assertEqual(script("build_index.py", [], root).code, 0)
        self.assertEqual(script("build_index.py", ["--check"], root).code, 0)

        index = json.loads((root / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["job_count"], 2)
        self.assertEqual(index["jobs"][1]["role_mix"], "80/20", "v4 eng_grc_ratio maps to role_mix")
        md = (root / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("### interviewing (1)", md)
        self.assertIn("### accepted (1)", md)

        add_job(root, "acme", "2026-03-c", "JOB-2026-003")
        self.assertEqual(script("build_index.py", ["--check"], root).code, 1)

    def test_build_index_rejects_duplicate_ids_and_wrong_names(self):
        dup = temp_dir()
        add_job(dup, "a", "2026-01-x", "JOB-2026-001")
        add_job(dup, "b", "2026-01-y", "JOB-2026-001")
        self.assertIn("duplicate job id", script("build_index.py", [], dup).stderr)

        bad = temp_dir()
        meta = add_job(bad, "a", "2026-01-x", "JOB-2026-001") / "metadata.yml"
        meta.write_text(meta.read_text().replace('name: "a/2026-01-x"', 'name: "a/other"'))
        self.assertIn('must be "a/2026-01-x"', script("build_index.py", [], bad).stderr)

    def test_demo_data_index_is_current(self):
        r = script("build_index.py", ["--check"], REPO_ROOT / "examples" / "demo-data")
        self.assertEqual(r.code, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
