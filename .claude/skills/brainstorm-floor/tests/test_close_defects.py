"""Paired tests for the four close/record defects found on a live seven-seat floor.

Each test goes red if the matching fix is removed from scripts/floor.py.
"""
from __future__ import annotations

import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
SCRIPTS = PKG / "scripts"
sys.path.insert(0, str(SCRIPTS))

import floor  # noqa: E402

from test_floor import FloorSession, _run, legal_through_converge  # noqa: E402

LIVE_FLOOR = HERE / "fixtures" / "bf-20260912-labs-trials.floor.jsonl"


def _open_live_preclose(tmp: str) -> Path:
    """Rebuild the live session just before the defective close, in a temp dir."""
    raw = LIVE_FLOOR.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in raw.splitlines() if line.strip()]
    entries = [
        e
        for e in entries
        if not (e.get("type") == "record" and e.get("author") == "host")
    ]
    convene = next(e for e in entries if e.get("type") == "convene")
    body = json.loads(convene["body"])
    dest = Path(tmp) / "live-session"
    dest.mkdir()
    with (dest / "floor.jsonl").open("w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(floor._dumps(e) + "\n")
    facts = next(
        (e.get("body") or "" for e in entries if e.get("type") == "facts"), ""
    )
    (dest / "facts.md").write_text(facts, encoding="utf-8")
    meta = {
        "topic": body.get("topic") or "",
        "seats": body["seats"],
        "opened_at": entries[0]["ts"] if entries else "",
        "closed": False,
        "outcome": None,
    }
    (dest / "session.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return dest


def _chosen_line(record_md: str) -> str:
    decision = record_md.split("## Decision", 1)[1]
    for line in decision.splitlines():
        if line.startswith("- chosen:"):
            return line
    raise AssertionError("no chosen line in Decision section")


def _support_first_lines(entries):
    lines = []
    for e in entries:
        if e.get("type") != "support":
            continue
        for raw in (e.get("body") or "").splitlines():
            stripped = raw.strip()
            if stripped:
                lines.append(stripped)
                break
    return lines


class TestDACloseRunsVerifierBeforeWrite(unittest.TestCase):
    """D-A: close computes the derived outcome the same way verify does and refuses."""

    def test_close_refuses_when_requested_outcome_contradicts_derived(self):
        close_src = inspect.getsource(floor.cmd_close)
        self.assertIn("_close_protocol_gates", close_src)
        self.assertIn(
            "assert_outcome_matches_derived",
            inspect.getsource(floor._close_protocol_gates),
        )
        self.assertIn(
            "derive_outcome", inspect.getsource(floor.assert_outcome_matches_derived)
        )
        self.assertIn(
            "outcome_contradicts_derived", inspect.getsource(floor.verify_entries)
        )
        self.assertIn(
            "outcome_contradicts_derived",
            inspect.getsource(floor.assert_outcome_matches_derived),
        )
        self.assertIn("_close_protocol_gates", inspect.getsource(floor.cmd_reclose))

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess, no_converge=True)
            derived = floor.derive_outcome(
                sess.entries(), floor.roster_of(sess.dir)
            )
            self.assertEqual(derived, "no_convergence")
            n_before = len(sess.entries())
            rc, out, err = sess.close("consensus_with_dissent")
            self.assertEqual(rc, 1)
            blob = out + err
            self.assertIn(floor.V_OUTCOME_MISMATCH, blob)
            self.assertIn("consensus_with_dissent", blob)
            self.assertIn("no_convergence", blob)
            self.assertFalse((sess.dir / "record.md").exists())
            self.assertEqual(len(sess.entries()), n_before)
            self.assertFalse(any(e["type"] == "record" for e in sess.entries()))
            meta = floor.load_session_meta(sess.dir)
            self.assertFalse(meta.get("closed"))

            rc, out, err = sess.close("no_convergence")
            self.assertEqual(rc, 0, err or out)
            rc, out, err = sess.verify()
            self.assertEqual(rc, 0, out + err)


class TestDBRecordNeverAuthorsAChosenFromSupport(unittest.TestCase):
    """D-B: the record never synthesises chosen from a support entry's body."""

    def test_chosen_is_never_taken_from_a_support_body(self):
        src = inspect.getsource(floor.render_record)
        self.assertNotIn('supports[0]["body"]', src)
        self.assertNotIn("supports[0]['body']", src)
        self.assertNotIn("_first_line(supports", src)
        self.assertIn("_chosen_value", src)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess)
            support_lines = _support_first_lines(sess.entries())
            self.assertTrue(support_lines)
            rc, out, err = sess.close("consensus")
            self.assertEqual(rc, 0, err or out)
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            chosen = _chosen_line(record)
            for line in support_lines:
                self.assertNotIn(
                    line,
                    chosen,
                    f"chosen line took text from a support body: {line!r} in {chosen!r}",
                )
            self.assertIn(floor.CHOSEN_NO_DECISION, chosen)
            decision = record.split("## Decision", 1)[1]
            self.assertIn("- supporting:", decision)
            self.assertIn("- objecting:", decision)
            self.assertIn("architecture-council (seq", decision)
            self.assertIn("lucens (seq", decision)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess)
            support_seq = [
                e["seq"] for e in sess.entries() if e["type"] == "support"
            ][0]
            decision_text = "DECISION_ENTRY_GATE_AT_WRITE_AND_READERS"
            rc, out, err = sess.post(
                "architecture-council",
                "decision",
                4,
                decision_text,
                phase="close",
                refs=[support_seq],
            )
            self.assertEqual(rc, 0, err or out)
            support_lines = _support_first_lines(sess.entries())
            rc, out, err = sess.close("consensus")
            self.assertEqual(rc, 0, err or out)
            chosen = _chosen_line(
                (sess.dir / "record.md").read_text(encoding="utf-8")
            )
            self.assertIn(decision_text, chosen)
            for line in support_lines:
                self.assertNotIn(
                    line,
                    chosen,
                    f"chosen line took text from a support body: {line!r} in {chosen!r}",
                )


