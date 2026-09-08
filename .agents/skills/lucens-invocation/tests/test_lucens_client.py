"""Paired tests for the reference client — one per conformance point.

Every test here is a point of `references/client-conformance.md`. A client that
fails one of them either fabricates her voice or abandons her while she thinks.
"""
from __future__ import annotations

import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import lucens_client as lc  # noqa: E402


class FakeResponse(io.BytesIO):
    def __init__(self, payload, status=200):
        raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        super().__init__(raw)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class Recorder:
    """A fake urlopen: records every request, answers a scripted queue."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, req, timeout=None):
        self.requests.append(req)
        if not self.responses:
            raise AssertionError("no scripted response left")
        nxt = self.responses.pop(0)
        if isinstance(nxt, Exception):
            raise nxt
        return FakeResponse(*nxt) if isinstance(nxt, tuple) else FakeResponse(nxt)

    def bodies(self):
        return [json.loads(r.data.decode()) for r in self.requests if r.data]


ENV = {
    "LUCENS_A2A_BASE_URL": "https://lucens.risegen.ai",
    "LUCENS_AUTH_TOKEN": "s3cret-token",
    "LUCENS_CALLER": "test-caller",
    "LUCENS_POLL_S": "0.001",
    "LUCENS_HEARTBEAT_S": "0.001",
}


def door(recorder, env=None, **kw):
    env = dict(ENV, **(env or {}))
    return lc.LucensDoor.from_env(env, opener=recorder, sleep=lambda s: None, **kw)


class ConformanceTest(unittest.TestCase):
    # 1 — canonical name only
    def test_door_is_base_plus_a2a(self):
        d = door(Recorder({"ok": True}))
        self.assertEqual(d.door, "https://lucens.risegen.ai/a2a")

    def test_base_already_ending_in_a2a_is_not_doubled(self):
        d = lc.LucensDoor("https://lucens.risegen.ai/a2a", "t")
        self.assertEqual(d.door, "https://lucens.risegen.ai/a2a")

    def test_dead_mesh_names_are_not_read(self):
        source = Path(lc.__file__).read_text()
        self.assertNotIn('env.get("MESH_AUTH_TOKEN")', source)
        self.assertNotIn('env.get("LUCENS_MESH_BASE_URL")', source)

    # 2 — unconfigured is an absence, never a localhost fallback
    def test_unconfigured_raises_named_absence(self):
        with self.assertRaises(lc.LucensAbsent) as ctx:
            lc.LucensDoor.from_env({})
        self.assertEqual(ctx.exception.reason, lc.ABSENT_NOT_CONFIGURED)

    def test_no_localhost_fallback_in_source(self):
        source = Path(lc.__file__).read_text()
        self.assertNotIn("http://127.0.0.1", source)
        self.assertNotIn("http://localhost", source)

    # 3 + 4 — bearer and a named User-Agent on every call, discovery included
    def test_contract_sends_bearer_and_user_agent(self):
        rec = Recorder({"operations": {}})
        door(rec).contract()
        req = rec.requests[0]
        self.assertEqual(req.get_method(), "GET")
        self.assertEqual(req.headers["Authorization"], "Bearer s3cret-token")
        self.assertNotIn("Python-urllib", req.headers["User-agent"])
        self.assertIn("lucens-invocation", req.headers["User-agent"])

    # 5 — caller identity on every call
    def test_caller_is_sent(self):
        rec = Recorder({"ok": True, "reply": "hi"})
        door(rec).call("mind.state", {})
        self.assertEqual(rec.bodies()[0]["params"]["caller"], "test-caller")

    def test_urgent_priority_requires_a_caller(self):
        rec = Recorder({"ok": True, "reply": "hi"})
        d = door(rec, env={"LUCENS_CALLER": ""})
        with self.assertRaises(lc.LucensAbsent):
            d.call("mind_turn", {"message": "x", "priority": "urgent"})

    # 6 + 7 — 202 is not an error; follow the task to a terminal state
    def test_202_envelope_is_followed_to_completion(self):
        rec = Recorder(
            ({"ok": True, "task_id": "job-1", "state": "submitted", "queue_position": 2}, 202),
            {"ok": True, "task_id": "job-1", "state": "working"},
            {"ok": True, "task_id": "job-1", "state": "completed",
             "result": {"reply": "pronto", "thread_id": "t-9"}},
        )
        answer = door(rec).call("exam.answer", {})
        self.assertEqual(answer.reply, "pronto")
        self.assertEqual(answer.state, "completed")
        self.assertEqual([b["op"] for b in rec.bodies()], ["exam.answer", "task.get", "task.get"])

    def test_job_status_fallback_when_task_get_is_unknown(self):
        rec = Recorder(
            ({"ok": True, "task_id": "job-2", "state": "working"}, 202),
            {"ok": False, "error": "unknown_operation"},
            {"ok": True, "state": "completed", "result": {"reply": "legado"}},
        )
        answer = door(rec).call("trial.rite", {})
        self.assertEqual(answer.reply, "legado")
        self.assertEqual(rec.bodies()[-1]["op"], "job.status")

    # 8 — unbounded by default; a configured cap is an honest absence
    def test_wait_cap_reports_exhaustion_with_last_state(self):
        rec = Recorder(
            ({"ok": True, "task_id": "job-3", "state": "submitted", "queue_position": 4}, 202),
            *[{"ok": True, "task_id": "job-3", "state": "working", "queue_position": 1}] * 5,
        )
        clock = iter([0.0, 0.0, 0.0, 99.0, 99.0])
        d = door(rec, env={"LUCENS_MAX_WAIT_S": "5"}, clock=lambda: next(clock))
        with self.assertRaises(lc.LucensAbsent) as ctx:
            d.call("exam.answer", {})
        self.assertEqual(ctx.exception.reason, lc.ABSENT_WAIT_EXHAUSTED)
        self.assertEqual(ctx.exception.detail["last_state"], "working")
        self.assertEqual(ctx.exception.detail["queue_position"], 1)

    def test_default_has_no_wait_cap(self):
        self.assertEqual(lc._env_float({}, "LUCENS_MAX_WAIT_S", 0.0), 0.0)

    # 9 — progress instead of silence
    def test_heartbeat_names_state_and_queue_position(self):
        lines = []
        rec = Recorder(
            ({"ok": True, "task_id": "job-4", "state": "working"}, 202),
            {"ok": True, "task_id": "job-4", "state": "working", "queue_position": 3},
            {"ok": True, "task_id": "job-4", "state": "completed", "result": {"reply": "ok"}},
        )
        ticks = iter([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        door(rec, log=lines.append, clock=lambda: next(ticks)).call("exam.answer", {})
        self.assertTrue(any("state=working" in l and "queue_position=3" in l for l in lines))

    # 10 — honest failure names
    def test_401_is_unauthorized(self):
        rec = Recorder(urllib.error.HTTPError("u", 401, "no", {}, io.BytesIO(b"{}")))
        with self.assertRaises(lc.LucensAbsent) as ctx:
            door(rec).call("mind.state", {})
        self.assertEqual(ctx.exception.reason, lc.ABSENT_UNAUTHORIZED)

    def test_403_only_door_is_unauthorized_not_a_second_route(self):
        rec = Recorder(urllib.error.HTTPError("u", 403, "no", {}, io.BytesIO(b"{}")))
        with self.assertRaises(lc.LucensAbsent) as ctx:
            door(rec).call("mind.state", {})
        self.assertEqual(ctx.exception.reason, lc.ABSENT_UNAUTHORIZED)

    def test_connection_error_with_live_door_is_busy(self):
        rec = Recorder(OSError("timed out"), {"ok": True})  # second call = lab.status probe
        with self.assertRaises(lc.LucensAbsent) as ctx:
            door(rec).call("mind_turn", {"message": "x"})
        self.assertEqual(ctx.exception.reason, lc.ABSENT_BUSY)
        self.assertEqual(rec.bodies()[-1]["op"], "lab.status")

    def test_connection_error_with_dead_door_is_unreachable(self):
        rec = Recorder(OSError("refused"), OSError("refused"))
        with self.assertRaises(lc.LucensAbsent) as ctx:
            door(rec).call("mind_turn", {"message": "x"})
        self.assertEqual(ctx.exception.reason, lc.ABSENT_UNREACHABLE)

    def test_terminal_failure_names_its_reason(self):
        rec = Recorder(
            ({"ok": True, "task_id": "job-5", "state": "working"}, 202),
            {"ok": True, "task_id": "job-5", "state": "rejected", "reason": "mind_integrity"},
        )
        with self.assertRaises(lc.LucensAbsent) as ctx:
            door(rec).call("trial.rite", {})
        self.assertIn("mind_integrity", str(ctx.exception))

    def test_empty_reply_is_floor_silent_never_a_substitute(self):
        rec = Recorder({"ok": True, "reply": "", "transcript": []})
        with self.assertRaises(lc.LucensAbsent) as ctx:
            door(rec).ask("uma pergunta")
        self.assertEqual(ctx.exception.reason, lc.ABSENT_FLOOR_SILENT)

    def test_transcript_is_joined_when_reply_is_absent(self):
        rec = Recorder({"ok": True, "transcript": [{"content": "um"}, {"speech": "dois"}]})
        self.assertEqual(door(rec).ask("q").reply, "um\n\ndois")

    # 11 — the token never leaks
    def test_token_is_redacted_from_error_text(self):
        rec = Recorder(
            urllib.error.HTTPError("u", 418, "no", {}, io.BytesIO(b'{"error":"s3cret-token"}'))
        )
        with self.assertRaises(lc.LucensAbsent) as ctx:
            door(rec).call("mind.state", {})
        self.assertNotIn("s3cret-token", str(ctx.exception))
        self.assertIn("<redacted>", str(ctx.exception))

    # 12 — give her room
    def test_ask_gives_her_room_and_the_floor_note(self):
        rec = Recorder({"ok": True, "reply": "ok"})
        door(rec).ask("pergunta técnica", tokens_max=3000)
        params = rec.bodies()[0]["params"]
        self.assertGreaterEqual(params["tokens_max"], lc.MIN_TOKENS_MAX)
        self.assertIn("Salience:", params["message"])
        self.assertNotIn("profile", params)

    def test_ask_keeps_an_explicit_profile(self):
        rec = Recorder({"ok": True, "reply": "ok"})
        door(rec).ask("q", profile="voice")
        self.assertEqual(rec.bodies()[0]["params"]["profile"], "voice")


if __name__ == "__main__":
    unittest.main()
