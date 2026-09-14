"""Paired tests for the enhancement mode's state machine and its audit.

Each test names the rule it guards. They run without a gen binary, without a network and without
a repository: the mode's laws are testable by construction, or they are not laws.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
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
    state = gpe_mode.cmd_arm(str(tmp_path), path, runner=runner)
    # An armed mode runs its minute monitor — the rite refuses to advance without one — so the
    # helper that arms also beats. The tests that assert the REFUSAL clear the heartbeat.
    _beat(tmp_path)
    return state


def _beat(tmp_path, seconds_ago=0.0):
    import time as _t
    d = tmp_path / ".risegen" / "gpe-mode" / "monitor"
    d.mkdir(parents=True, exist_ok=True)
    (d / "heartbeat.json").write_text(json.dumps({"at": _t.time() - seconds_ago, "pid": 1}))


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
    acceptance = gpe_mode.cmd_acceptance(str(tmp_path), "pytest -q tests/test_seat.py", "good/", "bad/", "origin/main")
    assert acceptance["held_out"] is True

    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"), session_id="s1")
    gpe_mode.cmd_fact(str(tmp_path), "judge.acceptance_result", "not_fulfilled")
    with pytest.raises(gpe_mode.ModeError) as err:
        gpe_mode.cmd_acceptance(str(tmp_path), "pytest -q -k anything_that_passes", "good/", "bad/", "origin/main")
    assert "acceptance_authored_after_result" in str(err.value)


def test_a_cycle_never_closes_fulfilled_on_gens_word(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", "origin/main")
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
    # The open phase names the instruments the request carries — "none" is an answer, silence is
    # not (founder ruling 2026-09-09: a named instrument is part of the deliverable).
    gpe_mode.cmd_fact(str(tmp_path), "open.instruments_named", "none")
    gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", "origin/main")
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
    gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", "origin/main")
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
    gpe_mode.cmd_acceptance(str(tmp_path), "pytest -q tests/test_thing.py", "good/", "bad/", "origin/main")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"), session_id="s1")
    for name, value in [
        ("provision.clean", True), ("dispatch.brief_delivered", True),
        ("dispatch.model", gpe_mode.GEN_MODEL),
        ("dispatch.knobs_read_from_source", "GEN_SKIP_LOOP_DETECTION=1 (internal/engine/home.go)"),
        ("open.instruments_named", "none"), ("judge.provenance_verified", "n/a"),
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
        "judge.acceptance_ran", "judge.diff_read", "dispatch.model",
        "open.instruments_named", "judge.provenance_verified",
        "dispatch.knobs_read_from_source",
        "correct.implemented", "correct.tests_paired", "correct.blocked_named",
        "land.on_main", "land.remote_verified",
        "redeploy.version", "redeploy.sha256", "redeploy.readback_independent",
        "close.new_cause", "close.correction_landed",
    }, sorted(free)


def test_the_cli_refuses_by_name_and_exits_nonzero(tmp_path, capsys):
    rc = gpe_mode.main(["--repo", str(tmp_path), "open", "--request", "x"])
    assert rc == 1
    assert json.loads(capsys.readouterr().out)["refused"] == "mode_not_armed"


# ---------------------------------------------------------------- the model pin

def test_arming_records_the_pinned_model(tmp_path):
    """The mode pins gen's model; arming writes it where the dispatch and the tick both read it."""
    state = arm(tmp_path)
    assert state["gen"]["model"] == gpe_mode.GEN_MODEL


def test_the_cli_prints_the_pin_so_it_is_never_typed_from_memory(tmp_path, capsys):
    assert gpe_mode.main(["--repo", str(tmp_path), "model"]) == 0
    assert capsys.readouterr().out.strip() == gpe_mode.GEN_MODEL


def test_every_write_stamps_who_wrote_it(tmp_path):
    """The tick tells the supervisor's mandated writes from anyone else's by this stamp."""
    import time as _t
    before = _t.time()
    arm(tmp_path)
    stamp = gpe_mode.read_state(str(tmp_path))["state_machine_wrote_at"]
    assert before <= stamp <= _t.time()
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    assert gpe_mode.read_state(str(tmp_path))["state_machine_wrote_at"] >= stamp


# ---------------------------------------------------------------- THE PLAN GATE
# Founder, 2026-09-09: "voce precisa implementar tudo o que e está previsto e só depois disparar a
# proxima tentativa, proteja a skill para que isso seja assegurado". Measured on cycle
# gpe-24500fd57f7d: two councils, sixteen items, four landed, next attempt opened anyway.

