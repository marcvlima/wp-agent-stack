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


# --- The model pin: the flight runs on the model the mode pins ----------------------------------
# Founder, 2026-09-09: "e pra manter esse mesmo inclusive pode atualizar a skill para que ele
# sempre rode neste modelo durante este modo". Measured on cycle gpe-24500fd57f7d, where the
# dispatch inherited the environment's model and the same binary had announced a fallback to a
# different one minutes earlier.

def test_a_flight_off_the_pin_is_a_disagreement():
    out = ev(record_model="qwen3.8-max")
    assert any(d.startswith("model_off_pin") for d in out["disagreements"]), out["line"]
    assert "qwen3.8-max" in out["line"] and gpe_tick.PINNED_MODEL in out["line"]
    assert out["concluded"] is False  # law 1: reported, never terminal


def test_a_flight_on_the_pin_agrees():
    assert ev(record_model=gpe_tick.PINNED_MODEL)["disagreements"] == []


def test_an_unmeasured_model_is_not_read_as_agreement_or_as_a_breach():
    """None is 'not measured', which is never a reading — and never a silent pass either."""
    assert ev(record_model=None)["disagreements"] == []
    assert gpe_tick.record_model(None) is None
    assert gpe_tick.record_model("/nonexistent/record.jsonl") is None


def test_the_model_is_read_from_gens_own_record_newest_last(tmp_path):
    rec = tmp_path / "session.jsonl"
    rec.write_text(
        json.dumps({"type": "user", "message": {}}) + "\n"
        + json.dumps({"type": "assistant", "model": "qwen3.8-flash"}) + "\n"
        + "{not json}\n"
        + json.dumps({"type": "assistant", "model": "qwen3.8-max"}) + "\n")
    assert gpe_tick.record_model(str(rec)) == "qwen3.8-max"


def test_the_pin_is_the_one_the_state_machine_publishes():
    """Two literals that must never drift apart: the tick judges what the dispatch is given."""
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))
    import gpe_mode
    assert gpe_tick.PINNED_MODEL == gpe_mode.GEN_MODEL


# --- P7 / cycle gpe-24500fd57f7d: the alarm names the act of SOMETHING ELSE ----------------------
# The contract REQUIRES the supervisor to record supervise.* and judge.* after the dispatch, so
# "the surface was written since dispatch" fired on every honest cycle. An alarm that is always on
# is an alarm nobody reads.

def _surface(tmp_path, state):
    d = tmp_path / ".risegen" / "gpe-mode"
    d.mkdir(parents=True, exist_ok=True)
    (d / "state.json").write_text(json.dumps(state))
    return str(tmp_path)


def test_the_supervisors_own_mandated_write_is_not_tampering(tmp_path):
    repo = _surface(tmp_path, {"armed": True, "state_machine_wrote_at": time.time()})
    assert gpe_tick.foreign_write(repo, dispatch_at=time.time() - 60) is False


def test_a_write_the_state_machine_did_not_make_is_tampering(tmp_path):
    """The stamp is old; the file is newer — something else wrote the surface."""
    repo = _surface(tmp_path, {"armed": True, "state_machine_wrote_at": time.time() - 3600})
    assert gpe_tick.foreign_write(repo, dispatch_at=time.time() - 60) is True


def test_a_surface_untouched_since_the_dispatch_is_never_tampering(tmp_path):
    repo = _surface(tmp_path, {"armed": True, "state_machine_wrote_at": time.time()})
    assert gpe_tick.foreign_write(repo, dispatch_at=time.time() + 3600) is False


def test_a_state_file_with_no_stamp_falls_back_to_the_old_reading_not_to_a_pass(tmp_path):
    """Silence about provenance is never a pass — an unstamped state reads as foreign."""
    repo = _surface(tmp_path, {"armed": True})
    assert gpe_tick.foreign_write(repo, dispatch_at=time.time() - 60) is True


def test_no_dispatch_means_nothing_to_compare(tmp_path):
    repo = _surface(tmp_path, {"armed": True})
    assert gpe_tick.foreign_write(repo, dispatch_at=None) is False


# --- The plan gate, seen from the minute tick ---------------------------------------------------

def test_the_tick_names_a_plan_that_has_not_landed():
    cycle = {"attempts": [{"n": 1, "doctor": {
        "prescriptions": [{"id": "P1", "target": "gen:x"}],
        "lucens_backlog": [{"area": "logic", "title": "T-logic"}]}, "landings": {}}]}
    assert gpe_tick.unlanded_plan(cycle) == ["P1", "T-logic"]


