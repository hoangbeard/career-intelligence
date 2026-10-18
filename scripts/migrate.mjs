#!/usr/bin/env node
// Brings an older data root up to the current format. Dry run by default.
//
//   node scripts/migrate.mjs                 show what would change
//   node scripts/migrate.mjs --write         apply the changes
//   options for a profile without front matter:
//     --name "<Full Name>" --language vi --timezone +07:00 --currency VND --location "<City, Country>"
//
// Changes (each one is skipped when already done, so running twice is safe):
//   - jobs/*/*/metadata.yml: add `schema: 5`; rename `eng_grc_ratio` to `role_mix`.
//     Other keys and every value are kept as they are.
//   - profile/career-profile.md: add the front matter block if it has none.
//   - profile/work-history/README.md: rename to _index.md (files starting with
//     "_" are not employer files).
// Also reports relative Markdown links that point to missing files. Report and
// note text is never rewritten.
import { existsSync } from "node:fs";
import { readdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname, join, relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { resolveDataRoot } from "./lib/paths.mjs";

function option(argv, name, fallback) {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback;
}

async function walk(dir, out = []) {
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".")) continue;
    const path = join(dir, entry.name);
    if (entry.isDirectory()) await walk(path, out);
    else out.push(path);
  }
  return out;
}

export function migrateMetadata(text) {
  let next = text;
  const notes = [];
  if (!/^schema:\s*/m.test(next)) {
    // After any leading comment lines, before the first key.
    const lines = next.split("\n");
    const at = lines.findIndex((l) => /^[A-Za-z_]/.test(l));
    lines.splice(at < 0 ? lines.length : at, 0, "schema: 5");
    next = lines.join("\n");
    notes.push("add schema: 5");
  }
  if (/^eng_grc_ratio:/m.test(next) && !/^role_mix:/m.test(next)) {
    next = next.replace(/^eng_grc_ratio:/m, "role_mix:");
    notes.push("eng_grc_ratio -> role_mix");
  }
  return { text: next, notes };
}

export function profileFrontMatter({ name, language, timezone, currency, location }) {
  const q = (v) => JSON.stringify(v);
  return [
    "---",
    `name: ${q(name)}`,
    `language: ${q(language)}`,
    `timezone: ${q(timezone)}`,
    `currency: ${q(currency)}`,
    `location: ${q(location)}`,
    `cv_file_pattern: ${q(`${name.replace(/\s+/g, "")}_<Company>_<Role>`)}`,
    "evidence_window_months: 60",
    "---",
    "",
  ].join("\n");
}

export async function migrate(dataRoot, argv = []) {
  const write = argv.includes("--write");
  const changes = [];
  const files = await walk(dataRoot);

  for (const path of files.filter((p) => p.endsWith("/metadata.yml") && relative(dataRoot, p).startsWith("jobs/"))) {
    const text = await readFile(path, "utf8");
    const r = migrateMetadata(text);
    if (r.notes.length) {
      changes.push(`${relative(dataRoot, path)}: ${r.notes.join(", ")}`);
      if (write) await writeFile(path, r.text);
    }
  }

  const profile = join(dataRoot, "profile", "career-profile.md");
  if (existsSync(profile)) {
    const text = await readFile(profile, "utf8");
    if (!text.startsWith("---")) {
      const fm = profileFrontMatter({
        name: option(argv, "name", "<Your Name>"),
        language: option(argv, "language", "en"),
        timezone: option(argv, "timezone", "+00:00"),
        currency: option(argv, "currency", "USD"),
        location: option(argv, "location", "<City, Country>"),
      });
      changes.push(`profile/career-profile.md: add front matter\n${fm.trimEnd().replace(/^/gm, "    ")}`);
      if (write) await writeFile(profile, fm + text);
    }
  }

  const readme = join(dataRoot, "profile", "work-history", "README.md");
  if (existsSync(readme)) {
    changes.push("profile/work-history/README.md -> profile/work-history/_index.md");
    if (write) await rename(readme, join(dirname(readme), "_index.md"));
  }

  // Walk again: --write may have renamed files.
  const broken = [];
  for (const path of (await walk(dataRoot)).filter((p) => p.endsWith(".md"))) {
    const text = await readFile(path, "utf8");
    for (const m of text.matchAll(/\]\(([^)\s]+)\)/g)) {
      const target = m[1].split("#")[0];
      if (!target || /^[a-z]+:/i.test(target)) continue;
      if (!existsSync(resolve(dirname(path), decodeURI(target)))) broken.push(`${relative(dataRoot, path)} -> ${target}`);
    }
  }
  return { write, changes, broken };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const { write, changes, broken } = await migrate(resolveDataRoot(), process.argv.slice(2));
    console.log(changes.length ? `${write ? "Changed" : "Would change"} (${changes.length}):\n  ${changes.join("\n  ")}` : "Nothing to migrate.");
    if (broken.length) console.log(`\nBroken links, not changed (${broken.length}):\n  ${broken.join("\n  ")}`);
    if (!write && changes.length) console.log("\nRun again with --write to apply, then: node scripts/build-index.mjs");
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
