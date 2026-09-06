# The MoE-gated deliberation model (generic specification)

The council mechanism, brand- and domain-agnostic. A council instantiates this
spec with its own roster and charters; the mechanism itself does not change.
Nickname: **"all hear, few speak."**

## Roles

- **Moderator** — the orchestrating model. Runs on the strongest model available
  (deciding is expensive reasoning). Never holds a seat: routes, referees,
  synthesizes.
- **Seats** — expert personas, each a distinct lens on the council's domain.
- **Ratifier** — the human (founder/owner). Final word on every outcome.

## Disclosure levels

| Level | Content | Loaded |
|---|---|---|
| L0 | `references/roster.md` — one line per seat (≤15 tokens) | once per session, kept in context ("everyone is in the room") |
| L1 | `references/seats/<slug>/charter.md` (≤600 tokens) | only when the seat is gated HOT |
| L2 | other files in the seat's folder | only while HOT, only if the charter is insufficient |

The skill's frontmatter description is the zeroth gate: the harness indexes it;
the body loads only on invocation.

## Protocol — per agenda item

1. **Brief** — Moderator fills the session-brief template (≤300 tokens):
   question (one sentence), decision at stake, constraints, prior art pointers,
   token budget, max hot rounds (default 3).
2. **Gate** — score every L0 line against the brief: 0 = warm, 1 = relevant,
   2 = specialist. Top 2–4 become **HOT**. Record the gating table.
3. **Hot rounds** — each HOT seat, charter loaded, speaks AS the persona:
   position → cross-challenge the other HOT seats → revise. Stay in charter; a
   seat argues its lens, never a generic assistant voice.
4. **Warm sweep** — ONE batched call on the cheapest capable model, carrying:
   roster minus HOT seats + brief + rolling summary. Each warm seat answers
   `<seat-slug>: <one line insight/risk | PASS>`. Never restate the summary.
5. **Promote** — a WARM flag is *substantive* when it names a mechanism, risk or
   precedent absent from the hot round (not a vibe, not a restatement).
   Substantive flag → that seat is HOT next round. Log promotions.
6. **Synthesize** — recommendation + explicit dissents + what evidence would
   reverse the answer. Deliver to the ratifier.

## Hard token rules

- Budgets: roster line ≤15 · charter ≤600 · brief ≤300 · rolling summary ≤500.
- Between rounds, the rolling summary REPLACES the transcript.
- Stop early on convergence (a round adds no new position).
- Budget exhausted → synthesize with what exists and say so.

## Session record (always produced)

Gating table · promotions · synthesis (recommendation, dissents, reversal
conditions) · token-spend estimate. Persist to the active memory-bank topic when
the ratifier ratifies; the transcript only on explicit request.

## Why this shape (cost rationale)

- Naive N-seat deliberation costs O(N × rounds) strong-model calls. This model
  costs O(k × rounds) strong + O(rounds) cheap, k = 2–4, with N only appearing
  in the ~15-token-per-seat roster — the roster can grow without the session
  cost growing with it.
- The warm sweep is the deliberate extension over classic MoE routing: unrouted
  experts still see the token stream cheaply, because cross-domain insight is
  precisely what councils exist to catch.
- Promotion makes the gate self-correcting: a wrong routing decision costs one
  round, not the session.

## Evolution hook

Log which seats were gated hot, which warm flags were promoted, and which
syntheses the ratifier ratified/overrode. That record is training signal: the
gate starts heuristic and can later be learned. (In RiseGen, this is LucensMind
sample-class material.)
