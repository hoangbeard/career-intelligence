import shutil
import unittest

from helpers import REPO_ROOT, temp_dir
from sync_wrappers import load_skills, sync


class WrappersTest(unittest.TestCase):
    def test_committed_wrappers_match_skills(self):
        _, problems = sync(REPO_ROOT, check=True)
        self.assertEqual(problems, [])

    def test_every_skill_has_a_valid_name_and_description(self):
        skills = load_skills(REPO_ROOT)
        self.assertGreaterEqual(len(skills), 10)
        for s in skills:
            self.assertGreater(len(s["description"]), 40, s["name"])

    def test_check_reports_orphaned_and_edited_wrappers(self):
        root = temp_dir("career-intelligence-wrap-")
        shutil.copytree(REPO_ROOT / "skills", root / "skills")
        sync(root)
        (root / ".agents/skills/jd-pipeline/SKILL.md").write_text("edited")
        shutil.copytree(root / ".omp/skills/jd-pipeline", root / ".omp/skills/old-skill")
        _, problems = sync(root, check=True)
        self.assertEqual(
            sorted(problems),
            [".agents/skills/jd-pipeline/SKILL.md: out of date", ".omp/skills/old-skill: no matching skill"],
        )


if __name__ == "__main__":
    unittest.main()
