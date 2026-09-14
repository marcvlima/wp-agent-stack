"""One tick per minute, until the request succeeds.

> "incluir na skill que tem que ter um mecanismo de monitoramento a cada um minuto pra garantir
> que o fluxo esta rodando ate concluir" — founder, 2026-09-09
> "voce nao pode parar, e tem que tem um monitoramento a cada um minuto para garantir que o fluxo
> esta funcionando ate ter sucesso." — founder, 2026-09-09, correcting a supervisor that stopped

The founder's rule has three parts and this module is all three: **a cada um minuto** (the default
interval, and the CLI's own loop), **garantir que o fluxo esta rodando** (every tick MEASURES the
flow instead of assuming it), and **ate concluir** (the loop ends on a measured conclusion and on
nothing else).

It exists because of a measured failure on cycle `gpe-8a711f9ba13b` (2026-09-09). A supervisor's
ad-hoc watch named `audit_tampering_detected` by grepping the whole session record for the
supervision path — and matched the BRIEF, which names that path in order to FORBID it. The watch
then broke its own loop on that first tick, and gen ran unsupervised until it died on its own.
Three laws, all tested. The third arrived by correction: the supervisor reached the end of a
failed attempt, wrote a report and STOPPED to ask the founder what to do next. The founder named
that the defect — the retry is unbounded and a stop is a failure of the flow, so the mechanism
that watches the flow must be able to see the supervisor's own silence.

1. **A disagreement never ends the watch.** A tick that finds something wrong reports
   `OUT_OF_ACCORD` and ticks again. Only a conclusion ends it. A watch that stops at its first
   suspicion is the silence-read-as-a-pass this mode exists to forbid.
2. **Measure the act, not the mention.** Tampering is a WRITE into the supervision surface, read
   from that surface's own mtime — never the appearance of its name in text an actor merely read.
3. **The supervisor does not stop.** A flow silent past `FLOW_STALL_SECONDS` with the request
   unfulfilled is `supervisor_stopped` — the same class of disagreement as a stalled subject, and
   read from the mode's own state file, which moves whenever any phase records a fact.

Standard library only. `evaluate()` is pure: it takes readings and returns one tick, so both laws
are testable without a process, a network or a clock.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

DEFAULT_INTERVAL = 60  # the founder's minute, in seconds
STALL_SECONDS = 300  # a record frozen this long, with the process alive, is gen_stalled
FLOW_STALL_SECONDS = 900  # the WHOLE flow silent this long, unfulfilled, is a stopped supervisor

#: INERTIA. Founder, 2026-09-09: *"voce nao pode ficar parado, ou esta monitorando ou esta atuando
#: no que e responsabilidade sua … tem que ter um monitor pra impedir a inercia a cada um minuto"*.
#: There are exactly two states an armed supervisor may be in: WATCHING a live flight, or WORKING
#: on what is its own. Neither one, for longer than this, is inertia — and it is named on the
#: minute, not at the 15-minute horizon `supervisor_stopped` watches, because a quarter of an hour
#: of nothing is not a lapse the founder should have to notice himself.
#:
#: Measured on cycle gpe-24500fd57f7d: between a council closing and the next landing, and again
#: between a judgement and the next dispatch, the flow sat still with no flight running and no
#: write to its own surface, and nothing said so.
INERTIA_SECONDS = 60

#: Where the tick proves IT IS RUNNING. Founder, 2026-09-09, restating the order after the first
#: cut only added the reading: *"precisa adicionar na skill pra que tenha um monitor que é ativado
#: a cada minuto para garantir que o fluxo nao pare"*. A check that exists but is not running
#: guarantees nothing, and the thing it would have caught — a supervisor standing still — is
#: exactly the state in which nobody remembers to start it. So the tick writes a heartbeat every
#: minute and the state machine REFUSES to move the cycle when that heartbeat is stale.
#:
#: It lives in its own subdirectory so that writing it is never read as tampering with the
#: supervision surface (see `surface_mtime`).
HEARTBEAT_REL = os.path.join(".risegen", "gpe-mode", "monitor", "heartbeat.json")

#: How stale a heartbeat may be before the monitor counts as absent: two ticks, so one missed
#: interval is a hiccup and two is a stopped watch.
HEARTBEAT_STALE_SECONDS = 2 * DEFAULT_INTERVAL

# The only outcomes that END the watch. Anything else keeps it ticking.
CONCLUDED = ("fulfilled",)

# The one halt that is not the flow's fault: the cycle reached something only the
# founder can discharge. It is still reported every minute — the founder must see
# what is waiting on them — but it is named for what it is, never as a stopped
# supervisor or a dead flow.
FOUNDER_HALT = "gen_asked_user"

# The model the mode pins for gen (gpe_mode.GEN_MODEL, kept here as a literal so the tick has no
# import-time dependency on the state machine). The tick reads the model out of gen's OWN record
# and disagrees when the flight is not on the pin — the same discipline as every other reading
# here: the act, never the intention. A dispatch that MEANT to pass -m and did not looks exactly
# like a dispatch that did, until something measures the record.
PINNED_MODEL = "qwen3.8-flash"


def read_state(repo):
    path = os.path.join(repo, ".risegen", "gpe-mode", "state.json")
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


#: How far the surface's newest mtime may sit ahead of the state machine's own stamp and still
#: be that same write (the stamp is taken before the file is closed and replaced).
STATE_WRITE_TOLERANCE_SECONDS = 5


def surface_mtime(repo):
    """Newest mtime under the supervision surface — the only evidence of tampering.

    The monitor's own heartbeat subdirectory is excluded: the watch writing proof that it is alive
    is not a write into the audit surface, and reading it as one would make the minute monitor and
    the tampering alarm impossible to run at the same time.
    """
    newest = 0.0
    for base, dirs, files in os.walk(os.path.join(repo, ".risegen", "gpe-mode")):
        dirs[:] = [d for d in dirs if d != "monitor"]
        for name in files:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(base, name)))
            except OSError:
                continue
    return newest


def foreign_write(repo, dispatch_at):
    """True only when the surface was written since the dispatch by something that is NOT the
    state machine.

    `state_machine_wrote_at` is stamped by gpe_mode.write_state on every write it makes. A surface
    whose newest mtime is that same write (within a small tolerance) is the supervisor doing what
    the contract obliges it to do. A surface newer than the stamp was written by something else —
    that is the act this alarm exists for. A state file with no stamp is a state machine older than
    this rule: the reading falls back to the raw "written since dispatch" test rather than to a
    silent pass.
    """
    if not dispatch_at:
        return False
    newest = surface_mtime(repo)
    if newest <= dispatch_at:
        return False
    stamp = read_state(repo).get("state_machine_wrote_at")
    if not isinstance(stamp, (int, float)):
        return True
    return newest > stamp + STATE_WRITE_TOLERANCE_SECONDS


def alive(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError, TypeError):
        return False
    return True


def evaluate(*, armed, outcome, flow_running, records, frozen_seconds,
             surface_written_after_dispatch, flow_silent_seconds=None, halt=None,
             breaches=None, record_model=None):
    """Turn one set of readings into one tick. Pure: no I/O, no clock, no process.

    Returns `line` (what a human and a monitor both read), `disagreements` (named, never
    swallowed) and `concluded` (whether the watch may end).
    """
    if not armed:
        return {"line": "TICK disarmed", "disagreements": [], "concluded": True}

    if outcome in CONCLUDED:
        # G3 (cvsess-63124fd46e3b4c68): success masks process failure, so compliance is reported
        # separately from result. Cycle gpe-8a711f9ba13b closed `fulfilled` having run all eight
        # iterations in breach, and a watch that goes quiet on the result would let exactly that
        # pass unremarked one more time. The watch still ENDS — the work is done — but it does
        # not end silently about how the work got there.
        line = "TICK concluded outcome=%s" % outcome
        if breaches:
            line += " | OUT_OF_ACCORD cycle_closed_in_breach · %s — run gpe_report.py" % (
                ", ".join(sorted(set(breaches))))
        return {"line": line, "disagreements": list(breaches or []), "concluded": True}

    # A named founder dependency is not a defect in the flow, and calling it one every minute
    # is how a real alarm becomes noise and gets ignored. It is still reported — what waits on
    # the founder must stay visible — and the watch still does not end.
    if halt == FOUNDER_HALT and not breaches:
        return {
            "line": "TICK awaiting_founder · the cycle reached something only the founder can "
                    "discharge; everything not depending on it is done",
            "disagreements": [],
            "concluded": False,
        }

    dis = []
    # "garantir que o fluxo esta rodando" — a flow that is neither running nor concluded is the
    # disagreement this mechanism exists to catch. It is NOT a reason to stop watching.
    if not flow_running:
        dis.append("flow_not_running · gen is gone and the cycle is not fulfilled — judge or redispatch")
    elif frozen_seconds is not None and frozen_seconds >= STALL_SECONDS:
        dis.append("gen_stalled · record frozen %ss while the process lives" % frozen_seconds)

    # INERTIA, on the minute. Watching or working — there is no third state. A flight that is not
    # running is not being watched, so the only thing that can be happening is the supervisor's own
    # work, and that work leaves marks on the supervision surface. No flight and no mark is
    # standing still, and it is said every minute rather than once a quarter of an hour.
    if (not flow_running) and flow_silent_seconds is not None and \
            INERTIA_SECONDS <= flow_silent_seconds < FLOW_STALL_SECONDS:
        dis.append("supervisor_inert · no flight is running and the flow has not moved for %ss — "
                   "be watching or be working; there is no third state" % flow_silent_seconds)

    # Law 3: the supervisor does not stop. The founder set no cap and named the stop itself the
    # failure — "voce nao pode parar … ate ter sucesso" (2026-09-09). A flow that has gone silent
    # while the request is unfulfilled is a STOPPED SUPERVISOR, and that is the condition this
    # mechanism exists to make visible. Waiting on a founder answer is not an exception: everything
    # that does not depend on the answer is still owed.
    if flow_silent_seconds is not None and flow_silent_seconds >= FLOW_STALL_SECONDS:
        dis.append("supervisor_stopped · the flow has not advanced for %ss and the request is not "
                   "fulfilled — resume the cycle" % flow_silent_seconds)

    # M4 (Code Doctor cvsess-63124fd46e3b4c68, ambition critic): a report that exists only at the
    # close would have been written after the EIGHTH attempt of gpe-8a711f9ba13b — long past the
    # point where it mattered. The tick already reads the state file every minute, so a cycle in
    # breach is named HERE, while it can still change behaviour. Same argument CD-2 made inside
    # gen for the unread-brief warning: emit it before any tool runs, not only in the post-hoc
    # outcome line.
    if breaches:
        dis.append("cycle_in_breach · %s — run gpe_report.py --verify" % ", ".join(sorted(set(breaches))))

    # The model is a pin while the mode is armed, so a flight on anything else is a disagreement
    # — reported, never terminal. `None` is "not measured yet", which is not a reading.
    if record_model and record_model != PINNED_MODEL:
        dis.append("model_off_pin · gen is flying on %s, the mode pins %s" % (record_model, PINNED_MODEL))

    # Law 2: the act, never the mention — and the act of WHOM. The supervisor is REQUIRED by the
    # contract to record supervise.* and judge.* after the dispatch, so "written since dispatch" on
    # its own names every honest cycle. Tampering is a write the state machine did not make.
    if surface_written_after_dispatch:
        dis.append("audit_tampering_detected · the supervision surface was written since dispatch "
                   "by something other than the state machine")

    line = "TICK records=%s frozen=%ss running=%s" % (
        records, frozen_seconds if frozen_seconds is not None else "?",
        "yes" if flow_running else "no")
    line += (" | " + " | ".join("OUT_OF_ACCORD " + d for d in dis)) if dis else " | IN_ACCORD"

    # Law 1: a disagreement is reported, never terminal.
    return {"line": line, "disagreements": dis, "concluded": False}


def unlanded_plan(cycle):
    """Plan items of the newest council that carry no landing — a breach while it still matters.

    The tick is where a cycle in breach becomes visible on the minute rather than at the close, and
    an unlanded plan is precisely the breach that cost cycle gpe-24500fd57f7d twelve of sixteen
    items: recorded, never implemented, and the next attempt opened anyway.
    """
    attempts = (cycle or {}).get("attempts") or []
    if not attempts:
        return []
    a = attempts[-1]
    doctor = a.get("doctor") or {}
    landed = a.get("landings") or {}
    ids = []
    for p in doctor.get("prescriptions") or []:
        ident = str(p.get("id") or p.get("target") or "").strip()
        if ident and ident not in landed:
            ids.append(ident)
    for b in doctor.get("lucens_backlog") or []:
        ident = str(b.get("id") or b.get("title") or "").strip()
        if ident and ident not in landed:
            ids.append(ident)
    return ids


def cycle_breaches(cycle):
    """Every rite breach in the cycle, measured the same way gpe_report.py --verify measures it.

    Imported lazily and degrading to no reading at all rather than to a false clean: a tick that
    could not measure must never look like a tick that found nothing.
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import gpe_report
    except ImportError:
        return []
    found = []
    for row in gpe_report.audit_attempts(cycle):
        found.extend(row["breaches"])
    if unlanded_plan(cycle):
        found.append("plan_not_landed(%d)" % len(unlanded_plan(cycle)))
    return found


