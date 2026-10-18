#!/usr/bin/env node
// Prints the next free job ID for a year: JOB-YYYY-NNN.
import { loadJobs, nextJobId } from "./lib/jobs.mjs";
import { resolveDataRoot } from "./lib/paths.mjs";

const year = process.argv[2];
if (!/^\d{4}$/.test(year ?? "")) {
  console.error("Usage: node scripts/next-job-id.mjs <YYYY>");
  process.exit(1);
}

try {
  console.log(nextJobId(await loadJobs(resolveDataRoot()), year));
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
