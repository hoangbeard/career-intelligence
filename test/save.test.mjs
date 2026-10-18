// End-to-end tests for save.mjs and renumber-job.mjs with real git repos:
// one bare "origin" and two clones standing in for two sessions (for example
// the phone and the laptop).
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdir, mkdtemp, readFile, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { addJob, script } from "./helpers.mjs";

const git = (cwd, ...args) => execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();

// origin.git plus two clones, each with an instance marker and a data/ root.
async function twoSessions() {
  const base = await mkdtemp(join(tmpdir(), "rexcareer-save-"));
  const origin = join(base, "origin.git");
  git(base, "init", "-q", "--bare", "-b", "main", origin);
  const seed = join(base, "seed");
  git(base, "clone", "-q", origin, seed);
  for (const [k, v] of [["user.name", "Test"], ["user.email", "test@example.com"], ["commit.gpgsign", "false"]]) git(seed, "config", k, v);
  await writeFile(join(seed, ".rexcareer-instance"), "");
  await addJob(join(seed, "data"), { company: "acme", slot: "2026-01-a", id: "JOB-2026-001" });
  git(seed, "add", "-A");
  git(seed, "commit", "-q", "-m", "seed");
  git(seed, "push", "-q", "origin", "main");
  const clones = [];
  for (const name of ["phone", "laptop"]) {
    const dir = join(base, name);
    git(base, "clone", "-q", origin, dir);
    for (const [k, v] of [["user.name", name], ["user.email", `${name}@example.com`], ["commit.gpgsign", "false"]]) git(dir, "config", k, v);
    clones.push(dir);
  }
  return { origin, phone: clones[0], laptop: clones[1] };
}

test("save commits, pushes and the other session sees the job", async () => {
  const { phone, laptop } = await twoSessions();
  await addJob(join(phone, "data"), { company: "globex", slot: "2026-02-b", id: "JOB-2026-002" });
  const r = await script("save.mjs", ["Analyze Globex JD"], join(phone, "data"));
  assert.equal(r.code, 0, r.stderr);
  assert.match(r.stdout, /pushed/);
  git(laptop, "pull", "-q");
  const index = JSON.parse(await readFile(join(laptop, "data", "index.json"), "utf8"));
  assert.deepEqual(index.jobs.map((j) => j.id), ["JOB-2026-001", "JOB-2026-002"]);
});

test("two sessions that pick the same ID: the later save renumbers its job", async () => {
  const { phone, laptop } = await twoSessions();
  await addJob(join(phone, "data"), { company: "globex", slot: "2026-02-b", id: "JOB-2026-002" });
  await addJob(join(laptop, "data"), { company: "initech", slot: "2026-02-c", id: "JOB-2026-002" });
  await writeFile(
    join(laptop, "data", "jobs", "initech", "2026-02-c", "report.md"),
    "# Report\n\n> **Job ID:** JOB-2026-002 · **Job Name:** `initech/2026-02-c`\n",
  );
  await mkdir(join(laptop, "data", "companies", "initech"), { recursive: true });
  await writeFile(join(laptop, "data", "companies", "initech", "profile.md"), "| 2026-02 | Engineer | JOB-2026-002 | new |\n");
  assert.equal((await script("save.mjs", ["phone job"], join(phone, "data"))).code, 0);

  // Both sessions changed the generated index too: that conflict is solved by rebuilding it.
  const r = await script("save.mjs", ["laptop job"], join(laptop, "data"));
  assert.equal(r.code, 0, r.stderr);
  assert.match(r.stdout, /JOB-2026-002 was taken, now JOB-2026-003/);

  git(phone, "pull", "-q");
  const index = JSON.parse(await readFile(join(phone, "data", "index.json"), "utf8"));
  assert.deepEqual(
    index.jobs.map((j) => `${j.id} ${j.name}`),
    ["JOB-2026-001 acme/2026-01-a", "JOB-2026-002 globex/2026-02-b", "JOB-2026-003 initech/2026-02-c"],
  );
  const report = await readFile(join(phone, "data", "jobs", "initech", "2026-02-c", "report.md"), "utf8");
  assert.match(report, /\*\*Job ID:\*\* JOB-2026-003/);
  const company = await readFile(join(phone, "data", "companies", "initech", "profile.md"), "utf8");
  assert.match(company, /JOB-2026-003/, "the company profile follows the new ID");
});

test("a real conflict stops save and keeps the local commit", async () => {
  const { phone, laptop } = await twoSessions();
  const notes = (dir) => join(dir, "data", "jobs", "acme", "2026-01-a", "notes.md");
  await writeFile(notes(phone), "phone version\n");
  assert.equal((await script("save.mjs", ["phone notes"], join(phone, "data"))).code, 0);
  await writeFile(notes(laptop), "laptop version\n");
  const r = await script("save.mjs", ["laptop notes"], join(laptop, "data"));
  assert.equal(r.code, 1);
  assert.match(r.stderr, /conflict in data\/jobs\/acme\/2026-01-a\/notes\.md/);
  assert.equal(git(laptop, "log", "-1", "--format=%s"), "laptop notes");
  assert.equal(git(laptop, "status", "--porcelain"), "");
});

test("save refuses to run in the public skeleton", async () => {
  // With no REXCAREER_DATA the data root is <repo>/data, which does not exist here.
  const r = await script("save.mjs", ["x"], "");
  assert.equal(r.code, 1);
  assert.match(r.stderr, /Data root not found|public rexcareer skeleton/);
});
