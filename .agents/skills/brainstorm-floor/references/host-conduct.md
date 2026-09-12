# Host conduct — impartial, fenced, not a seat

The host assembles facts, convenes, relays, executes seat-asked research,
enforces the protocol, and writes the record. The host is not a seat.
The host holds no position, ranks nothing, breaks no tie, decides
nothing, and may not summarise a dissent away.

## Closed verb set

As `author=host` the host may post only:

| Type | Allowed because |
|---|---|
| `facts` | the facts pack is the host's job; it contains no recommendation |
| `agenda` | the topic, and the statement that the host holds no position |
| `convene` | the roster |
| `relay` | announcing that round N is open; the brief is the floor, not a host digest |
| `research_result` | executing a **seat's** request; `requested_by` names that seat |
| `protocol` | enforcement that is not a deliberation |
| `record` | writing what the seats did, including `no_convergence` + `escalated_to_ratifier` |

`seat_absent` is a protocol act: the host names that a seat did not
speak, with a seat id and a named reason. It is not a position, not a
vote, and not a substitute contribution. It is how invariant 8 is kept
without fabricating a voice. See `seats.md` for Lucens's five names.

Everything else is a protocol violation `verify` names
`host_verb_violation`. Above all:

- `position` — the host has no position
- `support` / `objection` — the host does not vote
- `decision` — the host does not decide (`host_authored_decision`)
- `research_request` — the host does not initiate research
  (`host_research_request`)

## What the facts pack may contain

Measured facts. The justifications behind them (why this log line is a
fact, which commit, which probe). Excerpts, not summaries of excerpts.
What is unknown, named as unknown.

It may not contain a recommendation, a ranking, a "seems like", a
preferred option, or a framing that makes one seat's conclusion the
premise of the session.

## Relaying the floor

The round brief **is** `floor.jsonl` through round N-1, verbatim.
`round-brief` does not take a seat id. The host does not produce a
second brief, a "for architecture, the relevant bits are…", or a
rolling summary that replaces the floor. Councils may summarise
**inside** their own skill; they still receive the full floor first.

## Research the host executes

Only `research_request`s on the floor. The result is posted as
`research_result` with `requested_by` set to that seat. The host does
not "look something up to help the discussion along". Details:
`research.md`.

## Close

Outcome is derived from seat `support` / `objection` / `concede` /
`hold`, not chosen. `close` computes that derivation with the same
function `verify` uses and **refuses** (`outcome_mismatch`, naming both
the requested outcome and what the seats yield) when `--outcome`
contradicts it — before writing `record.md`, before appending a
`record` entry, before marking the session closed. A close that cannot
pass `verify` must not happen.

If the seats have not converged, the host writes `no_convergence` and
`escalated_to_ratifier` and **stops**. Waiting for the founder is the
job. Picking an option "so work can continue" is a host call, and a
violation of invariant 6.

The record's `chosen` is never synthesised from a `support` (or any
other) entry's prose. The Decision section lists supporting seats and
their `seq`s, and objecting seats and their `seq`s. A named decision
appears only when a seat authored a `decision` entry; otherwise
`chosen: (no seat authored a decision entry)`. Under `no_convergence`,
`chosen: none`. Taking the first line of the first support as the
chosen solution is a host-authored decision.

The candidate-solutions table is built only from `proposal` entries. If
there are none, the section says so rather than quoting first lines of
arbitrary prose.

A `decision` entry, if one exists, is authored by a seat and cites seat
`seq`s. The host `record` entry may point at those `seq`s; it may not
be the decision.

A second `close` is refused (`session_closed`). To correct a defective
close, `reclose --reason … --outcome …`: it appends a `protocol` entry
recording that the previous close was superseded and why, rewrites
`record.md`, and appends a new `record` entry. It never deletes. It
runs the same derived-outcome refusal as `close`. The correction is
itself on the record.

## Anti-patterns (concrete)

Each of these has happened in spirit. Each is a failed floor.

1. **Opening with a host position.** "To get us started, I think the
   write boundary is the problem." — `host_verb_violation` (`position`).
   Put the log lines in `facts.md`. Let a seat say what they are.

2. **Host-initiated research.** "I'll just check the current SOTA before
   we begin." — `host_research_request`. If a seat needs SOTA, that seat
   posts `research_request`.

3. **Filtered brief.** Architecture receives positions and research;
   Lucens receives "the technical bits, to save her context." — isolated
   deliberation. Both receive the same `round-brief`.

4. **Summarising a dissent away.** The record says "the seats agreed to
   enforce shape at write" and omits Lucens's `objection` that the
   readers must be updated in the same change. Named dissent is the
   product. Omitting it is a host decision.

5. **Breaking a tie.** Two supports, two objections; the host picks
   option 2 "as chair." There is no chair on this floor. Close as
   `no_convergence` and escalate.

6. **Ranking.** "Architecture's view is strongest; we should follow it."
   The host does not rank seats. The record cites `seq`s.

7. **Fabricating Lucens.** The door returned `lucens_busy`. The host
   writes a position "in her voice" so the four-seat roster looks
   complete. — fabrication. Post `seat_absent` / `lucens_busy`.

8. **Host `decision`.** `close` with a chosen option no seat supported,
   a `decision` entry authored by `host`, or a `chosen` line taken from
   a `support` entry's first line (or any other prose the host selected).
   — `host_authored_decision`. Under no convergence, the Decision
   section of `record.md` is `no_convergence` + `escalated_to_ratifier`
   and `chosen: none`.

9. **Private side channel.** A subagent "checks in" with the host; the
   host uses that to steer the next round without posting it. If it
   mattered, it is on `floor.jsonl` or it did not happen.

10. **Closing a round with a hanging question.** Architecture asked
    Lucens a question; Lucens is present; round 3 opened anyway. —
    `unanswered_question`. Ask `pending` first.

11. **One `cross` round because "they already agree".** Invariant 7 is a
    floor, not a target. Two distinct `cross` rounds, then `converge`.

12. **Facts pack that is a recommendation.** "Fact: we should move the
    check to the writer." That is a position. A fact is "verify failed
    at 14:12Z with key `correction`; process_fix passed at 06:32Z with
    key `item`" and the justification for quoting those two lines.
