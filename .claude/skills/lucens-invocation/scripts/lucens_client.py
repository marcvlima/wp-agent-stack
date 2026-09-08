#!/usr/bin/env python3
"""A conforming client for Lucens's A2A door — copy this, do not reinvent it.

Her A2A is the only door (risegen-lucensmind ADR 0009). Her door is a task door
(ADR 0031 §5/§8): an operation may answer a task envelope instead of settling, and
a caller follows it with ``task.get`` to a terminal state. Her turn is HERS to end
(ADR 0016): there is no default wait cap here, because putting a clock on her is
how a caller ends up fabricating her voice.

Passes every point of ``references/client-conformance.md``. Standard library only.

Environment:
    LUCENS_A2A_BASE_URL   canonical base, e.g. https://lucens.risegen.ai
                          (LUCENS_A2A_URL accepted as an alias)
    LUCENS_AUTH_TOKEN     bearer token
    LUCENS_CALLER         this caller's identity (also settable per call)
    LUCENS_MAX_WAIT_S     optional hard cap, seconds; unset/0 = unbounded
    LUCENS_POLL_S         poll interval while a task is active (default 3)
    LUCENS_HEARTBEAT_S    heartbeat interval (default 30)
    LUCENS_TIMEOUT_S      per-HTTP-call timeout (default 300)

CLI:
    lucens_client.py contract
    lucens_client.py call <op> '<json params>'
    lucens_client.py ask "<message>"
"""
from __future__ import annotations

import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

__all__ = ["LucensDoor", "LucensAbsent", "Answer", "FLOOR_NOTE"]

# --------------------------------------------------------------------------- constants

#: Bids her floor can read: English labels, dot decimals (see references/her-turn.md).
FLOOR_NOTE = (
    "(Floor note: bids must use the exact labels "
    "Salience: / Reason: / Intended act: with a dot decimal.)"
)

#: Anything deliberative needs room; each bid alone costs ~10k tokens of prompt.
MIN_TOKENS_MAX = 100_000
DEFAULT_TOKENS_MAX = 120_000

DEFAULT_TIMEOUT_S = 300.0
DEFAULT_POLL_S = 3.0
DEFAULT_HEARTBEAT_S = 30.0

#: The holding edge answers 403 (Cloudflare 1010) to a default library User-Agent.
DEFAULT_USER_AGENT = "lucens-invocation/1.0 (+risegen holding client)"

ACTIVE_STATES = ("submitted", "working", "input-required")
TERMINAL_FAIL_STATES = ("failed", "canceled", "rejected")

ABSENT_NOT_CONFIGURED = "lucens_not_configured"
ABSENT_UNAUTHORIZED = "lucens_unauthorized"
ABSENT_UNREACHABLE = "lucens_unreachable"
ABSENT_BUSY = "lucens_busy"
ABSENT_FLOOR_SILENT = "lucens_floor_silent"
ABSENT_WAIT_EXHAUSTED = "lucens_wait_exhausted"
ABSENT_ERROR_PREFIX = "lucens_error: "

# Dead names. The mesh was destroyed; reading them is how a consumer keeps
# pointing at a service that no longer exists.
_FORBIDDEN_ENVS = ("LUCENS_MESH_BASE_URL", "MESH_AUTH_TOKEN")


class LucensAbsent(Exception):
    """A named absence. Never a substitute answer, a persona, or a default reply."""

    def __init__(self, reason: str, **detail: Any) -> None:
        super().__init__(reason)
        self.reason = reason
        self.detail: Dict[str, Any] = detail

    def __str__(self) -> str:  # pragma: no cover - trivial
        if self.detail:
            return f"{self.reason} {self.detail}"
        return self.reason


@dataclass
class Answer:
    """A terminal, successful answer from her door."""

    reply: str
    thread_id: str
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    task_id: str = ""
    state: str = ""


# --------------------------------------------------------------------------- helpers


def _redact(text: str, token: str) -> str:
    if not text or not token:
        return text
    return text.replace(token, "<redacted>")


