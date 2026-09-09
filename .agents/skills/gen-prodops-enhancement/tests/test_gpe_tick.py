"""Paired tests for the minute tick — the mechanism the founder ordered on 2026-09-09.

> "incluir na skill que tem que ter um mecanismo de monitoramento a cada um minuto pra garantir
> que o fluxo esta rodando ate concluir"

Each test names the law it guards, and every law traces to something that actually broke on cycle
`gpe-8a711f9ba13b`. They run without a process, without a network and without a clock.
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import gpe_tick  # noqa: E402


BASE = dict(
    armed=True,
    outcome=None,
    flow_running=True,
    records=18,
    frozen_seconds=3,
    surface_written_after_dispatch=False,
    flow_silent_seconds=0,
    halt=None,
    breaches=None,
)


def ev(**over):
    return gpe_tick.evaluate(**{**BASE, **over})


# --- Law 1: a disagreement never ends the watch -------------------------------------------------
# The measured defect: the ad-hoc watch broke its loop on tick 1, and gen ran unsupervised until it
# died on its own. Every disagreement below must be REPORTED and still leave the watch running.

def test_a_stall_is_reported_and_the_watch_keeps_ticking():
    t = ev(frozen_seconds=gpe_tick.STALL_SECONDS + 1)
    assert any("gen_stalled" in d for d in t["disagreements"])
    assert t["concluded"] is False


def test_a_dead_flow_is_reported_and_the_watch_keeps_ticking():
    t = ev(flow_running=False)
    assert any("flow_not_running" in d for d in t["disagreements"])
    assert t["concluded"] is False


def test_tampering_is_reported_and_the_watch_keeps_ticking():
    t = ev(surface_written_after_dispatch=True)
    assert any("audit_tampering_detected" in d for d in t["disagreements"])
    assert t["concluded"] is False


def test_no_disagreement_whatsoever_ends_the_watch():
    for d in (
        dict(flow_running=False),
        dict(frozen_seconds=gpe_tick.STALL_SECONDS + 1),
        dict(surface_written_after_dispatch=True),
    ):
        assert ev(**d)["concluded"] is False, d


# --- "ate concluir": only a conclusion ends it --------------------------------------------------

def test_only_a_measured_conclusion_ends_the_watch():
    assert ev(outcome="fulfilled")["concluded"] is True
    assert ev(outcome="new_attempt")["concluded"] is False
    assert ev(outcome=None)["concluded"] is False


def test_disarming_ends_the_watch():
    assert ev(armed=False)["concluded"] is True


# --- Law 2: measure the act, not the mention ----------------------------------------------------
# The measured defect: the watch grepped the session record for the supervision path and matched
# the BRIEF, which names that path in order to forbid it.

def test_tampering_comes_only_from_a_write_never_from_text(tmp_path):
    repo = tmp_path / "repo"
    surface = repo / ".risegen" / "gpe-mode"
    surface.mkdir(parents=True)
    (surface / "state.json").write_text(json.dumps({"armed": True, "cycles": []}))

    # A record that TALKS about the surface, exactly as a brief does.
    record = repo / "record.jsonl"
    record.write_text(json.dumps({
        "type": "user",
        "text": "Do NOT read or write .risegen/gpe-mode/ — that is the supervision surface.",
    }) + "\n")

    dispatch_at = gpe_tick.surface_mtime(str(repo)) + 1  # nothing written since dispatch
    t = gpe_tick.tick(str(repo), record=str(record), pid=None, dispatch_at=dispatch_at)
    assert not any("audit_tampering_detected" in d for d in t["disagreements"])


def test_a_real_write_to_the_surface_is_caught(tmp_path):
    repo = tmp_path / "repo"
    surface = repo / ".risegen" / "gpe-mode"
    surface.mkdir(parents=True)
    (surface / "state.json").write_text(json.dumps({"armed": True, "cycles": []}))

    dispatch_at = gpe_tick.surface_mtime(str(repo)) - 1  # the surface moved after dispatch
    t = gpe_tick.tick(str(repo), record=None, pid=None, dispatch_at=dispatch_at)
    assert any("audit_tampering_detected" in d for d in t["disagreements"])


# --- the founder's interval ---------------------------------------------------------------------

def test_the_default_interval_is_the_founders_minute():
    assert gpe_tick.DEFAULT_INTERVAL == 60


def test_a_single_tick_reports_without_looping(tmp_path, capsys):
    repo = tmp_path / "repo"
    (repo / ".risegen" / "gpe-mode").mkdir(parents=True)
    (repo / ".risegen" / "gpe-mode" / "state.json").write_text(
        json.dumps({"armed": True, "cycles": [{"outcome": None}]}))
    rc = gpe_tick.main(["--repo", str(repo)])  # no --every: one tick, then return
    out = capsys.readouterr().out
    assert out.startswith("TICK ")
    assert rc == 1  # the flow is not running and not concluded — a named disagreement


# --- Law 3: the supervisor does not stop ---------------------------------------------------------
# The measured correction: the supervisor finished a failed attempt, wrote a report and stopped to
# ask the founder what to do next. "voce nao pode parar … ate ter sucesso" — founder, 2026-09-09.

def test_a_silent_flow_with_the_request_unfulfilled_is_a_stopped_supervisor():
    t = ev(flow_silent_seconds=gpe_tick.FLOW_STALL_SECONDS + 1)
    assert any("supervisor_stopped" in d for d in t["disagreements"])


def test_a_stopped_supervisor_does_not_end_the_watch_either():
    t = ev(flow_silent_seconds=gpe_tick.FLOW_STALL_SECONDS + 1)
    assert t["concluded"] is False


def test_a_flow_that_is_still_advancing_is_not_called_stopped():
    t = ev(flow_silent_seconds=gpe_tick.FLOW_STALL_SECONDS - 1)
    assert not any("supervisor_stopped" in d for d in t["disagreements"])


def test_a_fulfilled_request_is_never_a_stopped_supervisor():
    # Success is the one silence that is allowed.
    t = ev(outcome="fulfilled", flow_silent_seconds=10 * gpe_tick.FLOW_STALL_SECONDS)
    assert t["disagreements"] == []
    assert t["concluded"] is True


def test_the_flow_heartbeat_comes_from_the_mode_state_file(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".risegen" / "gpe-mode").mkdir(parents=True)
    (repo / ".risegen" / "gpe-mode" / "state.json").write_text(
        json.dumps({"armed": True, "cycles": [{"outcome": "new_attempt"}]}))
    # Just written, so the flow is not silent — no supervisor_stopped.
    t = gpe_tick.tick(str(repo))
    assert not any("supervisor_stopped" in d for d in t["disagreements"])

    # Backdate the state file past the threshold: the same reading now names the stop.
    old = time.time() - (gpe_tick.FLOW_STALL_SECONDS + 60)
    os.utime(repo / ".risegen" / "gpe-mode" / "state.json", (old, old))
    t = gpe_tick.tick(str(repo))
    assert any("supervisor_stopped" in d for d in t["disagreements"])
    assert t["concluded"] is False


# --- A named founder dependency is not a defect in the flow ---------------------------------------
# Measured on cycle gpe-8a711f9ba13b: the cycle reached the one thing only the founder could do —
# a tap on a device — and the tick spent twenty minutes crying flow_not_running at it. An alarm
# that cannot tell "waiting on the founder" from "the supervisor stopped" becomes noise, and that
# is how a real alarm gets ignored.

def test_a_founder_halt_is_named_not_called_a_dead_flow():
    t = ev(flow_running=False, halt=gpe_tick.FOUNDER_HALT)
    assert "awaiting_founder" in t["line"]
    assert not any("flow_not_running" in d for d in t["disagreements"])


def test_a_founder_halt_still_does_not_end_the_watch():
    # Law 1 holds here too: only a measured conclusion ends it.
    assert ev(flow_running=False, halt=gpe_tick.FOUNDER_HALT)["concluded"] is False


def test_a_founder_halt_is_not_a_stopped_supervisor():
    t = ev(flow_running=False, halt=gpe_tick.FOUNDER_HALT,
           flow_silent_seconds=gpe_tick.FLOW_STALL_SECONDS * 3)
    assert not any("supervisor_stopped" in d for d in t["disagreements"])


def test_any_other_halt_is_still_a_disagreement():
    # Only the founder halt is exempt; a stagnation is still the flow's problem.
    t = ev(flow_running=False, halt="gen_loop_detected")
    assert any("flow_not_running" in d for d in t["disagreements"])


def test_the_halt_is_read_from_the_latest_attempt(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".risegen" / "gpe-mode").mkdir(parents=True)
    (repo / ".risegen" / "gpe-mode" / "state.json").write_text(json.dumps({
        "armed": True,
        # The councils and lineage keep this cycle out of breach, so the test isolates the one
        # property it guards: the halt is read from the LATEST attempt, not the first.
        "cycles": [{"outcome": "new_attempt", "attempts": [
            {"n": 1, "halt": "gen_loop_detected", "council": {"session_id": "cvsess-a"}},
            {"n": 2, "halt": "gen_asked_user", "council": {"session_id": "cvsess-b"},
             "correction": {"commit": "aaa1111", "redeployed": True, "backlog_ref": "#2900"}},
        ]}],
    }))
    assert "awaiting_founder" in gpe_tick.tick(str(repo))["line"]


# --- M4 in the tick: a breach is named on the minute, not at the close ----------------------------
# Ambition critic, cvsess-63124fd46e3b4c68: a report that exists only at the close would have been
# written after the EIGHTH attempt of gpe-8a711f9ba13b. The tick already reads state.json every
# minute, so the breach is named while it can still change behaviour.

def test_a_cycle_in_breach_is_named_on_the_tick():
    t = ev(breaches=["no_council", "no_new_correction"])
    assert any("cycle_in_breach" in d for d in t["disagreements"])
    assert "no_new_correction" in t["line"]


def test_a_breach_does_not_end_the_watch_either():
    assert ev(breaches=["no_council"])["concluded"] is False


def test_a_breach_outranks_the_founder_wait():
    # Waiting on the founder is not a defect, but a flow in breach is — and the breach must not be
    # hidden behind the wait, which is exactly how eight iterations went unnoticed.
    t = ev(flow_running=False, halt=gpe_tick.FOUNDER_HALT, breaches=["no_council"])
    assert any("cycle_in_breach" in d for d in t["disagreements"])


def test_a_clean_cycle_raises_no_breach():
    assert not any("cycle_in_breach" in d for d in ev(breaches=[])["disagreements"])


def test_the_tick_reads_breaches_the_same_way_verify_does(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".risegen" / "gpe-mode").mkdir(parents=True)
    (repo / ".risegen" / "gpe-mode" / "state.json").write_text(json.dumps({
        "armed": True,
        "cycles": [{"id": "c", "attempts": [
            {"n": 1, "cause": "a"},
            {"n": 2, "cause": "b", "correction": {"commit": "d0a39d3", "redeployed": True}},
            {"n": 3, "cause": "c", "correction": {"commit": "d0a39d3", "redeployed": True}},
        ]}],
    }))
    line = gpe_tick.tick(str(repo))["line"]
    assert "cycle_in_breach" in line
    assert "no_new_correction" in line


def test_a_cycle_that_closed_fulfilled_in_breach_does_not_pass_silently():
    # G3: success masks process failure. gpe-8a711f9ba13b closed fulfilled with all eight
    # iterations in breach; a watch that goes quiet on the result lets that repeat.
    t = ev(outcome="fulfilled", breaches=["no_council", "no_new_correction"])
    assert t["concluded"] is True            # the work IS done
    assert "cycle_closed_in_breach" in t["line"]   # ...and how it got there is still named


def test_a_clean_fulfilled_cycle_ends_quietly():
    t = ev(outcome="fulfilled", breaches=[])
    assert t["concluded"] is True
    assert t["disagreements"] == []
    assert "OUT_OF_ACCORD" not in t["line"]
