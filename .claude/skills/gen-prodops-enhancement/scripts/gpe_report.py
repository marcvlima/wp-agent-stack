"""M3 `verify` and M4 `report` — what a reader who was not here can find out.

Code Doctor `cvsess-63124fd46e3b4c68`, convened by the founder over the previous council's
referral that *the auditor is not audited*. Bancadas: code assistant (agentic-development), ai
(ai-ml), agência de marketing (agency), and Lucens.

Measured on cycle `gpe-8a711f9ba13b`: eight attempts, one council. `no_new_correction` fired four
consecutive times while the tool accepted every one, because the check read the CAUSE — which the
supervisor writes — and never the COMMIT, which is what actually changed. The council's identity
was lost when `close --outcome new_attempt` followed by `attempt` wiped the cycle facts. Five
commits landed on a product repository's main carrying council prescriptions with no backlog
lineage at all. Nobody noticed for seven iterations, because the founder's problem was getting
solved and success masks process failure.

Two rules from that session govern this module:

* **G2 — a defect with a name and no measurement is decoration.** `no_new_correction` was
  written down, declared to stop the flow, and never measured. Detection lands before any fix.
* **G4 — every mechanism must be runnable by someone who was not there and does not trust the
  supervisor.** The supervisor authored the mechanisms, convened the council, and wrote the
  evidence the council read. `verify` and `report` answer from `state.json` alone, so the founder,
  a future assistant or CI can ask without the answer passing through anyone's narration.

The founder specified the report's contents himself (2026-09-09): the iterations, the cause of
each iteration's conclusion, whether it was failure or success, which failure when it failed, the
backlog items derived from the council's deliberation, and the new version generated and
redeployed.

Standard library only. Both commands read; neither writes.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ABSENT = "— not recorded"


def read_state(repo):
    with open(os.path.join(repo, ".risegen", "gpe-mode", "state.json")) as fh:
        return json.load(fh)


def audit_attempts(cycle):
    """One verdict per attempt, from the state file and nothing else.

    `council` and `correction_new` are the two facts nobody could establish about cycle
    gpe-8a711f9ba13b after the fact — which is precisely why they are measured here.
    """
    rows, spent = [], set()
    for a in cycle.get("attempts") or []:
        corr = a.get("correction") or {}
        commit = (corr.get("commit") or "").strip()
        council = (a.get("council") or {}).get("session_id") or ""

        breaches = []
        if not council:
            breaches.append("no_council")
        if a.get("n", 1) > 1:
            if not commit:
                breaches.append("no_correction")
            elif commit in spent:
                breaches.append("no_new_correction")
            if commit and not (corr.get("backlog_ref") or "").strip():
                breaches.append("no_backlog_lineage")
        if commit:
            spent.add(commit)

        rows.append({
            "n": a.get("n"),
            "council": council,
            "cause": a.get("cause") or "",
            "halt": a.get("halt"),
            "halt_detail": a.get("halt_detail") or "",
            "correction": commit,
            "backlog_ref": (corr.get("backlog_ref") or "").strip(),
            "redeployed": bool(corr.get("redeployed")),
            "version": (a.get("facts") or {}).get("redeploy.version") or "",
            "sha256": (a.get("facts") or {}).get("redeploy.sha256") or "",
            "acceptance": (a.get("facts") or {}).get("judge.acceptance_result") or "",
            "breaches": breaches,
        })
    return rows


def outcome_of(row, cycle_outcome, is_last):
    """How this iteration ended, in the flow's own vocabulary — never invented."""
    if row["acceptance"] == "fulfilled" or (is_last and cycle_outcome == "fulfilled"):
        return "SUCCESS"
    if row["halt"]:
        return "FAILURE"
    if row["acceptance"] == "not_fulfilled":
        return "FAILURE"
    return "FAILURE" if not is_last else "OPEN"


def render(state, cycle):
    rows = audit_attempts(cycle)
    out = []
    out.append("GEN PRODOPS ENHANCEMENT — CYCLE REPORT")
    out.append("=" * 78)
    out.append("cycle:   %s" % cycle.get("id"))
    out.append("request: %s" % (cycle.get("request") or "").strip().replace("\n", " ")[:200])
    out.append("gen:     %s" % ((state.get("gen") or {}).get("version") or ABSENT))
    out.append("outcome: %s" % (cycle.get("outcome") or "open"))
    out.append("")

    for i, r in enumerate(rows):
        last = i == len(rows) - 1
        verdict = outcome_of(r, cycle.get("outcome"), last)
        out.append("ITERATION %s — %s" % (r["n"], verdict))
        out.append("  how it ended:  %s" % (r["halt"] or (r["acceptance"] or ABSENT)))
        if verdict == "FAILURE" and r["halt_detail"]:
            out.append("  which failure: %s" % r["halt_detail"][:300])
        out.append("  cause named:   %s" % (r["cause"][:220] if r["cause"] else ABSENT))
        out.append("  council:       %s" % (r["council"] or ABSENT))
        out.append("  backlog:       %s" % (r["backlog_ref"] or ABSENT))
        out.append("  correction:    %s%s" % (r["correction"] or ABSENT,
                                              " (redeployed)" if r["redeployed"] else ""))
        out.append("  version:       %s" % (r["version"] or ABSENT))
        out.append("  sha256:        %s" % (r["sha256"] or ABSENT))
        if r["breaches"]:
            out.append("  BREACH:        %s" % ", ".join(r["breaches"]))
        out.append("")

    breached = [r for r in rows if r["breaches"]]
    out.append("-" * 78)
    out.append("iterations: %d · in breach: %d" % (len(rows), len(breached)))
    if breached:
        out.append("A cycle in breach ran iterations the rite did not authorise. The breach is "
                   "named here rather than absent, because silence is how this went unnoticed "
                   "for seven iterations on gpe-8a711f9ba13b.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--json", action="store_true", help="machine-readable audit instead of the report")
    ap.add_argument("--verify", action="store_true",
                    help="M3: exit non-zero when any iteration is in breach")
    args = ap.parse_args(argv)

    state = read_state(args.repo)
    cycles = state.get("cycles") or []
    if not cycles:
        print("no cycle in %s" % args.repo)
        return 1
    cycle = cycles[-1]
    rows = audit_attempts(cycle)

    if args.json:
        print(json.dumps({"cycle": cycle.get("id"), "attempts": rows}, indent=2))
    elif args.verify:
        for r in rows:
            print("attempt %-2s council=%-24s correction=%-10s %s" % (
                r["n"], r["council"] or "NONE", (r["correction"] or "none")[:10],
                "OUT_OF_ACCORD " + ",".join(r["breaches"]) if r["breaches"] else "IN_ACCORD"))
    else:
        print(render(state, cycle))

    return 1 if any(r["breaches"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
