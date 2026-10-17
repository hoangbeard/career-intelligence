import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { addJob, script, tempDataRoot } from "./helpers.mjs";

test("data-root fails with a hint when the folder is missing", async () => {
  const r = await script("data-root.mjs", [], "/nonexistent/rexcareer-data");
  assert.equal(r.code, 1);
  assert.match(r.stderr, /init\.mjs/);
});

test("init creates a data root and never overwrites", async () => {
  const root = await tempDataRoot();
  assert.equal((await script("init.mjs", [root])).code, 0);
  for (const p of ["profile/career-profile.md", "profile/work-history", "companies", "jobs", "reports"]) {
    assert.ok(existsSync(join(root, p)), p);
  }
  await writeFile(join(root, "profile/career-profile.md"), "mine");
  await script("init.mjs", [root]);
  assert.equal(await readFile(join(root, "profile/career-profile.md"), "utf8"), "mine");
  const r = await script("data-root.mjs", [], root);
  assert.equal(r.stdout.trim(), root);
});

test("next-job-id continues the sequence per year", async () => {
  const root = await tempDataRoot();
  assert.equal((await script("next-job-id.mjs", ["2026"], root)).stdout.trim(), "JOB-2026-001");
  await addJob(root, { company: "acme", slot: "2026-01-a", id: "JOB-2026-007" });
  await addJob(root, { company: "acme", slot: "2025-12-b", id: "JOB-2025-030" });
  assert.equal((await script("next-job-id.mjs", ["2026"], root)).stdout.trim(), "JOB-2026-008");
  assert.equal((await script("next-job-id.mjs", ["26"], root)).code, 1);
});

test("build-index writes, checks and detects drift", async () => {
  const root = await tempDataRoot();
  await addJob(root, { company: "acme", slot: "2026-01-a", id: "JOB-2026-001", status: "interviewing" });
  await addJob(root, {
    company: "globex",
    slot: "2026-02-b",
    id: "JOB-2026-002",
    status: "accepted",
    extra: 'eng_grc_ratio: "80/20"\n',
  });
  assert.equal((await script("build-index.mjs", ["--check"], root)).code, 1);
  assert.equal((await script("build-index.mjs", [], root)).code, 0);
  assert.equal((await script("build-index.mjs", ["--check"], root)).code, 0);

  const index = JSON.parse(await readFile(join(root, "index.json"), "utf8"));
  assert.equal(index.job_count, 2);
  assert.equal(index.jobs[1].role_mix, "80/20", "v4 eng_grc_ratio maps to role_mix");
  const md = await readFile(join(root, "INDEX.md"), "utf8");
  assert.match(md, /### interviewing \(1\)/);
  assert.match(md, /### accepted \(1\)/);

  await addJob(root, { company: "acme", slot: "2026-03-c", id: "JOB-2026-003" });
  assert.equal((await script("build-index.mjs", ["--check"], root)).code, 1);
});

test("build-index rejects duplicate IDs and wrong names", async () => {
  const dup = await tempDataRoot();
  await addJob(dup, { company: "a", slot: "2026-01-x", id: "JOB-2026-001" });
  await addJob(dup, { company: "b", slot: "2026-01-y", id: "JOB-2026-001" });
  assert.match((await script("build-index.mjs", [], dup)).stderr, /duplicate job id/);

  const bad = await tempDataRoot();
  await addJob(bad, { company: "a", slot: "2026-01-x", id: "JOB-2026-001" });
  const meta = join(bad, "jobs/a/2026-01-x/metadata.yml");
  await writeFile(meta, (await readFile(meta, "utf8")).replace('name: "a/2026-01-x"', 'name: "a/other"'));
  assert.match((await script("build-index.mjs", [], bad)).stderr, /must be "a\/2026-01-x"/);
});

test("demo data index is current", async () => {
  const r = await script("build-index.mjs", ["--check"], join(import.meta.dirname, "..", "examples", "demo-data"));
  assert.equal(r.code, 0, r.stderr);
});
