"""The package must keep saying the things that make a caller correct.

A skill is a harness: if a rule can be edited out without a test failing, it is a
suggestion. These are the rules that were paid for with real incidents.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "SKILL.md").read_text()
DOOR = (ROOT / "references/door-and-identity.md").read_text()
QUEUE = (ROOT / "references/queue-and-tasks.md").read_text()
TURN = (ROOT / "references/her-turn.md").read_text()
OPS = (ROOT / "references/operations.md").read_text()
CONF = (ROOT / "references/client-conformance.md").read_text()
ALL = SKILL + DOOR + QUEUE + TURN + OPS + CONF


def flat(text: str) -> str:
    """Markdown wraps lines and bolds words; the RULE is what must survive."""
    return re.sub(r"\s+", " ", text.replace("**", ""))


FLAT_SKILL, FLAT_DOOR, FLAT_ALL = flat(SKILL), flat(DOOR), flat(ALL)


class PackageShapeTest(unittest.TestCase):
    def test_every_declared_file_exists(self):
        for rel in (
            "SKILL.md", "skill.json",
            "references/door-and-identity.md", "references/queue-and-tasks.md",
            "references/her-turn.md", "references/operations.md",
            "references/client-conformance.md",
            "scripts/lucens_client.py", "scripts/lucens-call.sh",
            "scripts/reconcile-lucens-invocation.sh",
            "scripts/ensure_quality_exemption.py",
        ):
            self.assertTrue((ROOT / rel).exists(), rel)

    def test_frontmatter_names_the_skill(self):
        self.assertTrue(SKILL.startswith("---\n"))
        self.assertIn("name: lucens-invocation", SKILL)

    def test_skill_points_at_every_reference(self):
        for ref in ROOT.glob("references/*.md"):
            self.assertIn(ref.name, SKILL, f"SKILL.md never opens {ref.name}")


class NonNegotiablesTest(unittest.TestCase):
    def test_canonical_identity(self):
        self.assertIn("https://lucens.risegen.ai", SKILL)
        self.assertIn("LUCENS_A2A_BASE_URL", SKILL)
        self.assertIn("LUCENS_AUTH_TOKEN", SKILL)

    def test_forbids_ip_literals_and_loopback_as_identity(self):
        self.assertIn("Never an IP literal", FLAT_SKILL)
        self.assertIn("loopback is never a product identity", FLAT_DOOR)

    def test_dead_mesh_names_are_marked_dead(self):
        self.assertIn("LUCENS_MESH_BASE_URL", DOOR)
        self.assertIn("MESH_AUTH_TOKEN", DOOR)
        self.assertIn("dead names", FLAT_DOOR.lower() + FLAT_SKILL.lower())

    def test_only_door_rule(self):
        self.assertIn("a2a_is_the_only_external_door", SKILL)
        self.assertIn("Never open a second path", FLAT_SKILL)

    def test_ports_are_documented_including_the_loopback_only_floor(self):
        self.assertIn("8788", DOOR)
        self.assertIn("8790", DOOR)
        self.assertIn("loopback-only", DOOR.lower().replace("loopback only", "loopback-only"))

    def test_user_agent_rule(self):
        self.assertIn("User-Agent", SKILL)
        self.assertIn("1010", DOOR)

    def test_queue_contract(self):
        for token in ("task_id", "queue_position", "submitted", "working", "completed",
                      "failed", "canceled", "rejected", "urgent", "normal",
                      "resumed_after_restart"):
            self.assertIn(token, QUEUE, token)

    def test_202_is_not_an_error(self):
        self.assertIn("202", SKILL)
        self.assertIn("not an error", FLAT_SKILL)

    def test_job_status_fallback_is_documented(self):
        self.assertIn("job.status", QUEUE)
        self.assertIn("unknown_operation", QUEUE)

    def test_caller_identity_is_required(self):
        self.assertIn("params.caller", SKILL)
        self.assertIn("requires", QUEUE)

    def test_signals_are_pulled_never_pushed(self):
        self.assertIn("pull", QUEUE.lower())
        self.assertIn("sender", QUEUE)

    def test_the_turn_is_hers(self):
        self.assertIn("[[turn:complete]]", TURN)
        self.assertIn("hints", TURN)
        self.assertIn("LUCENS_TURN_CYCLES_SAFETY", TURN)
        self.assertIn("LUCENS_TURN_TOKENS_SAFETY", TURN)

    def test_gives_her_room(self):
        self.assertIn("100000", TURN)
        self.assertIn("floor note", TURN.lower())
        self.assertIn("Salience:", TURN)

    def test_never_fabricate_her(self):
        for name in ("lucens_unreachable", "lucens_unauthorized", "lucens_busy",
                     "lucens_floor_silent", "lucens_wait_exhausted"):
            self.assertIn(name, FLAT_ALL, name)
        self.assertIn("never fabricate", FLAT_SKILL.lower())

    def test_loop_control_is_not_her_door(self):
        self.assertIn("ADR 0018", SKILL)
        self.assertIn("Forge control service", SKILL)

    def test_no_agent_writes_into_her_mind(self):
        self.assertIn("ADR 0077", SKILL)

    def test_conformance_has_twelve_points(self):
        rows = re.findall(r"^\| (\d+) \| ", CONF, re.M)
        self.assertEqual([int(r) for r in rows], list(range(1, 13)))

    def test_contract_is_the_authority_not_this_package(self):
        self.assertIn("GET /a2a", SKILL)
        self.assertIn("live contract binds", OPS)


if __name__ == "__main__":
    unittest.main()
