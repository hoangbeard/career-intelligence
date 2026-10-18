#!/usr/bin/env node
// Keeps personal data out of the public skeleton.
//
// In the skeleton (no .rexcareer-instance file) nothing under data/ and no
// instance marker may be committed. In a private instance the check passes.
//
//   node scripts/guard.mjs [files...]   check the given paths (pre-commit passes staged files)
//   node scripts/guard.mjs              check every file git tracks
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import { INSTANCE_MARKER, isInstance, repoRoot } from "./lib/paths.mjs";

export function forbiddenPaths(paths, instance) {
  if (instance) return [];
  return paths.filter((p) => {
    const rel = p.replace(/^\.\//, "");
    return rel === "data" || rel.startsWith("data/") || rel === INSTANCE_MARKER;
  });
}

function trackedFiles() {
  return execFileSync("git", ["ls-files", "-z"], { cwd: repoRoot, encoding: "utf8" }).split("\0").filter(Boolean);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const paths = process.argv.length > 2 ? process.argv.slice(2) : trackedFiles();
  const bad = forbiddenPaths(paths, isInstance());
  if (bad.length) {
    console.error(
      "guard: personal data must not be committed to the rexcareer skeleton.\n" +
        `  ${bad.slice(0, 20).join("\n  ")}${bad.length > 20 ? `\n  … and ${bad.length - 20} more` : ""}\n` +
        "Keep your data in a private instance: scripts/create-instance.sh <owner>/<repo>",
    );
    process.exitCode = 1;
  }
}
