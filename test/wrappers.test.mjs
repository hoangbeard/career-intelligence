import { test } from "node:test";
import assert from "node:assert/strict";
import { cp, mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { loadSkills, sync } from "../scripts/sync-wrappers.mjs";
import { repoRoot } from "../scripts/lib/paths.mjs";

test("committed wrappers match skills/", async () => {
  const { problems } = await sync(repoRoot, { check: true });
  assert.deepEqual(problems, []);
});

test("every skill has a valid name and description", async () => {
  const skills = await loadSkills(repoRoot);
  assert.ok(skills.length >= 10);
  for (const s of skills) assert.ok(s.description.length > 40, s.name);
});

test("check reports orphaned and edited wrappers", async () => {
  const root = await mkdtemp(join(tmpdir(), "rexcareer-wrap-"));
  await cp(join(repoRoot, "skills"), join(root, "skills"), { recursive: true });
  await sync(root);
  await writeFile(join(root, ".agents/skills/jd-pipeline/SKILL.md"), "edited");
  await cp(join(root, ".omp/skills/jd-pipeline"), join(root, ".omp/skills/old-skill"), { recursive: true });
  const { problems } = await sync(root, { check: true });
  assert.deepEqual(problems.sort(), [
    ".agents/skills/jd-pipeline/SKILL.md: out of date",
    ".omp/skills/old-skill: no matching skill",
  ]);
});
