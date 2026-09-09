"""Paired tests for the enhancement mode's state machine and its audit.

Each test names the rule it guards. They run without a gen binary, without a network and without
a repository: the mode's laws are testable by construction, or they are not laws.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import types

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import gpe_audit  # noqa: E402
import gpe_mode  # noqa: E402

CONTRACT = os.path.join(os.path.dirname(HERE), "references", "request-contract.yaml")


def fake_gen(tmp_path, version="gen 1.2.3"):
    """A stand-in binary plus a runner that answers for it."""
    path = tmp_path / "gen"
    path.write_text("#!/bin/sh\necho %s\n" % version)
    path.chmod(0o755)

    def runner(argv, **kwargs):
        assert argv[0] == str(path) and argv[1] == "--version"
        return types.SimpleNamespace(returncode=0, stdout=version + "\n", stderr="")

    return str(path), runner


def arm(tmp_path):
    path, runner = fake_gen(tmp_path)
    return gpe_mode.cmd_arm(str(tmp_path), path, runner=runner)


# ---------------------------------------------------------------- R1: the mode is on disk

def test_arming_writes_the_state_the_assistant_rereads(tmp_path):
    arm(tmp_path)
    state = json.loads((tmp_path / ".risegen" / "gpe-mode" / "state.json").read_text())
    assert state["armed"] is True
    assert state["gen"]["version"] == "gen 1.2.3"
    assert len(state["gen"]["sha256"]) == 64


def test_arming_refuses_an_unreadable_gen(tmp_path):
    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_arm(str(tmp_path), str(tmp_path / "nowhere"))
    assert "gen_unreadable" in str(err.value)


def test_nothing_runs_before_the_mode_is_armed(tmp_path):
    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_open(str(tmp_path), "do the thing")
    assert "mode_not_armed" in str(err.value)


# ---------------------------------------------------------------- R2/R4: the request and its acceptance

def test_the_request_is_kept_verbatim(tmp_path):
    arm(tmp_path)
    words = "corrige o leitor que perdeu o assento dela"
    cycle = gpe_mode.cmd_open(str(tmp_path), words)
    assert cycle["request"] == words


def test_the_acceptance_is_held_out_and_declared_before_the_result(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    acceptance = gpe_mode.cmd_acceptance(str(tmp_path), "pytest -q tests/test_seat.py")
    assert acceptance["held_out"] is True

    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"), session_id="s1")
    gpe_mode.cmd_fact(str(tmp_path), "judge.acceptance_result", "not_fulfilled")
    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_acceptance(str(tmp_path), "pytest -q -k anything_that_passes")
    assert "acceptance_authored_after_result" in str(err.value)


def test_a_cycle_never_closes_fulfilled_on_gens_word(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"), session_id="s1")
    gpe_mode.cmd_fact(str(tmp_path), "dispatch.brief_delivered", True)
    # M2 (cvsess-63124fd46e3b4c68): every attempt carries its deliberation before any close.
    gpe_mode.cmd_doctor(str(tmp_path), "cvsess-close", backlog=[], prescriptions=[])
    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_close(str(tmp_path), "fulfilled")
    assert "close_without_acceptance" in str(err.value)

    gpe_mode.cmd_fact(str(tmp_path), "judge.acceptance_result", "fulfilled")
    assert gpe_mode.cmd_close(str(tmp_path), "fulfilled")["outcome"] == "fulfilled"


# ---------------------------------------------------------------- R5: halts

def test_only_named_halts_exist(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"))
    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_halt(str(tmp_path), "it_felt_stuck")
    assert "unknown_halt" in str(err.value)
    assert gpe_mode.cmd_halt(str(tmp_path), "gen_stalled", "no record for 6m")["halt"] == "gen_stalled"


# ---------------------------------------------------------------- R9: unbounded, never vacuous

def _council(tmp_path, sid="cvsess-x"):
    """M1's precondition: a deliberation stands behind the attempt being superseded."""
    gpe_mode.cmd_doctor(str(tmp_path), sid, backlog=[], prescriptions=[])


