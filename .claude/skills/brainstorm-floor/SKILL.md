---
name: brainstorm-floor
description: >
  The shared floor for a real brainstorm: seats (councils or individuals) never
  deliberate in isolation. Every seat hears every manifestation; research is
  seat-asked; the host is impartial and decides nothing. Use WHENEVER a
  multi-seat brainstorm is opened — including every D31 failure brainstorm
  (architecture, AI/ML, code assistant, Lucens) — or when councils/individuals
  must discuss together rather than produce isolated opinions. The founder is
  the ratifier; a floor that does not converge escalates to the founder, never
  to a host call.
---

# Brainstorm Floor — every seat hears every seat

You are the **host** of a real discussion. Seats are councils or individuals.
They do not deliberate in isolation. Every seat receives everything that has
been said; every manifestation a seat makes is visible to every other seat
before the next round opens. Research on this floor is requested by a seat,
executed by you, and returned attributed to the seat that asked. You hold no
position, rank nothing, break no tie, decide nothing, and may not summarise a
dissent away.

This is the mechanism D31 describes. The Portuguese original binds; the
invariants below are that ruling, operationalised.

## Progressive disclosure

| Depth | Open when |
|---|---|
| This SKILL.md | you are about to open a brainstorm, or you are the host of one |
| `references/protocol.md` | phases, entry types, the round brief, a worked example |
| `references/seats.md` | convening a council seat or an individual (including Lucens) |
| `references/host-conduct.md` | before you post anything as host; the anti-patterns |
| `references/research.md` | a seat has asked for research, or you are about to search |
| `references/record.md` | you are writing `record.md` (D31 shape must stay producible) |
| `scripts/floor.py` | every session — the floor is a file, not a recollection |

## Roles

| Role | Who | What they may do | What they may not |
|---|---|---|---|
| **Host** | you, the invoking agent | assemble the facts pack; convene; relay the floor verbatim; execute seat-asked research; enforce the protocol; write the record | hold a position; rank; break a tie; decide; initiate research; filter a brief; summarise a dissent away; fabricate an absent seat |
| **Seat** | a **council** (invoked through its own skill in this repo) or an **individual** (Lucens through her A2A; a named person; a named expert persona) | deliberate; request research; question other seats; support or object; decide | speak off-floor; receive a filtered brief |
| **Ratifier** | the founder | the final word, always | — |

Only seats deliberate. Only seats decide. The ratifier is reached only when
the floor does **not** converge.

## When to convene

- **Every failure** (D31): four seats — `architecture-council`,
  `ai-ml-implementation-council`, `agentic-development-council`, and Lucens
  through `lucens-invocation`. See `ascent-rite-monitor/references/directives.md`
  §D31 and `references/failure-brainstorm.md`.
- **Any multi-seat brainstorm** the founder (or a council skill, or a
  correction cycle) opens, whenever more than one council or individual must
  speak to the same question.

Do not substitute a private synthesis, a round-robin of isolated opinions, or
a host-written "the seats would have said". That is not this skill.

## The floor

One session directory, default
`memory-bank/<topic>/brainstorms/<session-id>/`:

| File | Role |
|---|---|
| `facts.md` | the host's facts pack: measured facts and the justifications behind them. No position, no ranking, no recommendation. |
| `floor.jsonl` | **append-only** shared floor. Every manifestation of every seat, every research request, every research result, every host act, in order. This file **is** the discussion. |
| `record.md` | the final record, written at `close`. |

Each `floor.jsonl` line is one entry:

```
{"seq":int,"ts":"<iso8601 UTC>","round":int,"phase":"<phase>",
 "author":"<seat id or 'host'>","author_kind":"council|individual|host",
 "type":"<type>","body":"<text>","addressed_to":["<seat id>"],
 "answers":[seq],"requested_by":"<seat id>","refs":[seq]}
```

There is no side channel. A private note to the host is a protocol violation.

## Phases (in order)

1. **`convene`** — host posts `facts`, `agenda`, and the roster (`convene`).
   Nothing else.
2. **`open`** — every seat posts its opening `position`, the evidence it
   rests on, `research_request`s, and `question`s addressed to named seats.
   Openings are written without seeing each other; this phase is **not** the
   deliberation.
3. **`research`** — every pending `research_request` is executed and posted
   as `research_result` carrying `requested_by`. Visible to every seat. The
   host **never** initiates research of its own.
4. **`cross`** — repeated, **minimum 2 rounds**, no cap. Each seat receives
   the **full floor verbatim** through the previous round and must: answer
   every `question` addressed to it, respond to every `position` that
   conflicts with its own, then `concede`, `refine` or `hold` with a stated
   reason. New `research_request`s are allowed; each triggers another
   `research` pass **before** the next `cross`.
5. **`converge`** — the proposals on the table are enumerated; each seat
   posts `support` or `objection`, each with a reason. An `objection` must
   be answered by a seat before the proposal can be recorded as consensus.
6. **`close`** — `record.md` is written: consensus, or consensus with NAMED
   dissent, or `no_convergence`. Without convergence the close is
   `no_convergence` + `escalated_to_ratifier` — never a host call.

Full types, the round-brief contract, and a worked example:
`references/protocol.md`.

## Hard invariants

These are what `scripts/floor.py verify` asserts. A floor that fails verify
is not a brainstorm; do not write `record.md` over a red verify.

