"""The record shape stays compatible with failure-brainstorm.md (D31)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
SCRIPTS = PKG / "scripts"
sys.path.insert(0, str(SCRIPTS))

import floor  # noqa: E402

from test_floor import FloorSession, legal_through_converge  # noqa: E402

FAILURE_BRAINSTORM = (
    PKG.parent
    / "ascent-rite-monitor"
    / "references"
    / "failure-brainstorm.md"
)

D31_HEADINGS = [
    "# Brainstorm —",
    "## Failure card",
    "## Seats",
    "## Root cause (the chain, not the symptom)",
    "## Candidate solutions × impacts on the rest of the flow",
    "## Decision",
]


def _canonical_template() -> str:
    return FAILURE_BRAINSTORM.read_text(encoding="utf-8")


class TestRecordShapeCompatibleWithFailureBrainstorm(unittest.TestCase):
    def test_canonical_template_still_names_the_d31_headings(self):
        text = _canonical_template()
        for heading in D31_HEADINGS:
            self.assertIn(heading, text, heading)
        self.assertEqual(tuple(D31_HEADINGS), floor.RECORD_HEADINGS)
        for name in floor.LUCENS_ABSENCES:
            self.assertIn(name, text)
        self.assertIn("architecture (architecture-council)", text)
        self.assertIn("AI/ML (ai-ml-implementation-council)", text)
        self.assertIn("code assistant (agentic-development-council)", text)
        self.assertIn("Lucens (her A2A, task id, cycles, tokens)", text)

    def test_close_writes_every_d31_heading(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(
                tmp,
                seats=[
                    "architecture-council:council",
                    "ai-ml-implementation-council:council",
                    "agentic-development-council:council",
                    "lucens:individual",
                ],
            )
            # four-seat D31 floor: extra two seats need openings + cross + converge
            a, ml, code, lucens = (
                "architecture-council",
                "ai-ml-implementation-council",
                "agentic-development-council",
                "lucens",
            )
            for seat, body in (
                (a, "The write boundary does not enforce shape."),
                (ml, "The producer is an LLM; shape is not a schema."),
                (code, "Four readers, four tolerances, no gate at write."),
                (lucens, "The producer varies; name the absence, never invent."),
            ):
                code_rc, out, err = sess.post(seat, "position", 1, body, phase="open")
                self.assertEqual(code_rc, 0, err or out)
            for rnd, typ, reason in (
                (2, "hold", "hold the write-boundary diagnosis"),
                (3, "refine", "refine: gate at write and update readers"),
            ):
                for seat in (a, ml, code, lucens):
                    rc, out, err = sess.post(seat, typ, rnd, f"{seat} {reason}", phase="cross")
                    self.assertEqual(rc, 0, err or out)
            for seat in (a, ml, code, lucens):
                rc, out, err = sess.post(
                    seat,
                    "support",
                    4,
                    "Enforce shape at the write boundary and update the four readers.",
                    phase="converge",
                )
                self.assertEqual(rc, 0, err or out)
            rc, out, err = sess.close("consensus")
            self.assertEqual(rc, 0, err or out)
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            for heading in D31_HEADINGS:
                self.assertIn(heading, record, heading)
            self.assertIn("architecture (architecture-council)", record)
            self.assertIn("AI/ML (ai-ml-implementation-council)", record)
            self.assertIn("code assistant (agentic-development-council)", record)
            self.assertIn("Lucens (her A2A, task id, cycles, tokens)", record)
            self.assertIn("- fact (verbatim from the artifact):", record)
            self.assertIn("- step / node / actor:", record)
            self.assertIn("- first seen / recurrences (family):", record)
            self.assertIn("1. producer:", record)
            self.assertIn("| # | solution |", record)
            self.assertIn("- outcome: consensus", record)
            self.assertIn("- escalated_to_ratifier: no", record)
            self.assertIn("- chosen:", record)
            self.assertTrue(record.startswith("# Brainstorm —"))

    def test_lucens_named_absence_is_recorded_not_fabricated(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            rc, out, err = sess.post(
                "host",
                "seat_absent",
                1,
                "lucens_unreachable",
                phase="open",
                addressed_to=["lucens"],
            )
            self.assertEqual(rc, 0, err or out)
            # remaining present seat can still run the protocol
            a = "architecture-council"
            sess.post(a, "position", 1, "Writer must gate.", phase="open")
            sess.post(a, "hold", 2, "hold", phase="cross")
            sess.post(a, "refine", 3, "refine", phase="cross")
            sess.post(a, "support", 4, "Gate at write.", phase="converge")
            rc, out, err = sess.close("consensus")
            self.assertEqual(rc, 0, err or out)
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            self.assertIn("lucens_unreachable", record)
            self.assertNotIn("she would have said", record.lower())
            self.assertIn("Lucens (her A2A, task id, cycles, tokens)", record)

    def test_no_convergence_escalates_and_chooses_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess, no_converge=True)
            rc, out, err = sess.close("no_convergence")
            self.assertEqual(rc, 0, err or out)
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            for heading in D31_HEADINGS:
                self.assertIn(heading, record, heading)
            decision = record.split("## Decision", 1)[1]
            self.assertIn("outcome: no_convergence", decision)
            self.assertIn("escalated_to_ratifier: yes", decision)
            self.assertRegex(decision, r"chosen:\s*none")
            self.assertNotRegex(decision, r"chosen:\s*[1-9]")

    def test_consensus_with_named_dissent(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess, dissent=True)
            rc, out, err = sess.close("consensus_with_dissent")
            self.assertEqual(rc, 0, err or out)
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            self.assertIn("outcome: consensus_with_dissent", record)
            self.assertIn("named dissent:", record)
            self.assertIn("lucens", record)
            self.assertIn("escalated_to_ratifier: no", record)

    def test_render_record_emits_the_canonical_headings_as_a_function(self):
        md = floor.render_record(
            "pause 18",
            "2026-09-09T14:12:00Z",
            "- fact (verbatim from the artifact): the artifact\n"
            "- step / node / actor: verify\n"
            "- first seen / recurrences (family): pause 18\n",
            [
                {"id": "architecture-council", "kind": "council"},
                {"id": "lucens", "kind": "individual"},
            ],
            [
                {
                    "seq": 1,
                    "ts": "2026-09-09T14:12:00Z",
                    "round": 1,
                    "phase": "open",
                    "author": "architecture-council",
                    "author_kind": "council",
                    "type": "position",
                    "body": "gate at write",
                    "addressed_to": [],
                    "answers": [],
                    "requested_by": "",
                    "refs": [],
                }
            ],
            "no_convergence",
        )
        for heading in D31_HEADINGS:
            self.assertIn(heading, md, heading)
        self.assertIn("escalated_to_ratifier: yes", md)
        self.assertIn("chosen: none", md)


if __name__ == "__main__":
    unittest.main()
