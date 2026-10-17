import { existsSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import { parseFlatYaml } from "./flat-yaml.mjs";

export const JOB_ID = /^JOB-(\d{4})-(\d{3,})$/;

async function dirs(path) {
  if (!existsSync(path)) return [];
  const entries = await readdir(path, { withFileTypes: true });
  return entries.filter((e) => e.isDirectory() && !e.name.startsWith(".")).map((e) => e.name).sort();
}

// Reads every <data>/jobs/<company>/<slot>/metadata.yml and validates IDs and names.
export async function loadJobs(dataRoot) {
  const jobsDir = join(dataRoot, "jobs");
  const jobs = [];
  const seen = new Map();
  for (const company of await dirs(jobsDir)) {
    for (const slot of await dirs(join(jobsDir, company))) {
      const metaPath = join(jobsDir, company, slot, "metadata.yml");
      if (!existsSync(metaPath)) continue;
      const path = `jobs/${company}/${slot}`;
      const meta = parseFlatYaml(await readFile(metaPath, "utf8"));
      if (!JOB_ID.test(meta.id ?? "")) throw new Error(`${path}: invalid job id "${meta.id ?? ""}"`);
      if (seen.has(meta.id)) throw new Error(`${path}: duplicate job id ${meta.id} (also in ${seen.get(meta.id)})`);
      seen.set(meta.id, path);
      const expected = `${company}/${slot}`;
      if (meta.name !== expected) throw new Error(`${path}: name "${meta.name ?? ""}" must be "${expected}"`);
      jobs.push({ ...meta, _path: path });
    }
  }
  return jobs;
}
