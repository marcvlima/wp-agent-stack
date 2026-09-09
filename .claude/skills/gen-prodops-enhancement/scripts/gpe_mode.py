#!/usr/bin/env python3
"""gen prodops enhancement mode — the state the assistant re-reads, on disk.

The mode is a FILE, not a memory. Lucens named the failure of a thin supervisor protocol
(2026-09-08): *supervisory drift* — an assistant that forgets it is in the mode and quietly does
the work itself. This module is the cure: arming, cycles, attempts, facts, halts and closes all
land in `<repo>/.risegen/gpe-mode/state.json`, and every turn begins by reading it.

Nothing here judges: judging is `gpe_audit.py`, against `references/request-contract.yaml`.
Standard library only.

    gpe_mode.py arm        --repo R [--gen PATH]
    gpe_mode.py status     --repo R [--json]
    gpe_mode.py open       --repo R --request FILE|-
    gpe_mode.py acceptance --repo R --command CMD
    gpe_mode.py attempt    --repo R --worktree PATH [--session-id ID]
                                    [--cause NAME] [--correction COMMIT] [--redeployed]
    gpe_mode.py fact       --repo R NAME VALUE
    gpe_mode.py halt       --repo R NAME [--detail TEXT]
    gpe_mode.py doctor     --repo R --session-id ID --backlog FILE [--prescriptions FILE]
    gpe_mode.py close      --repo R --outcome fulfilled|new_attempt
    gpe_mode.py disarm     --repo R
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

#: The founder's three areas, closed by enum — the same set the Ascent rite enforces as
#: LUCENS_BACKLOG_AREAS / evolve.lucens_backlog_three_areas.
LUCENS_BACKLOG_AREAS = ("quantum_computing", "ontologies", "logic")

#: Halts, read from gen's OWN record (references/halts.md).
HALTS = (
    "gen_asked_user",
    "gen_stalled",
    "gen_loop_detected",
    "gen_repeats_completion",
    "audit_tampering_detected",
    "gen_exit_nonzero",
    "acceptance_failed",
    "none",
)

STATE_REL = os.path.join(".risegen", "gpe-mode", "state.json")


class ModeError(RuntimeError):
    """A named refusal. Its text is the name the assistant reports — never a workaround."""


# ---------------------------------------------------------------- state io

def state_path(repo: str) -> str:
    return os.path.join(repo, STATE_REL)


def read_state(repo: str) -> Dict[str, Any]:
    path = state_path(repo)
    if not os.path.exists(path):
        return {"armed": False, "cycles": []}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_state(repo: str, state: Dict[str, Any]) -> str:
    path = state_path(repo)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False, sort_keys=False)
        fh.write("\n")
    os.replace(tmp, path)
    return path


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def require_armed(state: Dict[str, Any]) -> None:
    if not state.get("armed"):
        raise ModeError("mode_not_armed")


def current_cycle(state: Dict[str, Any]) -> Dict[str, Any]:
    cycles = state.get("cycles") or []
    if not cycles:
        raise ModeError("no_open_cycle")
    cycle = cycles[-1]
    if cycle.get("outcome") == "fulfilled":
        raise ModeError("no_open_cycle")
    return cycle


def current_attempt(cycle: Dict[str, Any]) -> Dict[str, Any]:
    attempts = cycle.get("attempts") or []
    if not attempts:
        raise ModeError("no_open_attempt")
    return attempts[-1]


# ---------------------------------------------------------------- gen read-back

def gen_readback(gen_path: Optional[str] = None,
                 runner=subprocess.run) -> Dict[str, str]:
    """Read the gen build that will execute: its path, version and sha256.

    An armed mode over an unknown build cannot judge a redeploy later, so an unreadable gen is a
    named refusal (`gen_unreadable`) — never an arming with a blank version.
    """
    path = gen_path or _which("gen")
    if not path or not os.path.exists(path):
        raise ModeError("gen_unreadable: no gen binary at %s" % (path or "$PATH"))
    try:
        proc = runner([path, "--version"], capture_output=True, text=True, timeout=60)
    except Exception as exc:  # noqa: BLE001 - the reason travels in the name
        raise ModeError("gen_unreadable: %s" % exc) from exc
    if proc.returncode != 0:
        raise ModeError("gen_unreadable: `%s --version` exited %s" % (path, proc.returncode))
    version = (proc.stdout or proc.stderr or "").strip().splitlines()
    return {
        "path": path,
        "version": version[0].strip() if version else "",
        "sha256": _sha256(path),
    }


def _which(name: str) -> Optional[str]:
    for part in (os.environ.get("PATH") or "").split(os.pathsep):
        cand = os.path.join(part, name)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- commands

def cmd_arm(repo: str, gen_path: Optional[str] = None, runner=subprocess.run) -> Dict[str, Any]:
    gen = gen_readback(gen_path, runner=runner)
    state = read_state(repo)
    state.update({
        "armed": True,
        "armed_at": _now(),
        "repo": os.path.abspath(repo),
        "gen": gen,
    })
    state.setdefault("cycles", [])
    write_state(repo, state)
    return state


def cmd_disarm(repo: str) -> Dict[str, Any]:
    state = read_state(repo)
    state["armed"] = False
    state["disarmed_at"] = _now()
    write_state(repo, state)
    return state


def cmd_open(repo: str, request: str) -> Dict[str, Any]:
    """Open a cycle on the founder's words, VERBATIM. A paraphrase is where the objective drifts."""
    state = read_state(repo)
    require_armed(state)
    if not request.strip():
        raise ModeError("empty_request")
    cycles = state.setdefault("cycles", [])
    if cycles and cycles[-1].get("outcome") not in ("fulfilled", "abandoned"):
        raise ModeError("cycle_still_open: %s" % cycles[-1]["id"])
    cycle = {
        "id": "gpe-%s" % hashlib.sha256((request + _now()).encode()).hexdigest()[:12],
        "opened_at": _now(),
        "request": request,
        "acceptance": None,
        "attempts": [],
        "facts": {"open.request_verbatim": True},
        "outcome": None,
    }
    cycles.append(cycle)
    write_state(repo, state)
    return cycle


