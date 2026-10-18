import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { forbiddenPaths } from "../scripts/guard.mjs";
import { migrate, migrateMetadata } from "../scripts/migrate.mjs";
import { addJob, script, tempDataRoot } from "./helpers.mjs";

test("guard blocks data/ and the instance marker in the skeleton only", () => {
  const paths = ["README.md", "data/profile/career-profile.md", "./data/jobs/x/metadata.yml", ".rexcareer-instance", "examples/demo-data/INDEX.md"];
  assert.deepEqual(forbiddenPaths(paths, false), [
    "data/profile/career-profile.md",
    "./data/jobs/x/metadata.yml",
    ".rexcareer-instance",
  ]);
  assert.deepEqual(forbiddenPaths(paths, true), []);
});

test("guard passes on this repository", async () => {
  const r = await script("guard.mjs", []);
  assert.equal(r.code, 0, r.stderr);
});

test("migrate turns v4 metadata into v5 and keeps everything else", () => {
  const v4 = '# comment\nid: "JOB-2025-001"\nname: "a/2025-01-x"\neng_grc_ratio: "70/30"\nnotes: "kept"\n';
  const { text, notes } = migrateMetadata(v4);
  assert.equal(text, '# comment\nschema: 5\nid: "JOB-2025-001"\nname: "a/2025-01-x"\nrole_mix: "70/30"\nnotes: "kept"\n');
  assert.deepEqual(notes, ["add schema: 5", "eng_grc_ratio -> role_mix"]);
  assert.deepEqual(migrateMetadata(text).notes, [], "second run changes nothing");
});

test("migrate: dry run writes nothing, --write applies, second run is a no-op", async () => {
  const root = await tempDataRoot();
  await addJob(root, { company: "a", slot: "2025-01-x", id: "JOB-2025-001", extra: 'eng_grc_ratio: "70/30"\n' });
  const meta = join(root, "jobs/a/2025-01-x/metadata.yml");
  await writeFile(meta, (await readFile(meta, "utf8")).replace("schema: 5\n", ""));
  await mkdir(join(root, "profile/work-history"), { recursive: true });
  await writeFile(join(root, "profile/career-profile.md"), "# Hồ sơ\n\nNội dung cũ [cv](cv/missing.md)\n");
  await writeFile(join(root, "profile/work-history/README.md"), "# Index\n");
  const before = await readFile(meta, "utf8");

  const dry = await migrate(root, []);
  assert.equal(dry.changes.length, 3);
  assert.deepEqual(dry.broken, ["profile/career-profile.md -> cv/missing.md"]);
  assert.equal(await readFile(meta, "utf8"), before, "dry run writes nothing");

  await migrate(root, ["--write", "--name", "Mai Nguyen", "--language", "vi", "--timezone", "+07:00", "--currency", "VND"]);
  const profile = await readFile(join(root, "profile/career-profile.md"), "utf8");
  assert.match(profile, /^---\nname: "Mai Nguyen"\nlanguage: "vi"\ntimezone: "\+07:00"\ncurrency: "VND"/);
  assert.match(profile, /# Hồ sơ\n\nNội dung cũ/, "old text kept");
  assert.ok(existsSync(join(root, "profile/work-history/_index.md")));
  assert.match(await readFile(meta, "utf8"), /^schema: 5$/m);
  assert.deepEqual((await migrate(root, ["--write"])).changes, [], "second run is a no-op");
});

test("doctor reports profile, open jobs with next steps and the next ID", async () => {
  const root = await tempDataRoot();
  assert.equal((await script("init.mjs", [root])).code, 0);
  await addJob(root, { company: "acme", slot: "2026-01-a", id: "JOB-2026-004", status: "interviewing" });
  await writeFile(join(root, "jobs/acme/2026-01-a/CONTEXT.md"), "# CONTEXT\n\n## Now\n\n- Status: interviewing\n- Next: 2026-11-03 panel interview\n");
  const r = await script("doctor.mjs", [], root);
  assert.equal(r.code, 0, r.stderr);
  assert.match(r.stdout, /career profile: language en/);
  assert.match(r.stdout, /work history: empty/);
  assert.match(r.stdout, /JOB-2026-004 interviewing .*next: 2026-11-03 panel interview/);
  assert.match(r.stdout, /next ID JOB-\d{4}-\d{3}/);
});

test("doctor never fails at session start, even without data", async () => {
  const r = await script("doctor.mjs", ["--session-start"], "/nonexistent/rexcareer-data");
  assert.equal(r.code, 0);
  assert.match(r.stdout, /problem|onboarding/);
});