def test_a_new_attempt_needs_a_new_cause_and_a_redeployed_correction(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt1"))
    gpe_mode.cmd_halt(str(tmp_path), "gen_stalled")
    gpe_mode.cmd_doctor(str(tmp_path), "cvsess-novelty", backlog=[], prescriptions=[])

    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt2"))
    assert "no_new_correction" in str(err.value)

    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt2"),
                             cause="brief_missing_repo", correction="abc1234")
    assert "no_new_correction" in str(err.value)  # landed but never redeployed

    second = gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt2"),
                                  cause="brief_missing_repo", correction="abc1234",
                                  redeployed=True, backlog_ref="#2901")
    assert second["n"] == 2

    gpe_mode.cmd_halt(str(tmp_path), "gen_stalled")
    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt3"),
                             cause="brief_missing_repo", correction="", redeployed=False)
    assert "no_new_correction" in str(err.value)


def test_there_is_no_attempt_cap(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt0"))
    # M1 (cvsess-63124fd46e3b4c68) now requires a council behind each predecessor, a commit no
    # earlier attempt spent, and backlog lineage. The founder's rule is untouched: there is no
    # CEILING. A well-formed iteration opens forever; only a vacuous one is refused.
    for n in range(1, 12):
        gpe_mode.cmd_doctor(str(tmp_path), "cvsess-%d" % n, backlog=[], prescriptions=[])
        gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / ("wt%d" % n)),
                             cause="cause-%d" % n, correction="c%d" % n, redeployed=True,
                             backlog_ref="#29%02d" % n)
    state = gpe_mode.read_state(str(tmp_path))
    assert len(state["cycles"][-1]["attempts"]) == 12


# ---------------------------------------------------------------- R7: her three areas

def test_the_three_areas_are_closed_by_enum():
    assert gpe_mode.LUCENS_BACKLOG_AREAS == ("quantum_computing", "ontologies", "logic")


def test_an_area_counts_only_when_named_and_titled():
    assert gpe_mode.backlog_gaps([]) == list(gpe_mode.LUCENS_BACKLOG_AREAS)
    entries = [
        {"area": "quantum_computing", "title": "Entanglement-aware search", "prescription": "…"},
        {"area": "ontologies", "title": "", "prescription": "…"},          # no title
        {"area": "philosophy", "title": "Something else", "prescription": "…"},  # outside the three
        {"area": "logic", "title": "Non-monotonic check", "prescription": "…"},
    ]
    assert gpe_mode.backlog_gaps(entries) == ["ontologies"]


