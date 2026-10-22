"""End-to-end tests for save.py and renumber_job.py with real git repos: one
bare "origin" and two clones standing in for two sessions (for example the
phone and the laptop)."""

import json
import unittest

from helpers import add_job, git, script, temp_dir
from lib.paths import INSTANCE_MARKER, is_instance


def configure(repo, name):
    for key, value in (("user.name", name), ("user.email", f"{name}@example.com"), ("commit.gpgsign", "false")):
        git(repo, "config", key, value)


def two_sessions():
    """origin.git plus two clones, each with an instance marker and a data/ root."""
    base = temp_dir("career-intelligence-save-")
    origin = base / "origin.git"
    git(base, "init", "-q", "--bare", "-b", "main", str(origin))
    seed = base / "seed"
    git(base, "clone", "-q", str(origin), str(seed))
    configure(seed, "seed")
    (seed / INSTANCE_MARKER).write_text("")
    add_job(seed / "data", "acme", "2026-01-a", "JOB-2026-001")
    git(seed, "add", "-A")
    git(seed, "commit", "-q", "-m", "seed")
    git(seed, "push", "-q", "origin", "main")
    clones = []
    for name in ("phone", "laptop"):
        directory = base / name
        git(base, "clone", "-q", str(origin), str(directory))
        configure(directory, name)
        clones.append(directory)
    return clones


def index_jobs(repo):
    return json.loads((repo / "data" / "index.json").read_text(encoding="utf-8"))["jobs"]


class SaveTest(unittest.TestCase):
    def test_save_commits_pushes_and_the_other_session_sees_the_job(self):
        phone, laptop = two_sessions()
        add_job(phone / "data", "globex", "2026-02-b", "JOB-2026-002")
        r = script("save.py", ["Analyze Globex JD"], phone / "data")
        self.assertEqual(r.code, 0, r.stderr)
        self.assertIn("pushed", r.stdout)
        git(laptop, "pull", "-q")
        self.assertEqual([j["id"] for j in index_jobs(laptop)], ["JOB-2026-001", "JOB-2026-002"])

    def test_two_sessions_that_pick_the_same_id_the_later_save_renumbers_its_job(self):
        phone, laptop = two_sessions()
        add_job(phone / "data", "globex", "2026-02-b", "JOB-2026-002")
        job = add_job(laptop / "data", "initech", "2026-02-c", "JOB-2026-002")
        (job / "report.md").write_text("# Report\n\n> **Job ID:** JOB-2026-002 · **Job Name:** `initech/2026-02-c`\n")
        company = laptop / "data" / "companies" / "initech"
        company.mkdir(parents=True)
        (company / "profile.md").write_text("| 2026-02 | Engineer | JOB-2026-002 | new |\n")
        self.assertEqual(script("save.py", ["phone job"], phone / "data").code, 0)

        # Both sessions changed the generated index too: that conflict is solved by rebuilding it.
        r = script("save.py", ["laptop job"], laptop / "data")
        self.assertEqual(r.code, 0, r.stderr)
        self.assertIn("JOB-2026-002 was taken, now JOB-2026-003", r.stdout)

        git(phone, "pull", "-q")
        self.assertEqual(
            [f"{j['id']} {j['name']}" for j in index_jobs(phone)],
            ["JOB-2026-001 acme/2026-01-a", "JOB-2026-002 globex/2026-02-b", "JOB-2026-003 initech/2026-02-c"],
        )
        report = (phone / "data/jobs/initech/2026-02-c/report.md").read_text()
        self.assertIn("**Job ID:** JOB-2026-003", report)
        profile = (phone / "data/companies/initech/profile.md").read_text()
        self.assertIn("JOB-2026-003", profile, "the company profile follows the new ID")

    def test_a_real_conflict_stops_save_and_keeps_the_local_commit(self):
        phone, laptop = two_sessions()

        def notes(repo):
            return repo / "data/jobs/acme/2026-01-a/notes.md"

        notes(phone).write_text("phone version\n")
        self.assertEqual(script("save.py", ["phone notes"], phone / "data").code, 0)
        notes(laptop).write_text("laptop version\n")
        r = script("save.py", ["laptop notes"], laptop / "data")
        self.assertEqual(r.code, 1)
        self.assertIn("conflict in data/jobs/acme/2026-01-a/notes.md", r.stderr)
        self.assertEqual(git(laptop, "log", "-1", "--format=%s"), "laptop notes")
        self.assertEqual(git(laptop, "status", "--porcelain"), "")

    # Only in the skeleton: in a private instance <repo>/data is the user's
    # real data, and this test must never save it.
    @unittest.skipIf(is_instance(), "running inside a private instance")
    def test_save_refuses_to_run_in_the_public_skeleton(self):
        # With no data root variable the data root is <repo>/data, which does not exist here.
        r = script("save.py", ["x"], "")
        self.assertEqual(r.code, 1)
        self.assertRegex(r.stderr, r"Data root not found|public career-intelligence skeleton")

    def test_save_keeps_a_merge_from_the_skeleton_upstream(self):
        phone, laptop = two_sessions()
        # An unrelated "upstream" history merged into the instance, like a skeleton update.
        upstream = phone.parent / "upstream"
        git(phone.parent, "init", "-q", "-b", "main", str(upstream))
        configure(upstream, "up")
        (upstream / "SKELETON.md").write_text("skeleton\n")
        git(upstream, "add", "-A")
        git(upstream, "commit", "-q", "-m", "skeleton")
        skeleton_head = git(upstream, "rev-parse", "HEAD")
        git(phone, "fetch", "-q", str(upstream), "main:refs/remotes/upstream/main")
        git(phone, "merge", "-q", "--allow-unrelated-histories", "--no-edit", "upstream/main")

        # Another session pushes first, so the merge must be carried over a new remote commit.
        add_job(laptop / "data", "globex", "2026-02-b", "JOB-2026-002")
        self.assertEqual(script("save.py", ["laptop job"], laptop / "data").code, 0)

        add_job(phone / "data", "initech", "2026-02-c", "JOB-2026-003")
        r = script("save.py", ["phone job after skeleton merge"], phone / "data")
        self.assertEqual(r.code, 0, r.stderr)
        # The skeleton commit is still an ancestor: future upstream merges stay clean.
        git(phone, "merge-base", "--is-ancestor", skeleton_head, "HEAD")
        subjects = git(phone, "log", "--format=%s").split("\n")
        self.assertEqual(subjects.count("skeleton"), 1, "skeleton commit not duplicated")

    def test_save_pushes_without_rebasing_when_the_remote_has_nothing_new(self):
        phone, _ = two_sessions()
        git(phone, "commit", "-q", "--allow-empty", "-m", "local only")
        before = git(phone, "rev-parse", "HEAD")
        add_job(phone / "data", "globex", "2026-02-b", "JOB-2026-002")
        self.assertEqual(script("save.py", ["add job"], phone / "data").code, 0)
        git(phone, "merge-base", "--is-ancestor", before, "HEAD")


if __name__ == "__main__":
    unittest.main()