def cmd_acceptance(repo: str, command: str) -> Dict[str, Any]:
    """Declare the acceptance BEFORE the dispatch, and hold it out of gen's brief.

    An acceptance written after a result is `acceptance_authored_after_result`: the check would
    then be shaped by the answer it is supposed to judge.
    """
    state = read_state(repo)
    require_armed(state)
    cycle = current_cycle(state)
    for attempt in cycle.get("attempts") or []:
        if attempt.get("facts", {}).get("judge.acceptance_result"):
            raise ModeError("acceptance_authored_after_result")
    cycle["acceptance"] = {
        "command": command,
        "declared_at": _now(),
        "held_out": True,
    }
    cycle["facts"]["open.acceptance_declared"] = True
    cycle["facts"]["open.acceptance_held_out"] = True
    write_state(repo, state)
    return cycle["acceptance"]


def cmd_attempt(repo: str, worktree: str, session_id: str = "",
                cause: str = "", correction: str = "", redeployed: bool = False,
                backlog_ref: str = "") -> Dict[str, Any]:
    """Open an attempt.

    There is no cap (founder, 2026-09-08: it iterates until the request is fulfilled). The bound is
    NOVELTY: a second attempt names a cause never named before in this cycle, and carries a
    correction that landed AND was redeployed since the previous attempt. A repetition is refused
    by name — `no_new_correction` — and the missing correction is found, not the request abandoned.
    """
    state = read_state(repo)
    require_armed(state)
    cycle = current_cycle(state)
    attempts = cycle.setdefault("attempts", [])
    if attempts:
        previous = [a.get("cause") for a in attempts if a.get("cause")]
        if not cause:
            raise ModeError("no_new_correction: a new attempt must name its cause")
        if cause in previous and not (correction and redeployed):
            raise ModeError(
                "no_new_correction: cause %r was already named and no correction landed and "
                "redeployed since" % cause)
        if not (correction and redeployed):
            raise ModeError(
                "no_new_correction: a new attempt opens on a redeployed correction, never on the "
                "build that already failed")

        # M1 (Code Doctor cvsess-63124fd46e3b4c68) — the attempt gate. On cycle
        # gpe-8a711f9ba13b the check above passed eight times while the flow was in breach from
        # its second iteration: a NEW CAUSE with an OLD COMMIT satisfied it, so attempts 5, 6, 7
        # and 8 all rode d0a39d3. The cause is what the supervisor writes; the commit is what
        # actually changed. Only the commit is evidence.
        #
        # This is the law the mode landed inside gen as C-BRIEF-01 — an act whose precondition
        # cannot hold does not exist — finally applied to the harness's own state machine. The
        # council's finding was that the mode enforced against its subject the very rule it
        # exempted itself from.
        spent = {(a.get("correction") or {}).get("commit") for a in attempts}
        spent.discard(None)
        spent.discard("")
        if correction in spent:
            raise ModeError(
                "no_new_correction: commit %s already carried a previous attempt of this cycle. "
                "A new cause with an old commit is not a new correction — find the missing "
                "correction, land it, redeploy, then reopen." % correction[:12])
        if not backlog_ref:
            raise ModeError(
                "no_backlog_lineage: a correction that lands as CODE carries the backlog item it "
                "came from. Five commits landed on a product main with none, under an override "
                "scoped to work that by definition has no code deliverable.")
        if not (attempts[-1].get("council") or {}).get("session_id"):
            raise ModeError(
                "no_council_behind_attempt: attempt %d has no Code Doctor recorded. Every cycle "
                "ends in a deliberation, on success and on failure, and the next attempt opens "
                "from it — not from the supervisor's own judgement."
                % attempts[-1].get("n", len(attempts)))
    attempt = {
        "n": len(attempts) + 1,
        "opened_at": _now(),
        "worktree": worktree,
        "session_id": session_id,
        "cause": cause,
        "correction": ({"commit": correction, "redeployed": bool(redeployed),
                        "backlog_ref": backlog_ref} if correction else None),
        # M2: council identity lives HERE, on the attempt, and never in a cycle-level facts dict.
        # On gpe-8a711f9ba13b `close --outcome new_attempt` followed by `attempt` wiped the cycle
        # facts, so a council that genuinely convened reads as None today.
        "council": {},
        "facts": {"provision.worktree": worktree},
        "halt": None,
    }
    if session_id:
        attempt["facts"]["dispatch.session_id"] = session_id
    attempts.append(attempt)
    write_state(repo, state)
    return attempt