class TestDCCandidateTableFromProposalsOnly(unittest.TestCase):
    """D-C: the candidate table is built only from proposal entries."""

    def test_candidate_table_is_not_first_lines_of_arbitrary_prose(self):
        unique_pos = "**AI/ML seat - round 2, CROSS.** UNIQUE_POSITION_NOT_A_PROPOSAL"
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            a, b = "architecture-council", "lucens"
            sess.post(a, "position", 1, unique_pos, phase="open")
            sess.post(b, "position", 1, "Lucens opening that is not a proposal.", phase="open")
            sess.post(a, "hold", 2, "hold A", phase="cross")
            sess.post(b, "hold", 2, "hold L", phase="cross")
            sess.post(a, "refine", 3, "refine A", phase="cross")
            sess.post(b, "refine", 3, "refine L", phase="cross")
            sess.post(a, "support", 4, "support A UNIQUE_SUPPORT_NOT_A_PROPOSAL", phase="converge")
            sess.post(b, "support", 4, "support L", phase="converge")
            rc, out, err = sess.close("consensus")
            self.assertEqual(rc, 0, err or out)
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            table = record.split("## Candidate solutions", 1)[1].split("## Decision", 1)[0]
            self.assertIn(floor.NO_PROPOSAL_NOTE, table)
            self.assertNotIn("UNIQUE_POSITION_NOT_A_PROPOSAL", table)
            self.assertNotIn(unique_pos, table)
            self.assertNotIn("UNIQUE_SUPPORT_NOT_A_PROPOSAL", table)
            self.assertNotIn("| 1 |", table)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            a, b = "architecture-council", "lucens"
            proposal = "Gate shape at the write boundary and update the four readers."
            sess.post(a, "position", 1, unique_pos, phase="open")
            sess.post(b, "position", 1, "Lucens opening.", phase="open")
            rc, out, err = sess.post(
                a, "proposal", 1, proposal, phase="open"
            )
            self.assertEqual(rc, 0, err or out)
            sess.post(a, "hold", 2, "hold A", phase="cross")
            sess.post(b, "hold", 2, "hold L", phase="cross")
            sess.post(a, "refine", 3, "refine A", phase="cross")
            sess.post(b, "refine", 3, "refine L", phase="cross")
            sess.post(a, "support", 4, "support A", phase="converge")
            sess.post(b, "support", 4, "support L", phase="converge")
            rc, out, err = sess.close("consensus")
            self.assertEqual(rc, 0, err or out)
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            table = record.split("## Candidate solutions", 1)[1].split("## Decision", 1)[0]
            self.assertNotIn(floor.NO_PROPOSAL_NOTE, table)
            self.assertIn(proposal, table)
            self.assertIn("| 1 |", table)
            self.assertNotIn("UNIQUE_POSITION_NOT_A_PROPOSAL", table)


