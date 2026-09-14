#!/usr/bin/env python3
"""gen prodops enhancement mode — the state the assistant re-reads, on disk.

The mode is a FILE, not a memory. Lucens named the failure of a thin supervisor protocol
(2026-09-08): *supervisory drift* — an assistant that forgets it is in the mode and quietly does
the work itself. This module is the cure: arming, cycles, attempts, facts, halts and closes all
land in `<repo>/.risegen/gpe-mode/state.json`, and every turn begins by reading it.

Nothing here judges: judging is `gpe_audit.py`, against `references/request-contract.yaml`.
Standard library only.

    gpe_mode.py arm        --repo R [--gen PATH]
    gpe_mode.py model      --repo R
    gpe_mode.py status     --repo R [--json]
    gpe_mode.py open       --repo R --request FILE|-
    gpe_mode.py acceptance --repo R --command CMD --passes-fixture P --fails-fixture F
    gpe_mode.py fixtures-proven --repo R
    gpe_mode.py finding    --repo R --about supervisor|gen --text TEXT [--found-by gen]
    gpe_mode.py attempt    --repo R --worktree PATH [--session-id ID]
                                    [--cause NAME] [--correction COMMIT] [--redeployed]
    gpe_mode.py fact       --repo R NAME VALUE
    gpe_mode.py landed     --repo R --item ID --commit SHA [--note TEXT]
    gpe_mode.py monitor    --repo R start|status
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
import signal
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

#: The founder's three areas, closed by enum — the same set the Ascent rite enforces as
#: LUCENS_BACKLOG_AREAS / evolve.lucens_backlog_three_areas.
LUCENS_BACKLOG_AREAS = ("quantum_computing", "ontologies", "logic")

#: The model gen runs on while the mode is armed — a PIN, not a default (founder, 2026-09-09:
#: *"e pra manter esse mesmo inclusive pode atualizar a skill para que ele sempre rode neste
#: modelo durante este modo"*, ruling on the model cycle gpe-24500fd57f7d measured in gen's own
#: record). It is read from here and passed as `-m` at the dispatch, so the flight never inherits
#: whatever the environment's default happens to be that minute: on this same host, minutes before
#: that dispatch, an unreachable model catalogue made gen announce a fallback to a DIFFERENT model.
#: A pin that lives only in prose is the same silence.
GEN_MODEL = "qwen3.8-flash"

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

#: The minute monitor's proof of life, written by gpe_tick.beat(). Founder, 2026-09-09:
#: *"precisa adicionar na skill pra que tenha um monitor que é ativado a cada minuto para garantir
#: que o fluxo nao pare"*.
#:
#: The first cut of this order added the READING (`supervisor_inert`) and left the RUNNING to the
#: supervisor's memory — which is the one thing that cannot be relied on, because a supervisor
#: that has stopped is exactly a supervisor who is not going to start its own watchdog. So the
#: state machine refuses to move a cycle forward while the heartbeat is stale: no monitor, no rite.
HEARTBEAT_REL = os.path.join(".risegen", "gpe-mode", "monitor", "heartbeat.json")
HEARTBEAT_STALE_SECONDS = 120


def heartbeat_age(repo: str) -> Optional[float]:
    """Seconds since the monitor last proved it was running, or None when it never has."""
    path = os.path.join(repo, HEARTBEAT_REL)
    try:
        with open(path) as fh:
            at = float(json.load(fh).get("at") or 0)
    except (OSError, ValueError, TypeError):
        return None
    if at <= 0:
        return None
    return max(0.0, time.time() - at)


def require_monitor(repo: str) -> None:
    """Refuse to advance the rite while the minute monitor is not running.

    A named refusal, like every other in this module: `monitor_not_running`. The cure is to start
    it — `gpe_mode.py monitor start --repo R` — never to work around it.
    """
    age = heartbeat_age(repo)
    if age is None:
        raise ModeError(
            "monitor_not_running: the minute monitor has never beaten in this repository. "
            "Start it — `gpe_mode.py monitor start --repo <repo>` — and keep it running until "
            "the flow concludes. A flow nobody is watching is the state this mode exists to "
            "forbid.")
    if age > HEARTBEAT_STALE_SECONDS:
        raise ModeError(
            "monitor_not_running: the minute monitor last beat %ds ago (stale past %ds). "
            "Restart it before moving the cycle." % (int(age), HEARTBEAT_STALE_SECONDS))


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
    """Write the state, stamping WHEN the state machine last wrote it.

    The stamp is what lets the tick tell the supervisor's own mandated writes from a write by
    anything else. Measured on cycle gpe-24500fd57f7d: the tick called `audit_tampering_detected`
    on every armed cycle, because the contract REQUIRES the supervisor to record supervise.* and
    judge.* facts AFTER the dispatch, and the tick read any post-dispatch write to the surface as
    tampering. An alarm that is always on is an alarm nobody reads.
    """
    path = state_path(repo)
    state["state_machine_wrote_at"] = time.time()
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
        "model": GEN_MODEL,
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


def cmd_acceptance(repo: str, command: str,
                   passes_fixture: str = "", fails_fixture: str = "",
                   base: str = "") -> Dict[str, Any]:
    """Declare the acceptance BEFORE the dispatch, and hold it out of gen's brief.

    An acceptance written after a result is `acceptance_authored_after_result`: the check would
    then be shaped by the answer it is supposed to judge.

    R3 (Code Doctor cvsess-32e38638bcbe40d7): the acceptance SHIPS WITH A CASE IT MUST FAIL AND A
    CASE IT MUST PASS, and both are recorded here. It is the only artifact in this flow with no
    paired test, and it decides whether a whole cycle's work stands. On attempt 3 of cycle
    gpe-24500fd57f7d its first run reported six failures of which FIVE were false negatives — a
    targeting defect in the check itself, on work that was correct. A false negative voids honest
    work exactly as a false pass launders dishonest work; the only difference is who it wrongs.

    A check never shown to fail is not known to work. A check never shown to pass is not known to
    be fair.
    """
    state = read_state(repo)
    require_armed(state)
    cycle = current_cycle(state)
    for attempt in cycle.get("attempts") or []:
        if attempt.get("facts", {}).get("judge.acceptance_result"):
            raise ModeError("acceptance_authored_after_result")
    if not (str(passes_fixture).strip() and str(fails_fixture).strip()):
        raise ModeError(
            "acceptance_without_fixtures: declare the case it must PASS and the case it must "
            "FAIL. Five of six failures on attempt 3 of gpe-24500fd57f7d were false negatives, "
            "and nothing but a human reading carefully caught them.")
    if not str(base).strip():
        raise ModeError(
            "acceptance_without_base: name the ref this acceptance judges against. On cycle "
            "gpe-24500fd57f7d the supervisor landed one attempt's work mid-cycle, the base moved "
            "under the check, and the SAME command produced 18/9 and 27/27 — both honest, only "
            "one of them measuring the party under test.")
    cycle["acceptance"] = {
        "command": command,
        "base": base,
        "declared_at": _now(),
        "held_out": True,
        "fixtures": {"must_pass": passes_fixture, "must_fail": fails_fixture,
                     "proven": False},
    }
    cycle["facts"]["open.acceptance_declared"] = True
    cycle["facts"]["open.acceptance_held_out"] = True
    write_state(repo, state)
    return cycle["acceptance"]


def occupants(worktree: str) -> List[int]:
    """Pids with a live process whose working directory is inside `worktree`.

    S2 (Code Doctor cvsess-3b780482572e46d1): on attempt 4 the supervisor removed and recreated a
    worktree UNDER two live gen processes, then dispatched a second flight into the same branch.
    Two flights, one tree, one contract. An act that assumes an empty tree must measure that the
    tree is empty.
    """
    worktree = os.path.abspath(worktree)
    found: List[int] = []
    try:
        out = subprocess.run(["lsof", "-t", "+D", worktree], capture_output=True, text=True,
                             timeout=20)
    except Exception:  # noqa: BLE001 — an unmeasurable tree is reported, never assumed empty
        return found
    for line in (out.stdout or "").splitlines():
        line = line.strip()
        if not line.isdigit():
            continue
        pid = int(line)
        if pid != os.getpid() and pid not in found:
            found.append(pid)
    return found


def require_empty_tree(worktree: str) -> None:
    """Refuse an act that assumes nobody is working in this tree."""
    busy = occupants(worktree)
    if busy:
        raise ModeError(
            "worktree_occupied: %d live process(es) are working in %s (pids %s). A dispatch or a "
            "teardown here would put two flights in one tree, which is how attempt 4 of "
            "gpe-24500fd57f7d nearly shipped two sources of truth for one contract. End the "
            "flight first — `gpe_mode.py halt <name> --pid <pid>` measures that it ended."
            % (len(busy), worktree, ", ".join(str(p) for p in busy)))


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
    require_monitor(repo)
    require_empty_tree(worktree)
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

        # THE PLAN GATE (founder, 2026-09-09: *"voce precisa implementar tudo o que esta previsto
        # e so depois disparar a proxima tentativa, proteja a skill para que isso seja
        # assegurado"*). Law 10 already said a deliberation obliges an implementation. It said it
        # in PROSE, and the supervisor of cycle gpe-24500fd57f7d landed four of sixteen items and
        # opened the next attempt regardless — because this gate asked for ONE correction commit
        # and never for the plan. Her floor was the worst of it: six entries across two councils,
        # zero implemented, all six merely recorded.
        #
        # There is no deferral flag here on purpose. A deferral is exactly the loophole the
        # measured failure walked through, and the founder's order has no "unless".
        missing = unlanded(attempts[-1], cycle)
        if missing:
            raise ModeError(
                "plan_not_landed: attempt %d's council prescribed %d item(s) that have not landed "
                "— %s. Implement them, test them, land them on main and redeploy; record each with "
                "`gpe_mode.py landed --item <id> --commit <sha>`. A deliberation whose "
                "prescriptions did not land bought nothing."
                % (attempts[-1].get("n", len(attempts)), len(missing), ", ".join(missing)))
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


def plan_items(attempt: Dict[str, Any]) -> List[Dict[str, str]]:
    """Every item the previous council OBLIGED: its prescriptions and her backlog, as one list.

    Her three areas are not a lower class of item. On cycle gpe-24500fd57f7d both councils
    returned her floor and not one of the six entries became code, because the mode had a word for
    recording them and none for landing them.
    """
    doctor = attempt.get("doctor") or {}
    items: List[Dict[str, str]] = []
    for p in doctor.get("prescriptions") or []:
        ident = str(p.get("id") or p.get("target") or "").strip()
        if ident:
            items.append({"id": ident, "kind": "prescription", "target": str(p.get("target") or "")})
    for b in doctor.get("lucens_backlog") or []:
        ident = str(b.get("id") or b.get("title") or "").strip()
        if ident:
            items.append({"id": ident, "kind": "lucens_backlog", "area": str(b.get("area") or "")})
    return items


def finding_id(entry: Dict[str, Any]) -> str:
    """The id of a finding, derived from its text when it has none.

    Findings recorded before v2.9.0 carry no id, and an item the gate cannot name is an item the
    gate cannot enforce — three of gen's five findings about the supervisor were in exactly that
    state, unenforceable because they arrived early. The id is derived, never invented: the same
    text always yields the same id, so a landing recorded against it stays valid.
    """
    if entry.get("id"):
        return str(entry["id"])
    return "finding-%s" % hashlib.sha256(str(entry.get("text") or "").encode()).hexdigest()[:8]


def unlanded(attempt: Dict[str, Any], cycle: Optional[Dict[str, Any]] = None) -> List[str]:
    """The ids of the previous council's plan — and of the subject's findings about the supervisor
    — that carry no landing.

    S3 (Code Doctor cvsess-3b780482572e46d1): across two attempts gen audited the supervisor four
    times and was right four times, including an occupancy the supervisor could not see. The
    findings lane recorded them and nothing acted. A lane that records and never answers is a
    suggestion box, and a subject that is never answered stops reporting — which would cost this
    mode its most reliable auditor.
    """
    landed = (attempt.get("landings") or {})
    out = [i["id"] for i in plan_items(attempt) if i["id"] not in landed]
    for f in (cycle or {}).get("findings") or []:
        if f.get("about") != "supervisor":
            continue
        fid = finding_id(f)
        if fid not in landed and not f.get("landed"):
            out.append(fid)
    return out


def cmd_landed(repo: str, item_id: str, commit: str, note: str = "") -> Dict[str, Any]:
    """Record that ONE item of the council's plan landed as code, with the commit that carries it.

    Founder, 2026-09-09: *"voce precisa implementar tudo o que esta previsto e so depois disparar a
    proxima tentativa"*. The mode already said a deliberation obliges an implementation (law 10) —
    in prose, and prose does not generalize itself. Measured on cycle gpe-24500fd57f7d: sixteen
    items across two councils, four landed, and the supervisor opened the next attempt anyway,
    because `attempt` only ever asked for ONE correction commit. This is the ledger that gate reads.
    """
    state = read_state(repo)
    require_armed(state)
    attempt = current_attempt(current_cycle(state))
    known = {i["id"] for i in plan_items(attempt)}
    known |= {finding_id(f) for f in (current_cycle(state).get("findings") or [])
              if f.get("about") == "supervisor"}
    if not known:
        raise ModeError("no_plan_to_land: this attempt has no council plan recorded yet")
    if item_id not in known:
        raise ModeError("unknown_plan_item: %r is not in this attempt's plan (%s)"
                        % (item_id, ", ".join(sorted(known))))
    if not str(commit).strip():
        raise ModeError("landing_without_commit: a landed item names the commit that carries it")
    landings = attempt.setdefault("landings", {})
    landings[item_id] = {"commit": commit, "note": note, "landed_at": _now()}
    write_state(repo, state)
    return {"item": item_id, "commit": commit, "remaining": unlanded(attempt)}


def cmd_monitor(repo: str, action: str, record: str = "", pid: str = "") -> Dict[str, Any]:
    """Start the minute monitor, or report whether it is beating.

    `start` launches `gpe_tick.py --every 60` detached, so the watch outlives the command that
    started it. The supervisor is not trusted to remember: the rite refuses to advance without it.
    """
    if action == "status":
        age = heartbeat_age(repo)
        return {"running": age is not None and age <= HEARTBEAT_STALE_SECONDS,
                "last_beat_seconds_ago": None if age is None else int(age),
                "stale_after_seconds": HEARTBEAT_STALE_SECONDS}
    here = os.path.dirname(os.path.abspath(__file__))
    argv = [sys.executable, os.path.join(here, "gpe_tick.py"), "--repo", os.path.abspath(repo),
            "--every", "60"]
    if record:
        argv += ["--record", record]
    # The pid is what lets the tick see a LIVE FLIGHT. Without it `alive()` is always false, so a
    # perfectly healthy dispatch reads as `flow_not_running` and, a minute later, as
    # `supervisor_inert` — the inertia alarm firing at a supervisor who is doing exactly what it
    # should. Measured on attempt 4 of cycle gpe-24500fd57f7d, with gen 335 records into a good
    # flight. An alarm that cannot tell working from stopped is the alarm it was built to replace.
    if pid:
        argv += ["--pid", str(pid)]
    log_dir = os.path.join(repo, ".risegen", "gpe-mode", "monitor")
    os.makedirs(log_dir, exist_ok=True)
    log = open(os.path.join(log_dir, "tick.log"), "a")
    proc = subprocess.Popen(argv, stdout=log, stderr=log, start_new_session=True)
    return {"started": True, "pid": proc.pid, "every_seconds": 60,
            "log": os.path.join(log_dir, "tick.log")}


def cmd_fixtures_proven(repo: str) -> Dict[str, Any]:
    """Record that the acceptance was run against BOTH fixtures and behaved: passed the good one,
    failed the bad one. Only the supervisor can assert this, and only after running them."""
    state = read_state(repo)
    require_armed(state)
    cycle = current_cycle(state)
    acc = cycle.get("acceptance") or {}
    if not acc.get("fixtures"):
        raise ModeError("acceptance_without_fixtures")
    acc["fixtures"]["proven"] = True
    acc["fixtures"]["proven_at"] = _now()
    write_state(repo, state)
    return acc["fixtures"]


def cmd_finding(repo: str, about: str, text: str, found_by: str = "gen") -> Dict[str, Any]:
    """Record a defect found in one party's surface BY ANOTHER.

    R5 (Code Doctor cvsess-32e38638bcbe40d7). On attempt 3 the SUBJECT audited the SUPERVISOR: gen
    found that the entity resolver refused AACP from inside a worktree — the only shape the mode
    ever runs in — and that `gen entities resolve ACP` collided with risegen-aacp. It documented
    the second rather than tripping over it. Both reached the supervisor only because a human read
    the transcript, and the mode had no channel for them.

    A subject that audits its supervisor and is never answered stops reporting. The findings lane
    is that answer: the Code Doctor reads these as first-class input, not as anecdote.
    """
    state = read_state(repo)
    require_armed(state)
    if about not in ("supervisor", "gen"):
        raise ModeError("finding_about_unknown: %r (want supervisor or gen)" % about)
    if not str(text).strip():
        raise ModeError("finding_without_text")
    cycle = current_cycle(state)
    findings = cycle.setdefault("findings", [])
    entry = {"about": about, "found_by": found_by, "text": text, "at": _now(),
             "id": "finding-%s" % hashlib.sha256(text.encode()).hexdigest()[:8],
             "landed": None}
    findings.append(entry)
    write_state(repo, state)
    return entry


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


def process_group_of(pid: int) -> Optional[int]:
    """The process GROUP a pid belongs to, or None when it is already gone."""
    try:
        return os.getpgid(int(pid))
    except (OSError, ValueError, TypeError):
        return None


def end_flight(pid: Optional[int], wait_seconds: float = 3.0) -> Dict[str, Any]:
    """End a flight and MEASURE that it ended. Signals the process GROUP, waits, escalates, and
    reports the survivors it can still see.

    S1 (Code Doctor cvsess-3b780482572e46d1). On attempt 4 of cycle gpe-24500fd57f7d the
    supervisor signalled the PARENT PID and recorded the halt. Children 9769 and 9771 survived,
    kept working, and the supervisor then removed and recreated the worktree under them and
    dispatched a SECOND flight into the same tree and branch. gen detected the occupancy itself
    and yielded, which is the only reason the cycle did not ship two sources of truth for one
    contract.

    Killing a parent is not ending a flight. Typing `kill` is asserting a fact — the work is over
    — that the typist has not measured. So the state machine does it, and swears what it saw.
    """
    result: Dict[str, Any] = {"pid": pid, "pgid": None, "signalled": False,
                              "survivors": [], "ended": True}
    if not pid:
        return result
    pgid = process_group_of(pid)
    result["pgid"] = pgid
    for sig in (signal.SIGTERM, signal.SIGKILL):
        target_alive = process_group_of(pid) is not None
        if not target_alive:
            break
        try:
            if pgid is not None:
                os.killpg(pgid, sig)
            else:
                os.kill(int(pid), sig)
            result["signalled"] = True
        except (OSError, ValueError, TypeError):
            pass
        deadline = time.time() + wait_seconds
        while time.time() < deadline and process_group_of(pid) is not None:
            time.sleep(0.1)
    if process_group_of(pid) is not None:
        result["survivors"] = [int(pid)]
        result["ended"] = False
    return result


def cmd_halt(repo: str, name: str, detail: str = "", pid: Optional[int] = None) -> Dict[str, Any]:
    """Name a halt — and, when a pid is given, END THE FLIGHT and record what was measured.

    Stopping means the in-flight work is over, not that a flag was set (founder, 2026-05-09). The
    mode used to take the assistant's word for that; on attempt 4 of gpe-24500fd57f7d the word was
    wrong and two flights shared a worktree. A halt that could not end its flight refuses to be
    recorded as a halt: `halt_did_not_end_the_flight`.
    """
    if name not in HALTS:
        raise ModeError("unknown_halt: %s" % name)
    state = read_state(repo)
    require_armed(state)
    attempt = current_attempt(current_cycle(state))
    ended = None
    if pid:
        ended = end_flight(pid)
        if not ended["ended"]:
            raise ModeError(
                "halt_did_not_end_the_flight: pid %s survived SIGTERM and SIGKILL to its process "
                "group %s. The flight is NOT over and must not be recorded as halted."
                % (pid, ended["pgid"]))
    attempt["halt"] = None if name == "none" else name
    attempt.setdefault("facts", {})["supervise.halt"] = name
    if detail:
        attempt["halt_detail"] = detail
    if ended is not None:
        attempt["halt_interruption"] = ended
    write_state(repo, state)
    return {"halt": name, "detail": detail, "interruption": ended}


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
    sub.add_parser("model")
    p = sub.add_parser("landed")
    p.add_argument("--item", required=True, help="the plan item id (a prescription id or a backlog title)")
    p.add_argument("--commit", required=True, help="the commit that carries it")
    p.add_argument("--note", default="", help="what landed, in one line")
    sub.add_parser("disarm")
    sub.add_parser("status").add_argument("--json", action="store_true")
    p = sub.add_parser("open"); p.add_argument("--request", required=True)
    p = sub.add_parser("acceptance"); p.add_argument("--command", required=True)
    p.add_argument("--passes-fixture", default="", help="the case this acceptance MUST pass")
    p.add_argument("--fails-fixture", default="", help="the case this acceptance MUST fail")
    p.add_argument("--base", default="", help="the ref this acceptance judges against")
    sub.add_parser("fixtures-proven")
    p = sub.add_parser("monitor")
    p.add_argument("action", choices=["start", "status"])
    p.add_argument("--record", default="", help="gen's own record, when a flight is in the air")
    p.add_argument("--pid", default="", help="the dispatched gen process, so the tick can see the flight")
    p = sub.add_parser("finding")
    p.add_argument("--about", required=True, choices=["supervisor", "gen"])
    p.add_argument("--text", required=True)
    p.add_argument("--found-by", default="gen")
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
    p.add_argument("--pid", type=int, default=None,
                   help="the flight to END — the state machine signals its process GROUP and "
                        "verifies nothing survived")
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
        elif args.cmd == "monitor":
            out = cmd_monitor(repo, args.action, args.record, args.pid)
        elif args.cmd == "fixtures-proven":
            out = cmd_fixtures_proven(repo)
        elif args.cmd == "finding":
            out = cmd_finding(repo, args.about, args.text, args.found_by)
        elif args.cmd == "landed":
            out = cmd_landed(repo, args.item, args.commit, args.note)
        elif args.cmd == "model":
            print(GEN_MODEL)
            return 0
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
            out = cmd_acceptance(repo, args.command, args.passes_fixture, args.fails_fixture,
                                 args.base)
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
            out = cmd_halt(repo, args.name, args.detail, args.pid)
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