def cmd_fact(repo: str, name: str, value: Any) -> Dict[str, Any]:
    """Record a fact WHEN IT IS MEASURED. A fact written ahead of its measurement is the first
    step of a fabricated close."""
    state = read_state(repo)
    require_armed(state)
    cycle = current_cycle(state)
    try:
        target = current_attempt(cycle)
    except ModeError:
        target = cycle
    target.setdefault("facts", {})[name] = value
    write_state(repo, state)
    return {name: value}


def cmd_halt(repo: str, name: str, detail: str = "") -> Dict[str, Any]:
    """Name a halt. Naming it is the assistant's signal that gen's processes are ALREADY gone:
    stopping means the in-flight work is over, not that a flag was set (founder, 2026-09-05)."""
    if name not in HALTS:
        raise ModeError("unknown_halt: %s" % name)
    state = read_state(repo)
    require_armed(state)
    attempt = current_attempt(current_cycle(state))
    attempt["halt"] = None if name == "none" else name
    attempt.setdefault("facts", {})["supervise.halt"] = name
    if detail:
        attempt["halt_detail"] = detail
    write_state(repo, state)
    return {"halt": name, "detail": detail}


def backlog_gaps(entries: List[Dict[str, Any]]) -> List[str]:
    """Areas of the founder's three that no well-formed entry covers.

    An entry counts for its area only when `area` is one of the three — named, never inferred —
    and it carries a title. An absent backlog is all three missing.
    """
    covered = set()
    for entry in entries or []:
        area = str((entry or {}).get("area") or "").strip()
        title = str((entry or {}).get("title") or "").strip()
        if area in LUCENS_BACKLOG_AREAS and title:
            covered.add(area)
    return [area for area in LUCENS_BACKLOG_AREAS if area not in covered]