def test_the_tick_is_quiet_once_every_item_landed():
    cycle = {"attempts": [{"n": 1, "doctor": {
        "prescriptions": [{"id": "P1", "target": "gen:x"}],
        "lucens_backlog": [{"area": "logic", "title": "T-logic"}]},
        "landings": {"P1": {"commit": "a"}, "T-logic": {"commit": "b"}}}]}
    assert gpe_tick.unlanded_plan(cycle) == []


def test_a_cycle_with_no_council_yet_has_no_unlanded_plan():
    assert gpe_tick.unlanded_plan({"attempts": [{"n": 1}]}) == []
    assert gpe_tick.unlanded_plan({}) == []


# --- Inertia: watching or working, never idle ---------------------------------------------------
# Founder, 2026-09-09: "voce nao pode ficar parado, ou está monitorando ou está atuando no que é
# responsabilidade sua … tem que ter um monitor pra impedir a inercia a cada um minuto".

def test_no_flight_and_no_movement_is_inertia_on_the_minute():
    out = ev(flow_running=False, flow_silent_seconds=gpe_tick.INERTIA_SECONDS)
    assert any(d.startswith("supervisor_inert") for d in out["disagreements"]), out["line"]
    assert out["concluded"] is False  # law 1: named, never terminal


def test_a_running_flight_is_never_inertia_however_quiet_the_supervisor_is():
    """While gen flies, WATCHING is the work. The supervisor's own silence is expected."""
    out = ev(flow_running=True, flow_silent_seconds=600)
    assert not any(d.startswith("supervisor_inert") for d in out["disagreements"])


def test_a_supervisor_that_is_working_is_not_inert():
    """Its work leaves marks on the surface; a fresh mark is the evidence of working."""
    out = ev(flow_running=False, flow_silent_seconds=5)
    assert not any(d.startswith("supervisor_inert") for d in out["disagreements"])


def test_past_the_long_horizon_the_harder_name_takes_over():
    """Inertia is the minute-scale reading; supervisor_stopped is the quarter-hour one. A tick
    must not shout both at once about the same silence."""
    out = ev(flow_running=False, flow_silent_seconds=gpe_tick.FLOW_STALL_SECONDS)
    names = [d.split(" ")[0] for d in out["disagreements"]]
    assert "supervisor_stopped" in names
    assert "supervisor_inert" not in names


def test_an_unmeasured_silence_is_not_inertia():
    """None is 'not measured', which is never a reading — the rule this cycle learned three times."""
    out = ev(flow_running=False, flow_silent_seconds=None)
    assert not any(d.startswith("supervisor_inert") for d in out["disagreements"])


# --- The monitor proves it is running, every minute ---------------------------------------------

def test_every_tick_writes_a_heartbeat(tmp_path):
    (tmp_path / ".risegen" / "gpe-mode").mkdir(parents=True)
    (tmp_path / ".risegen" / "gpe-mode" / "state.json").write_text(json.dumps({"armed": True}))
    gpe_tick.tick(str(tmp_path))
    beat = json.loads((tmp_path / gpe_tick.HEARTBEAT_REL).read_text())
    assert time.time() - beat["at"] < 5
    assert beat["interval"] == gpe_tick.DEFAULT_INTERVAL


def test_the_heartbeat_is_not_read_as_tampering_with_the_surface(tmp_path):
    """The watch proving it is alive must not trip the alarm that watches the surface — otherwise
    the minute monitor and the tampering alarm cannot both be on."""
    d = tmp_path / ".risegen" / "gpe-mode"
    d.mkdir(parents=True)
    (d / "state.json").write_text(json.dumps({"armed": True, "state_machine_wrote_at": time.time()}))
    dispatch_at = time.time() - 30
    gpe_tick.beat(str(tmp_path))
    assert gpe_tick.foreign_write(str(tmp_path), dispatch_at) is False


def test_a_heartbeat_that_cannot_be_written_never_kills_the_watch(tmp_path):
    """A watch that dies trying to say it is alive is worse than one that says nothing."""
    (tmp_path / ".risegen" / "gpe-mode").mkdir(parents=True)
    (tmp_path / ".risegen" / "gpe-mode" / "state.json").write_text(json.dumps({"armed": True}))
    (tmp_path / ".risegen" / "gpe-mode" / "monitor").write_text("a file where a directory goes")
    out = gpe_tick.tick(str(tmp_path))  # must not raise
    assert "line" in out