def _cycle_with_a_council(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", "origin/main")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"), session_id="s1")
    gpe_mode.cmd_doctor(
        str(tmp_path), session_id="cvsess-1",
        backlog=[{"area": a, "title": "T-%s" % a, "prescription": "p"}
                 for a in gpe_mode.LUCENS_BACKLOG_AREAS],
        prescriptions=[{"id": "P1", "target": "gen:resolver", "why": "…"},
                       {"id": "P2", "target": "gen:banking", "why": "…"}])


def _open_next(tmp_path, commit="abc1234"):
    return gpe_mode.cmd_attempt(
        str(tmp_path), worktree=str(tmp_path / "wt2"), session_id="s2",
        cause="a_new_cause", correction=commit, redeployed=True,
        backlog_ref="org/repo#1")


def test_a_new_attempt_is_refused_while_the_plan_has_not_landed(tmp_path):
    _cycle_with_a_council(tmp_path)
    with pytest.raises(gpe_mode.ModeError) as exc:
        _open_next(tmp_path)
    msg = str(exc.value)
    assert msg.startswith("plan_not_landed")
    assert "P1" in msg and "P2" in msg


def test_her_floor_is_not_a_lower_class_of_item(tmp_path):
    """Six of her entries were recorded and none implemented; the gate counts them like any other."""
    _cycle_with_a_council(tmp_path)
    gpe_mode.cmd_landed(str(tmp_path), "P1", "aaa1111")
    gpe_mode.cmd_landed(str(tmp_path), "P2", "bbb2222")
    with pytest.raises(gpe_mode.ModeError) as exc:
        _open_next(tmp_path)
    for area in gpe_mode.LUCENS_BACKLOG_AREAS:
        assert "T-%s" % area in str(exc.value)


def test_the_attempt_opens_once_every_item_has_landed(tmp_path):
    _cycle_with_a_council(tmp_path)
    for i, item in enumerate(["P1", "P2"] + ["T-%s" % a for a in gpe_mode.LUCENS_BACKLOG_AREAS]):
        gpe_mode.cmd_landed(str(tmp_path), item, "c%06d" % i)
    attempt = _open_next(tmp_path)
    assert attempt["n"] == 2


def test_a_landing_names_its_commit_and_its_item(tmp_path):
    _cycle_with_a_council(tmp_path)
    with pytest.raises(gpe_mode.ModeError) as exc:
        gpe_mode.cmd_landed(str(tmp_path), "P1", "")
    assert "landing_without_commit" in str(exc.value)
    with pytest.raises(gpe_mode.ModeError) as exc:
        gpe_mode.cmd_landed(str(tmp_path), "P99", "abc")
    assert "unknown_plan_item" in str(exc.value)


def test_there_is_no_deferral_flag(tmp_path):
    """The loophole the measured failure walked through is not reintroduced as an option."""
    source = open(os.path.join(os.path.dirname(HERE), "scripts", "gpe_mode.py")).read()
    for loophole in ("--defer", "deferred", "skip_plan", "force_attempt"):
        assert loophole not in source, loophole


# ---------------------------------------------------------------- R3: the acceptance's own fixtures

def test_an_acceptance_without_fixtures_is_refused(tmp_path):
    """The only artifact in this flow with no paired test is the one that decides the verdict."""
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    for missing in (("", "bad/"), ("good/", ""), ("", "")):
        with pytest.raises(gpe_mode.ModeError) as exc:
            gpe_mode.cmd_acceptance(str(tmp_path), "true", *missing, base="origin/main")
        assert "acceptance_without_fixtures" in str(exc.value)


def test_an_acceptance_without_a_base_is_refused(tmp_path):
    """One command gave 18/9 and 27/27 on this cycle, both honest, only one measuring gen."""
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    with pytest.raises(gpe_mode.ModeError) as exc:
        gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", base="")
    assert "acceptance_without_base" in str(exc.value)


