import { test } from "node:test";
import assert from "node:assert/strict";
import { parseFlatYaml, parseFrontMatter } from "../scripts/lib/flat-yaml.mjs";

test("parses scalars, nulls, numbers and arrays", () => {
  const meta = parseFlatYaml(
    [
      'id: "JOB-2026-001"   # comment',
      "match_score: 82",
      "recommendation: null",
      "cv_used:",
      'domains: ["appsec", "cloud"]',
      "legacy: ['a', 'b']",
      "  indented: ignored",
    ].join("\n"),
  );
  assert.deepEqual(meta, {
    id: "JOB-2026-001",
    match_score: 82,
    recommendation: null,
    cv_used: null,
    domains: ["appsec", "cloud"],
    legacy: ["a", "b"],
  });
});

test("keeps # and escaped quotes inside double-quoted strings", () => {
  const meta = parseFlatYaml('notes: "C# role, \\"remote\\" # not a comment"');
  assert.equal(meta.notes, 'C# role, "remote" # not a comment');
});

test("reads front matter", () => {
  assert.deepEqual(parseFrontMatter('---\ncompany: "Acme"\n---\n# Acme'), { company: "Acme" });
  assert.deepEqual(parseFrontMatter("# no front matter"), {});
});