def record_model(record):
    """The newest model stamped in gen's own record, or None when it cannot be read.

    Never a default: an unreadable record is "not measured", and a tick that could not measure
    must not look like a tick that measured the pin and agreed.
    """
    if not record or not os.path.exists(record):
        return None
    found = None
    try:
        with open(record) as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row.get("model"), str) and row["model"]:
                    found = row["model"]
    except OSError:
        return None
    return found


def beat(repo):
    """Write the proof that the monitor ran, this minute. Never raises: a heartbeat that cannot be
    written must not kill the watch that was about to report something."""
    path = os.path.join(repo, HEARTBEAT_REL)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump({"at": time.time(), "pid": os.getpid(), "interval": DEFAULT_INTERVAL}, fh)
        os.replace(tmp, path)
    except OSError:
        pass
    return path


def tick(repo, record=None, pid=None, dispatch_at=None):
    state = read_state(repo)
    cycles = state.get("cycles") or []
    cycle = cycles[-1] if cycles else {}

    records, frozen = None, None
    if record and os.path.exists(record):
        try:
            with open(record, "rb") as fh:
                records = sum(1 for _ in fh)
            frozen = int(time.time() - os.path.getmtime(record))
        except OSError:
            pass

    # The flow's own heartbeat: the mode's state file moves whenever any phase records a fact.
    try:
        flow_silent = int(time.time() - os.path.getmtime(
            os.path.join(repo, ".risegen", "gpe-mode", "state.json")))
    except OSError:
        flow_silent = None

    beat(repo)
    return evaluate(
        armed=bool(state.get("armed")),
        outcome=cycle.get("outcome"),
        flow_running=alive(pid),
        records=records,
        frozen_seconds=frozen,
        surface_written_after_dispatch=foreign_write(repo, dispatch_at),
        flow_silent_seconds=flow_silent,
        halt=(cycle.get("attempts") or [{}])[-1].get("halt"),
        breaches=cycle_breaches(cycle),
        record_model=record_model(record),
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--record", help="gen's own JSONL record for this cycle")
    ap.add_argument("--pid", type=int, help="the dispatched gen process")
    ap.add_argument("--dispatch-at", type=float, help="epoch seconds of the dispatch")
    ap.add_argument("--every", type=int, nargs="?", const=DEFAULT_INTERVAL,
                    help="loop at this interval (default %ds — the founder's minute)"
                         % DEFAULT_INTERVAL)
    args = ap.parse_args(argv)

    while True:
        t = tick(args.repo, args.record, args.pid, args.dispatch_at)
        print(t["line"], flush=True)
        if t["concluded"] or args.every is None:
            return 0 if not t["disagreements"] else 1
        time.sleep(args.every)


if __name__ == "__main__":
    sys.exit(main())