def test_the_fixtures_are_recorded_and_start_unproven(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    acc = gpe_mode.cmd_acceptance(str(tmp_path), "check.sh", "good-sample/", "forged-sample/",
                                  "origin/main")
    assert acc["base"] == "origin/main"
    assert acc["fixtures"] == {"must_pass": "good-sample/", "must_fail": "forged-sample/",
                               "proven": False}
    proven = gpe_mode.cmd_fixtures_proven(str(tmp_path))
    assert proven["proven"] is True and proven["proven_at"]


# ---------------------------------------------------------------- R5: the subject audits the supervisor

def test_a_finding_the_subject_made_about_the_supervisor_is_recorded(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    e = gpe_mode.cmd_finding(
        str(tmp_path), about="supervisor",
        text="gen entities resolve refuses AACP from inside a worktree")
    assert e["about"] == "supervisor" and e["found_by"] == "gen"
    cycle = gpe_mode.read_state(str(tmp_path))["cycles"][-1]
    assert len(cycle["findings"]) == 1


def test_a_finding_names_a_party_and_carries_text(tmp_path):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    for kwargs, want in (
        (dict(about="nobody", text="x"), "finding_about_unknown"),
        (dict(about="supervisor", text="  "), "finding_without_text"),
    ):
        with pytest.raises(gpe_mode.ModeError) as exc:
            gpe_mode.cmd_finding(str(tmp_path), **kwargs)
        assert want in str(exc.value)


# ---------------------------------------------------------------- the minute monitor must be RUNNING
# Founder, 2026-09-09, restating the order after the first cut only added the reading: "precisa
# adicionar na skill pra que tenha um monitor que é ativado a cada minuto para garantir que o fluxo
# nao pare". A check that exists but is not running guarantees nothing — and a supervisor that has
# stopped is exactly the one who will not remember to start its own watchdog.

def test_the_rite_refuses_to_advance_with_no_monitor(tmp_path):
    _cycle_with_a_council(tmp_path)
    for item in ["P1", "P2"] + ["T-%s" % a for a in gpe_mode.LUCENS_BACKLOG_AREAS]:
        gpe_mode.cmd_landed(str(tmp_path), item, "c1")
    (tmp_path / ".risegen" / "gpe-mode" / "monitor" / "heartbeat.json").unlink()
    with pytest.raises(gpe_mode.ModeError) as exc:
        _open_next(tmp_path)
    assert "monitor_not_running" in str(exc.value)
    assert "never beaten" in str(exc.value)


def test_a_stale_heartbeat_is_no_monitor_at_all(tmp_path):
    _cycle_with_a_council(tmp_path)
    for item in ["P1", "P2"] + ["T-%s" % a for a in gpe_mode.LUCENS_BACKLOG_AREAS]:
        gpe_mode.cmd_landed(str(tmp_path), item, "c1")
    _beat(tmp_path, seconds_ago=gpe_mode.HEARTBEAT_STALE_SECONDS + 1)
    with pytest.raises(gpe_mode.ModeError) as exc:
        _open_next(tmp_path)
    assert "monitor_not_running" in str(exc.value)


def test_a_beating_monitor_lets_the_rite_move(tmp_path):
    _cycle_with_a_council(tmp_path)
    for i, item in enumerate(["P1", "P2"] + ["T-%s" % a for a in gpe_mode.LUCENS_BACKLOG_AREAS]):
        gpe_mode.cmd_landed(str(tmp_path), item, "c%d" % i)
    _beat(tmp_path)
    assert _open_next(tmp_path)["n"] == 2


def test_monitor_status_reports_what_it_measured(tmp_path):
    assert gpe_mode.cmd_monitor(str(tmp_path), "status") == {
        "running": False, "last_beat_seconds_ago": None,
        "stale_after_seconds": gpe_mode.HEARTBEAT_STALE_SECONDS}
    _beat(tmp_path)
    st = gpe_mode.cmd_monitor(str(tmp_path), "status")
    assert st["running"] is True and st["last_beat_seconds_ago"] == 0


def test_the_heartbeat_age_of_a_corrupt_file_is_unknown_not_fresh(tmp_path):
    d = tmp_path / ".risegen" / "gpe-mode" / "monitor"
    d.mkdir(parents=True, exist_ok=True)
    (d / "heartbeat.json").write_text("{not json")
    assert gpe_mode.heartbeat_age(str(tmp_path)) is None


def test_monitor_start_passes_the_flight_pid_to_the_tick(monkeypatch, tmp_path):
    """Without the pid the tick cannot see a live flight, so a healthy dispatch reads as
    flow_not_running and then as supervisor_inert — the inertia alarm firing at a supervisor doing
    exactly what it should. Measured on attempt 4 of gpe-24500fd57f7d, 335 records into a good
    flight."""
    seen = {}

    class FakeProc:
        pid = 4242

    def fake_popen(argv, **kwargs):
        seen["argv"] = argv
        return FakeProc()

    monkeypatch.setattr(gpe_mode.subprocess, "Popen", fake_popen)
    out = gpe_mode.cmd_monitor(str(tmp_path), "start", record="/tmp/rec.jsonl", pid="777")
    assert out["started"] is True
    assert "--pid" in seen["argv"] and "777" in seen["argv"]
    assert "--record" in seen["argv"] and "/tmp/rec.jsonl" in seen["argv"]
    assert "--every" in seen["argv"] and "60" in seen["argv"]


def test_monitor_start_without_a_flight_passes_no_pid(monkeypatch, tmp_path):
    seen = {}

    class FakeProc:
        pid = 1

    def fake_popen(argv, **kwargs):
        seen["argv"] = argv
        return FakeProc()

    monkeypatch.setattr(gpe_mode.subprocess, "Popen", fake_popen)
    gpe_mode.cmd_monitor(str(tmp_path), "start")
    assert "--pid" not in seen["argv"]


# ---------------------------------------------------------------- S1: the halt ENDS the flight
# Code Doctor cvsess-3b780482572e46d1, over attempt 4 of gpe-24500fd57f7d: the supervisor signalled
# a PARENT PID, children 9769/9771 survived, and it then recreated the worktree under them and
# dispatched a second flight into the same branch. Killing a parent is not ending a flight, and
# typing `kill` asserts a fact the typist has not measured.

def _spawn_group():
    """A parent whose CHILD outlives a signal to the parent alone — the exact shape that failed."""
    import subprocess as sp
    parent = sp.Popen(
        [sys.executable, "-c",
         "import subprocess,sys,time;"
         "subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)']);"
         "time.sleep(30)"],
        start_new_session=True)
    time.sleep(0.5)
    return parent


def test_the_state_machine_ends_the_whole_group(tmp_path):
    parent = _spawn_group()
    try:
        out = gpe_mode.end_flight(parent.pid)
        assert out["ended"] is True, out
        assert out["pgid"] == parent.pid, "the group is the target, not the pid"
        assert out["survivors"] == []
    finally:
        try:
            os.killpg(parent.pid, 9)
        except OSError:
            pass


def test_a_halt_that_could_not_end_its_flight_refuses_to_be_recorded(tmp_path, monkeypatch):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", "origin/main")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"))
    monkeypatch.setattr(gpe_mode, "end_flight",
                        lambda pid, **kw: {"pid": pid, "pgid": 1, "signalled": True,
                                           "survivors": [pid], "ended": False})
    with pytest.raises(gpe_mode.ModeError) as exc:
        gpe_mode.cmd_halt(str(tmp_path), "gen_stalled", pid=4242)
    assert "halt_did_not_end_the_flight" in str(exc.value)
    # and the halt is NOT on the record: a flight still running was never halted
    attempt = gpe_mode.read_state(str(tmp_path))["cycles"][-1]["attempts"][-1]
    assert attempt["halt"] is None


