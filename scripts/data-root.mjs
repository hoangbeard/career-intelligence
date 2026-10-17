#!/usr/bin/env node
// Prints the absolute data root. Agents run this once per session.
import { resolveDataRoot } from "./lib/paths.mjs";

try {
  console.log(resolveDataRoot());
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