def cmd_doctor(repo: str, session_id: str, backlog: List[Dict[str, Any]],
               prescriptions: Optional[List[Dict[str, Any]]] = None,
               lucens_present: bool = True, lucens_absent_reason: str = "") -> Dict[str, Any]:
    """Record the Code Doctor close over this session. Her backlog is HERS: this never writes an
    entry on her behalf (ADR 0077) — it only reads what she answered and names what is missing."""
    state = read_state(repo)
    require_armed(state)
    attempt = current_attempt(current_cycle(state))
    gaps = backlog_gaps(backlog)
    prescriptions = prescriptions or []
    outside = [p.get("target") for p in prescriptions
               if not str(p.get("target") or "").strip().startswith("gen:")]
    doctor = {
        "council_session_id": session_id,
        "lucens": {"present": bool(lucens_present), "absent_reason": lucens_absent_reason},
        "lucens_backlog": backlog,
        "lucens_backlog_gaps": gaps,
        "prescriptions": prescriptions,
        "targets_outside_gen": outside,
        "recorded_at": _now(),
    }
    # M2: the identity is immutable once written. A council that convened is a fact about the
    # past, and a later transition may not quietly replace it with another session's id.
    existing = (attempt.get("council") or {}).get("session_id")
    if existing and session_id and existing != session_id:
        raise ModeError(
            "council_identity_immutable: attempt %d already recorded council %s; a deliberation "
            "that happened cannot be overwritten by another." % (attempt.get("n", 0), existing))
    attempt["council"] = {"session_id": session_id, "recorded_at": _now()}
    attempt["doctor"] = doctor
    facts = attempt.setdefault("facts", {})
    facts["doctor.council_real"] = bool(session_id)
    facts["doctor.lucens_present"] = bool(lucens_present)
    facts["doctor.lucens_backlog_three_areas"] = not gaps
    facts["doctor.targets_gen"] = not outside
    write_state(repo, state)
    return doctor


def cmd_close(repo: str, outcome: str) -> Dict[str, Any]:
    if outcome not in ("fulfilled", "new_attempt"):
        raise ModeError("unknown_outcome: %s" % outcome)
    state = read_state(repo)
    require_armed(state)
    cycle = current_cycle(state)
    attempt = current_attempt(cycle)
    attempt.setdefault("facts", {})["close.outcome"] = outcome
    # M2 close-gate (Code Doctor cvsess-63124fd46e3b4c68): a cycle cannot close while any attempt
    # lacks a council. On gpe-8a711f9ba13b eight attempts closed behind one deliberation, and the
    # founder ratified the result by hand while the flow was in breach — success masked it.
    uncouncilled = [a.get("n") for a in cycle.get("attempts", [])
                    if not (a.get("council") or {}).get("session_id")]
    if uncouncilled:
        raise ModeError(
            "close_without_council: attempt(s) %s carry no Code Doctor. Every cycle ends in a "
            "deliberation, on success and on failure — a cycle cannot be closed around the ones "
            "that were skipped." % ", ".join(str(n) for n in uncouncilled))
    if outcome == "fulfilled":
        if attempt["facts"].get("judge.acceptance_result") != "fulfilled":
            raise ModeError(
                "close_without_acceptance: a cycle closes fulfilled only on the supervisor's own "
                "execution of the held-out acceptance")
        cycle["outcome"] = "fulfilled"
        cycle["closed_at"] = _now()
    else:
        cycle["outcome"] = None
    write_state(repo, state)
    return {"outcome": outcome, "cycle": cycle["id"]}


