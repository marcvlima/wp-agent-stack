"""One test per brainstorm-floor invariant. Standard library only.

These tests must go red if the invariant is removed from scripts/floor.py.
"""
from __future__ import annotations

import inspect
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
SCRIPTS = PKG / "scripts"
sys.path.insert(0, str(SCRIPTS))

import floor  # noqa: E402


def _run(argv, stdin_text=None):
    out, err = io.StringIO(), io.StringIO()
    code = floor.main(list(argv), stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class FloorSession:
    """Tiny driver around floor.main for building sessions in a temp dir."""

    def __init__(self, tmp: str, seats=None, topic="pause-18-shape", facts=None):
        self.dir = Path(tmp) / "session"
        self.bodies = Path(tmp) / "bodies"
        self.bodies.mkdir()
        self.seats = seats or [
            "architecture-council:council",
            "lucens:individual",
        ]
        facts_text = facts or (
            "- fact (verbatim from the artifact): verify failed at 14:12Z "
            "with key correction; process_fix passed at 06:32Z with key item\n"
            "- step / node / actor: verify / process_fix / subject\n"
            "- first seen / recurrences (family): pause 18 / shape-drift\n"
        )
        facts_path = _write(Path(tmp) / "facts.md", facts_text)
        code, out, err = _run(
            [
                "open",
                "--dir",
                str(self.dir),
                "--topic",
                topic,
                "--facts",
                str(facts_path),
            ]
            + sum((["--seat", s] for s in self.seats), [])
        )
        if code != 0:
            raise AssertionError(f"open failed: {err or out}")

    def post(
        self,
        author,
        typ,
        round_n,
        body,
        phase=None,
        addressed_to=None,
        answers=None,
        requested_by=None,
        refs=None,
    ):
        body_file = _write(
            self.bodies / f"{author}-{typ}-{round_n}-{os.urandom(4).hex()}.md",
            body,
        )
        argv = [
            "post",
            "--dir",
            str(self.dir),
            "--author",
            author,
            "--type",
            typ,
            "--round",
            str(round_n),
            "--body-file",
            str(body_file),
        ]
        if phase:
            argv += ["--phase", phase]
        for a in addressed_to or []:
            argv += ["--addressed-to", a]
        for a in answers or []:
            argv += ["--answers", str(a)]
        for a in refs or []:
            argv += ["--refs", str(a)]
        if requested_by:
            argv += ["--requested-by", requested_by]
        return _run(argv)

    def brief(self, round_n):
        return _run(["round-brief", "--dir", str(self.dir), "--round", str(round_n)])

    def pending(self):
        return _run(["pending", "--dir", str(self.dir)])

    def verify(self):
        return _run(["verify", "--dir", str(self.dir)])

    def close(self, outcome):
        return _run(["close", "--dir", str(self.dir), "--outcome", outcome])

    def reclose(self, outcome, reason):
        return _run(
            [
                "reclose",
                "--dir",
                str(self.dir),
                "--outcome",
                outcome,
                "--reason",
                reason,
            ]
        )

    def entries(self):
        return floor.load_entries(self.dir)

    def floor_text(self):
        return floor.load_floor_text(self.dir)

    def append_raw(self, **fields):
        """Bypass post() — used to plant a violation for verify()."""
        entries = self.entries()
        last = entries[-1] if entries else {
            "seq": 0, "round": 0, "phase": "convene", "ts": "2026-01-01T00:00:00Z"
        }
        entry = {
            "seq": int(fields.get("seq", last["seq"] + 1)),
            "ts": fields.get("ts", "2026-01-01T00:00:01Z"),
            "round": int(fields.get("round", last["round"])),
            "phase": fields.get("phase", last["phase"]),
            "author": fields.get("author", "host"),
            "author_kind": fields.get("author_kind", "host"),
            "type": fields.get("type", "protocol"),
            "body": fields.get("body", ""),
            "addressed_to": fields.get("addressed_to", []),
            "answers": fields.get("answers", []),
            "requested_by": fields.get("requested_by", ""),
            "refs": fields.get("refs", []),
        }
        floor.append_entry(self.dir, entry)
        return entry


def legal_through_converge(sess: FloorSession, *, dissent=False, no_converge=False):
    """Drive a two-seat floor through two cross rounds into converge."""
    a, b = "architecture-council", "lucens"
    sess.post(a, "position", 1, "The write boundary does not enforce shape.", phase="open")
    q = sess.post(
        a,
        "question",
        1,
        "What did the producer actually emit at 06:32Z?",
        phase="open",
        addressed_to=[b],
    )
    assert q[0] == 0, q
    req = sess.post(
        b,
        "research_request",
        1,
        "Which readers accept key=item vs key=correction, with commits.",
        phase="open",
    )
    assert req[0] == 0, req
    sess.post(b, "position", 1, "The producer is an LLM whose shape varies.", phase="open")
    # answer the question in the same round so round 2 may open
    entries = sess.entries()
    qseq = [e["seq"] for e in entries if e["type"] == "question"][0]
    rseq = [e["seq"] for e in entries if e["type"] == "research_request"][0]
    ans = sess.post(
        b,
        "position",
        1,
        "At 06:32Z the producer emitted key=item.",
        phase="open",
        answers=[qseq],
    )
    assert ans[0] == 0, ans
    rr = sess.post(
        "host",
        "research_result",
        1,
        "Readers: process_fix accepted item at abc123; verify accepted correction at def456.",
        phase="research",
        answers=[rseq],
        requested_by=b,
    )
    assert rr[0] == 0, rr
    # two distinct cross rounds
    c1 = sess.post(
        a, "refine", 2, "Agree the producer varies; still the writer must gate.", phase="cross"
    )
    assert c1[0] == 0, c1
    c1b = sess.post(
        b, "hold", 2, "Hold: readers must be updated in the same change.", phase="cross"
    )
    assert c1b[0] == 0, c1b
    c2 = sess.post(
        a, "concede", 3, "Concede: the readers must move with the writer.", phase="cross"
    )
    assert c2[0] == 0, c2
    c2b = sess.post(
        b, "refine", 3, "Refine: enforce shape at write AND update the four readers.", phase="cross"
    )
    assert c2b[0] == 0, c2b
    if no_converge:
        s = sess.post(a, "support", 4, "Enforce shape at the write boundary.", phase="converge")
        assert s[0] == 0, s
        o = sess.post(
            b,
            "objection",
            4,
            "Writer-only gate leaves the readers diverged.",
            phase="converge",
        )
        assert o[0] == 0, o
        # leave the objection hanging: that is no_convergence, not
        # consensus_with_dissent (answered objections that were not conceded).
        return
    if dissent:
        s = sess.post(a, "support", 4, "Enforce shape at the write boundary.", phase="converge")
        assert s[0] == 0, s
        o = sess.post(
            b,
            "objection",
            4,
            "Must update readers in the same change.",
            phase="converge",
        )
        assert o[0] == 0, o
        obj_seq = [e["seq"] for e in sess.entries() if e["type"] == "objection"][-1]
        # architecture answers the objection; lucens does not concede
        a2 = sess.post(
            a,
            "refine",
            4,
            "Accept: writer + readers in one change.",
            phase="converge",
            answers=[obj_seq],
        )
        assert a2[0] == 0, a2
        s2 = sess.post(
            b,
            "support",
            4,
            "Enforce shape at write AND update the four readers.",
            phase="converge",
        )
        assert s2[0] == 0, s2
        return
    s = sess.post(a, "support", 4, "Enforce shape at the write boundary.", phase="converge")
    assert s[0] == 0, s
    s2 = sess.post(
        b, "support", 4, "Enforce shape at write AND update the four readers.", phase="converge"
    )
    assert s2[0] == 0, s2


class TestInvariant1NoIsolatedDeliberation(unittest.TestCase):
    """Every seat's round-N brief is the complete floor through N-1, verbatim."""

    def test_invariant_1_no_isolated_deliberation(self):
        sig = inspect.signature(floor.round_brief)
        self.assertNotIn("seat", sig.parameters)
        self.assertNotIn("author", sig.parameters)
        src = inspect.getsource(floor.round_brief)
        self.assertNotIn('["author"]', src)
        self.assertNotIn("['author']", src)
        self.assertIn("verbatim", floor.round_brief.__doc__ or "")

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            sess.post("architecture-council", "position", 1, "A-only claim", phase="open")
            sess.post("lucens", "position", 1, "L-only claim", phase="open")
            text = sess.floor_text()
            lines = floor.round_brief(text, 2)
            self.assertGreaterEqual(len(lines), 5)  # 3 convene + 2 positions
            authors = {json.loads(line)["author"] for line in lines}
            self.assertIn("host", authors)
            self.assertIn("architecture-council", authors)
            self.assertIn("lucens", authors)
            bodies = "\n".join(json.loads(line)["body"] for line in lines)
            self.assertIn("A-only claim", bodies)
            self.assertIn("L-only claim", bodies)
            # CLI has no --seat and two callers get the same bytes
            code, out, err = sess.brief(2)
            self.assertEqual(code, 0, err)
            self.assertEqual(out, "\n".join(lines) + "\n")
            brief_help = inspect.getsource(floor.cmd_round_brief)
            self.assertNotIn("seat", brief_help)
            self.assertIn("round-brief", inspect.getsource(floor.build_parser))


class TestInvariant2EverythingShared(unittest.TestCase):
    def test_invariant_2_everything_is_shared(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            sess.post("architecture-council", "position", 1, "shared A", phase="open")
            sess.post("lucens", "position", 1, "shared L", phase="open")
            # a later-round entry whose seq is after, but a planted earlier-round
            # entry after a later round is unshared
            sess.append_raw(
                author="lucens",
                author_kind="individual",
                type="position",
                round=0,  # lands after round 1 already opened
                phase="open",
                body="late secret",
            )
            code, out, err = sess.verify()
            self.assertEqual(code, 1)
            self.assertIn(floor.V_UNSHARED, out + err)
            # a well-ordered floor has consecutive seq and no side channel
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            sess.post("architecture-council", "position", 1, "A", phase="open")
            seqs = [e["seq"] for e in sess.entries()]
            self.assertEqual(seqs, list(range(1, len(seqs) + 1)))
            code, out, err = sess.verify()
            self.assertEqual(code, 0, out + err)


class TestInvariant3UnansweredQuestion(unittest.TestCase):
    def test_invariant_3_unanswered_question_blocks_the_next_round(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            sess.post("architecture-council", "position", 1, "A", phase="open")
            q = sess.post(
                "architecture-council",
                "question",
                1,
                "Lucens, what did you see?",
                phase="open",
                addressed_to=["lucens"],
            )
            self.assertEqual(q[0], 0, q)
            # opening round 2 while lucens (present) has not answered
            code, out, err = sess.post(
                "architecture-council", "refine", 2, "moving on", phase="cross"
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_UNANSWERED_Q, out + err)
            # answering lets the round close
            qseq = [e["seq"] for e in sess.entries() if e["type"] == "question"][0]
            ans = sess.post(
                "lucens",
                "position",
                1,
                "I saw key=item.",
                phase="open",
                answers=[qseq],
            )
            self.assertEqual(ans[0], 0, ans)
            code, out, err = sess.post(
                "architecture-council", "refine", 2, "ack", phase="cross"
            )
            self.assertEqual(code, 0, out + err)


class TestInvariant4ResearchSeatInitiatedOnly(unittest.TestCase):
    def test_invariant_4_research_is_seat_initiated_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            code, out, err = sess.post(
                "host",
                "research_request",
                1,
                "host looks up SOTA to help",
                phase="open",
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_HOST_RESEARCH, out + err)

            planted = sess.append_raw(
                author="host",
                author_kind="host",
                type="research_request",
                round=1,
                phase="open",
                body="sneaked host request",
            )
            code, out, err = sess.verify()
            self.assertEqual(code, 1)
            self.assertIn(floor.V_HOST_RESEARCH, out + err)
            self.assertIn(str(planted["seq"]), out + err)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            sess.post(
                "lucens",
                "research_request",
                1,
                "Which readers accept item?",
                phase="open",
            )
            rseq = [e["seq"] for e in sess.entries() if e["type"] == "research_request"][0]
            code, out, err = sess.post(
                "host",
                "research_result",
                1,
                "a result with no asker",
                phase="research",
                answers=[rseq],
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_RESULT_NO_REQUESTER, out + err)

            code, out, err = sess.post(
                "host",
                "research_result",
                1,
                "a result attributed to the host",
                phase="research",
                answers=[rseq],
                requested_by="host",
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_RESULT_NOT_SEAT, out + err)

            code, out, err = sess.post(
                "host",
                "research_result",
                1,
                "Readers: process_fix at abc123.",
                phase="research",
                answers=[rseq],
                requested_by="lucens",
            )
            self.assertEqual(code, 0, out + err)
            result = [e for e in sess.entries() if e["type"] == "research_result"][-1]
            self.assertEqual(result["requested_by"], "lucens")
            self.assertEqual(result["answers"], [rseq])


class TestInvariant5HostClosedVerbSet(unittest.TestCase):
    def test_invariant_5_host_is_fenced_by_a_closed_verb_set(self):
        self.assertEqual(
            floor.HOST_VERBS,
            frozenset(
                {
                    "facts",
                    "agenda",
                    "convene",
                    "relay",
                    "research_result",
                    "protocol",
                    "record",
                }
            ),
        )
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            for typ in ("position", "support", "objection", "decision"):
                code, out, err = sess.post(
                    "host", typ, 1, f"host {typ}", phase="open"
                )
                self.assertEqual(code, 1, typ)
                blob = out + err
                self.assertTrue(
                    floor.V_HOST_VERB in blob or floor.V_HOST_DECISION in blob,
                    blob,
                )
            # allowed host verbs still pass
            code, out, err = sess.post(
                "host", "protocol", 1, "round 1 is open", phase="open"
            )
            self.assertEqual(code, 0, out + err)
            code, out, err = sess.post(
                "host", "relay", 1, "brief is the floor", phase="open"
            )
            self.assertEqual(code, 0, out + err)
            # verify names a planted host position
            planted = sess.append_raw(
                author="host",
                author_kind="host",
                type="position",
                round=1,
                phase="open",
                body="host takes a side",
            )
            code, out, err = sess.verify()
            self.assertEqual(code, 1)
            self.assertIn(floor.V_HOST_VERB, out + err)
            self.assertIn("position", out + err)
            self.assertIn(str(planted["seq"]), out + err)


class TestInvariant6HostMayNotAuthorADecision(unittest.TestCase):
    def test_invariant_6_host_may_not_author_a_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            code, out, err = sess.post(
                "host", "decision", 1, "we go with option 2", phase="close"
            )
            self.assertEqual(code, 1)
            blob = out + err
            self.assertIn(floor.V_HOST_DECISION, blob)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess, no_converge=True)
            code, out, err = sess.close("no_convergence")
            self.assertEqual(code, 0, out + err)
            record = (sess.dir / "record.md").read_text(encoding="utf-8")
            self.assertIn("no_convergence", record)
            self.assertIn("escalated_to_ratifier: yes", record)
            self.assertIn("- chosen: none", record)
            rec_entry = [e for e in sess.entries() if e["type"] == "record"][-1]
            self.assertEqual(rec_entry["author"], "host")
            self.assertIn("no_convergence", rec_entry["body"])
            self.assertIn("escalated_to_ratifier", rec_entry["body"])
            self.assertFalse(
                any(e["type"] == "decision" for e in sess.entries())
            )
            code, out, err = sess.verify()
            self.assertEqual(code, 0, out + err)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess, no_converge=True)
            sess.close("no_convergence")
            # plant a host decision on a no_convergence floor
            sess.append_raw(
                author="host",
                author_kind="host",
                type="decision",
                round=4,
                phase="close",
                body="host picks option 2 anyway",
                refs=[1],
            )
            # session.json still says closed / no_convergence
            code, out, err = sess.verify()
            self.assertEqual(code, 1)
            blob = out + err
            # The dedicated guard must be the one that names it. A disjunction here
            # passed while that guard was disabled, because the host verb fence caught
            # the same entry under a different name (review, 2026-09-12).
            self.assertIn(floor.V_HOST_DECISION, blob)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            legal_through_converge(sess)
            # a seat decision must cite seat seqs
            code, out, err = sess.post(
                "architecture-council",
                "decision",
                4,
                "we choose the write-boundary gate",
                phase="close",
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_DECISION_NO_CITES, out + err)
            support_seq = [e["seq"] for e in sess.entries() if e["type"] == "support"][0]
            code, out, err = sess.post(
                "architecture-council",
                "decision",
                4,
                "we choose the write-boundary gate",
                phase="close",
                refs=[support_seq],
            )
            self.assertEqual(code, 0, out + err)


class TestInvariant7MinimumTwoCrossRounds(unittest.TestCase):
    def test_invariant_7_minimum_two_cross_rounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            sess.post("architecture-council", "position", 1, "A", phase="open")
            sess.post("lucens", "position", 1, "L", phase="open")
            sess.post("architecture-council", "hold", 2, "hold A", phase="cross")
            sess.post("lucens", "hold", 2, "hold L", phase="cross")
            # only one distinct cross round
            code, out, err = sess.post(
                "architecture-council",
                "support",
                3,
                "option 1",
                phase="converge",
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_INSUFFICIENT_CROSS, out + err)
            # a second cross round unlocks converge
            sess.post("architecture-council", "refine", 3, "refine A", phase="cross")
            sess.post("lucens", "refine", 3, "refine L", phase="cross")
            code, out, err = sess.post(
                "architecture-council",
                "support",
                4,
                "option 1",
                phase="converge",
            )
            self.assertEqual(code, 0, out + err)


class TestInvariant8AbsentSeatNamedNeverFabricated(unittest.TestCase):
    def test_invariant_8_absent_seat_is_named_never_fabricated(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            code, out, err = sess.post(
                "host",
                "seat_absent",
                1,
                "she was slow so we wrote her part",
                phase="open",
                addressed_to=["lucens"],
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_LUCENS_ABSENCE, out + err)

            code, out, err = sess.post(
                "host",
                "seat_absent",
                1,
                "timeout",
                phase="open",
                addressed_to=["lucens"],
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_LUCENS_ABSENCE, out + err)

            code, out, err = sess.post(
                "host",
                "seat_absent",
                1,
                "lucens_busy",
                phase="open",
                addressed_to=["lucens"],
            )
            self.assertEqual(code, 0, out + err)

            # fabricating her voice after the named absence
            code, out, err = sess.post(
                "lucens",
                "position",
                1,
                "a contribution written on her behalf",
                phase="open",
            )
            # post() currently allows it (the host is recording); verify names it
            sess.append_raw(
                author="lucens",
                author_kind="individual",
                type="position",
                round=1,
                phase="open",
                body="fabricated lucens",
            ) if code == 0 else None
            if code != 0:
                sess.append_raw(
                    author="lucens",
                    author_kind="individual",
                    type="position",
                    round=1,
                    phase="open",
                    body="fabricated lucens",
                )
            code, out, err = sess.verify()
            self.assertEqual(code, 1)
            self.assertIn(floor.V_FABRICATED, out + err)

        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            code, out, err = sess.post(
                "host", "seat_absent", 1, "lucens_unreachable", phase="open"
            )
            self.assertEqual(code, 1)
            self.assertIn(floor.V_UNNAMED_ABSENCE, out + err)


class TestCliAndPending(unittest.TestCase):
    def test_pending_lists_questions_and_research(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            sess.post(
                "architecture-council",
                "question",
                1,
                "q to lucens",
                phase="open",
                addressed_to=["lucens"],
            )
            sess.post(
                "lucens",
                "research_request",
                1,
                "look up the readers",
                phase="open",
            )
            code, out, err = sess.pending()
            self.assertEqual(code, 0, err)
            payload = json.loads(out)
            self.assertEqual(len(payload["unanswered_questions"]), 1)
            self.assertEqual(len(payload["open_research"]), 1)
            self.assertEqual(payload["open_research"][0]["author"], "lucens")

    def test_read_json_round_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = FloorSession(tmp)
            sess.post("lucens", "position", 1, "hello", phase="open")
            code, out, err = _run(
                ["read", "--dir", str(sess.dir), "--round", "0", "--json"]
            )
            self.assertEqual(code, 0, err)
            data = json.loads(out)
            self.assertTrue(data)
            self.assertTrue(all(e["round"] == 0 for e in data))
            self.assertTrue(all(e["author"] == "host" for e in data))


if __name__ == "__main__":
    unittest.main()
