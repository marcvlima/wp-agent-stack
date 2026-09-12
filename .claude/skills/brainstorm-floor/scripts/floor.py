#!/usr/bin/env python3
"""brainstorm-floor — the shared floor for a real discussion.

Standard library only. The host is not a seat: this CLI records the floor,
enforces the protocol, and writes the record. It never searches the web and
it never decides.

Subcommands: open, post, read, round-brief, pending, verify, close, reclose.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, TextIO, Tuple


# --------------------------------------------------------------------------- constants

PHASES = ("convene", "open", "research", "cross", "converge", "close")

HOST_VERBS = frozenset(
    {
        "facts",
        "agenda",
        "convene",
        "relay",
        "research_result",
        "protocol",
        "record",
    }
)
# Naming an absence is a protocol act (invariant 8), not a deliberation.
HOST_ALLOWED_TYPES = HOST_VERBS | frozenset({"seat_absent"})

SEAT_KINDS = frozenset({"council", "individual"})
AUTHOR_KINDS = frozenset({"council", "individual", "host"})

LUCENS_ABSENCES = frozenset(
    {
        "lucens_unreachable",
        "lucens_unauthorized",
        "lucens_busy",
        "lucens_floor_silent",
        "lucens_wait_exhausted",
    }
)
LUCENS_IDS = frozenset({"lucens", "lucens.risegen.ai"})

SEAT_DELIBERATIVE = frozenset(
    {
        "position",
        "proposal",
        "research_request",
        "question",
        "concede",
        "refine",
        "hold",
        "support",
        "objection",
        "decision",
    }
)

TYPE_PHASE = {
    "facts": "convene",
    "agenda": "convene",
    "convene": "convene",
    "position": "open",
    "proposal": "open",
    "research_result": "research",
    "concede": "cross",
    "refine": "cross",
    "hold": "cross",
    "support": "converge",
    "objection": "converge",
    "decision": "close",
    "record": "close",
}

OUTCOMES = ("consensus", "consensus_with_dissent", "no_convergence")

ENTRY_KEYS = (
    "seq",
    "ts",
    "round",
    "phase",
    "author",
    "author_kind",
    "type",
    "body",
    "addressed_to",
    "answers",
    "requested_by",
    "refs",
)

RECORD_HEADINGS = (
    "# Brainstorm —",
    "## Failure card",
    "## Seats",
    "## Root cause (the chain, not the symptom)",
    "## Candidate solutions × impacts on the rest of the flow",
    "## Decision",
)

D31_SEAT_LABELS = {
    "architecture-council": "architecture (architecture-council)",
    "ai-ml-implementation-council": "AI/ML (ai-ml-implementation-council)",
    "agentic-development-council": "code assistant (agentic-development-council)",
    "lucens": "Lucens (her A2A, task id, cycles, tokens)",
    "lucens.risegen.ai": "Lucens (her A2A, task id, cycles, tokens)",
}

FACTS_FILE = "facts.md"
FLOOR_FILE = "floor.jsonl"
RECORD_FILE = "record.md"
SESSION_FILE = "session.json"

V_HOST_VERB = "host_verb_violation"
V_HOST_RESEARCH = "host_research_request"
V_RESULT_NO_REQUESTER = "research_result_missing_requested_by"
V_RESULT_NOT_SEAT = "research_result_requested_by_not_a_seat"
V_HOST_DECISION = "host_authored_decision"
V_DECISION_NO_CITES = "decision_missing_seat_citations"
V_HOST_CALL = "host_call_without_convergence"
V_MISSING_ESCALATION = "missing_escalation"
V_UNANSWERED_Q = "unanswered_question"
V_INSUFFICIENT_CROSS = "insufficient_cross_rounds"
V_UNSHARED = "unshared_manifestation"
V_SEQ_GAP = "seq_gap"
V_UNNAMED_ABSENCE = "unnamed_absence"
V_LUCENS_ABSENCE = "lucens_absence_unnamed"
V_FABRICATED = "fabricated_seat"
V_OUTCOME_MISMATCH = "outcome_mismatch"
V_UNANSWERED_OBJECTION = "unanswered_objection"

CHOSEN_NO_DECISION = "(no seat authored a decision entry)"
NO_PROPOSAL_NOTE = (
    "(no proposal entries on this floor - see the seats' positions)"
)


class ProtocolError(Exception):
    """A named protocol violation raised at the gate (post/open/close)."""

    def __init__(self, name: str, detail: str = "") -> None:
        self.name = name
        self.detail = detail
        msg = f"{name}: {detail}" if detail else name
        super().__init__(msg)


# --------------------------------------------------------------------------- time / paths


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def session_paths(session_dir: str | Path) -> Dict[str, Path]:
    root = Path(session_dir)
    return {
        "root": root,
        "facts": root / FACTS_FILE,
        "floor": root / FLOOR_FILE,
        "record": root / RECORD_FILE,
        "session": root / SESSION_FILE,
    }


# --------------------------------------------------------------------------- jsonl io


def _dumps(entry: Dict[str, Any]) -> str:
    ordered = {k: entry[k] for k in ENTRY_KEYS}
    return json.dumps(ordered, ensure_ascii=False, separators=(",", ":"))


def load_floor_text(session_dir: str | Path) -> str:
    path = session_paths(session_dir)["floor"]
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def load_entries(session_dir: str | Path) -> List[Dict[str, Any]]:
    text = load_floor_text(session_dir)
    entries: List[Dict[str, Any]] = []
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        entries.append(json.loads(raw))
    return entries


def append_entry(session_dir: str | Path, entry: Dict[str, Any]) -> Dict[str, Any]:
    paths = session_paths(session_dir)
    paths["root"].mkdir(parents=True, exist_ok=True)
    line = _dumps(entry) + "\n"
    with paths["floor"].open("a", encoding="utf-8") as fh:
        fh.write(line)
    return entry


def load_session_meta(session_dir: str | Path) -> Dict[str, Any]:
    path = session_paths(session_dir)["session"]
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    entries = load_entries(session_dir)
    for e in entries:
        if e.get("type") == "convene":
            body = e.get("body") or "{}"
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {}
            if isinstance(parsed, dict) and parsed.get("seats"):
                return {
                    "topic": parsed.get("topic") or "",
                    "seats": parsed["seats"],
                    "closed": False,
                    "outcome": None,
                }
    return {"topic": "", "seats": [], "closed": False, "outcome": None}


def save_session_meta(session_dir: str | Path, meta: Dict[str, Any]) -> None:
    path = session_paths(session_dir)["session"]
    path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def roster_of(session_dir: str | Path) -> List[Dict[str, str]]:
    meta = load_session_meta(session_dir)
    return list(meta.get("seats") or [])


def seat_ids_of(roster: Sequence[Dict[str, str]]) -> List[str]:
    return [s["id"] for s in roster]


def is_lucens(seat_id: str) -> bool:
    return (seat_id or "").strip().lower() in LUCENS_IDS


def is_host(author: str, author_kind: str = "") -> bool:
    return author == "host" or author_kind == "host"


# --------------------------------------------------------------------------- round brief (invariant 1)


def round_brief(floor_text: str, round_n: int) -> List[str]:
    """Return the complete floor through round N-1, verbatim.

    Pure function of ``floor.jsonl`` text and the round number. Does not
    take a seat id and does not filter by author. Every seat's round-N
    brief is this list of jsonl lines, in file order.
    """
    out: List[str] = []
    n = int(round_n)
    for line in floor_text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        entry = json.loads(raw)
        if int(entry["round"]) < n:
            out.append(raw)
    return out


# --------------------------------------------------------------------------- pending / presence


def _answered_seqs(entries: Sequence[Dict[str, Any]]) -> set:
    answered = set()
    for e in entries:
        for a in e.get("answers") or []:
            answered.add(int(a))
    return answered


def absent_seat_ids(entries: Sequence[Dict[str, Any]]) -> set:
    absent = set()
    for e in entries:
        if e.get("type") == "seat_absent":
            for s in e.get("addressed_to") or []:
                if s:
                    absent.add(s)
    return absent


def present_seat_ids(
    roster: Sequence[Dict[str, str]], entries: Sequence[Dict[str, Any]]
) -> List[str]:
    absent = absent_seat_ids(entries)
    return [s["id"] for s in roster if s["id"] not in absent]


def unanswered_questions(
    entries: Sequence[Dict[str, Any]], present: Sequence[str]
) -> List[Dict[str, Any]]:
    answered = _answered_seqs(entries)
    present_set = set(present)
    out = []
    for e in entries:
        if e.get("type") != "question":
            continue
        if int(e["seq"]) in answered:
            continue
        addressees = [a for a in (e.get("addressed_to") or []) if a in present_set]
        if addressees:
            out.append(e)
    return out


def open_research(entries: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    answered = _answered_seqs(entries)
    return [
        e
        for e in entries
        if e.get("type") == "research_request" and int(e["seq"]) not in answered
    ]


def pending_payload(session_dir: str | Path) -> Dict[str, Any]:
    entries = load_entries(session_dir)
    roster = roster_of(session_dir)
    present = present_seat_ids(roster, entries)
    questions = unanswered_questions(entries, present)
    research = open_research(entries)

    def slim(e: Dict[str, Any], extra: Tuple[str, ...] = ()) -> Dict[str, Any]:
        keys = ("seq", "author", "round", "body") + extra
        return {k: e.get(k) for k in keys}

    return {
        "unanswered_questions": [
            slim(q, ("addressed_to",)) for q in questions
        ],
        "open_research": [slim(r) for r in research],
    }


def cross_round_numbers(entries: Sequence[Dict[str, Any]]) -> List[int]:
    return sorted({int(e["round"]) for e in entries if e.get("phase") == "cross"})


def unanswered_objections(
    entries: Sequence[Dict[str, Any]], present: Sequence[str]
) -> List[Dict[str, Any]]:
    cited = _answered_seqs(entries)
    present_set = set(present)
    return [
        e
        for e in entries
        if e.get("type") == "objection"
        and e.get("author") in present_set
        and int(e["seq"]) not in cited
    ]


# --------------------------------------------------------------------------- verify (all invariants)


def _named_reason_in_body(body: str) -> Optional[str]:
    """A named absence reason is a slug of [a-z0-9_]+ in the body."""
    text = (body or "").strip()
    if not text:
        return None
    for name in LUCENS_ABSENCES:
        if re.search(rf"(^|\s){re.escape(name)}(\s|$)", text):
            return name
    m = re.search(r"\b([a-z][a-z0-9_]{1,63})\b", text)
    return m.group(1) if m else None


def verify_entries(
    entries: Sequence[Dict[str, Any]],
    roster: Sequence[Dict[str, str]],
    outcome: Optional[str] = None,
    closed: bool = False,
) -> List[Tuple[str, str]]:
    """Return a list of (violation_name, detail) for the floor."""
    violations: List[Tuple[str, str]] = []
    seat_id_set = set(seat_ids_of(roster))
    present = present_seat_ids(roster, entries)

    # seq consecutive and rounds non-decreasing in seq order (invariant 2)
    expected = 1
    last_round: Optional[int] = None
    for e in entries:
        seq = int(e.get("seq") or 0)
        if seq != expected:
            violations.append(
                (V_SEQ_GAP, f"seq={seq} expected={expected}")
            )
        expected = seq + 1
        rnd = int(e.get("round") or 0)
        if last_round is not None and rnd < last_round:
            violations.append(
                (
                    V_UNSHARED,
                    f"seq={seq} round={rnd} lands after round {last_round} "
                    "already opened",
                )
            )
        if last_round is None or rnd > last_round:
            last_round = rnd if last_round is None else max(last_round, rnd)
        else:
            last_round = max(last_round, rnd)

    # host fence (5), research (4), decision (6), absences (8)
    for e in entries:
        author = e.get("author") or ""
        kind = e.get("author_kind") or ""
        typ = e.get("type") or ""
        seq = e.get("seq")
        host = is_host(author, kind)

        if host and typ not in HOST_ALLOWED_TYPES:
            violations.append(
                (V_HOST_VERB, f"seq={seq} host type={typ}")
            )
        if host and typ == "decision":
            violations.append(
                (V_HOST_DECISION, f"seq={seq} host authored a decision")
            )
        if typ == "research_request" and host:
            violations.append(
                (V_HOST_RESEARCH, f"seq={seq} research_request authored by host")
            )
        if typ == "research_result":
            rb = (e.get("requested_by") or "").strip()
            if not rb:
                violations.append(
                    (V_RESULT_NO_REQUESTER, f"seq={seq} research_result has no requested_by")
                )
            elif rb == "host" or rb not in seat_id_set:
                violations.append(
                    (
                        V_RESULT_NOT_SEAT,
                        f"seq={seq} requested_by={rb!r} is not a seat",
                    )
                )
        if typ == "decision" and not host:
            cites = [int(x) for x in (e.get("refs") or []) + (e.get("answers") or [])]
            seat_seqs = {
                int(x["seq"])
                for x in entries
                if x.get("author_kind") in ("council", "individual")
            }
            if not any(c in seat_seqs for c in cites):
                violations.append(
                    (V_DECISION_NO_CITES, f"seq={seq} decision cites no seat entries")
                )
        if typ == "seat_absent":
            addressees = [a for a in (e.get("addressed_to") or []) if a]
            if not addressees:
                violations.append(
                    (V_UNNAMED_ABSENCE, f"seq={seq} seat_absent carries no seat id")
                )
            reason = _named_reason_in_body(e.get("body") or "")
            if not reason:
                violations.append(
                    (V_UNNAMED_ABSENCE, f"seq={seq} seat_absent carries no named reason")
                )
            for sid in addressees:
                if is_lucens(sid):
                    if not any(
                        re.search(
                            rf"(^|\s){re.escape(name)}(\s|$)", e.get("body") or ""
                        )
                        for name in LUCENS_ABSENCES
                    ):
                        violations.append(
                            (
                                V_LUCENS_ABSENCE,
                                f"seq={seq} lucens absence is not a contract name",
                            )
                        )

    # fabricated seat: deliberative manifestation after seat_absent (invariant 8)
    absent_at: Dict[str, int] = {}
    for e in entries:
        if e.get("type") == "seat_absent":
            for s in e.get("addressed_to") or []:
                absent_at[s] = int(e["seq"])
        author = e.get("author") or ""
        if (
            author in absent_at
            and int(e["seq"]) > absent_at[author]
            and (e.get("type") in SEAT_DELIBERATIVE)
        ):
            violations.append(
                (
                    V_FABRICATED,
                    f"seq={e.get('seq')} author={author} spoke after seat_absent",
                )
            )

    # unanswered questions in closed rounds (invariant 3)
    max_round = max((int(e["round"]) for e in entries), default=-1)
    session_is_closed = closed or any(
        e.get("type") == "record" or e.get("phase") == "close" for e in entries
    )
    for q in unanswered_questions(entries, present):
        q_round = int(q["round"])
        later = q_round < max_round or session_is_closed
        if later:
            who = ",".join(q.get("addressed_to") or [])
            violations.append(
                (
                    V_UNANSWERED_Q,
                    f"seq={q.get('seq')} addressed to {who} (present) "
                    f"when round {q_round} closed",
                )
            )

    # min 2 cross rounds before converge/close (invariant 7)
    n_cross = len(cross_round_numbers(entries))
    has_converge = any(e.get("phase") == "converge" for e in entries)
    has_close = any(
        e.get("phase") == "close" or e.get("type") in ("record", "decision")
        for e in entries
    )
    if (has_converge or has_close) and n_cross < 2:
        violations.append(
            (
                V_INSUFFICIENT_CROSS,
                f"cross rounds={n_cross} (minimum 2) before converge/close",
            )
        )

    # objections must be answered before consensus (converge protocol)
    if has_converge or has_close or session_is_closed:
        for obj in unanswered_objections(entries, present):
            if (outcome or "") == "consensus" or session_is_closed and outcome == "consensus":
                violations.append(
                    (
                        V_UNANSWERED_OBJECTION,
                        f"seq={obj.get('seq')} objection unanswered before consensus",
                    )
                )

    # close / outcome (invariant 6)
    record_entries = [e for e in entries if e.get("type") == "record"]
    decision_entries = [e for e in entries if e.get("type") == "decision"]
    effective_outcome = outcome
    if effective_outcome is None and record_entries:
        body = record_entries[-1].get("body") or ""
        if re.search(r"\bno_convergence\b", body):
            effective_outcome = "no_convergence"
        elif re.search(r"\bconsensus_with_dissent\b", body):
            effective_outcome = "consensus_with_dissent"
        elif re.search(r"\bconsensus\b", body):
            effective_outcome = "consensus"

    if effective_outcome == "no_convergence":
        bodies = " ".join(e.get("body") or "" for e in record_entries)
        if record_entries and not re.search(r"\bescalated_to_ratifier\b", bodies):
            violations.append(
                (V_MISSING_ESCALATION, "no_convergence close lacks escalated_to_ratifier")
            )
        host_decisions = [
            e for e in decision_entries if is_host(e.get("author") or "", e.get("author_kind") or "")
        ]
        if host_decisions:
            violations.append(
                (
                    V_HOST_CALL,
                    "no_convergence close contains a host decision",
                )
            )
        # a chosen option under no_convergence is a host call
        if record_entries and re.search(
            r"chosen:\s*(?!none\b)(?!n/a\b)\S", bodies, re.I
        ):
            violations.append(
                (V_HOST_CALL, "no_convergence close records a chosen option")
            )

    derived = derive_outcome(entries, roster)
    if outcome_contradicts_derived(effective_outcome, derived):
        violations.append(
            (
                V_OUTCOME_MISMATCH,
                f"recorded {effective_outcome} but seats yield {derived}",
            )
        )

    if effective_outcome in ("consensus", "consensus_with_dissent"):
        supports = [
            e
            for e in entries
            if e.get("type") == "support"
            and e.get("author_kind") in ("council", "individual")
        ]
        if not supports:
            violations.append(
                (
                    V_HOST_DECISION,
                    f"{effective_outcome} recorded with no seat support entries",
                )
            )

    if effective_outcome == "consensus_with_dissent":
        objectors = [
            e.get("author")
            for e in entries
            if e.get("type") == "objection" and e.get("author") in set(present)
        ]
        if not objectors:
            violations.append(
                (
                    V_OUTCOME_MISMATCH,
                    "consensus_with_dissent recorded with no named objector",
                )
            )

    return violations


def derive_outcome(
    entries: Sequence[Dict[str, Any]], roster: Sequence[Dict[str, str]]
) -> Optional[str]:
    """Derive close outcome from seat support/objection. None if not yet converge."""
    if not any(e.get("phase") == "converge" for e in entries):
        return None
    present = set(present_seat_ids(roster, entries))
    if not present:
        return "no_convergence"
    supporters = {
        e.get("author")
        for e in entries
        if e.get("type") == "support" and e.get("author") in present
    }
    objectors = {
        e.get("author")
        for e in entries
        if e.get("type") == "objection" and e.get("author") in present
    }
    hanging = unanswered_objections(entries, list(present))
    if hanging:
        return "no_convergence"
    if present <= supporters and not objectors:
        return "consensus"
    if supporters and objectors:
        return "consensus_with_dissent"
    if present <= supporters:
        return "consensus"
    return "no_convergence"


def outcome_contradicts_derived(
    requested: Optional[str], derived: Optional[str]
) -> bool:
    """True when a stated outcome disagrees with what the seats yield.

    ``derived is None`` means the floor has not reached converge, so only
    ``no_convergence`` is acceptable as a close; a consensus claim is a
    contradiction. Used by both ``close``/``reclose`` and ``verify``.
    """
    if not requested:
        return False
    if derived == requested:
        return False
    if derived is None and requested == "no_convergence":
        return False
    return True


def assert_outcome_matches_derived(
    entries: Sequence[Dict[str, Any]],
    roster: Sequence[Dict[str, str]],
    requested: str,
) -> Optional[str]:
    """Return the derived outcome, or raise if ``requested`` contradicts it.

    A close that cannot pass ``verify`` must not happen: this is the gate.
    """
    derived = derive_outcome(entries, roster)
    if outcome_contradicts_derived(requested, derived):
        raise ProtocolError(
            V_OUTCOME_MISMATCH,
            f"requested {requested} but seats yield {derived}",
        )
    return derived


def verify_dir(session_dir: str | Path) -> List[Tuple[str, str]]:
    entries = load_entries(session_dir)
    meta = load_session_meta(session_dir)
    roster = list(meta.get("seats") or [])
    return verify_entries(
        entries,
        roster,
        outcome=meta.get("outcome"),
        closed=bool(meta.get("closed")),
    )


# --------------------------------------------------------------------------- record


def _first_line(text: str, default: str = "") -> str:
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return default


def _grab_bullet(text: str, prefixes: Sequence[str]) -> Optional[str]:
    for line in (text or "").splitlines():
        s = line.strip()
        for p in prefixes:
            if s.lower().startswith(p.lower()):
                return s.split(":", 1)[-1].strip() if ":" in s else s
    return None


def _seat_label(seat: Dict[str, str]) -> str:
    sid = seat["id"]
    if sid in D31_SEAT_LABELS:
        return D31_SEAT_LABELS[sid]
    return f"{sid} ({seat.get('kind') or 'seat'})"


def _seat_summary(seat: Dict[str, str], entries: Sequence[Dict[str, Any]]) -> str:
    sid = seat["id"]
    absences = [
        e
        for e in entries
        if e.get("type") == "seat_absent" and sid in (e.get("addressed_to") or [])
    ]
    if absences:
        reason = _named_reason_in_body(absences[-1].get("body") or "") or (
            absences[-1].get("body") or ""
        ).strip()
        if is_lucens(sid):
            return reason
        return f"absent: {reason}"
    interesting = [
        e
        for e in entries
        if e.get("author") == sid
        and e.get("type")
        in ("position", "refine", "hold", "concede", "support", "objection")
    ]
    if not interesting:
        return "(no manifestation)"
    last = interesting[-1]
    body = (last.get("body") or "").strip().replace("\n", " ")
    if len(body) > 400:
        body = body[:397] + "..."
    return f"[{last.get('type')}] {body}" if body else f"[{last.get('type')}]"


def _proposal_rows(
    entries: Sequence[Dict[str, Any]],
) -> List[Tuple[Dict[str, Any], str]]:
    """Candidate-table rows from ``proposal`` entries only. Never first lines of arbitrary prose."""
    rows: List[Tuple[Dict[str, Any], str]] = []
    for e in entries:
        if e.get("type") != "proposal":
            continue
        if e.get("author_kind") not in ("council", "individual"):
            continue
        line = _first_line(e.get("body") or "")
        if line:
            rows.append((e, line))
    return rows


def _side_list(entries: Sequence[Dict[str, Any]], typ: str) -> str:
    items = [
        e
        for e in entries
        if e.get("type") == typ
        and e.get("author_kind") in ("council", "individual")
    ]
    if not items:
        return "none"
    return ", ".join(f"{e.get('author')} (seq {e.get('seq')})" for e in items)


def _seat_decision_entries(
    entries: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return [
        e
        for e in entries
        if e.get("type") == "decision"
        and e.get("author_kind") in ("council", "individual")
        and not is_host(e.get("author") or "", e.get("author_kind") or "")
    ]


def _chosen_value(entries: Sequence[Dict[str, Any]], outcome: str) -> str:
    """Named decision from a seat ``decision`` entry, or an explicit none.

    Never taken from a support/position/refine body's first line.
    """
    if outcome == "no_convergence":
        return "none"
    decisions = _seat_decision_entries(entries)
    if not decisions:
        return CHOSEN_NO_DECISION
    parts: List[str] = []
    for d in decisions:
        body = (d.get("body") or "").strip().replace("\n", " ")
        if len(body) > 240:
            body = body[:237] + "..."
        if body:
            parts.append(f"seq {d['seq']} by {d['author']}: {body}")
        else:
            parts.append(f"seq {d['seq']} by {d['author']}")
    return "; ".join(parts)


def render_record(
    topic: str,
    ts: str,
    facts_text: str,
    roster: Sequence[Dict[str, str]],
    entries: Sequence[Dict[str, Any]],
    outcome: str,
) -> str:
    facts_text = facts_text or ""
    fact = _grab_bullet(
        facts_text, ("- fact (verbatim from the artifact)", "- fact")
    ) or (
        _first_line(facts_text, "n/a — not a D31 failure; see facts.md")
        if facts_text.strip()
        else "n/a — not a D31 failure; see facts.md"
    )
    step = (
        _grab_bullet(facts_text, ("- step / node / actor", "- step")) or "n/a"
    )
    seen = (
        _grab_bullet(
            facts_text, ("- first seen / recurrences (family)", "- first seen")
        )
        or "n/a"
    )

    lines: List[str] = []
    lines.append(f"# Brainstorm — {topic} · {ts}")
    lines.append("")
    lines.append("## Failure card")
    lines.append(f"- fact (verbatim from the artifact): {fact}")
    lines.append(f"- step / node / actor: {step}")
    lines.append(f"- first seen / recurrences (family): {seen}")
    lines.append("")
    lines.append("## Seats")
    for seat in roster:
        lines.append(f"- {_seat_label(seat)}: {_seat_summary(seat, entries)}")
    lines.append("")
    lines.append("## Root cause (the chain, not the symptom)")
    root_block = _extract_named_block(facts_text, "root cause")
    if root_block:
        lines.append(root_block.rstrip())
    else:
        lines.append("1. producer: n/a — not supplied as a D31 chain; see Seats and facts.md")
        lines.append("2. reader(s): n/a")
        lines.append("3. divergence: n/a")
        lines.append("4. why it was not caught: n/a")
    lines.append("")
    lines.append("## Candidate solutions × impacts on the rest of the flow")
    lines.append(
        "| # | solution | steps/nodes/readers/actors touched (D25) | "
        "cost to the iteration | resilience | fluidity | speed |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    proposal_rows = _proposal_rows(entries)
    if proposal_rows:
        for i, (entry, solution) in enumerate(proposal_rows, 1):
            cell = (
                f"seq {entry['seq']} ({entry.get('author')}): {solution}"
            ).replace("|", "/")
            lines.append(f"| {i} | {cell} | n/a | n/a | n/a | n/a | n/a |")
    else:
        lines.append(NO_PROPOSAL_NOTE)
    lines.append("")
    lines.append("## Decision")
    objections = [
        e
        for e in entries
        if e.get("type") == "objection"
        and e.get("author_kind") in ("council", "individual")
    ]
    dissenters = ", ".join(
        f"{e.get('author')} (seq {e.get('seq')})" for e in objections
    ) or "none"
    chosen = _chosen_value(entries, outcome)
    supporting = _side_list(entries, "support")
    objecting = _side_list(entries, "objection")
    lines.append(f"- chosen: {chosen}")
    lines.append(f"- supporting: {supporting}")
    lines.append(f"- objecting: {objecting}")
    if outcome == "no_convergence":
        lines.append(f"- named dissent: {dissenters}")
        lines.append("- outcome: no_convergence")
        lines.append("- escalated_to_ratifier: yes")
    elif outcome == "consensus_with_dissent":
        lines.append(f"- named dissent: {dissenters}")
        lines.append("- outcome: consensus_with_dissent")
        lines.append("- escalated_to_ratifier: no")
    else:
        lines.append(
            "- named dissent: none"
            if dissenters == "none"
            else f"- named dissent: {dissenters}"
        )
        lines.append("- outcome: consensus")
        lines.append("- escalated_to_ratifier: no")
    lines.append("- rows: n/a")
    lines.append("- measured after landing: n/a")
    lines.append("")
    return "\n".join(lines)


def _extract_named_block(text: str, heading_needle: str) -> str:
    needle = heading_needle.lower()
    capture: List[str] = []
    on = False
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") and needle in stripped.lower():
            on = True
            continue
        if on and stripped.startswith("#"):
            break
        if on:
            capture.append(line)
    return "\n".join(capture).strip()


# --------------------------------------------------------------------------- post gate


def infer_phase(
    typ: str, entries: Sequence[Dict[str, Any]], explicit: Optional[str]
) -> str:
    if explicit:
        if explicit not in PHASES:
            raise ProtocolError("unknown_phase", explicit)
        return explicit
    if typ in TYPE_PHASE:
        return TYPE_PHASE[typ]
    if not entries:
        return "convene"
    last = entries[-1].get("phase") or "convene"
    if last == "convene":
        return "open"
    return last


def author_kind_of(author: str, roster: Sequence[Dict[str, str]]) -> str:
    if author == "host":
        return "host"
    for s in roster:
        if s["id"] == author:
            kind = s.get("kind") or ""
            if kind not in SEAT_KINDS:
                raise ProtocolError("unknown_kind", kind)
            return kind
    raise ProtocolError("unknown_author", author)


def gate_post(
    *,
    author: str,
    author_kind: str,
    typ: str,
    phase: str,
    round_n: int,
    body: str,
    addressed_to: Sequence[str],
    answers: Sequence[int],
    requested_by: str,
    refs: Sequence[int],
    entries: Sequence[Dict[str, Any]],
    roster: Sequence[Dict[str, str]],
    closed: bool,
) -> None:
    if closed:
        raise ProtocolError("session_closed", "the floor is already closed")
    if phase not in PHASES:
        raise ProtocolError("unknown_phase", phase)
    host = is_host(author, author_kind)
    seat_id_set = set(seat_ids_of(roster))

    if typ == "research_request" and host:
        raise ProtocolError(V_HOST_RESEARCH, "research_request authored by host")
    if host and typ == "decision":
        raise ProtocolError(V_HOST_DECISION, "host may not author a decision")
    if host and typ not in HOST_ALLOWED_TYPES:
        raise ProtocolError(V_HOST_VERB, f"host type={typ}")
    if typ == "research_result":
        rb = (requested_by or "").strip()
        if not rb:
            raise ProtocolError(
                V_RESULT_NO_REQUESTER, "research_result requires --requested-by a seat"
            )
        if rb == "host" or rb not in seat_id_set:
            raise ProtocolError(V_RESULT_NOT_SEAT, f"requested_by={rb!r} is not a seat")
    if typ == "question" and not [a for a in addressed_to if a]:
        raise ProtocolError("question_unaddressed", "question requires --addressed-to")
    if typ == "seat_absent":
        if not [a for a in addressed_to if a]:
            raise ProtocolError(V_UNNAMED_ABSENCE, "seat_absent requires --addressed-to")
        if not _named_reason_in_body(body):
            raise ProtocolError(V_UNNAMED_ABSENCE, "seat_absent requires a named reason")
        for sid in addressed_to:
            if is_lucens(sid) and not any(
                re.search(rf"(^|\s){re.escape(name)}(\s|$)", body or "")
                for name in LUCENS_ABSENCES
            ):
                raise ProtocolError(
                    V_LUCENS_ABSENCE, "lucens absence must be a contract name"
                )
    if typ == "decision":
        if host:
            raise ProtocolError(V_HOST_DECISION, "host may not author a decision")
        cites = list(refs) + list(answers)
        seat_seqs = {
            int(e["seq"])
            for e in entries
            if e.get("author_kind") in ("council", "individual")
        }
        if not any(int(c) in seat_seqs for c in cites):
            raise ProtocolError(
                V_DECISION_NO_CITES, "decision must cite seat entries by seq"
            )

    if phase == "converge" or typ in ("support", "objection"):
        if len(cross_round_numbers(entries)) < 2:
            raise ProtocolError(
                V_INSUFFICIENT_CROSS, "minimum 2 cross rounds before converge"
            )

    # a new round may not open while a previous round has hanging questions
    if entries:
        max_round = max(int(e["round"]) for e in entries)
        if int(round_n) > max_round:
            present = present_seat_ids(roster, entries)
            hanging = unanswered_questions(entries, present)
            if hanging:
                q = hanging[0]
                raise ProtocolError(
                    V_UNANSWERED_Q,
                    f"seq={q.get('seq')} still unanswered; cannot open round {round_n}",
                )


def make_entry(
    *,
    seq: int,
    ts: str,
    round_n: int,
    phase: str,
    author: str,
    author_kind: str,
    typ: str,
    body: str,
    addressed_to: Sequence[str],
    answers: Sequence[int],
    requested_by: str,
    refs: Sequence[int],
) -> Dict[str, Any]:
    return {
        "seq": int(seq),
        "ts": ts,
        "round": int(round_n),
        "phase": phase,
        "author": author,
        "author_kind": author_kind,
        "type": typ,
        "body": body if body is not None else "",
        "addressed_to": [a for a in addressed_to if a],
        "answers": [int(a) for a in answers],
        "requested_by": requested_by or "",
        "refs": [int(a) for a in refs],
    }


# --------------------------------------------------------------------------- commands


def parse_seat(spec: str) -> Dict[str, str]:
    if ":" not in spec:
        raise ProtocolError("bad_seat", f"expected id:kind, got {spec!r}")
    sid, kind = spec.rsplit(":", 1)
    sid, kind = sid.strip(), kind.strip()
    if not sid or kind not in SEAT_KINDS:
        raise ProtocolError("bad_seat", f"expected id:council|individual, got {spec!r}")
    return {"id": sid, "kind": kind}


def parse_int_list(values: Optional[Sequence[str]]) -> List[int]:
    out: List[int] = []
    for v in values or []:
        for part in str(v).split(","):
            part = part.strip()
            if part:
                out.append(int(part))
    return out


def parse_str_list(values: Optional[Sequence[str]]) -> List[str]:
    out: List[str] = []
    for v in values or []:
        for part in str(v).split(","):
            part = part.strip()
            if part:
                out.append(part)
    return out


def cmd_open(args: argparse.Namespace, stdout: TextIO, stderr: TextIO) -> int:
    seats = [parse_seat(s) for s in args.seat]
    seen = set()
    for s in seats:
        if s["id"] in seen:
            raise ProtocolError("duplicate_seat", s["id"])
        seen.add(s["id"])
    if not seats:
        raise ProtocolError("no_seats", "open requires at least one --seat id:kind")
    facts_src = Path(args.facts)
    if not facts_src.is_file():
        raise ProtocolError("missing_facts", str(facts_src))
    facts_text = facts_src.read_text(encoding="utf-8")
    paths = session_paths(args.dir)
    if paths["floor"].exists() and paths["floor"].read_text(encoding="utf-8").strip():
        raise ProtocolError("already_open", str(paths["root"]))
    paths["root"].mkdir(parents=True, exist_ok=True)
    paths["facts"].write_text(facts_text, encoding="utf-8")
    ts = now_utc()
    topic = args.topic
    meta = {
        "topic": topic,
        "seats": seats,
        "opened_at": ts,
        "closed": False,
        "outcome": None,
    }
    save_session_meta(args.dir, meta)
    convene_body = json.dumps({"topic": topic, "seats": seats}, ensure_ascii=False)
    agenda_body = (
        f"Topic: {topic}\n\n"
        "The host holds no position, ranks nothing, breaks no tie, and will not "
        "decide. Only seats deliberate. Research is seat-asked. Without "
        "convergence this floor escalates to the ratifier.\n\n"
        "Seats: " + ", ".join(f"{s['id']} ({s['kind']})" for s in seats)
    )
    seq = 1
    for typ, body in (
        ("facts", facts_text),
        ("agenda", agenda_body),
        ("convene", convene_body),
    ):
        append_entry(
            args.dir,
            make_entry(
                seq=seq,
                ts=ts,
                round_n=0,
                phase="convene",
                author="host",
                author_kind="host",
                typ=typ,
                body=body,
                addressed_to=[],
                answers=[],
                requested_by="",
                refs=[],
            ),
        )
        seq += 1
    stdout.write(f"opened {paths['root']} seats={len(seats)} topic={topic!r}\n")
    return 0


def cmd_post(args: argparse.Namespace, stdout: TextIO, stderr: TextIO) -> int:
    body_path = Path(args.body_file)
    if not body_path.is_file():
        raise ProtocolError("missing_body", str(body_path))
    body = body_path.read_text(encoding="utf-8")
    entries = load_entries(args.dir)
    meta = load_session_meta(args.dir)
    roster = list(meta.get("seats") or [])
    if not roster:
        raise ProtocolError("not_open", "no roster; run open first")
    author = args.author
    kind = author_kind_of(author, roster)
    typ = args.type
    phase = infer_phase(typ, entries, args.phase)
    addressed_to = parse_str_list(args.addressed_to)
    answers = parse_int_list(args.answers)
    refs = parse_int_list(args.refs)
    requested_by = args.requested_by or ""
    gate_post(
        author=author,
        author_kind=kind,
        typ=typ,
        phase=phase,
        round_n=int(args.round),
        body=body,
        addressed_to=addressed_to,
        answers=answers,
        requested_by=requested_by,
        refs=refs,
        entries=entries,
        roster=roster,
        closed=bool(meta.get("closed")),
    )
    entry = make_entry(
        seq=len(entries) + 1,
        ts=now_utc(),
        round_n=int(args.round),
        phase=phase,
        author=author,
        author_kind=kind,
        typ=typ,
        body=body,
        addressed_to=addressed_to,
        answers=answers,
        requested_by=requested_by,
        refs=refs,
    )
    append_entry(args.dir, entry)
    stdout.write(
        f"posted seq={entry['seq']} author={author} type={typ} "
        f"round={entry['round']} phase={phase}\n"
    )
    return 0


def cmd_read(args: argparse.Namespace, stdout: TextIO, stderr: TextIO) -> int:
    entries = load_entries(args.dir)
    if args.round is not None:
        entries = [e for e in entries if int(e["round"]) == int(args.round)]
    if args.json:
        stdout.write(json.dumps(entries, ensure_ascii=False, indent=2) + "\n")
        return 0
    for e in entries:
        stdout.write(
            f"#seq={e['seq']} round={e['round']} phase={e['phase']} "
            f"author={e['author']} kind={e['author_kind']} type={e['type']}\n"
        )
        stdout.write((e.get("body") or "") + "\n")
    return 0


def cmd_round_brief(args: argparse.Namespace, stdout: TextIO, stderr: TextIO) -> int:
    text = load_floor_text(args.dir)
    lines = round_brief(text, int(args.round))
    if lines:
        stdout.write("\n".join(lines) + "\n")
    return 0


def cmd_pending(args: argparse.Namespace, stdout: TextIO, stderr: TextIO) -> int:
    payload = pending_payload(args.dir)
    stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return 0


def cmd_verify(args: argparse.Namespace, stdout: TextIO, stderr: TextIO) -> int:
    violations = verify_dir(args.dir)
    if not violations:
        stdout.write("OK\n")
        return 0
    for name, detail in violations:
        stdout.write(f"VIOLATION {name}: {detail}\n")
    return 1


def _close_protocol_gates(
    entries: Sequence[Dict[str, Any]],
    roster: Sequence[Dict[str, str]],
    outcome: str,
) -> Optional[str]:
    """Refuse a close that cannot pass verify. Writes nothing."""
    if outcome not in OUTCOMES:
        raise ProtocolError("bad_outcome", outcome)
    if len(cross_round_numbers(entries)) < 2:
        raise ProtocolError(
            V_INSUFFICIENT_CROSS, "minimum 2 cross rounds before close"
        )
    present = present_seat_ids(roster, entries)
    hanging_q = unanswered_questions(entries, present)
    if hanging_q:
        q = hanging_q[0]
        raise ProtocolError(
            V_UNANSWERED_Q, f"seq={q.get('seq')} unanswered at close"
        )
    return assert_outcome_matches_derived(entries, roster, outcome)


def _record_entry_body(
    outcome: str,
    supports: Sequence[Dict[str, Any]],
    objectors: Sequence[Dict[str, Any]],
) -> str:
    if outcome == "no_convergence":
        return (
            "outcome: no_convergence\n"
            "escalated_to_ratifier: yes\n"
            "chosen: none\n"
            "The floor did not converge. The ratifier holds the final word. "
            "The host authors no decision.\n"
        )
    if outcome == "consensus_with_dissent":
        return (
            "outcome: consensus_with_dissent\n"
            "escalated_to_ratifier: no\n"
            "named dissent: "
            + ", ".join(e.get("author") or "" for e in objectors)
            + "\n"
            "supporting seqs: "
            + ", ".join(str(e["seq"]) for e in supports)
            + "\n"
        )
    return (
        "outcome: consensus\n"
        "escalated_to_ratifier: no\n"
        "supporting seqs: "
        + ", ".join(str(e["seq"]) for e in supports)
        + "\n"
    )


def _apply_close(
    session_dir: str | Path,
    entries: Sequence[Dict[str, Any]],
    roster: Sequence[Dict[str, str]],
    meta: Dict[str, Any],
    outcome: str,
    ts: str,
) -> Path:
    paths = session_paths(session_dir)
    facts_text = (
        paths["facts"].read_text(encoding="utf-8") if paths["facts"].is_file() else ""
    )
    topic = meta.get("topic") or ""
    record_md = render_record(topic, ts, facts_text, roster, entries, outcome)
    paths["record"].write_text(record_md, encoding="utf-8")
    supports = [
        e
        for e in entries
        if e.get("type") == "support"
        and e.get("author_kind") in ("council", "individual")
    ]
    present = present_seat_ids(roster, entries)
    objectors = [
        e
        for e in entries
        if e.get("type") == "objection" and e.get("author") in set(present)
    ]
    append_entry(
        session_dir,
        make_entry(
            seq=len(entries) + 1,
            ts=ts,
            round_n=int(entries[-1]["round"]) if entries else 0,
            phase="close",
            author="host",
            author_kind="host",
            typ="record",
            body=_record_entry_body(outcome, supports, objectors),
            addressed_to=[],
            answers=[int(e["seq"]) for e in supports],
            requested_by="",
            refs=[int(e["seq"]) for e in supports],
        ),
    )
    meta["closed"] = True
    meta["outcome"] = outcome
    meta["closed_at"] = ts
    save_session_meta(session_dir, meta)
    return paths["record"]


def cmd_close(args: argparse.Namespace, stdout: TextIO, stderr: TextIO) -> int:
    outcome = args.outcome
    paths = session_paths(args.dir)
    entries = load_entries(args.dir)
    meta = load_session_meta(args.dir)
    roster = list(meta.get("seats") or [])
    if meta.get("closed"):
        raise ProtocolError("session_closed", "already closed")
    _close_protocol_gates(entries, roster, outcome)
    ts = now_utc()
    record_path = _apply_close(args.dir, entries, roster, meta, outcome, ts)
    stdout.write(f"closed outcome={outcome} record={record_path}\n")
    return 0


def cmd_reclose(args: argparse.Namespace, stdout: TextIO, stderr: TextIO) -> int:
    outcome = args.outcome
    reason = (args.reason or "").strip()
    if not reason:
        raise ProtocolError("missing_reason", "reclose requires --reason")
    paths = session_paths(args.dir)
    entries = load_entries(args.dir)
    meta = load_session_meta(args.dir)
    roster = list(meta.get("seats") or [])
    if not meta.get("closed"):
        raise ProtocolError(
            "session_not_closed", "reclose requires a previous close"
        )
    _close_protocol_gates(entries, roster, outcome)
    ts = now_utc()
    previous_outcome = meta.get("outcome")
    protocol_body = (
        "previous close superseded\n"
        f"previous_outcome: {previous_outcome}\n"
        f"reason: {reason}\n"
        "The previous record entry remains on the floor. This close replaces "
        "record.md.\n"
    )
    append_entry(
        args.dir,
        make_entry(
            seq=len(entries) + 1,
            ts=ts,
            round_n=int(entries[-1]["round"]) if entries else 0,
            phase="close",
            author="host",
            author_kind="host",
            typ="protocol",
            body=protocol_body,
            addressed_to=[],
            answers=[],
            requested_by="",
            refs=[],
        ),
    )
    entries = load_entries(args.dir)
    record_path = _apply_close(args.dir, entries, roster, meta, outcome, ts)
    meta = load_session_meta(args.dir)
    meta["reclosed_at"] = ts
    save_session_meta(args.dir, meta)
    stdout.write(
        f"reclosed outcome={outcome} record={record_path} "
        f"previous_outcome={previous_outcome}\n"
    )
    return 0


# --------------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="floor.py",
        description="Shared brainstorm floor — seats deliberate, the host does not.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    open_p = sub.add_parser("open", help="convene a session (facts, agenda, roster)")
    open_p.add_argument("--dir", required=True)
    open_p.add_argument("--topic", required=True)
    open_p.add_argument("--facts", required=True)
    open_p.add_argument(
        "--seat",
        action="append",
        required=True,
        help="repeatable id:kind (council|individual)",
    )

    post_p = sub.add_parser("post", help="append one manifestation to the floor")
    post_p.add_argument("--dir", required=True)
    post_p.add_argument("--author", required=True)
    post_p.add_argument("--type", required=True, dest="type")
    post_p.add_argument("--round", required=True, type=int)
    post_p.add_argument("--phase", default=None)
    post_p.add_argument("--addressed-to", action="append", default=[], dest="addressed_to")
    post_p.add_argument("--answers", action="append", default=[])
    post_p.add_argument("--refs", action="append", default=[])
    post_p.add_argument("--requested-by", default="", dest="requested_by")
    post_p.add_argument("--body-file", required=True, dest="body_file")

    read_p = sub.add_parser("read", help="print the floor")
    read_p.add_argument("--dir", required=True)
    read_p.add_argument("--round", default=None, type=int)
    read_p.add_argument("--json", action="store_true")

    brief_p = sub.add_parser(
        "round-brief", help="complete floor through round N-1, verbatim"
    )
    brief_p.add_argument("--dir", required=True)
    brief_p.add_argument("--round", required=True, type=int)

    pend_p = sub.add_parser("pending", help="unanswered questions and open research")
    pend_p.add_argument("--dir", required=True)

    ver_p = sub.add_parser("verify", help="assert every invariant; exit 1 on violation")
    ver_p.add_argument("--dir", required=True)

    close_p = sub.add_parser("close", help="write record.md from the seats' outcome")
    close_p.add_argument("--dir", required=True)
    close_p.add_argument(
        "--outcome",
        required=True,
        choices=list(OUTCOMES),
    )

    reclose_p = sub.add_parser(
        "reclose",
        help="supersede a defective close on the record (append-only)",
    )
    reclose_p.add_argument("--dir", required=True)
    reclose_p.add_argument(
        "--outcome",
        required=True,
        choices=list(OUTCOMES),
    )
    reclose_p.add_argument(
        "--reason",
        required=True,
        help="why the previous close is superseded (required, on the record)",
    )
    return p


def main(
    argv: Optional[Sequence[str]] = None,
    stdout: Optional[TextIO] = None,
    stderr: Optional[TextIO] = None,
) -> int:
    stdout = stdout if stdout is not None else sys.stdout
    stderr = stderr if stderr is not None else sys.stderr
    parser = build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except SystemExit as e:
        code = e.code
        return int(code) if isinstance(code, int) else 2
    dispatch = {
        "open": cmd_open,
        "post": cmd_post,
        "read": cmd_read,
        "round-brief": cmd_round_brief,
        "pending": cmd_pending,
        "verify": cmd_verify,
        "close": cmd_close,
        "reclose": cmd_reclose,
    }
    try:
        return dispatch[args.cmd](args, stdout, stderr)
    except ProtocolError as exc:
        stderr.write(f"VIOLATION {exc.name}: {exc.detail}\n" if exc.detail else f"VIOLATION {exc.name}\n")
        return 1
    except FileNotFoundError as exc:
        stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