def test_a_halt_that_ended_its_flight_records_what_it_measured(tmp_path, monkeypatch):
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", "origin/main")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"))
    monkeypatch.setattr(gpe_mode, "end_flight",
                        lambda pid, **kw: {"pid": pid, "pgid": 99, "signalled": True,
                                           "survivors": [], "ended": True})
    out = gpe_mode.cmd_halt(str(tmp_path), "gen_stalled", pid=4242)
    assert out["interruption"]["ended"] is True
    attempt = gpe_mode.read_state(str(tmp_path))["cycles"][-1]["attempts"][-1]
    assert attempt["halt_interruption"]["pgid"] == 99


def test_a_halt_with_no_pid_still_works_and_measures_nothing(tmp_path):
    """`halt none` after a flight already exited has nothing to end, and must not pretend it did."""
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", "origin/main")
    gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"))
    out = gpe_mode.cmd_halt(str(tmp_path), "none")
    assert out["interruption"] is None


def test_ending_a_pid_that_is_already_gone_is_not_a_failure():
    out = gpe_mode.end_flight(999999)
    assert out["ended"] is True and out["signalled"] is False


# ---------------------------------------------------------------- S2: an occupied tree refuses
def test_a_dispatch_into_an_occupied_tree_is_refused(tmp_path, monkeypatch):
    """Attempt 4: the supervisor recreated a worktree under two live gen processes and dispatched
    a second flight into the same branch. gen detected the occupancy the supervisor could not."""
    arm(tmp_path)
    gpe_mode.cmd_open(str(tmp_path), "do the thing")
    gpe_mode.cmd_acceptance(str(tmp_path), "true", "good/", "bad/", "origin/main")
    monkeypatch.setattr(gpe_mode, "occupants", lambda wt: [9769, 9771])
    with pytest.raises(gpe_mode.ModeError) as exc:
        gpe_mode.cmd_attempt(str(tmp_path), worktree=str(tmp_path / "wt"))
    msg = str(exc.value)
    assert "worktree_occupied" in msg and "9769" in msg and "9771" in msg