class TestDDRecloseCorrectsADefectiveClose(unittest.TestCase):
    """D-D: a defective close is corrected on the record, not made permanent."""

    def test_reclose_is_append_only_and_refuses_a_contradicted_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess, no_converge=True)
            rc, out, err = sess.close("no_convergence")
            self.assertEqual(rc, 0, err or out)
            n_before = len(sess.entries())
            first_record = [e for e in sess.entries() if e["type"] == "record"][-1]

            rc, out, err = sess.close("no_convergence")
            self.assertEqual(rc, 1)
            self.assertIn("session_closed", out + err)
            self.assertEqual(len(sess.entries()), n_before)

            rc, out, err = _run(
                ["reclose", "--dir", str(sess.dir), "--outcome", "no_convergence"]
            )
            self.assertNotEqual(rc, 0)
            self.assertEqual(len(sess.entries()), n_before)

            rc, out, err = sess.reclose(
                "consensus_with_dissent",
                "try the wrong outcome after a defective close",
            )
            self.assertEqual(rc, 1)
            self.assertIn(floor.V_OUTCOME_MISMATCH, out + err)
            self.assertEqual(len(sess.entries()), n_before)
            self.assertEqual(
                [e for e in sess.entries() if e["type"] == "record"][-1]["body"],
                first_record["body"],
            )

            reason = (
                "previous close used a host-authored chosen line; rewrite the record"
            )
            rc, out, err = sess.reclose("no_convergence", reason)
            self.assertEqual(rc, 0, err or out)
            entries = sess.entries()
            self.assertGreater(len(entries), n_before)
            protocol = [
                e
                for e in entries
                if e["type"] == "protocol"
                and "previous close superseded" in (e.get("body") or "")
            ]
            self.assertTrue(protocol)
            self.assertIn(reason, protocol[-1]["body"])
            self.assertIn("previous_outcome:", protocol[-1]["body"])
            records = [e for e in entries if e["type"] == "record"]
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["seq"], first_record["seq"])
            self.assertEqual(records[0]["body"], first_record["body"])
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            self.assertIn("outcome: no_convergence", record)
            self.assertIn("- chosen: none", record)
            rc, out, err = sess.verify()
            self.assertEqual(rc, 0, out + err)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess)
            rc, out, err = sess.reclose(
                "consensus", "there was no previous close"
            )
            self.assertEqual(rc, 1)
            self.assertIn("session_not_closed", out + err)


class TestLiveSessionLabsTrialsCloseMustMatchDerived(unittest.TestCase):
    """The live 2026-09-12 seven-seat floor is the proof these defects are real."""

    def test_live_bf_20260912_close_refuses_cwd_accepts_no_convergence(self):
        self.assertTrue(LIVE_FLOOR.is_file(), LIVE_FLOOR)
        with tempfile.TemporaryDirectory() as tmp:
            dest = _open_live_preclose(tmp)
            derived = floor.derive_outcome(
                floor.load_entries(dest), floor.roster_of(dest)
            )
            self.assertEqual(derived, "no_convergence")
            rc, out, err = _run(
                [
                    "close",
                    "--dir",
                    str(dest),
                    "--outcome",
                    "consensus_with_dissent",
                ]
            )
            self.assertEqual(rc, 1)
            blob = out + err
            self.assertIn(floor.V_OUTCOME_MISMATCH, blob)
            self.assertIn("consensus_with_dissent", blob)
            self.assertIn("no_convergence", blob)
            self.assertFalse((dest / "record.md").exists())
            self.assertFalse(
                any(e["type"] == "record" for e in floor.load_entries(dest))
            )

            rc, out, err = _run(
                ["close", "--dir", str(dest), "--outcome", "no_convergence"]
            )
            self.assertEqual(rc, 0, err or out)
            record = (dest / "record.md").read_text(encoding="utf-8")
            self.assertIn("outcome: no_convergence", record)
            chosen = _chosen_line(record)
            self.assertRegex(chosen, r"chosen:\s*none")
            self.assertNotIn(
                "Vote, verbatim from my round-3 statement (seq=19).", chosen
            )
            support_lines = _support_first_lines(floor.load_entries(dest))
            for line in support_lines:
                self.assertNotIn(line, chosen)
            table = record.split("## Candidate solutions", 1)[1].split(
                "## Decision", 1
            )[0]
            self.assertIn(floor.NO_PROPOSAL_NOTE, table)
            self.assertNotIn("**AI/ML seat - round 2, CROSS.**", table)
            rc, out, err = _run(["verify", "--dir", str(dest)])
            self.assertEqual(rc, 0, out + err)


if __name__ == "__main__":
    unittest.main()
