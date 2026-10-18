import { mkdtemp, mkdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { repoRoot } from "../scripts/lib/paths.mjs";

const run = promisify(execFile);

export async function tempDataRoot() {
  return mkdtemp(join(tmpdir(), "rexcareer-test-"));
}

export async function addJob(root, { company, slot, id, status = "new", extra = "" }) {
  const dir = join(root, "jobs", company, slot);
  await mkdir(dir, { recursive: true });
  await writeFile(
    join(dir, "metadata.yml"),
    `schema: 5\nid: "${id}"\nname: "${company}/${slot}"\ncompany: "${company}"\ncompany_slug: "${company}"\n` +
      `role: "Engineer"\nstatus: "${status}"\ndomains: ["cloud-security"]\n${extra}`,
  );
}

// Runs a script and returns { code, stdout, stderr } without throwing.
// Tests always pass a temporary data root, or "" only where the test checks
// that the skeleton has no data (see save.test.mjs).
export async function script(name, args, dataRoot) {
  try {
    const { stdout, stderr } = await run(process.execPath, [join(repoRoot, "scripts", name), ...args], {
      env: { ...process.env, REXCAREER_DATA: dataRoot ?? "" },
    });
    return { code: 0, stdout, stderr };
  } catch (error) {
    return { code: error.code, stdout: error.stdout, stderr: error.stderr };
  }
}