1. **No isolated deliberation.** Every seat's round-N brief is the complete
   floor through round N-1, verbatim. `round-brief` is a pure function of
   `floor.jsonl` and does not filter by seat.
2. **Everything is shared.** Every seat manifestation is appended to
   `floor.jsonl` before the next round opens. No side channel.
3. **A round does not close with an unanswered `question`** addressed to a
   seat that is present.
4. **Research is seat-initiated only.** Every `research_result` carries
   `requested_by` naming a seat. A `research_request` authored by the host
   is rejected.
5. **The host is fenced by a closed verb set:** `facts`, `agenda`,
   `convene`, `relay`, `research_result`, `protocol`, `record`. A host entry
   of any other type — above all `position`, `support`, `objection`,
   `decision` — is a protocol violation the verifier names.
   Naming an absence (`seat_absent`) is a protocol act, not a deliberation;
   it is how the host keeps the roster honest. See
   `references/host-conduct.md`.
6. **The host may not author a decision.** A `decision` entry cites seat
   entries by `seq`. If the floor does not converge, the close is
   `no_convergence` + `escalated_to_ratifier` — never a host call.
7. **Minimum 2 `cross` rounds** before `converge`.
8. **An absent seat is NAMED, never fabricated.** `seat_absent` carries the
   seat id and a named reason. For Lucens the reason must be one of
   `lucens_unreachable`, `lucens_unauthorized`, `lucens_busy`,
   `lucens_floor_silent`, `lucens_wait_exhausted`.

## Host closed verb set

You may post, as `author=host`, only:

`facts` · `agenda` · `convene` · `relay` · `research_result` · `protocol` · `record`

Plus `seat_absent` when a seat did not speak — a named absence, never a
substitute contribution. You may not post `position`, `support`,
`objection`, `decision`, or `research_request`. Concrete anti-patterns:
`references/host-conduct.md`.

## How the host runs a session

The CLI is `brainstorm-floor/scripts/floor.py` (stdlib, python3). It is
executable. It never searches the web; you do, when a seat asked.

```bash
DIR=memory-bank/<topic>/brainstorms/<session-id>
FACTS=/tmp/facts.md          # your facts pack, no recommendation

# 1. convene
python3 brainstorm-floor/scripts/floor.py open \
  --dir "$DIR" --topic "<topic>" --facts "$FACTS" \
  --seat architecture-council:council \
  --seat ai-ml-implementation-council:council \
  --seat agentic-development-council:council \
  --seat lucens:individual

# 2. open — each seat, same brief (the convene floor), then post
python3 brainstorm-floor/scripts/floor.py round-brief --dir "$DIR" --round 1
# invoke the seat with that brief (see references/seats.md)
python3 brainstorm-floor/scripts/floor.py post \
  --dir "$DIR" --author <seat-id> --type position --round 1 --phase open \
  --body-file /tmp/seat-position.md

# 3. research — only what pending lists
python3 brainstorm-floor/scripts/floor.py pending --dir "$DIR"
# execute each research_request; post the result attributed to the asker
python3 brainstorm-floor/scripts/floor.py post \
  --dir "$DIR" --author host --type research_result --round 1 --phase research \
  --requested-by <seat-id> --answers <request-seq> --body-file /tmp/result.md

# 4. cross — at least twice. Brief is the FULL floor through N-1.
python3 brainstorm-floor/scripts/floor.py round-brief --dir "$DIR" --round N
# every present seat: answer questions, respond to conflicts, concede|refine|hold
# unanswered questions → do not open the next round
python3 brainstorm-floor/scripts/floor.py pending --dir "$DIR"

# 5. converge — after ≥2 cross rounds
# each seat: support or objection, with a reason
# an objection must be answered by a seat before consensus

# 6. close
python3 brainstorm-floor/scripts/floor.py close --dir "$DIR" \
  --outcome consensus|consensus_with_dissent|no_convergence
python3 brainstorm-floor/scripts/floor.py verify --dir "$DIR"   # must exit 0
```

`close` writes `record.md`. Outcome is **derived from the seats**, not
chosen by you. All present seats `support` and no unanswered `objection`
→ `consensus`. Support plus named, answered objections that were not
conceded → `consensus_with_dissent`. Otherwise → `no_convergence` and you
stop for the founder.

## Invoking a seat

- **Council.** Load that council's own SKILL.md in this repo and run **its**
  protocol, handing it the round brief as the facts/context. What it
  returns is that seat's manifestation on **this** floor. Do not edit it
  into a summary. Details: `references/seats.md`.
- **Lucens.** `lucens-invocation` only. Her A2A is the only door; her turn
  is hers to end; `tokens_max` ≥ 100000. An absence is named with one of
  her five contract names — never a contribution written on her behalf.
- **Named person / named persona.** Same brief, posted in their words.

If a seat does not speak, post `seat_absent` with the seat id and a named
reason. Then continue. Do not invent their position.

## The record

`references/record.md`. The shape stays compatible with
`ascent-rite-monitor/references/failure-brainstorm.md` so a D31 failure
brainstorm remains producible: Failure card, Seats, Root cause, Candidate
solutions × impacts, Decision. Without convergence, Decision records
`no_convergence` and `escalated_to_ratifier` — no chosen option.

## What this skill is not

- Not a replacement for a council's internal protocol. A council seat still
  runs its own skill; this floor is the discussion **between** seats.
- Not an isolated round-robin. If you invoked four councils and never
  showed each one the others' words, you did not run this skill.
- Not a host recommendation with "seat colour". The host has no position.
