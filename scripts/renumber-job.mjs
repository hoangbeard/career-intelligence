#!/usr/bin/env node
// Gives a job a new free ID, for example after two sessions picked the same
// one. Updates metadata.yml and the "Job ID" line of the job's Markdown files
// (never source.* or artifacts/).
//
//   node scripts/renumber-job.mjs <data>/jobs/<company>/<slot>
import { existsSync } from "node:fs";
import { readdir, readFile, writeFile } from "node:fs/promises";
import { join, relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { parseFlatYaml } from "./lib/flat-yaml.mjs";
import { JOB_ID, loadJobs, nextJobId } from "./lib/jobs.mjs";
import { resolveDataRoot } from "./lib/paths.mjs";

export async function renumberJob(dataRoot, jobDir) {
  const metaPath = join(jobDir, "metadata.yml");
  if (!existsSync(metaPath)) throw new Error(`${jobDir}: no metadata.yml`);
  const metaText = await readFile(metaPath, "utf8");
  const oldId = parseFlatYaml(metaText).id ?? "";
  const m = oldId.match(JOB_ID);
  if (!m) throw new Error(`${jobDir}: invalid job id "${oldId}"`);

  const others = (await loadJobs(dataRoot, { allowDuplicates: true })).filter(
    (j) => resolve(dataRoot, j._path) !== resolve(jobDir),
  );
  const newId = nextJobId([...others, { id: oldId }], m[1]);

  await writeFile(metaPath, metaText.replace(/^id:\s*.*$/m, `id: "${newId}"`));
  const changed = ["metadata.yml"];
  for (const file of await readdir(jobDir)) {
    if (!file.endsWith(".md") || file.startsWith("source.")) continue;
    const path = join(jobDir, file);
    const text = await readFile(path, "utf8");
    const next = text.replace(new RegExp(`(\\*\\*Job ID:\\*\\* )${oldId}\\b`, "g"), `$1${newId}`);
    if (next !== text) {
      await writeFile(path, next);
      changed.push(file);
    }
  }
  return { oldId, newId, changed, jobPath: relative(dataRoot, jobDir) };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const target = process.argv[2];
  if (!target) {
    console.error("Usage: node scripts/renumber-job.mjs <job folder>");
    process.exit(1);
  }
  try {
    const r = await renumberJob(resolveDataRoot(), resolve(target));
    console.log(`${r.jobPath}: ${r.oldId} -> ${r.newId} (${r.changed.join(", ")})`);
    console.log(`Check other files that mention ${r.oldId} (company profile Hiring intel, reports).`);
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}