def test_the_doctor_records_gaps_and_targets_outside_gen(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"))
    doctor = gpe_mode.cmd_doctor(
        str(tmp_path), session_id="loopsess-1",
        backlog=[{"area": "quantum_computing", "title": "t", "prescription": "p"}],
        prescriptions=[{"target": "gen:internal/loop", "why": "…"},
                       {"target": "ascent:cmd/ascent", "why": "…"}])
    assert doctor["lucens_backlog_gaps"] == ["ontologies", "logic"]
    assert doctor["targets_outside_gen"] == ["ascent:cmd/ascent"]

    state = gpe_mode.read_state(str(tmp_path))
    facts = state["cycles"][-1]["attempts"][-1]["facts"]
    assert facts["doctor.lucens_backlog_three_areas"] is False
    assert facts["doctor.targets_gen"] is False


def test_a_seat_that_was_never_asked_is_not_a_pass(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"))
    gpe_mode.cmd_doctor(str(tmp_path), session_id="loopsess-2", backlog=[],
                        lucens_present=False, lucens_absent_reason="lucens_unreachable")
    state = gpe_mode.read_state(str(tmp_path))
    attempt = state["cycles"][-1]["attempts"][-1]
    assert attempt["facts"]["doctor.lucens_present"] is False
    assert attempt["doctor"]["lucens"]["absent_reason"] == "lucens_unreachable"


# ---------------------------------------------------------------- R10: the audit judges by the contract

def contract():
    return gpe_audit.load_contract(CONTRACT)


def test_pending_is_never_a_defect_and_unknown_always_is(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true")
    state = gpe_mode.read_state(str(tmp_path))
    rows, defects = gpe_audit.audit(state, contract())
    by_fact = {r["fact"]: r["verdict"] for r in rows}
    assert by_fact["open.request_verbatim"] == "ok"
    assert by_fact["judge.acceptance_ran"] == "pending"
    assert defects == []

    # The moment a later phase records a fact, the phase's own silent facts become UNKNOWN.
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"), session_id="s1")
    gpe_mode.cmd_fact(str(tmp_path), "judge.acceptance_ran", True)
    rows, defects = gpe_audit.audit(gpe_mode.read_state(str(tmp_path)), contract())
    by_fact = {r["fact"]: r["verdict"] for r in rows}
    assert by_fact["judge.acceptance_result"] == "unknown"
    assert "judge.acceptance_result" in defects


def test_a_not_fulfilled_acceptance_is_out_of_accord(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"), session_id="s1")
    for name, value in [("provision.clean", True), ("dispatch.brief_delivered", True),
                        ("supervise.record_read", True), ("supervise.halt", "acceptance_failed"),
                        ("judge.acceptance_ran", True), ("judge.diff_read", True),
                        ("judge.acceptance_result", "not_fulfilled")]:
        gpe_mode.cmd_fact(str(tmp_path), name, value)
    _, defects = gpe_audit.audit(gpe_mode.read_state(str(tmp_path)), contract())
    assert "judge.acceptance_result" in defects


def test_a_whole_honest_cycle_is_in_accord(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "pytest -q tests/test_thing.py")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"), session_id="s1")
    for name, value in [
        ("provision.clean", True), ("dispatch.brief_delivered", True),
        ("supervise.record_read", True), ("supervise.halt", "none"),
        ("judge.acceptance_ran", True), ("judge.acceptance_result", "fulfilled"),
        ("judge.diff_read", True),
        ("correct.implemented", True), ("correct.tests_paired", True),
        ("correct.blocked_named", True),
        ("land.on_main", "9267076"), ("land.remote_verified", True),
        ("redeploy.version", "gen 1.2.4"), ("redeploy.sha256", "a" * 64),
        ("redeploy.readback_independent", True),
        ("close.new_cause", True), ("close.correction_landed", True),
    ]:
        gpe_mode.cmd_fact(str(tmp_path), name, value)
    gpe_mode.cmd_doctor(
        str(tmp_path), session_id="loopsess-3",
        backlog=[{"area": a, "title": "t-%s" % a, "prescription": "p"}
                 for a in gpe_mode.LUCENS_BACKLOG_AREAS],
        prescriptions=[{"target": "gen:internal/loop", "why": "…"}])
    gpe_mode.cmd_close(str(tmp_path), "fulfilled")
    rows, defects = gpe_audit.audit(gpe_mode.read_state(str(tmp_path)), contract())
    assert defects == [], defects
    assert all(r["verdict"] in ("ok",) for r in rows), [r for r in rows if r["verdict"] != "ok"]


# ---------------------------------------------------------------- the contract itself

def test_every_contract_fact_is_reachable_by_the_state_machine():
    """A fact no phase can ever record is a contract that judges nothing."""
    names = {m["name"] for p in contract()["phases"] for m in p["must"]}
    source = open(os.path.join(os.path.dirname(HERE), "scripts", "gpe_mode.py")).read()
    audit_source = open(os.path.join(os.path.dirname(HERE), "scripts", "gpe_audit.py")).read()
    # Facts the state machine writes itself, plus the ones the assistant records with `fact`.
    written = {n for n in names if n in source or n in audit_source}
    free = names - written
    assert free == {
        "provision.clean", "dispatch.brief_delivered", "supervise.record_read",
        "judge.acceptance_ran", "judge.diff_read",
        "correct.implemented", "correct.tests_paired", "correct.blocked_named",
        "land.on_main", "land.remote_verified",
        "redeploy.version", "redeploy.sha256", "redeploy.readback_independent",
        "close.new_cause", "close.correction_landed",
    }, sorted(free)


def test_the_cli_refuses_by_name_and_exits_nonzero(tmp_path, capsys):
    rc = gpe_mode.main(["--repo", str(tmp_path), "open", "--request", "x"])
    assert rc == 1
    assert json.loads(capsys.readouterr().out)["refused"] == "mode_not_armed"
