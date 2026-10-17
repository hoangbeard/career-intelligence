#!/usr/bin/env node
// Prints the next free job ID for a year: JOB-YYYY-NNN.
import { JOB_ID, loadJobs } from "./lib/jobs.mjs";
import { resolveDataRoot } from "./lib/paths.mjs";

const year = process.argv[2];
if (!/^\d{4}$/.test(year ?? "")) {
  console.error("Usage: node scripts/next-job-id.mjs <YYYY>");
  process.exit(1);
}

try {
  const jobs = await loadJobs(resolveDataRoot());
  let max = 0;
  for (const job of jobs) {
    const [, y, n] = job.id.match(JOB_ID);
    if (y === year) max = Math.max(max, Number(n));
  }
  console.log(`JOB-${year}-${String(max + 1).padStart(3, "0")}`);
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
