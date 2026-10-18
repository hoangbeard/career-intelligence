// Small git helpers for the save and doctor scripts. Every call runs in `cwd`.
import { execFileSync } from "node:child_process";

export function git(cwd, args, { allowFail = false } = {}) {
  try {
    return execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
  } catch (error) {
    if (allowFail) return null;
    const detail = (error.stderr || error.stdout || error.message || "").toString().trim();
    throw new Error(`git ${args.join(" ")} failed: ${detail}`);
  }
}

// Top level of the git repository that contains `path`, or null.
export function repoTop(path) {
  return git(path, ["rev-parse", "--show-toplevel"], { allowFail: true });
}

export function hasRemote(cwd, name = "origin") {
  return (git(cwd, ["remote"], { allowFail: true }) ?? "").split("\n").includes(name);
}

export function currentBranch(cwd) {
  return git(cwd, ["rev-parse", "--abbrev-ref", "HEAD"], { allowFail: true });
}

export function upstreamRef(cwd) {
  return git(cwd, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], { allowFail: true });
}

export function isClean(cwd) {
  return (git(cwd, ["status", "--porcelain"], { allowFail: true }) ?? "x") === "";
}

export function conflictedFiles(cwd) {
  const out = git(cwd, ["diff", "--name-only", "--diff-filter=U"], { allowFail: true }) ?? "";
  return out.split("\n").filter(Boolean);
}