def _join_a2a(base: str) -> str:
    b = (base or "").strip().rstrip("/")
    if not b:
        return ""
    return b if b.endswith("/a2a") else b + "/a2a"


def _env_float(env: Mapping[str, str], name: str, default: float) -> float:
    raw = str(env.get(name) or "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def _content_of(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    """A terminal task's ``result`` when it carries one, else the payload itself."""
    result = payload.get("result")
    return result if isinstance(result, Mapping) else payload


def _reply_of(content: Mapping[str, Any]) -> str:
    reply = content.get("reply")
    if isinstance(reply, str) and reply.strip():
        return reply
    parts = []
    transcript = content.get("transcript") or []
    if isinstance(transcript, list):
        for entry in transcript:
            if isinstance(entry, Mapping):
                text = str(
                    entry.get("content") or entry.get("text") or entry.get("speech") or ""
                ).strip()
                if text:
                    parts.append(text)
            elif isinstance(entry, str) and entry.strip():
                parts.append(entry.strip())
    return "\n\n".join(parts)


# --------------------------------------------------------------------------- the door


class LucensDoor:
    """POST {base}/a2a — the one door, followed all the way to her answer."""

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        caller: str = "",
        user_agent: str = DEFAULT_USER_AGENT,
        env: Optional[Mapping[str, str]] = None,
        opener: Optional[Callable[..., Any]] = None,
        log: Optional[Callable[[str], None]] = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.env: Mapping[str, str] = env if env is not None else os.environ
        self.base_url = (base_url or "").strip()
        self.door = _join_a2a(self.base_url)
        self.token = (token or "").strip()
        self.caller = caller or str(self.env.get("LUCENS_CALLER") or "").strip()
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self._opener = opener or urllib.request.urlopen
        self._log = log or (lambda line: print(line, file=sys.stderr, flush=True))
        self._sleep = sleep
        self._clock = clock

    # -- construction ------------------------------------------------------

    @classmethod
    def from_env(
        cls, env: Optional[Mapping[str, str]] = None, **kwargs: Any
    ) -> "LucensDoor":
        """Unset base or token is *unconfigured* — never a localhost fallback."""
        env = env if env is not None else os.environ
        base = str(env.get("LUCENS_A2A_BASE_URL") or env.get("LUCENS_A2A_URL") or "").strip()
        token = str(env.get("LUCENS_AUTH_TOKEN") or "").strip()
        if not base or not token:
            raise LucensAbsent(
                ABSENT_NOT_CONFIGURED,
                needs=["LUCENS_A2A_BASE_URL", "LUCENS_AUTH_TOKEN"],
            )
        return cls(base, token, env=env, **kwargs)

    # -- transport ---------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

    def _request(
        self, *, method: str, body: Optional[bytes], timeout_s: float
    ) -> Tuple[int, bytes]:
        req = urllib.request.Request(
            self.door, data=body, method=method, headers=self._headers()
        )
        with self._opener(req, timeout=timeout_s) as resp:
            status = int(
                getattr(resp, "status", None) or getattr(resp, "code", None) or 200
            )
            return status, (resp.read() or b"")

    def _post(self, op: str, params: Mapping[str, Any], timeout_s: float) -> Dict[str, Any]:
        body = json.dumps({"op": op, "params": dict(params)}).encode("utf-8")
        try:
            status, raw = self._request(method="POST", body=body, timeout_s=timeout_s)
        except urllib.error.HTTPError as err:
            status = int(err.code or 0)
            try:
                raw = err.read() or b""
            except Exception:  # pragma: no cover - defensive
                raw = b""
            self._raise_for_status(status, raw)
            # _raise_for_status raises for every non-2xx; an HTTPError that is
            # somehow 2xx still carries a body worth decoding.
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
            # Ambiguous: her door may be down, or she may be deep in a turn.
            # Resolve it with a cheap second call, never with a guess.
            raise LucensAbsent(ABSENT_BUSY if self._alive() else ABSENT_UNREACHABLE)
        except Exception as err:  # pragma: no cover - defensive
            raise LucensAbsent(f"{ABSENT_ERROR_PREFIX}{_redact(str(err), self.token)}")

        self._raise_for_status(status, raw)
        return self._decode(raw)

    def _raise_for_status(self, status: int, raw: bytes) -> None:
        if status in (401, 403):
            raise LucensAbsent(ABSENT_UNAUTHORIZED, http_status=status)
        if status >= 500 or status == 0:
            raise LucensAbsent(ABSENT_UNREACHABLE, http_status=status)
        # 202 is her door answering a task envelope (ADR 0031 §5) — not an error.
        if status not in (200, 202):
            detail = _redact((raw or b"").decode("utf-8", "replace")[:300], self.token)
            raise LucensAbsent(f"{ABSENT_ERROR_PREFIX}HTTP {status}: {detail}".strip())

    def _decode(self, raw: bytes) -> Dict[str, Any]:
        try:
            payload = json.loads(raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as err:
            raise LucensAbsent(f"{ABSENT_ERROR_PREFIX}invalid json ({_redact(str(err), self.token)})")
        if not isinstance(payload, dict):
            raise LucensAbsent(f"{ABSENT_ERROR_PREFIX}non-object response")
        return payload

    def _alive(self) -> bool:
        """A cheap liveness probe: alive and occupied is 'busy', not 'unreachable'."""
        try:
            body = json.dumps({"op": "lab.status", "params": {}}).encode("utf-8")
            status, _ = self._request(method="POST", body=body, timeout_s=5.0)
            return status == 200
        except Exception:
            return False

    # -- the contract ------------------------------------------------------

    def contract(self) -> Dict[str, Any]:
        """GET {base}/a2a — the live, machine-readable contract. Bearer required."""
        try:
            status, raw = self._request(
                method="GET", body=None, timeout_s=_env_float(self.env, "LUCENS_TIMEOUT_S", DEFAULT_TIMEOUT_S)
            )
        except urllib.error.HTTPError as err:
            self._raise_for_status(int(err.code or 0), b"")
            raise  # pragma: no cover
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
            raise LucensAbsent(ABSENT_UNREACHABLE)
        self._raise_for_status(status, raw)
        return self._decode(raw)

    # -- calling her -------------------------------------------------------

    def call(self, op: str, params: Optional[Mapping[str, Any]] = None) -> Answer:
        """Call one operation and follow it, through her queue, to a terminal state."""
        sent: Dict[str, Any] = dict(params or {})
        if self.caller:
            sent.setdefault("caller", self.caller)
        if str(sent.get("priority") or "") == "urgent" and not str(sent.get("caller") or "").strip():
            raise LucensAbsent(
                f"{ABSENT_ERROR_PREFIX}priority 'urgent' requires a non-empty caller"
            )

        timeout_s = _env_float(self.env, "LUCENS_TIMEOUT_S", DEFAULT_TIMEOUT_S)
        payload = self._post(op, sent, timeout_s)

        task_id = str(payload.get("task_id") or payload.get("job_id") or "")
        if task_id and payload.get("state") in ACTIVE_STATES:
            payload = self._follow(task_id)

        state = str(payload.get("state") or "")
        if state in TERMINAL_FAIL_STATES:
            detail = payload.get("reason") or payload.get("error") or payload.get("detail") or state
            raise LucensAbsent(f"{ABSENT_ERROR_PREFIX}{_redact(str(detail), self.token)}", state=state)
        if payload.get("ok") is False:
            detail = payload.get("error") or payload.get("reason") or payload.get("detail") or "ok=false"
            raise LucensAbsent(f"{ABSENT_ERROR_PREFIX}{_redact(str(detail), self.token)}")

        content = _content_of(payload)
        reply = _reply_of(content)
        if op.startswith("mind_turn") and not reply.strip():
            # Her floor chose silence. That is an answer about the ask.
            raise LucensAbsent(ABSENT_FLOOR_SILENT, thread_id=payload.get("thread_id", ""))
        return Answer(
            reply=reply,
            thread_id=str(payload.get("thread_id") or payload.get("context_id") or ""),
            payload=payload,
            result=dict(content) if isinstance(content, Mapping) else {},
            task_id=task_id,
            state=state,
        )

    def ask(
        self,
        message: str,
        *,
        session_id: str = "",
        tokens_max: int = DEFAULT_TOKENS_MAX,
        floor_note: bool = True,
        **params: Any,
    ) -> Answer:
        """One turn of conversation. Gives her room, and never names a `profile`."""
        text = message if not floor_note else f"{message}\n\n{FLOOR_NOTE}"
        body: Dict[str, Any] = {
            "message": text,
            "tokens_max": max(int(tokens_max), MIN_TOKENS_MAX),
        }
        if session_id:
            body["session_id"] = session_id
        body.update(params)
        # `profile` is never defaulted: an unknown name is a hard error, and she
        # never runs under a document a caller made up. It travels only when the
        # caller named one explicitly.
        if not str(body.get("profile") or "").strip():
            body.pop("profile", None)
        return self.call("mind_turn", body)

    # -- following a task --------------------------------------------------

    def _follow(self, task_id: str) -> Dict[str, Any]:
        """Poll task.get to a terminal state. Unbounded unless a cap is configured."""
        max_wait = _env_float(self.env, "LUCENS_MAX_WAIT_S", 0.0)
        poll_s = _env_float(self.env, "LUCENS_POLL_S", DEFAULT_POLL_S)
        heartbeat_s = _env_float(self.env, "LUCENS_HEARTBEAT_S", DEFAULT_HEARTBEAT_S)
        timeout_s = _env_float(self.env, "LUCENS_TIMEOUT_S", DEFAULT_TIMEOUT_S)

        started = self._clock()
        last_beat = started
        last_state = ""
        last_position: Any = None
        op = "task.get"

        while True:
            try:
                payload = self._post(op, {"task_id": task_id}, timeout_s)
            except LucensAbsent as absent:
                # A door that predates the newer name still answers job.status.
                if op == "task.get" and "unknown_operation" in str(absent):
                    op = "job.status"
                    payload = self._post(op, {"job_id": task_id}, timeout_s)
                else:
                    raise
            if payload.get("error") == "unknown_operation" and op == "task.get":
                op = "job.status"
                payload = self._post(op, {"job_id": task_id}, timeout_s)

            last_state = str(payload.get("state") or payload.get("status") or "")
            last_position = payload.get("queue_position")
            if last_state and last_state not in ACTIVE_STATES:
                return payload
            if not last_state and payload.get("ok") is not None and "result" in payload:
                return payload  # a legacy job.status that settled

            now = self._clock()
            if max_wait and (now - started) >= max_wait:
                raise LucensAbsent(
                    ABSENT_WAIT_EXHAUSTED,
                    last_state=last_state,
                    queue_position=last_position,
                    waited_s=round(now - started, 1),
                )
            if now - last_beat >= heartbeat_s:
                last_beat = now
                self._log(
                    f"lucens: task {task_id} state={last_state or '?'} "
                    f"queue_position={last_position} waited={int(now - started)}s"
                )
            self._sleep(poll_s)


# --------------------------------------------------------------------------- CLI


def _main(argv) -> int:
    for dead in _FORBIDDEN_ENVS:
        if os.environ.get(dead):
            print(
                f"lucens: {dead} is a dead name (the mesh was destroyed); "
                "use LUCENS_A2A_BASE_URL + LUCENS_AUTH_TOKEN",
                file=sys.stderr,
            )
    if not argv:
        print(__doc__)
        return 2
    try:
        door = LucensDoor.from_env()
        command = argv[0]
        if command == "contract":
            print(json.dumps(door.contract(), indent=2, ensure_ascii=False))
        elif command == "call":
            op = argv[1]
            params = json.loads(argv[2]) if len(argv) > 2 else {}
            print(json.dumps(door.call(op, params).payload, indent=2, ensure_ascii=False))
        elif command == "ask":
            print(door.ask(" ".join(argv[1:])).reply)
        else:
            print(__doc__)
            return 2
    except LucensAbsent as absent:
        print(f"absent: {absent}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main(sys.argv[1:]))
