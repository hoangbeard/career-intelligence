import unittest

import helpers  # noqa: F401  (puts scripts/ on sys.path)
from lib.flat_yaml import parse_flat_yaml, parse_front_matter


class FlatYamlTest(unittest.TestCase):
    def test_parses_scalars_nulls_numbers_and_arrays(self):
        meta = parse_flat_yaml(
            "\n".join(
                [
                    'id: "JOB-2026-001"   # comment',
                    "match_score: 82",
                    "ratio: 1.50",
                    "recommendation: null",
                    "cv_used:",
                    'domains: ["appsec", "cloud"]',
                    "legacy: ['a', 'b']",
                    "plain: 'quoted'",
                    "  indented: ignored",
                ]
            )
        )
        self.assertEqual(
            meta,
            {
                "id": "JOB-2026-001",
                "match_score": 82,
                "ratio": 1.5,
                "recommendation": None,
                "cv_used": None,
                "domains": ["appsec", "cloud"],
                "legacy": ["a", "b"],
                "plain": "quoted",
            },
        )
        self.assertIsInstance(meta["match_score"], int)

    def test_keeps_hash_and_escaped_quotes_inside_double_quoted_strings(self):
        meta = parse_flat_yaml('notes: "C# role, \\"remote\\" # not a comment"')
        self.assertEqual(meta["notes"], 'C# role, "remote" # not a comment')

    def test_reads_front_matter(self):
        self.assertEqual(parse_front_matter('---\ncompany: "Acme"\n---\n# Acme'), {"company": "Acme"})
        self.assertEqual(parse_front_matter("# no front matter"), {})


if __name__ == "__main__":
    unittest.main()
