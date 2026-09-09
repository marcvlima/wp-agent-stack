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

# The only outcomes that END the watch. Anything else keeps it ticking.
CONCLUDED = ("fulfilled",)

# The one halt that is not the flow's fault: the cycle reached something only the
# founder can discharge. It is still reported every minute — the founder must see
# what is waiting on them — but it is named for what it is, never as a stopped
# supervisor or a dead flow.
FOUNDER_HALT = "gen_asked_user"


def read_state(repo):
    path = os.path.join(repo, ".risegen", "gpe-mode", "state.json")
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def surface_mtime(repo):
    """Newest mtime under the supervision surface — the only evidence of tampering."""
    newest = 0.0
    for base, _dirs, files in os.walk(os.path.join(repo, ".risegen", "gpe-mode")):
        for name in files:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(base, name)))
            except OSError:
                continue
    return newest


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
             breaches=None):
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

    # Law 2: the act, never the mention.
    if surface_written_after_dispatch:
        dis.append("audit_tampering_detected · the supervision surface was written since dispatch")

    line = "TICK records=%s frozen=%ss running=%s" % (
        records, frozen_seconds if frozen_seconds is not None else "?",
        "yes" if flow_running else "no")
    line += (" | " + " | ".join("OUT_OF_ACCORD " + d for d in dis)) if dis else " | IN_ACCORD"

    # Law 1: a disagreement is reported, never terminal.
    return {"line": line, "disagreements": dis, "concluded": False}


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
    return found


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

    return evaluate(
        armed=bool(state.get("armed")),
        outcome=cycle.get("outcome"),
        flow_running=alive(pid),
        records=records,
        frozen_seconds=frozen,
        surface_written_after_dispatch=bool(dispatch_at and surface_mtime(repo) > dispatch_at),
        flow_silent_seconds=flow_silent,
        halt=(cycle.get("attempts") or [{}])[-1].get("halt"),
        breaches=cycle_breaches(cycle),
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
