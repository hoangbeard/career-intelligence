#!/usr/bin/env node
// Saves the data root to git so any other session (another machine, a cloud
// agent, the phone) continues from the same state.
//
//   node scripts/save.mjs "<what changed>"
//
// Steps: rebuild the index, commit the data root, rebase on origin, fix the
// two conflicts that can be fixed by machine (generated index files, a job ID
// taken by another session), then push. Anything else stops with a clear
// message and leaves your commit in place.
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join, relative } from "node:path";
import { pathToFileURL } from "node:url";
import { conflictedFiles, git, hasRemote, repoTop, upstreamRef } from "./lib/git.mjs";
import { duplicateGroups, loadJobs } from "./lib/jobs.mjs";
import { isInstance, repoRoot, resolveDataRoot } from "./lib/paths.mjs";
import { renumberJob } from "./renumber-job.mjs";

const GENERATED = ["INDEX.md", "index.json"];

function buildIndex(dataRoot) {
  execFileSync(process.execPath, [join(repoRoot, "scripts", "build-index.mjs")], {
    env: { ...process.env, REXCAREER_DATA: dataRoot },
    stdio: ["ignore", "ignore", "pipe"],
  });
}

function rebaseInProgress(top) {
  const dir = git(top, ["rev-parse", "--git-dir"]);
  const abs = dir.startsWith("/") ? dir : join(top, dir);
  return existsSync(join(abs, "rebase-merge")) || existsSync(join(abs, "rebase-apply"));
}

// Rebase on the remote. Conflicts limited to the generated index are solved by
// taking the remote copy for now; save() rebuilds it once IDs are fixed. Any
// other conflict aborts the rebase and throws.
function rebase(top, dataRoot, dataRel) {
  const generated = new Set(GENERATED.map((f) => (dataRel === "." ? f : `${dataRel}/${f}`)));
  // Nothing new on the remote: push as is. Rebasing here would replay merge
  // commits (such as a merge from the skeleton upstream) as new commits.
  if (git(top, ["merge-base", "--is-ancestor", "@{u}", "HEAD"], { allowFail: true }) !== null) return;
  // --rebase-merges keeps merge commits, so the upstream history stays shared.
  if (git(top, ["rebase", "--rebase-merges", "@{u}"], { allowFail: true }) !== null) return;
  for (let round = 0; round < 50 && rebaseInProgress(top); round++) {
    const conflicts = conflictedFiles(top);
    const other = conflicts.filter((f) => !generated.has(f));
    if (other.length) {
      git(top, ["rebase", "--abort"], { allowFail: true });
      throw new Error(
        `conflict in ${other.join(", ")}. Your commit is kept locally. ` +
          "Pull, merge those files by hand (or ask the agent), then run save again.",
      );
    }
    if (conflicts.length) {
      git(top, ["checkout", "--ours", "--", ...conflicts]);
      git(top, ["add", "--", ...conflicts]);
    }
    const env = { ...process.env, GIT_EDITOR: "true" };
    try {
      execFileSync("git", ["rebase", "--continue"], { cwd: top, env, stdio: ["ignore", "pipe", "pipe"] });
    } catch {
      // Either the next commit conflicts (loop again) or there was nothing left to commit.
      if (rebaseInProgress(top) && !conflictedFiles(top).length) {
        execFileSync("git", ["rebase", "--skip"], { cwd: top, env, stdio: "ignore" });
      }
    }
  }
}

// Jobs added locally that reuse an ID someone else pushed first get a new ID.
async function fixDuplicateIds(top, dataRoot) {
  const changed = new Set((git(top, ["diff", "--name-only", "@{u}..HEAD"], { allowFail: true }) ?? "").split("\n"));
  const notes = [];
  for (const group of duplicateGroups(await loadJobs(dataRoot, { allowDuplicates: true }))) {
    const local = group.filter((j) => changed.has(relative(top, join(dataRoot, j._path, "metadata.yml"))));
    const keep = group.find((j) => !local.includes(j)) ?? group[0];
    for (const job of group.filter((j) => j !== keep)) {
      const r = await renumberJob(dataRoot, join(dataRoot, job._path));
      notes.push(`${r.jobPath}: ${r.oldId} was taken, now ${r.newId}`, ...r.warnings.map((w) => `warning: ${w}`));
    }
  }
  return notes;
}

export async function save(message, { push = true } = {}) {
  const dataRoot = resolveDataRoot();
  const top = repoTop(dataRoot);
  if (!top) throw new Error(`${dataRoot} is not in a git repository; nothing to save to`);
  if (top === repoRoot && !isInstance()) {
    throw new Error("this is the public rexcareer skeleton; keep real data in a private instance (scripts/create-instance.sh)");
  }
  const dataRel = relative(top, dataRoot) || ".";
  const log = [];

  buildIndex(dataRoot);
  git(top, ["add", "-A", "--", dataRel]);
  if (git(top, ["diff", "--cached", "--quiet"], { allowFail: true }) === null) {
    try {
      git(top, ["commit", "-q", "-m", message]);
    } catch (error) {
      throw new Error(`commit failed (${error.message}). If commit signing is on, unlock your signing agent and run save again.`);
    }
    log.push(`committed: ${message}`);
  } else log.push("nothing new to commit");

  if (!push || !hasRemote(top) || !upstreamRef(top)) {
    log.push("no upstream branch; commit kept locally");
    return log;
  }

  for (let attempt = 1; attempt <= 3; attempt++) {
    git(top, ["fetch", "--quiet"]);
    rebase(top, dataRoot, dataRel);
    const notes = await fixDuplicateIds(top, dataRoot);
    buildIndex(dataRoot);
    git(top, ["add", "-A", "--", dataRel]);
    if (git(top, ["diff", "--cached", "--quiet"], { allowFail: true }) === null) {
      const subject = notes.length ? "Renumber jobs whose ID was taken by another session" : "Rebuild index after sync";
      git(top, ["commit", "-q", "-m", subject]);
    }
    log.push(...notes);
    if (git(top, ["push", "--quiet"], { allowFail: true }) !== null) {
      log.push(`pushed to ${upstreamRef(top)}`);
      return log;
    }
    log.push(`push rejected (attempt ${attempt}), retrying`);
  }
  throw new Error("push failed three times; run `git status` and `git push` to see why");
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const message = process.argv.slice(2).join(" ").trim();
  if (!message) {
    console.error('Usage: node scripts/save.mjs "<what changed>"');
    process.exit(1);
  }
  try {
    for (const line of await save(message)) console.log(line);
  } catch (error) {
    console.error(`save: ${error.message}`);
    process.exitCode = 1;
  }
}