def test_an_unmeasurable_tree_is_reported_empty_only_because_it_cannot_be_measured(tmp_path,
                                                                                   monkeypatch):
    """lsof missing is 'not measured'. It must not raise — but the caller sees an empty list, so
    the honest place for that limit is here, in one named test, rather than a silent assumption
    spread through the code."""
    monkeypatch.setattr(gpe_mode.subprocess, "run",
                        lambda *a, **kw: (_ for _ in ()).throw(FileNotFoundError("lsof")))
    assert gpe_mode.occupants(str(tmp_path)) == []


# ---------------------------------------------------------------- S3: a finding GATES the attempt
def test_an_unanswered_finding_about_the_supervisor_blocks_the_next_attempt(tmp_path):
    _cycle_with_a_council(tmp_path)
    for i, item in enumerate(["P1", "P2"] + ["T-%s" % a for a in gpe_mode.LUCENS_BACKLOG_AREAS]):
        gpe_mode.cmd_landed(str(tmp_path), item, "c%d" % i)
    f = gpe_mode.cmd_finding(str(tmp_path), about="supervisor",
                             text="the resolver refuses AACP from inside a worktree")
    with pytest.raises(gpe_mode.ModeError) as exc:
        _open_next(tmp_path)
    assert "plan_not_landed" in str(exc.value) and f["id"] in str(exc.value)
    gpe_mode.cmd_landed(str(tmp_path), f["id"], "8b9124a")
    assert _open_next(tmp_path)["n"] == 2


def test_a_finding_about_gen_is_not_the_supervisors_to_land(tmp_path):
    _cycle_with_a_council(tmp_path)
    for i, item in enumerate(["P1", "P2"] + ["T-%s" % a for a in gpe_mode.LUCENS_BACKLOG_AREAS]):
        gpe_mode.cmd_landed(str(tmp_path), item, "c%d" % i)
    gpe_mode.cmd_finding(str(tmp_path), about="gen", found_by="supervisor", text="gen looped")
    assert _open_next(tmp_path)["n"] == 2


def test_a_finding_recorded_before_ids_existed_is_still_gateable(tmp_path):
    """Three of gen's five findings predated the id field. An item the gate cannot NAME is an item
    the gate cannot enforce, and arriving early is not a reason to escape it."""
    _cycle_with_a_council(tmp_path)
    for i, item in enumerate(["P1", "P2"] + ["T-%s" % a for a in gpe_mode.LUCENS_BACKLOG_AREAS]):
        gpe_mode.cmd_landed(str(tmp_path), item, "c%d" % i)
    state = gpe_mode.read_state(str(tmp_path))
    state["cycles"][-1]["findings"] = [
        {"about": "supervisor", "found_by": "gen", "text": "the brief named an unlanded base"}]
    gpe_mode.write_state(str(tmp_path), state)

    legacy_id = gpe_mode.finding_id({"text": "the brief named an unlanded base"})
    with pytest.raises(gpe_mode.ModeError) as exc:
        _open_next(tmp_path)
    assert legacy_id in str(exc.value)
    gpe_mode.cmd_landed(str(tmp_path), legacy_id, "abc1234")
    assert _open_next(tmp_path)["n"] == 2


def test_a_derived_id_is_stable_so_a_landing_against_it_keeps_holding():
    a = gpe_mode.finding_id({"text": "same text"})
    b = gpe_mode.finding_id({"text": "same text"})
    assert a == b and a.startswith("finding-")
    assert gpe_mode.finding_id({"id": "finding-explicit", "text": "x"}) == "finding-explicit"
