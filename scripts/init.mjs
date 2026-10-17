#!/usr/bin/env node
// Creates an empty data root: node scripts/init.mjs <path>
// Never overwrites existing files.
import { existsSync } from "node:fs";
import { copyFile, mkdir, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { repoRoot } from "./lib/paths.mjs";

const target = process.argv[2];
if (!target) {
  console.error("Usage: node scripts/init.mjs <path>");
  process.exit(1);
}
const root = resolve(target);

const created = [];
for (const dir of ["profile/work-history", "companies", "jobs", "reports"]) {
  const path = join(root, dir);
  if (!existsSync(path)) {
    await mkdir(path, { recursive: true });
    await writeFile(join(path, ".gitkeep"), "");
    created.push(`${dir}/`);
  }
}

const files = [["templates/career-profile.md", "profile/career-profile.md"]];
for (const [from, to] of files) {
  const path = join(root, to);
  if (!existsSync(path)) {
    await copyFile(join(repoRoot, from), path);
    created.push(to);
  }
}

const readme = join(root, "README.md");
if (!existsSync(readme)) {
  await writeFile(
    readme,
    "# Job search data\n\nPersonal data for rexcareer. Keep this folder private.\n" +
      "Point the tools at it with `REXCAREER_DATA=<this folder>`.\n",
  );
  created.push("README.md");
}

console.log(created.length ? `Created in ${root}:\n  ${created.join("\n  ")}` : `${root} is already set up.`);
console.log(`\nNext:\n  export REXCAREER_DATA="${root}"\n  edit ${join(root, "profile/career-profile.md")}`);