def cmd_status(repo: str) -> Dict[str, Any]:
    state = read_state(repo)
    cycles = state.get("cycles") or []
    cycle = cycles[-1] if cycles else None
    return {
        "armed": bool(state.get("armed")),
        "repo": state.get("repo") or os.path.abspath(repo),
        "gen": state.get("gen"),
        "cycle": (cycle or {}).get("id"),
        "attempts": len((cycle or {}).get("attempts") or []),
        "outcome": (cycle or {}).get("outcome"),
    }


# ---------------------------------------------------------------- cli

def _load_json_file(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(prog="gpe_mode.py", description=__doc__)
    parser.add_argument("--repo", default=".")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("arm"); p.add_argument("--gen", default=None)
    sub.add_parser("disarm")
    sub.add_parser("status").add_argument("--json", action="store_true")
    p = sub.add_parser("open"); p.add_argument("--request", required=True)
    p = sub.add_parser("acceptance"); p.add_argument("--command", required=True)
    p = sub.add_parser("attempt")
    p.add_argument("--backlog-ref", default="", dest="backlog_ref",
                   help="the ABG item this correction came from (M1: a correction that lands as "
                        "code carries its lineage)")
    p.add_argument("--worktree", required=True)
    p.add_argument("--session-id", default="")
    p.add_argument("--cause", default="")
    p.add_argument("--correction", default="")
    p.add_argument("--redeployed", action="store_true")
    p = sub.add_parser("fact"); p.add_argument("name"); p.add_argument("value")
    p = sub.add_parser("halt"); p.add_argument("name"); p.add_argument("--detail", default="")
    p = sub.add_parser("doctor")
    p.add_argument("--session-id", required=True)
    p.add_argument("--backlog", required=True)
    p.add_argument("--prescriptions", default="")
    p.add_argument("--lucens-absent", default="")
    p = sub.add_parser("close"); p.add_argument("--outcome", required=True)

    args = parser.parse_args(argv)
    repo = args.repo
    try:
        if args.cmd == "arm":
            out: Any = cmd_arm(repo, args.gen)
            out = {"armed": True, "gen": out["gen"], "state": state_path(repo)}
        elif args.cmd == "disarm":
            out = {"armed": False, "state": state_path(repo)}
            cmd_disarm(repo)
        elif args.cmd == "status":
            out = cmd_status(repo)
        elif args.cmd == "open":
            request = sys.stdin.read() if args.request == "-" else open(
                args.request, encoding="utf-8").read() if os.path.exists(args.request) else args.request
            out = cmd_open(repo, request)
        elif args.cmd == "acceptance":
            out = cmd_acceptance(repo, args.command)
        elif args.cmd == "attempt":
            out = cmd_attempt(repo, args.worktree, args.session_id, args.cause,
                              args.correction, args.redeployed, args.backlog_ref)
        elif args.cmd == "fact":
            try:
                value = json.loads(args.value)
            except json.JSONDecodeError:
                value = args.value
            out = cmd_fact(repo, args.name, value)
        elif args.cmd == "halt":
            out = cmd_halt(repo, args.name, args.detail)
        elif args.cmd == "doctor":
            backlog = _load_json_file(args.backlog)
            prescriptions = _load_json_file(args.prescriptions) if args.prescriptions else []
            out = cmd_doctor(repo, args.session_id, backlog, prescriptions,
                             lucens_present=not args.lucens_absent,
                             lucens_absent_reason=args.lucens_absent)
        elif args.cmd == "close":
            out = cmd_close(repo, args.outcome)
        else:  # pragma: no cover - argparse refuses first
            raise ModeError("unknown_command")
    except ModeError as err:
        print(json.dumps({"ok": False, "refused": str(err)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "result": out}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
