"""Paired tests for the vendored-skill quality exemption.

The incident: vendoring this package's Python into `.claude/skills/` switched
quality-guard's python surface ON in 14 repositories that have no Python, where
`pytest -q` collects nothing and exits 5 — a red gate that blocks every commit
in the repo, not only ours.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from ensure_quality_exemption import WANTED, ensure  # noqa: E402

BLOCK_LIST = """version: 1
surfaces:
  - id: python
    prod_globs: ["**/*.py"]
    test_globs: ["**/test_*.py"]
    gate_cmd: "pytest -q"
    blast: normal
exemptions:
  generated:
    - "**/vendor/**"
    - "**/node_modules/**"
"""

INLINE_LIST = """version: 1
surfaces:
  - id: go
    prod_globs: ["**/*.go"]
    test_globs: ["**/*_test.go"]
    gate_cmd: "go test ./..."
    blast: normal
exemptions:
  generated: ["**/vendor/**", "**/*.gen.go"]
"""

NO_EXEMPTIONS = """version: 1
surfaces:
  - id: python
    prod_globs: ["**/*.py"]
    test_globs: ["**/test_*.py"]
    gate_cmd: "pytest -q"
    blast: normal
"""


class EnsureExemptionTest(unittest.TestCase):
    def test_block_list_gains_both_globs(self):
        out = ensure(BLOCK_LIST)
        for glob in WANTED:
            self.assertIn(f'- "{glob}"', out)

    def test_inline_list_gains_both_globs(self):
        out = ensure(INLINE_LIST)
        for glob in WANTED:
            self.assertIn(glob, out)
        self.assertIn('generated: ["**/vendor/**", "**/*.gen.go"', out)

    def test_missing_exemptions_section_is_created(self):
        out = ensure(NO_EXEMPTIONS)
        self.assertIn("exemptions:", out)
        self.assertIn("  generated:", out)
        for glob in WANTED:
            self.assertIn(glob, out)

    def test_existing_exemptions_are_kept(self):
        out = ensure(BLOCK_LIST)
        self.assertIn('- "**/vendor/**"', out)
        self.assertIn('- "**/node_modules/**"', out)

    def test_surfaces_are_untouched(self):
        out = ensure(BLOCK_LIST)
        self.assertIn('gate_cmd: "pytest -q"', out)
        self.assertIn('prod_globs: ["**/*.py"]', out)

    def test_is_idempotent(self):
        once = ensure(BLOCK_LIST)
        self.assertEqual(ensure(once), once)
        self.assertEqual(once.count('"**/.claude/skills/**"'), 1)

    def test_output_always_ends_with_a_newline(self):
        self.assertTrue(ensure("version: 1\nsurfaces: []").endswith("\n"))

    def test_a_later_top_level_key_does_not_swallow_the_section(self):
        text = BLOCK_LIST + "policy:\n  strict: true\n"
        out = ensure(text)
        self.assertIn("policy:", out)
        self.assertEqual(out.count('"**/.agents/skills/**"'), 1)


if __name__ == "__main__":
    unittest.main()
