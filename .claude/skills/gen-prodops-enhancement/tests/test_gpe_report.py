"""Paired tests for M1–M4, Code Doctor cvsess-63124fd46e3b4c68.

Every test replays the REAL attempt sequence of cycle gpe-8a711f9ba13b —
[none, 9997cbf, 9997cbf, 87ca3f3, d0a39d3, d0a39d3, d0a39d3, d0a39d3] — because the
verification-quality seat's rule stands: a mechanism that cannot reproduce the failure it was
prescribed for is one nobody has reason to believe.

The sequence matters. `no_new_correction` was already written in the skill and already declared to
stop the flow; what it measured was the CAUSE, which the supervisor writes freely, and never the
COMMIT, which is the only thing that actually changed. It fired zero times across four reuses.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

import gpe_mode  # noqa: E402
import gpe_report  # noqa: E402

# The measured sequence, verbatim from state.json.
REAL_SEQUENCE = [None, "9997cbf", "9997cbf", "87ca3f3", "d0a39d3", "d0a39d3", "d0a39d3", "d0a39d3"]


def cycle_with(attempts):
    return {"id": "gpe-8a711f9ba13b", "request": "connect the iPad", "attempts": attempts}


def attempt(n, commit=None, council="", backlog="", halt=None):
    a = {"n": n, "cause": "cause %d" % n, "halt": halt, "facts": {}}
    if council:
        a["council"] = {"session_id": council}
    if commit:
        a["correction"] = {"commit": commit, "redeployed": True, "backlog_ref": backlog}
    return a


# --- M3 verify: the measurement that was missing --------------------------------------------------

def test_the_real_sequence_is_flagged_at_every_reuse():
    rows = gpe_report.audit_attempts(cycle_with(
        [attempt(i + 1, c) for i, c in enumerate(REAL_SEQUENCE)]))
    reused = [r["n"] for r in rows if "no_new_correction" in r["breaches"]]
    assert reused == [3, 6, 7, 8], reused


def test_every_attempt_of_the_real_cycle_is_in_breach():
    rows = gpe_report.audit_attempts(cycle_with(
        [attempt(i + 1, c) for i, c in enumerate(REAL_SEQUENCE)]))
    assert all(r["breaches"] for r in rows)
    assert all("no_council" in r["breaches"] for r in rows)


def test_a_clean_cycle_is_not_flagged():
    rows = gpe_report.audit_attempts(cycle_with([
        attempt(1, council="cvsess-a"),
        attempt(2, "aaa1111", council="cvsess-b", backlog="#2900"),
        attempt(3, "bbb2222", council="cvsess-c", backlog="#2901"),
    ]))
    assert not any(r["breaches"] for r in rows), [r["breaches"] for r in rows]


def test_verify_exits_non_zero_on_a_cycle_in_breach(tmp_path, capsys):
    repo = tmp_path / "repo"
    (repo / ".risegen" / "gpe-mode").mkdir(parents=True)
    (repo / ".risegen" / "gpe-mode" / "state.json").write_text(json.dumps({
        "armed": True,
        "cycles": [cycle_with([attempt(i + 1, c) for i, c in enumerate(REAL_SEQUENCE)])],
    }))
    assert gpe_report.main(["--repo", str(repo), "--verify"]) == 1
    assert "no_new_correction" in capsys.readouterr().out


# --- M1 attempt-gate: the refusal ------------------------------------------------------------------

def armed_repo(tmp_path, attempts):
    repo = tmp_path / "repo"
    (repo / ".risegen" / "gpe-mode").mkdir(parents=True)
    (repo / ".risegen" / "gpe-mode" / "state.json").write_text(json.dumps({
        "armed": True,
        "gen": {"version": "gen 0.2.0", "sha256": "abc"},
        "cycles": [cycle_with(attempts)],
    }))
    # An armed mode runs its minute monitor; the rite refuses to advance without one.
    import time as _t
    beat = repo / ".risegen" / "gpe-mode" / "monitor"
    beat.mkdir(parents=True, exist_ok=True)
    (beat / "heartbeat.json").write_text(json.dumps({"at": _t.time(), "pid": 1}))
    return str(repo)


def test_a_new_cause_with_an_old_commit_is_refused():
    """The exact hole: attempts 5-8 each named a fresh cause and rode the same d0a39d3."""
    repo = armed_repo(pytest.importorskip("pathlib") and __import__("pathlib").Path(
        __import__("tempfile").mkdtemp()), [
            attempt(1, council="cvsess-a"),
            attempt(2, "d0a39d3", council="cvsess-b", backlog="#2900")])
    with pytest.raises(gpe_mode.ModeError) as e:
        gpe_mode.cmd_attempt(repo, "/wt", cause="a brand new cause",
                             correction="d0a39d3", redeployed=True, backlog_ref="#2901")
    assert "no_new_correction" in str(e.value)
    assert "d0a39d3" in str(e.value)


def test_a_correction_without_backlog_lineage_is_refused(tmp_path):
    repo = armed_repo(tmp_path, [
        attempt(1, council="cvsess-a"),
        attempt(2, "aaa1111", council="cvsess-b", backlog="#2900")])
    with pytest.raises(gpe_mode.ModeError) as e:
        gpe_mode.cmd_attempt(repo, "/wt", cause="new", correction="bbb2222", redeployed=True)
    assert "no_backlog_lineage" in str(e.value)


def test_an_attempt_whose_predecessor_had_no_council_is_refused(tmp_path):
    """Iterations 2 through 8 all opened this way and nothing stopped."""
    repo = armed_repo(tmp_path, [attempt(1)])
    with pytest.raises(gpe_mode.ModeError) as e:
        gpe_mode.cmd_attempt(repo, "/wt", cause="new", correction="aaa1111",
                             redeployed=True, backlog_ref="#2900")
    assert "no_council_behind_attempt" in str(e.value)


def test_a_well_formed_attempt_still_opens(tmp_path):
    repo = armed_repo(tmp_path, [attempt(1, council="cvsess-a")])
    a = gpe_mode.cmd_attempt(repo, "/wt", cause="a named new cause",
                             correction="aaa1111", redeployed=True, backlog_ref="#2900")
    assert a["n"] == 2
    assert a["correction"]["backlog_ref"] == "#2900"


# --- M2 close-gate and immutable council identity --------------------------------------------------

def test_a_cycle_cannot_close_around_skipped_councils(tmp_path):
    repo = armed_repo(tmp_path, [
        attempt(1, council="cvsess-a"),
        attempt(2, "aaa1111", backlog="#2900")])
    gpe_mode.cmd_fact(repo, "judge.acceptance_result", "fulfilled")
    with pytest.raises(gpe_mode.ModeError) as e:
        gpe_mode.cmd_close(repo, "fulfilled")
    assert "close_without_council" in str(e.value)


def test_a_recorded_council_cannot_be_overwritten(tmp_path):
    repo = armed_repo(tmp_path, [attempt(1, council="cvsess-real")])
    with pytest.raises(gpe_mode.ModeError) as e:
        gpe_mode.cmd_doctor(repo, "cvsess-other", backlog=[], prescriptions=[])
    assert "council_identity_immutable" in str(e.value)


def test_council_identity_survives_close_then_attempt(tmp_path):
    """close --outcome new_attempt then attempt is exactly what wiped doctor.council_real."""
    repo = armed_repo(tmp_path, [attempt(1, council="cvsess-a")])
    gpe_mode.cmd_close(repo, "new_attempt")
    gpe_mode.cmd_attempt(repo, "/wt", cause="new", correction="aaa1111",
                         redeployed=True, backlog_ref="#2900")
    state = json.load(open(os.path.join(repo, ".risegen", "gpe-mode", "state.json")))
    first = state["cycles"][-1]["attempts"][0]
    assert first["council"]["session_id"] == "cvsess-a"


# --- M4 report: the founder's specification --------------------------------------------------------

def test_the_report_carries_every_field_the_founder_named(tmp_path):
    a2 = attempt(2, "aaa1111", council="cvsess-b", backlog="#2900", halt="gen_loop_detected")
    a2["halt_detail"] = "action_stagnation"
    a2["facts"] = {"redeploy.version": "gen 0.2.0 commit aaa1111", "redeploy.sha256": "deadbeef"}
    state = {"armed": True, "gen": {"version": "gen 0.2.0"},
             "cycles": [cycle_with([attempt(1, council="cvsess-a"), a2])]}
    text = gpe_report.render(state, state["cycles"][-1])

    assert "ITERATION 2" in text
    assert "FAILURE" in text                    # success or failure
    assert "gen_loop_detected" in text          # how it ended
    assert "action_stagnation" in text          # WHICH failure
    assert "#2900" in text                      # derived backlog
    assert "commit aaa1111" in text             # the new version
    assert "deadbeef" in text                   # ...and its sha256


def test_missing_data_is_a_named_absence_never_a_blank(tmp_path):
    state = {"armed": True, "gen": {}, "cycles": [cycle_with([attempt(1)])]}
    text = gpe_report.render(state, state["cycles"][-1])
    assert gpe_report.ABSENT in text
    assert "  council:       \n" not in text


def test_the_report_names_the_breach_rather_than_staying_silent():
    state = {"armed": True, "gen": {},
             "cycles": [cycle_with([attempt(i + 1, c) for i, c in enumerate(REAL_SEQUENCE)])]}
    text = gpe_report.render(state, state["cycles"][-1])
    assert "BREACH" in text
    assert "in breach: 8" in text
