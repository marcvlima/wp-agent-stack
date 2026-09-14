#!/usr/bin/env python3
"""Judge one enhancement-mode cycle STRICTLY against the request contract.

The definitions ARE the validation (founder, 2026-09-05): a phase is judged against its written
`must` facts, never against an exit code and never against an actor's own success line.

Readings, and the only ones:
    ok       the fact is there and it says the phase was honoured
    pending  the phase was not reached yet — NEVER a defect
    unknown  the phase was reached and the fact is absent — ALWAYS a defect
    defect   the fact is there and it says the phase was not honoured

Exit 0 = IN_ACCORD · 1 = OUT_OF_ACCORD (the first defect is named) · 2 = the audit itself failed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONTRACT = os.path.join(os.path.dirname(HERE), "references", "request-contract.yaml")

OK, PENDING, UNKNOWN, DEFECT = "ok", "pending", "unknown", "defect"


def load_contract(path: str) -> Dict[str, Any]:
    try:
        import yaml  # noqa: PLC0415 - optional at import time, required here
    except ImportError as exc:  # pragma: no cover - environment, not logic
        raise SystemExit("gpe_audit: PyYAML is required to read %s (%s)" % (path, exc))
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def facts_of(cycle: Dict[str, Any], attempt: Optional[Dict[str, Any]],
             state: Dict[str, Any]) -> Dict[str, Any]:
    """The facts in scope for one attempt: the arming, the cycle's own, then the attempt's."""
    merged: Dict[str, Any] = {}
    gen = state.get("gen") or {}
    if state.get("armed"):
        merged["arm.state_written"] = True
    if gen.get("version"):
        merged["arm.gen_version"] = gen["version"]
    if gen.get("sha256"):
        merged["arm.gen_sha256"] = gen["sha256"]
    if gen.get("model"):
        merged["arm.gen_model"] = gen["model"]
    merged.update(cycle.get("facts") or {})
    if attempt:
        merged.update(attempt.get("facts") or {})
    return merged


def read_fact(value: Any) -> str:
    """One fact, one reading. `false`, `"unknown"`, `null` and an empty string are never a pass."""
    if value is None or value == "":
        return UNKNOWN
    if isinstance(value, bool):
        return OK if value else DEFECT
    if isinstance(value, str) and value.strip().lower() in ("unknown", "?"):
        return UNKNOWN
    if isinstance(value, str) and value.strip().lower() in ("not_fulfilled", "false", "failed"):
        return DEFECT
    return OK


def reached(phase_slug: str, order: List[str], facts: Dict[str, Any]) -> bool:
    """A phase is reached when it, or any later phase, has recorded a fact."""
    idx = order.index(phase_slug)
    for slug in order[idx:]:
        if any(name.startswith(slug + ".") for name in facts):
            return True
    return False


def audit(state: Dict[str, Any], contract: Dict[str, Any],
          cycle_id: str = "") -> Tuple[List[Dict[str, str]], List[str]]:
    cycles = state.get("cycles") or []
    if cycle_id:
        cycles = [c for c in cycles if c.get("id") == cycle_id]
    if not cycles:
        return [], ["no_cycle"]
    cycle = cycles[-1]
    attempts = cycle.get("attempts") or []
    attempt = attempts[-1] if attempts else None
    facts = facts_of(cycle, attempt, state)

    phases = contract["phases"]
    order = [p["slug"] for p in phases]
    rows: List[Dict[str, str]] = []
    defects: List[str] = []

    for phase in phases:
        slug = phase["slug"]
        phase_reached = reached(slug, order, facts)
        for must in phase["must"]:
            name = must["name"]
            if name in facts:
                verdict = read_fact(facts[name])
            elif phase_reached:
                verdict = UNKNOWN
            else:
                verdict = PENDING
            rows.append({"phase": slug, "fact": name, "verdict": verdict,
                         "value": json.dumps(facts.get(name))})
            if verdict in (UNKNOWN, DEFECT):
                defects.append(name)

    # A halt that was named must have interrupted: a halt with no interruption fact is the
    # measured shape of "a pause file exists while the work goes on".
    if attempt and attempt.get("halt") and not facts.get("supervise.halt"):
        defects.append("supervise.halt")

    # The doctor's backlog gaps are defects by name, so the founder reads WHICH area is missing.
    doctor = (attempt or {}).get("doctor") or {}
    for area in doctor.get("lucens_backlog_gaps") or []:
        defects.append("lucens_backlog_gap:%s" % area)
    for target in doctor.get("targets_outside_gen") or []:
        defects.append("target_outside_gen:%s" % target)

    return rows, defects


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="gpe_audit.py", description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--contract", default=DEFAULT_CONTRACT)
    parser.add_argument("--cycle", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    path = os.path.join(args.repo, ".risegen", "gpe-mode", "state.json")
    if not os.path.exists(path):
        print("OUT_OF_ACCORD mode_not_armed (no %s)" % path)
        return 1
    with open(path, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    rows, defects = audit(state, load_contract(args.contract), args.cycle)

    if args.json:
        print(json.dumps({"rows": rows, "defects": defects,
                          "verdict": "IN_ACCORD" if not defects else "OUT_OF_ACCORD"},
                         indent=2, ensure_ascii=False))
    else:
        for row in rows:
            if row["verdict"] != "pending":
                print("%-10s %-38s %-8s %s" % (row["phase"], row["fact"], row["verdict"],
                                               row["value"]))
        print("IN_ACCORD" if not defects else "OUT_OF_ACCORD %s" % defects[0])
    return 0 if not defects else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
