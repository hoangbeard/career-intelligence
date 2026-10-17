// Shared path helpers. The data root holds the user's personal data and is
// never part of this repo: $REXCAREER_DATA, else <repo>/data.
import { existsSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, isAbsolute, join, resolve } from "node:path";

export const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..");

export function resolveDataRoot(env = process.env) {
  const raw = env.REXCAREER_DATA?.trim();
  const root = raw ? (isAbsolute(raw) ? raw : resolve(process.cwd(), raw)) : join(repoRoot, "data");
  if (!existsSync(root) || !statSync(root).isDirectory()) {
    const hint = raw ? `REXCAREER_DATA points to ${root}` : `no REXCAREER_DATA and no ${root}`;
    throw new Error(`Data root not found (${hint}). Run: node scripts/init.mjs <path>`);
  }
  return root;
}
