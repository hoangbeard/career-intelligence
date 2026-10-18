#!/usr/bin/env node
// Checks the setup and prints a short status so a new session (local or
// cloud) can carry on where the last one stopped.
//
//   node scripts/doctor.mjs                  check and print status
//   node scripts/doctor.mjs --session-start  also fast-forward from origin first;
//                                            never fails (used by session hooks)
import { existsSync } from "node:fs";
import { readdir, readFile } from "node:fs/promises";
import { join, relative } from "node:path";
import { pathToFileURL } from "node:url";
import { parseFrontMatter } from "./lib/flat-yaml.mjs";
import { currentBranch, git, hasRemote, isClean, repoTop, upstreamRef } from "./lib/git.mjs";
import { duplicateGroups, loadJobs, nextJobId } from "./lib/jobs.mjs";
import { isInstance, repoRoot, resolveDataRoot } from "./lib/paths.mjs";

const ACTIVE = ["offer", "interviewing", "applied", "watching", "analyzed", "new"];

// "- Next: ..." (or "- Blocker: ...") from a job's CONTEXT.md.
async function nextStep(dataRoot, job) {
  const path = join(dataRoot, job._path, "CONTEXT.md");
  if (!existsSync(path)) return null;
  const text = await readFile(path, "utf8");
  for (const key of ["Next", "Blocker"]) {
    const m = text.match(new RegExp(`^- ${key}:\\s*(.+)$`, "m"));
    if (m && !/^(none|-|n\/a)?$/i.test(m[1].trim()) && !m[1].startsWith("(")) return `${key.toLowerCase()}: ${m[1].trim()}`;
  }
  return null;
}

async function profileStatus(dataRoot) {
  const lines = [];
  const profile = join(dataRoot, "profile", "career-profile.md");
  if (!existsSync(profile)) lines.push("career profile: missing (run the onboarding skill)");
  else {
    const fm = parseFrontMatter(await readFile(profile, "utf8"));
    if (!fm.language) lines.push("career profile: no front matter (language, timezone, currency); run the onboarding skill");
    else lines.push(`career profile: language ${fm.language}, timezone ${fm.timezone ?? "?"}, currency ${fm.currency ?? "?"}`);
  }
  const dir = join(dataRoot, "profile", "work-history");
  const files = existsSync(dir) ? (await readdir(dir)).filter((f) => f.endsWith(".md") && !f.startsWith("_")) : [];
  let verified = 0;
  for (const f of files) if (parseFrontMatter(await readFile(join(dir, f), "utf8")).verified === "true") verified++;
  lines.push(
    files.length
      ? `work history: ${files.length} employer file(s), ${verified} verified`
      : "work history: empty (run the onboarding or work-history skill)",
  );
  return lines;
}

function gitStatus(top, dataRoot, { pull }) {
  const lines = [];
  if (!top) return ["git: data root is not in a git repository; work is not saved anywhere"];
  if (pull && hasRemote(top) && upstreamRef(top)) {
    if (isClean(top)) {
      const ok = git(top, ["pull", "--ff-only", "--quiet"], { allowFail: true });
      lines.push(ok === null ? "git: could not fast-forward from origin (check `git status`)" : "git: up to date with origin");
    } else lines.push("git: local changes present, did not pull");
  }
  const dataRel = relative(top, dataRoot) || ".";
  const dirty = (git(top, ["status", "--porcelain", "--", dataRel], { allowFail: true }) ?? "").split("\n").filter(Boolean);
  if (dirty.length) lines.push(`git: ${dirty.length} unsaved change(s) in ${dataRel}/ (run: node scripts/save.mjs "<message>")`);
  if (upstreamRef(top)) {
    const ahead = Number(git(top, ["rev-list", "--count", "@{u}..HEAD"], { allowFail: true }) ?? 0);
    if (ahead) lines.push(`git: ${ahead} commit(s) not pushed (run: node scripts/save.mjs "<message>")`);
  }
  const branch = currentBranch(top);
  if (branch && branch !== "main" && branch !== "HEAD") lines.push(`git: on branch ${branch}; saves go to this branch`);
  return lines;
}

export async function report({ pull = false } = {}) {
  const out = [];
  const [major, minor] = process.versions.node.split(".").map(Number);
  if (major < 20 || (major === 20 && minor < 11)) out.push(`node: ${process.versions.node} is too old; need 20.11 or newer`);

  let dataRoot;
  try {
    dataRoot = resolveDataRoot();
  } catch {
    out.push(
      "data: none yet. Ask the agent to run the onboarding skill (\"set me up\").",
      isInstance() ? "" : "note: this is the public skeleton; keep real data in a private instance (scripts/create-instance.sh).",
    );
    return out.filter(Boolean);
  }

  const top = repoTop(dataRoot);
  out.push(...gitStatus(top, dataRoot, { pull }));
  out.push(`data root: ${dataRoot}${isInstance() && dataRoot.startsWith(repoRoot) ? " (private instance)" : ""}`);
  out.push(...(await profileStatus(dataRoot)));

  const jobs = await loadJobs(dataRoot, { allowDuplicates: true });
  for (const group of duplicateGroups(jobs)) {
    out.push(`problem: duplicate ${group[0].id} in ${group.map((j) => j._path).join(" and ")} (run: node scripts/renumber-job.mjs <newer job dir>)`);
  }
  const year = new Date().getFullYear();
  const counts = ACTIVE.map((s) => [s, jobs.filter((j) => j.status === s).length]).filter(([, n]) => n);
  out.push(`jobs: ${jobs.length} total${counts.length ? `; open: ${counts.map(([s, n]) => `${n} ${s}`).join(", ")}` : ""}; next ID ${nextJobId(jobs, year)}`);

  const open = jobs.filter((j) => ["offer", "interviewing", "applied", "watching"].includes(j.status));
  open.sort((a, b) => ACTIVE.indexOf(a.status) - ACTIVE.indexOf(b.status) || a.id.localeCompare(b.id));
  for (const job of open.slice(0, 12)) {
    const step = await nextStep(dataRoot, job);
    out.push(`  ${job.id} ${job.status.padEnd(12)} ${job.role ?? "?"} @ ${job.company ?? "?"}${step ? ` | ${step}` : ""}`);
  }
  if (open.length > 12) out.push(`  … ${open.length - 12} more in INDEX.md`);
  return out;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const sessionStart = process.argv.includes("--session-start");
  try {
    const lines = await report({ pull: sessionStart });
    console.log(["rexcareer status", ...lines.map((l) => (l.startsWith("  ") ? l : `- ${l}`))].join("\n"));
  } catch (error) {
    console.log(`rexcareer status\n- problem: ${error.message}`);
    if (!sessionStart) process.exitCode = 1;
  }
}
