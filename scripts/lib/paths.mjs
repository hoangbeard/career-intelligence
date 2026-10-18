// Shared path helpers.
//
// Data root: $REXCAREER_DATA, else <repo>/data. In the public skeleton the
// data root is never committed (scripts/guard.mjs blocks it). In a private
// instance, marked by the file .rexcareer-instance, <repo>/data is committed
// so that every clone, local or cloud, has the same data.
import { existsSync, realpathSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, isAbsolute, join, resolve } from "node:path";

export const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");
export const INSTANCE_MARKER = ".rexcareer-instance";

// True in a private instance repo, false in the public skeleton.
export function isInstance(root = repoRoot) {
  return existsSync(join(root, INSTANCE_MARKER));
}

export function resolveDataRoot(env = process.env) {
  const raw = env.REXCAREER_DATA?.trim();
  const root = raw ? (isAbsolute(raw) ? raw : resolve(process.cwd(), raw)) : join(repoRoot, "data");
  if (!existsSync(root) || !statSync(root).isDirectory()) {
    const hint = raw ? `REXCAREER_DATA points to ${root}` : `no REXCAREER_DATA and no ${root}`;
    throw new Error(
      `Data root not found (${hint}). ` +
        "Ask the agent to run the onboarding skill, or run: node scripts/init.mjs data",
    );
  }
  // Real path, so it compares equal to what git reports (macOS: /var -> /private/var).
  return realpathSync(root);
}
